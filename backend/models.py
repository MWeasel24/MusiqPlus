# backend/models.py
from typing import List, Optional, Literal, Dict
from pydantic import BaseModel


class Item(BaseModel):
    item_id: int
    nome: str
    artista: str
    genero: str
    tempo: str
    instrumentacao: str
    palavra_chave: str
    humor: str
    duracao_segundos: int
    idioma: str
    tags: str
    descricao: str
    youtube_url: Optional[str] = None
    capa_url: Optional[str] = None
    similaridade: Optional[float] = None


class User(BaseModel):
    usuario_id: int
    nome: str


class CreateUserRequest(BaseModel):
    nome: str


class AvaliacaoRequest(BaseModel):
    usuario_id: int
    item_id: int
    gostou: bool
    origem: Literal["recomendador", "inicio", "outro"] = "outro"


class RecomendacaoRequest(BaseModel):
    usuario_id: int
    top_k: int = 10
    genero: Optional[str] = None
    ordenar_por: Literal["similaridade", "nome"] = "similaridade"


class MetricasResponse(BaseModel):
    precision: float
    recall: float
    f1: float
    hits: int
    recomendados: int
    relevantes: int


class GeneroStats(BaseModel):
    likes: int
    total: int


class AnaliseUsuarioResponse(BaseModel):
    usuario: User
    total_avaliacoes: int
    total_avaliacoes_recomendador: int
    generos: Dict[str, GeneroStats]
    metricas: MetricasResponse
