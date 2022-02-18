from serverlessworkflow.sdk.hydration import Fields


class EventDataFilter:
    useData: bool = None
    data: str = None
    toStateData: str = None

    def __init__(self,
                 useData: bool = None,
                 data: str = None,
                 toStateData: str = None,
                 **kwargs):
        Fields(locals(), kwargs, Fields.default_hydration).set_to_object(self)
