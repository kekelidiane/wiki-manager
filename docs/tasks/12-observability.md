# Tâche 12 — Observabilité (traces et métriques)

> **Branche** : `feat/da/observability`
> **Effort estimé** : 0,5 jour
> **Dépend de** : tâche 01


## Objectif

Instrumenter le service : traces distribuées OpenTelemetry et métriques
Prometheus. Objectif, pouvoir suivre une requête de bout en bout et
mesurer latence, débit et santé base en production.


## Livrables

```
src/app/metrics/
├── __init__.py
├── prometheus.py                 # middleware métriques HTTP + endpoint, record_db_query
└── tracing.py                    # init_tracing(app)
```

Config d'exemple pour la stack locale :

```
otel-collector-config.yaml
prometheus.yml
```


## Consignes

### 1. Traces OpenTelemetry

`init_tracing(app)` instrumente FastAPI, les requêtes sortantes et
`asyncpg`, et exporte en OTLP vers l'endpoint lu en config
(`OTEL_EXPORTER_OTLP_ENDPOINT`, suffixé `/v1/traces`).

### 2. Métriques Prometheus

Un middleware HTTP compte les requêtes et mesure les latences par route
et par code de statut. Une fonction `record_db_query` mesure la durée et
le succès des requêtes base (à appeler depuis les stores). Un endpoint
expose les métriques au format Prometheus.

### 3. Branchement

Le serveur (tâche 01) appelle `init_tracing` et `init_metrics` et ajoute
le middleware métriques. Ces appels sont contrôlés par la config pour
pouvoir les couper en local si besoin.


## Critères d'acceptation

1. Les traces remontent dans le collector local pour une requête de test.
2. L'endpoint métriques renvoie des compteurs et histogrammes cohérents.
3. Les durées de requêtes base sont enregistrées.
4. Les endpoints OTLP viennent de la config, pas du code en dur.


## Avant de pousser

- [ ] `ruff` / `black` propres
- [ ] `pytest` vert
- [ ] Trace visible dans la stack locale (collector + backend de traces)
