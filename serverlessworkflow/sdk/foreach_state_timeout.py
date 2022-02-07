from serverlessworkflow.sdk.state_exec_timeout import StateExecTimeOut


class ForEachStateTimeOut:
    stateExecTimeOut: StateExecTimeOut = None
    actionExecTimeOut: str = None  # ActionExecTimeOut
