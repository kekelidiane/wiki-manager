# Tâche 01 — Scaffold du projet et configuration

> **Branche** : `feat/da/scaffold-config`
> **Effort estimé** : 1 jour
> **Dépend de** : rien, c'est la première tâche.


## Objectif

Poser le squelette du service FastAPI et la couche de configuration.
À la fin, l'application démarre, expose sa documentation Swagger et
répond sur un endpoint de santé. **Aucune logique métier ici** : ni
modèle, ni base de données, ni authentification. On construit seulement
le socle sur lequel toutes les autres tâches vont s'appuyer.

Point important qui distingue ce projet de l'ancien `wiki` : **aucun
secret n'est écrit en dur dans le code**. Toute valeur sensible (URL de
base, identifiants, clés) est lue depuis l'environnement.


## Livrables

Arborescence attendue en fin de tâche :

```
wiki-manager/
├── pyproject.toml                # dépendances + config ruff/black/pytest
├── run.py                        # point d'entrée : instancie et lance le serveur
├── .env.example                  # documente toutes les variables attendues
├── .gitignore                    # .env, __pycache__, .ruff_cache, etc.
└── src/
    └── app/
        ├── __init__.py
        ├── server/
        │   ├── __init__.py
        │   └── server.py          # WikiServer : app factory FastAPI
        ├── configs/
        │   ├── __init__.py
        │   ├── environment.py     # EnvKey + chargement env, valeurs par défaut non sensibles
        │   ├── logger_config.py   # logging JSON + middleware request-id
        │   └── router_config.py   # agrège les routers
        ├── hooks/
        │   ├── __init__.py
        │   └── startup_shutdown_events.py   # lifespan (vide pour l'instant)
        ├── core/
        │   ├── __init__.py
        │   └── json/
        │       ├── __init__.py
        │       └── json_response.py          # ORJSONResponse
        └── api/
            ├── __init__.py
            └── routes/
                ├── __init__.py
                └── health/
                    ├── __init__.py
                    └── health_check_api.py    # GET /health
```

Plus un test :

```
tests/
├── __init__.py
└── api/
    ├── __init__.py
    └── test_health.py
```


## Consignes

### 1. `pyproject.toml`

Layout `src`, backend setuptools. Dépendances runtime minimales pour
cette tâche :

```
fastapi, uvicorn, orjson, python-dotenv, python-json-logger,
python-multipart
```

Extra `dev` : `pytest`, `pytest-asyncio`, `black`, `ruff`. Configure
`ruff` et `black` (longueur de ligne 88) et `pytest-asyncio` en mode
auto dans le même fichier.

### 2. Configuration — secrets hors du code

`configs/environment.py` expose une énumération `EnvKey` et un
dictionnaire `ENVIRONMENT_CONFIG` construit en lisant `os.environ`,
avec repli sur des valeurs par défaut **uniquement pour ce qui n'est pas
sensible** (port, préfixe de route, niveau de log).

Les valeurs sensibles (connexion base, clés S3, secret Keycloak) n'ont
**pas** de valeur par défaut : si la variable manque, on lève une erreur
explicite au démarrage plutôt que de démarrer avec un identifiant en
dur. Documente chaque variable dans `.env.example`.

Variables attendues à ce stade :

```
WIKI_API_VERSION=v1
WIKI_API_NAME=wiki
WIKI_BINDING_HOST=0.0.0.0
WIKI_BINDING_PORT=8080
WIKI_LOG_LEVEL=debug
```

### 3. App factory

`server/server.py` définit une classe `WikiServer` qui construit
l'instance FastAPI : titre, version, `openapi_url` / `docs_url` /
`redoc_url` préfixés par la route racine, `lifespan` branché, et une
méthode `run()` qui lance uvicorn. Les middlewares CORS et TrustedHost
seront ajoutés et durcis en tâche 13 — pour l'instant, un CORS permissif
en développement suffit, avec un commentaire signalant qu'il sera
restreint.

### 4. Logging JSON + request-id

`configs/logger_config.py` fournit un `LOGGING_CONFIG` (formatteur JSON)
et un middleware `RequestIdMiddleware` qui attache un identifiant unique
à chaque requête et le remet dans les logs.

### 5. Endpoint de santé

`GET /health` renvoie `{"status": "ok"}` en 200. Pas d'accès base ici,
c'est un simple ping de vivacité. Le check base viendra avec la tâche 03.


## Critères d'acceptation

1. `python run.py` démarre le serveur sans erreur.
2. La doc Swagger est accessible sur `/api/v1/wiki/documentation`.
3. `GET /api/v1/wiki/health` renvoie 200 avec `{"status": "ok"}`.
4. Si une variable sensible obligatoire manque, le démarrage échoue avec
   un message clair (à vérifier plus tard, quand les secrets seront
   introduits ; à ce stade documente le mécanisme).
5. `.env` est bien ignoré par git ; `.env.example` liste les variables.
6. Chaque dossier sous `src/app` a son `__init__.py`.


## Avant de pousser

- [ ] `ruff check src tests` propre
- [ ] `black --check src tests` propre
- [ ] `pytest` vert (au moins le test du endpoint santé)
- [ ] Démarrage manuel vérifié, Swagger et `/health` répondent


## Pour référence

L'ancien projet `wiki` a exactement cette structure de socle (voir
`server/server.py`, `configs/`, `hooks/startup_shutdown_events.py`).
Tu peux t'en inspirer, à une différence près, la principale de cette
tâche : **on ne recopie aucun secret en dur** dans `environment.py`.
