import copy

from serverlessworkflow.sdk.swf_base import ComplexTypeOf, HydratableParameter, SwfBase


class FunctionRef(SwfBase):
    refName: str = None
    arguments: dict[str, dict] = None
    selectionSet: str = None
    invoke: str = None

    def __init__(self,
                 refName: str = None,
                 arguments: dict[str, any] = None,
                 selectionSet: str = None,
                 invoke: str = None,
                 **kwargs):
        SwfBase.__init__(self, locals(), kwargs, FunctionRef.f_hydration)

    @staticmethod
    def f_hydration(p_key, p_value):
        if p_key == 'arguments':
            return HydratableParameter(value=p_value).hydrateAs(ComplexTypeOf(dict))

        return copy.deepcopy(p_value)
