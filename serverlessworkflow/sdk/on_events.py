from serverlessworkflow.sdk.action import Action
from serverlessworkflow.sdk.enums import ActionMode
from serverlessworkflow.sdk.event_data_filter import EventDataFilter


class OnEvents:
    eventRefs: [str] = None
    actionMode: ActionMode = None
    actions: [Action] = None
    eventDataFilter: EventDataFilter = None

    def __init__(self,
                 eventRefs: [str] = None,
                 actionMode: ActionMode = None,
                 actions: [Action] = None,
                 eventDataFilter: EventDataFilter = None,
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

            self.__setattr__(local.replace("_", ""), value)

        # duplicated
        for k in kwargs.keys():
            value = kwargs[k]
            if value == "true":
                value = True

            self.__setattr__(k.replace("_", ""), value)
            # duplicated
