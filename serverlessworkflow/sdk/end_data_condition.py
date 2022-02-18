from __future__ import annotations

import copy

from serverlessworkflow.sdk.end import End
from serverlessworkflow.sdk.hydration import SimpleTypeOf, ComplexTypeOf, UnionTypeOf, HydratableParameter, \
    Fields
from serverlessworkflow.sdk.metadata import Metadata


class EndDataCondition:
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
        Fields(locals(), kwargs, EndDataCondition.f_hydration).set_to_object(self)

    @staticmethod
    def f_hydration(p_key, p_value):
        if p_key == 'end':
            return HydratableParameter(value=p_value).hydrateAs(UnionTypeOf([SimpleTypeOf(bool),
                                                                             ComplexTypeOf(End)]))
        return copy.deepcopy(p_value)
