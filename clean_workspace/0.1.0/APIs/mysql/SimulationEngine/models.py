"""
models.py
------------------

Pydantic (v1) models describing the JSON file that keeps persistent
state for the DuckDB‐backed MySQL simulator.

Example JSON
============

{
  "attached": {
    "main_db": {
      "sanitized": "main_db",
      "path": "main_db.duckdb"
    },
    "inventory_db": {
      "sanitized": "inventory_db",
      "path": "inventory_db.duckdb"
    }
  },
  "current": "main",
  "primary_internal_name": "main_db"
}
"""

from __future__ import annotations

import re
from typing import Dict

from pydantic import BaseModel, Field, validator


# ---------------------------------------------------------------------------
# Validators / helpers
# ---------------------------------------------------------------------------
_DB_NAME_RE = re.compile(r"^[A-Za-z0-9_\-]+$")


def _validate_db_name(name: str) -> str:
    if not _DB_NAME_RE.match(name) or name in {".", ".."}:
        raise ValueError("invalid MySQL database name")
    return name


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class AttachedEntry(BaseModel):
    """
    One entry inside the ``attached`` mapping.

    Attributes
    ----------
    sanitized:
        File-system safe alias actually used when the database is ATTACHed
        to DuckDB.
    path:
        Relative path to the ``*.duckdb`` file from the simulator’s
        database_directory.
    """

    sanitized: str = Field(..., description="sanitized DuckDB alias")
    path: str = Field(..., description="relative path to *.duckdb file")

    # basic sanity check
    _db_name = validator("sanitized", allow_reuse=True)(_validate_db_name)


class SimulationSnapshot(BaseModel):
    """
    Root model that mirrors the JSON snapshot persisted by DuckDBManager.

    Attributes
    ----------
    attached:
        Mapping of user-visible database names to their corresponding
        `AttachedEntry`.
    current:
        Alias currently selected with `USE` (often `"main"`).
    primary_internal_name:
        The internal name DuckDB assigned to the main database file
        (helps during result-patching).
    """

    attached: Dict[str, AttachedEntry]
    current: str
    primary_internal_name: str

    # Validation for keys in `attached`
    @validator("attached", pre=True)
    def _validate_keys(cls, v):
        if not isinstance(v, dict):
            raise TypeError("attached must be an object")
        for key in v:
            _validate_db_name(key)
        return v

