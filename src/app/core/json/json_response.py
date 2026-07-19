from typing import Any

import orjson
from starlette.responses import JSONResponse


class ORJSONResponse(JSONResponse):
    media_type = "application/json"

    def render(self, content: Any) -> bytes:
        return orjson.dumps(
            content,
            option=orjson.OPT_SERIALIZE_UUID
            | orjson.OPT_SERIALIZE_DATACLASS
            | orjson.OPT_SERIALIZE_NUMPY
            | orjson.OPT_UTC_Z,
        )
