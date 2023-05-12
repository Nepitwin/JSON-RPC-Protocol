import json
from json import JSONDecodeError

from jsonrpc.enum import JsonRpcErrorCode
from jsonrpc.model.entity import Entity
from jsonrpc.model.jsonrpcbatch import JsonRpcBatch
from jsonrpc.model.jsonrpcnotification import JsonRpcNotification
from jsonrpc.model.jsonrpcerror import JsonRpcError
from jsonrpc.model.jsonrpcresponse import JsonRpcResponse
from jsonrpc.model.jsonrpcrequest import JsonRpcRequest
from jsonrpc.validator.validator import Validator


class JsonRpcParser:

    def parse(self, json_data: str) -> Entity:

        try:
            data = json.loads(json_data)
        except JSONDecodeError:
            return JsonRpcError("2.0", JsonRpcErrorCode.ParseError)

        if self._is_request(data):
            return JsonRpcRequest(data["jsonrpc"], data["method"], data["params"], data["id"])

        if self._is_response(data):
            return JsonRpcResponse(data["jsonrpc"], data["result"], data["id"])

        if self._is_error(data):
            error_content = data["error"]
            return JsonRpcError(data["jsonrpc"], error_content["code"], data["id"])

        if self._is_notification(data):
            if "params" in data:
                return JsonRpcNotification(data["jsonrpc"], data["method"], data["params"])

            return JsonRpcNotification(data["jsonrpc"], data["method"])

        if self._is_batch(data):
            batch = JsonRpcBatch()

            if not data:
                batch.elements.append(JsonRpcError("2.0", JsonRpcErrorCode.InvalidRequest))
                return batch

            for element in data:
                batch.elements.append(self.parse(str(element)))
            return batch

        if isinstance(data, dict) and "id" in data:
            return JsonRpcError("2.0", JsonRpcErrorCode.InvalidRequest, data["id"])

        return JsonRpcError("2.0", JsonRpcErrorCode.InvalidRequest)

    @staticmethod
    def _is_batch(data) -> bool:
        return isinstance(data, list)

    @staticmethod
    def _is_error(data) -> bool:
        return isinstance(data, dict) and Validator.validate_jsonrpc_from_json(data) \
            and Validator.validate_error_from_json(data) \
            and Validator.validate_id_from_json(data)

    @staticmethod
    def _is_notification(data) -> bool:
        return isinstance(data, dict) and (
                (Validator.validate_jsonrpc_from_json(data)
                 and Validator.validate_method_from_json(data))
                or
                (Validator.validate_jsonrpc_from_json(data)
                 and Validator.validate_method_from_json(data)
                 and Validator.validate_params_from_json(data))
        )

    @staticmethod
    def _is_request(data) -> bool:
        return isinstance(data, dict) \
            and Validator.validate_jsonrpc_from_json(data) \
            and Validator.validate_method_from_json(data) \
            and Validator.validate_params_from_json(data) \
            and Validator.validate_id_from_json(data)

    @staticmethod
    def _is_response(data) -> bool:
        return isinstance(data, dict) \
            and Validator.validate_jsonrpc_from_json(data) \
            and Validator.validate_result_from_json(data) \
            and Validator.validate_id_from_json(data)
