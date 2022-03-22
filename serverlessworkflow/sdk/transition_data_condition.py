from __future__ import annotations

import copy

from serverlessworkflow.sdk.metadata import Metadata
from serverlessworkflow.sdk.swf_base import HydratableParameter, UnionTypeOf, SimpleTypeOf, ComplexTypeOf, SwfBase
from serverlessworkflow.sdk.transition import Transition


class TransitionDataCondition(SwfBase):
    name: str = None
    condition: str = None
    transition: (str | Transition) = None
    metadata: Metadata = None

    def __init__(self,
                 name: str = None,
                 condition: str = None,
                 transition: (str | Transition) = None,
                 metadata: Metadata = None,
                 **kwargs):
        SwfBase.__init__(self, locals(), kwargs, TransitionDataCondition.f_hydration)

    @staticmethod
    def f_hydration(p_key, p_value):
        if p_key == 'transition':
            return HydratableParameter(value=p_value).hydrateAs(UnionTypeOf([SimpleTypeOf(str),
                                                                             ComplexTypeOf(Transition)]))

        return copy.deepcopy(p_value)
