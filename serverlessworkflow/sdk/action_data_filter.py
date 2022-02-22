from serverlessworkflow.sdk.hydration import Fields


class ActionDataFilter:
    fromStateData: str = None
    useResults: bool = None
    results: str = None
    toStateData: str = None

    def __init__(self,
                 fromStateData: str = None,
                 useResults: bool = None,
                 results: str = None,
                 toStateData: str = None,
                 **kwargs):
        Fields(locals(), kwargs, Fields.default_hydration).set_to_object(self)
