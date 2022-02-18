from serverlessworkflow.sdk.hydration import Fields


class StateExecTimeOut:
    single: str = None
    total: str = None

    def __init__(self,
                 single: str = None,
                 total: str = None,
                 **kwargs):
        Fields(locals(), kwargs, Fields.default_hydration).set_to_object(self)
