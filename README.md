# La gazette

Revue de presse automatique : chaque matin à 7 h, les thèmes qui occupent la presse régionale et nationale, avec les liens vers les articles. Voir [docs/cadrage.md](docs/cadrage.md).

![CI](https://github.com/Aldric07/Projet_m2ops/actions/workflows/ci.yml/badge.svg)

## Lancer (deux commandes)

Prérequis : **Docker** (avec Compose) et **Git**.

```bash
git clone https://github.com/Aldric07/Projet_m2ops.git la-gazette && cd la-gazette
bin/dev
```

`bin/dev` démarre Postgres, construit l'image puis collecte une source (La Croix par défaut). Il affiche le nombre d'items et le fichier JSON écrit. Pour une autre source de [sources.csv](sources.csv) :

```bash
bin/dev --source "Sud Ouest"
```

Pour arrêter l'environnement : `docker compose down` (ajoute `-v` pour effacer aussi les données).

## Tester

```bash
bin/test
```

Lance le lint (`ruff`) et les tests (`pytest`) dans un conteneur : seul Docker est nécessaire. Sans Docker : `python3.12 -m venv .venv && .venv/bin/pip install -e ".[dev]" && .venv/bin/pytest`.

## Arborescence

| Chemin | Contenu |
|---|---|
| `src/gazette/` | Code : `collect.py` lit un flux et écrit le brut en JSON |
| `tests/` | Tests ; `tests/fixtures/` contient des flux enregistrés |
| `infra/` | Infrastructure en code (`postgres/init.sql` pour l'instant) |
| `docs/` | Note de cadrage, stratégie CI/CD |
| `bin/` | `dev` et `test` |
| `sources.csv` | Les sources, leur flux et leurs conditions |

## Contribuer

Lire [CONTRIBUTING.md](CONTRIBUTING.md) : une branche par sujet, une pull request relue, et la CI doit être verte avant le merge.
