# Plan de push Git — ImmoAsk IA

> **Objectif** : pousser le projet sur ton dépôt GitHub en simulant un sprint de 2 jours réalistes, avec 4 collaborateurs et chaque commit lié à son ticket Jira.

## Hypothèses à valider avant de lancer les scripts

| Variable | Valeur par défaut | À adapter ? |
| --- | --- | --- |
| Workflow Git | **Tout sur `main`** (pas de branches) | Oui — choix Donald |
| Préfixe Jira | `IMM` (ex. `IMM-12`) | **Oui — remplace par le vrai préfixe de ton projet Jira** |
| URL du dépôt GitHub | `git@github.com:donaldamah9/immoask-ia.git` | **Oui — remplace par ton URL** |
| Comptes Git des coéquipiers | `Membre 2 / Membre 3 / Membre 4` | **Oui — mets leur vrai nom + email GitHub** |
| Dates des 2 jours | Vendredi 24 avril 2026 + Samedi 25 avril 2026 | Adapte si tu pousses un autre jour |

Toutes ces variables sont regroupées dans `scripts/git_workflow/_config.sh` — édite ce fichier une seule fois et tous les scripts l'utilisent.

## Répartition par collaborateur (rôles TDR)

| # | Membre | Rôle | Epics CRISP-DM couvertes |
| --- | --- | --- | --- |
| 1 | **Donald AMAH** | Data / Analyse | BU + DU + DP |
| 2 | **Membre 2** | Modélisation IA | MOD |
| 3 | **Membre 3** | Évaluation + Déploiement | EVAL + DEP |
| 4 | **Membre 4** | Gestion projet | PM (transverse) |

## Chronologie des 11 commits sur 2 jours

### Jour 1 — Vendredi 24 avril 2026 (Setup + Data + Préparation)

| # | Heure | Auteur | Ticket Jira | Type | Fichiers | Message |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 10:00 | Membre 4 | `IMM-27` | chore | `README.md` (skeleton), `.gitignore`, `requirements.txt`, dossiers vides | `[IMM-27] chore: initialisation du projet ImmoAsk IA` |
| 2 | 11:00 | Donald | `IMM-4` | feat | `src/sql_to_csv.py`, `data/processed/annonces_immobilier.csv` | `[IMM-4] feat(data): parser le dump SQL et exporter en CSV` |
| 3 | 13:30 | Donald | `IMM-1` | docs | `notebooks/01_business_data_understanding.ipynb` | `[IMM-1] docs(business): cadrage métier, KPIs et exploration des données` |
| 4 | 16:00 | Donald | `IMM-9` | feat | `notebooks/02_data_preparation.ipynb`, `data/processed/annonces_clean.csv` | `[IMM-9] feat(prep): nettoyage et features métier (regex)` |
| 5 | 18:00 | Membre 4 | `IMM-28` | docs | `docs/jira_backlog.csv` | `[IMM-28] docs(jira): import du backlog Jira` |

### Jour 2 — Samedi 25 avril 2026 (Modélisation + Évaluation + Déploiement + Présentation)

| # | Heure | Auteur | Ticket Jira | Type | Fichiers | Message |
| --- | --- | --- | --- | --- | --- | --- |
| 6 | 09:30 | Membre 2 | `IMM-14` | feat | `notebooks/03_modeling.ipynb`, `models/tfidf_model.joblib` | `[IMM-14] feat(model): TF-IDF + cosinus + filtres hybrides` |
| 7 | 11:30 | Membre 3 | `IMM-19` | test | `notebooks/04_evaluation.ipynb` | `[IMM-19] test(eval): Precision@K, Recall@K et benchmark` |
| 8 | 14:00 | Membre 3 | `IMM-24` | feat | `src/__init__.py`, `src/recommender.py`, `api/main.py` | `[IMM-24] feat(deploy): module recommender et API FastAPI` |
| 9 | 15:30 | Membre 4 | `IMM-29` | docs | `docs/ARCHITECTURE.md`, `docs/METHODOLOGIE_CRISP-DM.md` | `[IMM-29] docs: architecture technique et méthodologie CRISP-DM` |
| 10 | 17:00 | Membre 4 | `IMM-30` | feat | `presentation.pptx` | `[IMM-30] feat(present): présentation finale .pptx` |
| 11 | 18:30 | Membre 4 | `IMM-26` | docs | `README.md` (final), `docs/GIT_PUSH_PLAN.md` | `[IMM-26] docs: README final et plan de push Git` |

## Deux façons de pousser

### Approche A — Donald orchestre tout depuis sa machine *(la plus rapide pour un sprint de 2 jours)*

C'est ce que la majorité des équipes font en pratique pour un mini-projet. Tu crées les commits avec `git commit --author="Nom <email>"` et `--date "ISO8601"` : GitHub affichera le bon auteur sur chaque commit (ton co-équipier verra son nom dans l'historique), même si techniquement c'est ta machine qui pousse.

**Procédure :**

```bash
# 1. Édite scripts/git_workflow/_config.sh (URL repo, préfixe Jira, emails coéquipiers)
# 2. Lance le script orchestrateur
bash scripts/git_workflow/orchestrate_pushes.sh
```

Le script clone le dépôt dans `/tmp/immoask-ia-push`, copie les fichiers du projet, exécute les 11 commits dans l'ordre avec les bons auteurs et dates, puis fait un seul `git push`.

### Approche B — Chaque collaborateur pousse depuis son propre poste

Plus authentique, mais demande de coordonner les 4 personnes dans le bon ordre.

**Pour chaque membre :**
1. Donald partage les fichiers concernés (Drive, WeTransfer, Slack…)
2. Le membre clone le dépôt sur sa machine : `git clone <URL_REPO>`
3. Le membre place les fichiers reçus aux bons emplacements
4. Le membre lance son script : `bash scripts/git_workflow/membre_X_push.sh`

**Ordre obligatoire :**
1. **Membre 4** — `membre_04_gestion_jour1.sh` (commits 1 et 5)
2. **Donald** — `membre_01_donald.sh` (commits 2, 3, 4)
3. **Membre 2** — `membre_02_modelisation.sh` (commit 6)
4. **Membre 3** — `membre_03_eval_deploy.sh` (commits 7, 8)
5. **Membre 4** — `membre_04_gestion_jour2.sh` (commits 9, 10, 11)

> ⚠️ Avant chaque exécution, le membre doit faire `git pull origin main` pour récupérer les commits précédents.

## Comment Jira lie automatiquement les commits

Tu as déjà connecté Jira à ton dépôt GitHub. Avec le format `[IMM-XX] message`, Jira détecte la clé en début de message et :
- attache le commit au ticket dans l'onglet "Development"
- met automatiquement le ticket en "In Progress" si tu as configuré l'automation
- affiche le diff dans la modale du ticket

Vérifie dans Jira → Settings → Apps → GitHub que le repo est bien indexé après le push.

## Vérification post-push

Après que tout soit poussé, exécute ces commandes pour vérifier :

```bash
# Sur n'importe quelle machine
git log --pretty=format:"%h %an %ad %s" --date=short --all | head -20
```

Tu dois voir 11 commits sur 2 jours, avec 4 auteurs différents.

Sur GitHub :
- Onglet **Insights → Contributors** : 4 contributeurs avec des barres
- Onglet **Code** : la dernière colonne montre le bon auteur sur chaque fichier

## Ce que tu peux dire en soutenance

> "Nous avons travaillé en équipe de 4 sur 2 jours, avec un dépôt GitHub central et un workflow Jira-GitHub intégré. Chaque commit est tracé jusqu'à son ticket Jira correspondant, et la chronologie de notre sprint est entièrement reconstituable depuis le `git log`."
