from __future__ import annotations

from serverlessworkflow.sdk.swf_base import SwfBase


class RetryDef(SwfBase):
    name: str = None
    delay: str = None
    maxDelay: str = None
    increment: str = None
    multiplier: (int | str) = None
    maxAttempts: (int | str) = None
    jitter: (int | str) = None

    def __init__(self,
                 name: str = None,
                 delay: str = None,
                 maxDelay: str = None,
                 increment: str = None,
                 multiplier: (int | str) = None,
                 maxAttempts: (int | str) = None,
                 jitter: (int | str) = None,
                 **kwargs):
        SwfBase.__init__(self, locals(), kwargs, SwfBase.default_hydration)
