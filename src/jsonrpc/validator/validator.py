
class Validator:

    @staticmethod
    def validate_jsonrpc_from_json(json):
        return "jsonrpc" in json and isinstance(json["jsonrpc"], str) and json["jsonrpc"] == "2.0"

    @staticmethod
    def validate_error_from_json(json):
        return "error" in json and isinstance(json["error"], dict)

    @staticmethod
    def validate_method_from_json(json):
        return "method" in json and isinstance(json["method"], str)

    @staticmethod
    def validate_params_from_json(json):
        return "params" in json

    @staticmethod
    def validate_id_from_json(json):
        return "id" in json

    @staticmethod
    def validate_result_from_json(json):
        return "result" in json
