from __future__ import annotations

import copy

from serverlessworkflow.sdk.action import Action
from serverlessworkflow.sdk.end import End
from serverlessworkflow.sdk.error import Error
from serverlessworkflow.sdk.metadata import Metadata
from serverlessworkflow.sdk.operation_state_timeout import OperationStateTimeOut
from serverlessworkflow.sdk.state import State
from serverlessworkflow.sdk.state_data_filter import StateDataFilter
from serverlessworkflow.sdk.swf_base import HydratableParameter, ComplexTypeOf, ArrayTypeOf, UnionTypeOf, \
    SimpleTypeOf, SwfBase
from serverlessworkflow.sdk.transition import Transition


class OperationState(State, SwfBase):
    id: str = None
    name: str = None
    type: str = None
    end: (bool | End) = None
    stateDataFilter: StateDataFilter = None
    actionMode: str = None
    actions: [Action] = None
    timeouts: OperationStateTimeOut = None
    onErrors: [Error] = None
    transition: (str | Transition) = None
    compensatedBy: str = None
    usedForCompensation: bool = None
    metadata: Metadata = None

    def __init__(self,
                 id: str = None,
                 name: str = None,
                 type: str = None,
                 stateDataFilter: StateDataFilter = None,
                 actionMode: str = None,
                 actions: [Action] = None,
                 timeouts: OperationStateTimeOut = None,
                 onErrors: [Error] = None,
                 transition: (str | Transition) = None,
                 compensatedBy: str = None,
                 usedForCompensation: bool = None,
                 metadata: Metadata = None,
                 end: (bool | End) = None,
                 **kwargs):

        _default_values = {'type': 'operation', 'actionMode': 'sequential', 'usedForCompensation': False}
        SwfBase.__init__(self, locals(), kwargs, OperationState.f_hydration,
                         _default_values)

    @staticmethod
    def f_hydration(p_key, p_value):

        if p_key == 'stateDataFilter':
            return HydratableParameter(value=p_value).hydrateAs(ComplexTypeOf(StateDataFilter))

        if p_key == 'actions':
            return HydratableParameter(value=p_value).hydrateAs(ArrayTypeOf(Action))

        if p_key == 'timeouts':
            return HydratableParameter(value=p_value).hydrateAs(ComplexTypeOf(OperationStateTimeOut))

        if p_key == 'onErrors':
            return HydratableParameter(value=p_value).hydrateAs(ArrayTypeOf(Error))

        if p_key == 'transition':
            return HydratableParameter(value=p_value).hydrateAs(
                UnionTypeOf([SimpleTypeOf(str), ComplexTypeOf(Transition)]))

        if p_key == 'end':
            return HydratableParameter(value=p_value).hydrateAs(UnionTypeOf([SimpleTypeOf(bool), ComplexTypeOf(End)]))

        return copy.deepcopy(p_value)
