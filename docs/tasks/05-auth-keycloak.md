# Tâche 05 — Authentification Keycloak/JWT réelle

> **Branche** : `feat/da/auth-keycloak`
> **Effort estimé** : 1,5 jour
> **Dépend de** : tâche 01


## Objectif

Mettre en place l'authentification réelle par token Keycloak et les
décorateurs de contrôle de rôle. C'est la **correction du défaut le plus
grave de l'ancien projet** : dans `wiki`, le provider d'authentification
était remplacé par un mock qui injectait un faux utilisateur avec tous
les rôles, court-circuitant toute sécurité. Ici, on branche le vrai
provider et le mock ne sert **que** pour les tests.


## Livrables

```
src/app/models/security/
├── __init__.py
└── auth_user.py                  # AuthenticatedUser (roles, has_role)
src/app/security/
├── __init__.py
├── api_roles.py                  # ApiRoles : MANAGER, EMPLOYEE, DIRECTOR
├── access_granter.py             # has_role / has_roles / has_any_roles
├── authentication_provider.py    # AuthenticationProvider (HTTPBearer)
├── auth_token_client.py          # récupère/valide les clés Keycloak
└── managers/
    ├── __init__.py
    ├── authentication_manager.py       # interface
    ├── jwt_authentication_manager.py   # validation JWT
    └── oauth2_authentication_manager.py
```

Tests :

```
tests/security/
├── __init__.py
├── test_access_granter.py
└── test_authentication_provider.py
```


## Consignes

### 1. AuthenticatedUser

Modèle portant `user_id`, `username`, `email`, `scopes`, `roles`,
`groups`, avec une méthode `has_role(role)`.

### 2. Provider et managers

`AuthenticationProvider` étend `HTTPBearer`, extrait le token, refuse un
schéma non `Bearer`, et délègue au premier manager qui `supports(token)`.
Le `JWTAuthenticationManager` valide la signature contre les clés
publiques Keycloak (audience, expiration, issuer) et construit
l'`AuthenticatedUser` depuis les claims.

### 3. Point clé — le vrai provider est actif

```python
AUTHENTICATION_PROVIDER = AuthenticationProvider([JWT_AUTHENTICATION_MANAGER])
```

Un `AuthenticationProviderMock` peut exister **uniquement** pour les
tests, jamais câblé par défaut. Le secret client Keycloak vient de
l'environnement (tâche 01), jamais du code.

### 4. Décorateurs de rôle

`has_role`, `has_roles` (tous requis), `has_any_roles` (au moins un).
Ils retrouvent l'`AuthenticatedUser` dans les arguments de la fonction
décorée et lèvent une `ApiException` 403 si l'utilisateur manque ou n'a
pas le rôle.


## Critères d'acceptation

1. Une requête sans token, avec un mauvais schéma ou un token invalide
   est rejetée en 401.
2. Un token valide produit un `AuthenticatedUser` avec les bons rôles.
3. `has_any_roles` autorise si un rôle correspond, refuse (403) sinon.
4. Le provider par défaut exporté est le **vrai** provider, pas le mock.
5. Aucun secret Keycloak en dur ; tout vient de la config.


## Avant de pousser

- [ ] `ruff` / `black` propres
- [ ] `pytest` vert, dont les cas 401/403
- [ ] Vérifié manuellement avec un vrai token Keycloak de dev
- [ ] `grep` de contrôle : le mock n'est pas le provider par défaut
