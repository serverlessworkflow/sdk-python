import os
import unittest
from os import listdir

from serverlessworkflow.sdk.action import Action
from serverlessworkflow.sdk.action_data_filter import ActionDataFilter
from serverlessworkflow.sdk.function import Function
from serverlessworkflow.sdk.function_ref import FunctionRef
from serverlessworkflow.sdk.operation_state import OperationState
from serverlessworkflow.sdk.workflow import Workflow


class TestWorkflow(unittest.TestCase):
    workflow = Workflow(
        id="greeting",
        name="Greeting Workflow",
        description="Greet Someone",
        version='1.0',
        specVersion='0.8',
        start="Greet",
        states=[
            OperationState(
                name="Greet",
                type="operation",
                actions=[
                    Action(
                        functionRef=FunctionRef(
                            refName="greetingFunction",
                            arguments={
                                "name": "${ .person.name }"
                            }
                        ),
                        actionDataFilter=ActionDataFilter(
                            results="${ .greeting }"
                        )
                    )
                ],
                end=True
            )
        ],
        functions=[
            Function(name="greetingFunction",
                     operation="file://myapis/greetingapis.json#greeting")
        ]
    )

    def test_workflow_to_json(self):
        expected = """{
    "id": "greeting",
    "name": "Greeting Workflow",
    "version": "1.0",
    "description": "Greet Someone",
    "specVersion": "0.8",
    "start": "Greet",
    "states": [
        {
            "name": "Greet",
            "type": "operation",
            "actions": [
                {
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
            ],
            "end": true
        }
    ],
    "functions": [
        {
            "name": "greetingFunction",
            "operation": "file://myapis/greetingapis.json#greeting"
        }
    ]
}"""

        self.assertEqual(expected, self.workflow.to_json())

    def test_workflow_to_yaml(self):
        expected = """id: greeting
name: Greeting Workflow
version: '1.0'
description: Greet Someone
specVersion: '0.8'
start: Greet
states:
- name: Greet
  type: operation
  actions:
  - functionRef:
      refName: greetingFunction
      arguments:
        name: ${ .person.name }
    actionDataFilter:
      results: ${ .greeting }
  end: true
functions:
- name: greetingFunction
  operation: file://myapis/greetingapis.json#greeting
"""
        self.assertEqual(expected, self.workflow.to_yaml())

    def test_programmatically_create_workflow(self):

        self.assertEqual("greeting", self.workflow.id)
        self.assertEqual("operation", self.workflow.states[0].type)
        self.assertTrue(isinstance(self.workflow.states[0], OperationState))
        self.assertEqual(True, self.workflow.states[0].end)
        self.assertTrue(isinstance(self.workflow.states[0].actions[0], Action))
        self.assertTrue(isinstance(self.workflow.states[0].actions[0].functionRef, FunctionRef))
        self.assertTrue(isinstance(self.workflow.functions[0], Function))

    def test_workflow_from_source_json(self):
        examples_dir = os.path.join(os.path.dirname(__file__), '../../examples')
        examples = listdir(examples_dir)
        self.assertEqual(len(examples), 10)

        for example in examples:
            with self.subTest(f"test_{example}"):
                with open(examples_dir + "/" + example, "r") as swf_file:
                    workflow = Workflow.from_source(swf_file.read())
                    self.assertTrue(isinstance(workflow, Workflow))

    def test_instance_workflow_class(self):
        examples_dir = os.path.join(os.path.dirname(__file__), '../../examples')
        examples = listdir(examples_dir)
        self.assertEqual(len(examples), 10)

        for example in examples:
            with self.subTest(f"test_{example}"):
                with open(examples_dir + "/" + example, "r") as swf_file:
                    workflow = Workflow.from_source(swf_file.read())
                    self.assertTrue(isinstance(workflow, Workflow))

    def test_workflow_from_source_yaml(self):
        wf_file = os.path.join(os.path.dirname(__file__), 'test_workflow.yaml')
        self.assert_test_workflow_file(wf_file)

    def assert_test_workflow_file(self, wf_file):
        with open(wf_file, "r") as swf_file:
            workflow = Workflow.from_source(swf_file.read())

            self.assertEqual("greeting", workflow.id)
            self.assertEqual("operation", workflow.states[0].type)
            self.assertEqual(True, workflow.states[0].end)
            self.assertEqual('jq', workflow.expressionLang)
            self.assertTrue(isinstance(workflow.states[0].actions[0], Action))
            self.assertTrue(isinstance(workflow.states[0].actions[0].functionRef, FunctionRef))
            self.assertTrue(isinstance(workflow.functions[0], Function))
