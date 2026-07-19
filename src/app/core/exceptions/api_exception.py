class ApiErrorsCode:
    CATEGORY_FORM_NOT_CORRECT = 8000
    CATEGORY_NOT_FOUND = 2001
    CATEGORY_ALREADY_EXISTS = 2000
    USER_NOT_FOUND = 1000
    USER_ALREADY_EXISTS = 1001
    ROLE = 2000
    RESOURCE_ACCESS_DENIED = 9000


class ApiException(Exception):
    def __init__(self, status_code: int, error_code: int, message: str):
        super().__init__(message)
        self._status_code = status_code
        self._error_code = error_code
        self._message = message

    @property
    def message(self):
        return {"error_code": self._error_code, "message": self._message}

    @property
    def status_code(self):
        return self._status_code

    @property
    def error_code(self):
        return self._error_code

    @staticmethod
    def server_internal_error() -> dict:
        return {"error_code": 500, "message": "internal server error"}
