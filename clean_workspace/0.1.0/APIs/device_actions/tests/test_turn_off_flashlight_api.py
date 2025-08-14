
import pytest
from device_actions.turn_off_flashlight_api import turn_off_flashlight
from device_actions.SimulationEngine.db import DB
from device_actions.SimulationEngine.models import PhoneState
from device_actions.SimulationEngine.utils import get_phone_state, update_phone_state

@pytest.fixture(autouse=True)
def clear_db():
    DB["phone_state"] = PhoneState().model_dump(mode="json")
    yield

def test_turn_off_flashlight():
    update_phone_state({"flashlight_on": True})
    result = turn_off_flashlight()
    assert result["result"] == "Turned off flashlight"



    assert get_phone_state().flashlight_on is False

def test_turn_off_flashlight_already_off():
    result = turn_off_flashlight()
    assert result["result"] == "Flashlight is already off."



    assert get_phone_state().flashlight_on is False
