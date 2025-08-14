import json
import os

DEFAULT_DB_PATH = os.path.join(
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ),
    "DBs",
    "GooglePeopleDefaultDB.json",
)


class DB:
    """Database class for Google People API simulation."""
    
    def __init__(self):
        self._data = {}
        self._load_default_data()
    
    def _load_default_data(self):
        """Load default data from JSON file."""
        try:
            with open(DEFAULT_DB_PATH, "r", encoding="utf-8") as f:
                self._data.update(json.load(f))
        except FileNotFoundError:
            # Initialize with empty data if file doesn't exist
            self._data = {}
    
    def get(self, key: str, default=None):
        """Get a value from the database."""
        return self._data.get(key, default)
    
    def set(self, key: str, value):
        """Set a value in the database."""
        self._data[key] = value
    
    def clear(self):
        """Clear all data from the database."""
        self._data.clear()
    
    def update(self, data):
        """Update the database with new data."""
        self._data.update(data)


# Create a singleton instance
DB = DB()


def save_state(filepath: str) -> None:
    """Save the current state to a JSON file."""
    with open(filepath, "w") as f:
        json.dump(DB._data, f)


def load_state(filepath: str) -> None:
    """Load state from a JSON file."""
    with open(filepath, "r") as f:
        state = json.load(f)
    DB.clear()
    DB.update(state)
