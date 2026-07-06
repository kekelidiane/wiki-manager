# Tâche 13 — Durcissement sécurité et conteneurisation

> **Branche** : `feat/da/security-docker`
> **Effort estimé** : 0,5 jour
> **Dépend de** : tâche 01


## Objectif

Fermer les points faibles de configuration hérités de l'ancien projet et
livrer une image conteneur exploitable. Dans `wiki`, le CORS autorisait
toutes les origines avec `allow_credentials`, le TrustedHost acceptait
tout hôte, et le Dockerfile de `wiki-chat` n'était même pas fonctionnel.


## Livrables

```
src/app/server/server.py           # CORS et TrustedHost durcis, pilotés par config
src/app/configs/environment.py      # WIKI_ALLOWED_ORIGINS, WIKI_ALLOWED_HOSTS
Dockerfile                          # image Python réelle qui lance le service
docker-compose.yml                  # api + postgres + minio + stack observabilité
.dockerignore
.env.example                        # complété
```


## Consignes

### 1. CORS

Remplace `allow_origins=["*"]` par une liste d'origines lue en config.
Rappelle-toi que `allow_credentials=True` est **incompatible** avec une
origine `*` : soit on liste les origines et on garde les credentials,
soit pas de credentials. Choisis la liste d'origines explicite.

### 2. TrustedHost

`allowed_hosts` vient de la config, valeurs de production réelles, pas
`*`.

### 3. Dockerfile

Image basée sur un `python:3.11-slim`, installe le projet, expose le port
et lance `run.py` (ou uvicorn). Pas d'`ubuntu:latest` avec un entrypoint
bidon. Utilisateur non-root de préférence.

### 4. docker-compose

Monte l'API, PostgreSQL, MinIO et la stack d'observabilité (collector,
prometheus) pour un environnement de dev reproductible. Les secrets
passent par variables d'environnement / fichier `.env`, jamais commités.


## Critères d'acceptation

1. Le CORS n'autorise que les origines configurées, cohérent avec les
   credentials.
2. Le TrustedHost n'accepte que les hôtes configurés.
3. `docker build` produit une image qui démarre et répond sur `/health`.
4. `docker compose up` monte l'ensemble de la stack de dev.
5. Aucun secret dans l'image ni dans le compose.


## Avant de pousser

- [ ] `ruff` / `black` propres
- [ ] `docker build` et run vérifiés
- [ ] `docker compose up` monte la stack
- [ ] Test CORS manuel depuis une origine non autorisée (doit être
      bloqué)
