from typing import Any, Dict, List, Optional, Union
from serverlessworkflow.sdk.action import Action
from serverlessworkflow.sdk.function_ref import FunctionRef
from serverlessworkflow.sdk.state_machine_extensions import (
    CustomGraphMachine,
    CustomHierarchicalGraphMachine,
    CustomHierarchicalMachine,
)
from serverlessworkflow.sdk.transition import Transition
from serverlessworkflow.sdk.workflow import (
    State,
    EventState,
    SleepState,
    CallbackState,
    DataBasedSwitchState,
    InjectState,
    EventBasedSwitchState,
    ParallelState,
    OperationState,
    ForEachState,
    Workflow,
)
from serverlessworkflow.sdk.transition_data_condition import TransitionDataCondition
from serverlessworkflow.sdk.end_data_condition import EndDataCondition

from transitions.extensions import HierarchicalMachine, GraphMachine
from transitions.extensions.nesting import NestedState
import warnings

NestedState.separator = "."


class StateMachineGenerator:
    def __init__(
        self,
        state: State,
        state_machine: Union[CustomHierarchicalMachine, CustomGraphMachine],
        subflows: List[Workflow] = [],
        is_first_state=False,
        get_actions=False,
    ):
        self.state = state
        self.is_first_state = is_first_state
        self.state_machine = state_machine
        self.get_actions = get_actions
        self.subflows = subflows

        if (
            self.get_actions
            and not isinstance(self.state_machine, CustomHierarchicalMachine)
            and not isinstance(self.state_machine, CustomHierarchicalGraphMachine)
        ):
            raise AttributeError(
                "The provided state machine must be of the CustomHierarchicalMachine or CustomHierarchicalGraphMachine types."
            )
        if not self.get_actions and (
            isinstance(self.state_machine, CustomHierarchicalMachine)
            or isinstance(self.state_machine, CustomHierarchicalGraphMachine)
        ):
            raise AttributeError(
                "The provided state machine can not be of the CustomHierarchicalMachine or CustomHierarchicalGraphMachine types."
            )

    def generate(self):
        self.definitions()
        self.transitions()

    def transitions(self):
        self.start_transition()
        self.data_conditions_transitions()
        self.event_conditions_transition()
        self.error_transitions()
        self.natural_transition(
            self.state.name,
            self.state.transition if hasattr(self.state, "transition") else None,
        )
        self.compensated_by_transition()
        self.end_transition()

    def start_transition(self):
        if self.is_first_state:
            self.state_machine._initial = self.state.name

    def data_conditions_transitions(self):
        if isinstance(self.state, DataBasedSwitchState):
            data_conditions = self.state.dataConditions
            if data_conditions:
                state_name = self.state.name
                for data_condition in data_conditions:
                    if isinstance(data_condition, TransitionDataCondition):
                        transition = data_condition.transition
                        condition = data_condition.condition
                        self.natural_transition(state_name, transition, condition)
                    if (
                        isinstance(data_condition, EndDataCondition)
                        and data_condition.end
                    ):
                        condition = data_condition.condition
                        self.end_state(state_name, condition=condition)
                self.default_condition_transition(self.state)

    def event_conditions_transition(self):
        if isinstance(self.state, EventBasedSwitchState):
            event_conditions = self.state.eventConditions
            if event_conditions:
                state_name = self.state.name
                for event_condition in event_conditions:
                    transition = event_condition.transition
                    event_ref = event_condition.eventRef
                    self.natural_transition(state_name, transition, event_ref)
                    if event_condition.end:
                        self.end_state(state_name, condition=event_ref)
                self.default_condition_transition(self.state)

    def default_condition_transition(self, state: State):
        if hasattr(state, "defaultCondition"):
            default_condition = state.defaultCondition
            if default_condition:
                self.natural_transition(
                    self.state.name, default_condition.transition, "default"
                )

    def end_transition(self):
        if hasattr(self.state, "end") and self.state.end:
            self.end_state(self.state.name)

    def natural_transition(
        self,
        source: str,
        target: Union[str, Transition],
        label: Optional[str] = None,
    ):
        if target:
            if isinstance(target, Transition):
                desc_transition = target.nextState
            else:
                desc_transition = target
            if source not in self.state_machine.states.keys():
                self.state_machine.add_states(source)
            if desc_transition not in self.state_machine.states.keys():
                self.state_machine.add_states(desc_transition)
            self.state_machine.add_transition(
                trigger=label if label else "", source=source, dest=desc_transition
            )

    def error_transitions(self):
        if hasattr(self.state, "onErrors") and (on_errors := self.state.onErrors):
            for error in on_errors:
                self.natural_transition(
                    self.state.name,
                    error.transition,
                    error.errorRef,
                )

    def compensated_by_transition(self):
        compensated_by = self.state.compensatedBy
        if compensated_by:
            self.natural_transition(self.state.name, compensated_by, "compensated by")

    def definitions(self):
        state_type = self.state.type
        if state_type == "sleep":
            self.sleep_state_details()
        elif state_type == "event":
            self.event_state_details()
        elif state_type == "operation":
            self.operation_state_details()
        elif state_type == "parallel":
            self.parallel_state_details()
        elif state_type == "switch":
            if self.state.dataConditions:
                self.data_based_switch_state_details()
            elif self.state.eventConditions:
                self.event_based_switch_state_details()
            else:
                raise Exception(f"Unexpected switch type;\n state value= {self.state}")
        elif state_type == "inject":
            self.inject_state_details()
        elif state_type == "foreach":
            self.foreach_state_details()
        elif state_type == "callback":
            self.callback_state_details()
        else:
            raise Exception(
                f"Unexpected type= {state_type};\n state value= {self.state}"
            )

    def parallel_state_details(self):
        if isinstance(self.state, ParallelState):
            state_name = self.state.name
            if state_name not in self.state_machine.states.keys():
                self.state_machine.add_states(state_name)
            self.state_machine.get_state(state_name).tags = ["parallel_state"]

            state_name = self.state.name
            branches = self.state.branches
            if branches:
                if self.get_actions:
                    self.state_machine.get_state(state_name).initial = []
                    for branch in branches:
                        if hasattr(branch, "actions") and branch.actions:
                            branch_name = branch.name
                            self.state_machine.get_state(state_name).add_substates(
                                branch_state := self.state_machine.state_cls(
                                    branch_name
                                )
                            )
                            self.state_machine.get_state(state_name).initial.append(
                                branch_name
                            )
                            branch_state.tags = ["branch"]
                            self.generate_actions_info(
                                machine_state=branch_state,
                                state_name=f"{state_name}.{branch_name}",
                                actions=branch.actions,
                            )

    def event_based_switch_state_details(self):
        if isinstance(self.state, EventBasedSwitchState):
            state_name = self.state.name
            if state_name not in self.state_machine.states.keys():
                self.state_machine.add_states(state_name)
            self.state_machine.get_state(state_name).tags = [
                "event_based_switch_state",
                "switch_state",
            ]

    def data_based_switch_state_details(self):
        if isinstance(self.state, DataBasedSwitchState):
            state_name = self.state.name
            if state_name not in self.state_machine.states.keys():
                self.state_machine.add_states(state_name)
            self.state_machine.get_state(state_name).tags = [
                "data_based_switch_state",
                "switch_state",
            ]

    def inject_state_details(self):
        if isinstance(self.state, InjectState):
            state_name = self.state.name
            if state_name not in self.state_machine.states.keys():
                self.state_machine.add_states(state_name)
            self.state_machine.get_state(state_name).tags = ["inject_state"]

    def operation_state_details(self):
        if isinstance(self.state, OperationState):
            state_name = self.state.name
            if state_name not in self.state_machine.states.keys():
                self.state_machine.add_states(state_name)
            (machine_state := self.state_machine.get_state(state_name)).tags = [
                "operation_state"
            ]
            self.generate_actions_info(
                machine_state=machine_state,
                state_name=self.state.name,
                actions=self.state.actions,
                action_mode=self.state.actionMode,
            )

    def sleep_state_details(self):
        if isinstance(self.state, SleepState):
            state_name = self.state.name
            if state_name not in self.state_machine.states.keys():
                self.state_machine.add_states(state_name)
            self.state_machine.get_state(state_name).tags = ["sleep_state"]

    def event_state_details(self):
        if isinstance(self.state, EventState):
            state_name = self.state.name
            if state_name not in self.state_machine.states.keys():
                self.state_machine.add_states(state_name)
            self.state_machine.get_state(state_name).tags = ["event_state"]

    def foreach_state_details(self):
        if isinstance(self.state, ForEachState):
            state_name = self.state.name
            if state_name not in self.state_machine.states.keys():
                self.state_machine.add_states(state_name)
            self.state_machine.get_state(state_name).tags = ["foreach_state"]
            self.generate_actions_info(
                machine_state=self.state_machine.get_state(self.state.name),
                state_name=self.state.name,
                actions=self.state.actions,
                action_mode=self.state.mode,
            )

    def callback_state_details(self):
        if isinstance(self.state, CallbackState):
            state_name = self.state.name
            if state_name not in self.state_machine.states.keys():
                self.state_machine.add_states(state_name)
            self.state_machine.get_state(state_name).tags = ["callback_state"]
            action = self.state.action
            if action and action.functionRef:
                self.generate_actions_info(
                    machine_state=self.state_machine.get_state(self.state.name),
                    state_name=self.state.name,
                    actions=[action],
                )

    def get_subflow_state(
        self, machine_state: NestedState, state_name: str, actions: List[Action]
    ):
        added_states = {}
        for i, action in enumerate(actions):
            if action.subFlowRef:
                if isinstance(action.subFlowRef, str):
                    workflow_id = action.subFlowRef
                    workflow_version = None
                else:
                    workflow_id = action.subFlowRef.workflowId
                    workflow_version = action.subFlowRef.version
                none_found = True
                for sf in self.subflows:
                    if sf.id == workflow_id and (
                        (workflow_version and sf.version == workflow_version)
                        or not workflow_version
                    ):
                        none_found = False
                        new_machine = CustomHierarchicalMachine(
                            model=None, initial=None, auto_transitions=False
                        )

                        # Generate the state machine for the subflow
                        for state in sf.states:
                            StateMachineGenerator(
                                state=state,
                                state_machine=new_machine,
                                is_first_state=sf.start == state.name,
                                get_actions=self.get_actions,
                                subflows=self.subflows,
                            ).generate()

                        # Convert the new_machine into a NestedState
                        added_states[i] = self.subflow_state_name(
                            action=action, subflow=sf
                        )
                        nested_state = self.state_machine.state_cls(added_states[i])
                        nested_state.tags = ["subflow"]
                        machine_state.add_substate(nested_state)
                        self.state_machine_to_nested_state(
                            state_name=state_name,
                            state_machine=new_machine,
                            nested_state=nested_state,
                        )

                if none_found:
                    warnings.warn(
                        f"Specified subflow [{workflow_id} {workflow_version if workflow_version else ''}] not found.",
                        category=UserWarning,
                    )
        return added_states

    def generate_actions_info(
        self,
        machine_state: NestedState,
        state_name: str,
        actions: List[Dict[str, Action]],
        action_mode: str = "sequential",
    ):
        parallel_states = []
        if actions:
            new_subflows_names = self.get_subflow_state(
                machine_state=machine_state, state_name=state_name, actions=actions
            )
            for i, action in enumerate(actions):
                name = None
                if action.functionRef:
                    name = (
                        self.get_function_name(action.functionRef)
                        if isinstance(action.functionRef, str)
                        else (
                            action.functionRef.refName
                            if isinstance(action.functionRef, FunctionRef)
                            else None
                        )
                    )
                    if name not in machine_state.states.keys():
                        machine_state.add_substate(
                            ns := self.state_machine.state_cls(name)
                        )
                        ns.tags = ["function"]
                elif action.subFlowRef:
                    name = new_subflows_names.get(i)
                elif action.eventRef:
                    name = f"{action.eventRef.triggerEventRef}/{action.eventRef.resultEventRef}"
                    if name not in machine_state.states.keys():
                        machine_state.add_substate(
                            ns := self.state_machine.state_cls(name)
                        )
                        ns.tags = ["event"]
                if name:
                    if action_mode == "sequential":
                        if i < len(actions) - 1:
                            # get next name
                            next_name = None
                            if actions[i + 1].functionRef:
                                next_name = (
                                    self.get_function_name(actions[i + 1].functionRef)
                                    if isinstance(actions[i + 1].functionRef, str)
                                    else (
                                        actions[i + 1].functionRef.refName
                                        if isinstance(
                                            actions[i + 1].functionRef, FunctionRef
                                        )
                                        else None
                                    )
                                )
                                if (
                                    next_name
                                    not in self.state_machine.get_state(
                                        state_name
                                    ).states.keys()
                                ):
                                    machine_state.add_substate(
                                        ns := self.state_machine.state_cls(next_name)
                                    )
                                    ns.tags = ["function"]
                            elif actions[i + 1].subFlowRef:
                                next_name = new_subflows_names.get(i + 1)
                            elif actions[i + 1].eventRef:
                                next_name = f"{action.eventRef.triggerEventRef}/{action.eventRef.resultEventRef}"
                                if (
                                    next_name
                                    not in self.state_machine.get_state(
                                        state_name
                                    ).states.keys()
                                ):
                                    machine_state.add_substate(
                                        ns := self.state_machine.state_cls(name)
                                    )
                                    ns.tags = ["event"]
                            self.state_machine.add_transition(
                                trigger="",
                                source=f"{state_name}.{name}",
                                dest=f"{state_name}.{next_name}",
                            )
                        if i == 0:
                            machine_state.initial = name
                    elif action_mode == "parallel":
                        parallel_states.append(name)
                if action_mode == "parallel":
                    machine_state.initial = parallel_states

    def subflow_state_name(self, action: Action, subflow: Workflow):
        return (
            action.name
            if action.name
            else f"{subflow.id}/{subflow.version.replace(NestedState.separator, '-')}"
        )

    def add_all_sub_states(
        self,
        original_state: Union[NestedState, CustomHierarchicalMachine],
        new_state: NestedState,
    ):
        if len(original_state.states) == 0:
            return
        for substate in original_state.states.values():
            new_state.add_substate(ns := self.state_machine.state_cls(substate.name))
            ns.tags = substate.tags
            self.add_all_sub_states(substate, ns)
        new_state.initial = original_state.initial

    def state_machine_to_nested_state(
        self,
        state_name: str,
        state_machine: CustomHierarchicalMachine,
        nested_state: NestedState,
    ) -> NestedState:
        self.add_all_sub_states(state_machine, nested_state)

        for trigger, event in state_machine.events.items():
            for transition_l in event.transitions.values():
                for transition in transition_l:
                    source = transition.source
                    dest = transition.dest
                    self.state_machine.add_transition(
                        trigger=trigger,
                        source=f"{state_name}.{nested_state.name}.{source}",
                        dest=f"{state_name}.{nested_state.name}.{dest}",
                    )

    def get_function_name(
        self, fn_ref: Union[Dict[str, Any], str, None]
    ) -> Optional[str]:
        if isinstance(fn_ref, dict) and "refName" in fn_ref:
            return fn_ref["refName"]
        elif isinstance(fn_ref, str):
            return fn_ref
        return None

    def end_state(self, name, condition=None):
        if name not in self.state_machine.states.keys():
            self.state_machine.add_states(name)

        if not condition:
            self.state_machine.get_state(name).final = True
        else:
            if "[*]" not in self.state_machine.states.keys():
                self.state_machine.add_states("[*]")
                self.state_machine.get_state("[*]").final = True
            self.state_machine.add_transition(
                trigger=condition if condition else "", source=name, dest="[*]"
            )
