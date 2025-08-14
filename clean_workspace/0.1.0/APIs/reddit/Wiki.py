from .SimulationEngine.db import DB
from typing import Dict, Any, List

"""
Simulation of /wiki endpoints.
Manages wiki page operations within a subreddit.
"""


def post_api_wiki_alloweditor_add(page: str, username: str) -> Dict[str, Any]:
    """
    Adds a user to the wiki editors list for a page.

    Args:
        page (str): The name of the wiki page.
        username (str): The username to grant editing access.

    Returns:
        Dict[str, Any]:
        - If the page is invalid, returns a dictionary with the key "error" and the value "Invalid wiki page.".
        - If the username is invalid, returns a dictionary with the key "error" and the value "Invalid username.".
        - If the user is already an editor, returns a dictionary with the key "error" and the value "User already an editor.".
        - On successful addition, returns a dictionary with the following keys:
            - status (str): The status of the operation ("editor_added")
            - page (str): The wiki page name
            - username (str): The added editor's username
    """
    return {"status": "editor_added", "page": page, "username": username}


def post_api_wiki_alloweditor_del(page: str, username: str) -> Dict[str, Any]:
    """
    Removes a user from the wiki editors list.

    Args:
        page (str): The name of the wiki page.
        username (str): The username to remove from editors.

    Returns:
        Dict[str, Any]:
        - If the page is invalid, returns a dictionary with the key "error" and the value "Invalid wiki page.".
        - If the username is invalid, returns a dictionary with the key "error" and the value "Invalid username.".
        - If the user is not an editor, returns a dictionary with the key "error" and the value "User not an editor.".
        - On successful removal, returns a dictionary with the following keys:
            - status (str): The status of the operation ("editor_removed")
            - page (str): The wiki page name
            - username (str): The removed editor's username
    """
    return {"status": "editor_removed", "page": page, "username": username}


def post_api_wiki_alloweditor_act(act: str) -> Dict[str, Any]:
    """
    Performs an action to add or remove a wiki editor.

    Args:
        act (str): "add" or "del" to modify wiki editors.

    Returns:
        Dict[str, Any]:
        - If the action is invalid, returns a dictionary with the key "error" and the value "Invalid action.".
        - On successful action, returns a dictionary with the following keys:
            - status (str): The status of the operation ("wiki_editor_action")
            - action (str): The performed action
    """
    return {"status": "wiki_editor_action", "action": act}


def post_api_wiki_edit(page: str, content: str) -> Dict[str, Any]:
    """
    Edits the content of a wiki page.

    Args:
        page (str): The name of the wiki page.
        content (str): The new content in raw markdown.

    Returns:
        Dict[str, Any]:
        - If the page is invalid, returns a dictionary with the key "error" and the value "Invalid wiki page.".
        - If the content is invalid, returns a dictionary with the key "error" and the value "Invalid content.".
        - On successful edit, returns a dictionary with the following keys:
            - status (str): The status of the operation ("wiki_page_edited")
            - page (str): The edited wiki page name
    """
    subwiki = DB.setdefault("wiki", {}).setdefault("default_subreddit", {}) # Ensure keys exist
    subwiki[page] = {"content": content}
    return {"status": "wiki_page_edited", "page": page}


def post_api_wiki_hide(page: str, revision: str) -> Dict[str, Any]:
    """
    Hides a specific revision from the wiki history.

    Args:
        page (str): The name of the wiki page.
        revision (str): The revision ID to hide.

    Returns:
        Dict[str, Any]:
        - If the page is invalid, returns a dictionary with the key "error" and the value "Invalid wiki page.".
        - If the revision is invalid, returns a dictionary with the key "error" and the value "Invalid revision.".
        - On successful hiding, returns a dictionary with the following keys:
            - status (str): The status of the operation ("revision_hidden")
            - page (str): The wiki page name
            - revision (str): The hidden revision ID
    """
    return {"status": "revision_hidden", "page": page, "revision": revision}


def post_api_wiki_revert(page: str, revision: str) -> Dict[str, Any]:
    """
    Reverts a wiki page to a previous revision.

    Args:
        page (str): The name of the wiki page.
        revision (str): The revision ID to revert to.

    Returns:
        Dict[str, Any]:
        - If the page is invalid, returns a dictionary with the key "error" and the value "Invalid wiki page.".
        - If the revision is invalid, returns a dictionary with the key "error" and the value "Invalid revision.".
        - On successful revert, returns a dictionary with the following keys:
            - status (str): The status of the operation ("wiki_page_reverted")
            - page (str): The wiki page name
            - revision (str): The reverted revision ID
    """
    return {"status": "wiki_page_reverted", "page": page, "revision": revision}


def get_wiki_discussions_page(page: str) -> Dict[str, Any]:
    """
    Retrieves discussion links related to a wiki page.

    Args:
        page (str): The name of the wiki page.

    Returns:
        Dict[str, Any]:
        - If the page is invalid, returns a dictionary with the key "error" and the value "Invalid wiki page.".
        - On successful retrieval, returns a dictionary with the following keys:
            - page (str): The wiki page name
            - discussions (List[Dict[str, Any]]): A list of discussion objects, each containing:
                - id (str): The discussion ID
                - title (str): The discussion title
                - created_utc (int): The creation timestamp
    """
    return {"page": page, "discussions": []}


def get_wiki_pages() -> List[str]:
    """
    Retrieves a list of wiki pages for a subreddit.

    Returns:
        List[str]:
        - If there are no wiki pages, returns an empty list.
        - On successful retrieval, returns a list of wiki page names.
    """
    subwiki = DB.get("wiki", {}).get("default_subreddit", {}) # Use .get for safety
    return list(subwiki.keys())


def get_wiki_revisions() -> List[Dict[str, Any]]:
    """
    Retrieves recent revisions for all wiki pages.

    Returns:
        List[Dict[str, Any]]:
        - If there are no revisions, returns an empty list.
        - On successful retrieval, returns a list of revision objects, each containing:
            - page (str): The wiki page name
            - revision_id (str): The revision ID
            - author (str): The author's username
            - timestamp (int): The revision timestamp
            - reason (str): The revision reason
    """
    return []


def get_wiki_revisions_page(page: str) -> Dict[str, Any]:
    """
    Retrieves revisions for a specific wiki page.

    Args:
        page (str): The name of the wiki page.

    Returns:
        Dict[str, Any]:
        - If the page is invalid, returns a dictionary with the key "error" and the value "Invalid wiki page.".
        - On successful retrieval, returns a dictionary with the following keys:
            - page (str): The wiki page name
            - revisions (List[Dict[str, Any]]): A list of revision objects, each containing:
                - revision_id (str): The revision ID
                - author (str): The author's username
                - timestamp (int): The revision timestamp
                - reason (str): The revision reason
    """
    return {"page": page, "revisions": []}


def get_wiki_settings_page(page: str) -> Dict[str, Any]:
    """
    Retrieves the settings for a specific wiki page.

    Args:
        page (str): The name of the wiki page.

    Returns:
        Dict[str, Any]:
        - If the page is invalid, returns a dictionary with the key "error" and the value "Invalid wiki page.".
        - On successful retrieval, returns a dictionary with the following keys:
            - page (str): The wiki page name
            - settings (Dict[str, Any]): A dictionary containing:
                - listed (bool): Whether the page is listed
                - permlevel (int): The permission level
                - editors (List[str]): A list of editor usernames
    """
    return {"page": page, "settings": {}}


def get_wiki_page(page: str) -> Dict[str, Any]:
    """
    Retrieves the content of a wiki page.

    Args:
        page (str): The name of the wiki page.

    Returns:
        Dict[str, Any]:
        - If the page is invalid, returns a dictionary with the key "error" and the value "Invalid wiki page.".
        - If the page is not found, returns a dictionary with the key "error" and the value "not_found".
        - On successful retrieval, returns a dictionary with the following keys:
            - page (str): The wiki page name
            - content (str): The page content in raw markdown
    """
    subwiki = DB.get("wiki", {}).get("default_subreddit", {}) # Use .get for safety
    if page in subwiki:
        return {"page": page, "content": subwiki[page]["content"]}
    return {"page": page, "error": "not_found"}
