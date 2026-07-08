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


ENVIRONMENT_CONFIG = {k: get_env_or_default(k.name) for k in EnvKey}
