"""Convertit le dump PostgreSQL `immoask_ia.sql` en CSV exploitable par pandas.

Le dump contient une instruction :
    COPY public.annonces_immobilier (col1, col2, ...) FROM stdin;
suivie de lignes tabulées puis d'un `\.` final.

Ce script extrait uniquement cette section et la sauvegarde en CSV propre
dans `data/processed/annonces_immobilier.csv`.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = PROJECT_ROOT / "data" / "raw" / "immoask_ia.sql"
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "processed" / "annonces_immobilier.csv"


def parse_pg_copy(sql_path: Path) -> tuple[list[str], list[list[str]]]:
    """Extrait la section COPY ... FROM stdin du dump et renvoie (colonnes, lignes)."""
    text = sql_path.read_text(encoding="utf-8")
    # Recherche du bloc COPY ... FROM stdin; ... \.
    m = re.search(
        r"COPY public\.annonces_immobilier \(([^)]+)\) FROM stdin;\n(.*?)\n\\\.",
        text,
        flags=re.DOTALL,
    )
    if not m:
        raise RuntimeError("Bloc COPY introuvable dans le dump SQL.")
    columns = [c.strip() for c in m.group(1).split(",")]
    raw_rows = m.group(2).split("\n")
    rows: list[list[str]] = []
    for raw in raw_rows:
        if not raw:
            continue
        # Les champs sont séparés par des tabulations
        fields = raw.split("\t")
        # PostgreSQL représente NULL par \N
        fields = [None if f == r"\N" else f for f in fields]
        rows.append(fields)
    return columns, rows


def write_csv(columns: list[str], rows: list[list[str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, quoting=csv.QUOTE_ALL)
        w.writerow(columns)
        for r in rows:
            w.writerow(r)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    columns, rows = parse_pg_copy(args.input)
    write_csv(columns, rows, args.output)

    # Validation rapide : on s'assure que la colonne metadata (JSON) est bien parseable
    meta_idx = columns.index("metadata") if "metadata" in columns else None
    if meta_idx is not None:
        ok = 0
        ko = 0
        for r in rows:
            try:
                if r[meta_idx]:
                    json.loads(r[meta_idx])
                ok += 1
            except Exception:
                ko += 1
        print(f"JSON metadata : {ok} OK / {ko} KO")

    print(f"Colonnes : {columns}")
    print(f"{len(rows)} lignes extraites → {args.output}")


if __name__ == "__main__":
    main()
