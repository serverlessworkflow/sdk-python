# Serverless Workflow Specification - Python SDK

Provides the Python API/SPI for the [Serverless Workflow Specification](https://github.com/serverlessworkflow/specification)

With the SDK you can:
* Programmatically build workflow definitions 
* Parse workflow JSON and YAML definitions
* Validate workflow definitions

### Status

Current sdk version conforms to the [Serverless Workflow specification v1.0](https://github.com/serverlessworkflow/specification/tree/v1.0.0).

### Install and use

- Python 3.10+ required

```bash
pip install serverlessworkflow
```

```python
from serverlessworkflow.sdk import (
    Workflow,
    Document,
    CallHttpTask,
    CallHttpArguments,
)

new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2", 
                    namespace="examples", 
                    name="http-query-params", 
                    version="1.0.0"
                ),
                do=[
                    {
                        "searchStarWarsCharacters": CallHttpTask(
                            with_=CallHttpArguments(
                                method="get",
                                endpoint="https://swapi.dev/api/people/",
                                query={"search": "${.searchQuery}"},
                            )
                        )
                    }
                ],
                input={
                    "schema": {
                        "format": "json",
                        "document": {
                            "type": "object",
                            "required": ["searchQuery"],
                            "properties": {"searchQuery": {"type": "string"}},
                        },
                    }
                },
            )
```

## Programmatically build workflow definitions

```python
from serverlessworkflow.sdk import (
    Workflow,
    Document,
    CallHttpTask,
    CallHttpArguments,
)

workflow = Workflow(
    document=Document(
        dsl="1.0.0",
        namespace="default",
        name="greeting",
        version="1.0.0",
        title="Greeting Workflow",
        summary="Greet Someone",
    ),
    do=[
        CallHttpTask(
            call="http",
            with_=CallHttpArguments(
                method="get",
                endpoint="https://api.example.com/greet?name={$input.name}"
            )
        )
    ]
)
```
You can see full examples in the [tests/specification](tests/specification) directory

## Parse workflow JSON and YAML definitions

### Load from YAML source

```python
from serverlessworkflow.sdk import Workflow

yaml_content = """
document:
  dsl: 1.0.0-alpha1
  namespace: default
  name: greeting
  version: 1.0.0
do:
  - call: http
    with:
      method: get
      endpoint: https://api.example.com/greet
"""

workflow = Workflow.from_yaml(yaml_content)
```

You can see full examples in the [tests/specification](tests/specification) directory


### Export workflow to YAML

```python
from serverlessworkflow.sdk import Workflow, Document, SetTask

workflow = Workflow(
    document=Document(
        dsl="1.0.0-alpha1",
        namespace="default",
        name="greeting",
        version="1.0.0",
    ),
    do=[
        SetTask(set={"greeting": "Hello World"})
    ]
)

yaml_output = workflow.to_yaml()
print(yaml_output)
```

You can see full examples in the [tests/specification](tests/specification) directory

## Generate workflow state machine and graph

**Note** Please note that `pip install serverlessworkflow[viz]` needs to be installed in order for this to work. The `viz` feature installs pydot, which supports `graphviz`.

To generate the workflow graph diagram:

To dot files:
```python
workflow.render_graph(filename="/tmp/out.dot")
```

The following requires `graphviz` to be installed (verify by checking to see if the `dot` binary is on the PATH):

To png files:
```python
workflow.render_graph(filename="/tmp/out.png")
```

# Local development

## Install dependencies and run tests

- [uv](https://docs.astral.sh/uv/) recommended for dependency management

```bash

# Install dependencies
uv sync --all-extras
uv pip install -e .[dev,viz]

# Run tests
uv run pytest

# Run linting
uv run ruff check .

# Run type checking
uv run mypy .
```