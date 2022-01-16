import json
import os

from jsonschema.validators import validate

from serverlessworkflow_sdk.workflow import Workflow


class WorkflowValidator:
    workflow: Workflow
    json_schema_content: object = None

    def __init__(self, workflow: Workflow):
        self.workflow = workflow

        if not self.json_schema_content:
            file_json_schema = os.path.join(os.path.dirname(__file__), 'jsonschemas', 'workflow.json')
            with open(file_json_schema, "r") as json_schema:
                self.json_schema_content = json.load(json_schema)

    def validate(self):
        workflow = json.loads(json.dumps(self.workflow, default=lambda o: o.__dict__))
        validate(workflow, self.json_schema_content)

    def __repr__(self):
        return "{!r}".format(self.__dict__)
