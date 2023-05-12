from jsonrpc.model.jsonrpcrequest import JsonRpcRequest
from jsonrpc.model.jsonrpcresponse import JsonRpcResponse
from jsonrpc.model.jsonrpcnotification import JsonRpcNotification
from jsonrpc.model.jsonrpcerror import JsonRpcError
from jsonrpc.model.jsonrpcbatch import JsonRpcBatch
from jsonrpc.parser import JsonRpcParser
from typing import cast

import unittest


class TestJsonParser(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = JsonRpcParser()

    def _is_entity_type_of(self, entity,
                           is_batch=False, is_error=False, is_notification=False, is_request=False, is_response=False):
        self.assertEqual(entity.is_request, is_request)
        self.assertEqual(entity.is_response, is_response)
        self.assertEqual(entity.is_notification, is_notification)
        self.assertEqual(entity.is_error, is_error)
        self.assertEqual(entity.is_batch, is_batch)

    def _expect_json_error_in_batch(self, entity):
        self.assertTrue(type(entity) is JsonRpcError)
        entity = cast(JsonRpcError, entity)
        self._is_entity_type_of(entity, is_error=True)
        self.assertEqual(entity.jsonrpc, "2.0")
        self.assertEqual(entity.error, {
            "code": -32600,
            "message": "Invalid Request",
        })
        self.assertEqual(entity.id, None)
        self.assertEqual(entity.dump(),
                         '{"jsonrpc": "2.0", "error": {"code": -32600, "message": "Invalid Request"}, "id": null}')

    def test_json_rpc_request_as_positional_arguments(self):
        json = '{"jsonrpc": "2.0", "method": "subtract", "params": [42, 23], "id": 1}'
        entity = self.parser.parse(json)
        self.assertTrue(type(entity) is JsonRpcRequest)
        entity = cast(JsonRpcRequest, entity)
        self._is_entity_type_of(entity, is_request=True)
        self.assertEqual(entity.jsonrpc, "2.0")
        self.assertEqual(entity.method, "subtract")
        self.assertEqual(entity.params, [42, 23])
        self.assertEqual(entity.id, 1)
        self.assertEqual(entity.dump(), json)

    def test_json_rpc_request_as_named_arguments(self):
        json = '{"jsonrpc": "2.0", "method": "subtract", "params": {"subtrahend": 23, "minuend": 42}, "id": 3}'
        entity = self.parser.parse(json)
        self.assertTrue(type(entity) is JsonRpcRequest)
        entity = cast(JsonRpcRequest, entity)
        self._is_entity_type_of(entity, is_request=True)
        self.assertEqual(entity.jsonrpc, "2.0")
        self.assertEqual(entity.method, "subtract")
        self.assertEqual(entity.params, {"subtrahend": 23, "minuend": 42})
        self.assertEqual(entity.id, 3)
        self.assertEqual(entity.dump(), json)

    def test_json_rpc_response(self):
        json = '{"jsonrpc": "2.0", "result": 19, "id": 1}'
        entity = self.parser.parse(json)
        self.assertTrue(type(entity) is JsonRpcResponse)
        entity = cast(JsonRpcResponse, entity)
        self._is_entity_type_of(entity, is_response=True)
        self.assertEqual(entity.jsonrpc, "2.0")
        self.assertEqual(entity.result, 19)
        self.assertEqual(entity.id, 1)
        self.assertEqual(entity.dump(), json)

    def test_json_rpc_notification_with_params(self):
        json = '{"jsonrpc": "2.0", "method": "update", "params": [1, 2, 3, 4, 5]}'
        entity = self.parser.parse(json)
        self.assertTrue(type(entity) is JsonRpcNotification)
        entity = cast(JsonRpcNotification, entity)
        self._is_entity_type_of(entity, is_notification=True)
        self.assertEqual(entity.jsonrpc, "2.0")
        self.assertEqual(entity.method, "update")
        self.assertEqual(entity.params, [1, 2, 3, 4, 5])
        self.assertEqual(entity.dump(), json)

    def test_json_rpc_notification_without_params(self):
        json = '{"jsonrpc": "2.0", "method": "foobar"}'
        entity = self.parser.parse(json)
        self.assertTrue(type(entity) is JsonRpcNotification)
        entity = cast(JsonRpcNotification, entity)
        self._is_entity_type_of(entity, is_notification=True)
        self.assertEqual(entity.jsonrpc, "2.0")
        self.assertEqual(entity.method, "foobar")
        self.assertEqual(entity.params, None)
        self.assertEqual(entity.dump(), json)

    def test_rpc_call_by_invalid_json(self):
        entity = self.parser.parse('{"jsonrpc": "2.0", "method": "foobar, "params": "bar", "baz]')
        self.assertTrue(type(entity) is JsonRpcError)
        entity = cast(JsonRpcError, entity)
        self._is_entity_type_of(entity, is_error=True)
        self.assertEqual(entity.jsonrpc, "2.0")
        self.assertEqual(entity.error, {
            "code": -32700,
            "message": "Parse error",
        })
        self.assertEqual(entity.id, None)
        self.assertEqual(entity.dump(),
                         '{"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}, "id": null}')

    def test_rpc_call_by_invalid_request_object(self):
        entity = self.parser.parse('{"jsonrpc": "2.0", "method": 1, "params": "bar"}')
        self.assertTrue(type(entity) is JsonRpcError)
        entity = cast(JsonRpcError, entity)
        self._is_entity_type_of(entity, is_error=True)
        self.assertEqual(entity.jsonrpc, "2.0")
        self.assertEqual(entity.error, {
            "code": -32600,
            "message": "Invalid Request",
        })
        self.assertEqual(entity.id, None)
        self.assertEqual(entity.dump(),
                         '{"jsonrpc": "2.0", "error": {"code": -32600, "message": "Invalid Request"}, "id": null}')

    def test_rpc_call_by_empty_array(self):
        entity = self.parser.parse('[]')
        self.assertTrue(type(entity) is JsonRpcBatch)
        entity = cast(JsonRpcBatch, entity)
        for sub_entity in entity.elements:
            self._expect_json_error_in_batch(sub_entity)
        self.assertEqual(entity.dump(), '['
                                        '"{\\"jsonrpc\\": \\"2.0\\", \\"error\\": {\\"code\\": -32600, \\"message\\": \\"Invalid Request\\"}, \\"id\\": null}"'
                                        ']')

    def test_rpc_call_by_invalid_batch(self):
        entity = self.parser.parse('[1]')
        self.assertTrue(type(entity) is JsonRpcBatch)
        entity = cast(JsonRpcBatch, entity)
        for sub_entity in entity.elements:
            self._expect_json_error_in_batch(sub_entity)
        self.assertEqual(entity.dump(), '['
                                        '"{\\"jsonrpc\\": \\"2.0\\", \\"error\\": {\\"code\\": -32600, \\"message\\": \\"Invalid Request\\"}, \\"id\\": null}"'
                                        ']')

    def test_rpc_call_by_invalid_multiple_batch(self):
        entity = self.parser.parse('[1,2,3]')
        self.assertTrue(type(entity) is JsonRpcBatch)
        entity = cast(JsonRpcBatch, entity)
        for sub_entity in entity.elements:
            self._expect_json_error_in_batch(sub_entity)
        self.assertEqual(entity.dump(), '['
                                        '"{\\"jsonrpc\\": \\"2.0\\", \\"error\\": {\\"code\\": -32600, \\"message\\": \\"Invalid Request\\"}, \\"id\\": null}", '
                                        '"{\\"jsonrpc\\": \\"2.0\\", \\"error\\": {\\"code\\": -32600, \\"message\\": \\"Invalid Request\\"}, \\"id\\": null}", '
                                        '"{\\"jsonrpc\\": \\"2.0\\", \\"error\\": {\\"code\\": -32600, \\"message\\": \\"Invalid Request\\"}, \\"id\\": null}"'
                                        ']')

    def test_rpc_call_as_batch(self):
        entity = self.parser.parse('[{"jsonrpc": "2.0", "method": "sum", "params": [1,2,4], "id": "1"},'
                                   '{"jsonrpc": "2.0", "method": "notify_hello", "params": [7]},'
                                   '{"jsonrpc": "2.0", "method": "subtract", "params": [42,23], "id": "2"},'
                                   '{"foo": "boo"},'
                                   '{"jsonrpc": "2.0", "method": "foo.get", "params": {"name": "myself"}, "id": "5"},'
                                   '{"jsonrpc": "2.0", "method": "get_data", "id": "9"}]')
        self.assertTrue(type(entity) is JsonRpcBatch)
        # TODO Checkup params

    def test_rpc_error_id_as_string(self):
        json = '{"jsonrpc": "2.0", "error": {"code": -32601, "message": "Method not found"}, "id": "1"}'
        entity = self.parser.parse(json)
        self.assertTrue(type(entity) is JsonRpcError)
        entity = cast(JsonRpcError, entity)
        self._is_entity_type_of(entity, is_error=True)
        self.assertEqual(entity.jsonrpc, "2.0")
        self.assertEqual(entity.error, {
            "code": -32601,
            "message": "Method not found",
        })
        self.assertEqual(entity.id, "1")
        self.assertEqual(entity.dump(), json)

    def test_rpc_error_id_as_number(self):
        json = '{"jsonrpc": "2.0", "error": {"code": -32601, "message": "Method not found"}, "id": 1}'
        entity = self.parser.parse(json)
        self.assertTrue(type(entity) is JsonRpcError)
        entity = cast(JsonRpcError, entity)
        self._is_entity_type_of(entity, is_error=True)
        self.assertEqual(entity.jsonrpc, "2.0")
        self.assertEqual(entity.error, {
            "code": -32601,
            "message": "Method not found",
        })
        self.assertEqual(entity.id, 1)
        self.assertEqual(entity.dump(), json)
