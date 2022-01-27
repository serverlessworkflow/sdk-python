import json

import yaml

from serverlessworkflow.sdk.injectstate import Injectstate
from serverlessworkflow.sdk.operationstate import Operationstate
from serverlessworkflow.sdk.state import State


def is_inject_state(state: State):
    return state['type'] == 'inject'


def is_operation_state(state: State):
    return state['type'] == 'operation'


class Workflow:
    id = None
    key = None
    name = None
    description = None
    version = None
    annotations = None
    dataInputSchema = None
    schema = None
    failOnValidationErrors = None
    secrets = None
    constants = None
    start = None
    specVersion = None
    expressionLang = None
    timeouts = None
    errors = None
    keepActive = None
    metadata = None
    events = None
    functions = None
    autoRetries = None
    retries = None
    auth = None
    states = None

    def __init__(self,
                 id_=None,
                 key=None,
                 name=None,
                 version=None,
                 description=None,
                 specVersion=None,
                 annotations=None,
                 dataInputSchema=None,
                 schema=None,
                 failOnValidationErrors=None,
                 secrets=None,
                 constants=None,
                 start=None,
                 expressionLang=None,
                 timeouts=None,
                 errors=None,
                 keepActive=None,
                 metadata=None,
                 events=None,
                 autoRetries=None,
                 retries=None,
                 auth=None,
                 states=None,
                 functions=None,
                 **kwargs):

        # duplicated
        for local in list(locals()):
            if local in ["self", "kwargs"]:
                continue
            value = locals().get(local)
            if not value:
                continue
            if value == "true":
                value = True
            # duplicated

            if local == 'states':
                value = Workflow.load_states(value)

            self.__setattr__(local.replace("_", ""), value)

        # duplicated
        for k in kwargs.keys():
            value = kwargs[k]
            if value == "true":
                value = True

            self.__setattr__(k.replace("_", ""), value)
        # duplicated

    def to_json(self) -> str:
        return json.dumps(self,
                          default=lambda o: o.__dict__,
                          indent=4)

    def to_yaml(self):
        def noop(self_, *args, **kw):
            pass

        yaml.emitter.Emitter.process_tag = noop
        return yaml.dump(self,
                         sort_keys=False,
                         # , default_flow_style=False,
                         allow_unicode=True,
                         )

    @classmethod
    def from_source(cls, source: str):
        try:
            loaded_data = yaml.safe_load(source)
            loaded_data["id_"] = loaded_data["id"]
            del loaded_data["id"]
            return cls(**loaded_data)
        except Exception:
            raise Exception("Format not supported")

    @staticmethod
    def load_states(states: [State]):
        result = []
        for state in states:
            if is_inject_state(state):
                result.append(Injectstate(**(states[0])))
            elif is_operation_state(state):
                result.append(Operationstate(**(states[0])))
            else:
                result.append(State(**(states[0])))

        return result

    def __repr__(self):
        return "{!r}".format(self.__dict__)
