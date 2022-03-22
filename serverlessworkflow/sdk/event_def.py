from __future__ import annotations

import copy
from enum import Enum

from serverlessworkflow.sdk.correlation_def import CorrelationDef
from serverlessworkflow.sdk.metadata import Metadata
from serverlessworkflow.sdk.swf_base import HydratableParameter, UnionTypeOf, ArrayTypeOf, ComplexTypeOf, SwfBase


class Kind(Enum):
    CONSUMED = "consumed"
    PRODUCED = "produced"


class EventDef(SwfBase):
    name: str = None
    source: str = None
    type: str = None
    kind: Kind = None
    correlation: (CorrelationDef | [CorrelationDef]) = None
    dataOnly: bool = None
    metadata: Metadata = None

    def __init__(self,
                 name: str = None,
                 source: str = None,
                 type: str = None,
                 kind: Kind = None,
                 correlation: (CorrelationDef | [CorrelationDef]) = None,  # CorrelationDefs
                 dataOnly: bool = None,
                 metadata: Metadata = None,
                 **kwargs):
        _default_values = {'kind': 'consumed', 'dataOnly': True, }
        SwfBase.__init__(self, locals(), kwargs, EventDef.f_hydration,
                         _default_values)

    @staticmethod
    def f_hydration(p_key, p_value):
        if p_key == 'correlation':
            return HydratableParameter(value=p_value).hydrateAs(UnionTypeOf([ComplexTypeOf(CorrelationDef),
                                                                             ArrayTypeOf(CorrelationDef)]))
        return copy.deepcopy(p_value)
