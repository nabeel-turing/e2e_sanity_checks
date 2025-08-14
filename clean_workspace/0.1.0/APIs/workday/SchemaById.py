"""
SCIM Schema Management by ID Module

This module provides functionality for managing SCIM (System for Cross-domain Identity Management)
schemas using their unique URIs in the Workday Strategic Sourcing system. It supports operations
for retrieving detailed schema information.

The module interfaces with the simulation database to provide access to SCIM schema definitions,
which are essential for understanding the structure and attributes of identity resources in the
system.

Functions:
    get: Retrieves a specific SCIM schema by its URI
"""

from typing import Dict, Optional, Any
from .SimulationEngine import db

def get(uri: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves a specific SCIM schema by its URI.

    This endpoint provides the structure and metadata for a SCIM resource type, including all attributes and constraints, as defined by the schema URI (e.g., User, Group).

    Args:
        uri (str): Schema URI identifying the SCIM resource type.
            - Example: "urn:ietf:params:scim:schemas:core:2.0:User"

    Returns:
        Optional[Dict[str, Any]]: None or the definition of the SCIM schema. If found, it can contain the following keys:
            - schemas (List[str]): List of schema URIs this response complies with.
            - id (str): Unique identifier of the schema.
            - meta (Dict[str, str]):
                - resourceType (str): Type of resource.
                - location (str): URI to fetch the schema.
            - name (str): Human-readable schema name.
            - description (str): Human-readable schema description.
            - attributes (List[Dict[str, Any]]): Attributes defined by this schema.
                - name (str): Name of the attribute.
                - type (str): Data type (e.g., string, boolean).
                - subAttributes (List[Dict[str, Any]]): Nested attributes (for complex types).
                - multiValued (bool): Whether the attribute accepts multiple values.
                - description (str): Description of the attribute.
                - required (str): Whether the attribute is required ("true" or "false").
                - canonicalValues (List[str]): List of valid values for the attribute.
                - caseExact (bool): Indicates case sensitivity.
                - mutability (str): Defines write access (e.g., readOnly, readWrite).
                - returned (str): Visibility in responses (e.g., always, default).
                - uniqueness (str): Defines uniqueness level (none, server, global).
                - referenceTypes (List[str]): Reference target types (if type = reference).

    """
    for schema in db.DB["scim"]["schemas"]:
        if schema.get("uri") == uri:
            return schema
    return None 