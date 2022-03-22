from serverlessworkflow.sdk.swf_base import SwfBase


class EventDataFilter(SwfBase):
    useData: bool = None
    data: str = None
    toStateData: str = None

    def __init__(self,
                 useData: bool = None,
                 data: str = None,
                 toStateData: str = None,
                 **kwargs):
        SwfBase.__init__(self, locals(), kwargs, SwfBase.default_hydration)
