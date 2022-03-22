import copy

from serverlessworkflow.sdk.state_exec_timeout import StateExecTimeOut
from serverlessworkflow.sdk.swf_base import HydratableParameter, ComplexTypeOf, SwfBase


class ParallelStateTimeOut(SwfBase):
    stateExecTimeOut: StateExecTimeOut = None
    branchExecTimeOut: str = None  # BranchExecTimeOut

    def __init__(self,
                 stateExecTimeOut: StateExecTimeOut = None,
                 branchExecTimeOut: str = None,
                 **kwargs):
        SwfBase.__init__(self, locals(), kwargs, ParallelStateTimeOut.f_hydration)

    @staticmethod
    def f_hydration(p_key, p_value):
        if p_key == 'stateExecTimeOut':
            return HydratableParameter(value=p_value).hydrateAs(ComplexTypeOf(StateExecTimeOut))

        return copy.deepcopy(p_value)
