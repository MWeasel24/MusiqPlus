# backend/recommender.py
from __future__ import annotations

from typing import Optional, Dict

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .config import DATA_DIR

_itens_df: Optional[pd.DataFrame] = None
_avaliacoes_df: Optional[pd.DataFrame] = None
_usuarios_df: Optional[pd.DataFrame] = None

_vectorizer: Optional[TfidfVectorizer] = None
_item_matrix = None

def _global_relevantes(threshold: float = 0.5):
    """
    Define quais itens são relevantes globalmente, com base no gabarito (avaliacoes.csv).
    threshold = média mínima de 'gostou' para um item ser considerado relevante.
    """
    aval = load_avaliacoes_df()
    if aval.empty:
        return set()

    media_por_item = aval.groupby("item_id")["gostou"].mean()
    relevantes = media_por_item[media_por_item >= threshold].index.tolist()
    return set(int(i) for i in relevantes)

def _ensure_itens_loaded() -> pd.DataFrame:
    global _itens_df
    if _itens_df is None:
        path = DATA_DIR / "itens.csv"
        if not path.exists():
            raise RuntimeError(
                f"Arquivo itens.csv não encontrado em {path}. Rode backend/data/setup_data.py."
            )
        df = pd.read_csv(path)
        df["genero"] = df["genero"].fillna("desconhecido").astype(str)
        df["tags"] = df["tags"].fillna("").astype(str)
        df["palavra_chave"] = df["palavra_chave"].fillna("").astype(str)
        df["humor"] = df["humor"].fillna("").astype(str)
        df["instrumentacao"] = df["instrumentacao"].fillna("").astype(str)
        df["idioma"] = df["idioma"].fillna("").astype(str)
        df["descricao"] = df["descricao"].fillna("").astype(str)
        _itens_df = df
    return _itens_df


def _build_feature_text(row: pd.Series) -> str:
    parts = [
        row["genero"],
        row["tags"],
        row["palavra_chave"],
        row["humor"],
        row["instrumentacao"],
        row["idioma"],
        row["descricao"],
    ]
    return " ".join(str(p) for p in parts if p)


def _ensure_model():

    stopwords_pt = [
    'a', 'o', 'e', 'de', 'do', 'da', 'em', 'um', 'uma', 'que', 'é',
    'para', 'com', 'não', 'no', 'na', 'os', 'as', 'por', 'mais', 'menos',
    'seu', 'sua', 'isso', 'também', 'ou', 'mas', 'se', 'então', 'quando',
    'onde', 'como', 'porque'
    ]

    global _vectorizer, _item_matrix, _itens_df
    itens = _ensure_itens_loaded()
    if _vectorizer is None or _item_matrix is None:
        itens = itens.copy()
        itens["feature_text"] = itens.apply(_build_feature_text, axis=1)
        _vectorizer = TfidfVectorizer(stop_words=stopwords_pt)
        _item_matrix = _vectorizer.fit_transform(itens["feature_text"])
        _itens_df = itens


def get_itens_df() -> pd.DataFrame:
    _ensure_model()
    return _itens_df.copy()


def load_avaliacoes_df() -> pd.DataFrame:
    global _avaliacoes_df
    if _avaliacoes_df is None:
        path = DATA_DIR / "avaliacoes.csv"
        if not path.exists():
            raise RuntimeError(
                f"Arquivo avaliacoes.csv não encontrado em {path}. Rode backend/data/setup_data.py."
            )
        df = pd.read_csv(path)
        df["gostou"] = df["gostou"].astype(int)
        _avaliacoes_df = df
    return _avaliacoes_df.copy()


def load_usuarios_df() -> pd.DataFrame:
    global _usuarios_df
    path = DATA_DIR / "usuarios.csv"
    if path.exists():
        df = pd.read_csv(path)
    else:
        df = pd.DataFrame(columns=["usuario_id", "nome", "item_id", "gostou", "origem"])

    if not df.empty:
        if "usuario_id" in df.columns:
            df["usuario_id"] = df["usuario_id"].astype(int)
        if "nome" in df.columns:
            df["nome"] = df["nome"].astype(str)
        if "gostou" in df.columns:
            df["gostou"] = df["gostou"].fillna(0).astype(int)

    _usuarios_df = df
    return _usuarios_df.copy()


def salvar_usuarios_df(df: pd.DataFrame) -> None:
    global _usuarios_df
    path = DATA_DIR / "usuarios.csv"
    df.to_csv(path, index=False)
    _usuarios_df = df.copy()


def _user_profile_vector(usuario_id: int, usuarios_df: pd.DataFrame):
    _ensure_model()
    liked_ids = usuarios_df[
        (usuarios_df["usuario_id"] == usuario_id) & (usuarios_df["gostou"] == 1)
    ]["item_id"].dropna().unique()

    if len(liked_ids) == 0:
        raise ValueError(
            "Usuário ainda não possui likes suficientes para montar o perfil."
        )

    itens = _ensure_itens_loaded()
    liked_idx = itens.index[itens["item_id"].isin(liked_ids)].tolist()
    if not liked_idx:
        raise ValueError(
            "Itens curtidos pelo usuário não existem mais no catálogo."
        )

    liked_vectors = _item_matrix[liked_idx]
    profile = liked_vectors.mean(axis=0)  # ainda é np.matrix
    # converte para ndarray 1D para evitar o erro do np.matrix
    profile = np.asarray(profile).ravel()
    return profile


def recommend_for_user(
    usuario_id: int,
    top_k: int = 10,
    genero: Optional[str] = None,
) -> pd.DataFrame:
    """
    Gera recomendações baseado apenas nos atributos dos itens (TF-IDF + cosseno).
    Usa joblib.Parallel para paralelizar o cálculo de similaridade.
    """
    _ensure_model()
    itens = _ensure_itens_loaded()
    usuarios_df = load_usuarios_df()
    profile = _user_profile_vector(usuario_id, usuarios_df)
    n_items = _item_matrix.shape[0]

    def sim_for_idx(i: int) -> float:
        # linha i da matriz TF-IDF (sparse)
        v_sparse = _item_matrix[i]
        # converte para array 1D
        v = v_sparse.toarray().ravel()
        s = cosine_similarity(
            profile.reshape(1, -1),
            v.reshape(1, -1),
        )[0, 0]
        return float(s)

    # Paralelismo aqui
    sims = Parallel(n_jobs=-1)(delayed(sim_for_idx)(i) for i in range(n_items))

    itens = itens.copy()
    itens["similaridade"] = np.array(sims)

    liked_ids = usuarios_df[
        (usuarios_df["usuario_id"] == usuario_id) & (usuarios_df["gostou"] == 1)
    ]["item_id"].dropna().unique()

    mask = ~itens["item_id"].isin(liked_ids)

    if genero:
        mask &= itens["genero"].str.lower() == genero.lower()

    candidatos = itens[mask]
    candidatos = candidatos.sort_values("similaridade", ascending=False)
    if top_k is not None:
        candidatos = candidatos.head(top_k)
    return candidatos.reset_index(drop=True)


def compute_metricas(usuario_id: int) -> Dict[str, float]:
    """
    Métricas usando APENAS avaliações cuja origem == 'recomendador'.

    Agora os usuários de gabarito (avaliacoes.csv) são OUTROS usuários.
    Então:
      - relevância é definida globalmente por item (média de 'gostou' no gabarito);
      - hits = recomendações que o usuário gostou E que são relevantes no gabarito.
    """
    aval = load_avaliacoes_df()
    usuarios = load_usuarios_df()

    relevantes = _global_relevantes(threshold=0.6)

    # Todas as avaliações do usuário no sistema
    regs_usuario = usuarios[usuarios["usuario_id"] == usuario_id]

    # Apenas avaliações feitas na aba Recomendador
    regs_rec = regs_usuario[regs_usuario["origem"] == "recomendador"]

    if regs_rec.empty:
        return {
            "precision": 0.0,
            "recall": 0.0,
            "f1": 0.0,
            "hits": 0,
            "recomendados": 0,
            "relevantes": len(relevantes),
        }

    # Itens recomendados (avaliados na aba Recomendador)
    recomendados = set(int(i) for i in regs_rec["item_id"].dropna().tolist())

    # Hits: recomendados que são relevantes globalmente e que o usuário marcou como gostou=1
    hits = 0
    for _, row in regs_rec.iterrows():
        item_id = int(row["item_id"])
        if item_id in relevantes and int(row["gostou"]) == 1:
            hits += 1

    n_recomendados = len(recomendados)
    n_relevantes = len(relevantes)

    precision = hits / n_recomendados if n_recomendados else 0.0
    recall = hits / n_relevantes if n_relevantes else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall) > 0
        else 0.0
    )

    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "hits": hits,
        "recomendados": n_recomendados,
        "relevantes": n_relevantes,
    }

def genero_stats(usuario_id: int) -> Dict[str, Dict[str, int]]:
    usuarios = load_usuarios_df()
    itens = _ensure_itens_loaded()

    regs = usuarios[usuarios["usuario_id"] == usuario_id]
    if regs.empty:
        return {}

    merged = regs.merge(itens[["item_id", "genero"]], on="item_id", how="left")
    stats: Dict[str, Dict[str, int]] = {}
    for genero, grupo in merged.groupby("genero"):
        total = len(grupo)
        likes = int((grupo["gostou"] == 1).sum())
        stats[genero] = {"likes": likes, "total": int(total)}
    return stats


def user_ratings(usuario_id: int) -> pd.DataFrame:
    usuarios = load_usuarios_df()
    itens = _ensure_itens_loaded()
    regs = usuarios[usuarios["usuario_id"] == usuario_id]
    if regs.empty:
        return pd.DataFrame()
    merged = regs.merge(
        itens[["item_id", "nome", "genero", "artista"]],
        on="item_id",
        how="left",
    )
    return merged

# em backend/recommender.py

def registrar_avaliacao(usuario_id: int, item_id: int, gostou: bool, origem: str):
    """
    Registra uma avaliação de forma idempotente:
    - para cada (usuario_id, item_id) existe no máximo UMA linha em usuarios.csv
    - se já existia, é substituída (atualiza gostou e origem)
    """
    global _usuarios_df

    df = load_usuarios_df()  # sempre traz a versão mais recente

    # remove qualquer linha anterior desse usuário para esse item
    mask = (df["usuario_id"] == usuario_id) & (df["item_id"] == item_id)
    df = df[~mask]

    # adiciona nova linha
    nova_linha = {
        "usuario_id": int(usuario_id),
        "nome": str(
            df[df["usuario_id"] == usuario_id]["nome"].iloc[0]
        ) if "nome" in df.columns and (df["usuario_id"] == usuario_id).any() else "",
        "item_id": int(item_id),
        "gostou": 1 if gostou else 0,
        "origem": origem,  # "inicio", "recomendador" ou "outro"
    }

    df = pd.concat([df, pd.DataFrame([nova_linha])], ignore_index=True)

    # salva e atualiza cache
    df.to_csv(DATA_DIR / "usuarios.csv", index=False)
    _usuarios_df = df
