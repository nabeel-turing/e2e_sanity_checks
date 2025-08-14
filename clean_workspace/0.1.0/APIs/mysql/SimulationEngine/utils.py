from __future__ import annotations

from typing import Any, Dict, List
import json
import datetime

import duckdb
from sqlglot import parse_one

from .db import db_manager

# ----------------------------------------------------------------------
# JSON Serialization
# ----------------------------------------------------------------------
class DateTimeEncoder(json.JSONEncoder):
    """
    Custom JSON encoder that converts datetime objects to ISO format strings.
    
    This encoder handles datetime.datetime, datetime.date, and datetime.time objects
    by converting them to their ISO format string representation, which is compatible
    with JSON and can be parsed by most datetime libraries.
    """
    def default(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
            return obj.isoformat()
        return super().default(obj)

# ----------------------------------------------------------------------
# Internal helpers
# ----------------------------------------------------------------------
def _query_type(sql: str) -> str: # pragma: no cover
    """Return first SQL keyword in lower-case (`select`, `insert`, …)."""
    try:
        expr = parse_one(sql, error_level="ignore")
        if expr:
            return expr.key.lower()
    except Exception:
        pass
    return sql.lstrip().split(None, 1)[0].lower()


def _current_schema() -> str: # pragma: no cover
    """Return the currently selected database alias, or 'default'."""
    alias = db_manager._current_db_alias  # pylint: disable=protected-access
    return alias or "default"


def _format_success(sql: str, result: Dict[str, Any]) -> str: # pragma: no cover
    """Generate human success strings identical to the TS MCP helpers."""
    qtype = _query_type(sql)
    schema = _current_schema()
    affected = result.get("affected_rows", 0)

    if qtype == "insert":
        last_id = affected if affected else 0
        return (
            f"Insert successful on schema '{schema}'. "
            f"Affected rows: {affected}, Last insert ID: {last_id}"
        )
    if qtype == "update":
        changed = affected
        return (
            f"Update successful on schema '{schema}'. "
            f"Affected rows: {affected}, Changed rows: {changed}"
        )
    if qtype == "delete":
        return f"Delete successful on schema '{schema}'. Affected rows: {affected}"
    return f"DDL operation successful on schema '{schema}'."


def _tables_for_db(db_name: str) -> List[str]: # pragma: no cover
    """Return table names for `db_name` and restore previous context."""
    cur = db_manager._current_db_alias  # pylint: disable=protected-access
    try:
        db_manager.execute_query(f"USE {db_name}") 
        table_catalog = "handler_main_test" if db_name == "main" else db_name
        rows = db_manager.execute_query(f"SELECT table_name FROM information_schema.tables WHERE table_catalog = '{table_catalog}'")["data"] or []
        return [r[0] for r in rows]
    except duckdb.CatalogException:
        # NOTE: Unlike MySQL, DuckDB's duckdb_databases() doesn't list empty attached databases because it only tracks databases with at least one table or view.
        return []
    finally:
        if cur != db_manager._current_db_alias:
            db_manager.execute_query(f"USE {cur}")
