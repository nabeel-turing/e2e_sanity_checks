
import pytest
from device_actions.turn_on_flashlight_api import turn_on_flashlight
from device_actions.SimulationEngine.db import DB
from device_actions.SimulationEngine.models import PhoneState
from device_actions.SimulationEngine.utils import get_phone_state, update_phone_state

@pytest.fixture(autouse=True)
def clear_db():
    DB["phone_state"] = PhoneState().model_dump(mode="json")
    yield

def test_turn_on_flashlight():
    result = turn_on_flashlight()
    assert result["result"] == "Turned on flashlight"


    assert get_phone_state().flashlight_on is True

def test_turn_on_flashlight_already_on():
    update_phone_state({"flashlight_on": True})
    result = turn_on_flashlight()
    assert result["result"] == "Flashlight is already on."



    assert get_phone_state().flashlight_on is True
