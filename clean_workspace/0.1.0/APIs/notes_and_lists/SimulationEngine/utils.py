import uuid
from datetime import datetime
from typing import Dict, List, Optional, Union, Any
import dateutil.parser as dateutil_parser
from .db import DB  # Import the global DB instance
from .models import utc_now_iso  # Import the new helper function and models

# Consistency Maintenance Functions
def update_title_index(title: Optional[str], item_id: str) -> None:
    """Maintains title index when items are created/updated"""
    if not title:
        return
    
    # Ensure title_index exists
    if "title_index" not in DB:
        DB["title_index"] = {}
    
    # Remove old references
    for existing_title, ids in list(DB["title_index"].items()):
        if item_id in ids:
            DB["title_index"][existing_title].remove(item_id)
            if not DB["title_index"][existing_title]:
                del DB["title_index"][existing_title]
    
    # Add new reference
    if title not in DB["title_index"]:
        DB["title_index"][title] = []
    if item_id not in DB["title_index"][title]:
        DB["title_index"][title].append(item_id)

def update_content_index(item_id: str, content: str) -> None:
    """Updates content index when items are created/updated"""
    # Ensure content_index exists
    if "content_index" not in DB:
        DB["content_index"] = {}
    
    # Tokenize content into keywords
    keywords = set()
    for word in content.lower().split():
        cleaned = word.strip(".,!?;:\"'()[]{}<>@#$%^&*+-=/\\|~`")
        if cleaned and len(cleaned) > 2:
            keywords.add(cleaned)
    
    # Update index entries
    for keyword in keywords:
        if keyword not in DB["content_index"]:
            DB["content_index"][keyword] = []
        if item_id not in DB["content_index"][keyword]:
            DB["content_index"][keyword].append(item_id)

def remove_from_indexes(item_id: str) -> None:
    """Removes an item from all indexes when deleted"""
    # Title index cleanup
    if "title_index" in DB:
        for title, ids in list(DB["title_index"].items()):
            if item_id in ids:
                DB["title_index"][title].remove(item_id)
                if not DB["title_index"][title]:
                    del DB["title_index"][title]
    
    # Content index cleanup
    if "content_index" in DB:
        for keyword, ids in list(DB["content_index"].items()):
            if item_id in ids:
                DB["content_index"][keyword].remove(item_id)
                if not DB["content_index"][keyword]:
                    del DB["content_index"][keyword]

def maintain_note_history(note_id: str, old_content: str) -> None:
    """Maintains content history when a note is updated"""
    if note_id not in DB["notes"]:
        return
    
    note = DB["notes"][note_id]
    if old_content != note["content"]:
        note["content_history"].append(old_content)
        if len(note["content_history"]) > 10:
            note["content_history"].pop(0)

def maintain_list_item_history(list_id: str, item_id: str, old_content: str) -> None:
    """Maintains history for list items when updated"""
    if list_id not in DB["lists"] or item_id not in DB["lists"][list_id]["items"]:
        return
    
    lst = DB["lists"][list_id]
    if item_id not in lst["item_history"]:
        lst["item_history"][item_id] = []
    
    current_content = lst["items"][item_id]["content"]
    if old_content != current_content:
        lst["item_history"][item_id].append(old_content)
        if len(lst["item_history"][item_id]) > 5:
            lst["item_history"][item_id].pop(0)

# Utility/Interaction Functions
def get_note(note_id: str) -> Optional[Dict]:
    """Retrieves a note by ID if it exists"""
    return DB["notes"].get(note_id)

def get_list(list_id: str) -> Optional[Dict]:
    """Retrieves a list by ID if it exists"""
    return DB["lists"].get(list_id)

def get_list_item(list_id: str, item_id: str) -> Optional[Dict]:
    """Retrieves a specific list item if it exists"""
    lst = DB["lists"].get(list_id)
    if not lst:
        return None
    return lst["items"].get(item_id)

def find_by_title(title: str) -> List[str]:
    """Finds item IDs by exact title match"""
    return DB.get("title_index", {}).get(title, [])

def find_by_keyword(keyword: str) -> List[str]:
    """Finds item IDs containing a keyword"""
    return DB.get("content_index", {}).get(keyword.lower(), [])

def search_notes_and_lists(query: Optional[str] = None, hint: Optional[str] = None, legacy: bool = False) -> Union[Dict[str, List[Dict]], List[Dict]]:
    """Searches notes and lists by query with optional type hint.
    If legacy=True, returns a flat list of matching notes and lists (for backward compatibility).
    
    Args:
        query (Optional[str]): The query to search for.
        hint (Optional[str]): The type of item to search for.
        legacy (bool): Whether to return a flat list of matching notes and lists (for backward compatibility).
    
    Returns:
        Union[Dict[str, List[Dict]], List[Dict]]: A dictionary containing the matching notes and lists, or a flat list of matching notes and lists.
    """
    # Type check
    if query is not None and not isinstance(query, str):
        raise TypeError("query must be a string or None")

    # Handle empty or None/whitespace query
    if query is None or (isinstance(query, str) and not query.strip()):
        if legacy:
            return []
        return {"notes": [], "lists": []}

    query_lower = query.lower()
    notes = []
    lists = []
    flat_results = []

    # Search notes
    if hint in (None, "NOTE", "ANY"):
        for note_id, note in DB["notes"].items():
            title = note.get("title") or ""
            content = note.get("content") or ""
            if query_lower in title.lower() or query_lower in content.lower():
                # Fill missing fields with defaults
                note_result = {
                    "id": note.get("id", note_id),
                    "title": note.get("title"),
                    "content": note.get("content", ""),
                    "created_at": note.get("created_at", ""),
                    "updated_at": note.get("updated_at", ""),
                    "content_history": note.get("content_history", []),
                }
                notes.append(note_result)
                flat_results.append(note_result)

    # Search lists
    if hint in (None, "LIST", "ANY"):
        for list_id, lst in DB["lists"].items():
            title = lst.get("title") or ""
            list_matches = query_lower in title.lower()
            items = lst.get("items", {})
            item_matches = any(query_lower in (item.get("content", "").lower()) for item in items.values())
            if list_matches or item_matches:
                # Fill missing fields with defaults
                list_result = {
                    "id": lst.get("id", list_id),
                    "title": lst.get("title"),
                    "items": items,
                    "created_at": lst.get("created_at", ""),
                    "updated_at": lst.get("updated_at", ""),
                    "item_history": lst.get("item_history", {}),
                }
                lists.append(list_result)
                flat_results.append(list_result)

    if legacy:
        return flat_results
    return {"notes": notes, "lists": lists}

def create_note(title: Optional[str], content: str) -> Dict:
    """Creates a new note with automatic title generation"""
    note_id = f"note_{str(uuid.uuid4())[:8]}"
    created_at = utc_now_iso()
    
    # Generate title if missing
    if not title and content:
        title = content[:50] + ("..." if len(content) > 50 else "")
    
    note = {
        "id": note_id,
        "title": title,
        "content": content,
        "created_at": created_at,
        "updated_at": created_at,
        "content_history": []
    }
    
    DB["notes"][note_id] = note
    if title:
        update_title_index(title, note_id)
    update_content_index(note_id, content)
    
    return note

def add_to_list(list_id: str, items: List[str]) -> Dict:
    """Adds items to an existing list"""
    lst = DB["lists"].get(list_id)
    if not lst:
        raise ValueError(f"List {list_id} not found")
    
    current_time = utc_now_iso()
    lst["updated_at"] = current_time
    
    for content in items:
        item_id = f"item_{str(uuid.uuid4())[:8]}"
        lst["items"][item_id] = {
            "id": item_id,
            "content": content,
            "created_at": current_time,
            "updated_at": current_time
        }
        update_content_index(item_id, content)
    
    return lst

def get_recent_operations(limit: int = 10) -> List[Dict]:
    """Gets the most recent operations for undo functionality"""
    sorted_ops = sorted(
        DB["operation_log"].values(),
        key=lambda op: op["timestamp"],
        reverse=True
    )
    return sorted_ops[:limit]

def log_operation(operation_type: str, target_id: str, parameters: dict) -> str:
    """Records an operation in the log with a snapshot"""
    op_id = f"op_{str(uuid.uuid4())[:8]}"
    timestamp = utc_now_iso()
    
    # Create snapshot of current state
    snapshot = None
    if target_id in DB["notes"]:
        snapshot = DB["notes"][target_id].copy()
    elif target_id in DB["lists"]:
        snapshot = DB["lists"][target_id].copy()
    else:
        # Search for list items
        for lst in DB["lists"].values():
            if target_id in lst["items"]:
                snapshot = lst["items"][target_id].copy()
                break
    
    DB["operation_log"][op_id] = {
        "id": op_id,
        "operation_type": operation_type,
        "target_id": target_id,
        "parameters": parameters,
        "timestamp": timestamp,
        "snapshot": snapshot
    }
    
    return op_id

def find_items_by_search(search_text: str):
        """Find notes and lists matching the search text"""
        search_lower = search_text.lower()
        found_notes = set()
        found_lists = set()
        
        # Search in notes
        for note_id, note in DB["notes"].items():
            # Search in title and content (case-insensitive)
            title_match = note.get("title") and search_lower in note["title"].lower()
            content_match = search_lower in note["content"].lower()
            
            if title_match or content_match:
                found_notes.add(note_id)
        
        # Search in lists
        for list_id, lst in DB["lists"].items():
            # Search in title
            title_match = lst.get("title") and search_lower in lst["title"].lower()
            
            # Search in list items content
            item_match = any(
                search_lower in item["content"].lower()
                for item in lst["items"].values()
            )
            
            if title_match or item_match:
                found_lists.add(list_id)
        
        return found_notes, found_lists
    