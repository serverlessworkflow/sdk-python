"""Graph visualization utilities for Serverless Workflow."""

import re
from dataclasses import dataclass, field
from functools import singledispatch
from typing import Any

import pydot

from serverlessworkflow.sdk import Workflow
from serverlessworkflow.sdk.base import TaskBase, TaskItem
from serverlessworkflow.sdk.call_tasks import CallAsyncApiTask, CallHttpTask
from serverlessworkflow.sdk.tasks import (
    DoTask,
    EmitTask,
    ForkTask,
    ForTask,
    ListenTask,
    RaiseTask,
    RunTask,
    SetTask,
    SwitchTask,
    TryTask,
    WaitTask,
)


@dataclass
class Node:
    """Generic node representation, independent of rendering library."""

    name: str
    label: str | None = None
    shape: str = "box"
    style: str = "rounded"
    fillcolor: str | None = None
    color: str | None = None

    def __post_init__(self):
        """Set label to name if not provided."""
        if self.label is None:
            self.label = self.name

    def to_pydot(self) -> pydot.Node:
        """Convert to pydot.Node for rendering."""
        attrs: dict[str, Any] = {"label": f'"{self.label}"'}
        if self.shape:
            attrs["shape"] = self.shape
        if self.style:
            attrs["style"] = self.style
        if self.fillcolor:
            attrs["fillcolor"] = self.fillcolor
        if self.color:
            attrs["color"] = self.color
        return pydot.Node(self.name, **attrs)


@dataclass
class Edge:
    """Generic edge representation, independent of rendering library."""

    source: str
    destination: str
    label: str | None = None
    style: str | None = None
    color: str | None = None
    xlabel: str | None = None

    def __hash__(self):
        """Return hash of edge attributes."""
        return hash(
            (self.source, self.destination, self.label, self.style, self.color, self.xlabel)
        )

    def __eq__(self, other):
        """Check equality with another edge."""
        if not isinstance(other, Edge):
            return False
        return (
            self.source == other.source
            and self.destination == other.destination
            and self.label == other.label
            and self.style == other.style
            and self.color == other.color
            and self.xlabel == other.xlabel
        )

    def to_pydot(self) -> pydot.Edge:
        """Convert to pydot.Edge for rendering."""
        attrs: dict[str, Any] = {}
        if self.label:
            attrs["label"] = f'"{self.label}"'
        if self.style:
            attrs["style"] = self.style
        if self.color:
            attrs["color"] = self.color
        if self.xlabel:
            attrs["xlabel"] = f'"{self.xlabel}"'
        return pydot.Edge(self.source, self.destination, **attrs)


@dataclass
class Cluster:
    """Generic cluster/subgraph representation, independent of rendering library."""

    id: str
    label: str | None = None
    style: str | None = None
    color: str | None = None
    fillcolor: str | None = None
    gradientangle: str | None = None
    labelloc: str = "t"
    nodes: list[Node] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)
    subclusters: list["Cluster"] = field(default_factory=list)

    def to_pydot(self) -> pydot.Cluster:
        """Convert to pydot.Cluster for rendering."""
        attrs: dict[str, Any] = {}
        if self.label:
            attrs["label"] = f'"{self.label}"'
        if self.style:
            attrs["style"] = self.style
        if self.color:
            attrs["color"] = self.color
        if self.fillcolor:
            attrs["fillcolor"] = self.fillcolor
        if self.gradientangle:
            attrs["gradientangle"] = self.gradientangle
        if self.labelloc:
            attrs["labelloc"] = self.labelloc

        cluster = pydot.Cluster(self.id, **attrs)

        # Sort for deterministic output
        sorted_nodes = sorted(self.nodes, key=lambda n: n.name)
        for node in sorted_nodes:
            cluster.add_node(node.to_pydot())

        sorted_edges = sorted(
            self.edges,
            key=lambda e: (e.source, e.destination, e.label or "", e.style or "", e.color or ""),
        )
        for edge in sorted_edges:
            cluster.add_edge(edge.to_pydot())

        sorted_subclusters = sorted(self.subclusters, key=lambda c: c.id)
        for subcluster in sorted_subclusters:
            cluster.add_subgraph(subcluster.to_pydot())  # type: ignore[arg-type]

        return cluster


def render_workflow_graph(
    workflow: Workflow, filename: str | None = None, engine: str = "graphviz"
) -> str:
    """Render the workflow state machine to a file.

    :param workflow: The workflow object.
    :param title: Title for the graph.
    :param filename: Output filename.
    :param engine: Graph engine to use ("graphviz").
    """
    if engine == "graphviz":
        # Parse the workflow into generic graph structures
        nodes: list[Node] = []
        edges: list[Edge] = []
        clusters: list[Cluster] = []
        task_names: set[str] = set()
        task_order: list[str] = []  # Track order of tasks for flow edges
        inputs: set[str] = set()
        input_edges: list[tuple] = []  # (input_name, task_name) - use list to preserve order

        startNode = Node("start", shape="circle", style="filled", fillcolor="lightgreen")
        nodes.append(startNode)

        _parse_task(
            workflow.do, nodes, edges, clusters, task_names, task_order, inputs, input_edges
        )

        # Add input nodes for inputs that are not also task names
        # Sort for deterministic output
        pure_inputs = sorted(inputs - task_names)
        for input_name in pure_inputs:
            input_node = Node(
                input_name, label=f"Input: {input_name}", style="filled", fillcolor="lightyellow"
            )
            nodes.append(input_node)

        # Add input edges (dashed)
        for input_name, task_name in input_edges:
            if input_name in pure_inputs:
                edges.append(Edge(input_name, task_name, style="dashed", xlabel="input"))

        edges.append(Edge(startNode.name, nodes[1].name))

        endNode = Node("end", shape="doublecircle", style="filled", fillcolor="lightcoral")
        nodes.append(endNode)

        # Connect the last task(s) to the end node
        # Use task_order to get the actual last tasks (which may be inside clusters)
        if task_order:
            # Get all tasks that appear at the end of task_order
            # For forks, this will be multiple branch endings
            # For sequential tasks, this will be one task
            last_tasks = []
            if len(task_order) > 1:
                # Check if we have multiple tasks that aren't connected to anything after them
                # This happens with fork branches
                # Use list to maintain order (deterministic)
                potential_last = task_order[-3:] if len(task_order) >= 3 else task_order
                # Find tasks that don't have outgoing edges to other tasks in task_order
                for task in potential_last:
                    has_outgoing = False
                    for edge in edges:
                        if edge.source == task and edge.destination in task_names:
                            has_outgoing = True
                            break
                    if not has_outgoing or task == task_order[-1]:
                        last_tasks.append(task)
            else:
                last_tasks = [task_order[-1]]

            # Remove duplicates while preserving order
            seen = set()
            unique_last_tasks = []
            for task in last_tasks:
                if task not in seen:
                    seen.add(task)
                    unique_last_tasks.append(task)

            # Connect each last task to the end node
            for last_task in unique_last_tasks:
                edges.append(Edge(last_task, endNode.name))

        # Convert to pydot graph

        graph = pydot.Dot(
            workflow.document.name,
            graph_type="digraph",
            labelloc="top",
            fontsize="20",
            rankdir="TB",
            splines="ortho",
        )

        graph.set_node_defaults(shape="box", style="rounded")

        # Sort for deterministic output
        # Nodes are sorted by name
        sorted_nodes = sorted(nodes, key=lambda n: n.name)
        for node in sorted_nodes:
            graph.add_node(node.to_pydot())

        # Edges are sorted by (source, destination, label)
        sorted_edges = sorted(
            edges,
            key=lambda e: (e.source, e.destination, e.label or "", e.style or "", e.color or ""),
        )
        for edge in sorted_edges:
            graph.add_edge(edge.to_pydot())

        # Clusters are sorted by id
        sorted_clusters = sorted(clusters, key=lambda c: c.id)
        for cluster in sorted_clusters:
            graph.add_subgraph(cluster.to_pydot())  # type: ignore[arg-type]

    if filename is not None and filename != "":
        graph.write(filename, format="raw")

    return graph.to_string()


# Type-specific task handlers using singledispatch
@singledispatch
def _handle_task_object(
    _task_obj: Any,
    task_name: str,
    nodes: list[Node],
    edges: list[Edge],
    _clusters: list[Cluster],
    task_names: set[str],
    task_order: list[str],
    _inputs: set[str],
    _input_edges: list[tuple],
    _cluster_counter: list[int],
) -> None:
    """Default handler for unknown task types."""
    # For unknown task types, create a simple node
    task_label = f"{task_name}"
    node = Node(task_name, label=task_label)
    nodes.append(node)
    task_names.add(task_name)

    # Create edge from previous task to this task
    if task_order:
        prev_task = task_order[-1]
        edges.append(Edge(prev_task, task_name))
    task_order.append(task_name)


@_handle_task_object.register
def _(
    task_obj: ForTask,
    task_name: str,
    nodes: list[Node],
    edges: list[Edge],
    clusters: list[Cluster],
    task_names: set[str],
    task_order: list[str],
    inputs: set[str],
    input_edges: list[tuple],
    cluster_counter: list[int],
) -> None:
    """Handle ForTask: loop iteration."""
    cluster_counter[0] += 1

    cluster = Cluster(id=f"cluster_{cluster_counter[0]}", style="dashed", labelloc="b")

    # Create a node for the for task itself
    for_label = f"{task_name}\\nfor loop"
    node = Node(task_name, label=for_label, shape="hexagon", style="filled", fillcolor="lightblue")
    nodes.append(node)
    task_names.add(task_name)

    # Create edge from previous task to this for task
    if task_order:
        prev_task = task_order[-1]
        edges.append(Edge(prev_task, task_name))
    task_order.append(task_name)

    # Parse the tasks within the for loop into the cluster
    if task_obj.do:
        cluster_nodes: list[Node] = []
        cluster_edges: list[Edge] = []
        cluster_subclusters: list[Cluster] = []
        cluster_task_order: list[str] = []

        _parse_task(
            task_obj.do,
            cluster_nodes,
            cluster_edges,
            cluster_subclusters,
            task_names,
            cluster_task_order,
            inputs,
            input_edges,
            task_name,
            cluster_counter,
        )

        cluster.nodes.extend(cluster_nodes)
        cluster.edges.extend(cluster_edges)
        cluster.subclusters.extend(cluster_subclusters)

        # Add edge from for task to first task in cluster
        if cluster_nodes:
            edges.append(Edge(task_name, cluster_nodes[0].name))
            # Add edge from last task in cluster back to for task (loop)
            edges.append(Edge(cluster_nodes[-1].name, task_name, style="dotted", label="loop"))
            task_order.append(cluster_nodes[-1].name)

        clusters.append(cluster)


@_handle_task_object.register
def _(
    task_obj: ForkTask,
    task_name: str,
    nodes: list[Node],
    edges: list[Edge],
    clusters: list[Cluster],
    task_names: set[str],
    task_order: list[str],
    inputs: set[str],
    input_edges: list[tuple],
    cluster_counter: list[int],
) -> None:
    """Handle ForkTask: parallel execution."""
    cluster_counter[0] += 1

    cluster = Cluster(id=f"cluster_{cluster_counter[0]}", style="dashed", labelloc="b")

    # Create a node for the fork task itself
    fork_label = f"{task_name}\\nfork"
    node = Node(
        task_name, label=fork_label, shape="diamond", style="filled", fillcolor="lightgreen"
    )
    nodes.append(node)
    task_names.add(task_name)

    # Create edge from previous task to this fork task
    if task_order:
        prev_task = task_order[-1]
        edges.append(Edge(prev_task, task_name))
    task_order.append(task_name)

    # Parse the branches within the fork into the cluster
    if task_obj.fork:
        branches = (
            task_obj.fork.get("branches", [])
            if isinstance(task_obj.fork, dict)
            else getattr(task_obj.fork, "branches", [])
        )

        branch_last_nodes = []
        for branch in branches:
            branch_nodes: list[Node] = []
            branch_edges: list[Edge] = []
            branch_subclusters: list[Cluster] = []
            branch_task_order: list[str] = []

            _parse_task(
                branch,
                branch_nodes,
                branch_edges,
                branch_subclusters,
                task_names,
                branch_task_order,
                inputs,
                input_edges,
                task_name,
                cluster_counter,
            )

            cluster.nodes.extend(branch_nodes)
            cluster.edges.extend(branch_edges)
            cluster.subclusters.extend(branch_subclusters)

            # Add edge from fork task to first task in each branch
            if branch_nodes:
                edges.append(Edge(task_name, branch_nodes[0].name))
                branch_last_nodes.append(branch_nodes[-1].name)

        # Update task_order to continue after all branches
        if branch_last_nodes:
            task_order.extend(branch_last_nodes)

        clusters.append(cluster)


@_handle_task_object.register
def _(
    task_obj: SwitchTask,
    task_name: str,
    nodes: list[Node],
    edges: list[Edge],
    clusters: list[Cluster],
    task_names: set[str],
    task_order: list[str],
    _inputs: set[str],
    _input_edges: list[tuple],
    cluster_counter: list[int],
) -> None:
    """Handle SwitchTask: conditional branching."""
    cluster_counter[0] += 1

    cluster = Cluster(id=f"cluster_{cluster_counter[0]}", style="dashed", labelloc="b")

    # Create a node for the switch task itself
    switch_label = f"{task_name}\\nswitch"
    node = Node(
        task_name, label=switch_label, shape="triangle", style="filled", fillcolor="lightyellow"
    )
    nodes.append(node)
    task_names.add(task_name)

    # Create edge from previous task to this switch task
    if task_order:
        prev_task = task_order[-1]
        edges.append(Edge(prev_task, task_name))
    task_order.append(task_name)

    # Parse the cases within the switch into the cluster
    if task_obj.switch:
        case_nodes = []
        for case_dict in task_obj.switch:
            # Each case_dict is like {'case1': {'when': '...', 'then': '...'}}
            for case_name, case_config in case_dict.items():
                # Create a node for each case
                when_value = (
                    case_config.get("when", "")
                    if isinstance(case_config, dict)
                    else getattr(case_config, "when", "")
                )

                # Escape double quotes in the when value for DOT syntax
                when_escaped = when_value.replace('"', '\\"') if when_value else ""

                case_label = (
                    f"{case_name}\\n{when_escaped}" if when_escaped else f"{case_name}\\ndefault"
                )
                case_node = Node(
                    case_name,
                    label=case_label,
                    shape="box",
                    style="rounded,filled",
                    fillcolor="lightyellow",
                )
                cluster.nodes.append(case_node)
                case_nodes.append(case_name)

                # Add edge from switch task to this case
                edges.append(Edge(task_name, case_name, label=case_name))

        # Update task_order to include all case nodes
        if case_nodes:
            task_order.extend(case_nodes)

        clusters.append(cluster)


@_handle_task_object.register
def _(
    task_obj: TryTask,
    task_name: str,
    nodes: list[Node],
    edges: list[Edge],
    clusters: list[Cluster],
    task_names: set[str],
    task_order: list[str],
    inputs: set[str],
    input_edges: list[tuple],
    cluster_counter: list[int],
) -> None:
    """Handle TryTask: error handling with try/catch blocks."""
    cluster_counter[0] += 1

    main_cluster = Cluster(id=f"cluster_{cluster_counter[0]}", labelloc="b")

    # Create a node for the try-catch task itself
    try_label = f"{task_name}\\ntry-catch"
    node = Node(task_name, label=try_label, shape="octagon", style="filled", fillcolor="lightpink")
    nodes.append(node)
    task_names.add(task_name)

    # Create edge from previous task to this try-catch task
    if task_order:
        prev_task = task_order[-1]
        edges.append(Edge(prev_task, task_name))
    task_order.append(task_name)

    # Create subcluster for try block
    cluster_counter[0] += 1
    try_cluster = Cluster(id=f"cluster_{cluster_counter[0]}", label="try", labelloc="b")

    # Parse the try block
    try_nodes = []
    if task_obj.try_:
        try_node_list: list[Node] = []
        try_edge_list: list[Edge] = []
        try_subcluster_list: list[Cluster] = []
        try_task_order: list[str] = []

        _parse_task(
            task_obj.try_,
            try_node_list,
            try_edge_list,
            try_subcluster_list,
            task_names,
            try_task_order,
            inputs,
            input_edges,
            task_name,
            cluster_counter,
        )

        try_cluster.nodes.extend(try_node_list)
        try_cluster.edges.extend(try_edge_list)
        try_cluster.subclusters.extend(try_subcluster_list)

        # Add edge from try-catch task to first task in try block
        if try_node_list:
            edges.append(Edge(task_name, try_node_list[0].name, label="try"))
            try_nodes = try_node_list

        main_cluster.subclusters.append(try_cluster)

    # Create subcluster for catch block
    cluster_counter[0] += 1
    catch_cluster = Cluster(id=f"cluster_{cluster_counter[0]}", label="catch", labelloc="b")

    # Parse the catch block
    catch_nodes = []
    if task_obj.catch:
        catch_config = (
            task_obj.catch if isinstance(task_obj.catch, dict) else task_obj.catch.__dict__
        )
        catch_do = (
            catch_config.get("do", [])
            if isinstance(catch_config, dict)
            else getattr(task_obj.catch, "do", [])
        )

        if catch_do:
            catch_node_list: list[Node] = []
            catch_edge_list: list[Edge] = []
            catch_subcluster_list: list[Cluster] = []
            catch_task_order: list[str] = []

            _parse_task(
                catch_do,
                catch_node_list,
                catch_edge_list,
                catch_subcluster_list,
                task_names,
                catch_task_order,
                inputs,
                input_edges,
                task_name,
                cluster_counter,
            )

            catch_cluster.nodes.extend(catch_node_list)
            catch_cluster.edges.extend(catch_edge_list)
            catch_cluster.subclusters.extend(catch_subcluster_list)

            # Add edge from try-catch task to first task in catch block (on error)
            if catch_node_list:
                edges.append(
                    Edge(
                        task_name,
                        catch_node_list[0].name,
                        label="catch",
                        style="dashed",
                        color="red",
                    )
                )
                catch_nodes = catch_node_list

            main_cluster.subclusters.append(catch_cluster)

            # Update task_order to include both try and catch last nodes
            if try_nodes:
                task_order.append(try_nodes[-1].name)
            if catch_nodes:
                task_order.append(catch_nodes[-1].name)

    clusters.append(main_cluster)


@_handle_task_object.register
def _(
    task_obj: CallHttpTask,
    task_name: str,
    nodes: list[Node],
    edges: list[Edge],
    clusters: list[Cluster],
    task_names: set[str],
    task_order: list[str],
    inputs: set[str],
    input_edges: list[tuple],
    cluster_counter: list[int],
) -> None:
    """Handle CallHttpTask: HTTP requests."""
    if task_obj.with_ is None:
        task_label = f"{task_name}\\ncall: http"
    else:
        task_label = (
            f"{task_name}\\ncall: http\\n{task_obj.with_.method.upper()} {task_obj.with_.endpoint}"
        )
    node = Node(task_name, label=task_label)
    nodes.append(node)
    task_names.add(task_name)

    # Create edge from previous task to this task
    if task_order:
        prev_task = task_order[-1]
        edges.append(Edge(prev_task, task_name))
    task_order.append(task_name)

    # Recursively parse the task object, passing task_name as current
    _parse_task(
        task_obj,
        nodes,
        edges,
        clusters,
        task_names,
        task_order,
        inputs,
        input_edges,
        task_name,
        cluster_counter,
    )


@_handle_task_object.register
def _(
    task_obj: CallAsyncApiTask,
    task_name: str,
    nodes: list[Node],
    edges: list[Edge],
    clusters: list[Cluster],
    task_names: set[str],
    task_order: list[str],
    inputs: set[str],
    input_edges: list[tuple],
    cluster_counter: list[int],
) -> None:
    """Handle CallAsyncApiTask: AsyncAPI operations with optional foreach in subscription."""
    task_label = f"{task_name}\\ncall: asyncapi"
    if (
        task_obj.with_ is not None
        and hasattr(task_obj.with_, "operation")
        and task_obj.with_.operation
    ):
        task_label += f"\\n{task_obj.with_.operation}"

    node = Node(task_name, label=task_label)
    nodes.append(node)
    task_names.add(task_name)

    # Create edge from previous task to this task
    if task_order:
        prev_task = task_order[-1]
        edges.append(Edge(prev_task, task_name))
    task_order.append(task_name)

    # Check if there's a foreach in the subscription
    if (
        task_obj.with_ is not None
        and hasattr(task_obj.with_, "subscription")
        and task_obj.with_.subscription
    ):
        subscription = task_obj.with_.subscription
        subscription_dict = (
            subscription
            if isinstance(subscription, dict)
            else (subscription.__dict__ if hasattr(subscription, "__dict__") else {})
        )

        foreach_config = (
            subscription_dict.get("foreach")
            if isinstance(subscription_dict, dict)
            else getattr(subscription, "foreach", None)
        )

        if foreach_config:
            # Create a cluster for the foreach loop within this task
            cluster_counter[0] += 1

            cluster = Cluster(id=f"cluster_{cluster_counter[0]}", style="dashed", labelloc="b")

            # Parse the tasks within the foreach
            foreach_do = (
                foreach_config.get("do", [])
                if isinstance(foreach_config, dict)
                else getattr(foreach_config, "do", [])
            )

            if foreach_do:
                foreach_nodes: list[Node] = []
                foreach_edges: list[Edge] = []
                foreach_subclusters: list[Cluster] = []
                foreach_task_order: list[str] = []

                _parse_task(
                    foreach_do,
                    foreach_nodes,
                    foreach_edges,
                    foreach_subclusters,
                    task_names,
                    foreach_task_order,
                    inputs,
                    input_edges,
                    task_name,
                    cluster_counter,
                )

                cluster.nodes.extend(foreach_nodes)
                cluster.edges.extend(foreach_edges)
                cluster.subclusters.extend(foreach_subclusters)

                # Add edge from main task to first task in foreach
                if foreach_nodes:
                    edges.append(Edge(task_name, foreach_nodes[0].name, label="foreach"))
                    # Update task_order to include the last task in the foreach
                    task_order.append(foreach_nodes[-1].name)

                clusters.append(cluster)

    # Recursively parse the task object for other nested structures
    _parse_task(
        task_obj,
        nodes,
        edges,
        clusters,
        task_names,
        task_order,
        inputs,
        input_edges,
        task_name,
        cluster_counter,
    )


@_handle_task_object.register(ListenTask)
@_handle_task_object.register(SetTask)
@_handle_task_object.register(WaitTask)
@_handle_task_object.register(EmitTask)
@_handle_task_object.register(RaiseTask)
@_handle_task_object.register(RunTask)
@_handle_task_object.register(DoTask)
def _(
    task_obj: Any,
    task_name: str,
    nodes: list[Node],
    edges: list[Edge],
    _clusters: list[Cluster],
    task_names: set[str],
    task_order: list[str],
    inputs: set[str],
    input_edges: list[tuple],
    _cluster_counter: list[int],
) -> None:
    """Handle simple task types with basic rendering."""
    task_type = type(task_obj).__name__.replace("Task", "").lower()
    task_label = f"{task_name}\\n{task_type}"
    node = Node(task_name, label=task_label)
    nodes.append(node)
    task_names.add(task_name)

    # Create edge from previous task to this task
    if task_order:
        prev_task = task_order[-1]
        edges.append(Edge(prev_task, task_name))
    task_order.append(task_name)

    # Extract inputs from task
    _extract_inputs(task_obj, inputs, input_edges, task_name)


def _parse_task(
    task: list[TaskItem] | TaskItem | dict | CallHttpTask | CallAsyncApiTask,
    nodes: list[Node],
    edges: list[Edge],
    clusters: list[Cluster],
    task_names: set[str],
    task_order: list[str],
    inputs: set[str],
    input_edges: list[tuple],
    current_task_name: str | None = None,
    cluster_counter: list[int] | None = None,
) -> None:
    """Parse workflow tasks into generic graph structures."""
    if cluster_counter is None:
        cluster_counter = [0]

    if isinstance(task, list):
        for t in task:
            _parse_task(
                t,
                nodes,
                edges,
                clusters,
                task_names,
                task_order,
                inputs,
                input_edges,
                current_task_name,
                cluster_counter,
            )
    elif isinstance(task, TaskItem):
        # Handle TaskItem objects (name + task pair)
        _handle_task_object(
            task.task,
            task.name,
            nodes,
            edges,
            clusters,
            task_names,
            task_order,
            inputs,
            input_edges,
            cluster_counter,
        )
    elif isinstance(task, dict):
        for task_name, task_obj in task.items():
            # Dispatch to the appropriate handler based on task type
            _handle_task_object(
                task_obj,
                task_name,
                nodes,
                edges,
                clusters,
                task_names,
                task_order,
                inputs,
                input_edges,
                cluster_counter,
            )
    elif isinstance(task, TaskBase):
        # Extract inputs from task (e.g., {petId} in endpoint URLs)
        # and track edges from input to current task
        _extract_inputs(task, inputs, input_edges, current_task_name)
        # Handle nested tasks within TaskBase objects (e.g., do, fork, etc.)
        if (
            hasattr(task, "do")
            and task.do is not None
            and not isinstance(task, (ForTask | ForkTask | SwitchTask))
        ):
            _parse_task(
                task.do,
                nodes,
                edges,
                clusters,
                task_names,
                task_order,
                inputs,
                input_edges,
                current_task_name,
                cluster_counter,
            )


def _extract_inputs(
    task: TaskBase, inputs: set[str], input_edges: list[tuple], current_task_name: str | None
) -> None:
    """Extract input variables from a task and track edges to the task."""
    # Look for {variable} patterns in task properties
    # For HTTP tasks, check the endpoint
    if hasattr(task, "with_") and task.with_ is not None:
        with_obj = task.with_
        if hasattr(with_obj, "endpoint") and with_obj.endpoint:
            # Find all {variable} patterns
            matches = re.findall(r"\{(\w+)\}", str(with_obj.endpoint))
            for match in matches:
                inputs.add(match)
                if current_task_name and (match, current_task_name) not in input_edges:
                    input_edges.append((match, current_task_name))
