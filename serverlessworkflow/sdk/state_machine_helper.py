from typing import List
from serverlessworkflow.sdk.workflow import Workflow
from serverlessworkflow.sdk.state_machine_generator import StateMachineGenerator
from serverlessworkflow.sdk.state_machine_extensions import (
    CustomGraphMachine,
    CustomHierarchicalGraphMachine,
)


class StateMachineHelper:
    FINAL_NODE_STYLE = {"peripheries": "2", "color": "red"}
    INITIAL_NODE_STYLE = {"peripheries": "2", "color": "green"}
    TAGS = [
        "parallel_state",
        "switch_state",
        "inject_state",
        "operation_state",
        "sleep_state",
        "event_state",
        "foreach_state",
        "callback_state",
        "subflow",
        "function",
        "event",
        "branch",
    ]
    COLORS = [
        "#8dd3c7",
        "#ffffb3",
        "#bebada",
        "#fb8072",
        "#80b1d3",
        "#fdb462",
        "#b3de69",
        "#fccde5",
        "#d9d9d9",
        "#bc80bd",
        "#ccebc5",
        "#ffed6f",
    ]

    def __init__(
        self,
        workflow: Workflow,
        subflows: List[Workflow] = [],
        get_actions=False,
        title="",
    ):
        self.subflows = subflows
        self.get_actions = get_actions

        machine_type = (
            CustomHierarchicalGraphMachine if self.get_actions else CustomGraphMachine
        )

        # Generate machine
        self.machine = machine_type(
            model=None,
            initial=None,
            show_conditions=True,
            auto_transitions=False,
            title=title,
        )
        StateMachineGenerator(
            workflow=workflow,
            state_machine=self.machine,
            get_actions=self.get_actions,
            subflows=subflows,
        ).generate()

        delattr(self.machine, "get_graph")
        del self.machine.style_attributes["node"]["active"]
        del self.machine.style_attributes["graph"]["active"]
        self.machine.add_model(machine_type.self_literal)

    def draw(self, filename: str, graph_engine="pygraphviz"):
        if graph_engine == "mermaid":
            self.machine.graph_cls = self.machine._init_graphviz_engine(
                graph_engine="mermaid"
            )
            self.machine.model_graphs[id(self.machine.model)] = self.machine.graph_cls(
                self.machine
            )

        # Define style
        for name in (
            self.machine.get_nested_state_names()
            if self.get_actions
            else self.machine.states.keys()
        ):
            if self.machine.get_state(name).final or self.machine.initial == name:
                self.machine.style_attributes["node"][name] = (
                    self.FINAL_NODE_STYLE
                    if self.machine.get_state(name).final
                    else self.INITIAL_NODE_STYLE
                )
                self.machine.model_graphs[id(self.machine.model)].set_node_style(
                    name, name
                )

            for tag in self.machine.get_state(name).tags:
                if tag in self.TAGS:
                    self.machine.style_attributes["node"][name] = {
                        "fillcolor": self.COLORS[self.TAGS.index(tag)]
                    }
                    self.machine.model_graphs[id(self.machine.model)].set_node_style(
                        name, name
                    )
                    break

        self.machine.get_graph().draw(filename, prog="dot")
