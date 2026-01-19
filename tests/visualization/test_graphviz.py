"""Docstring for tests.visualization.test_graphviz.

Tests for graphviz visualization of Serverless Workflow spec examples.
"""
import subprocess
from pathlib import Path

import pytest

from serverlessworkflow.sdk.workflow import Workflow

SPEC_EXAMPLES_DIR = (
    Path(__file__).parent.parent.parent / "submodules" / "specification" / "examples"
)


@pytest.mark.spec_example
@pytest.mark.parametrize(
    "example_file", list(SPEC_EXAMPLES_DIR.glob("*.yaml")), ids=lambda f: f.name
)
def test_graphviz_examples(example_file):
    """Test that SDK can render graphviz visualizations for spec examples."""
    print(f"Testing workflow from {example_file.name}:")

    with open(example_file, encoding="utf-8") as f:
        workflow = Workflow.from_yaml(f.read())

    Path("tests/visualization/outputs").mkdir(parents=True, exist_ok=True)

    example_name = example_file.stem

    # rendered_graph = workflow.render_graph()
    rendered_graph = workflow.render_graph(
        filename=f"tests/visualization/outputs/{example_name}.dot"
    )

    # Render PNG visualizations for comparison
    fixture_dot = Path(f"tests/visualization/fixtures/{example_name}.dot")

    if fixture_dot.exists():
        fixture_png = fixture_dot.with_suffix(".png")
        try:
            subprocess.run(
                ["dot", "-Tpng", str(fixture_dot), "-o", str(fixture_png)],
                check=True,
                capture_output=True,
            )
            print(f"  Generated: {fixture_png}")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"  Warning: Could not render {fixture_png}: {e}")

    output_filename = Path(f"tests/visualization/outputs/{example_name}.dot")
    if output_filename.exists():
        output_png = output_filename.with_suffix(".png")
        try:
            subprocess.run(
                ["dot", "-Tpng", str(output_filename), "-o", str(output_png)],
                check=True,
                capture_output=True,
            )
            print(f"  Generated: {output_png}")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"  Warning: Could not render {output_png}: {e}")

    with open(f"tests/visualization/fixtures/{example_name}.dot", encoding="utf-8") as f:
        expected_graph = f.read()

    assert rendered_graph == expected_graph
