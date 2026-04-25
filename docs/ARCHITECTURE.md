# Architecture technique — ImmoAsk IA

## Vue d'ensemble

```
┌─────────────────────────────────────────────────────────────────┐
│                    Source SQL (PostgreSQL dump)                  │
│                   data/raw/immoask_ia.sql                        │
└────────────────────────────┬────────────────────────────────────┘
                             │ src/sql_to_csv.py
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│            annonces_immobilier.csv (255 annonces)                │
└────────────────────────────┬────────────────────────────────────┘
                             │ notebook 02
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│         annonces_clean.csv + features métier                     │
│    type_transaction, type_bien, ville_norm, quartier,            │
│    texte_modele                                                  │
└────────────────────────────┬────────────────────────────────────┘
                             │ notebook 03
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│        models/tfidf_model.joblib                                 │
│   (vectorizer + matrice similarité + métadonnées)                │
└────────────────────────────┬────────────────────────────────────┘
                             │
                 ┌───────────┴───────────┐
                 ▼                       ▼
    ┌──────────────────────┐  ┌──────────────────────┐
    │  src/recommender.py  │  │   api/main.py        │
    │  (classe Python)     │  │   (FastAPI, REST)    │
    └──────────────────────┘  └──────────────────────┘
```

## Composants

### 1. Ingestion (`src/sql_to_csv.py`)
Parse le dump PostgreSQL et extrait la table `annonces_immobilier` en CSV quoted.

### 2. Notebooks CRISP-DM (`notebooks/`)
| Notebook | Phase CRISP-DM | Entrée | Sortie |
| --- | --- | --- | --- |
| `01_business_data_understanding.ipynb` | 1 & 2 | CSV brut | Rapport exploratoire + viz |
| `02_data_preparation.ipynb` | 3 | CSV brut | `annonces_clean.csv` |
| `03_modeling.ipynb` | 4 | `annonces_clean.csv` | `tfidf_model.joblib` |
| `04_evaluation.ipynb` | 5 | modèle + données | Métriques + bench |

### 3. Modèle hybride (`src/recommender.py`)
Classe `ImmoAskRecommender` qui combine :
- **Filtre dur** (rules-based) sur `type_bien` et `type_transaction` : garantit la cohérence métier des recommandations
- **Ranking souple** par similarité cosinus TF-IDF : ordonne les candidats par proximité sémantique

API de la classe :
```python
reco = ImmoAskRecommender.load("models/tfidf_model.joblib")
reco.recommend(item_id, top_k=5)             # depuis une annonce de référence
reco.recommend_from_query("chambre salon lome", top_k=5)   # depuis une requête texte libre
```

### 4. API de déploiement (`api/main.py`)
FastAPI expose le recommender en HTTP :

| Méthode | Endpoint | Description |
| --- | --- | --- |
| GET | `/` | Health check |
| GET | `/recommend?id=...&top_k=5` | Recommandations depuis une annonce |
| GET | `/search?query=...&top_k=5` | Recherche libre |
| GET | `/annonces?limit=20&offset=0` | Pagination du catalogue |

Lancement :
```bash
uvicorn api.main:app --reload
# Docs interactives Swagger : http://localhost:8000/docs
```

## Choix technologiques

| Choix | Alternatives | Justification |
| --- | --- | --- |
| **TF-IDF** | Word2Vec, Sentence-BERT | Simple, interprétable, déterministe, pas de GPU requis |
| **Cosine similarity** | Jaccard, BM25 | Robuste à la longueur variable, standard en reco content-based |
| **Filtres métier (hybride)** | Ranker unique | Garantit Accuracy ≥ 95%, évite les mismatches absurdes (terrain vs studio) |
| **scikit-learn** | TensorFlow, PyTorch | Volume de données faible, pas d'avantage du deep learning |
| **FastAPI** | Flask, Django | Auto-doc OpenAPI, validation Pydantic, performance async |
| **joblib** | pickle, mlflow | Compression gzip intégrée, standard sklearn |

## Performance

| Indicateur | Valeur mesurée |
| --- | --- |
| Precision@5 (hybride) | **100%** |
| Recall@5 (hybride) | **100%** |
| Precision@5 (baseline TF-IDF pur) | 83.5% |
| Taille du modèle sérialisé | ~250 KB |
| Latence d'inférence (recommend) | < 10 ms |
| Volume du catalogue | 255 annonces |

## Scalabilité

Pour passer à 100 000+ annonces :
- Remplacer la matrice dense `n×n` par un index approximatif (**Faiss**, **Annoy**) — la mémoire devient le facteur limitant à partir de ~10 000 items.
- Persister les embeddings dans un vector store (**pgvector**, **Qdrant**).
- Ajouter un cache Redis côté API sur les recommandations populaires.
