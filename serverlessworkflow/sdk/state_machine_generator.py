from typing import Any, Dict, List, Optional, Union
from serverlessworkflow.sdk.callback_state import CallbackState
from serverlessworkflow.sdk.function_ref import FunctionRef
from serverlessworkflow.sdk.sleep_state import SleepState
from serverlessworkflow.sdk.transition import Transition
from serverlessworkflow.sdk.workflow import (
    State,
    DataBasedSwitchState,
    EventBasedSwitchState,
    ParallelState,
    OperationState,
    ForEachState,
)
from serverlessworkflow.sdk.transition_data_condition import TransitionDataCondition
from serverlessworkflow.sdk.end_data_condition import EndDataCondition

from transitions.extensions import HierarchicalMachine, GraphMachine
from transitions.extensions.nesting import NestedState

NestedState.separator = "."


class StateMachineGenerator:
    def __init__(
        self,
        state: State,
        state_machine: Union[HierarchicalMachine, GraphMachine],
        is_first_state=False,
        get_actions=False,
    ):
        self.state = state
        self.is_first_state = is_first_state
        self.state_machine = state_machine
        self.get_actions = get_actions

        if self.get_actions and not isinstance(self.state_machine, HierarchicalMachine):
            raise AttributeError(
                "The provided state machine must be of the HierarchicalMachine type."
            )
        if not self.get_actions and isinstance(self.state_machine, HierarchicalMachine):
            raise AttributeError(
                "The provided state machine can not be of the HierarchicalMachine type."
            )

    def source_code(self) -> str:
        state_definition = self.definitions()
        state_transitions = self.transitions()

        state_description = state_definition
        for tr in state_transitions:
            state_description += "\n" + tr

        return state_description

    def definitions(self) -> str:
        details = self.definition_details()
        return (
            self.definition_name()
            + "\n"
            + self.definition_type()
            + ("\n" + details if details is not None else "")
        )

    def transitions(self) -> List[str]:
        transitions = []
        transitions += self.start_transition()
        transitions += self.data_conditions_transitions()
        transitions += self.event_conditions_transition()
        transitions += self.error_transitions()
        transitions += self.natural_transition(
            self.state_key_diagram(self.state.name),
            self.state.transition if hasattr(self.state, "transition") else None,
        )
        transitions += self.compensated_by_transition()
        transitions += self.end_transition()
        return transitions

    def state_key_diagram(self, name: str) -> Optional[str]:
        return name.replace(" ", "_") if name else None

    def start_transition(self) -> List[str]:
        transitions = []
        if self.is_first_state:
            state_name = self.state_key_diagram(self.state.name)
            transitions.append(self.transition_description("[*]", state_name))

            if state_name not in self.state_machine.states.keys():
                self.state_machine.add_states(state_name)
                self.state_machine._initial = state_name
            else:
                self.state_machine._initial = state_name

        return transitions

    def data_conditions_transitions(self) -> List[str]:
        transitions = []
        if isinstance(self.state, DataBasedSwitchState):
            data_conditions = self.state.dataConditions
            if data_conditions:
                state_name = self.state.name
                for data_condition in data_conditions:
                    if isinstance(data_condition, TransitionDataCondition):
                        transition = data_condition.transition
                        condition = data_condition.condition
                        transitions += self.natural_transition(
                            state_name, transition, condition
                        )
                    if (
                        isinstance(data_condition, EndDataCondition)
                        and data_condition.end
                    ):
                        transitions.append(
                            self.transition_description(state_name, "[*]", condition)
                        )
                        self.end_state(state_name, condition=condition)
                transitions += self.default_condition_transition(self.state)
        return transitions

    def event_conditions_transition(self) -> List[str]:
        transitions = []
        if isinstance(self.state, EventBasedSwitchState):
            event_conditions = self.state.eventConditions
            if event_conditions:
                state_name = self.state.name
                for event_condition in event_conditions:
                    transition = event_condition.transition
                    event_ref = event_condition.eventRef
                    transitions += self.natural_transition(
                        state_name, transition, event_ref
                    )
                    if event_condition.end:
                        transitions.append(
                            self.transition_description(state_name, "[*]", event_ref)
                        )
                        self.end_state(state_name, condition=event_ref)
                transitions += self.default_condition_transition(self.state)
        return transitions

    def default_condition_transition(self, state: Dict[str, Any]) -> List[str]:
        transitions = []
        if hasattr(state, "defaultCondition"):
            default_condition = state.defaultCondition
            if default_condition:
                transitions += self.natural_transition(
                    self.state.name, default_condition.transition, "default"
                )
        return transitions

    def end_transition(self) -> List[str]:
        transitions = []
        if hasattr(self.state, "end") and self.state.end:
            state_name = self.state.name
            transition_label = None
            end = self.state.end
            if hasattr(end, "produceEvents") and end.produceEvents:
                events = ",".join(pe.eventRef for pe in end.produceEvents)
                transition_label = f"Produced event = [{events}]"
            transitions.append(
                self.transition_description(state_name, "[*]", transition_label)
            )
            self.end_state(state_name)
        return transitions

    def natural_transition(
        self,
        source: str,
        target: Union[str, Transition],
        label: Optional[str] = None,
    ) -> List[str]:
        transitions = []
        if target:
            if isinstance(target, Transition):
                desc_transition = target.nextState
            else:
                desc_transition = target
            transitions.append(
                self.transition_description(source, desc_transition, label)
            )
            if source not in self.state_machine.states.keys():
                self.state_machine.add_states(source)
            if desc_transition not in self.state_machine.states.keys():
                self.state_machine.add_states(desc_transition)
            self.state_machine.add_transition(
                trigger=label if label else "", source=source, dest=desc_transition
            )

        return transitions

    def error_transitions(self) -> List[str]:
        transitions = []
        if hasattr(self.state, "onErrors") and (on_errors := self.state.onErrors):
            for error in on_errors:
                transitions += self.natural_transition(
                    self.state_key_diagram(self.state.name),
                    error.transition,
                    error.errorRef,
                )
        return transitions

    def compensated_by_transition(self) -> List[str]:
        transitions = []
        compensated_by = self.state.compensatedBy
        if compensated_by:
            transitions += self.natural_transition(
                self.state.name, compensated_by, "compensated by"
            )
        return transitions

    def definition_details(self) -> Optional[str]:
        definition = None
        state_type = self.state.type
        if state_type == "sleep":
            definition = self.sleep_state_details()
        elif state_type == "event":
            pass
        elif state_type == "operation":
            definition = self.operation_state_details()
        elif state_type == "parallel":
            definition = self.parallel_state_details()
        elif state_type == "switch":
            if self.state.dataConditions:
                definition = self.data_based_switch_state_details()
            elif self.state.eventConditions:
                definition = self.event_based_switch_state_details()
            else:
                raise Exception(f"Unexpected switch type;\n state value= {self.state}")
        elif state_type == "inject":
            pass
        elif state_type == "foreach":
            definition = self.foreach_state_details()
        elif state_type == "callback":
            definition = self.callback_state_details()
        else:
            raise Exception(
                f"Unexpected type= {state_type};\n state value= {self.state}"
            )

        if (
            hasattr(self.state, "usedForCompensation")
            and self.state.usedForCompensation
        ):
            definition = self.state_description(
                self.state_key_diagram(self.state.name), "usedForCompensation\n"
            ) + (definition or "")
        return definition

    def definition_type(self) -> str:
        state_type = self.state.type
        state_type_cap = state_type.capitalize() if state_type else ""
        return self.state_description(
            self.state_key_diagram(self.state.name), "type", f"{state_type_cap} State"
        )

    def parallel_state_details(self) -> Optional[str]:
        descriptions = []
        if isinstance(self.state, ParallelState):
            state_name = self.state_key_diagram(self.state.name)

            # Completion type
            completion_type = self.state.completionType
            if completion_type:
                descriptions.append(
                    self.state_description(
                        state_name,
                        "Completion type",
                        completion_type,
                    )
                )

            # Branches
            branches = self.state.branches
            if branches:
                descriptions.append(
                    self.state_description(
                        state_name,
                        "Num. of branches",
                        str(len(branches)),
                    )
                )

                if self.get_actions:
                    branch_states = ""
                    for branch in branches:
                        if hasattr(branch, "actions") and branch.actions:
                            branch_name = self.state_key_diagram(branch.name)
                            self.state_machine.get_state(state_name).add_substates(
                                NestedState(branch_name)
                            )
                            branch_state = self.state_machine.get_state(
                                state_name
                            ).states[branch.name]
                            sub_state_name = f"{self.state_key_diagram(self.state.name)}.{self.state_key_diagram(branch.name)}"
                            branch_states += f"state {sub_state_name} {{\n"
                            branch_states += f"{self.generate_composite_state(branch_state, f'{state_name}.{branch_name}', branch.actions, 'sequential')}\n"
                            branch_states += f"}}\n"
                            branch_states += f"[*] --> {sub_state_name}\n"
                            branch_states += f"{sub_state_name} --> [*]\n"

                    descriptions.append(
                        f"state {self.state_key_diagram(self.state.name)} {{\n{branch_states}\n}}\n"
                    )

        return "\n".join(descriptions) if descriptions else None

    def event_based_switch_state_details(self) -> str:
        return self.state_description(
            self.state_key_diagram(self.state.name), "Condition type", "event-based"
        )

    def data_based_switch_state_details(self) -> str:
        return self.state_description(
            self.state_key_diagram(self.state.name), "Condition type", "data-based"
        )

    def operation_state_details(self) -> Optional[str]:
        descriptions = []
        if isinstance(self.state, OperationState):
            action_mode = self.state.actionMode
            if action_mode:
                descriptions.append(
                    self.state_description(
                        self.state_key_diagram(self.state.name),
                        "Action mode",
                        action_mode,
                    )
                )
            actions = self.state.actions
            if actions:
                descriptions.append(
                    self.state_description(
                        self.state_key_diagram(self.state.name),
                        "Num. of actions",
                        str(len(actions)),
                    )
                )
                if self.get_actions:
                    descriptions.append(
                        f"state {self.state_key_diagram(self.state.name)} {{\n"
                        f"{self.generate_composite_state(self.state_machine.get_state(self.state.name), self.state.name, actions, action_mode)}\n"
                        f"}}\n"
                    )

        if self.state.name not in self.state_machine.states.keys():
            self.state_machine.add_states(self.state.name)
            if self.is_first_state:
                self.state_machine._initial = self.state.name

        return "\n".join(descriptions) if descriptions else None

    def sleep_state_details(self) -> Optional[str]:
        if isinstance(self.state, SleepState):
            duration = self.state.duration
            if duration:
                return self.state_description(
                    self.state_key_diagram(self.state.name), "Duration", duration
                )
        return None

    def foreach_state_details(self) -> Optional[str]:
        descriptions = []
        if isinstance(self.state, ForEachState):
            input_collection = self.state.inputCollection
            if input_collection:
                descriptions.append(
                    self.state_description(
                        self.state_key_diagram(self.state.name),
                        "Input collection",
                        input_collection,
                    )
                )
            actions = self.state.actions
            if actions:
                descriptions.append(
                    self.state_description(
                        self.state_key_diagram(self.state.name),
                        "Num. of actions",
                        str(len(actions)),
                    )
                )
        return "\n".join(descriptions) if descriptions else None

    def callback_state_details(self) -> Optional[str]:
        descriptions = []
        if isinstance(self.state, CallbackState):
            action = self.state.action
            if action and action.functionRef:
                function_ref = action.functionRef
                function_ref_description = (
                    function_ref.refName
                    if isinstance(function_ref, FunctionRef)
                    else function_ref
                )
                descriptions.append(
                    self.state_description(
                        self.state_key_diagram(self.state.name),
                        "Callback function",
                        function_ref_description,
                    )
                )

                if self.get_actions:
                    descriptions.append(
                        f"state {self.state_key_diagram(self.state.name)} {{\n"
                        f"{self.generate_composite_state(self.state_machine.get_state(self.state.name), self.state.name, [action], 'sequential')}\n"
                        f"}}\n"
                    )
            event_ref = self.state.eventRef
            if event_ref:
                descriptions.append(
                    self.state_description(
                        self.state_key_diagram(self.state.name),
                        "Callback event",
                        event_ref,
                    )
                )
        return "\n".join(descriptions) if descriptions else None

    def definition_name(self) -> str:
        return f"{self.state_key_diagram(self.state.name)} : {self.state.name}"

    def transition_description(
        self, source: str, target: str, label: Optional[str] = None
    ) -> str:
        desc = f"{self.state_key_diagram(source)} --> {self.state_key_diagram(target)}"
        if label:
            desc += f" : {label}"
        return desc

    def state_description(
        self, state_name: str, description: str, value: Optional[str] = None
    ) -> str:
        return f"{state_name} : {description}" + (
            f" = {value}" if value is not None else ""
        )

    def generate_composite_state(
        self,
        machine_state: NestedState,
        state_name: str,
        actions: List[Dict[str, Any]],
        action_mode: str,
    ) -> str:
        transitions = ""
        parallel_states = []

        if actions:
            for i, action in enumerate(actions):
                fn_name = (
                    self.get_function_name(action.functionRef)
                    if isinstance(action.functionRef, str)
                    else (
                        action.functionRef.refName
                        if isinstance(action.functionRef, FunctionRef)
                        else None
                    )
                )
                if fn_name:
                    if fn_name not in machine_state.states.keys():
                        machine_state.add_substate(NestedState(fn_name))
                    if action_mode == "sequential":
                        current_action = f"{state_name}.{fn_name}"

                        if i < len(actions) - 1:
                            next_fn_name = (
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
                            next_action = f"{state_name}.{next_fn_name}"
                            if (
                                next_fn_name
                                not in self.state_machine.get_state(
                                    state_name
                                ).states.keys()
                            ):
                                machine_state.add_substate(NestedState(next_fn_name))
                            self.state_machine.add_transition(
                                trigger="",
                                source=f"{state_name}.{fn_name}",
                                dest=f"{state_name}.{next_fn_name}",
                            )
                        else:
                            next_action = "[*]"

                        if i == 0:
                            transitions += f"[*] --> {current_action}\n"
                            machine_state.initial = fn_name

                        transitions += f"{current_action} --> {next_action}\n"
                    elif action_mode == "parallel":
                        transitions += f"[*] --> {fn_name}\n"
                        transitions += f"{fn_name} --> [*]\n"
                        parallel_states.append(fn_name)
                if action_mode == "parallel":
                    machine_state.initial = parallel_states

        return transitions

    def get_function_name(
        self, fn_ref: Union[Dict[str, Any], str, None]
    ) -> Optional[str]:
        if isinstance(fn_ref, dict) and "refName" in fn_ref:
            return self.state_key_diagram(fn_ref["refName"])
        elif isinstance(fn_ref, str):
            return self.state_key_diagram(fn_ref)
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
