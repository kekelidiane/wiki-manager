# Tâche 11 — Utilisateurs (datastore Keycloak)

> **Branche** : `feat/da/users-keycloak`
> **Effort estimé** : 0,5 jour
> **Dépend de** : tâche 05


## Objectif

Exposer les informations utilisateur nécessaires à l'interface
(affichage d'auteurs, listes de membres) en interrogeant Keycloak comme
source de vérité des identités. On ne duplique pas les utilisateurs en
base locale.


## Livrables

```
src/app/storage/rds/clients/keycloak_client.py
src/app/services/user/
├── __init__.py
└── user_service.py
src/app/storage/rds/datastore/user/
├── __init__.py
└── user_store.py                 # KeycloakDatastore
src/app/api/routes/user/
├── __init__.py
└── user_api.py
```

Tests :

```
tests/services/test_user_service.py
```


## Consignes

### 1. Client Keycloak

`KeycloakClient` obtient un token d'accès service
(`client_credentials`) à partir des paramètres de config (realm, client
id, **secret via environnement**) et interroge l'API admin de Keycloak.

### 2. Datastore et service

`KeycloakDatastore` récupère un utilisateur par id et liste les
utilisateurs (paginé). `UserService` expose ces opérations avec le
contrôle de rôle adapté.

### 3. Robustesse

Gère l'indisponibilité de Keycloak sans faire tomber tout le service :
erreur claire remontée, timeouts raisonnables, jamais de secret loggué.


## Critères d'acceptation

1. Récupérer un utilisateur par id renvoie ses données publiques.
2. La liste des utilisateurs est paginée.
3. Le secret client Keycloak vient de l'environnement, jamais du code ni
   des logs.
4. Une panne Keycloak renvoie une erreur maîtrisée, pas une 500 brute.


## Avant de pousser

- [ ] `ruff` / `black` propres
- [ ] `pytest` vert (client Keycloak mocké)
- [ ] Testé contre un Keycloak de dev
