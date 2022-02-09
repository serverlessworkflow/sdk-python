from serverlessworkflow.sdk.state_exec_timeout import StateExecTimeOut
from serverlessworkflow.sdk.workflow_exec_timeout import WorkflowExecTimeOut


class WorkflowTimeOut:
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

        # duplicated
        for local in list(locals()):
            if local in ["self", "kwargs"]:
                continue
            value = locals().get(local)
            if not value:
                continue
            if value == "true":
                value = True
            # duplicated

            self.__setattr__(local.replace("_", ""), value)

        # duplicated
        for k in kwargs.keys():
            value = kwargs[k]
            if value == "true":
                value = True

            self.__setattr__(k.replace("_", ""), value)
            # duplicated
