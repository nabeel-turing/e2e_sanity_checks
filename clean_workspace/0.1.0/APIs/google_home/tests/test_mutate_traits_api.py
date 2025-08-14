import pytest
from google_home.mutate_traits_api import mutate_traits
from google_home.SimulationEngine.db import DB
from google_home.SimulationEngine.custom_errors import (
    InvalidInputError,
    DeviceNotFoundError,
)


class TestMutateTraits:
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
                                        {"name": "on", "value": False},
                                        {"name": "brightness", "value": 0.5},
                                    ],
                                }
                            ]
                        },
                    }
                },
            }
        }
        DB["actions"] = []

    def test_mutate_traits_valid(self):
        """
        Test mutate_traits with valid inputs.
        """
        # For OnOff/on, command_values should be [] (no value), not ["true"]
        results = mutate_traits(
            device_ids=["light-1"],
            trait_names=["OnOff"],
            command_names=["on"],
            command_values=[],
        )
        assert len(results) == 1
        assert results[0]["result"] == "SUCCESS"
        assert results[0]["commands"]["device_ids"] == ["light-1"]

        # Verify that the device state was updated
        device = DB["structures"]["Home"]["rooms"]["Living Room"]["devices"]["LIGHT"][0]
        assert device["device_state"][0]["value"] is True

        # Verify that the action was logged
        assert len(DB["actions"]) == 1
        action = DB["actions"][0]
        assert action["action_type"] == "mutate_traits"
        assert action["inputs"]["device_ids"] == ["light-1"]

    def test_mutate_traits_invalid_device_id(self):
        """
        Test mutate_traits with an invalid device ID.
        """
        # For OnOff/on, command_values should be [] (no value), not ["true"]
        with pytest.raises(DeviceNotFoundError):
            mutate_traits(
                device_ids=["invalid-device"],
                trait_names=["OnOff"],
                command_names=["on"],
                command_values=[],
            )

    def test_mutate_traits_invalid_trait(self):
        """
        Test mutate_traits with an invalid trait.
        """
        with pytest.raises(InvalidInputError):
            mutate_traits(
                device_ids=["light-1"],
                trait_names=["InvalidTrait"],
                command_names=["on"],
            )

    def test_mutate_traits_invalid_command(self):
        """
        Test mutate_traits with an invalid command.
        """
        with pytest.raises(InvalidInputError):
            mutate_traits(
                device_ids=["light-1"],
                trait_names=["OnOff"],
                command_names=["InvalidCommand"],
                command_values=[],
            )