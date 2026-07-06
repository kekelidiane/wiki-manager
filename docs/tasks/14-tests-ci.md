# Tâche 14 — Tests et intégration continue

> **Branche** : `feat/da/tests-ci`
> **Effort estimé** : 1 jour
> **Dépend de** : tâche 08 (idéalement en fin de parcours)


## Objectif

Consolider la couverture de tests et automatiser les vérifications sur
chaque Pull Request via GitHub Actions. À la fin, une PR qui casse le
lint, le format ou les tests est signalée automatiquement.


## Livrables

```
.github/workflows/ci.yml
tests/conftest.py                  # fixtures partagées (app, base de test, faux user)
tests/                             # complétion des cas manquants
```


## Consignes

### 1. Fixtures

`conftest.py` fournit un client de test FastAPI, une base de test
(PostgreSQL de CI ou base éphémère), et un `AuthenticatedUser` de test
via le `AuthenticationProviderMock` (le seul usage légitime du mock).

### 2. Couverture

Complète les tests des couches où c'est mince : au minimum le service
article (cycle de vie), les réactions (compteurs), le query builder
(rejet d'injection), l'authentification (401/403).

### 3. Pipeline CI

Le workflow, déclenché sur push et pull_request vers `develop` :

1. installe Python 3.11 et les dépendances (`.[dev]`),
2. lance `ruff check src tests`,
3. lance `black --check src tests`,
4. lance `pytest`,
5. échoue si l'une des étapes échoue.

Prévois un service PostgreSQL dans le job pour les tests qui touchent la
base.


## Critères d'acceptation

1. `ci.yml` se déclenche sur les PR vers `develop`.
2. Les quatre étapes (deps, ruff, black, pytest) tournent et bloquent la
   PR en cas d'échec.
3. La suite de tests couvre les chemins critiques listés.
4. Le mock d'authentification n'est utilisé que dans les tests.


## Avant de pousser

- [ ] `ruff` / `black` propres
- [ ] `pytest` vert en local
- [ ] Workflow validé sur une PR de test (pipeline vert)
