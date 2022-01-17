from serverlessworkflow.sdk.action import Action
from serverlessworkflow.sdk.state import State


class OperationState(State):
    
    name: str
    type: str
    actions: [Action]
    end: bool
    dataConditions: object #TODO
    defaultCondition: object #TODO

    def __init__(self, name: str = None,
                 type: str = "operation",
                 actions: [Action] = None,
                 end: bool = None,
                 dataConditions: object = None,
                 defaultCondition: object = None,
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

            if local == 'actions':
                value = OperationState.load_actions(value)


            self.__setattr__(local.replace("_", ""), value)

        # duplicated
        for k in kwargs.keys():
            value = kwargs[k]
            if value == "true":
                value = True

            if k == 'actions':
                value = OperationState.load_actions(value)

            self.__setattr__(k.replace("_", ""), value)
            # duplicated




    @staticmethod
    def load_actions(value):
        return [Action(**action) for action in value]
