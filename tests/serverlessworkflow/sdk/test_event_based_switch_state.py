import unittest

from serverlessworkflow.sdk.event_based_switch_state import EventBasedSwitchState
from serverlessworkflow.sdk.transition_event_condition import TransitionEventCondition


class TestEventBasedSwitchState(unittest.TestCase):
    def test_programmatically_create_object(self):
        event_based_switch_state = EventBasedSwitchState(eventConditions=[TransitionEventCondition(
            name="Hold Book",
            eventRef="Hold Book Event",
            transition="Request Hold"

        )])

        self.assertTrue(isinstance(event_based_switch_state.eventConditions[0], TransitionEventCondition))
