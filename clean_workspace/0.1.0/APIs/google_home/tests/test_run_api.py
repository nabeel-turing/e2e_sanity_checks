import pytest
from google_home.run_api import run
from google_home.SimulationEngine.db import DB
from google_home.SimulationEngine.custom_errors import (
    InvalidInputError,
    DeviceNotFoundError,
)


class TestRun:
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

    def test_run_valid(self):
        """
        Test run with valid inputs.
        """
        results = run(
            devices=["light-1"],
            op="on",
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
        assert action["action_type"] == "run"
        assert action["inputs"]["devices"] == ["light-1"]

    def test_run_invalid_device_id(self):
        """
        Test run with an invalid device ID.
        """
        with pytest.raises(DeviceNotFoundError):
            run(
                devices=["invalid-device"],
                op="on",
            )

    def test_run_provided_values_for_command_not_requiring_values(self):
        """
        Test run with provided values for a command that does not require values.
        """
        with pytest.raises(ValueError):
            run(
                devices=["light-1"],
                op="on",
                values=["true"],
            )

    def test_run_invalid_op(self):
        """
        Test run with an invalid operation.
        """
        with pytest.raises(InvalidInputError):
            run(
                devices=["light-1"],
                op="InvalidOp",
                values=["true"],
            )