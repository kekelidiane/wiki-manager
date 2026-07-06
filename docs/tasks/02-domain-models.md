# Tâche 02 — Modèles de domaine (SQLModel)

> **Branche** : `feat/da/domain-models`
> **Effort estimé** : 1 jour
> **Dépend de** : tâche 01
> **Référence** : [`docs/domain-model.md`](../domain-model.md) — à lire
> entièrement avant de commencer. C'est la source de vérité.


## Objectif

Créer les classes **SQLModel** qui correspondent aux tables PostgreSQL,
les deux énumérations et les tables de liaison. **Pas de CRUD, pas
d'endpoints, pas encore de migration Alembic** — juste les modèles et
leurs relations.

Le reviewer vérifie que le code correspond à `docs/domain-model.md`
exactement : noms de colonnes, types, contraintes, index.


## Livrables

```
src/app/models/
├── __init__.py                   # réexporte les modèles pour import court
├── common/
│   ├── __init__.py
│   └── audit.py                  # AuditMixin
└── wiki/
    ├── __init__.py
    └── wiki_models.py            # entités + enums + tables de liaison
```

Tests :

```
tests/models/
├── __init__.py
└── test_wiki_models.py
```


## Consignes

### 1. Mixin d'audit

Factorise les cinq colonnes d'audit (`created_by`, `created_at`,
`updated_by`, `updated_at`, `version`) dans `common/audit.py`. Chaque
entité en hérite au lieu de recopier ces champs.

### 2. Énumérations

`Status` et `ReactionType` héritent de `(str, Enum)`, valeurs en
UPPER_SNAKE identiques à leur nom.

### 3. Entités

Crée `Category`, `Media`, `Article`, `Comment`, `ArticleReaction`, plus
les tables de liaison `ArticleCategoryLink` (`article_categories`) et
`ArticleMediaLink` (`article_medias_gallery`).

1. Chaque entité a un `id` int (clé primaire interne, `exclude=True`) et
   un `<entity>_id` str unique public.
2. `Article.tags` et `Article.sources` sont des colonnes `JSON`.
3. `Article.is_deleted` et `Comment.is_deleted` sont `exclude=True`
   (jamais renvoyés à l'API).
4. `ArticleReaction` porte la contrainte d'unicité composite
   `(article_id, user_id)` nommée `uq_article_reactions_article_user`.
5. Déclare les relations (`Relationship`) : catégories, galerie de
   médias, commentaires, réactions, plus la couverture via
   `cover_image_id`.
6. Respecte les index indiqués dans la référence (`title`, `state`,
   `user_id`, `admin_review`, `article_id`, `user_id`, `reaction`).


## Critères d'acceptation

1. Les cinq entités, les deux enums et les deux tables de liaison sont
   définis et correspondent à `docs/domain-model.md`.
2. `SQLModel.metadata.tables` contient les sept tables attendues.
3. Un test instancie chaque modèle avec des valeurs valides sans erreur.
4. Les colonnes `exclude=True` n'apparaissent pas dans
   `model_dump()`.
5. Aucun accès base ici : les tests n'ouvrent pas de connexion.


## Avant de pousser

- [ ] `ruff check src tests` propre
- [ ] `black --check src tests` propre
- [ ] `pytest` vert
- [ ] Relecture croisée avec `docs/domain-model.md`
