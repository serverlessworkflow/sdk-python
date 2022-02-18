from __future__ import annotations

import copy

from serverlessworkflow.sdk.end import End
from serverlessworkflow.sdk.hydration import UnionTypeOf, SimpleTypeOf, ComplexTypeOf, HydratableParameter, \
    Fields
from serverlessworkflow.sdk.transition import Transition


class DefaultConditionDef:
    transition: (str | Transition) = None
    end: (bool | End) = None

    def __init__(self,
                 transition: (str | Transition) = None,
                 end: (bool | End) = None,
                 **kwargs):
        Fields(locals(), kwargs, DefaultConditionDef.f_hydration).set_to_object(self)

    @staticmethod
    def f_hydration(p_key, p_value):

        if p_key == 'transition':
            return HydratableParameter(value=p_value).hydrateAs(UnionTypeOf([SimpleTypeOf(str),
                                                                             ComplexTypeOf(Transition)]))

        if p_key == 'end':
            return HydratableParameter(value=p_value).hydrateAs(UnionTypeOf([SimpleTypeOf(bool),
                                                                             ComplexTypeOf(End)]))

        return copy.deepcopy(p_value)
