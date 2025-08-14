import pytest
from unittest.mock import patch
from google_home.SimulationEngine.utils import (
    add_structure,
    get_structure,
    update_structure,
    delete_structure,
    add_room,
    get_room,
    update_room,
    delete_room,
    add_device,
    get_device,
    update_device,
    delete_device,
)
from google_home.SimulationEngine.custom_errors import (
    InvalidInputError,
    DeviceNotFoundError,
)

@pytest.fixture
def mock_db():
    with patch("google_home.SimulationEngine.utils.DB", {"structures": {}}) as _mock_db:
        yield _mock_db

# region Structure Tests
def test_add_structure(mock_db):
    structure_data = {"name": "Home", "rooms": {}}
    result = add_structure(structure_data)
    assert result["name"] == "Home"
    assert "Home" in mock_db["structures"]

def test_add_existing_structure(mock_db):
    structure_data = {"name": "Home", "rooms": {}}
    add_structure(structure_data)
    with pytest.raises(InvalidInputError, match="Structure 'Home' already exists."):
        add_structure(structure_data)

def test_add_invalid_structure(mock_db):
    with pytest.raises(InvalidInputError):
        add_structure({"rooms": {}})  # Missing 'name'

def test_get_structure(mock_db):
    structure_data = {"name": "Home", "rooms": {}}
    add_structure(structure_data)
    result = get_structure("Home")
    assert result is not None
    assert result["name"] == "Home"

def test_get_nonexistent_structure(mock_db):
    result = get_structure("NonExistentHome")
    assert result is None

def test_update_structure(mock_db):
    structure_data = {"name": "Home", "rooms": {}}
    add_structure(structure_data)
    update_data = {"name": "New Home"}
    result = update_structure("Home", update_data)
    assert result["name"] == "New Home"
    assert "New Home" in mock_db["structures"]
    assert "Home" not in mock_db["structures"]

def test_update_nonexistent_structure(mock_db):
    with pytest.raises(DeviceNotFoundError, match="Structure 'NonExistentHome' not found."):
        update_structure("NonExistentHome", {"name": "New Name"})

def test_update_structure_with_invalid_data(mock_db):
    structure_data = {"name": "Home", "rooms": {}}
    add_structure(structure_data)
    with pytest.raises(InvalidInputError):
        update_structure("Home", {"name": 123})  # Invalid type for name

def test_delete_structure(mock_db):
    structure_data = {"name": "Home", "rooms": {}}
    add_structure(structure_data)
    delete_structure("Home")
    assert "Home" not in mock_db["structures"]

def test_delete_nonexistent_structure(mock_db):
    with pytest.raises(DeviceNotFoundError, match="Structure 'NonExistentHome' not found."):
        delete_structure("NonExistentHome")
# endregion

# region Room Tests
def test_add_room(mock_db):
    add_structure({"name": "Home", "rooms": {}})
    room_data = {"name": "Living Room", "devices": {}}
    result = add_room("Home", room_data)
    assert result["name"] == "Living Room"
    assert "Living Room" in mock_db["structures"]["Home"]["rooms"]

def test_add_room_to_nonexistent_structure(mock_db):
    with pytest.raises(DeviceNotFoundError, match="Structure 'NonExistentHome' not found."):
        add_room("NonExistentHome", {"name": "Living Room", "devices": {}})

def test_add_existing_room(mock_db):
    add_structure({"name": "Home", "rooms": {}})
    room_data = {"name": "Living Room", "devices": {}}
    add_room("Home", room_data)
    with pytest.raises(InvalidInputError, match="Room 'Living Room' already exists in structure 'Home'."):
        add_room("Home", room_data)

def test_add_invalid_room(mock_db):
    add_structure({"name": "Home", "rooms": {}})
    with pytest.raises(InvalidInputError):
        add_room("Home", {"devices": {}})  # Missing 'name'

def test_get_room(mock_db):
    add_structure({"name": "Home", "rooms": {}})
    add_room("Home", {"name": "Living Room", "devices": {}})
    result = get_room("Home", "Living Room")
    assert result is not None
    assert result["name"] == "Living Room"

def test_get_nonexistent_room(mock_db):
    add_structure({"name": "Home", "rooms": {}})
    assert get_room("Home", "NonExistentRoom") is None
    assert get_room("NonExistentHome", "Living Room") is None

def test_update_room(mock_db):
    add_structure({"name": "Home", "rooms": {}})
    add_room("Home", {"name": "Living Room", "devices": {}})
    update_data = {"name": "Family Room"}
    result = update_room("Home", "Living Room", update_data)
    assert result["name"] == "Family Room"
    assert "Family Room" in mock_db["structures"]["Home"]["rooms"]
    assert "Living Room" not in mock_db["structures"]["Home"]["rooms"]

def test_update_nonexistent_room(mock_db):
    add_structure({"name": "Home", "rooms": {}})
    with pytest.raises(DeviceNotFoundError, match="Room 'NonExistentRoom' in structure 'Home' not found."):
        update_room("Home", "NonExistentRoom", {"name": "New Name"})

def test_update_room_with_invalid_data(mock_db):
    add_structure({"name": "Home", "rooms": {}})
    add_room("Home", {"name": "Living Room", "devices": {}})
    with pytest.raises(InvalidInputError):
        update_room("Home", "Living Room", {"name": 123})

def test_delete_room(mock_db):
    add_structure({"name": "Home", "rooms": {}})
    add_room("Home", {"name": "Living Room", "devices": {}})
    delete_room("Home", "Living Room")
    assert "Living Room" not in mock_db["structures"]["Home"]["rooms"]

def test_delete_nonexistent_room(mock_db):
    add_structure({"name": "Home", "rooms": {}})
    with pytest.raises(DeviceNotFoundError, match="Room 'NonExistentRoom' in structure 'Home' not found."):
        delete_room("Home", "NonExistentRoom")
# endregion

# region Device Tests
@pytest.fixture
def device_data():
    return {
        "id": "light-123",
        "names": ["Main Light"],
        "types": ["LIGHT"],
        "traits": ["OnOff"],
        "room_name": "Living Room",
        "structure": "Home",
        "toggles_modes": [],
        "device_state": [{"name": "on", "value": False}],
    }

def test_add_device(mock_db, device_data):
    add_structure({"name": "Home", "rooms": {}})
    add_room("Home", {"name": "Living Room", "devices": {}})
    result = add_device("Home", "Living Room", device_data)
    assert result["id"] == "light-123"
    assert result in mock_db["structures"]["Home"]["rooms"]["Living Room"]["devices"]["LIGHT"]

def test_add_device_to_nonexistent_room(mock_db, device_data):
    with pytest.raises(DeviceNotFoundError, match="Room 'NonExistentRoom' in structure 'Home' not found."):
        add_device("Home", "NonExistentRoom", device_data)

def test_add_existing_device(mock_db, device_data):
    add_structure({"name": "Home", "rooms": {}})
    add_room("Home", {"name": "Living Room", "devices": {}})
    add_device("Home", "Living Room", device_data)
    with pytest.raises(InvalidInputError, match="Device with ID 'light-123' already exists."):
        add_device("Home", "Living Room", device_data)

def test_add_invalid_device(mock_db):
    add_structure({"name": "Home", "rooms": {}})
    add_room("Home", {"name": "Living Room", "devices": {}})
    with pytest.raises(InvalidInputError):
        add_device("Home", "Living Room", {"id": "invalid-device"}) # Missing fields

def test_get_device(mock_db, device_data):
    add_structure({"name": "Home", "rooms": {}})
    add_room("Home", {"name": "Living Room", "devices": {}})
    add_device("Home", "Living Room", device_data)
    result = get_device("light-123")
    assert result is not None
    assert result["id"] == "light-123"

def test_get_nonexistent_device(mock_db):
    assert get_device("nonexistent-device") is None

def test_update_device(mock_db, device_data):
    add_structure({"name": "Home", "rooms": {}})
    add_room("Home", {"name": "Living Room", "devices": {}})
    add_device("Home", "Living Room", device_data)
    update_data = {"names": ["New Main Light"]}
    result = update_device("light-123", update_data)
    assert result["names"] == ["New Main Light"]
    assert get_device("light-123")["names"] == ["New Main Light"]

def test_update_nonexistent_device(mock_db):
    with pytest.raises(DeviceNotFoundError, match="Device with ID 'nonexistent-device' not found."):
        update_device("nonexistent-device", {"names": ["New Name"]})

def test_update_device_with_invalid_data(mock_db, device_data):
    add_structure({"name": "Home", "rooms": {}})
    add_room("Home", {"name": "Living Room", "devices": {}})
    add_device("Home", "Living Room", device_data)
    with pytest.raises(InvalidInputError):
        update_device("light-123", {"traits": ["InvalidTrait"]})

def test_delete_device(mock_db, device_data):
    add_structure({"name": "Home", "rooms": {}})
    add_room("Home", {"name": "Living Room", "devices": {}})
    add_device("Home", "Living Room", device_data)
    delete_device("light-123")
    assert get_device("light-123") is None

def test_delete_nonexistent_device(mock_db):
    with pytest.raises(DeviceNotFoundError, match="Device with ID 'nonexistent-device' not found."):
        delete_device("nonexistent-device")
# endregion