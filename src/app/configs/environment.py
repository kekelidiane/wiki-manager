import os
from enum import Enum, auto

from dotenv import dotenv_values, load_dotenv

load_dotenv(".env")
defaults = dotenv_values(".env.example")


def get_env_or_default(key):
    val = os.getenv(key)
    if not val:
        val = defaults.get(key, None)
    return val


class EnvKey(Enum):
    WIKI_API_VERSION = auto()
    WIKI_API_NAME = auto()
    WIKI_BINDING_HOST = auto()
    WIKI_BINDING_PORT = auto()
    WIKI_LOG_LEVEL = auto()
    WIKI_DB_CONNEXION = auto()
    WIKI_DB_MIN_CON = auto()
    WIKI_DB_MAX_CON = auto()
    WIKI_KEYCLOAK_URL = auto()
    WIKI_KEYCLOAK_ISSUER = auto()
    WIKI_KEYCLOAK_CLIENT_ID = auto()
    WIKI_KEYCLOAK_CLIENT_SECRET = auto()
    WIKI_S3_ACCESS_KEY = auto()
    WIKI_S3_SECRET_KEY = auto()
    WIKI_S3_BUCKET_NAME = auto()
    WIKI_S3_REGION = auto()
    WIKI_S3_URL = auto()
    AWS_BLOB_SAS_TTL_IN_SECS = auto()


ENVIRONMENT_CONFIG = {k: get_env_or_default(k.name) for k in EnvKey}
