import json
import os
import unittest
from os import listdir

from serverlessworkflow.sdk.action import Action
from serverlessworkflow.sdk.function import Function
from serverlessworkflow.sdk.function_ref import FunctionRef
from serverlessworkflow.sdk.workflow import Workflow


class TestWorkflow(unittest.TestCase):
    workflow = Workflow(id_="greeting",
                        name="Greeting Workflow",
                        description="Greet Someone",
                        version='1.0',
                        specVersion='0.8',
                        start="Greet",
                        states=[
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
                                "end": True
                            }
                        ],
                        functions=[
                            {
                                "name": "greetingFunction",
                                "operation": "file://myapis/greetingapis.json#greeting"
                            }
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

    def test_workflow_from_source_json(self):
        examples_dir = os.path.join(os.path.dirname(__file__), '../../examples')
        examples = listdir(examples_dir)
        self.assertEqual(len(examples), 10)

        for example in examples:
            with self.subTest(f"test_{example}"):
                with open(examples_dir + "/" + example, "r") as swf_file:
                    workflow = Workflow.from_source(swf_file)
                    self.assertTrue(isinstance(workflow, Workflow))

    def test_instance_workflow_class(self):
        examples_dir = os.path.join(os.path.dirname(__file__), '../../examples')
        examples = listdir(examples_dir)
        self.assertEqual(len(examples), 10)

        for example in examples:
            with self.subTest(f"test_{example}"):
                with open(examples_dir + "/" + example, "r") as swf_file:
                    workflow = Workflow(**json.load(swf_file))
                    self.assertTrue(isinstance(workflow, Workflow))

    def test_workflow_from_source_yaml(self):
        wf_file = os.path.join(os.path.dirname(__file__), 'test_workflow.yaml')
        self.assert_test_workflow_file(wf_file)

    def assert_test_workflow_file(self, wf_file):
        with open(wf_file, "r") as swf_file:
            swf_content = swf_file.read()

            workflow = Workflow.from_source(swf_content)

            self.assertEqual("greeting", workflow.id)
            self.assertEqual("operation", workflow.states[0].type)
            self.assertEqual(True, workflow.states[0].end)
            self.assertTrue(isinstance(workflow.states[0].actions[0], Action))
            self.assertTrue(isinstance(workflow.states[0].actions[0].functionRef, FunctionRef))
            self.assertTrue(isinstance(workflow.functions[0], Function))
