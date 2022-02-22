import copy

from serverlessworkflow.sdk.hydration import HydratableParameter, ComplexTypeOf, Fields
from serverlessworkflow.sdk.state_exec_timeout import StateExecTimeOut


class EventStateTimeOut:
    stateExecTimeOut: StateExecTimeOut = None
    actionExecTimeOut: str = None  # ActionExecTimeOut
    eventTimeOut: str = None  # EventTimeOut

    def __init__(self,
                 stateExecTimeOut: StateExecTimeOut = None,
                 actionExecTimeOut: str = None,
                 eventTimeOut: str = None,
                 **kwargs):
        Fields(locals(), kwargs, EventStateTimeOut.f_hydration).set_to_object(self)

    @staticmethod
    def f_hydration(p_key, p_value):
        if p_key == 'stateExecTimeOut':
            return HydratableParameter(value=p_value).hydrateAs(ComplexTypeOf(StateExecTimeOut))

        return copy.deepcopy(p_value)
