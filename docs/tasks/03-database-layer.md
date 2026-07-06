# Tâche 03 — Couche base de données (asyncpg + query builders sûrs)

> **Branche** : `feat/da/database-layer`
> **Effort estimé** : 1 jour
> **Dépend de** : tâche 02


## Objectif

Mettre en place l'accès PostgreSQL asynchrone via un pool `asyncpg` et
des générateurs de requêtes réutilisables (`Select`, `Insert`,
`Update`). C'est ici qu'on corrige un **défaut de sécurité de l'ancien
projet** : dans `wiki`, le `SelectQueryBuilder` interpolait `order_by`,
`limit`, `offset` et les noms de colonnes directement dans la chaîne SQL,
ce qui ouvrait une injection. On paramétrise les valeurs et on met les
identifiants (colonnes, sens de tri) sur liste blanche.


## Livrables

```
src/app/storage/rds/
├── __init__.py
├── clients/
│   ├── __init__.py
│   └── database_manager.py       # DataBaseManager (pool asyncpg)
├── commons/
│   ├── __init__.py
│   ├── json_utils.py             # to_json / from_json
│   ├── sql_query_builder.py      # Select/Insert/Update builders
│   └── exceptions/
│       ├── __init__.py
│       └── dao_exception.py
└── datastore/
    └── interfaces/
        ├── __init__.py
        └── database_manager.py   # IPostgresDatabaseManager
```

Tests :

```
tests/storage/
├── __init__.py
└── test_sql_query_builder.py
```


## Consignes

### 1. DataBaseManager

Reprend le pattern de l'ancien `wiki` : `connect()` crée le pool à partir
de la chaîne de connexion et des tailles min/max lues en config,
`close()` le ferme, `_ensure_pool()` lève une erreur claire si on
l'utilise avant init. Méthodes `execute`, `execute_many`, `fetch`,
`fetch_row`, `fetch_value`.

Améliore la gestion d'erreur par rapport à l'ancien code : **pas de
`print`**, on loggue via le logger et on relève une exception dédiée
(`DaoException`) en conservant la cause (`raise ... from e`).

### 2. Query builders — sécurité d'abord

`InsertQueryBuilder` et `UpdateQueryBuilder` : génèrent des requêtes
paramétrées (`$1, $2, …`) à partir des colonnes du modèle.

`SelectQueryBuilder` : c'est le point sensible.

1. Les **valeurs** des clauses `WHERE` sont toujours des paramètres
   (`$n`), jamais concaténées.
2. Les **noms de colonnes** (WHERE, `order_by`, colonnes sélectionnées)
   sont validés contre la liste des colonnes réelles du modèle
   (`model_cls.__table__.columns`). Toute colonne inconnue lève une
   erreur, elle n'atteint jamais le SQL.
3. `order_dir` est contraint à `ASC` ou `DESC` (rien d'autre accepté).
4. `limit` et `offset` sont castés en `int` avant usage.

### 3. json_utils

`to_json` / `from_json` pour sérialiser les colonnes JSON (`tags`,
`sources`) au passage vers/depuis asyncpg.


## Critères d'acceptation

1. Le pool se connecte et se ferme proprement (test avec une base locale
   ou un pool mocké).
2. `SelectQueryBuilder` avec un `order_by` ou une colonne WHERE inconnue
   **lève une erreur** et ne produit pas de SQL.
3. Un `order_dir` autre que ASC/DESC est rejeté ou normalisé, jamais
   injecté.
4. Les valeurs WHERE ressortent bien comme paramètres, vérifiable dans la
   requête générée (présence de `$1`, absence de la valeur en clair).
5. Aucune utilisation de `print` dans la couche.


## Avant de pousser

- [ ] `ruff check src tests` propre
- [ ] `black --check src tests` propre
- [ ] `pytest` vert, dont les cas d'injection rejetés
- [ ] Revue manuelle : aucune interpolation de variable non validée dans
      une chaîne SQL


## Pour référence

Voir `sql_query_builder.py` de l'ancien `wiki` pour la structure des
builders — mais **relis la section « injection »** : c'est précisément ce
qu'on ne reproduit pas.
