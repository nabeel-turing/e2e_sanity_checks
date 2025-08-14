import pytest
from google_home.cancel_schedules_api import cancel_schedules
from google_home.SimulationEngine.db import DB
from google_home.SimulationEngine.custom_errors import (
    InvalidInputError,
    DeviceNotFoundError,
)


class TestCancelSchedules:
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
                                        {
                                            "name": "schedules",
                                            "value": [
                                                {
                                                    "start_time": "2025-07-15T19:00:00",
                                                    "action": "on",
                                                }
                                            ],
                                        },
                                    ],
                                }
                            ]
                        },
                    }
                },
            }
        }

    def test_cancel_schedules_all_devices(self):
        """
        Test cancel_schedules with no devices specified.
        """
        result = cancel_schedules()
        assert result["success"] is True
        assert result["operation_type"] == "CANCEL_SCHEDULES"
        device = DB["structures"]["Home"]["rooms"]["Living Room"]["devices"]["LIGHT"][0]
        assert len(device["device_state"][2]["value"]) == 0

    def test_cancel_schedules_valid_devices(self):
        """
        Test cancel_schedules with valid device IDs.
        """
        result = cancel_schedules(devices=["light-1"])
        assert result["success"] is True
        assert result["operation_type"] == "CANCEL_SCHEDULES"
        device = DB["structures"]["Home"]["rooms"]["Living Room"]["devices"]["LIGHT"][0]
        assert len(device["device_state"][2]["value"]) == 0

    def test_cancel_schedules_invalid_device_id(self):
        """
        Test cancel_schedules with an invalid device ID.
        """
        with pytest.raises(DeviceNotFoundError):
            cancel_schedules(devices=["invalid-device"])

    def test_cancel_schedules_mixed_valid_and_invalid_devices(self):
        """
        Test cancel_schedules with a mix of valid and invalid device IDs.
        """
        with pytest.raises(DeviceNotFoundError):
            cancel_schedules(devices=["light-1", "invalid-device"])

    def test_cancel_schedules_invalid_input_type(self):
        """
        Test cancel_schedules with invalid input type for devices.
        """
        with pytest.raises(InvalidInputError):
            cancel_schedules(devices="not-a-list")

    def test_cancel_schedules_no_schedules_to_cancel(self):
        """
        Test cancel_schedules when there are no schedules to cancel.
        """
        # Clear existing schedules
        device = DB["structures"]["Home"]["rooms"]["Living Room"]["devices"]["LIGHT"][0]
        device["device_state"][2]["value"] = []

        result = cancel_schedules(devices=["light-1"])
        assert result["success"] is True
        assert result["operation_type"] == "CANCEL_SCHEDULES"
        assert len(device["device_state"][2]["value"]) == 0

    def test_cancel_schedules_multiple_devices(self):
        """
        Test cancel_schedules with multiple devices.
        """
        DB["structures"]["Home"]["rooms"]["Bedroom"] = {
            "name": "Bedroom",
            "devices": {
                "LIGHT": [
                    {
                        "id": "light-2",
                        "names": ["Bedroom Light"],
                        "types": ["LIGHT"],
                        "traits": ["OnOff"],
                        "room_name": "Bedroom",
                        "structure": "Home",
                        "toggles_modes": [],
                        "device_state": [
                            {"name": "on", "value": False},
                            {
                                "name": "schedules",
                                "value": [
                                    {
                                        "start_time": "2025-07-15T22:00:00",
                                        "action": "off",
                                    }
                                ],
                            },
                        ],
                    }
                ]
            },
        }

        result = cancel_schedules(devices=["light-1", "light-2"])
        assert result["success"] is True
        assert result["operation_type"] == "CANCEL_SCHEDULES"
        device1 = DB["structures"]["Home"]["rooms"]["Living Room"]["devices"]["LIGHT"][
            0
        ]
        device2 = DB["structures"]["Home"]["rooms"]["Bedroom"]["devices"]["LIGHT"][0]
        assert len(device1["device_state"][2]["value"]) == 0
        assert len(device2["device_state"][1]["value"]) == 0

    def test_cancel_schedules_empty_devices_list(self):
        """
        Test cancel_schedules with an empty list of devices.
        """
        result = cancel_schedules(devices=[])
        assert result["success"] is True
        assert result["operation_type"] == "CANCEL_SCHEDULES"
        # No schedules should be canceled if devices list is empty
        device = DB["structures"]["Home"]["rooms"]["Living Room"]["devices"]["LIGHT"][0]
        assert len(device["device_state"][2]["value"]) == 0
        
    def test_cancel_schedules_no_devices_in_db(self):
        """
        Test cancel_schedules when there are no devices in the database.
        """
        original_structures = DB.get("structures")
        DB["structures"] = {}

        result = cancel_schedules()
        assert result["success"] is True
        assert result["operation_type"] == "CANCEL_SCHEDULES"

        DB["structures"] = original_structures

    def test_cancel_schedules_device_without_schedules_trait(self):
        """
        Test cancel_schedules for a device that does not have a 'schedules' trait.
        """
        DB["structures"]["Home"]["rooms"]["Living Room"]["devices"]["THERMOSTAT"] = [
            {
                "id": "thermostat-1",
                "names": ["Living Room Thermostat"],
                "types": ["THERMOSTAT"],
                "traits": ["TemperatureSetting"],
                "room_name": "Living Room",
                "structure": "Home",
                "toggles_modes": [],
                "device_state": [{"name": "temperature", "value": 22}],
            }
        ]

        result = cancel_schedules(devices=["thermostat-1"])
        assert result["success"] is True
        assert result["operation_type"] == "CANCEL_SCHEDULES"
        
        del DB["structures"]["Home"]["rooms"]["Living Room"]["devices"]["THERMOSTAT"]

    def test_cancel_schedules_device_with_empty_schedules(self):
        """
        Test cancel_schedules for a device with an empty 'schedules' list.
        """
        device = DB["structures"]["Home"]["rooms"]["Living Room"]["devices"]["LIGHT"][0]
        device["device_state"][2]["value"] = []

        result = cancel_schedules(devices=["light-1"])
        assert result["success"] is True
        assert result["operation_type"] == "CANCEL_SCHEDULES"
        assert len(device["device_state"][2]["value"]) == 0
        
        # Restore the schedule for other tests
        device["device_state"][2]["value"] = [
            {"start_time": "2025-07-15T19:00:00", "action": "on"}
        ]

    def test_cancel_schedules_no_rooms_in_structure(self):
        """
        Test cancel_schedules with a structure that has no rooms.
        """
        original_structures = DB.get("structures")
        DB["structures"] = {"Home": {"name": "Home", "rooms": {}}}

        result = cancel_schedules()
        assert result["success"] is True
        assert result["operation_type"] == "CANCEL_SCHEDULES"

        DB["structures"] = original_structures

    def test_cancel_schedules_no_devices_in_room(self):
        """
        Test cancel_schedules with a room that has no devices.
        """
        original_structures = DB.get("structures")
        DB["structures"] = {
            "Home": {
                "name": "Home",
                "rooms": {"Living Room": {"name": "Living Room", "devices": {}}},
            }
        }

        result = cancel_schedules()
        assert result["success"] is True
        assert result["operation_type"] == "CANCEL_SCHEDULES"

        DB["structures"] = original_structures

    def test_cancel_schedules_no_structures(self):
        """
        Test cancel_schedules with no structures in the database.
        """
        original_structures = DB.get("structures")
        DB["structures"] = {}

        result = cancel_schedules()
        assert result["success"] is True
        assert result["operation_type"] == "CANCEL_SCHEDULES"

        DB["structures"] = original_structures
