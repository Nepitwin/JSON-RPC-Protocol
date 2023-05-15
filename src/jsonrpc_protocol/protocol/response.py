import json

from jsonrpc_protocol.enum.protocolversion import ProtocolVersion
from jsonrpc_protocol.protocol.entity import Entity


class Response(Entity):

    def __init__(self, jsonrpc: ProtocolVersion, result: object, id: str):
        super().__init__(is_response=True)
        self.jsonrpc = jsonrpc
        self.result = result
        self.id = id

    def dump(self) -> str:
        return json.dumps({
            "jsonrpc": self.jsonrpc.value,
            "result": self.result,
            "id": self.id
        })