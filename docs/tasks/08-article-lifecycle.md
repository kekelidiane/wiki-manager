# Tâche 08 — Articles : CRUD et cycle de vie

> **Branche** : `feat/da/article-lifecycle`
> **Effort estimé** : 1,5 jour
> **Dépend de** : tâches 06 et 07
> **Référence** : [`docs/domain-model.md`](../domain-model.md) §4 (cycle
> de vie)


## Objectif

Le cœur du produit : créer, lire, modifier et supprimer des articles, et
gérer leur cycle de vie éditorial (brouillon, soumission, revue,
correction, publication). Les articles s'appuient sur les catégories
(tâche 06) et les médias (tâche 07).


## Livrables

```
src/app/api/dto/wiki/wiki_dto.py            # DTO article (create/update/response, correction)
src/app/api/routes/article/
├── __init__.py
└── article_api.py
src/app/services/article/
├── __init__.py
└── article_service.py
src/app/storage/rds/datastore/article/
├── __init__.py
└── article_store.py
src/app/storage/rds/datastore/interfaces/article.py
```

Tests :

```
tests/services/test_article_service.py
```


## Consignes

### 1. Création

`add_article` accepte uniquement un état initial `DRAFT` ou `SUBMITTED`
(tout autre état est rejeté en 400). Génère `article_id`, découpe les
`tags`, rattache catégories et médias, renseigne l'audit et le
`user_id` propriétaire.

### 2. Transitions

1. `update_and_resubmit` : l'auteur met à jour un article et le renvoie
   en soumission.
2. `request_correction` : un reviewer (`manager`/`director`) passe
   l'article en `CORRECTION_REQUESTED` avec un motif stocké dans
   `admin_review`.
3. `publish_article` : passe un article approuvé en `PUBLISHED`,
   réservé aux reviewers.

Chaque transition vérifie que l'état de départ est légal (par exemple on
ne publie pas un brouillon) et lève une erreur métier sinon.

### 3. Lecture et suppression

`get_article` renvoie l'article avec ses catégories, médias, couverture.
`delete_article` fait une **suppression logique** (`is_deleted = true`),
pas un DELETE physique.

### 4. Insertion multi-tables

L'insertion d'un article touche `articles`, `article_categories` et
`article_medias_gallery`. Fais-le dans une transaction pour éviter les
états partiels.


## Critères d'acceptation

1. Création acceptée seulement en `DRAFT`/`SUBMITTED`.
2. Les transitions illégales sont refusées avec une erreur métier
   explicite.
3. `request_correction` renseigne bien `admin_review`.
4. La suppression est logique, l'article disparaît des lectures
   standard.
5. Un article créé avec catégories et médias les retrouve à la lecture.
6. Les contrôles de rôle sont posés sur chaque opération.


## Avant de pousser

- [ ] `ruff` / `black` propres
- [ ] `pytest` vert, dont les transitions illégales
- [ ] Parcours manuel complet : créer, soumettre, demander correction,
      corriger, publier
