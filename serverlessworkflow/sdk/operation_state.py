from typing import Union

from serverlessworkflow.sdk.action import Action
from serverlessworkflow.sdk.end import End
from serverlessworkflow.sdk.enums import ActionMode
from serverlessworkflow.sdk.error import Error
from serverlessworkflow.sdk.metadata import Metadata
from serverlessworkflow.sdk.operation_state_timeout import OperationStateTimeOut
from serverlessworkflow.sdk.state_data_filter import StateDataFilter
from serverlessworkflow.sdk.transition import Transition


class OperationState:
    id: str = None
    name: str = None
    type: str = None
    end: Union[bool, End] = None
    stateDataFilter: StateDataFilter = None
    actionMode: ActionMode = None
    actions: [Action] = None
    timeouts: OperationStateTimeOut = None
    onErrors: [Error] = None
    transition: Union[str, Transition] = None
    compensatedBy: str = None
    usedForCompensation: bool = None
    metadata: Metadata = None

    def __init__(self,
                 id: str = None,
                 name: str = None,
                 type: str = None,
                 stateDataFilter: StateDataFilter = None,
                 actionMode: ActionMode = None,
                 actions: [Action] = None,
                 timeouts: OperationStateTimeOut = None,
                 onErrors: [Error] = None,
                 transition: Union[str, Transition] = None,
                 compensatedBy: str = None,
                 usedForCompensation: bool = None,
                 metadata: Metadata = None,
                 end: Union[bool, End] = None,
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
        return [Action(**action) if type(action) is not Action else action for action in value]
