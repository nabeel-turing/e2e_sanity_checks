"""
NotesAndLists API functions

This module provides the main API functions for the NotesAndLists service.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from .SimulationEngine.db import DB
from .SimulationEngine.models import ListItem, ListModel, Note, OperationLog
from .SimulationEngine.utils import get_list, get_note, get_list_item, update_content_index, maintain_list_item_history, remove_from_indexes, update_title_index, find_items_by_search
from .SimulationEngine.custom_errors import ListNotFoundError, ListItemNotFoundError, NotFoundError, OperationNotFoundError, UnsupportedOperationError, NoteNotFoundError, ValidationError
import copy
import uuid
import builtins

def delete_notes_and_lists(search_term: Optional[str] = None, query: Optional[str] = None, query_expansion: Optional[List[str]] = None, item_ids: Optional[List[str]] = None, item_id: Optional[str] = None) -> Dict[str, Any]:
    """
    This can be used to delete lists and/or notes.

    This function allows deletion of notes and lists by searching through various 
    methods including search terms, queries, query expansion, or direct item IDs.
    
    Args:
        search_term (Optional[str]): The name of the lists or notes, or keywords to 
            search for the lists or notes. Defaults to None.
        query (Optional[str]): Optional query to be used for searching notes and lists 
            items. This should not be set if the title is not specified. Defaults to None.
        query_expansion (Optional[List[str]]): Optional search query expansion using 
            synonyms or related terms. Defaults to None.
        item_ids (Optional[List[str]]): The IDs of the notes and/or lists to delete. 
            If available from the context, use this instead of search_term. Defaults to None.
        item_id (Optional[str]): The id of note or list which is to be deleted. 
            Defaults to None.

    Returns:
        Dict[str, Any]: A NotesAndListsResult object containing the IDs of the deleted 
            lists and/or notes with the following structure:
            - notes (List[Dict[str, Any]]): List of deleted notes containing:
                - id (str): The unique identifier of the note.
                - title (Optional[str]): The title of the note.
                - content (str): The content of the note.
                - created_at (str): The creation timestamp in ISO 8601 format.
                - updated_at (str): The last update timestamp in ISO 8601 format.
                - content_history (List[str]): List of previous content versions.
            - lists (List[Dict[str, Any]]): List of deleted lists containing:
                - id (str): The unique identifier of the list.
                - title (Optional[str]): The title of the list.
                - items (Dict[str, Dict[str, Any]]): Dictionary of list items where 
                    each item contains:
                    - id (str): The unique identifier of the item.
                    - content (str): The content of the item.
                    - created_at (str): The creation timestamp in ISO 8601 format.
                    - updated_at (str): The last update timestamp in ISO 8601 format.
                - created_at (str): The creation timestamp in ISO 8601 format.
                - updated_at (str): The last update timestamp in ISO 8601 format.
                - item_history (Dict[str, List[str]]): Dictionary mapping item IDs 
                    to their content history.

    Raises:
        TypeError: If search_term is not a string or None, if query is not a string or None, if query_expansion is not a list of strings or None, if item_ids is not a list of strings or None, or if item_id is not a string or None.
        ValueError: If search_term is empty or whitespace-only, if query is empty or whitespace-only, if query_expansion is an empty list, if query_expansion contains empty or whitespace-only strings, if item_ids is an empty list, if item_ids contains empty or whitespace-only strings, or if item_id is empty or whitespace-only.
        ValidationError: If parameters do not conform to the expected structure.
    """
    # Input validation
    
    # Validate search_term parameter
    if search_term is not None:
        if not isinstance(search_term, str):
            raise TypeError("search_term is not a string or None")
        if not search_term.strip():
            raise ValueError("search_term is empty or whitespace-only")
    
    # Validate query parameter
    if query is not None:
        if not isinstance(query, str):
            raise TypeError("query is not a string or None")
        if not query.strip():
            raise ValueError("query is empty or whitespace-only")
    
    # Validate query_expansion parameter
    if query_expansion is not None:
        if not isinstance(query_expansion, list):
            raise TypeError("query_expansion is not a list of strings or None")
        if not all(isinstance(term, str) for term in query_expansion):
            raise TypeError("query_expansion is not a list of strings or None")
        if len(query_expansion) == 0:
            raise ValueError("query_expansion is an empty list")
        if any(not term.strip() for term in query_expansion):
            raise ValueError("query_expansion contains empty or whitespace-only strings")
    
    # Validate item_ids parameter
    if item_ids is not None:
        if not isinstance(item_ids, list):
            raise TypeError("item_ids is not a list of strings or None")
        if not all(isinstance(item_id, str) for item_id in item_ids):
            raise TypeError("item_ids is not a list of strings or None")
        if len(item_ids) == 0:
            raise ValueError("item_ids is an empty list")
        if any(not item_id.strip() for item_id in item_ids):
            raise ValueError("item_ids contains empty or whitespace-only strings")
    
    # Validate item_id parameter
    if item_id is not None:
        if not isinstance(item_id, str):
            raise TypeError("item_id is not a string or None")
        if not item_id.strip():
            raise ValueError("item_id is empty or whitespace-only")
    
    # Initialize sets to collect unique items to delete
    notes_to_delete = set()
    lists_to_delete = set()
    
    # Handle direct deletion by item_ids
    if item_ids is not None:
        for target_id in item_ids:
            # Check if it's a note
            if target_id in DB["notes"]:
                notes_to_delete.add(target_id)
            # Check if it's a list
            elif target_id in DB["lists"]:
                lists_to_delete.add(target_id)
    
    # Handle direct deletion by single item_id
    if item_id is not None:
        # Check if it's a note
        if item_id in DB["notes"]:
            notes_to_delete.add(item_id)
        # Check if it's a list
        elif item_id in DB["lists"]:
            lists_to_delete.add(item_id)
    
    
    # Handle deletion by search_term
    elif search_term is not None:
        found_notes, found_lists = find_items_by_search(search_term)
        notes_to_delete.update(found_notes)
        lists_to_delete.update(found_lists)
    
    # Handle deletion by query
    elif query is not None:
        found_notes, found_lists = find_items_by_search(query)
        notes_to_delete.update(found_notes)
        lists_to_delete.update(found_lists)
    
    # Handle deletion by query_expansion
    elif query_expansion is not None:
        for expansion_term in query_expansion:
            found_notes, found_lists = find_items_by_search(expansion_term)
            notes_to_delete.update(found_notes)
            lists_to_delete.update(found_lists)
    
    # Collect items before deletion for return
    deleted_notes = []
    deleted_lists = []
    
    # Collect notes to be deleted
    for note_id in notes_to_delete:
        if note_id in DB["notes"]:
            note = DB["notes"][note_id].copy()
            deleted_notes.append(note)
    
    # Collect lists to be deleted  
    for list_id in lists_to_delete:
        if list_id in DB["lists"]:
            lst = DB["lists"][list_id].copy()
            deleted_lists.append(lst)
    
    # Actually delete the items from the database
    for note_id in notes_to_delete:
        if note_id in DB["notes"]:
            del DB["notes"][note_id]
            
            # Remove from title index
            for title, ids in list(DB["title_index"].items()):
                if note_id in ids:
                    DB["title_index"][title].remove(note_id)
                    if not DB["title_index"][title]:
                        del DB["title_index"][title]
            
            # Remove from content index
            for keyword, ids in list(DB["content_index"].items()):
                if note_id in ids:
                    DB["content_index"][keyword].remove(note_id)
                    if not DB["content_index"][keyword]:
                        del DB["content_index"][keyword]
    
    for list_id in lists_to_delete:
        if list_id in DB["lists"]:
            del DB["lists"][list_id]
            
            # Remove from title index
            for title, ids in list(DB["title_index"].items()):
                if list_id in ids:
                    DB["title_index"][title].remove(list_id)
                    if not DB["title_index"][title]:
                        del DB["title_index"][title]
            
            # Remove from content index
            for keyword, ids in list(DB["content_index"].items()):
                if list_id in ids:
                    DB["content_index"][keyword].remove(list_id)
                    if not DB["content_index"][keyword]:
                        del DB["content_index"][keyword]
    
    # Return the NotesAndListsResult structure with deleted items
    return {
        "notes": deleted_notes,
        "lists": deleted_lists
    }

def delete_list_item(search_term: Optional[str] = None, query: Optional[str] = None, query_expansion: Optional[List[str]] = None, list_id: Optional[str] = None, elements_to_delete: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    This can be used to delete items in a notes and lists list.

    This function allows deletion of specific items from lists by searching for lists 
    through various methods or by direct list ID, and then deleting specified items 
    by their IDs or through search criteria.
    
    Args:
        search_term (Optional[str]): The name of the list or keywords to search for 
            the list. Defaults to None.
        query (Optional[str]): Optional query to be used for searching notes and lists 
            items. This should not be set if the title is not specified. Defaults to None.
        query_expansion (Optional[List[str]]): Optional search query expansion using 
            synonyms or related terms. Defaults to None.
        list_id (Optional[str]): The id of list which contains the items to be deleted. 
            Defaults to None.
        elements_to_delete (Optional[List[str]]): The ids of list items to be deleted. 
            Defaults to None.

    Returns:
        Dict[str, Any]: A ListResult object containing the updated list information 
            with the following structure:
            - id (str): The unique identifier of the list.
            - title (Optional[str]): The title of the list.
            - items (Dict[str, Dict[str, Any]]): Dictionary of remaining list items where 
                each item contains:
                - id (str): The unique identifier of the item.
                - content (str): The content of the item.
                - created_at (str): The creation timestamp in ISO 8601 format.
                - updated_at (str): The last update timestamp in ISO 8601 format.
            - created_at (str): The creation timestamp in ISO 8601 format.
            - updated_at (str): The last update timestamp in ISO 8601 format.
            - item_history (Dict[str, List[str]]): Dictionary mapping item IDs 
                to their content history.
            - deleted_items (List[Dict[str, Any]]): List of deleted items containing:
                - id (str): The unique identifier of the deleted item.
                - content (str): The content of the deleted item.
                - created_at (str): The creation timestamp in ISO 8601 format.
                - updated_at (str): The last update timestamp in ISO 8601 format.

    Raises:
        TypeError: If search_term is not a string or None, if query is not a string or None, if query_expansion is not a list of strings or None, if list_id is not a string or None, or if elements_to_delete is not a list of strings or None.
        ValueError: If search_term is empty or whitespace-only, if query is empty or whitespace-only, if query_expansion is an empty list, if query_expansion contains empty or whitespace-only strings, if list_id is empty or whitespace-only, if elements_to_delete is an empty list, if elements_to_delete contains empty or whitespace-only strings, or if no list is found matching the search criteria.
        ValidationError: If parameters do not conform to the expected structure.
    """
    # Input validation
    
    # Validate search_term parameter
    if search_term is not None:
        if not isinstance(search_term, str):
            raise TypeError("search_term is not a string or None")
        if not search_term.strip():
            raise ValueError("search_term is empty or whitespace-only")
    
    # Validate query parameter
    if query is not None:
        if not isinstance(query, str):
            raise TypeError("query is not a string or None")
        if not query.strip():
            raise ValueError("query is empty or whitespace-only")
    
    # Validate query_expansion parameter
    if query_expansion is not None:
        if not isinstance(query_expansion, list):
            raise TypeError("query_expansion is not a list of strings or None")
        if not all(isinstance(term, str) for term in query_expansion):
            raise TypeError("query_expansion is not a list of strings or None")
        if len(query_expansion) == 0:
            raise ValueError("query_expansion is an empty list")
        if any(not term.strip() for term in query_expansion):
            raise ValueError("query_expansion contains empty or whitespace-only strings")
    
    # Validate list_id parameter
    if list_id is not None:
        if not isinstance(list_id, str):
            raise TypeError("list_id is not a string or None")
        if not list_id.strip():
            raise ValueError("list_id is empty or whitespace-only")
    
    # Validate elements_to_delete parameter
    if elements_to_delete is not None:
        if not isinstance(elements_to_delete, list):
            raise TypeError("elements_to_delete is not a list of strings or None")
        if not all(isinstance(element_id, str) for element_id in elements_to_delete):
            raise TypeError("elements_to_delete is not a list of strings or None")
        if len(elements_to_delete) == 0:
            raise ValueError("elements_to_delete is an empty list")
        if any(not element_id.strip() for element_id in elements_to_delete):
            raise ValueError("elements_to_delete contains empty or whitespace-only strings")
    
    # Find the target list
    target_list_id = None
    target_list = None
    
    # Method 1: Direct lookup by list_id
    if list_id is not None:
        if list_id in DB["lists"]:
            target_list_id = list_id
            target_list = DB["lists"][list_id]
        else:
            raise ValueError("no list is found matching the search criteria")
    
    # Method 2: Search-based lookup
    elif search_term is not None or query is not None or query_expansion is not None:
        # Helper function to search for lists
        def find_list_by_search(search_text: str) -> Optional[str]:
            """Find the first list matching the search text"""
            search_lower = search_text.lower()
            
            for lst_id, lst in DB["lists"].items():
                # Search in title
                title_match = lst.get("title") and search_lower in lst["title"].lower()
                
                # Search in list items content
                item_match = any(
                    search_lower in item["content"].lower()
                    for item in lst["items"].values()
                )
                
                if title_match or item_match:
                    return lst_id
            
            return None
        
        # Search by search_term
        if search_term is not None:
            target_list_id = find_list_by_search(search_term)
            if target_list_id:
                target_list = DB["lists"][target_list_id]
        
        # Search by query (if not found yet)
        if target_list_id is None and query is not None:
            target_list_id = find_list_by_search(query)
            if target_list_id:
                target_list = DB["lists"][target_list_id]
        
        # Search by query_expansion (if not found yet)
        if target_list_id is None and query_expansion is not None:
            for expansion_term in query_expansion:
                target_list_id = find_list_by_search(expansion_term)
                if target_list_id:
                    target_list = DB["lists"][target_list_id]
                    break
        
        # If no list found through search
        if target_list_id is None:
            # If elements_to_delete provided, this is an error (can't delete from non-existent list)
            if elements_to_delete is not None:
                raise ValueError("no list is found matching the search criteria")
            # Otherwise return empty result
            return {
                "id": None,
                "title": None,
                "items": {},
                "created_at": None,
                "updated_at": None,
                "item_history": {},
                "deleted_items": []
            }
    
    # Method 3: No search criteria provided - return empty result structure
    else:
        return {
            "id": None,
            "title": None,
            "items": {},
            "created_at": None,
            "updated_at": None,
            "item_history": {},
            "deleted_items": []
        }
    
    # Collect items to be deleted
    deleted_items = []
    items_to_remove = set()
    processed_items = set()  # Track items already processed to avoid duplicates
    
    if elements_to_delete is not None:
        for element_id in elements_to_delete:
            if element_id in target_list["items"] and element_id not in processed_items:
                # Collect the item data before deletion
                item_data = target_list["items"][element_id].copy()
                deleted_items.append(item_data)
                items_to_remove.add(element_id)
                processed_items.add(element_id)
    
    # Actually delete the items from the list
    for item_id in items_to_remove:
        if item_id in target_list["items"]:
            del target_list["items"][item_id]
            
            # Remove from content index if present
            for keyword, ids in list(DB["content_index"].items()):
                if item_id in ids:
                    DB["content_index"][keyword].remove(item_id)
                    if not DB["content_index"][keyword]:
                        del DB["content_index"][keyword]
    
    # Update the list's updated_at timestamp
    current_time = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    target_list["updated_at"] = current_time
    
    
    # Prepare the return structure (ListResult with deleted_items)
    result = target_list.copy()
    result["deleted_items"] = deleted_items
    
    return result

def show_notes_and_lists(item_ids: Optional[List[str]] = None, query: Optional[str] = None) -> Dict[str, Any]:
    """
    Use this function to display specific notes or lists.

    This function performs an implicit search to find the relevant items, so you 
    don't need to call search_notes_and_lists before using it. You can either 
    specify exact item IDs or provide a search query to find relevant notes and lists.
    
    Args:
        item_ids (Optional[List[str]]): The IDs of the notes and/or lists to show. 
            Use this if you know the IDs from previous interactions. Defaults to None.
        query (Optional[str]): A query to search for the notes and lists. Use this 
            if you don't know the IDs of the specific items. Defaults to None.

    Returns:
        Dict[str, Any]: A NotesAndListsResult object containing the details of the 
            specified notes and/or lists with the following structure:
            - notes (List[Dict[str, Any]]): List of matching notes containing:
                - id (str): The unique identifier of the note.
                - title (Optional[str]): The title of the note.
                - content (str): The content of the note.
                - created_at (str): The creation timestamp in ISO 8601 format.
                - updated_at (str): The last update timestamp in ISO 8601 format.
                - content_history (List[str]): List of previous content versions.
            - lists (List[Dict[str, Any]]): List of matching lists containing:
                - id (str): The unique identifier of the list.
                - title (Optional[str]): The title of the list.
                - items (Dict[str, Dict[str, Any]]): Dictionary of list items where 
                    each item contains:
                    - id (str): The unique identifier of the item.
                    - content (str): The content of the item.
                    - created_at (str): The creation timestamp in ISO 8601 format.
                    - updated_at (str): The last update timestamp in ISO 8601 format.
                - created_at (str): The creation timestamp in ISO 8601 format.
                - updated_at (str): The last update timestamp in ISO 8601 format.
                - item_history (Dict[str, List[str]]): Dictionary mapping item IDs 
                    to their content history.

    Raises:
        TypeError: If item_ids is not a list of strings or None, or if query is not a string or None.
        ValueError: If no valid item_ids or query is provided, or if specified item_ids are not found.
    """
    # Input validation
    
    # Validate item_ids parameter
    if item_ids is not None:
        if not isinstance(item_ids, list):
            raise TypeError("item_ids must be a list of strings or None")
        if not all(isinstance(item_id, str) for item_id in item_ids):
            raise TypeError("item_ids must be a list of strings or None")
        if len(item_ids) == 0:
            raise ValueError("item_ids cannot be an empty list")
        if any(not item_id.strip() for item_id in item_ids):
            raise ValueError("item_ids cannot contain empty or whitespace-only strings")
    
    # Validate query parameter
    if query is not None:
        if not isinstance(query, str):
            raise TypeError("query must be a string or None")
        if not query.strip():
            raise ValueError("query cannot be empty or whitespace-only")
    
    # Validate that at least one parameter is provided
    if item_ids is None and query is None:
        raise ValueError("At least one of item_ids or query must be provided")
    
    # Initialize result structure
    result = {
        "notes": [],
        "lists": []
    }
    
    # Track found items to avoid duplicates
    found_note_ids = set()
    found_list_ids = set()
    
    # Process item_ids parameter - find specific items by ID
    if item_ids is not None:
        for item_id in item_ids:
            # Check if it's a note
            if item_id in DB["notes"]:
                if item_id not in found_note_ids:
                    note_data = DB["notes"][item_id].copy()
                    result["notes"].append(note_data)
                    found_note_ids.add(item_id)
            
            # Check if it's a list
            elif item_id in DB["lists"]:
                if item_id not in found_list_ids:
                    list_data = DB["lists"][item_id].copy()
                    result["lists"].append(list_data)
                    found_list_ids.add(item_id)
    
    # Process query parameter - search functionality
    elif query is not None:
        query_lower = query.lower()
        
        # Search notes by title first, then content if title doesn't match
        for note_id, note_data in DB["notes"].items():
            if note_id not in found_note_ids:
                # Check title first (case-insensitive)
                title_match = (note_data.get("title") and 
                             query_lower in note_data["title"].lower())
                
                if title_match:
                    # Title matches, include note without checking content
                    result["notes"].append(note_data.copy())
                    found_note_ids.add(note_id)
                else:
                    # Title doesn't match, check content (case-insensitive)
                    content_match = query_lower in note_data["content"].lower()
                    if content_match:
                        result["notes"].append(note_data.copy())
                        found_note_ids.add(note_id)
        
        # Search lists by title first, then item content if title doesn't match
        for list_id, list_data in DB["lists"].items():
            if list_id not in found_list_ids:
                # Check list title first (case-insensitive)
                title_match = (list_data.get("title") and 
                              query_lower in list_data["title"].lower())
                
                if title_match:
                    # Title matches, include list without checking item content
                    result["lists"].append(list_data.copy())
                    found_list_ids.add(list_id)
                else:
                    # Title doesn't match, check list items content (case-insensitive)
                    content_match = False
                    if "items" in list_data:
                        for item_data in list_data["items"].values():
                            if query_lower in item_data["content"].lower():
                                content_match = True
                                break
                    
                    if content_match:
                        result["lists"].append(list_data.copy())
                        found_list_ids.add(list_id)
    
    return result

def update_list_item(
    list_id: Optional[str],
    list_item_id: str,
    updated_element: str,
    search_term: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Updates an existing item in a specified list.

    Args:
        list_id (Optional[str]): The ID of the list containing the item.
        list_item_id (str): The ID of the list item to update.
        updated_element (str): The new content for the list item.
        search_term (Optional[str]): A search term to find the list if the ID is not known.

    Returns:
        Dict[str, Any]: A dictionary representing the updated list.

    Raises:
        ValueError: If required arguments are missing or invalid.
        ListNotFoundError: If the specified list cannot be found.
        ListItemNotFoundError: If the specified list item cannot be found.
    """
    if not list_item_id or not isinstance(list_item_id, str):
        raise ValueError("A valid 'list_item_id' (string) is required.")
    if not updated_element or not isinstance(updated_element, str):
        raise ValueError("A valid 'updated_element' (string) is required.")

    target_list = None
    if list_id:
        if not isinstance(list_id, str):
            raise ValueError("'list_id' must be a string.")
        target_list = get_list(list_id)
    elif search_term:
        if not isinstance(search_term, str):
            raise ValueError("'search_term' must be a string.")
        # Simple search through lists
        search_term_lower = search_term.lower()
        for list_data in DB["lists"].values():
            # Check list title first
            title_match = (list_data.get("title") and 
                          search_term_lower in list_data["title"].lower())
            if title_match:
                target_list = list_data
                break
            # Check list items content if title doesn't match
            for item_data in list_data.get("items", {}).values():
                if search_term_lower in item_data["content"].lower():
                    target_list = list_data
                    break
            if target_list:
                break
    
    if not target_list:
        raise ListNotFoundError(f"No list found with the provided criteria.")

    list_id = target_list["id"]
    item_to_update = get_list_item(list_id, list_item_id)

    if not item_to_update:
        raise ListItemNotFoundError(f"List item '{list_item_id}' not found in list '{list_id}'.")

    old_content = item_to_update["content"]
    current_time = datetime.utcnow().isoformat() + "Z"

    item_to_update["content"] = updated_element
    item_to_update["updated_at"] = current_time
    
    maintain_list_item_history(list_id, list_item_id, old_content)
    update_content_index(list_item_id, updated_element)

    target_list["updated_at"] = current_time

    return target_list

def share_notes_and_lists(options: Optional[Dict[str, Any]] = None) -> None:
    """
    This function is not supported.
    
    Args:
        options (Optional[Dict[str, Any]]): An optional dictionary of parameters.
    
    Raises:
        UnsupportedOperationError: Always, as this feature is not implemented.
    """
    raise UnsupportedOperationError("'share_notes_and_lists' is not supported.")

def undo(undo_operation_ids: List[str]) -> str:
    """
    Reverts one or more previous operations based on their IDs.

    Args:
        undo_operation_ids (List[str]): A list of operation IDs to be undone.

    Returns:
        str: A message confirming the successful reversal of the operations.

    Raises:
        ValueError: If `undo_operation_ids` is empty or invalid.
        OperationNotFoundError: If an operation ID does not correspond to a logged operation.
    """
    if not undo_operation_ids or not isinstance(undo_operation_ids, list):
        raise ValueError("A non-empty list of 'undo_operation_ids' is required.")

    undone_count = 0
    for op_id in undo_operation_ids:
        operation = DB["operation_log"].get(op_id)
        if not operation:
            raise OperationNotFoundError(f"Operation with ID '{op_id}' not found.")

        op_type = operation["operation_type"]
        target_id = operation["target_id"]
        snapshot = operation.get("snapshot")

        if snapshot:
            # Determine if the snapshot is a note or a list
            is_note = "content" in snapshot and "content_history" in snapshot
            is_list = "items" in snapshot and "item_history" in snapshot

            if is_note:
                DB["notes"][target_id] = copy.deepcopy(snapshot)
                update_title_index(snapshot.get("title"), target_id)
                update_content_index(target_id, snapshot.get("content", ""))
            elif is_list:
                DB["lists"][target_id] = copy.deepcopy(snapshot)
                update_title_index(snapshot.get("title"), target_id)
                for item_id, item in snapshot.get("items", {}).items():
                    update_content_index(item_id, item.get("content", ""))
            else:
                raise ValueError(f"Snapshot for operation '{op_id}' has an unrecognized structure.")

        elif op_type in ["create_note", "create_list"]:
            if op_type == "create_note" and target_id in DB["notes"]:
                del DB["notes"][target_id]
            elif op_type == "create_list" and target_id in DB["lists"]:
                del DB["lists"][target_id]
            remove_from_indexes(target_id)
        
        else:
            raise ValueError(f"Cannot undo operation '{op_id}' of type '{op_type}' without a snapshot.")

        del DB["operation_log"][op_id]
        undone_count += 1


    return f"Successfully undid {undone_count} operation(s)."

def update_title(
        search_term: Optional[str] = None, 
        query: Optional[str] = None, 
        query_expansion: Optional[List[str]] = None, 
        item_id: Optional[str] = None, 
        updated_title: Optional[str] = None
        ) -> Dict[str, Any]:
    """This can be used to update the title of an existing list or note.

    This function updates the title of an existing list or note. 
    It can identify the target item using a search term, a more specific query, or a direct item ID.

    Args:
        search_term (Optional[str]): The name of the note or list. or keywords to search for the note or list.
        query (Optional[str]): Optional query to be used for searching notes and lists items. This should not be set if the title is not specified.
        query_expansion (Optional[List[str]]): Optional search query expansion using synonyms or related terms.
        item_id (Optional[str]): The id of the note or list to be updated. If available from the context, use this instead of search_term.
        updated_title (Optional[str]): The updated title of the notes and lists item.

    Returns:
        Dict[str, Any]: A dictionary containing information of the updated lists and/or notes. It contains the following keys:
            - notes_and_lists_items (List[Dict[str, Any]]): A list of dictionaries containing information of the updated lists and/or notes. It contains the following keys:
                - item_id (str): The unique identifier of the list or note.
                - title (str): The title of the list or note.
                - note_content (Optional[Dict[str, str]]): The note content of the list or note. It contains the following keys:
                    - text_content (str): The text content of the note.
                - list_content (Optional[Dict[str, any]]): The list content of the list or note. It contains the following keys:
                    - items (List[Dict[str, any]]): The items of the list. It contains the following keys:
                        - id (str): The unique identifier of the item.
                        - content (str): The text content of the item.
                - deep_link_url (str): The deep link URL of the list or note. TODO: Add deep link url

    Raises:
        TypeError: If input arguments are not of the correct type.
        NotFoundError: If the note or list is not found.
        ValueError: If input arguments fail validation.
    """
    # --- Argument Type Validation ---
    if item_id is not None and not isinstance(item_id, str):
        raise TypeError("Argument 'item_id' must be a string.")
    if search_term is not None and not isinstance(search_term, str):
        raise TypeError("Argument 'search_term' must be a string.")
    if query is not None and not isinstance(query, str):
        raise TypeError("Argument 'query' must be a string.")
    if query_expansion is not None:
        if not isinstance(query_expansion, list) or not all(isinstance(s, str) for s in query_expansion):
            raise TypeError("Argument 'query_expansion' must be a list of strings.")
    if updated_title is not None and not isinstance(updated_title, str):
        raise TypeError("Argument 'updated_title' must be a string.")
    

    # Validate that at least one identifier is provided
    if not item_id and not search_term and not query:
        raise ValueError("Either 'item_id', 'search_term', 'query', or 'query_expansion' must be provided to identify the item to update.")

    # Validate that an updated title is provided and is not empty
    if not updated_title or not updated_title.strip():
        raise ValueError("'updated_title' must be provided and cannot be empty.")

    notes_and_lists = list(DB.get('notes', {}).values()) + list(DB.get('lists', {}).values())

    # Find the item to update
    notes_and_lists_items = []
    notes_and_lists_items_ids = set()

    if item_id:
        for item in DB.get('notes', {}).values():
            if item.get('id') == item_id:
                if item_id not in notes_and_lists_items_ids:    
                    # Take snapshot before update for undo functionality
                    from .SimulationEngine.models import OperationLog
                    op_log = OperationLog(
                        operation_type="update_title",
                        target_id=item_id,
                        parameters={"updated_title": updated_title},
                        snapshot=copy.deepcopy(item)
                    )
                    if "operation_log" not in DB:
                        DB["operation_log"] = {}
                    DB["operation_log"][op_log.id] = op_log.model_dump()
                    
                    # Update the title
                    old_title = item.get('title', '')
                    DB['notes'][item_id]['title'] = updated_title
                    
                    # Update title index
                    update_title_index(updated_title, item_id)
                    
                    notes_and_lists_items.append({
                        'id' : item_id,
                        'title' : updated_title,
                        'note_content' : {
                            'content' : item.get('content', '')
                        },
                        'deep_link_url' : '' # TODO: Add deep link url
                    })
                    notes_and_lists_items_ids.add(item_id)

        for item in DB.get('lists', {}).values():
            if item.get('id') == item_id:
                if item_id not in notes_and_lists_items_ids:
                    # Take snapshot before update for undo functionality
                    from .SimulationEngine.models import OperationLog
                    op_log = OperationLog(
                        operation_type="update_title",
                        target_id=item_id,
                        parameters={"updated_title": updated_title},
                        snapshot=copy.deepcopy(item)
                    )
                    if "operation_log" not in DB:
                        DB["operation_log"] = {}
                    DB["operation_log"][op_log.id] = op_log.model_dump()
                    
                    # Update the title
                    old_title = item.get('title', '')
                    DB['lists'][item_id]['title'] = updated_title
                    
                    # Update title index
                    update_title_index(updated_title, item_id)
                    
                    notes_and_lists_items.append({
                        'id' : item_id,
                        'title' : updated_title,
                        'list_content' : {
                            'items' : list(item.get('items', {}).values())
                        },
                        'deep_link_url' : '' # TODO: Add deep link url
                    })
                    notes_and_lists_items_ids.add(item_id)
    else:
        # Fallback to searching by search_term and other query parameters
        search_keywords = set()
        if search_term:
            search_keywords.add(search_term.lower())
        if query:
            search_keywords.add(query.lower())
        if query_expansion:
            search_keywords.update(term.lower() for term in query_expansion)

        for item in DB.get('notes', {}).values():
            if any(term in item.get('title', '').lower() or term in item.get('text_content', '').lower() for term in search_keywords):
                if item.get('id') not in notes_and_lists_items_ids:   
                        # Take snapshot before update for undo functionality
                        from .SimulationEngine.models import OperationLog
                        op_log = OperationLog(
                            operation_type="update_title",
                            target_id=item.get('id'),
                            parameters={"updated_title": updated_title},
                            snapshot=copy.deepcopy(item)
                        )
                        if "operation_log" not in DB:
                            DB["operation_log"] = {}
                        DB["operation_log"][op_log.id] = op_log.model_dump()
                        
                        # Update the title
                        old_title = item.get('title', '')
                        DB['notes'][item.get('id')]['title'] = updated_title
                        
                        # Update title index
                        update_title_index(updated_title, item.get('id'))
                        
                        notes_and_lists_items.append({
                            'id' : item.get('id'),
                            'title' : updated_title,
                            'note_content' : {
                                'content' : item.get('content', '')
                            },
                            'deep_link_url' : '' # TODO: Add deep link url
                        })
                        notes_and_lists_items_ids.add(item.get('id'))

        for item in DB.get('lists', {}).values():
            if any(term in item.get('title', '').lower() for term in search_keywords):
                if item.get('id') not in notes_and_lists_items_ids:
                    # Take snapshot before update for undo functionality
                    from .SimulationEngine.models import OperationLog
                    op_log = OperationLog(
                        operation_type="update_title",
                        target_id=item.get('id'),
                        parameters={"updated_title": updated_title},
                        snapshot=copy.deepcopy(item)
                    )
                    if "operation_log" not in DB:
                        DB["operation_log"] = {}
                    DB["operation_log"][op_log.id] = op_log.model_dump()
                    
                    # Update the title
                    old_title = item.get('title', '')
                    DB['lists'][item.get('id')]['title'] = updated_title
                    
                    # Update title index
                    update_title_index(updated_title, item.get('id'))
                    
                    notes_and_lists_items.append({
                        'id' : item.get('id'),
                        'title' : updated_title,
                        'list_content' : {
                            'items' : list(item.get('items', {}).values())
                        },
                        'deep_link_url' : '' # TODO: Add deep link url
                    })
                    notes_and_lists_items_ids.add(item.get('id'))

    return {
        'notes_and_lists_items' : notes_and_lists_items
    }


def show_all(hint: Optional[str] = None) -> Dict[str, Any]:
    """
    Displays all notes or lists based on the provided hint.

    This function retrieves all notes and/or lists from the database and returns
    them in a structured format. The details of the items are provided through
    a side channel, eliminating the need to call show_notes_and_lists after this function.

    Args:
        hint (Optional[str]): The type of item to show. Can be:
            - "LIST": Show only lists
            - "NOTE": Show only notes  
            - "ANY": Show both notes and lists
            - None: Show both notes and lists (default behavior)

    Returns:
        Dict[str, Any]: A NotesAndListsResult object containing:
            - notes (List[Dict[str, Any]]): List of note objects, each containing:
                - id (str): The unique identifier of the note
                - title (Optional[str]): The title of the note
                - content (str): The content of the note
                - created_at (str): The creation timestamp in ISO format
                - updated_at (str): The last update timestamp in ISO format
                - content_history (List[str]): List of previous content versions
            - lists (List[Dict[str, Any]]): List of list objects, each containing:
                - id (str): The unique identifier of the list
                - title (Optional[str]): The title of the list
                - items (Dict[str, Dict[str, Any]]): Dictionary of list items, each containing:
                    - id (str): The unique identifier of the item
                    - content (str): The content of the item
                    - created_at (str): The creation timestamp in ISO format
                    - updated_at (str): The last update timestamp in ISO format
                - created_at (str): The creation timestamp in ISO format
                - updated_at (str): The last update timestamp in ISO format
                - item_history (Dict[str, List[str]]): Dictionary of item content history

    Raises:
        TypeError: If hint is not a string or None.
        ValueError: If hint is not one of the valid values (LIST, NOTE, ANY).
    """
    # Input validation
    if hint is not None and not isinstance(hint, str):
        raise TypeError("hint must be a string or None")
    
    if hint is not None:
        valid_hints = {"LIST", "NOTE", "ANY"}
        if hint not in valid_hints:
            raise ValueError(f"hint must be one of {valid_hints}, got '{hint}'")
    
    # Determine what to include based on hint
    include_notes = hint in (None, "NOTE", "ANY")
    include_lists = hint in (None, "LIST", "ANY")
    
    # Initialize result structure
    result = {
        "notes": [],
        "lists": []
    }
    
    # Retrieve notes if requested
    if include_notes:
        for note_id, note_data in DB["notes"].items():
            note_obj = {
                "id": note_data["id"],
                "title": note_data.get("title"),
                "content": note_data["content"],
                "created_at": note_data["created_at"],
                "updated_at": note_data["updated_at"],
                "content_history": note_data.get("content_history", [])
            }
            result["notes"].append(note_obj)
    
    # Retrieve lists if requested
    if include_lists:
        for list_id, list_data in DB["lists"].items():
            # Format list items according to docstring specification
            formatted_items = {}
            for item_id, item_data in list_data.get("items", {}).items():
                formatted_items[item_id] = {
                    "id": item_data["id"],
                    "content": item_data["content"],
                    "created_at": item_data["created_at"],
                    "updated_at": item_data["updated_at"]
                }
            
            list_obj = {
                "id": list_data["id"],
                "title": list_data.get("title"),
                "items": formatted_items,
                "created_at": list_data["created_at"],
                "updated_at": list_data["updated_at"],
                "item_history": list_data.get("item_history", {})
            }
            result["lists"].append(list_obj)
    
    
    return result


def get_notes_and_lists(item_ids: Optional[List[str]] = None, query: Optional[str] = None, search_term: Optional[str] = None, hint: str = 'ANY') -> Dict[str, Any]:
    """
    Use this function to retrieve notes or lists.

    The content of retrieved notes and lists can be empty. Do not call the 
    get_notes_and_lists again with the returned item IDs to retrieve the full content.
    This function can search by specific IDs, query terms, search terms, and can be 
    filtered by hint type.
    
    Args:
        item_ids (Optional[List[str]]): The IDs of the notes and lists to retrieve. 
            Use this if you know the IDs from previous interactions. Defaults to None.
        query (Optional[str]): Query to be used for searching notes and lists items. 
            Defaults to None.
        search_term (Optional[str]): The exact name of the list or note, or search terms 
            to find the lists or notes, only if it is not in NotesAndListsProvider values. 
            Do not use this if the user refers to a provider. This field should be populated 
            with the core identifying name of the note or list, even if a verb like "show," 
            "display," or "get" is present in the user's request. Defaults to None.
        hint (str): Type of the object to retrieve. Infer it from the user prompt. 
            If the user explicitly asks for lists or notes, use 'LIST' or 'NOTE' respectively. 
            Otherwise, use 'ANY'. Valid values are "NOTE", "LIST", or "ANY". Defaults to None.

    Returns:
        Dict[str, Any]: A NotesAndListsResult object containing the item_ids of the 
            retrieved notes and/or lists with the following structure:
            - notes (List[Dict[str, Any]]): List of retrieved notes containing:
                - id (str): The unique identifier of the note.
                - title (Optional[str]): The title of the note.
                - content (str): The content of the note.
                - created_at (str): The creation timestamp in ISO 8601 format.
                - updated_at (str): The last update timestamp in ISO 8601 format.
                - content_history (List[str]): List of previous content versions.
            - lists (List[Dict[str, Any]]): List of retrieved lists containing:
                - id (str): The unique identifier of the list.
                - title (Optional[str]): The title of the list.
                - items (Dict[str, Dict[str, Any]]): Dictionary of list items where 
                    each item contains:
                    - id (str): The unique identifier of the item.
                    - content (str): The content of the item.
                    - created_at (str): The creation timestamp in ISO 8601 format.
                    - updated_at (str): The last update timestamp in ISO 8601 format.
                - created_at (str): The creation timestamp in ISO 8601 format.
                - updated_at (str): The last update timestamp in ISO 8601 format.
                - item_history (Dict[str, List[str]]): Dictionary mapping item IDs 
                    to their content history.

    Raises:
        TypeError: If item_ids is not a list of strings or None, if query is not a string or None, if search_term is not a string or None, or if hint is not a string or None.
        ValueError: If item_ids is an empty list, if item_ids contains empty or whitespace-only strings, if query is empty or whitespace-only, if search_term is empty or whitespace-only, or if hint contains invalid values not in ["NOTE", "LIST", "ANY"].
    """
    # Input validation
    
    # Validate item_ids parameter
    if item_ids is not None:
        if not isinstance(item_ids, list):
            raise TypeError("item_ids is not a list of strings or None")
        if not all(isinstance(item_id, str) for item_id in item_ids):
            raise TypeError("item_ids is not a list of strings or None")
        if len(item_ids) == 0:
            raise ValueError("item_ids is an empty list")
        if any(not item_id.strip() for item_id in item_ids):
            raise ValueError("item_ids contains empty or whitespace-only strings")
    
    # Validate query parameter
    if query is not None:
        if not isinstance(query, str):
            raise TypeError("query is not a string or None")
        if not query.strip():
            raise ValueError("query is empty or whitespace-only")
    
    # Validate search_term parameter
    if search_term is not None:
        if not isinstance(search_term, str):
            raise TypeError("search_term is not a string or None")
        if not search_term.strip():
            raise ValueError("search_term is empty or whitespace-only")
    
    # Validate hint parameter
    if not isinstance(hint, str):
        raise TypeError("hint is not a string or None")
    valid_hint_values = ["NOTE", "LIST", "ANY"]
    if hint not in valid_hint_values:
        raise ValueError(f"hint contains invalid values not in {valid_hint_values}")
    
    # Initialize result sets to collect unique items
    found_notes = set()
    found_lists = set()
    
    # Handle direct lookup by item_ids
    if item_ids is not None:
        for item_id in item_ids:
            # Check if it's a note
            if item_id in DB["notes"]:
                found_notes.add(item_id)
            # Check if it's a list
            elif item_id in DB["lists"]:
                found_lists.add(item_id)
    
    # Handle search by query
    if query is not None:
        query_lower = query.lower()
        
        # Search in notes
        for note_id, note in DB["notes"].items():
            # Search in title and content (case-insensitive)
            title_match = note.get("title") and query_lower in note["title"].lower()
            content_match = query_lower in note["content"].lower()
            
            if title_match or content_match:
                found_notes.add(note_id)
        
        # Search in lists
        for list_id, lst in DB["lists"].items():
            # Search in title
            title_match = lst.get("title") and query_lower in lst["title"].lower()
            
            # Search in list items content
            item_match = any(
                query_lower in item["content"].lower()
                for item in lst["items"].values()
            )
            
            if title_match or item_match:
                found_lists.add(list_id)
    
    # Handle search by search_term (similar to query)
    if search_term is not None:
        search_term_lower = search_term.lower()
        
        # Search in notes
        for note_id, note in DB["notes"].items():
            # Search in title and content (case-insensitive)
            title_match = note.get("title") and search_term_lower in note["title"].lower()
            content_match = search_term_lower in note["content"].lower()
            
            if title_match or content_match:
                found_notes.add(note_id)
        
        # Search in lists
        for list_id, lst in DB["lists"].items():
            # Search in title
            title_match = lst.get("title") and search_term_lower in lst["title"].lower()
            
            # Search in list items content
            item_match = any(
                search_term_lower in item["content"].lower()
                for item in lst["items"].values()
            )
            
            if title_match or item_match:
                found_lists.add(list_id)
    
    # If no search parameters provided, return empty results
    if item_ids is None and query is None and search_term is None:
        found_notes = set()
        found_lists = set()
    
    # Apply hint filtering
    if hint == "NOTE":
        found_lists = set()  # Remove all lists
    elif hint == "LIST":
        found_notes = set()  # Remove all notes
    # If hint is "ANY" or None, keep both notes and lists
    
    # Build the result structure
    result_notes = []
    result_lists = []
    
    # Add found notes to result
    for note_id in found_notes:
        if note_id in DB["notes"]:
            note = DB["notes"][note_id].copy()
            result_notes.append(note)
    
    # Add found lists to result
    for list_id in found_lists:
        if list_id in DB["lists"]:
            lst = DB["lists"][list_id].copy()
            result_lists.append(lst)
    
    
    # Return the NotesAndListsResult structure
    return {
        "notes": result_notes,
        "lists": result_lists
    } 


def create_note(
        title: Optional[str] = None, 
        text_content: Optional[str] = None, 
        generated_title: Optional[str] = None
        ) -> Dict[str, Any]:
    """Use this function to create a new note.

    This function handles the creation of a note with initial content. The title
    argument must always be populated if text content is non-empty. The note is
    always created in the user's query language unless suggested otherwise.

    Args:
        title (Optional[str]): Title of the note. If the user explicitly specifies
            a title, use it. Otherwise, a suitable title must be generated,
            based on the value of the `text_content` argument and the
            overall prompt context. If `text_content` is empty as well, then
            leave this argument empty.
        text_content (Optional[str]): The text content of the note. This can be
            initial content provided by the user, or the result content of a
            `google_search` operation. The text_content should always be in
            user's query language unless suggested otherwise.
        generated_title (Optional[str]): Required if the `title` argument is
            empty. If the user provides the text content of the note but not
            a title, a suitable title should be generated, based on the text
            content and overall prompt context.

    Returns:
        Dict[str, Any]: A dictionary containing the details of the newly created
            note, structured as a TextNote object. It contains the following keys:
            - note_id (str): The unique identifier of the note.
            - title (str): The title of the note.
            - text_content (str): The text content of the note.
           
    Raises:
        TypeError: If input arguments are not of the correct type.
        ValidationError: If input arguments fail validation.
    """

    if title is not None and not isinstance(title, str):
        raise TypeError("A title must be a string.")
    
    if text_content is not None and not isinstance(text_content, str):
        raise TypeError("Text content must be a string.")
    
    if generated_title is not None and not isinstance(generated_title, str):
        raise TypeError("A generated title must be a string.")


    # Determine the effective title from the provided arguments. The user-provided
    # title takes precedence over the generated one.
    effective_title = title or generated_title

    # Check if the provided title and content are effectively empty (None or just whitespace).
    is_title_empty = not (effective_title and effective_title.strip())
    is_content_empty = not (text_content and text_content.strip())

    # A note must have some substance, either in the title or the text content.
    if is_title_empty and is_content_empty:
        raise ValidationError("A note must have at least a title or text content.")

    # As per the docstring, a note with non-empty content must also have a title.
    if not is_content_empty and is_title_empty:
        raise ValidationError("A note with text content must have a title.")
    

    # Generate a unique identifier for the new note.
    note_id = str(uuid.uuid4())

    # Generate timestamp for the note
    now_iso = datetime.now(timezone.utc).isoformat()

    # Construct the note object. If text_content is None, it defaults to an empty string.
    # The validation ensures `effective_title` is a non-empty string at this point.
    new_note = {
        "id": note_id,
        "title": effective_title,
        "content": text_content or "",
        "created_at": now_iso,
        "updated_at": now_iso,
        "content_history": []
    }

    # Ensure the 'notes' collection exists in the database and add the new note.
    # Notes are stored in a dictionary keyed by their unique note_id for efficient access.
    notes_db = DB.setdefault("notes", {})
    notes_db[note_id] = new_note

    return new_note


def update_note(
        search_term: Optional[str] = None, 
        query: Optional[str] = None, 
        query_expansion: Optional[List[str]] = None, 
        note_id: Optional[str] = None, 
        text_content: Optional[str] = None, 
        update_type: Optional[str] = None
        ) -> Dict[str, Any]:
    """This can be used to update (add/append/prepend/insert to) an existing note content.

    This function updates an existing note's content. The note to be updated can be
    identified by a search term, a query, or a specific note ID. The content can be
    added, appended, prepended, or inserted based on the specified update type.

    Args:
        search_term (Optional[str]): The name of the note or keywords to search for the note.
        query (Optional[str]): Optional query to be used for searching notes.
        query_expansion (Optional[List[str]]): Optional search query expansion using synonyms or related terms.
        note_id (Optional[str]): The id of the note to be updated. If available from the context, use this instead of search_term.
        text_content (Optional[str]): Text content to update the existing note with.
        update_type (Optional[str]): The type of update operation to be performed on the note. 
            Possible values: "APPEND","PREPEND","REPLACE","MOVE","EDIT"

    Returns:
        Dict[str, Any]: A dictionary containing information about the updated note. It contains the following keys:
            - note_id (str): The unique identifier of the note.
            - title (str): The title of the note.
            - text_content (str): The text content of the note.

    Raises:
        KeyError: If the 'notes' collection is not found in the database for provided note_id.
        TypeError: If input arguments are not of the correct type.
        ValidationError: If input arguments fail validation.
        NotFoundError: If the note is not found.
    """
    # --- Argument Type Validation ---
    if search_term is not None and not isinstance(search_term, str):
        raise TypeError("Argument 'search_term' must be a string.")
    if query is not None and not isinstance(query, str):
        raise TypeError("Argument 'query' must be a string.")
    if query_expansion is not None:
        if not isinstance(query_expansion, builtins.list) or not all(isinstance(i, str) for i in query_expansion):
            raise TypeError("Argument 'query_expansion' must be a list of strings.")
    if note_id is not None and not isinstance(note_id, str):
        raise TypeError("Argument 'note_id' must be a string.")
    if text_content is not None and not isinstance(text_content, str):
        raise TypeError("Argument 'text_content' must be a string.")
    if update_type is not None and not isinstance(update_type, str):
        raise TypeError("Argument 'update_type' must be a string.")

    # --- Argument Value Validation ---
    if not any([note_id, search_term, query]):
        raise ValidationError("Either note_id, search_term, or query must be provided.")

    VALID_UPDATE_TYPES = {"APPEND", "PREPEND", "REPLACE", "DELETE", "CLEAR", "MOVE", "EDIT"}
    if not update_type or update_type.upper() not in VALID_UPDATE_TYPES:
        raise ValidationError(f"Invalid 'update_type'.")
    
    update_type_upper = update_type.upper()

    TYPES_REQUIRING_CONTENT = {"APPEND", "PREPEND", "REPLACE", "DELETE", "EDIT"}
    if update_type_upper in TYPES_REQUIRING_CONTENT and text_content is None:
        raise ValidationError(f"'text_content' is required for update type '{update_type}'.")

    if update_type_upper == "MOVE":
        raise ValidationError("'MOVE' update type is not supported.")

    # --- Find the Note ---
    notes_db = DB.get("notes", {})
    found_note = None

    if note_id:
        # Prioritize searching by note_id if provided
        if note_id not in notes_db:
            raise NotFoundError(f"Note with id '{note_id}' not found.")

        found_note = notes_db[note_id]
    else:
        # Fallback to searching by keywords
        search_keywords = set()
        if search_term:
            search_keywords.add(search_term.lower())
        if query:
            search_keywords.add(query.lower())
        if query_expansion:
            search_keywords.update(term.lower() for term in query_expansion)

        matched_notes = []
        for note in notes_db.values():
            # Search in both title and content, case-insensitively
            title = note.get("title", "").lower()
            content = note.get("content", "").lower()
            if any(keyword in title or keyword in content for keyword in search_keywords):
                matched_notes.append(note)

        if not matched_notes:
            raise NotFoundError("No note found matching the search criteria.")
        if len(matched_notes) > 1:
            raise NotFoundError(f"Multiple notes found. Please be more specific or use a note_id.")
        found_note = matched_notes[0]

    # --- Update the Note Content ---
    original_content = found_note.get("content", "")

    if update_type_upper == "APPEND":
        found_note["content"] = original_content + text_content
    elif update_type_upper == "PREPEND":
        found_note["content"] = text_content + original_content
    elif update_type_upper in ["REPLACE", "EDIT"]:
        found_note["content"] = text_content
    elif update_type_upper == "DELETE":
        # Removes all occurrences of the specified text_content from the note
        found_note["content"] = original_content.replace(text_content, "")
    elif update_type_upper == "CLEAR":
        found_note["content"] = ""
    
    # The note object is a reference to a dictionary in DB['notes'], so the update is reflected in DB.

    DB["notes"][found_note["id"]] = found_note

    # --- Prepare and Return Response ---
    return {
        "id": found_note.get("id", ""),
        "title": found_note.get("title", ""),
        "content": found_note.get("content", ""),
    }


def append_to_note(
        query: Optional[str] = None,
        query_expansion: Optional[List[str]] = None,
        note_id: Optional[str] = None,
        text_content: Optional[str] = None
    ) -> Dict[str, any]:
    """This can be used to add content to an existing note.

    This function adds specified text content to an existing note, which can be identified either by its ID or by a search query.

    Args:
        query (Optional[str]): Optional query to be used for searching notes and lists items. This should not be set if the title is not specified.
        query_expansion (Optional[List[str]]): Optional search query expansion using synonyms or related terms.
        note_id (Optional[str]): The id of the note to which the text content will be appended.
        text_content (Optional[str]): Text content to be appended to the existing note.

    Returns:
        Dict[str, any]: A dictionary containing information in the updated note. It contains the following keys:
            - note_id (str): The unique identifier of the note.
            - title (str): The title of the note.
            - text_content (str): The text content of the note.

    Raises:
        TypeError: If input arguments are not of the correct type.
        NotFoundError: If the note is not found.
        ValidationError: If input arguments fail validation.
    """
    # --- Argument Type Validation ---
    if note_id is not None and not isinstance(note_id, str):
        raise TypeError("Argument 'note_id' must be a string.")
    if query is not None and not isinstance(query, str):
        raise TypeError("Argument 'query' must be a string.")
    if text_content is not None and not isinstance(text_content, str):
        raise TypeError("Argument 'text_content' must be a string.")
    if query_expansion is not None:
        if not isinstance(query_expansion, list) or not all(isinstance(s, str) for s in query_expansion):
            raise TypeError("Argument 'query_expansion' must be a list of strings.")

    if not note_id and not query:
        raise ValidationError("Either note_id or query must be provided.")

    target_note = None

    notes_db = DB.get("notes", {})

    if note_id:
        # Find the note by its unique ID.
        if note_id not in notes_db:
            raise NotFoundError(f"Note with id '{note_id}' not found.")

        target_note = notes_db[note_id]
    else:  # A query must have been provided.
        # Prepare search terms for a case-insensitive search.
        search_terms = {query.lower()}
        if query_expansion:
            search_terms.update(term.lower() for term in query_expansion)

        # Find the first note that matches the search criteria in its title or content.
        matched_notes = []
        for note in notes_db.values():
            # Search in both title and content, case-insensitively
            title = note.get("title", "").lower()
            content = note.get("content", "").lower()

            if any(term in title or term in content for term in search_terms):
                matched_notes.append(note)

        if not matched_notes:
            raise NotFoundError("No note found matching the search criteria.")
        if len(matched_notes) > 1:
            raise ValidationError(f"Multiple notes found. Please be more specific or use a note_id.")
        target_note = matched_notes[0]

    # Append the new text content to the found note.
    original_content = target_note.get("content", "")
    target_note["content"] = f"{original_content}{text_content}"

    DB["notes"][target_note["id"]] = target_note

    # Construct the response dictionary from the updated note data.
    response = {
        "id": target_note.get("id", ""),
        "title": target_note.get("title", ""),
        "content": target_note.get("content", ""),
    }

    return response
