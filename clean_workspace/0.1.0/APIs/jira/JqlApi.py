# APIs/jira/JqlApi.py
from typing import Dict, Any

def get_jql_autocomplete_data() -> Dict[str, Any]:
    """
    Get JQL autocomplete data.

    This method returns JQL autocomplete data.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - fields (List[str]): A list of fields - for mock implementation, returns a list of fields - "summary", "description"
            - operators (List[str]): A list of operators - for mock implementation, returns a list of operators - "=", "~"
    """
    return {"fields": ["summary", "description"], "operators": ["=", "~"]}
