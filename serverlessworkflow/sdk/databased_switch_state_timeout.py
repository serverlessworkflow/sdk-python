import copy

from serverlessworkflow.sdk.hydration import ComplexTypeOf, HydratableParameter, Fields
from serverlessworkflow.sdk.state_exec_timeout import StateExecTimeOut


class DataBasedSwitchStateTime0ut:
    stateExecTimeOut: StateExecTimeOut = None

    def __init__(self,
                 stateExecTimeOut: StateExecTimeOut = None,
                 **kwargs):
        Fields(locals(), kwargs, DataBasedSwitchStateTime0ut.f_hydration).set_to_object(self)

    @staticmethod
    def f_hydration(p_key, p_value):
        if p_key == 'stateExecTimeOut':
            return HydratableParameter(value=p_value).hydrateAs(ComplexTypeOf(StateExecTimeOut))

        return copy.deepcopy(p_value)
