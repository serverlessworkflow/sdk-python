import unittest

from serverlessworkflow.sdk.action import Action
from serverlessworkflow.sdk.action_data_filter import ActionDataFilter
from serverlessworkflow.sdk.function_ref import FunctionRef


class TestAction(unittest.TestCase):

    def test_load_function_ref(self):
        action = Action(functionRef=FunctionRef(refName="refNameTest"),
                        retryableErrors=["err1", "err2"])
        self.assertTrue(isinstance(action.functionRef, FunctionRef))
        self.assertTrue(action.functionRef.refName, "refNameTest")
        self.assertTrue(isinstance(action.retryableErrors, list))


    def test_load_retryable_errors(self):
        action_data = {
            'retryableErrors': ['err1', 'err2']}
        action = Action(**action_data)
        self.assertTrue(isinstance(action.retryableErrors, list))


    def test_dinamic_load(self):
        action_data = {
                                        "functionRef": {
                                            "refName": "greetingFunction",
                                            "arguments": {
                                                "name": "${ .person.name }"
                                            }
                                        },
                                        "actionDataFilter": {
                                            "results": "${ .greeting }"
                                        }
                                    }
        action = Action(**action_data)
        self.assertTrue(isinstance(action.actionDataFilter, ActionDataFilter))
