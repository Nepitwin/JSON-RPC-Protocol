import json


class Entity:

    def __init__(self, is_batch=False, is_error=False, is_notification=False, is_request=False, is_response=False):
        self.is_batch = is_batch
        self.is_error = is_error
        self.is_notification = is_notification
        self.is_request = is_request
        self.is_response = is_response

    def dump(self) -> str:
        raise NotImplementedError("Implement me")
