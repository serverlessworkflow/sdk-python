from serverlessworkflow.sdk.hydration import Fields


class CronDef:
    expression: str = None
    validUntil: str = None

    def __init__(self,
                 expression: str = None,
                 validUntil: str = None,
                 **kwargs):
        Fields(locals(), kwargs, Fields.default_hydration).set_to_object(self)
