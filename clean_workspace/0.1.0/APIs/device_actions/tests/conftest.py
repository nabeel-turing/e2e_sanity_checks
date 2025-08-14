import pytest
from unittest.mock import patch, MagicMock

def pytest_addoption(parser):
    parser.addoption(
        "--use-real-api", action="store_true", default=False, help="run tests that use the real API"
    )

@pytest.fixture(autouse=True)
def llm_mocker(request):
    if request.config.getoption("--use-real-api"):
        yield None
        return

    mock_llm = MagicMock()

    patcher1 = patch('device_actions.record_video_api.call_llm', new=mock_llm)
    patcher2 = patch('device_actions.take_photo_api.call_llm', new=mock_llm)
    patcher3 = patch('device_actions.open_app_api.call_llm', new=mock_llm)

    patcher1.start()
    patcher2.start()
    patcher3.start()

    yield mock_llm

    patcher1.stop()
    patcher2.stop()
    patcher3.stop()
