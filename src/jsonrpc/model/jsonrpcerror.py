import typing
import json

from jsonrpc.enum.jsonrpcerrorcode import JsonRpcErrorCode
from jsonrpc.model.entity import Entity


class JsonRpcError(Entity):

    def __init__(self, jsonrpc: str, error_code: int, id: typing.Optional[str] = None):
        super().__init__(is_error=True)
        self.jsonrpc = jsonrpc
        self.error = {
            "code": error_code,
            "message": self._error_code_to_message(error_code),
        }
        self.id = id

    def dump(self) -> str:
        return json.dumps({
            "jsonrpc": self.jsonrpc,
            "error": self.error,
            "id": self.id
        })

    @staticmethod
    def _error_code_to_message(error_code: int):
        if error_code == JsonRpcErrorCode.InvalidRequest:
            return "Invalid Request"

        if error_code == JsonRpcErrorCode.ParseError:
            return "Parse error"

        if error_code == JsonRpcErrorCode.InternalError:
            return "Internal error"

        if error_code == JsonRpcErrorCode.MethodNotFound:
            return "Method not found"

        if -32000 >= error_code <= -32099:
            return "Server error"

        return "Unknown error message from error code"
