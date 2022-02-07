from serverlessworkflow.sdk.state_exec_timeout import StateExecTimeOut


class EventStateTimeOut:
    stateExecTimeOut: StateExecTimeOut = None
    actionExecTimeOut: str = None  # ActionExecTimeOut
    eventTimeOut: str = None  # EventTimeOut
