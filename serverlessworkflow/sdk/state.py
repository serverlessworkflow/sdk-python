from serverlessworkflow.sdk.swf_base import SwfBase


class State(SwfBase):
    type: str = None

    def __init__(self,
                 type: str = None,
                 **kwargs):
        SwfBase.__init__(self, locals(), kwargs, SwfBase.default_hydration)

    def is_event_state(self):
        return self.type == 'event'

    def is_operation_state(self):
        return self.type == 'operation'

    def is_switch_state(self):
        return self.type == 'switch'

    def is_sleep_state(self):
        return self.type == 'sleep'

    def is_parallel_state(self):
        return self.type == 'parallel'

    def is_inject_state(self):
        return self.type == 'inject'

    def is_foreach_state(self):
        return self.type == 'foreach'

    def is_callback_state(self):
        return self.type == 'callback'
