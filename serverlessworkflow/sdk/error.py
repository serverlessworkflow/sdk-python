from __future__ import annotations

import copy

from serverlessworkflow.sdk.end import End
from serverlessworkflow.sdk.hydration import HydratableParameter, ArrayTypeOf, SimpleTypeOf, ComplexTypeOf, \
    UnionTypeOf, Fields
from serverlessworkflow.sdk.transition import Transition


class Error:
    errorRef: str = None
    errorRefs: [str] = None
    transition: (str | Transition) = None
    end: (bool | End) = None

    def __init__(self,
                 errorRef: str = None,
                 errorRefs: [str] = None,
                 transition: (str | Transition) = None,
                 end: (bool | End) = None,
                 **kwargs):

        Fields(locals(), kwargs, Error.f_hydration).set_to_object(self)

    @staticmethod
    def f_hydration(p_key, p_value):

        if p_key == 'errorRefs':
            return HydratableParameter(value=p_value).hydrateAs(ArrayTypeOf(ComplexTypeOf(Error)))

        if p_key == 'transition':
            return HydratableParameter(value=p_value).hydrateAs(UnionTypeOf([SimpleTypeOf(str),
                                                                             ComplexTypeOf(Transition)]))

        if p_key == 'end':
            return HydratableParameter(value=p_value).hydrateAs(UnionTypeOf([SimpleTypeOf(bool),
                                                                             ComplexTypeOf(End)]))

        return copy.deepcopy(p_value)
