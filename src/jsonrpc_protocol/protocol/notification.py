import json

from jsonrpc_protocol.protocol.params import Params
from jsonrpc_protocol.enum.protocolversion import ProtocolVersion
from jsonrpc_protocol.protocol.entity import Entity


class Notification(Entity):

    def __init__(self, jsonrpc: ProtocolVersion, method: str, params: Params = None):
        super().__init__(is_notification=True)
        self.jsonrpc = jsonrpc
        self.method = method
        self.params = params  # Optional Parameter

    def dump(self) -> str:
        if self.params:
            return json.dumps({
                "jsonrpc": self.jsonrpc.value,
                "method": self.method,
                "params": self.params.data
            })

        return json.dumps({
            "jsonrpc": self.jsonrpc.value,
            "method": self.method
        })
