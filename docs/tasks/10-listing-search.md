# Tâche 10 — Listing, recherche et pagination

> **Branche** : `feat/da/listing-search`
> **Effort estimé** : 1 jour
> **Dépend de** : tâche 08


## Objectif

Exposer la consultation en liste des articles : pagination, filtres
(état, tags, recherche texte) et une vue « admin » qui filtre aussi par
auteur. C'est ici que le `SelectQueryBuilder` sûr de la tâche 03 prouve
sa valeur : tous les tris et filtres passent par la liste blanche.


## Livrables

```
src/app/storage/rds/dto/search_options.py       # options de recherche/pagination
src/app/services/article/article_service.py      # get_all_articles, get_admin_all_articles
src/app/storage/rds/datastore/article/article_store.py
src/app/api/routes/article/article_api.py        # GET /article/list, /article/admin/list
```

Tests :

```
tests/services/test_listing.py
```


## Consignes

### 1. Pagination

Paramètres `index_size` (page) et `max_results` (taille de page), bornés
à des valeurs raisonnables (refuse une taille de page absurde). Traduits
en `LIMIT` / `OFFSET` castés en `int`.

### 2. Filtres

1. `state` : filtre sur l'énumération `Status`.
2. `tags` : filtre sur la colonne JSON des tags.
3. `search` : recherche sur le titre (et éventuellement le contenu).
4. Les articles supprimés logiquement (`is_deleted`) sont exclus.

### 3. Tri

Tout `order_by` demandé est validé contre les colonnes réelles
(liste blanche de la tâche 03). Un champ de tri inconnu est refusé, pas
injecté.

### 4. Vue admin

`get_admin_all_articles` ajoute un filtre `user_id` et n'est accessible
qu'aux rôles reviewers. La liste publique montre les articles publiés ;
la liste admin voit tous les états.


## Critères d'acceptation

1. La pagination renvoie la bonne tranche et un total exploitable.
2. Les filtres état / tags / recherche fonctionnent, combinables.
3. Un `order_by` non autorisé est rejeté.
4. Les articles supprimés n'apparaissent pas.
5. La vue admin exige un rôle reviewer et filtre par auteur.


## Avant de pousser

- [ ] `ruff` / `black` propres
- [ ] `pytest` vert, dont le rejet d'un tri non autorisé
- [ ] Parcours manuel : pagination, chaque filtre, vue admin
