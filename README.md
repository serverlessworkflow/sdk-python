# Serverless Workflow Specification - Python SDK

Provides the Python API/SPI for the [Serverless Workflow Specification](https://github.com/serverlessworkflow/specification)

> This is a WIP implementation

With the SDK you can:
* **WIP** Programmatically build workflow definitions 
* Parse workflow JSON and YAML definitions
* Validate workflow definitions


## Install dependencies and run test 

- Python 3 required

- pipenv required `pip install pipenv`

```
pipenv install

pipenv shell

python setup.py pytest
```

## **WIP** Programmatically build workflow definitions 

```
workflow = Workflow(id_="greeting",
                    name="Greeting Workflow",
                    description="Greet Someone",
                    version='1.0',
                    specVersion='0.8',
                    start="Greet",
                    states=[],
                    functions=[]
)             
```

## Parse workflow JSON and YAML definitions

### Convert from JSON or YAML source

```
swf_content = """id: greeting
name: Greeting Workflow
version: '1.0'
description: Greet Someone
specVersion: '0.8'
start: Greet
states:
- name: Greet
  type: operation
  actions:
  - functionRef:
      refName: greetingFunction
      arguments:
        name: ${ .person.name }
    actionDataFilter:
      results: ${ .greeting }
  end: true
functions:
- name: greetingFunction
  operation: file://myapis/greetingapis.json#greeting
"""
  workflow = Workflow.from_source(swf_content)
```

You can see a full example in the [test_workflow.py](tests/serverlessworkflow/sdk/test_workflow.py) file


### Parse workflow to JSON / YAML

```
workflow = Workflow(id_="greeting",
                    name="Greeting Workflow",
                    description="Greet Someone",
                    version='1.0',
                    specVersion='0.8',
                    start="Greet",
                    states=[],
                    functions=[]
)                
print(workflow.to_json())
print(workflow.to_yaml())
```

You can see a full example in the [test_workflow.py](tests/serverlessworkflow/sdk/test_workflow.py) file


## Validate workflow definitions

```
workflow = Workflow(id_="greeting",
                    name="Greeting Workflow",
                    description="Greet Someone",
                    version='1.0',
                    specVersion='0.8',
                    start="Greet",
                    states=[],
                    functions=[]
)
WorkflowValidator(Workflow(workflow)).validate()

```
The `validate` method will raise an exception if the provided workflow does not complaint specification.

You can see a full example in the [test_workflow_validator](tests/serverlessworkflow/sdk/test_workflow_validator.py) file