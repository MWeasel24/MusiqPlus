# frontend/streamlit_app.py
import os
from typing import Optional, Dict, Any, List

import requests
import streamlit as st
import pandas as pd

# URL do backend FastAPI
BACKEND_URL = os.getenv("MUSIQ_BACKEND_URL", "http://localhost:8000")


# =========================
# Helpers para chamar a API
# =========================
def api_get(path: str, params: Optional[Dict[str, Any]] = None):
    url = f"{BACKEND_URL}{path}"
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"Erro na comunicação com backend ({path}): {e}")
        return None


def api_post(path: str, json_data: Dict[str, Any]):
    url = f"{BACKEND_URL}{path}"
    try:
        resp = requests.post(url, json=json_data, timeout=20)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.HTTPError as e:
        try:
            detail = resp.json().get("detail")
        except Exception:
            detail = str(e)
        st.error(f"Erro da API: {detail}")
        return None
    except Exception as e:
        st.error(f"Erro na comunicação com backend ({path}): {e}")
        return None


def carregar_usuarios() -> List[Dict[str, Any]]:
    data = api_get("/usuarios")
    return data or []


def criar_usuario(nome: str):
    return api_post("/usuarios", {"nome": nome})


def listar_itens(q: Optional[str] = None, genero: Optional[str] = None):
    params: Dict[str, Any] = {}
    if q:
        params["q"] = q
    if genero and genero != "Todos":
        params["genero"] = genero
    data = api_get("/itens", params=params)
    return data or []


def recomendar(usuario_id: int, top_k: int = 10, genero: Optional[str] = None):
    payload = {
        "usuario_id": usuario_id,
        "top_k": top_k,
        "genero": None if genero == "Todos" else genero,
        "ordenar_por": "similaridade",
    }
    return api_post("/recomendar", payload) or []


def avaliar(usuario_id: int, item_id: int, gostou: bool, origem: str):
    payload = {
        "usuario_id": usuario_id,
        "item_id": item_id,
        "gostou": gostou,
        "origem": origem,
    }
    return api_post("/avaliar", payload)


def metricas(usuario_id: int):
    return api_get(f"/metricas/{usuario_id}") or {
        "precision": 0.0,
        "recall": 0.0,
        "f1": 0.0,
        "hits": 0,
        "recomendados": 0,
        "relevantes": 0,
    }


def analise_usuario(usuario_id: int):
    return api_get(f"/analise_usuario/{usuario_id}") or None


# =========================
# UI Helpers
# =========================
def carregar_css():
    css_path = os.path.join(os.path.dirname(__file__), "style.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def header_nav():
    st.markdown(
        "<div class='musiq-logo'>Musiq+</div>",
        unsafe_allow_html=True,
    )

    aba_atual = st.session_state.get("aba", "inicio")
    c1, c2, c3 = st.columns(3, gap="small")

    with c1:
        if st.button("Início", key="nav_inicio", use_container_width=True):
            aba_atual = "inicio"
    with c2:
        if st.button("Recomendador", key="nav_rec", use_container_width=True):
            aba_atual = "recomendador"
    with c3:
        if st.button("Análise", key="nav_ana", use_container_width=True):
            aba_atual = "analise"

    st.session_state["aba"] = aba_atual


def sidebar_user():
    st.sidebar.markdown("### Usuário ativo")

    usuarios = carregar_usuarios()
    if "usuario_id" not in st.session_state:
        st.session_state["usuario_id"] = None
        st.session_state["usuario_nome"] = None

    nomes = ["(Nenhum)"] + [str(u["nome"]) for u in usuarios]
    ids = [None] + [int(u["usuario_id"]) for u in usuarios]

    idx_atual = 0
    if st.session_state["usuario_id"] in ids:
        idx_atual = ids.index(st.session_state["usuario_id"])

    escolha = st.sidebar.selectbox("Selecionar usuário", nomes, index=idx_atual)
    novo_id = ids[nomes.index(escolha)]
    if novo_id != st.session_state["usuario_id"]:
        st.session_state["usuario_id"] = novo_id
        st.session_state["usuario_nome"] = escolha if novo_id is not None else None

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Criar novo usuário")
    novo_nome = st.sidebar.text_input("Nome do usuário")
    if st.sidebar.button("Criar"):
        if novo_nome.strip():
            resp = criar_usuario(novo_nome.strip())
            if resp:
                st.session_state["usuario_id"] = resp["usuario_id"]
                st.session_state["usuario_nome"] = resp["nome"]
                st.sidebar.success(f"Usuário '{resp['nome']}' criado.")
        else:
            st.sidebar.warning("Informe um nome válido.")

    if st.session_state["usuario_nome"]:
        st.sidebar.info(f"Ativo: **{st.session_state['usuario_nome']}**")
    else:
        st.sidebar.info("Nenhum usuário ativo.")


def card_musica(item: Dict[str, Any], origem: str, mostrar_sim: bool = False):
    """
    Card de música:
    - capa
    - nome, artista, genero, idioma
    - tags
    - similaridade (opcional)
    - botões: ▶ (se tiver link), 👍, 👎
    - estado de like/dislike salvo na sessão
    """
    usuario_id = st.session_state.get("usuario_id")
    rating_key = None
    if usuario_id is not None:
        rating_key = f"rating_{usuario_id}_{item['item_id']}"

    cols = st.columns([1, 3, 2])

    # Capa
    with cols[0]:
        if item.get("capa_url"):
            st.image(
                f"{BACKEND_URL}{item['capa_url']}",
                use_container_width=True,
            )

    # Infos principais
    with cols[1]:
        st.markdown(
            f"<div class='musiq-card-title'>{item['nome']}</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div class='musiq-card-sub'>{item['artista']} · {item['genero']} · {item['idioma']}</div>",
            unsafe_allow_html=True,
        )
        tags = item.get("tags", "")
        if tags:
            tags_html = ""
            for t in str(tags).split(","):
                t_clean = t.strip()
                if t_clean:
                    tags_html += f"<span class='musiq-tag'>{t_clean}</span>"
            if tags_html:
                st.markdown(
                    f"<div class='musiq-tags'>{tags_html}</div>",
                    unsafe_allow_html=True,
                )

    # Similaridade + ações
    with cols[2]:
        if mostrar_sim and "similaridade" in item and item["similaridade"] is not None:
            st.markdown(
                f"<div class='musiq-sim'>similaridade: {item['similaridade']:.3f}</div>",
                unsafe_allow_html=True,
            )

        if usuario_id is None:
            st.caption("Selecione um usuário para avaliar.")
        else:
            c1, c2, c3 = st.columns(3)
            with c1:
                if item.get("youtube_url"):
                    st.markdown(
                        f"""
                        <a href="{item['youtube_url']}" target="_blank" style="text-decoration:none;">
                            <button class="yt-button">▶</button>
                        </a>
                        """,
                        unsafe_allow_html=True,
                    )
            with c2:
                if st.button("✔️", key=f"like_{origem}_{item['item_id']}"):
                    avaliar(usuario_id, item["item_id"], True, origem)
                    if rating_key:
                        st.session_state[rating_key] = "like"
            with c3:
                if st.button("❌", key=f"dislike_{origem}_{item['item_id']}"):
                    avaliar(usuario_id, item["item_id"], False, origem)
                    if rating_key:
                        st.session_state[rating_key] = "dislike"

            # Exibição do estado atual
            if rating_key and rating_key in st.session_state:
                estado = st.session_state[rating_key]
                if estado == "like":
                    st.markdown(
                        "<span style='color:#22c55e;font-size:0.8rem;'>Avaliação atual: ✔️ </span>",
                        unsafe_allow_html=True,
                    )
                elif estado == "dislike":
                    st.markdown(
                        "<span style='color:#ef4444;font-size:0.8rem;'>Avaliação atual: ❌ </span>",
                        unsafe_allow_html=True,
                    )


# =========================
# Páginas
# =========================
def pagina_inicio():
    st.subheader("Buscar músicas")

    q = st.text_input("Pesquisar por nome, artista ou tag", key="busca_inicio")
    itens_busca = listar_itens(q=q) if q else []

    if q:
        st.markdown("#### Resultados da busca")
        for it in itens_busca:
            # origem "inicio" (válida no backend)
            card_musica(it, origem="inicio", mostrar_sim=False)
            st.markdown("---")

    st.markdown("#### Todas as músicas")
    todos_itens = listar_itens()
    for it in todos_itens:
        # também "inicio"
        card_musica(it, origem="inicio", mostrar_sim=False)
        st.markdown("---")


def pagina_recomendador():
    usuario_id = st.session_state.get("usuario_id")
    if usuario_id is None:
        st.warning("Selecione um usuário no sidebar para usar o recomendador.")
        return

    st.subheader("Recomendador por conteúdo")

    todos_itens = listar_itens()
    generos = ["Todos"] + sorted({it["genero"] for it in todos_itens})

    col1, col2, _ = st.columns([2, 1, 1])
    with col1:
        genero_sel = st.selectbox("Filtrar por gênero", generos, key="genero_rec")
    with col2:
        k = st.slider("Quantidade de recomendações", 5, 20, 10, key="topk_rec")

    if st.button("GERAR RECOMENDAÇÕES", use_container_width=True):
        recs = recomendar(usuario_id, top_k=k, genero=genero_sel)
        st.session_state["recomendacoes"] = recs

    recs = st.session_state.get("recomendacoes", [])
    if not recs:
        st.info("Nenhuma recomendação gerada ainda.")
        return

    st.markdown("#### Recomendações")
    for it in recs:
        card_musica(it, origem="recomendador", mostrar_sim=True)
        st.markdown("---")

    st.markdown("---")
    m = metricas(usuario_id)
    colm1, colm2, colm3 = st.columns(3)
    colm1.metric("Precision", f"{m['precision']:.3f}")
    colm2.metric("Recall", f"{m['recall']:.3f}")
    colm3.metric("F1-score", f"{m['f1']:.3f}")
    st.caption(
        "Métricas calculadas apenas com avaliações feitas na aba Recomendador."
    )


def pagina_analise():
    usuario_id = st.session_state.get("usuario_id")
    if usuario_id is None:
        st.warning("Selecione um usuário no sidebar para ver a análise.")
        return

    dados = analise_usuario(usuario_id)
    if not dados:
        st.info("Sem dados de análise para este usuário.")
        return

    st.subheader(f"Análise do usuário: {dados['usuario']['nome']}")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Avaliações totais", dados["total_avaliacoes"])
        st.metric(
            "Avaliações no recomendador", dados["total_avaliacoes_recomendador"]
        )
    with col2:
        m = dados["metricas"]
        st.metric("Precision", f"{m['precision']:.3f}")
        st.metric("Recall", f"{m['recall']:.3f}")
        st.metric("F1-score", f"{m['f1']:.3f}")

    st.markdown("---")
    st.markdown("#### Gêneros mais curtidos")
    generos = dados["generos"]
    if generos:
        df_gen = pd.DataFrame(
            [
                {
                    "Gênero": g,
                    "Likes": v["likes"],
                    "Total": v["total"],
                    "Proporção_likes": v["likes"] / v["total"] if v["total"] else 0.0,
                }
                for g, v in generos.items()
            ]
        )
        df_gen = df_gen.sort_values("Likes", ascending=False)
        st.dataframe(df_gen, use_container_width=True)
        st.bar_chart(df_gen.set_index("Gênero")[["Likes"]], use_container_width=True)
    else:
        st.info("Ainda não há avaliações suficientes para o gráfico de gêneros.")

    st.markdown("---")
    st.caption(
        "As avaliações do dataset avaliacoes.csv são usadas apenas como gabarito para calcular as métricas."
    )


# =========================
# main
# =========================
def main():
    st.set_page_config(page_title="Musiq+", layout="wide")
    carregar_css()

    if "aba" not in st.session_state:
        st.session_state["aba"] = "inicio"

    header_nav()
    sidebar_user()

    aba = st.session_state["aba"]
    if aba == "inicio":
        pagina_inicio()
    elif aba == "recomendador":
        pagina_recomendador()
    elif aba == "analise":
        pagina_analise()
    else:
        pagina_inicio()


if __name__ == "__main__":
    main()
