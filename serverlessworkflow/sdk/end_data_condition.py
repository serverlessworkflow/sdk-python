from __future__ import annotations

import copy

from serverlessworkflow.sdk.end import End
from serverlessworkflow.sdk.metadata import Metadata
from serverlessworkflow.sdk.swf_base import SimpleTypeOf, ComplexTypeOf, UnionTypeOf, HydratableParameter, SwfBase


class EndDataCondition(SwfBase):
    name: str = None
    condition: str = None
    end: (bool | End) = None
    metadata: Metadata = None

    def __init__(self,
                 name: str = None,
                 condition: str = None,
                 end: (bool | End) = None,
                 metadata: Metadata = None,
                 **kwargs):
        SwfBase.__init__(self, locals(), kwargs, EndDataCondition.f_hydration)

    @staticmethod
    def f_hydration(p_key, p_value):
        if p_key == 'end':
            return HydratableParameter(value=p_value).hydrateAs(UnionTypeOf([SimpleTypeOf(bool),
                                                                             ComplexTypeOf(End)]))
        return copy.deepcopy(p_value)
