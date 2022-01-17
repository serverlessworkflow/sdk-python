import json
import requests
from jsonschema.validators import validate
from serverlessworkflow_sdk.workflow import Workflow


class WorkflowValidator:
    workflow: Workflow
    json_schema_content: object = None
    SCHEMAS_WORKFLOW_JSON = "https://serverlessworkflow.io/schemas/0.8/workflow.json"

    def __init__(self, workflow: Workflow):
        self.workflow = workflow

        file_json_schema = requests.get(self.SCHEMAS_WORKFLOW_JSON)
        self.json_schema_content = file_json_schema.json()

    def validate(self):
        workflow = json.loads(json.dumps(self.workflow, default=lambda o: o.__dict__))
        validate(workflow, self.json_schema_content)

    def __repr__(self):
        return "{!r}".format(self.__dict__)
