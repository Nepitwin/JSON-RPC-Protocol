from jsonrpc_protocol.enum import ProtocolVersion


class Validator:

    @staticmethod
    def validate_jsonrpc_from_json(json: dict, protocol_version: ProtocolVersion):
        return "jsonrpc" in json and isinstance(json["jsonrpc"], str) \
            and json["jsonrpc"] == protocol_version.value

    @staticmethod
    def validate_error_from_json(json: dict):
        return "error" in json and isinstance(json["error"], dict)

    @staticmethod
    def validate_method_from_json(json: dict):
        return "method" in json and isinstance(json["method"], str)

    @staticmethod
    def validate_params_from_json(json: dict):
        return "params" in json

    @staticmethod
    def validate_id_from_json(json: dict):
        return "id" in json

    @staticmethod
    def validate_result_from_json(json: dict):
        return "result" in json
