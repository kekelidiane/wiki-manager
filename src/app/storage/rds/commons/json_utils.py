from typing import Any

import orjson


def to_json(model: Any) -> str | None:
    return (
        orjson.dumps(model, option=orjson.OPT_UTC_Z).decode("utf-8")
        if model is not None
        else None
    )


def from_json(model: str) -> dict | None:
    return orjson.loads(model) if model is not None else None
