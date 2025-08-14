"""
Utility functions for the Meet API simulation.
"""
from typing import Dict, Any, List, Optional
from .db import DB


def ensure_exists(collection: str, item_id: str) -> bool:
    """
    Checks if an item exists in a specific collection in the database.
    
    Args:
        collection (str): The name of the collection to check (e.g., "spaces", "conferenceRecords").
        item_id (str): The ID of the item to check for.
        
    Returns:
        True if the item exists, raises ValueError otherwise.
    """
    if collection not in DB or item_id not in DB[collection]:
        raise ValueError(f"Item '{item_id}' does not exist in collection '{collection}'.")
    return True

def paginate_results(items: List[Dict[str, Any]], collection_name: str, page_size: Optional[int] = None, page_token: Optional[str] = None) -> Dict[str, Any]:
    """
    Paginates a list of items based on the provided page size and token.
    
    Args:
        items (List[Dict[str, Any]]): The list of items to paginate.
        collection_name (str): The name of the collection (used as the key in the result).
        page_size (Optional[int]): The maximum number of items to return in a page.
        page_token (Optional[str]): A token indicating the starting position for the page.
        
    Returns:
        A dictionary containing the paginated items under collection_name key and a next page token if applicable.
    """
    if not page_size:
        page_size = 100
    
    start_index = 0
    if page_token:
        try:
            start_index = int(page_token)
        except ValueError:
            start_index = 0
    
    end_index = min(start_index + page_size, len(items))
    paginated_items = items[start_index:end_index]
    
    result = {
        collection_name: paginated_items
    }
    
    if end_index < len(items):
        result["nextPageToken"] = str(end_index)
    
    return result 