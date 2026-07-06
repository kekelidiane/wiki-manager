# Tâche 06 — Catégories (CRUD)

> **Branche** : `feat/da/category-crud`
> **Effort estimé** : 0,5 jour
> **Dépend de** : tâches 04 et 05


## Objectif

Première tranche verticale complète `routes → service → datastore` sur
l'entité la plus simple, la catégorie. Elle sert de **patron de
référence** pour les tâches 07 à 11 : même découpage en couches, même
gestion d'erreur, même contrôle de rôle.


## Livrables

```
src/app/api/dto/wiki/wiki_dto.py            # DTO catégorie (create/update/response)
src/app/api/routes/category/
├── __init__.py
└── category_api.py
src/app/services/category/
├── __init__.py
└── category_service.py
src/app/storage/rds/datastore/category/
├── __init__.py
└── category_store.py
src/app/storage/rds/datastore/interfaces/category.py
src/app/services/factory/services_factory.py   # câble le service
src/app/configs/router_config.py               # enregistre le router
```

Tests :

```
tests/services/test_category_service.py
```


## Consignes

### 1. DTO

`CreateCategoryDTO`, `UpdateCategoryDTO`, `CategoryResponse` (Pydantic).
Les entrées valident `title` non vide.

### 2. Service

`CategoryService` : `create`, `update`, `get`, `list`, `delete`. Chaque
méthode est décorée par le contrôle de rôle adapté (créer/modifier/
supprimer réservés `manager`/`director` ; lecture ouverte aux trois
rôles). Génère `category_id` (UUID), renseigne les champs d'audit depuis
l'`AuthenticatedUser`.

### 3. Datastore

`CategoryStore` implémente l'interface `ICategory` et utilise les query
builders de la tâche 03. Le `title` étant unique, gère le conflit
proprement (erreur métier, pas une 500 brute).

### 4. Routes

Un endpoint par opération, injection du service via le factory
(`Depends`), injection de l'`AuthenticatedUser` via le provider de la
tâche 05. Gestion uniforme : `ApiException` → réponse structurée,
exception inattendue → 500 générique.


## Critères d'acceptation

1. Créer, lire, lister, modifier, supprimer une catégorie fonctionne de
   bout en bout.
2. Un titre en double renvoie une erreur métier claire, pas une 500.
3. Un utilisateur sans le rôle requis reçoit 403.
4. Le service et le router sont bien câblés dans le factory et
   `router_config`.


## Avant de pousser

- [ ] `ruff` / `black` propres
- [ ] `pytest` vert
- [ ] Parcours manuel des cinq opérations via Swagger
