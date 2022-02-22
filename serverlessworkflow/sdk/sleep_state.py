from __future__ import annotations

import copy

from serverlessworkflow.sdk.end import End
from serverlessworkflow.sdk.error import Error
from serverlessworkflow.sdk.hydration import HydratableParameter, ComplexTypeOf, UnionTypeOf, SimpleTypeOf, \
    ArrayTypeOf, Fields
from serverlessworkflow.sdk.metadata import Metadata
from serverlessworkflow.sdk.sleep_state_timeout import SleepStateTimeOut
from serverlessworkflow.sdk.state import State
from serverlessworkflow.sdk.state_data_filter import StateDataFilter
from serverlessworkflow.sdk.transition import Transition


class SleepState(State):
    id: str = None
    name: str = None
    type: str = None
    end: (bool | End) = None
    stateDataFilter: StateDataFilter = None
    duration: str = None
    timeouts: SleepStateTimeOut = None
    onErrors: [Error] = None
    transition: (str | Transition) = None
    compensatedBy: str = None
    usedForCompensation: bool = None
    metadata: Metadata = None

    def __init__(self,
                 id: str = None,
                 name: str = None,
                 type: str = None,
                 end: (bool | End) = None,
                 stateDataFilter: StateDataFilter = None,
                 duration: str = None,
                 timeouts: SleepStateTimeOut = None,
                 onErrors: [Error] = None,
                 transition: (str | Transition) = None,
                 compensatedBy: str = None,
                 usedForCompensation: bool = None,
                 metadata: Metadata = None,
                 **kwargs):
        Fields(locals(), kwargs, SleepState.f_hydration).set_to_object(self)

    @staticmethod
    def f_hydration(p_key, p_value):

        if p_key == 'end':
            return HydratableParameter(value=p_value).hydrateAs(UnionTypeOf([SimpleTypeOf(bool),
                                                                             ComplexTypeOf(End)]))

        if p_key == 'stateDataFilter':
            return HydratableParameter(value=p_value).hydrateAs(ComplexTypeOf(StateDataFilter))

        if p_key == 'timeouts':
            return HydratableParameter(value=p_value).hydrateAs(ComplexTypeOf(SleepStateTimeOut))

        if p_key == 'onErrors':
            return HydratableParameter(value=p_value).hydrateAs(ArrayTypeOf(Error))

        if p_key == 'transition':
            return HydratableParameter(value=p_value).hydrateAs(UnionTypeOf([SimpleTypeOf(str),
                                                                             ComplexTypeOf(Transition)]))

        return copy.deepcopy(p_value)
