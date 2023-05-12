import json

from jsonrpc.model.entity import Entity


class JsonRpcBatch(Entity):

    def __init__(self):
        super().__init__(is_batch=True)
        self.elements = []

    def dump(self) -> str:
        data = []

        for entity in self.elements:
            data.append(entity.dump())

        return json.dumps(data)
