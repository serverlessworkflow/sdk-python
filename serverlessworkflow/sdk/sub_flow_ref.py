from serverlessworkflow.sdk.hydration import Fields


class SubFlowRef:
    workflowId: str = None
    version: str = None
    onParentComplete: str = None
    invoke: str = None

    def __init__(self,
                 workflowId: str = None,
                 version: str = None,
                 onParentComplete: str = None,
                 invoke: str = None,
                 **kwargs):
        Fields(locals(), kwargs, Fields.default_hydration).set_to_object(self)
