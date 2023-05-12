import json

from jsonrpc.model.entity import Entity


class JsonRpcNotification(Entity):

    def __init__(self, jsonrpc: str, method: str, params: object = None):
        super().__init__(is_notification=True)
        self.jsonrpc = jsonrpc
        self.method = method
        self.params = params  # Optional Parameter

    def dump(self) -> str:
        if self.params:
            return json.dumps({
                "jsonrpc": self.jsonrpc,
                "method": self.method,
                "params": self.params
            })

        return json.dumps({
            "jsonrpc": self.jsonrpc,
            "method": self.method
        })
