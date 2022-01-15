import json

import yaml

from serverlessworkflow_sdk.inject_state import InjectState
from serverlessworkflow_sdk.operation_state import OperationState
from serverlessworkflow_sdk.state import State


def is_inject_state(state: State):
    return state['type'] == 'inject'


def is_operation_state(state: State):
    return state['type'] == 'operation'


class Workflow:
    id: str
    key: str
    name: str
    version: str
    description: str
    specVersion: str
    start: str
    states: [State]
    functions: []

    def __init__(self,
                 id_: str = None,
                 key: str = None,
                 name: str = None,
                 version: str = None,
                 description: str = None,
                 specVersion: str = None,
                 start: str = None,
                 states: [State] = None,
                 functions: [] = None,
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
                result.append(InjectState(**(states[0])))
            elif is_operation_state(state):
                result.append(OperationState(**(states[0])))
            else:
                result.append(State(**(states[0])))

        return result

    def __repr__(self):
        return "{!r}".format(self.__dict__)
