# Tâche 04 — Migrations Alembic

> **Branche** : `feat/da/alembic-migrations`
> **Effort estimé** : 0,5 jour
> **Dépend de** : tâche 03


## Objectif

Brancher Alembic sur les modèles SQLModel et produire la migration
initiale qui crée toutes les tables du domaine. À la fin, `alembic
upgrade head` monte un schéma vide jusqu'à l'état complet.


## Livrables

```
alembic.ini
migrations/
├── env.py                        # configure la target metadata sur SQLModel
├── script.py.mako
└── versions/
    └── <hash>_init_tables.py     # création de toutes les tables
```

Plus le check de santé base branché sur le health check existant :

```
src/app/storage/rds/datastore/health/
├── __init__.py
└── health_check_provider.py
```


## Consignes

### 1. Configuration Alembic

`migrations/env.py` pointe `target_metadata` sur
`SQLModel.metadata` (après import des modèles de la tâche 02) et lit
l'URL de connexion depuis la configuration, **pas en dur** dans
`alembic.ini`.

### 2. Migration initiale

1. Génère l'autogénération, puis **relis-la** : l'autogen se trompe
   souvent sur les types JSON, les contraintes composites et les index.
2. Vérifie la présence de la contrainte
   `uq_article_reactions_article_user` et des deux tables de liaison.
3. `downgrade()` supprime les tables dans l'ordre inverse des
   dépendances.

### 3. Health check base

Ajoute un provider qui exécute un `SELECT 1` et l'expose. On enrichit
l'endpoint `/health` pour renvoyer l'état de la base (up/down).


## Critères d'acceptation

1. `alembic upgrade head` sur une base vide crée les sept tables sans
   erreur.
2. `alembic downgrade base` supprime tout proprement.
3. La contrainte d'unicité des réactions et les index de la référence
   sont présents dans le schéma généré.
4. `/health` reflète l'état réel de la base.


## Avant de pousser

- [ ] `alembic upgrade head` puis `downgrade base` testés sur base locale
- [ ] `ruff` / `black` propres
- [ ] `pytest` vert
- [ ] Migration relue à la main, pas juste autogénérée
