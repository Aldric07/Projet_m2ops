# Contribuer à La gazette

## Branches

- `main` est **toujours déployable**. Personne ne pousse directement dessus : elle est protégée sur GitHub.
- Une branche par sujet, créée depuis `main` à jour :
  - `feat/<sujet>` pour une fonctionnalité, ex. `feat/collecte-sud-ouest`
  - `fix/<sujet>` pour une correction
  - `docs/<sujet>`, `ci/<sujet>`, `infra/<sujet>`
- Une branche courte : on la merge en un ou deux jours, puis on la supprime.

## Commits

Format [Conventional Commits](https://www.conventionalcommits.org/fr/), en français :

```
feat(collecte): lire le flux de Sud Ouest
fix(parseur): ignorer les items sans lien
docs(cadrage): préciser les conditions du Monde
```

Types : `feat`, `fix`, `docs`, `test`, `ci`, `infra`, `refactor`, `chore`.

## Pull request et merge

1. Avant de pousser, lance `bin/test` en local.
2. Ouvre une pull request vers `main` en disant **ce qui change et comment le vérifier**.
3. **Une relecture** par un autre membre de l'équipe (Cheick, Yoann ou Aurelien) est obligatoire.
4. La **CI doit être verte** (lint, tests, build) : une CI rouge bloque le merge.
5. **L'auteur merge** lui-même, en *squash merge*, une fois la PR approuvée et la CI verte.

## Règles du projet

- On ne stocke jamais le texte intégral, le nom des auteurs ni les images d'un article. Les tests le vérifient : ne les supprime pas.
- Toute nouvelle source passe d'abord par `sources.csv`, avec son `robots.txt` et ses conditions vérifiés.
- Rien ne s'installe à la main : ce qui tourne est décrit dans le dépôt (`Dockerfile`, `docker-compose.yml`, `infra/`).
- Aucun secret dans le dépôt : mets-les dans un fichier `.env` (ignoré par Git) ou dans les secrets GitHub.
