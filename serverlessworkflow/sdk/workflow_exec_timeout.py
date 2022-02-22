from serverlessworkflow.sdk.hydration import Fields


class WorkflowExecTimeOut:
    duration: str = None
    interrupt: bool = None
    runBefore: str = None

    def __init__(self,
                 duration: str = None,
                 interrupt: bool = None,
                 runBefore: str = None,
                 **kwargs):
        Fields(locals(), kwargs, Fields.default_hydration).set_to_object(self)
