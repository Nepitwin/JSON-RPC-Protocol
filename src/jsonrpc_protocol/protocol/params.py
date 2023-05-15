

class Params:

    def __init__(self, params: object):
        self.data = params
        self.is_array = False
        self.is_dict = False

        if isinstance(params, dict):
            self.is_dict = True

        if isinstance(params, list):
            self.is_array = True

        if not self.is_array and not self.is_dict:
            raise ValueError("Invalid params")
