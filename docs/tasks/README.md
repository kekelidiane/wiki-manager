# Tâches — mode d'emploi

Ce dossier contient les tâches incrémentales du backend **wiki-manager**.
Chaque fichier (`01-*.md`, `02-*.md`, …) est un morceau de travail
autonome. On les fait dans l'ordre. On n'ouvre la tâche suivante que
lorsque la Pull Request de la précédente est mergée dans `develop`.

Le projet reconstruit proprement l'ancien backend `wiki` (articles,
catégories, médias, commentaires, réactions, utilisateurs) en corrigeant
les défauts connus : authentification réelle Keycloak au lieu du mock,
secrets sortis du code, requêtes SQL sans injection possible, CORS
restreint.


## 1. Avant de commencer une tâche

1. Récupère la dernière version de `develop` :
   ```bash
   git checkout develop
   git pull --rebase origin develop
   ```
2. Lis le fichier de la tâche entièrement **avant d'écrire du code**.
   Chaque tâche a une section « Critères d'acceptation » : c'est
   exactement ce que la review va vérifier.
3. Regarde le modèle de domaine dans [`docs/domain-model.md`](../domain-model.md)
   quand la tâche s'y réfère. C'est la source de vérité du schéma.
4. Si quelque chose n'est pas clair, demande **avant** d'y passer des
   heures — en PR brouillon ou directement. Une question coûte toujours
   moins cher qu'une journée dans la mauvaise direction.


## 2. Nommage des branches

Une branche par tâche, basée sur `develop`. Le préfixe indique le type,
`da` sont tes initiales.

| Type            | Préfixe        | Exemple                          |
|-----------------|----------------|----------------------------------|
| Fonctionnalité  | `feat/da/`     | `feat/da/domain-models`          |
| Correction      | `fix/da/`      | `fix/da/jwt-audience-check`      |
| Refactoring     | `refactor/da/` | `refactor/da/services-factory`   |
| Documentation   | `docs/da/`     | `docs/da/domain-model`           |
| Chore / CI      | `chore/da/`    | `chore/da/update-ruff`           |

Création :

```bash
git checkout -b feat/da/domain-models develop
```


## 3. Style des commits

Les messages de commit sont **en anglais**, pour garder un historique
homogène.

1. Impératif présent : *"add Article model"*, pas *"added"* ni *"adds"*.
2. Sujet court, 72 caractères maximum. Si plus de contexte est utile,
   ligne vide puis un corps.
3. Un commit = un changement logique. Utilise `git add -p` pour ne mettre
   en staging que ce qui va ensemble.

Bon :

```
add Article SQLModel and Status enum

Table articles per docs/domain-model.md. Includes audit columns
and optimistic locking.
```

Mauvais : `wip`, `fix stuff`, `more changes`. Nettoie ce genre de commits
avec `git rebase -i develop` avant d'ouvrir la PR.


## 4. Qualité du code — à lancer en local

Avant chaque push, ces trois commandes doivent être vertes :

```bash
ruff check src tests
black --check src tests
pytest
```

Si `ruff` ou `black` râlent, corrige :

```bash
ruff check --fix src tests
black src tests
```


## 5. Pousser et ouvrir une PR

```bash
git push -u origin feat/da/domain-models
```

Puis ouvre une PR sur GitHub :

1. **Titre** : le numéro de tâche suivi du sujet, ex. `[task-02] add domain models`.
2. **Base** : `develop`.
3. **Description** : copie ce modèle.

```markdown
## What
<un paragraphe : ce que fait cette PR>

## Why
Tâche : docs/tasks/02-domain-models.md

## Changes
<liste numérotée des principales additions>

## Tested
- [ ] ruff check src tests : ok
- [ ] black --check src tests : ok
- [ ] pytest : <N> passed
- [ ] vérifications manuelles s'il y en a

## Out of scope
<ce qu'un reviewer pourrait attendre mais qui appartient à une tâche ultérieure>
```

Mets la PR en **Draft** si tu veux un retour intermédiaire avant de la
finaliser.


## 6. Boucle de review

1. Le reviewer laisse des commentaires. Réponds à chacun : soit tu
   corriges, soit tu expliques ton choix.
2. Pousse les corrections en nouveaux commits. Pas de force-push tant que
   la review est en cours, ça rend les commentaires illisibles.
3. Une fois approuvée, la PR est mergée en squash dans `develop`.


## 7. Règles d'or

1. **PR courtes.** Au-delà d'environ 400 lignes de code, c'est
   probablement deux tâches. Découpe.
2. **Jamais de secret dans le code.** `.env` est gitignoré et le reste.
   Documente les variables attendues dans `.env.example`.
3. **Les tests vivent dans `tests/`**, en miroir de `src/app/`.
4. **Chaque nouveau module a un `__init__.py`**, même vide.
5. **Langues** : code et commits en anglais ; documentation et messages
   utilisateur en français.


## 8. Index des tâches

| #  | Fichier                                                       | Dépend de | Statut       |
|----|---------------------------------------------------------------|-----------|--------------|
| 01 | [`01-scaffold-config.md`](./01-scaffold-config.md)            | —         | À faire      |
| 02 | [`02-domain-models.md`](./02-domain-models.md)                | 01        | Bloquée      |
| 03 | [`03-database-layer.md`](./03-database-layer.md)              | 02        | Bloquée      |
| 04 | [`04-alembic-migrations.md`](./04-alembic-migrations.md)      | 03        | Bloquée      |
| 05 | [`05-auth-keycloak.md`](./05-auth-keycloak.md)                | 01        | Bloquée      |
| 06 | [`06-category-crud.md`](./06-category-crud.md)                | 04, 05    | Bloquée      |
| 07 | [`07-media-storage.md`](./07-media-storage.md)                | 04, 05    | Bloquée      |
| 08 | [`08-article-lifecycle.md`](./08-article-lifecycle.md)        | 06, 07    | Bloquée      |
| 09 | [`09-reactions-comments.md`](./09-reactions-comments.md)      | 08        | Bloquée      |
| 10 | [`10-listing-search.md`](./10-listing-search.md)             | 08        | Bloquée      |
| 11 | [`11-users-keycloak.md`](./11-users-keycloak.md)             | 05        | Bloquée      |
| 12 | [`12-observability.md`](./12-observability.md)               | 01        | Bloquée      |
| 13 | [`13-security-docker.md`](./13-security-docker.md)          | 01        | Bloquée      |
| 14 | [`14-tests-ci.md`](./14-tests-ci.md)                        | 08        | Bloquée      |

### Vue d'ensemble

```
01 scaffold  →  02 models  →  03 database  →  04 alembic
                                   ↓
                    05 auth  →  06 category  →  07 media  →  08 article
                                                                 ↓
                              09 reactions/comments   10 listing/search
                                                                 ↓
        11 users     12 observability     13 sécurité/docker     14 tests/ci
```

Chaque tâche est pensée pour rester petite (environ 400 lignes de code,
review en moins de 30 minutes). La tâche 06 pose le pattern
`routes → service → datastore` réutilisé par les slices 07 à 11.
