"""
This module provides functionality for managing relationships between projects and supplier
companies using external identifiers in the Workday Strategic Sourcing system.
"""

from typing import Dict, List

from .SimulationEngine import db

def post(project_external_id: str, supplier_external_ids: List[str]) -> bool:
    """
    Adds one or more supplier companies to a project using external identifiers.

    Args:
        project_external_id (str): The external identifier of the project.
        supplier_external_ids (List[str]): A list of supplier company external IDs to add to the project.

    Returns:
        bool: True if the suppliers were successfully added to the project,
              False if the project doesn't exist.
    """
    for id, project in db.DB["projects"]["projects"].items():
        if project.get("external_id") == project_external_id:
            if "supplier_companies" not in db.DB["projects"]["projects"][id]:
                db.DB["projects"]["projects"][id]["supplier_companies"] = []
            db.DB["projects"]["projects"][id]["supplier_companies"].extend(supplier_external_ids)
            return True
    return False

def delete(project_external_id: str, supplier_external_ids: List[str]) -> bool:
    """
    Removes one or more supplier companies from a project using external identifiers.

    Args:
        project_external_id (str): The external identifier of the project.
        supplier_external_ids (List[str]): A list of supplier company external IDs to remove from the project.
                                          For optimal performance, it's recommended to remove 10 or fewer
                                          suppliers in a single request.

    Returns:
        bool: True if the suppliers were successfully removed from the project,
              False if the project doesn't exist or has no supplier companies.
    """
    for id, project in db.DB["projects"]["projects"].items():
        if project.get("external_id") == project_external_id and "supplier_companies" in db.DB["projects"]["projects"][id]:
            db.DB["projects"]["projects"][id]["supplier_companies"] = [
                sid for sid in db.DB["projects"]["projects"][id]["supplier_companies"] if sid not in supplier_external_ids
            ]
            return True
    return False 