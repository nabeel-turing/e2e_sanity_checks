import pytest
from google_home.mutate_api import mutate
from google_home.SimulationEngine.db import DB
from google_home.SimulationEngine.custom_errors import (
    InvalidInputError,
    DeviceNotFoundError,
)
from pydantic import ValidationError


class TestMutate:
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

    def test_mutate_valid(self):
        """
        Test mutate with valid inputs.
        """
        # The new validation requires that "on" does NOT have values
        results = mutate(
            devices=["light-1"],
            traits=["OnOff"],
            commands=["on"],
            values=[],  # No values for "on"
        )
        assert len(results) == 1
        assert results[0]["result"] == "SUCCESS"
        assert results[0]["commands"]["device_ids"] == ["light-1"]

        # Verify that the device state was updated
        device = DB["structures"]["Home"]["rooms"]["Living Room"]["devices"]["LIGHT"][0]
        on_state = next(s for s in device["device_state"] if s["name"] == "on")
        assert on_state["value"] is True

        # Verify that the action was logged
        assert len(DB["actions"]) == 1
        action = DB["actions"][0]
        assert action["action_type"] == "mutate"
        assert action["inputs"]["devices"] == ["light-1"]

    def test_mutate_invalid_device_id(self):
        """
        Test mutate with an invalid device ID.
        """
        # The new validation will fail on input if values are provided for "on"
        with pytest.raises(DeviceNotFoundError):
            mutate(
                devices=["invalid-device"],
                traits=["OnOff"],
                commands=["on"],
                values=[],  # No values for "on"
            )

    def test_mutate_invalid_trait(self):
        """
        Test mutate with an invalid trait.
        """
        # The new model validation may raise ValidationError or InvalidInputError
        with pytest.raises((InvalidInputError, ValidationError)):
            mutate(
                devices=["light-1"],
                traits=["InvalidTrait"],
                commands=["on"],
                values=[],  # No values for "on"
            )

    def test_mutate_invalid_command(self):
        """
        Test mutate with an invalid command.
        """
        # The new model validation may raise ValidationError or InvalidInputError
        with pytest.raises((InvalidInputError, ValidationError)):
            mutate(
                devices=["light-1"],
                traits=["OnOff"],
                commands=["InvalidCommand"],
                values=[],  # No values for "on"
            )