import json

from jsonrpc_protocol.protocol.request import Request
from jsonrpc_protocol.protocol.response import Response
from jsonrpc_protocol.protocol.notification import Notification
from jsonrpc_protocol.protocol.error import Error
from jsonrpc_protocol.protocol.batch import Batch
from jsonrpc_protocol.serializer import Serializer
from typing import cast

import unittest


class TestParserProtocolV2(unittest.TestCase):
    InvalidRequest = '{"jsonrpc": "2.0", "error": {"code": -32600, "message": "Invalid Request"}, "id": null}'
    ParseError = '{"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}, "id": null}'

    def _is_entity_type_of(self, entity,
                           is_batch=False, is_error=False, is_notification=False, is_request=False, is_response=False):
        self.assertEqual(entity.is_request, is_request)
        self.assertEqual(entity.is_response, is_response)
        self.assertEqual(entity.is_notification, is_notification)
        self.assertEqual(entity.is_error, is_error)
        self.assertEqual(entity.is_batch, is_batch)

    def _expect_json_error_in_batch(self, entity):
        self.assertTrue(type(entity) is Error)
        entity = cast(Error, entity)
        self._is_entity_type_of(entity, is_error=True)
        self.assertEqual(entity.jsonrpc.value, "2.0")
        self.assertEqual(entity.error, {
            "code": -32600,
            "message": "Invalid Request",
        })
        self.assertEqual(entity.id, None)
        self.assertEqual(entity.dump(), self.InvalidRequest)

    def test_json_rpc_request_as_positional_arguments(self):
        data = '{"jsonrpc": "2.0", "method": "subtract", "params": [42, 23], "id": 1}'
        entity = Serializer.parse(data)
        self.assertTrue(type(entity) is Request)
        entity = cast(Request, entity)
        self._is_entity_type_of(entity, is_request=True)
        self.assertEqual(entity.jsonrpc.value, "2.0")
        self.assertEqual(entity.method, "subtract")
        self.assertFalse(entity.params.is_dict)
        self.assertTrue(entity.params.is_array)
        self.assertEqual(entity.params.data, [42, 23])
        self.assertEqual(entity.id, 1)
        self.assertEqual(entity.dump(), data)

    def test_json_rpc_request_as_named_arguments(self):
        data = '{"jsonrpc": "2.0", "method": "subtract", "params": {"subtrahend": 23, "minuend": 42}, "id": 3}'
        entity = Serializer.parse(data)
        self.assertTrue(type(entity) is Request)
        entity = cast(Request, entity)
        self._is_entity_type_of(entity, is_request=True)
        self.assertEqual(entity.jsonrpc.value, "2.0")
        self.assertEqual(entity.method, "subtract")
        self.assertFalse(entity.params.is_array)
        self.assertTrue(entity.params.is_dict)
        self.assertEqual(entity.params.data, {"subtrahend": 23, "minuend": 42})
        self.assertEqual(entity.id, 3)
        self.assertEqual(entity.dump(), data)

    def test_json_rpc_response(self):
        data = '{"jsonrpc": "2.0", "result": 19, "id": 1}'
        entity = Serializer.parse(data)
        self.assertTrue(type(entity) is Response)
        entity = cast(Response, entity)
        self._is_entity_type_of(entity, is_response=True)
        self.assertEqual(entity.jsonrpc.value, "2.0")
        self.assertEqual(entity.result, 19)
        self.assertEqual(entity.id, 1)
        self.assertEqual(entity.dump(), data)

    def test_json_rpc_notification_with_params(self):
        data = '{"jsonrpc": "2.0", "method": "update", "params": [1, 2, 3, 4, 5]}'
        entity = Serializer.parse(data)
        self.assertTrue(type(entity) is Notification)
        entity = cast(Notification, entity)
        self._is_entity_type_of(entity, is_notification=True)
        self.assertEqual(entity.jsonrpc.value, "2.0")
        self.assertEqual(entity.method, "update")
        self.assertTrue(entity.params.is_array)
        self.assertFalse(entity.params.is_dict)
        self.assertEqual(entity.params.data, [1, 2, 3, 4, 5])
        self.assertEqual(entity.dump(), data)

    def test_json_rpc_notification_without_params(self):
        data = '{"jsonrpc": "2.0", "method": "foobar"}'
        entity = Serializer.parse(data)
        self.assertTrue(type(entity) is Notification)
        entity = cast(Notification, entity)
        self._is_entity_type_of(entity, is_notification=True)
        self.assertEqual(entity.jsonrpc.value, "2.0")
        self.assertEqual(entity.method, "foobar")
        self.assertEqual(entity.params, None)
        self.assertEqual(entity.dump(), data)

    def test_rpc_call_by_invalid_json(self):
        entity = Serializer.parse('{"jsonrpc": "2.0", "method": "foobar, "params": "bar", "baz]')
        self.assertTrue(type(entity) is Error)
        entity = cast(Error, entity)
        self._is_entity_type_of(entity, is_error=True)
        self.assertEqual(entity.jsonrpc.value, "2.0")
        self.assertEqual(entity.error, {
            "code": -32700,
            "message": "Parse error",
        })
        self.assertEqual(entity.id, None)
        self.assertEqual(entity.dump(), self.ParseError)

    def test_rpc_call_by_invalid_request_object(self):
        entity = Serializer.parse('{"jsonrpc": "2.0", "method": 1, "params": "bar"}')
        self.assertTrue(type(entity) is Error)
        entity = cast(Error, entity)
        self._is_entity_type_of(entity, is_error=True)
        self.assertEqual(entity.jsonrpc.value, "2.0")
        self.assertEqual(entity.error, {
            "code": -32600,
            "message": "Invalid Request",
        })
        self.assertEqual(entity.id, None)
        self.assertEqual(entity.dump(), self.InvalidRequest)

    def test_rpc_call_by_empty_array(self):
        entity = Serializer.parse('[]')
        self.assertTrue(type(entity) is Error)
        entity = cast(Error, entity)
        self.assertEqual(entity.dump(), self.InvalidRequest)

    def test_rpc_call_by_invalid_batch(self):
        entity = Serializer.parse('[1]')
        self.assertTrue(type(entity) is Batch)
        entity = cast(Batch, entity)
        for sub_entity in entity.elements:
            self._expect_json_error_in_batch(sub_entity)
        expected_json_dict = [self.InvalidRequest]
        self.assertEqual(entity.dump(), json.dumps(expected_json_dict))

    def test_rpc_call_by_invalid_multiple_batch(self):
        entity = Serializer.parse('[1,2,3]')
        self.assertTrue(type(entity) is Batch)
        entity = cast(Batch, entity)
        for sub_entity in entity.elements:
            self._expect_json_error_in_batch(sub_entity)

        expected_json_dict = [self.InvalidRequest, self.InvalidRequest, self.InvalidRequest]
        self.assertEqual(entity.dump(), json.dumps(expected_json_dict))

    def test_rpc_call_as_batch(self):
        entity = Serializer.parse('['
                                  '{"jsonrpc": "2.0", "method": "sum", "params": [1,2,4], "id": "1"},'
                                  '{"jsonrpc": "2.0", "method": "notify_hello", "params": [7]},'
                                  '{"jsonrpc": "2.0", "method": "subtract", "params": [42,23], "id": "2"},'
                                  '{"foo": "boo"},'
                                  '{"jsonrpc": "2.0", "method": "foo.get", "params": {"name": "myself"}, "id": "5"},'
                                  '{"jsonrpc": "2.0", "method": "get_data", "id": "9"}'
                                  ']')
        self.assertTrue(type(entity) is Batch)
        entity = cast(Batch, entity)
        expected_types = [Request, Notification,
                          Request, Error,
                          Request, Notification]
        for i in range(len(expected_types)):
            self.assertTrue(type(entity.elements[i]) is expected_types[i])

    def test_rpc_error_id_as_string(self):
        json = '{"jsonrpc": "2.0", "error": {"code": -32601, "message": "Method not found"}, "id": "1"}'
        entity = Serializer.parse(json)
        self.assertTrue(type(entity) is Error)
        entity = cast(Error, entity)
        self._is_entity_type_of(entity, is_error=True)
        self.assertEqual(entity.jsonrpc.value, "2.0")
        self.assertEqual(entity.error, {
            "code": -32601,
            "message": "Method not found",
        })
        self.assertEqual(entity.id, "1")
        self.assertEqual(entity.dump(), json)

    def test_rpc_error_id_as_number(self):
        data = '{"jsonrpc": "2.0", "error": {"code": -32601, "message": "Method not found"}, "id": 1}'
        entity = Serializer.parse(data)
        self.assertTrue(type(entity) is Error)
        entity = cast(Error, entity)
        self._is_entity_type_of(entity, is_error=True)
        self.assertEqual(entity.jsonrpc.value, "2.0")
        self.assertEqual(entity.error, {
            "code": -32601,
            "message": "Method not found",
        })
        self.assertEqual(entity.id, 1)
        self.assertEqual(entity.dump(), data)

    def test_invalid_params_on_json_rpc_request(self):
        data = '{"jsonrpc": "2.0", "method": "subtract", "params": "hello", "id": 1}'
        entity = Serializer.parse(data)
        self.assertTrue(type(entity) is Error)
        entity = cast(Error, entity)
        self.assertEqual(entity.jsonrpc.value, "2.0")
        self.assertEqual(entity.error, {
            "code": -32600,
            "message": "Invalid Request",
        })
        self.assertEqual(entity.id, 1)

    def test_missing_params_on_json_rpc_request(self):
        data = '{"jsonrpc": "2.0", "method": "subtract", "params": null, "id": 1}'
        entity = Serializer.parse(data)
        self.assertTrue(type(entity) is Error)
        entity = cast(Error, entity)
        self.assertEqual(entity.jsonrpc.value, "2.0")
        self.assertEqual(entity.error, {
            "code": -32600,
            "message": "Invalid Request",
        })
        self.assertEqual(entity.id, 1)

    def test_invalid_params_on_notification_request(self):
        data = '{"jsonrpc": "2.0", "method": "foobar", "params": 5}'
        entity = Serializer.parse(data)
        self.assertTrue(type(entity) is Error)
        entity = cast(Error, entity)
        self.assertEqual(entity.jsonrpc.value, "2.0")
        self.assertEqual(entity.error, {
            "code": -32600,
            "message": "Invalid Request",
        })
        self.assertEqual(entity.id, None)

    def test_missing_params_on_notification_request(self):
        data = '{"jsonrpc": "2.0", "method": "foobar", "params": null}'
        entity = Serializer.parse(data)
        self.assertTrue(type(entity) is Error)
        entity = cast(Error, entity)
        self.assertEqual(entity.jsonrpc.value, "2.0")
        self.assertEqual(entity.error, {
            "code": -32600,
            "message": "Invalid Request",
        })
        self.assertEqual(entity.id, None)
