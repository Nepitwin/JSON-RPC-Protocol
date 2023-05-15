import typing
import json

from jsonrpc_protocol.enum.protocolversion import ProtocolVersion
from jsonrpc_protocol.enum.errorcode import ErrorCode
from jsonrpc_protocol.protocol.entity import Entity


class Error(Entity):

    def __init__(self, jsonrpc: ProtocolVersion, error_code: int, id: typing.Optional[str] = None):
        super().__init__(is_error=True)
        self.jsonrpc = jsonrpc
        self.error = {
            "code": error_code,
            "message": self._error_code_to_message(error_code),
        }
        self.id = id

    def dump(self) -> str:
        return json.dumps({
            "jsonrpc": self.jsonrpc.value,
            "error": self.error,
            "id": self.id
        })

    @staticmethod
    def _error_code_to_message(error_code: int):
        if error_code == ErrorCode.InvalidRequest:
            return "Invalid Request"

        if error_code == ErrorCode.ParseError:
            return "Parse error"

        if error_code == ErrorCode.InternalError:
            return "Internal error"

        if error_code == ErrorCode.MethodNotFound:
            return "Method not found"

        if -32000 >= error_code <= -32099:
            return "Server error"

        return "Unknown error message from error code"
