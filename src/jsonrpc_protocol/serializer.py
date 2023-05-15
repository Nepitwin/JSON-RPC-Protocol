import json
from json import JSONDecodeError

from jsonrpc_protocol.enum import ProtocolVersion
from jsonrpc_protocol.enum import ErrorCode
from jsonrpc_protocol.protocol import Params
from jsonrpc_protocol.protocol.entity import Entity
from jsonrpc_protocol.protocol.notification import Notification
from jsonrpc_protocol.protocol.response import Response
from jsonrpc_protocol.protocol.request import Request
from jsonrpc_protocol.protocol.batch import Batch
from jsonrpc_protocol.protocol.error import Error
from jsonrpc_protocol.validator import Validator


class Serializer:

    @staticmethod
    def parse(json_data: str, protocol_version: ProtocolVersion = ProtocolVersion.v2) -> Entity:

        try:
            json_data = json.loads(json_data)
        except JSONDecodeError:
            return Error(protocol_version, ErrorCode.ParseError)

        if isinstance(json_data, dict):
            try:
                protocol_version = ProtocolVersion.from_str(json_data["jsonrpc"])

                if Serializer._is_request(json_data, protocol_version):
                    return Request(protocol_version, json_data["method"], Params(json_data["params"]), json_data["id"])

                if Serializer._is_response(json_data, protocol_version):
                    return Response(protocol_version, json_data["result"], json_data["id"])

                if Serializer._is_notification(json_data, protocol_version):
                    if "params" in json_data:
                        return Notification(protocol_version, json_data["method"], Params(json_data["params"]))

                    return Notification(protocol_version, json_data["method"])

                if Serializer._is_error(json_data, protocol_version):
                    error_content = json_data["error"]
                    return Error(protocol_version, error_content["code"], json_data["id"])

            except NotImplementedError:
                pass
            except KeyError:
                pass
            except ValueError:
                pass

        elif Serializer._is_batch(json_data, protocol_version):
            if not json_data:
                return Error(protocol_version, ErrorCode.InvalidRequest)

            batch = Batch()

            for element in json_data:
                batch.elements.append(Serializer.parse(json.dumps(element)))

            return batch

        if isinstance(json_data, dict) and "id" in json_data:
            return Error(protocol_version, ErrorCode.InvalidRequest, json_data["id"])

        return Error(protocol_version, ErrorCode.InvalidRequest)

    @staticmethod
    def _is_batch(json_data: object, protocol: ProtocolVersion) -> bool:
        return isinstance(json_data, list) and protocol == ProtocolVersion.v2

    @staticmethod
    def _is_error(json_data: dict, protocol: ProtocolVersion) -> bool:
        return Validator.validate_jsonrpc_from_json(json_data, protocol) \
            and Validator.validate_error_from_json(json_data) \
            and Validator.validate_id_from_json(json_data) \
            and protocol == ProtocolVersion.v2

    @staticmethod
    def _is_notification(json_data: dict, protocol: ProtocolVersion) -> bool:
        return (Validator.validate_jsonrpc_from_json(json_data, protocol)
                and Validator.validate_method_from_json(json_data)) \
            or (Validator.validate_jsonrpc_from_json(json_data, protocol)
                and Validator.validate_method_from_json(json_data)
                and Validator.validate_params_from_json(json_data))

    @staticmethod
    def _is_request(json_data: dict, protocol: ProtocolVersion) -> bool:
        return Validator.validate_jsonrpc_from_json(json_data, protocol) \
            and Validator.validate_method_from_json(json_data) \
            and Validator.validate_params_from_json(json_data) \
            and Validator.validate_id_from_json(json_data)

    @staticmethod
    def _is_response(data: dict, protocol: ProtocolVersion) -> bool:
        return Validator.validate_jsonrpc_from_json(data, protocol) \
            and Validator.validate_result_from_json(data) \
            and Validator.validate_id_from_json(data)
