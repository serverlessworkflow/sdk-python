from serverlessworkflow.sdk.action import Action


class Operationstate:
    id = None
    name = None
    type = None
    end = None
    stateDataFilter = None
    actionMode = None
    actions = None
    timeouts = None
    stateExecTimeout = None
    actionExecTimeout = None
    onErrors = None
    transition = None
    compensatedBy = None
    usedForCompensation = None
    metadata = None

    def __init__(self,
                 id=None,
                 name=None,
                 type=None,
                 stateDataFilter=None,
                 actionMode=None,
                 actions=None,
                 end=None,
                 timeouts=None,
                 stateExecTimeout=None,
                 actionExecTimeout=None,
                 onErrors=None,
                 transition=None,
                 compensatedBy=None,
                 usedForCompensation=None,
                 metadata=None,
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
                value = Operationstate.load_actions(value)

            self.__setattr__(local.replace("_", ""), value)

        # duplicated
        for k in kwargs.keys():
            value = kwargs[k]
            if value == "true":
                value = True

            if k == 'actions':
                value = Operationstate.load_actions(value)

            self.__setattr__(k.replace("_", ""), value)
            # duplicated

    @staticmethod
    def load_actions(value):
        return [Action(**action) for action in value]
