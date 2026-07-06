# Modèle de domaine — wiki-manager

Ce document est la **source de vérité du schéma**. Les tâches 02, 03 et
04 doivent lui correspondre exactement (noms de colonnes, types,
contraintes, index). Ne le modifie pas sans en discuter d'abord.

Le domaine reprend celui de l'ancien backend `wiki` : une base de
connaissances interne où des utilisateurs rédigent des articles, classés
par catégories, illustrés par des médias, commentés et notés.


## 1. Colonnes d'audit communes

Chaque table métier porte les mêmes colonnes de traçabilité. On les
factorise dans un mixin partagé plutôt que de les répéter.

| Colonne      | Type         | Notes                                   |
|--------------|--------------|-----------------------------------------|
| `created_by` | str(55)      | username de l'auteur, non nul           |
| `created_at` | timestamptz  | défaut `now()`                          |
| `updated_by` | str(55)      | nullable                                |
| `updated_at` | timestamptz  | nullable                                |
| `version`    | int          | verrouillage optimiste, défaut 1        |

Chaque entité expose aussi un identifiant technique `id` (int, clé
primaire interne, exclu des réponses API) **et** un identifiant public
`<entity>_id` (str, UUID, unique) utilisé partout dans l'API.


## 2. Entités

### 2.1 Category — `categories`

Regroupe les articles par thème.

| Colonne        | Type      | Contraintes            |
|----------------|-----------|------------------------|
| `category_id`  | str       | unique, non nul        |
| `title`        | str       | unique, indexé         |
| `description`  | str       | nullable               |

Relation : plusieurs-à-plusieurs avec `Article` via la table de liaison
`article_categories (article_id, category_id)`.

### 2.2 Media — `medias`

Fichier stocké sur S3/MinIO, référencé par un article.

| Colonne       | Type     | Contraintes         |
|---------------|----------|---------------------|
| `media_id`    | str(40)  | unique, non nul     |
| `file_name`   | str(255) | non nul             |
| `file_type`   | str(255) | non nul             |
| `url`         | str      | non nul             |
| `uploaded_by` | str(55)  | non nul             |
| `uploaded_at` | timestamptz | défaut `now()`   |

Relation : galerie plusieurs-à-plusieurs avec `Article` via
`article_medias_gallery (article_id, media_id)`. Un article a aussi une
image de couverture unique (`cover_image_id`, clé étrangère nullable
vers `medias.media_id`).

### 2.3 Article — `articles`

Entité centrale.

| Colonne          | Type       | Contraintes                        |
|------------------|------------|------------------------------------|
| `article_id`     | str(40)    | unique, non nul                    |
| `title`          | str        | non nul, indexé                    |
| `content`        | str        | non nul                            |
| `tags`           | JSON       | liste de str, nullable             |
| `sources`        | JSON       | liste de str, nullable             |
| `state`          | enum Status| non nul, indexé                    |
| `likes`          | int        | défaut 0                           |
| `dislikes`       | int        | défaut 0                           |
| `is_deleted`     | bool       | défaut faux, exclu des réponses    |
| `user_id`        | str        | non nul, indexé (propriétaire)     |
| `admin_review`   | str        | nullable, indexé                   |
| `cover_image_id` | str        | clé étrangère nullable vers médias |

Relations : catégories (n..n), galerie de médias (n..n), commentaires
(1..n), réactions (1..n).

### 2.4 Comment — `comments`

| Colonne      | Type     | Contraintes                       |
|--------------|----------|-----------------------------------|
| `comment_id` | str(40)  | unique, non nul                   |
| `content`    | str(128) | non nul                           |
| `is_deleted` | bool     | défaut faux, exclu des réponses   |
| `article_id` | str      | clé étrangère vers `articles`     |

### 2.5 ArticleReaction — `article_reactions`

Note d'un utilisateur sur un article.

| Colonne       | Type            | Contraintes                    |
|---------------|-----------------|--------------------------------|
| `reaction_id` | str(40)         | unique, non nul                |
| `article_id`  | str(40)         | clé étrangère, indexé          |
| `user_id`     | str(55)         | non nul, indexé                |
| `reaction`    | enum ReactionType | non nul, indexé              |

Contrainte d'unicité composite `(article_id, user_id)` : **une seule
réaction par utilisateur et par article** (nom
`uq_article_reactions_article_user`).


## 3. Énumérations

`Status` (cycle de vie d'un article) : `DRAFT`, `SUBMITTED`, `PENDING`,
`CORRECTION_REQUESTED`, `APPROVED`, `PUBLISHED`.

`ReactionType` : `LIKE`, `DISLIKE`.


## 4. Cycle de vie d'un article

1. L'auteur crée l'article en `DRAFT` ou `SUBMITTED`.
2. Un article `SUBMITTED` part en revue (`PENDING`).
3. Le reviewer approuve (`APPROVED`) ou demande une correction
   (`CORRECTION_REQUESTED`), auquel cas `admin_review` porte le motif.
4. L'auteur corrige et resoumet.
5. Un article approuvé est publié (`PUBLISHED`) et devient visible.

Les transitions autorisées et les rôles qui peuvent les déclencher sont
détaillés dans la tâche 08.


## 5. Rôles

Trois rôles, portés par le token Keycloak : `employee`, `manager`,
`director`. La correspondance rôle → action est précisée dans chaque
tâche de service. Règle générale : un employé rédige et note ; un manager
et un directeur relisent, commentent et publient.
