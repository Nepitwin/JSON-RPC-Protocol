import json

from jsonrpc.model.entity import Entity


class JsonRpcResponse(Entity):

    def __init__(self, jsonrpc: str, result: object, id: str):
        super().__init__(is_response=True)
        self.jsonrpc = jsonrpc
        self.result = result
        self.id = id

    def dump(self) -> str:
        return json.dumps({
            "jsonrpc": self.jsonrpc,
            "result": self.result,
            "id": self.id
        })