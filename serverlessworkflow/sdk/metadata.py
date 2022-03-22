from typing import Dict

from serverlessworkflow.sdk.swf_base import SwfBase


class Metadata(Dict[str, str], SwfBase):

    def __init__(self,
                 **kwargs):
        SwfBase.__init__(self, locals(), kwargs, SwfBase.default_hydration)
