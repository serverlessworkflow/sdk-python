from __future__ import annotations

import copy

from serverlessworkflow.sdk.branch import Branch
from serverlessworkflow.sdk.end import End
from serverlessworkflow.sdk.error import Error
from serverlessworkflow.sdk.metadata import Metadata
from serverlessworkflow.sdk.parallel_state_timeout import ParallelStateTimeOut
from serverlessworkflow.sdk.state import State
from serverlessworkflow.sdk.state_data_filter import StateDataFilter
from serverlessworkflow.sdk.swf_base import HydratableParameter, UnionTypeOf, SimpleTypeOf, ComplexTypeOf, \
    ArrayTypeOf, SwfBase
from serverlessworkflow.sdk.transition import Transition


class ParallelState(State, SwfBase):
    id: str = None
    name: str = None
    type: str = None
    end: (bool | End) = None
    stateDataFilter: StateDataFilter = None
    timeouts: ParallelStateTimeOut = None
    branches: [Branch] = None
    completionType: str = None
    numCompleted: (int | str) = None
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
                 timeouts: ParallelStateTimeOut = None,
                 branches: [Branch] = None,
                 completionType: str = None,
                 numCompleted: (int | str) = None,
                 onErrors: [Error] = None,
                 transition: (str | Transition) = None,
                 compensatedBy: str = None,
                 usedForCompensation: bool = None,
                 metadata: Metadata = None,
                 **kwargs):

        _default_values = {'type': 'parallel', 'completionType': 'allOf', 'usedForCompensation': False}
        SwfBase.__init__(self, locals(), kwargs, ParallelState.f_hydration,
                         _default_values)

    @staticmethod
    def f_hydration(p_key, p_value):
        if p_key == 'end':
            return HydratableParameter(value=p_value).hydrateAs(UnionTypeOf([SimpleTypeOf(bool),
                                                                             ComplexTypeOf(End)]))
        if p_key == 'stateDataFilter':
            return HydratableParameter(value=p_value).hydrateAs(ComplexTypeOf(StateDataFilter))

        if p_key == 'timeouts':
            return HydratableParameter(value=p_value).hydrateAs(ComplexTypeOf(ParallelStateTimeOut))

        if p_key == 'branches':
            return HydratableParameter(value=p_value).hydrateAs(ArrayTypeOf(Branch))

        if p_key == 'branches':
            return HydratableParameter(value=p_value).hydrateAs(ArrayTypeOf(Branch))

        if p_key == 'numCompleted':
            return HydratableParameter(value=p_value).hydrateAs(UnionTypeOf([SimpleTypeOf(int),
                                                                             SimpleTypeOf(str)]))

        if p_key == 'onErrors':
            return HydratableParameter(value=p_value).hydrateAs(ArrayTypeOf(Error))

        if p_key == 'transition':
            return HydratableParameter(value=p_value).hydrateAs(UnionTypeOf([SimpleTypeOf(str),
                                                                             ComplexTypeOf(Transition)]))

        return copy.deepcopy(p_value)
