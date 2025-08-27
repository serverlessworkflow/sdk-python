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

from transitions.extensions.nesting import NestedState
import warnings

NestedState.separator = "."


class StateMachineGenerator:
    def __init__(
        self,
        workflow: Workflow,
        state_machine: Union[CustomHierarchicalMachine, CustomGraphMachine],
        subflows: List[Workflow] = [],
        get_actions=False,
    ):
        self.workflow = workflow
        self.state_machine = state_machine
        self.get_actions = get_actions
        self.subflows = subflows

        self.is_first_state = False
        self.current_state: State = None

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
        for self.current_state in self.workflow.states:
            self.is_first_state = self.workflow.start == self.current_state.name
            self.definitions()
            self.transitions()

    def transitions(self):
        self.start_transition()
        self.data_conditions_transitions()
        self.event_conditions_transition()
        self.error_transitions()
        self.natural_transition(
            self.current_state.name,
            (
                self.current_state.transition
                if hasattr(self.current_state, "transition")
                else None
            ),
        )
        self.compensated_by_transition()
        self.end_transition()

    def start_transition(self):
        if self.is_first_state:
            self.state_machine._initial = self.current_state.name

    def data_conditions_transitions(self):
        if isinstance(self.current_state, DataBasedSwitchState):
            data_conditions = self.current_state.dataConditions
            if data_conditions:
                state_name = self.current_state.name
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
                self.default_condition_transition(self.current_state)

    def event_conditions_transition(self):
        if isinstance(self.current_state, EventBasedSwitchState):
            event_conditions = self.current_state.eventConditions
            if event_conditions:
                state_name = self.current_state.name
                for event_condition in event_conditions:
                    transition = event_condition.transition
                    event_ref = event_condition.eventRef
                    self.natural_transition(state_name, transition, event_ref)
                    if event_condition.end:
                        self.end_state(state_name, condition=event_ref)
                self.default_condition_transition(self.current_state)

    def default_condition_transition(self, state: State):
        if hasattr(state, "defaultCondition"):
            default_condition = state.defaultCondition
            if default_condition:
                self.natural_transition(
                    self.current_state.name, default_condition.transition, "default"
                )

    def end_transition(self):
        if hasattr(self.current_state, "end") and self.current_state.end:
            self.end_state(self.current_state.name)

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
        if hasattr(self.current_state, "onErrors") and (
            on_errors := self.current_state.onErrors
        ):
            for error in on_errors:
                self.natural_transition(
                    self.current_state.name,
                    error.transition,
                    error.errorRef,
                )

    def compensated_by_transition(self):
        compensated_by = self.current_state.compensatedBy
        if compensated_by:
            self.natural_transition(
                self.current_state.name, compensated_by, "compensated by"
            )

    def definitions(self):
        state_type = self.current_state.type
        if state_type == "sleep":
            self.sleep_state_details()
        elif state_type == "event":
            self.event_state_details()
        elif state_type == "operation":
            self.operation_state_details()
        elif state_type == "parallel":
            self.parallel_state_details()
        elif state_type == "switch":
            if self.current_state.dataConditions:
                self.data_based_switch_state_details()
            elif self.current_state.eventConditions:
                self.event_based_switch_state_details()
            else:
                raise Exception(
                    f"Unexpected switch type;\n state value= {self.current_state}"
                )
        elif state_type == "inject":
            self.inject_state_details()
        elif state_type == "foreach":
            self.foreach_state_details()
        elif state_type == "callback":
            self.callback_state_details()
        else:
            raise Exception(
                f"Unexpected type= {state_type};\n state value= {self.current_state}"
            )

    def parallel_state_details(self):
        if isinstance(self.current_state, ParallelState):
            self.state_to_machine_state(["parallel_state", "state"])

            state_name = self.current_state.name
            branches = self.current_state.branches
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
                            branch_state.metadata = {
                                "branch": self.current_state.serialize().__dict__
                            }
                            self.generate_actions_info(
                                machine_state=branch_state,
                                state_name=f"{state_name}.{branch_name}",
                                actions=branch.actions,
                            )

    def event_based_switch_state_details(self):
        if isinstance(self.current_state, EventBasedSwitchState):
            self.state_to_machine_state(
                ["event_based_switch_state", "switch_state", "state"]
            )

    def data_based_switch_state_details(self):
        if isinstance(self.current_state, DataBasedSwitchState):
            self.state_to_machine_state(
                ["data_based_switch_state", "switch_state", "state"]
            )

    def inject_state_details(self):
        if isinstance(self.current_state, InjectState):
            self.state_to_machine_state(["inject_state", "state"])

    def operation_state_details(self):
        if isinstance(self.current_state, OperationState):
            machine_state = self.state_to_machine_state(["operation_state", "state"])
            self.generate_actions_info(
                machine_state=machine_state,
                state_name=self.current_state.name,
                actions=self.current_state.actions,
                action_mode=self.current_state.actionMode,
            )

    def sleep_state_details(self):
        if isinstance(self.current_state, SleepState):
            self.state_to_machine_state(["sleep_state", "state"])

    def event_state_details(self):
        if isinstance(self.current_state, EventState):
            state = self.state_to_machine_state(["event_state", "state"])
            if self.get_actions:
                if on_events := self.current_state.onEvents:
                    state.initial = [] if len(on_events) > 1 else on_events[0]
                    for i, oe in enumerate(on_events):
                        state.add_substate(
                            oe_state := self.state_machine.state_cls(
                                oe_name := f"onEvent {i}"
                            )
                        )

                        # define initial state
                        if i == 0 and len(on_events) > 1:
                            state.initial = [oe_state.name]
                        elif i == 0 and len(on_events) == 1:
                            state.initial = oe_state.name
                        else:
                            state.initial.append(oe_state.name)

                        event_names = []
                        for ie, event in enumerate(oe.eventRefs):
                            oe_state.add_substate(
                                ns := self.state_machine.state_cls(event)
                            )
                            ns.tags = ["event"]
                            self.get_action_event(state=ns, e_name=event)
                            event_names.append(event)

                            # define initial state
                            if ie == 0 and len(oe.eventRefs) > 1:
                                oe_state.initial = [event]
                            elif ie == 0 and len(oe.eventRefs) == 1:
                                oe_state.initial = event
                            else:
                                oe_state.initial.append(event)

                            if self.current_state.exclusive and oe.actions:
                                oe_state.add_substate(
                                    ns := self.state_machine.state_cls(
                                        action_name := f"action {ie}"
                                    )
                                )
                                self.state_machine.add_transition(
                                    trigger="",
                                    source=f"{self.current_state.name}.{oe_name}.{event}",
                                    dest=f"{self.current_state.name}.{oe_name}.{action_name}",
                                )
                                self.generate_actions_info(
                                    machine_state=ns,
                                    state_name=f"{self.current_state.name}.{oe_name}.{action_name}",
                                    actions=oe.actions,
                                    action_mode=oe.actionMode,
                                )
                        if not self.current_state.exclusive and oe.actions:
                            self.generate_actions_info(
                                machine_state=oe_state,
                                state_name=f"{self.current_state.name}.{oe_name}",
                                actions=oe.actions,
                                action_mode=oe.actionMode,
                                initial_states=event_names,
                            )

    def foreach_state_details(self):
        if isinstance(self.current_state, ForEachState):
            self.state_to_machine_state(["foreach_state", "state"])
            self.state_machine.add_transition(
                trigger=f"{self.current_state.iterationParam} IN {self.current_state.inputCollection}",
                source=self.current_state.name,
                dest=self.current_state.name,
            )
            self.generate_actions_info(
                machine_state=self.state_machine.get_state(self.current_state.name),
                state_name=self.current_state.name,
                actions=self.current_state.actions,
                action_mode=self.current_state.mode,
            )

    def callback_state_details(self):
        if isinstance(self.current_state, CallbackState):
            self.state_to_machine_state(["callback_state", "state"])
            action = self.current_state.action
            if action and action.functionRef:
                self.generate_actions_info(
                    machine_state=self.state_machine.get_state(self.current_state.name),
                    state_name=self.current_state.name,
                    actions=[action],
                )

    def state_to_machine_state(self, tags: List[str]) -> NestedState:
        state_name = self.current_state.name
        if state_name not in self.state_machine.states.keys():
            self.state_machine.add_states(state_name)
        (ns := self.state_machine.get_state(state_name)).tags = tags
        ns.metadata = {"state": self.current_state.serialize().__dict__}
        return ns

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
                        StateMachineGenerator(
                            workflow=sf,
                            state_machine=new_machine,
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
        initial_states: List[str] = [],
    ):
        if self.get_actions:
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
                            self.get_action_function(state=ns, f_name=name)
                    elif action.subFlowRef:
                        name = new_subflows_names.get(i)
                    elif action.eventRef:
                        name = f"{action.eventRef.triggerEventRef}/{action.eventRef.resultEventRef}"
                        if name not in machine_state.states.keys():
                            machine_state.add_substate(
                                ns := self.state_machine.state_cls(name)
                            )
                            ns.tags = ["event"]
                            self.get_action_event(
                                state=ns,
                                e_name=action.eventRef.triggerEventRef,
                                er_name=action.eventRef.resultEventRef,
                            )
                    if name:
                        if action_mode == "sequential":
                            if i < len(actions) - 1:
                                # get next name
                                next_name = None
                                if actions[i + 1].functionRef:
                                    next_name = (
                                        self.get_function_name(
                                            actions[i + 1].functionRef
                                        )
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
                                            ns := self.state_machine.state_cls(
                                                next_name
                                            )
                                        )
                                        ns.tags = ["function"]
                                        self.get_action_function(
                                            state=ns, f_name=next_name
                                        )
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
                                            ns := self.state_machine.state_cls(
                                                next_name
                                            )
                                        )
                                        ns.tags = ["event"]
                                        self.get_action_event(
                                            state=ns,
                                            e_name=action.eventRef.triggerEventRef,
                                            er_name=action.eventRef.resultEventRef,
                                        )
                                self.state_machine.add_transition(
                                    trigger="",
                                    source=f"{state_name}.{name}",
                                    dest=f"{state_name}.{next_name}",
                                )
                            if i == 0 and not initial_states:
                                machine_state.initial = name
                            elif i == 0 and initial_states:
                                for init_s in initial_states:
                                    self.state_machine.add_transition(
                                        trigger="",
                                        source=f"{state_name}.{init_s}",
                                        dest=f"{state_name}.{name}",
                                    )
                        elif action_mode == "parallel":
                            parallel_states.append(name)
                    if action_mode == "parallel" and not initial_states:
                        machine_state.initial = parallel_states
                    elif action_mode == "parallel" and initial_states:
                        for init_s in initial_states:
                            for ps in parallel_states:
                                self.state_machine.add_transition(
                                    trigger="",
                                    source=f"{state_name}.{init_s}",
                                    dest=f"{state_name}.{ps}",
                                )

    def get_action_function(self, state: NestedState, f_name: str):
        if self.workflow.functions:
            for function in self.workflow.functions:
                current_function = function.serialize().__dict__
                if current_function["name"] == f_name:
                    state.metadata = {"function": current_function}
                    break

    def get_action_event(self, state: NestedState, e_name: str, er_name: str = ""):
        if self.workflow.events:
            for event in self.workflow.events:
                current_event = event.serialize().__dict__
                if current_event["name"] == e_name:
                    state.metadata = {"event": current_event}
                if current_event["name"] == er_name:
                    state.metadata = {"result_event": current_event}

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
            ns.metadata = substate.metadata
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
