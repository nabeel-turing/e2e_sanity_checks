"""
SCIM Resource Type Management by ID Module

This module provides functionality for managing SCIM (System for Cross-domain Identity
Management) resource types using their unique identifiers in the Workday Strategic
Sourcing system. It supports operations for retrieving detailed information about
specific resource types.

The module interfaces with the simulation database to provide access to SCIM resource
type definitions, which include endpoint configurations, supported schemas, and
extensions for different types of resources in the system.

Functions:
    get: Retrieves SCIM resource type details by resource name
"""

from typing import Dict, Optional, Any
from .SimulationEngine import db

def get(resource: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves metadata for a specific SCIM resource type.

    This endpoint provides the schema, endpoint path, and any extensions supported for a given SCIM resource (e.g., "User"). It returns a subset of the information available from the general `/ResourceTypes` endpoint, focusing on a single resource type.

    Args:
        resource (str): Name of the SCIM resource type.
            - Example: "User"

    Returns:
        Optional[Dict[str, Any]]: None or the metadata describing the specified SCIM resource type. If found, it can contain the following keys:
            - schemas (List[str]): List of schema URIs this response adheres to.
            - id (str): Unique identifier for the resource type.
            - meta (Dict[str, str]):
                - resourceType (str): The SCIM resource type name.
                - location (str): URI for this specific resource type description.
            - name (str): Human-readable name of the resource.
            - description (str): Description of what the resource represents.
            - endpoint (str): Path to access this resource type (e.g., "/Users").
            - schema (str): URI of the primary schema used by this resource.
            - schemaExtensions (List[Dict[str, Any]]): List of schema extensions.
                - schema (str): URI of the extension schema.
                - required (bool): Indicates if this extension is mandatory.

    """

    for resource_type in db.DB["scim"]["resource_types"]:
        if resource_type.get("resource") == resource:
            return resource_type
    return None 