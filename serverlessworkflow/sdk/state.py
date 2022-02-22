from serverlessworkflow.sdk.hydration import Fields


class State:
    type: str = None

    def __init__(self,
                 type: str = None,
                 **kwargs):
        Fields(locals(), kwargs, Fields.default_hydration).set_to_object(self)

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
