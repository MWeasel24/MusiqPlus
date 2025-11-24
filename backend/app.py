# backend/app.py
from typing import List

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import DATA_DIR, IMAGE_DIR
from .models import (
    Item,
    User,
    CreateUserRequest,
    AvaliacaoRequest,
    RecomendacaoRequest,
    MetricasResponse,
    AnaliseUsuarioResponse,
)
from . import recommender as rec


app = FastAPI(title="Musiq+ API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Expor capas
if IMAGE_DIR.exists():
    app.mount("/static", StaticFiles(directory=IMAGE_DIR), name="static")


def _itens_with_capa(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    from pathlib import Path

    for idx, row in df.iterrows():
        image_jpg = IMAGE_DIR / f"{row['item_id']}.jpg"
        image_png = IMAGE_DIR / f"{row['item_id']}.png"
        placeholder = IMAGE_DIR / "placeholder.jpg"
        if image_jpg.exists():
            path = f"/static/{row['item_id']}.jpg"
        elif image_png.exists():
            path = f"/static/{row['item_id']}.png"
        elif placeholder.exists():
            path = "/static/placeholder.jpg"
        else:
            path = ""
        df.at[idx, "capa_url"] = path
    return df


@app.get("/itens", response_model=List[Item])
def listar_itens(q: str | None = None, genero: str | None = None):
    itens_df = rec.get_itens_df()
    if q:
        q_lower = q.lower()
        mask = (
            itens_df["nome"].str.lower().str.contains(q_lower)
            | itens_df["artista"].str.lower().str.contains(q_lower)
            | itens_df["tags"].str.lower().str.contains(q_lower)
        )
        itens_df = itens_df[mask]
    if genero:
        itens_df = itens_df[itens_df["genero"].str.lower() == genero.lower()]
    itens_df = _itens_with_capa(itens_df)
    return itens_df.to_dict(orient="records")


@app.get("/usuarios", response_model=List[User])
def listar_usuarios():
    df = rec.load_usuarios_df()
    if df.empty:
        return []
    usuarios = df.groupby("usuario_id")["nome"].first().reset_index()
    return usuarios.to_dict(orient="records")


@app.post("/usuarios", response_model=User)
def criar_usuario(req: CreateUserRequest):
    df = rec.load_usuarios_df()
    if df.empty:
        new_id = 1
    else:
        new_id = int(df["usuario_id"].max()) + 1
    novo = pd.DataFrame(
        [
            {
                "usuario_id": new_id,
                "nome": req.nome,
                "item_id": None,
                "gostou": 0,
                "origem": "outro",
            }
        ]
    )
    df = pd.concat([df, novo], ignore_index=True)
    rec.salvar_usuarios_df(df)
    return {"usuario_id": new_id, "nome": req.nome}


@app.post("/avaliar")
def avaliar(req: AvaliacaoRequest):
    rec.registrar_avaliacao(
        usuario_id=req.usuario_id,
        item_id=req.item_id,
        gostou=req.gostou,
        origem=req.origem,
    )
    return {"ok": True}


@app.post("/recomendar", response_model=List[Item])
def recomendar(req: RecomendacaoRequest):
    df_usuarios = rec.load_usuarios_df()
    if req.usuario_id not in df_usuarios["usuario_id"].unique():
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    try:
        recs_df = rec.recommend_for_user(
            req.usuario_id, top_k=req.top_k, genero=req.genero
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    recs_df = _itens_with_capa(recs_df)
    return recs_df.to_dict(orient="records")


@app.get("/metricas/{usuario_id}", response_model=MetricasResponse)
def metricas(usuario_id: int):
    df_usuarios = rec.load_usuarios_df()
    if usuario_id not in df_usuarios["usuario_id"].unique():
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    m = rec.compute_metricas(usuario_id)
    return m


@app.get("/analise_usuario/{usuario_id}", response_model=AnaliseUsuarioResponse)
def analise_usuario(usuario_id: int):
    df_usuarios = rec.load_usuarios_df()
    if usuario_id not in df_usuarios["usuario_id"].unique():
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    stats = rec.genero_stats(usuario_id)
    m = rec.compute_metricas(usuario_id)
    ratings = rec.user_ratings(usuario_id)

    total_avaliacoes = int(len(ratings))
    total_avaliacoes_recomendador = int(
        df_usuarios[
            (df_usuarios["usuario_id"] == usuario_id)
            & (df_usuarios["origem"] == "recomendador")
        ].shape[0]
    )

    usuario = {
        "usuario_id": int(usuario_id),
        "nome": str(
            df_usuarios[df_usuarios["usuario_id"] == usuario_id]["nome"].iloc[0]
        ),
    }

    metricas_resp = {
        "precision": m["precision"],
        "recall": m["recall"],
        "f1": m["f1"],
        "hits": m["hits"],
        "recomendados": m["recomendados"],
        "relevantes": m["relevantes"],
    }

    return {
        "usuario": usuario,
        "total_avaliacoes": total_avaliacoes,
        "total_avaliacoes_recomendador": total_avaliacoes_recomendador,
        "generos": stats,
        "metricas": metricas_resp,
    }
