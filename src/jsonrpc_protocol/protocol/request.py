import json

from jsonrpc_protocol.protocol.params import Params
from jsonrpc_protocol.enum.protocolversion import ProtocolVersion
from jsonrpc_protocol.protocol.entity import Entity


class Request(Entity):

    def __init__(self, jsonrpc: ProtocolVersion, method: str, params: Params, id: str):
        super().__init__(is_request=True)
        self.jsonrpc = jsonrpc
        self.method = method
        self.params = params
        self.id = id

    def dump(self) -> str:
        return json.dumps({
            "jsonrpc": self.jsonrpc.value,
            "method": self.method,
            "params": self.params.data,
            "id": self.id
        })