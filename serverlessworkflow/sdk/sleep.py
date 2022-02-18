from serverlessworkflow.sdk.hydration import Fields


class Sleep:
    before: str = None
    after: str = None

    def __init__(self,
                 before: str = None,
                 after: str = None,
                 **kwargs):
        Fields(locals(), kwargs, Fields.default_hydration).set_to_object(self)
