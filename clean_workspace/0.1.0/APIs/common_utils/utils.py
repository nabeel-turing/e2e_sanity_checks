import os

def discover_services() -> list[str]:
    """
    Discovers all available services by listing directories in the APIs folder.
    """
    services = []
    api_root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    for entry in os.listdir(api_root_dir):
        if os.path.isdir(os.path.join(api_root_dir, entry)) and entry != "common_utils" and not entry.startswith("__"):
            services.append(entry)
    return sorted(services)