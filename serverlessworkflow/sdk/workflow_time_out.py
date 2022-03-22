import copy

from serverlessworkflow.sdk.state_exec_timeout import StateExecTimeOut
from serverlessworkflow.sdk.swf_base import HydratableParameter, ComplexTypeOf, SwfBase
from serverlessworkflow.sdk.workflow_exec_timeout import WorkflowExecTimeOut


class WorkflowTimeOut(SwfBase):
    workflowExecTimeOut: WorkflowExecTimeOut = None
    stateExecTimeOut: StateExecTimeOut = None
    actionExecTimeOut: str = None  # ActionExecTimeOut
    branchExecTimeOut: str = None  # BranchExecTimeOut
    eventTimeOut: str = None  # EventTimeOut

    def __init__(self,
                 workflowExecTimeOut: WorkflowExecTimeOut = None,
                 stateExecTimeOut: StateExecTimeOut = None,
                 actionExecTimeOut: str = None,  # ActionExecTimeOut
                 branchExecTimeOut: str = None,  # BranchExecTimeOut
                 eventTimeOut: str = None,  # EventTimeOut
                 **kwargs):

        SwfBase.__init__(self, locals(), kwargs, WorkflowTimeOut.f_hydration)

    @staticmethod
    def f_hydration(p_key, p_value):
        if p_key == 'workflowExecTimeOut':
            return HydratableParameter(value=p_value).hydrateAs(ComplexTypeOf(WorkflowExecTimeOut))

        if p_key == 'stateExecTimeOut':
            return HydratableParameter(value=p_value).hydrateAs(ComplexTypeOf(StateExecTimeOut))

        return copy.deepcopy(p_value)
