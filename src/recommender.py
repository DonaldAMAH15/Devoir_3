"""Module Python réutilisable : moteur de recommandation ImmoAsk IA.

Il encapsule le modèle hybride (filtres métier + similarité cosinus TF-IDF)
entraîné dans le notebook 03 et sauvegardé dans `models/tfidf_model.joblib`.

Exemple d'utilisation :

>>> from src.recommender import ImmoAskRecommender
>>> reco = ImmoAskRecommender.load("models/tfidf_model.joblib")
>>> reco.recommend("fb_69a97f6185f1dd70f9aef290", top_k=5)
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


DEFAULT_MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "tfidf_model.joblib"


@dataclass
class ImmoAskRecommender:
    """Moteur de recommandation immobilière content-based hybride.

    - `vectorizer`  : TfidfVectorizer entraîné
    - `sim_matrix`  : matrice de similarité cosinus (n×n)
    - `ids`         : liste des ids d'annonces dans l'ordre de la matrice
    - `meta`        : liste de dicts (métadonnées des annonces)
    """

    vectorizer: TfidfVectorizer
    sim_matrix: np.ndarray
    ids: list[str]
    meta: list[dict[str, Any]]

    # -------------------------- I/O --------------------------
    @classmethod
    def load(cls, path: str | Path = DEFAULT_MODEL_PATH) -> "ImmoAskRecommender":
        artifact = joblib.load(Path(path))
        return cls(
            vectorizer=artifact["vectorizer"],
            sim_matrix=np.asarray(artifact["sim_matrix"], dtype="float32"),
            ids=list(artifact["ids"]),
            meta=list(artifact["meta"]),
        )

    def save(self, path: str | Path = DEFAULT_MODEL_PATH) -> None:
        joblib.dump(
            {
                "vectorizer": self.vectorizer,
                "sim_matrix": self.sim_matrix.astype("float32"),
                "ids": self.ids,
                "meta": self.meta,
            },
            Path(path),
            compress=3,
        )

    # -------------------------- Core API --------------------------
    @property
    def _df(self) -> pd.DataFrame:
        return pd.DataFrame(self.meta)

    def _index_of(self, item_id: str) -> int:
        if item_id not in self.ids:
            raise KeyError(f"id inconnu : {item_id}")
        return self.ids.index(item_id)

    def recommend(
        self,
        item_id: str,
        top_k: int = 5,
        filtre_transaction: bool = True,
        filtre_type_bien: bool = True,
    ) -> list[dict[str, Any]]:
        """Retourne les top_k annonces les plus similaires à `item_id`.

        Applique le filtre dur (rules-based) puis le ranking par cosinus.
        """
        idx = self._index_of(item_id)
        df = self._df
        scores = self.sim_matrix[idx].astype(float).copy()

        mask = np.ones(len(df), dtype=bool)
        if filtre_transaction:
            mask &= (df["type_transaction"] == df.loc[idx, "type_transaction"]).values
        if filtre_type_bien:
            mask &= (df["type_bien"] == df.loc[idx, "type_bien"]).values
        mask[idx] = False

        scores = np.where(mask, scores, -1.0)
        order = np.argsort(scores)[::-1][:top_k]
        order = [int(j) for j in order if scores[j] >= 0]

        result = []
        for j in order:
            row = df.iloc[j].to_dict()
            row["score"] = round(float(scores[j]), 4)
            result.append(row)
        return result

    def recommend_from_query(
        self,
        query: str,
        top_k: int = 5,
        type_bien: str | None = None,
        type_transaction: str | None = None,
    ) -> list[dict[str, Any]]:
        """Recommandation à partir d'une requête texte libre (pas d'annonce de ref).

        Utile pour un formulaire de recherche utilisateur.
        """
        import unicodedata

        def normalize(s: str) -> str:
            nfkd = unicodedata.normalize("NFD", s)
            return "".join(c for c in nfkd if not unicodedata.combining(c)).lower()

        q_vec = self.vectorizer.transform([normalize(query)])
        # On recalcule la similarité entre la requête et tout le catalogue
        X_all = self.vectorizer.transform([normalize(m.get("texte_modele", "")
                                                      if "texte_modele" in m
                                                      else m.get("titre", ""))
                                           for m in self.meta])
        scores = cosine_similarity(q_vec, X_all).ravel()

        df = self._df
        mask = np.ones(len(df), dtype=bool)
        if type_bien:
            mask &= (df["type_bien"] == type_bien).values
        if type_transaction:
            mask &= (df["type_transaction"] == type_transaction).values
        scores = np.where(mask, scores, -1.0)

        order = np.argsort(scores)[::-1][:top_k]
        order = [int(j) for j in order if scores[j] >= 0]
        result = []
        for j in order:
            row = df.iloc[j].to_dict()
            row["score"] = round(float(scores[j]), 4)
            result.append(row)
        return result


# -------------------------- CLI --------------------------
def _cli() -> None:
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Recommander ImmoAsk IA")
    parser.add_argument("--id", required=False, help="ID d'annonce de référence")
    parser.add_argument("--query", required=False, help="Requête texte libre")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL_PATH)
    args = parser.parse_args()

    reco = ImmoAskRecommender.load(args.model)
    if args.id:
        out = reco.recommend(args.id, top_k=args.top_k)
    elif args.query:
        out = reco.recommend_from_query(args.query, top_k=args.top_k)
    else:
        print("Spécifier --id ou --query")
        return
    print(json.dumps(out, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    _cli()
