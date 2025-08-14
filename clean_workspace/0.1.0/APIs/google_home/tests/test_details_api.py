import pytest
from google_home.details_api import details
from google_home.SimulationEngine.db import DB
from google_home.SimulationEngine.custom_errors import (
    InvalidInputError,
    DeviceNotFoundError,
)


class TestDetails:
    @classmethod
    def setup_class(cls):
        """
        Clear the database and set up with test-specific data.
        """
        DB.clear()
        DB["structures"] = {
            "Home": {
                "name": "Home",
                "rooms": {
                    "Living Room": {
                        "name": "Living Room",
                        "devices": {
                            "LIGHT": [
                                {
                                    "id": "light-1",
                                    "names": ["Living Room Light"],
                                    "types": ["LIGHT"],
                                    "traits": ["OnOff", "Brightness"],
                                    "room_name": "Living Room",
                                    "structure": "Home",
                                    "toggles_modes": [],
                                    "device_state": [
                                        {"name": "on", "value": True},
                                        {"name": "brightness", "value": 0.5},
                                    ],
                                }
                            ]
                        },
                    }
                },
            }
        }

    def test_details_valid_devices(self):
        """
        Test details with valid device IDs.
        """
        result = details(devices=["light-1"])
        assert "light-1" in result["devices_info"]

    def test_details_invalid_device_id(self):
        """
        Test details with an invalid device ID.
        """
        with pytest.raises(DeviceNotFoundError):
            details(devices=["invalid-device"])

    def test_details_empty_device_list(self):
        """
        Test details with an empty list of device IDs.
        """
        with pytest.raises(InvalidInputError):
            details(devices="[]")

    def test_details_mixed_valid_and_invalid_devices(self):
        """
        Test details with a mix of valid and invalid device IDs.
        """
        with pytest.raises(DeviceNotFoundError):
            details(devices=["light-1", "invalid-device"])