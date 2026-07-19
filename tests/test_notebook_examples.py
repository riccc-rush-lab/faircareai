"""Source-level contracts for documented notebook entry points."""

from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_notebook_guide_distinguishes_distribution_and_import_names() -> None:
    guide = (ROOT / "docs" / "NOTEBOOKS.md").read_text()

    assert "pip install faircare" in guide
    assert "from faircareai import" in guide
    assert "pip install marimo" in guide
    assert "%pip install faircare" in guide
    assert "max_collect_rows" in guide
    assert "save_delta" in guide


def test_jupyter_quickstart_uses_the_published_package_name() -> None:
    notebook = json.loads((ROOT / "notebooks" / "quickstart_tutorial.ipynb").read_text())
    source = "\n".join("".join(cell.get("source", [])) for cell in notebook["cells"])

    assert "pip install faircare" in source
    assert "pip install faircareai" not in source
    assert "results.show(platform=\"jupyter\")" in source


def test_marimo_quickstart_is_runnable_and_uses_the_public_display_api() -> None:
    source = (ROOT / "notebooks" / "marimo_quickstart.py").read_text()

    ast.parse(source)
    assert "import marimo as mo" in source
    assert "from faircareai import FairCareAudit" in source
    assert 'results.show(platform="marimo")' in source
    assert "results.to_tables()" in source
    assert "results.save_artifacts" in source
