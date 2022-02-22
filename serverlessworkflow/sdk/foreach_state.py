from __future__ import annotations

import copy

from serverlessworkflow.sdk.action import Action
from serverlessworkflow.sdk.end import End
from serverlessworkflow.sdk.error import Error
from serverlessworkflow.sdk.foreach_state_timeout import ForEachStateTimeOut
from serverlessworkflow.sdk.hydration import SimpleTypeOf, ComplexTypeOf, UnionTypeOf, HydratableParameter, \
    ArrayTypeOf, Fields
from serverlessworkflow.sdk.metadata import Metadata
from serverlessworkflow.sdk.state import State
from serverlessworkflow.sdk.state_data_filter import StateDataFilter
from serverlessworkflow.sdk.transition import Transition


class ForEachState(State):
    id: str = None
    name: str = None
    type: str = None
    end: (bool | End) = None
    inputCollection: str = None
    outputCollection: str = None
    iterationParam: str = None
    batchSize: (int | str) = None
    actions: [Action] = None
    timeouts: ForEachStateTimeOut = None
    stateDataFilter: StateDataFilter = None
    onErrors: [Error] = None
    transition: (str | Transition) = None
    compensatedBy: str = None
    usedForCompensation: bool = None
    mode: str = None
    metadata: Metadata = None

    def __init__(self,
                 id: str = None,
                 name: str = None,
                 type: str = None,
                 end: (bool | End) = None,
                 inputCollection: str = None,
                 outputCollection: str = None,
                 iterationParam: str = None,
                 batchSize: (int | str) = None,
                 actions: [Action] = None,
                 timeouts: ForEachStateTimeOut = None,
                 stateDataFilter: StateDataFilter = None,
                 onErrors: [Error] = None,
                 transition: (str | Transition) = None,
                 compensatedBy: str = None,
                 usedForCompensation: bool = None,
                 mode: str = None,
                 metadata: Metadata = None,
                 **kwargs):
        Fields(locals(), kwargs, ForEachState.f_hydration).set_to_object(self)

    @staticmethod
    def f_hydration(p_key, p_value):

        if p_key == 'end':
            return HydratableParameter(value=p_value).hydrateAs(UnionTypeOf([SimpleTypeOf(bool),
                                                                             ComplexTypeOf(End)]))
        if p_key == 'batchSize':
            return HydratableParameter(value=p_value).hydrateAs(UnionTypeOf([SimpleTypeOf(str),
                                                                             SimpleTypeOf(int)]))

        if p_key == 'actions':
            return HydratableParameter(value=p_value).hydrateAs(ArrayTypeOf(Action))

        if p_key == 'timeouts':
            return HydratableParameter(value=p_value).hydrateAs(ComplexTypeOf(ForEachStateTimeOut))

        if p_key == 'stateDataFilter':
            return HydratableParameter(value=p_value).hydrateAs(ComplexTypeOf(StateDataFilter))

        if p_key == 'onErrors':
            return HydratableParameter(value=p_value).hydrateAs(ArrayTypeOf(Error))

        if p_key == 'transition':
            return HydratableParameter(value=p_value).hydrateAs(UnionTypeOf([SimpleTypeOf(str),
                                                                             ComplexTypeOf(Transition)]))

        return copy.deepcopy(p_value)
