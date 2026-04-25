"""API FastAPI - ImmoAsk IA.

Lancement :
    uvicorn api.main:app --reload

Endpoints :
    GET /                       → status
    GET /recommend?id=...       → recommandations depuis une annonce existante
    GET /search?query=...       → recommandations depuis un texte libre
    GET /annonces?limit=20      → liste paginée du catalogue
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.recommender import ImmoAskRecommender, DEFAULT_MODEL_PATH


app = FastAPI(
    title="ImmoAsk IA — API de recommandation immobilière",
    description="Système de recommandation hybride (TF-IDF + filtres métier) pour annonces immobilières Togo.",
    version="1.0.0",
)


reco: Optional[ImmoAskRecommender] = None


@app.on_event("startup")
def load_model() -> None:
    global reco
    reco = ImmoAskRecommender.load(DEFAULT_MODEL_PATH)


@app.get("/")
def root():
    assert reco is not None
    return {
        "status": "ok",
        "model": "hybrid content-based (TF-IDF + rules)",
        "catalog_size": len(reco.ids),
    }


@app.get("/recommend")
def recommend(id: str, top_k: int = Query(5, ge=1, le=20)):
    """Recommande `top_k` annonces similaires à celle portant l'identifiant `id`."""
    assert reco is not None
    try:
        results = reco.recommend(id, top_k=top_k)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"reference_id": id, "top_k": top_k, "results": results}


@app.get("/search")
def search(
    query: str,
    top_k: int = Query(5, ge=1, le=20),
    type_bien: Optional[str] = None,
    type_transaction: Optional[str] = None,
):
    """Recommande `top_k` annonces correspondant à une requête texte libre."""
    assert reco is not None
    results = reco.recommend_from_query(
        query, top_k=top_k, type_bien=type_bien, type_transaction=type_transaction
    )
    return {"query": query, "top_k": top_k, "results": results}


@app.get("/annonces")
def list_annonces(limit: int = Query(20, ge=1, le=200), offset: int = Query(0, ge=0)):
    """Retourne un extrait du catalogue (utile pour tester le front)."""
    assert reco is not None
    end = offset + limit
    return {
        "total": len(reco.ids),
        "limit": limit,
        "offset": offset,
        "items": reco.meta[offset:end],
    }
