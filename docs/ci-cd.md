# Stratégie CI/CD

1. **Outil** : GitHub Actions (`.github/workflows/ci.yml`) ; registre d'images : `ghcr.io`.
2. **Déclencheurs** : chaque pull request, et chaque push sur `main`.
3. **Étapes** : `lint` (ruff) et `test` (pytest) en parallèle, puis `build`, uniquement si les deux passent.
4. **Pull request** : l'image est construite mais pas publiée, pour vérifier le `Dockerfile` avant le merge.
5. **Push sur `main`** : l'image est construite et publiée sur `ghcr.io/<dépôt>`.
6. **Tag** : `YYYYMMDDHHMMSS-sha` (date UTC du build et sha court du commit), plus `latest`, pour savoir d'où vient chaque image.
7. **Image** : multi-étapes, basée sur `python:3.12-slim`, sans outils de build, exécutée par un utilisateur non root (uid 10001).
8. **Garde-fou** : `main` est protégée. Le merge exige une PR relue et les trois jobs verts ; une CI rouge bloque le merge.
9. **Tests** : flux enregistrés dans `tests/fixtures/`, aucun appel réseau en CI. On y vérifie qu'aucun texte intégral, auteur ou image n'est conservé.
10. **Hors périmètre pour l'instant** : pas de déploiement automatique (prévu au TD 7), pas de matrice de versions, pas de cache avancé.
