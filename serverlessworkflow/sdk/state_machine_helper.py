from typing import List
from serverlessworkflow.sdk.workflow import Workflow
from serverlessworkflow.sdk.state_machine_generator import StateMachineGenerator
from transitions.extensions.diagrams import HierarchicalGraphMachine, GraphMachine
from transitions.extensions.nesting import NestedState
from transitions.extensions.diagrams_base import BaseGraph


class StateMachineHelper:
    FINAL_NODE_STYLE = {"fillcolor": "lightgreen", "peripheries": "2", "color": "green"}
    NESTED_NODE_STYLE = {"fillcolor": "cornflowerblue"}

    def __init__(
        self,
        workflow: Workflow,
        subflows: List[Workflow] = [],
        get_actions=False,
        title="",
    ):
        self.subflows = subflows
        self.get_actions = get_actions

        machine_type = HierarchicalGraphMachine if self.get_actions else GraphMachine

        # Generate machine
        self.machine = machine_type(
            model=None,
            initial=None,
            show_conditions=True,
            auto_transitions=False,
            title=title,
        )
        for index, state in enumerate(workflow.states):
            StateMachineGenerator(
                state=state,
                state_machine=self.machine,
                is_first_state=index == 0,
                get_actions=self.get_actions,
                subflows=subflows,
            ).generate()

        delattr(self.machine, "get_graph")
        self.machine.add_model(machine_type.self_literal)

    def draw(self, filename: str, graph_engine="pygraphviz"):
        final_nested = []
        if graph_engine == "mermaid":
            self.machine.graph_cls = self.machine._init_graphviz_engine(
                graph_engine="mermaid"
            )
            self.machine.model_graphs[id(self.machine.model)] = self.machine.graph_cls(
                self.machine
            )
            self.machine.model_graphs[id(self.machine.model)].set_node_style(
                getattr(self.machine.model, self.machine.model_attribute), "active"
            )
        if graph_engine != "mermaid":
            if self.get_actions:
                for _, s in self.machine.states.items():
                    final_nested.extend(self._get_nested_active_states(s))

        # Define style
        for name in (
            self.machine.get_nested_state_names()
            if self.get_actions
            else self.machine.states.keys()
        ):
            if self.machine.get_state(name).final or name in final_nested:
                self.machine.style_attributes["node"][name] = (
                    self.FINAL_NODE_STYLE
                    if self.machine.get_state(name).final
                    else self.NESTED_NODE_STYLE
                )
                self.machine.model_graphs[id(self.machine.model)].set_node_style(
                    name, name
                )

        self.machine.get_graph().draw(filename, prog="dot")

    def _color_graph_nodes(self, graph: BaseGraph, final_nested: List[str] = []):
        graph.graph_attr.update({"ranksep": "1.0"})
        for node in graph.nodes():
            if self.machine.get_state(str(node)).final:
                graph.get_node(node).attr["fillcolor"] = "lightgreen"
                graph.get_node(node).attr["peripheries"] = "2"
                graph.get_node(node).attr["color"] = "green"
            if str(node) in final_nested:
                graph.get_node(node).attr["fillcolor"] = "cornflowerblue"

    @classmethod
    def _get_nested_active_states(cls, state: NestedState, depth=0):
        if len(state.states) == 0:
            if depth > 0:
                return [state.name]
            else:
                return []

        final_states = []
        for _, nested in state.states.items():
            final_states.extend(
                f"{state.name}.{n}"
                for n in cls._get_nested_active_states(nested, depth + 1)
            )

        return final_states
