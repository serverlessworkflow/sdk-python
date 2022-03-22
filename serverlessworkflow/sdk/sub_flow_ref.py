from serverlessworkflow.sdk.swf_base import SwfBase


class SubFlowRef(SwfBase):
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
        SwfBase.__init__(self, locals(), kwargs, SwfBase.default_hydration)
