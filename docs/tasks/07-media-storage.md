# Tâche 07 — Médias et stockage objet (S3/MinIO)

> **Branche** : `feat/da/media-storage`
> **Effort estimé** : 1 jour
> **Dépend de** : tâches 04 et 05


## Objectif

Permettre l'upload de fichiers (images, pièces jointes) vers un stockage
objet compatible S3 (MinIO en local), et les référencer en base via
l'entité `Media`. Ces médias serviront de couverture et de galerie aux
articles (tâche 08).


## Livrables

```
src/app/storage/rds/clients/blob_manager.py     # S3Client (boto3)
src/app/api/routes/media/
├── __init__.py
└── media_api.py
src/app/services/media/
├── __init__.py
└── media_service.py
src/app/storage/rds/datastore/media/
├── __init__.py
└── media_store.py
src/app/storage/rds/datastore/interfaces/media.py
```

Tests :

```
tests/services/test_media_service.py
```


## Consignes

### 1. Client S3

`S3Client` (boto3) lit endpoint, clés, région et bucket depuis la config
(**secrets via environnement**, jamais en dur). Méthodes : `upload`
(retourne l'URL), `delete`.

### 2. Service

`MediaService` : `upload` prend le fichier (`UploadFile`), valide le type
MIME et la taille (fixe une limite raisonnable), pousse sur S3, crée la
ligne `Media` avec `media_id` (UUID) et les champs d'upload. `get`,
`list`, `delete` (supprime aussi l'objet S3).

### 3. Routes

Endpoint d'upload en `multipart/form-data`, récupération et suppression
par `media_id`. Contrôle de rôle : upload réservé aux rôles rédacteurs,
lecture ouverte.


## Critères d'acceptation

1. Un upload valide crée l'objet dans MinIO et la ligne `Media`, et
   renvoie l'URL.
2. Un type MIME hors whitelist ou un fichier trop gros est rejeté avec un
   message clair.
3. La suppression retire à la fois la ligne base et l'objet S3.
4. Aucune clé S3 en dur dans le code.


## Avant de pousser

- [ ] `ruff` / `black` propres
- [ ] `pytest` vert
- [ ] Upload/download/suppression testés contre un MinIO local
