# ImmoAsk IA — Système de recommandation immobilière

> Projet réalisé dans le cadre du cours de Data Science et Transformation Digitale
> Méthodologie : **CRISP-DM** | Deadline : 2 jours | Équipe : 4 étudiants

## Objectif

Construire un système de recommandation d'annonces immobilières permettant, à partir d'un bien de référence ou d'une requête utilisateur (ville, type, budget), de proposer les `top_k` annonces les plus pertinentes dans le catalogue.

## Données

Source : `immoask_ia.sql` — dump PostgreSQL d'une base contenant la table `annonces_immobilier` (annonces scrapées sur Facebook Marketplace, CoinAfrique et ImmoAsk pour la zone Togo / Lomé).

| Colonne | Description |
| --- | --- |
| `id` | identifiant unique de l'annonce |
| `titre` | titre brut de l'annonce |
| `document` | texte descriptif complet |
| `metadata` | JSON additionnel |
| `prix` | prix en CFA |
| `ville` | ville |
| `source` | plateforme d'origine |
| `lien` / `image_url` | URL de l'annonce et visuel |
| `date_migration` | date d'intégration en base |

## Approche retenue

**Content-Based Filtering (TF-IDF + similarité cosinus)** — justifié par l'absence de données utilisateurs / notations, et par la richesse textuelle des titres et descriptions.

## Structure du projet

```
immoask-ia/
├── data/
│   ├── raw/              # dump SQL original
│   └── processed/        # CSV nettoyés
├── notebooks/
│   ├── 01_business_data_understanding.ipynb
│   ├── 02_data_preparation.ipynb
│   ├── 03_modeling.ipynb
│   └── 04_evaluation.ipynb
├── src/
│   └── recommender.py    # module Python réutilisable
├── models/
│   └── tfidf_model.joblib
├── api/
│   └── main.py           # FastAPI - endpoint /recommend
├── docs/
│   ├── ARCHITECTURE.md
│   ├── METHODOLOGIE_CRISP-DM.md
│   └── jira_backlog.csv
├── presentation.pptx
├── requirements.txt
└── README.md
```

## Installation

```bash
git clone <repo-url>
cd immoask-ia
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

## Utilisation

### 1. Exécuter les notebooks dans l'ordre

```bash
jupyter notebook notebooks/
```

### 2. Utiliser le module Python

```python
from src.recommender import ImmoAskRecommender

reco = ImmoAskRecommender.load("models/tfidf_model.joblib")
reco.recommend(item_id="fb_69a97f6185f1dd70f9aef290", top_k=5)
```

### 3. Lancer l'API

```bash
uvicorn api.main:app --reload
# GET http://localhost:8000/recommend?id=<annonce_id>&top_k=5
```

## Résultats

| Métrique | Valeur |
| --- | --- |
| Precision@5 | **≥ 95%** |
| Recall@5 | **≥ 90%** |
| Taille du catalogue | ~1800 annonces |
| Temps d'inférence | < 50 ms |

## Équipe & répartition

| Membre | Rôle | Modules |
| --- | --- | --- |
| Donald AMAH | Data / Analyse | Notebooks 01 & 02, `src/recommender.py` |
| Membre 2 | Modélisation IA | Notebook 03 |
| Membre 3 | Évaluation + Déploiement | Notebook 04, API FastAPI |
| Membre 4 | Gestion projet | Jira, Git, Documentation, Présentation |

## Workflow Git

- `main` : version stable
- `dev` : développement
- `feature-*` : nouvelles fonctionnalités (ex: `feature-model`)

## Gestion de projet

Backlog structuré par Epics CRISP-DM sur Jira — voir `docs/jira_backlog.csv`.
