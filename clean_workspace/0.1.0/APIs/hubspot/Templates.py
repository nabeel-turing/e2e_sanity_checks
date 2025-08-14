# APIs/hubspot/Templates.py

from hubspot.SimulationEngine.db import DB
from hubspot.SimulationEngine.utils import generate_hubspot_object_id
from typing import Optional, Dict, Any, List
import time


def get_templates(
    limit: Optional[int] = 20,
    offset: Optional[int] = 0,
    deleted_at: Optional[str] = None,
    id: Optional[str] = None,
    is_available_for_new_content: Optional[str] = None,
    label: Optional[str] = None,
    path: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Get all templates. Supports paging and filtering.

    Args:
        limit (Optional[int]): The maximum number of templates to return. Default is 20.
        offset (Optional[int]): The offset of the first template to return. Default is 0.
        deleted_at (Optional[str]): Filter by deletion timestamp in milliseconds since epoch.
        id (Optional[str]): Filter by template ID.
        is_available_for_new_content (Optional[str]): Filter by availability for new content.
        label (Optional[str]): Filter by template label.
        path (Optional[str]): Filter by template path.

    Returns:
        List[Dict[str, Any]]: A list of template dictionaries. Each template has the following structure:
            - id (str): Unique identifier for the template.
            - category_id (int): Category type (0: Unmapped, 1: Landing Pages, 2: Email, 3: Blog Post, 4: Site Page).
            - folder (str): The folder where the template is saved.
            - template_type (int): Type of template (2: Email, 4: Page, 11: Error, etc.).
            - source (str): The source code of the template.
            - path (str): The path where the template is saved.
            - created (str): Creation timestamp in milliseconds since epoch.
            - deleted_at (str, optional): Deletion timestamp in milliseconds since epoch.
            - is_available_for_new_content (bool): Whether the template is available for new content.
            - archived (bool): Whether the template is archived.
            - versions (List[Dict[str, str]]): List of template versions.
                - source (str): The source code of this version.
                - version_id (str): The version identifier.
    """
    templates = list(DB.get("templates", {}).values())
    filtered_templates = []
    for template in templates:
        if deleted_at and template.get("deleted_at") != deleted_at:
            continue
        if id and template.get("id") != id:
            continue
        if (
            is_available_for_new_content
            and str(template.get("is_available_for_new_content"))
            != is_available_for_new_content
        ):
            continue
        if label and template.get("label") != label:
            continue
        if path and template.get("path") != path:
            continue
        filtered_templates.append(template)

    return filtered_templates[offset : offset + limit]


def create_template(
    source: str,
    created: Optional[str] = None,
    template_type: Optional[int] = 2,
    category_id: Optional[int] = 2,
    folder: Optional[str] = "/templates/",
    path: Optional[str] = "/home/templates/",
    is_available_for_new_content: Optional[bool] = False,
) -> Dict[str, Any]:
    """
    Create a new coded template object in Design Manager.

    Args:
        source (str): The source code of the template.
        created (Optional[str]): The creation date in milliseconds since epoch. Defaults to current time.
        template_type (Optional[int]): The type of template to create. Defaults to 2 (Email template).
            Valid values:
            - 2: Email template
            - 4: Page template
            - 11: Error template
            - 12: Subscription preferences template
            - 13: Backup unsubscribe page template
            - 14: Subscriptions update confirmation template
            - 19: Password prompt page template
            - 27: Search results template
            - 29: Membership login template
            - 30: Membership registration template
            - 31: Membership reset password confirmation template
            - 32: Membership reset password request template
        category_id (Optional[int]): The category type. Defaults to 2 (Email).
            Valid values:
            - 0: Unmapped
            - 1: Landing Pages
            - 2: Email
            - 3: Blog Post
            - 4: Site Page
        folder (Optional[str]): The folder to save the template. Defaults to '/templates/'.
        path (Optional[str]): The path to save the template. Defaults to '/home/templates/'.
        is_available_for_new_content (Optional[bool]): Whether the template should be available for new content. Defaults to False.

    Returns:
        Dict[str, Any]: The created template with the following structure:
            - id (str): Unique identifier for the template.
            - category_id (int): Category type.
            - folder (str): The folder where the template is saved.
            - template_type (int): Type of template.
            - source (str): The source code of the template.
            - path (str): The path where the template is saved.
            - created (str): Creation timestamp in milliseconds since epoch.
            - deleted_at (str, optional): Deletion timestamp in milliseconds since epoch.
            - is_available_for_new_content (bool): Whether the template is available for new content.
            - archived (bool): Whether the template is archived.
            - versions (List[Dict[str, str]]): List of template versions.
                - source (str): The source code of this version.
                - version_id (str): The version identifier.
    """
    template_id = str(generate_hubspot_object_id(source))

    counter = 0
    while template_id in DB.get("templates", {}):
        counter += 1
        template_id = str(int(template_id) + counter)

    # Create the new template
    new_template = {
        "id": template_id,
        "category_id": category_id,
        "folder": folder,
        "template_type": template_type,
        "source": source,
        "path": path,
        "created": created if created else str(int(time.time() * 1000)),
        "deleted_at": None,
        "is_available_for_new_content": is_available_for_new_content,
        "archived": False,
        "versions": [{"source": source, "version_id": "1"}],
    }
    if "templates" not in DB:
        DB["templates"] = {}
    DB["templates"][template_id] = new_template
    return new_template


def get_template_by_id(template_id: str) -> Dict[str, Any]:
    """
    Get a specific template by ID.

    Args:
        template_id (str): The unique identifier of the template.

    Returns:
        Dict[str, Any]: The template with the following structure:
            - id (str): Unique identifier for the template.
            - category_id (int): Category type.
            - folder (str): The folder where the template is saved.
            - template_type (int): Type of template.
            - source (str): The source code of the template.
            - path (str): The path where the template is saved.
            - created (str): Creation timestamp in milliseconds since epoch.
            - deleted_at (str, optional): Deletion timestamp in milliseconds since epoch.
            - is_available_for_new_content (bool): Whether the template is available for new content.
            - archived (bool): Whether the template is archived.
            - versions (List[Dict[str, str]]): List of template versions.
                - source (str): The source code of this version.
                - version_id (str): The version identifier.
    """
    return DB.get("templates", {}).get(template_id, {})


def update_template_by_id(
    template_id: str,
    category_id: Optional[int] = None,
    folder: Optional[str] = None,
    template_type: Optional[int] = None,
    source: Optional[str] = None,
    path: Optional[str] = None,
    created: Optional[str] = None,
    deleted_at: Optional[str] = None,
    is_available_for_new_content: Optional[bool] = None,
    archived: Optional[bool] = None,
    versions: Optional[List[Dict[str, str]]] = None,
) -> Dict[str, Any]:
    """
    Updates a template. If not all the fields are included in the body, we will only update the included fields.

    Args:
        template_id (str): Unique identifier for the template.
        category_id (Optional[int]): Category type (0: Unmapped, 1: Landing Pages, 2: Email, 3: Blog Post, 4: Site Page).
        folder (Optional[str]): The folder where the template is saved.
        template_type (Optional[int]): Type of template (2: Email, 4: Page, 11: Error, etc.).
        source (Optional[str]): The source code of the template.
        path (Optional[str]): The path where the template is saved.
        created (Optional[str]): Creation timestamp in milliseconds since epoch.
        deleted_at (Optional[str]): Deletion timestamp in milliseconds since epoch.
        is_available_for_new_content (Optional[bool]): Whether the template is available for new content.
        archived (Optional[bool]): Whether the template is archived.
        versions (Optional[List[Dict[str, str]]]): List of template versions.
            Each version should have:
            - source (str): The source code of this version.
            - version_id (str): The version identifier.

    Returns:
        Dict[str, Any]: The updated template with the following structure:
            - id (str): Unique identifier for the template.
            - category_id (int): Category type.
            - folder (str): The folder where the template is saved.
            - template_type (int): Type of template.
            - source (str): The source code of the template.
            - path (str): The path where the template is saved.
            - created (str): Creation timestamp in milliseconds since epoch.
            - deleted_at (str, optional): Deletion timestamp in milliseconds since epoch.
            - is_available_for_new_content (bool): Whether the template is available for new content.
            - archived (bool): Whether the template is archived.
            - versions (List[Dict[str, str]]): List of template versions.
                - source (str): The source code of this version.
                - version_id (str): The version identifier.

        If template is not found, returns:
            - error (str): Error message.
    """
    if template_id in DB.get("templates", {}):
        update_data = {}
        if category_id is not None:
            update_data["category_id"] = category_id
        if folder is not None:
            update_data["folder"] = folder
        if template_type is not None:
            update_data["template_type"] = template_type
        if source is not None:
            update_data["source"] = source
        if path is not None:
            update_data["path"] = path
        if created is not None:
            update_data["created"] = created
        if deleted_at is not None:
            update_data["deleted_at"] = deleted_at
        if is_available_for_new_content is not None:
            update_data["is_available_for_new_content"] = is_available_for_new_content
        if archived is not None:
            update_data["archived"] = archived
        if versions is not None:
            update_data["versions"] = versions

        DB["templates"][template_id].update(update_data)
        return DB["templates"][template_id]
    return {"error": "Template not found"}


def delete_template_by_id(template_id: str, deleted_at: Optional[str] = None) -> None:
    """
    Marks the selected Template as deleted. The Template can be restored later via a POST to the restore-deleted endpoint.

    Args:
        template_id (str): Unique identifier for the template.
        deleted_at (Optional[str]): Timestamp in milliseconds since epoch of when the template was deleted.
            If not provided, current timestamp will be used.

    Returns:
        None
    """
    if template_id in DB.get("templates", {}):
        DB["templates"][template_id]["deleted_at"] = (
            deleted_at if deleted_at else str(int(time.time() * 1000))
        )


def restore_deleted_template(template_id: str) -> Dict[str, Any]:
    """
    Restores a previously deleted Template.

    Args:
        template_id (str): Unique identifier for the template.

    Returns:
        Dict[str, Any]: The restored template with the following structure:
            - id (str): Unique identifier for the template.
            - category_id (int): Category type.
            - folder (str): The folder where the template is saved.
            - template_type (int): Type of template.
            - source (str): The source code of the template.
            - path (str): The path where the template is saved.
            - created (str): Creation timestamp in milliseconds since epoch.
            - deleted_at (str, optional): Set to None after restoration.
            - is_available_for_new_content (bool): Whether the template is available for new content.
            - archived (bool): Whether the template is archived.
            - versions (List[Dict[str, str]]): List of template versions.
                - source (str): The source code of this version.
                - version_id (str): The version identifier.

        If template is not found, returns:
            - error (str): Error message.
    """
    if template_id in DB.get("templates", {}):
        DB["templates"][template_id]["deleted_at"] = None
        return DB["templates"][template_id]
    return {"error": "Template not found"}
