class Entity:

    def __init__(self,
                 is_batch: bool = False,
                 is_error: bool = False,
                 is_notification: bool = False,
                 is_request: bool = False,
                 is_response: bool = False):
        self.is_batch = is_batch
        self.is_error = is_error
        self.is_notification = is_notification
        self.is_request = is_request
        self.is_response = is_response

    def dump(self) -> str:
        raise NotImplementedError("Implement me")
