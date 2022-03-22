from __future__ import annotations

import copy

from serverlessworkflow.sdk.continue_as_def import ContinueAsDef
from serverlessworkflow.sdk.produce_event_def import ProduceEventDef
from serverlessworkflow.sdk.swf_base import HydratableParameter, ArrayTypeOf, UnionTypeOf, SimpleTypeOf, \
    ComplexTypeOf, SwfBase


class End(SwfBase):
    terminate: bool = None
    produceEvents: [ProduceEventDef] = None
    compensate: bool = None
    continueAs: (str | ContinueAsDef) = None

    def __init__(self,
                 terminate: bool = None,
                 produceEvents: [ProduceEventDef] = None,
                 compensate: bool = None,
                 continueAs: (str | ContinueAsDef) = None,
                 **kwargs):

        _default_values = {'compensate': False, 'terminate': False, }
        SwfBase.__init__(self, locals(), kwargs, End.f_hydration,
                         _default_values)

    @staticmethod
    def f_hydration(p_key, p_value):
        if p_key == 'produceEvents':
            return HydratableParameter(value=p_value).hydrateAs(ArrayTypeOf(ProduceEventDef))

        if p_key == 'continueAs':
            return HydratableParameter(value=p_value).hydrateAs(UnionTypeOf([SimpleTypeOf(str),
                                                                             ComplexTypeOf(ContinueAsDef)]))

        return copy.deepcopy(p_value)
