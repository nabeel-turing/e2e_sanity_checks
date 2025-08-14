# APIs/jira/ServerInfoApi.py
from typing import Dict, Any

def get_server_info() -> Dict[str, Any]:
    """
    Get server information.

    This method returns information about the server.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - baseUrl (str): The base URL of the server, currently hardcoded to "http://mock-server:8080"
            - version (str): The version of the server, currently hardcoded to "6.1"
            - title (str): The title of the server, currently hardcoded to "Mock JIRA Server"

    """
    return {
        "baseUrl": "http://mock-server:8080",
        "version": "6.1",
        "title": "Mock JIRA Server",
    }
