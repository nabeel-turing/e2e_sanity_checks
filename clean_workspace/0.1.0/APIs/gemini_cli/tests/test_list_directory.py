import json
import os
import sys
from pathlib import Path

import pytest

# Ensure package root is importable when tests run via py.test
sys.path.append(str(Path(__file__).resolve().parents[2]))

from gemini_cli import list_directory  # noqa: E402
from gemini_cli.SimulationEngine import db as sim_db  # noqa: E402
from gemini_cli.SimulationEngine.custom_errors import InvalidInputError  # noqa: E402

DB_JSON_PATH = Path(__file__).resolve().parents[3] / "DBs" / "GeminiCliDefaultDB.json"


@pytest.fixture(autouse=True)
def reload_db(tmp_path):
    """Load fresh DB snapshot before each test."""
    sim_db.DB.clear()
    with open(DB_JSON_PATH, "r", encoding="utf-8") as fh:
        sim_db.DB.update(json.load(fh))
    yield
    sim_db.DB.clear()


def test_root_listing():
    root = sim_db.DB["workspace_root"]
    items = list_directory(root)
    names = [i["name"] for i in items]
    
    # Check expected files
    assert "README.md" in names
    assert ".gitignore" in names
    assert ".geminiignore" in names
    assert "package.json" in names
    
    # Check expected directories
    assert "src" in names
    assert "docs" in names
    assert "tests" in names
    assert ".gemini" in names
    
    # Check that we have the expected number of items (4 files + 4 directories = 8 total)
    assert len(items) == 8
    
    # Verify mix of files and directories
    files = [item for item in items if not item["is_directory"]]
    directories = [item for item in items if item["is_directory"]]
    assert len(files) == 4  # .gitignore, .geminiignore, README.md, package.json
    assert len(directories) == 4  # src, docs, tests, .gemini


def test_ignore_pattern():
    root = sim_db.DB["workspace_root"]
    items = list_directory(root, ignore=["*.md"])
    assert all(not n["name"].endswith(".md") for n in items)


def test_invalid_path_type():
    with pytest.raises(InvalidInputError):  # type: ignore[name-defined]
        list_directory(123)  # type: ignore[arg-type]


def test_relative_path():
    with pytest.raises(InvalidInputError):  # type: ignore[name-defined]
        list_directory("relative/path")


def test_path_outside_workspace():
    with pytest.raises(InvalidInputError):  # type: ignore[name-defined]
        list_directory("/etc")


def test_ignore_not_list():
    root = sim_db.DB["workspace_root"]
    with pytest.raises(InvalidInputError):  # type: ignore[name-defined]
        list_directory(root, ignore="*.md")  # type: ignore[arg-type]


def test_ignore_contains_non_string():
    root = sim_db.DB["workspace_root"]
    with pytest.raises(InvalidInputError):  # type: ignore[name-defined]
        list_directory(root, ignore=[123])  # type: ignore[list-item] 