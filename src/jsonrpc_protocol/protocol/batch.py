import json

from jsonrpc_protocol.protocol.entity import Entity


class Batch(Entity):

    def __init__(self):
        super().__init__(is_batch=True)
        self.elements: list = []

    def dump(self) -> str:
        data = []

        for entity in self.elements:
            data.append(entity.dump())

        return json.dumps(data)
