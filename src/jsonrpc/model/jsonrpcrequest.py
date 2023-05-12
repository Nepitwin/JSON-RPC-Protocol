import json

from jsonrpc.model.entity import Entity


class JsonRpcRequest(Entity):

    def __init__(self, jsonrpc: str, method: str, params: object, id: str):
        super().__init__(is_request=True)
        self.jsonrpc = jsonrpc
        self.method = method
        self.params = params
        self.id = id

    def dump(self) -> str:
        return json.dumps({
            "jsonrpc": self.jsonrpc,
            "method": self.method,
            "params": self.params,
            "id": self.id
        })