from typing import Any, Dict
from pydantic import ValidationError
from retail.SimulationEngine.custom_errors import InvalidInputError
from retail.SimulationEngine.models import ThinkInput


def think(thought: str) -> str:
    """Use the tool to think about something.

    It will not obtain new information or change the database, but just append
    the thought to the log. Use it when complex reasoning or some cache memory
    is needed.

    Args:
        thought (str): A thought to think about.

    Returns:
        str: An empty string.

    Raises:
        InvalidInputError: If the input is invalid.
    """
    try:
        ThinkInput(thought=thought)
    except ValidationError as e:
        raise InvalidInputError(e)

    return ""
