# wiki-manager

Backend de la base de connaissances interne, construit avec FastAPI.

Ce dépôt reconstruit proprement l'ancien service `wiki` : rédaction et
publication d'articles classés par catégories, illustrés de médias,
commentés et notés, avec authentification Keycloak et stockage objet
S3/MinIO.

Le travail est découpé en tâches incrémentales. Commence par lire
[`docs/tasks/README.md`](docs/tasks/README.md), puis fais les tâches dans
l'ordre. Le schéma de données de référence est dans
[`docs/domain-model.md`](docs/domain-model.md).


## Prérequis

1. Python 3.11 ou plus
2. PostgreSQL
3. Un stockage objet S3 (MinIO en local)
4. Un realm Keycloak pour l'authentification


## Démarrage

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install ".[dev]"
cp .env.example .env      # renseigne les variables
python run.py
```

Documentation Swagger : `http://localhost:8080/api/v1/wiki/documentation`


## Qualité

```bash
ruff check src tests
black --check src tests
pytest
```


## Organisation du dépôt

1. Branche par défaut de travail : `develop`.
2. Une branche par tâche : `feat/da/<slug>` depuis `develop`.
3. Le détail du workflow (branches, commits, PR, review) est dans
   [`docs/tasks/README.md`](docs/tasks/README.md).
