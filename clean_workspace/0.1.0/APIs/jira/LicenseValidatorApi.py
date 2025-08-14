# APIs/jira/LicenseValidatorApi.py
from .SimulationEngine.utils import _check_empty_field
from typing import Dict, Any


def validate_license(license: str) -> Dict[str, Any]:
    """
    Validate a license.

    This method validates a license.

    Args:
        license (str): The license to validate

    Returns:
        Dict[str, Any]: A dictionary containing:
            - valid (bool): Whether the license is valid
            - decoded (str): The decoded license

    Raises:
        ValueError: If the license is not found
    """
    err = _check_empty_field("license", license)
    if err:
        return {"error": err}
    # Fake decode
    return {"valid": True, "decoded": f"DecodedLicense({license[:10]}...)"}
