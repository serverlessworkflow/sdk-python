"""Validation tests for Serverless Workflow specification examples."""

from pathlib import Path

import pytest

from serverlessworkflow.sdk.workflow import Workflow

SPEC_EXAMPLES_DIR = (
    Path(__file__).parent.parent.parent / "submodules" / "specification" / "examples"
)


@pytest.mark.spec_example
@pytest.mark.parametrize("example_file", list(SPEC_EXAMPLES_DIR.glob("*.yaml")))
def test_spec_example_validations(example_file):
    """Test that SDK can parse and validate spec examples."""
    # Parse the example using v1 SDK
    with open(example_file, encoding="utf-8") as f:
        workflow = Workflow.from_yaml(f.read())

    # Verify basic structure was parsed correctly
    assert workflow.document is not None
    assert workflow.do is not None
    assert len(workflow.do) > 0

    # Test round-trip: YAML -> Workflow -> YAML -> Workflow
    yaml_output = workflow.to_yaml()
    workflow2 = Workflow.from_yaml(yaml_output)

    assert workflow == workflow2
