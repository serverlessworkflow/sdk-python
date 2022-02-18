import json
import os
import unittest
from os import listdir

from jsonschema.exceptions import ValidationError

from serverlessworkflow.sdk.workflow import Workflow
from serverlessworkflow.sdk.workflow_validator import WorkflowValidator


class TestWorkflowValidator(unittest.TestCase):

    def test_validate_examples(self):
        examples_dir = os.path.join(os.path.dirname(__file__), '../../examples')
        examples = listdir(examples_dir)
        self.assertEqual(len(examples), 9)

        for example in examples:
            with self.subTest(f"test_{example}"):

                with open(examples_dir + "/" + example, "r") as swf_file:
                    swf_file_content = json.load(swf_file)
                    workflow = Workflow(**swf_file_content)
                    WorkflowValidator(workflow).validate()

    def test_invalid_wf(self):
        wf_file = os.path.join(os.path.dirname(__file__), '../../examples', 'applicantrequest.json')

        with open(wf_file, "r") as swf_file:
            swf_content = swf_file.read()

            workflow = Workflow.from_source(swf_content)
            workflow.specVersion = None
            with self.assertRaises(ValidationError):
                WorkflowValidator(Workflow(workflow)).validate()

