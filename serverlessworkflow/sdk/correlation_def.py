from serverlessworkflow.sdk.hydration import Fields


class CorrelationDef:
    contextAttributeName: str = None
    contextAttributeValue: str = None

    def __init__(self,
                 contextAttributeName: str = None,
                 contextAttributeValue: str = None,
                 **kwargs):
        Fields(locals(), kwargs, Fields.default_hydration).set_to_object(self)
