# Tâche 09 — Réactions et commentaires

> **Branche** : `feat/da/reactions-comments`
> **Effort estimé** : 1 jour
> **Dépend de** : tâche 08


## Objectif

Ajouter les interactions sociales sur un article : réactions
(like/dislike, une seule par utilisateur) et commentaires. On s'appuie
sur la contrainte d'unicité `(article_id, user_id)` du modèle de
réaction.


## Livrables

Extension de l'article existant :

```
src/app/services/article/article_service.py    # like, dislike, cancel_reaction, add_comment, load_reactions
src/app/storage/rds/datastore/article/article_store.py
src/app/api/routes/article/article_api.py       # endpoints like/dislike/cancel/comment/reactions
src/app/api/dto/wiki/wiki_dto.py                # AddCommentDTO, ReactionResponse
```

Tests :

```
tests/services/test_reactions.py
```


## Consignes

### 1. Réactions

1. `like` / `dislike` : si l'utilisateur a déjà la même réaction, erreur
   métier (déjà liké / déjà disliké). Sinon on crée ou bascule la
   réaction et on met à jour les compteurs `likes` / `dislikes` de
   l'article.
2. `cancel_reaction` : retire la réaction existante, erreur si aucune.
3. Le passage like → dislike doit rester cohérent sur les compteurs
   (décrémenter l'un, incrémenter l'autre). Fais-le côté store, idéalement
   en une transaction, en t'appuyant sur la contrainte d'unicité.
4. `load_reactions` liste les réactions d'un article, paginé.

### 2. Commentaires

`add_comment` crée un `Comment` (contenu limité à 128 caractères, comme
au modèle) rattaché à l'article, réservé aux rôles reviewers. Champs
d'audit renseignés.


## Critères d'acceptation

1. Un utilisateur ne peut avoir qu'une réaction par article (contrainte
   respectée).
2. Double like renvoie une erreur métier, pas une 500.
3. Les compteurs `likes` / `dislikes` restent justes après bascule et
   annulation.
4. `cancel_reaction` sans réaction préalable renvoie une erreur métier.
5. Un commentaire trop long est rejeté à la validation.


## Avant de pousser

- [ ] `ruff` / `black` propres
- [ ] `pytest` vert, dont concurrence like/dislike
- [ ] Vérifié manuellement : compteurs cohérents après plusieurs
      bascules
