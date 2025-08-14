import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from .SimulationEngine.db import DB
from .SimulationEngine import utils



def create_list(
        list_name: Optional[str] = None,
        elements_to_add: Optional[List[str]] = None,
        generated_title: Optional[str] = None
    ) -> Dict[str, Any]:
    """Use this function to create a new list.

    This function handles the creation of a list with optional initial list items.
    The `list_name` argument should always be populated if the `elements_to_add`
    argument is non-empty. The list is always created in the user's query
    language unless suggested otherwise.

    Args:
        list_name (Optional[str]): Name of the list. If the user explicitly
            specifies a list name, use it. Otherwise, a suitable name must be
            generated based on the value of the `elements_to_add` argument and
            the overall prompt context. If `elements_to_add` is empty as well,
            then this argument should be left empty.
        elements_to_add (Optional[List[str]]): The items to include in the list.
            This can be initial list items provided by the user, or the result
            content of a `google_search` operation. The items to add to the list
            should always be in the user's query language unless suggested
            otherwise.
        generated_title (Optional[str]): Required if the `list_name` argument is
            empty. If the user provides the items to add to the list but not a
            list name, a suitable name should always be generated, based on the
            items to add and the overall prompt context.

    Returns:
        Dict[str, Any]: A dictionary containing the details of the newly created list. It contains the following keys:
            - id(str): The ID of the newly created list.
            - title(str): The name of the newly created list.
            - items(Dict[str, Dict[str, Any]]): A dictionary of the items in the newly created list. Each item is a dictionary with the item id as the key.
                -id(Dict[str, str]): A dictionary with the following keys:
                    - id(str): The ID of the item.
                    - content(str): The content of the item.
                    - created_at(str): The date and time the item was created. ISO 8601 format.
                    - updated_at(str): The date and time the item was last updated. ISO 8601 format.
            - created_at(str): The date and time the list was created. ISO 8601 format.
            - updated_at(str): The date and time the list was last updated. ISO 8601 format.
            - item_history(Dict[str, Any]): A dictionary containing the history of the items in the list.

    Raises:
        TypeError: If list_name, elements_to_add, or generated_title are not of type str.
        ValueError: If list_name is empty and elements_to_add is empty.
        ValidationError: If the list_name and generated_title are empty.
    """
    # Validate argument types
    if list_name is not None and not isinstance(list_name, str):
        raise TypeError("Argument 'list_name' must be a string.")
    if elements_to_add is not None:
        if not isinstance(elements_to_add, list):
            raise TypeError("Argument 'elements_to_add' must be a list of strings.")
        if not all(isinstance(item, str) for item in elements_to_add):
            raise TypeError("All elements in 'elements_to_add' must be strings.")
    if generated_title is not None and not isinstance(generated_title, str):
        raise TypeError("Argument 'generated_title' must be a string.")

    # Validate argument values based on logical constraints
    if not list_name and not generated_title and not elements_to_add:
        raise ValueError("One of the arguments 'list_name', 'generated_title', or 'elements_to_add' must be provided.")

    # Determine the final title, prioritizing the user-provided list_name
    final_title = list_name if list_name is not None else generated_title

    # A title must exist if elements are being added
    if elements_to_add and final_title is None:
        raise ValueError("A list name or a generated title is required when adding elements.")

    # Generate list metadata
    now_iso = datetime.now(timezone.utc).isoformat()
    list_id = str(uuid.uuid4())

    # Process list items if provided
    items_dict: Dict[str, Dict[str, Any]] = {}
    if elements_to_add:
        for item_content in elements_to_add:
            item_id = str(uuid.uuid4())
            item_now_iso = datetime.now(timezone.utc).isoformat()
            items_dict[item_id] = {
                "id": item_id,
                "content": item_content,
                "created_at": item_now_iso,
                "updated_at": item_now_iso,
            }

    # Construct the response dictionary
    new_list = {
        "id": list_id,
        "title": final_title,
        "items": items_dict,
        "created_at": now_iso,
        "updated_at": now_iso,
        "item_history": {},
    }

    DB.setdefault("lists", {})[list_id] = new_list

    return new_list

def add_to_list(
    list_id: Optional[str] = None,
    query: Optional[str] = None,
    search_term: Optional[str] = None,
    query_expansion: Optional[List[str]] = None,
    list_name: Optional[str] = None, 
    elements_to_add: Optional[List[str]] = None,
    is_bulk_mutation: Optional[bool] = False,
) -> Dict[str, Any]:
    """Use this function to add items to an existing list.

    Args:
        list_id (Optional[str]): The ID of the list to add items to.
        query (Optional[str]): A search query to find the list.
        search_term (Optional[str]): The name of the list to find.
        query_expansion (Optional[List[str]]): Synonyms to expand the search.
        list_name (Optional[str]): The name of the list to be created if one doesn't exist.
        elements_to_add (Optional[List[str]]): The items to add to the list. 
        is_bulk_mutation (Optional[bool]): Indicates if the intent is to modify multiple lists. Not implemented yet.
    Returns:
        Dict[str, Any]: A dictionary object containing the updated list.

    Raises:
        TypeError: If input arguments are not of the expected type.
        ValueError: If input arguments fail validation.
        TypeError: If input arguments are not of the expected type.
    """

    # Validate argument types
    if list_id is not None and not isinstance(list_id, str):
        raise TypeError("Argument 'list_id' must be a string.")
    if search_term is not None and not isinstance(search_term, str):
        raise TypeError("Argument 'search_term' must be a string.")
    if query is not None and not isinstance(query, str):
        raise TypeError("Argument 'query' must be a string.")
    if query_expansion is not None:
        if not isinstance(query_expansion, list) or not all(isinstance(item, str) for item in query_expansion):
            raise TypeError("Argument 'query_expansion' must be a list of strings.")

    if elements_to_add is not None:
        if not isinstance(elements_to_add, list):
            raise TypeError("Argument 'elements_to_add' must be a list of strings.")
        if not all(isinstance(item, str) for item in elements_to_add):
            raise TypeError("All elements in 'elements_to_add' must be strings.")
        if len(elements_to_add) == 0:
            raise ValueError("The 'elements_to_add' list cannot be empty.")

    # Validate argument values based on logical constraints
    if not list_id and not search_term and not query and not query_expansion:
        raise ValueError("You must provide either a 'list_id', 'search_term', 'query', or 'query_expansion'.")
    

    target_list_dict = None
    if list_id:
        if list_id in DB["lists"]:
            target_list_dict = DB["lists"][list_id]
    else: # Search by term
        search_terms = search_term.lower() if search_term else None
        query_expansion_terms = [term.lower() for term in query_expansion] if query_expansion else None
        query_terms = query.lower() if query else None

        for lst in DB["lists"].values():
            if search_terms and search_terms in lst["title"].lower():
                target_list_dict = lst
                break


            if query_terms and query_terms in lst["title"].lower():
                target_list_dict = lst
                break

            if query_expansion_terms:
                if any(term in lst["title"].lower() for term in query_expansion_terms):
                    target_list_dict = lst
                    break

    if not target_list_dict:
        raise ValueError("Could not find the specified list.")

    new_list_items = {}
    if elements_to_add:
        for ele in elements_to_add:
            new_id = str(uuid.uuid4())
            new_list_items[new_id] = {
                "id": new_id,
                "content": ele,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }

    target_list_dict['items'].update(new_list_items)
    target_list_dict['updated_at'] = datetime.now(timezone.utc).isoformat()
    DB["lists"][target_list_dict['id']] = target_list_dict

    return target_list_dict