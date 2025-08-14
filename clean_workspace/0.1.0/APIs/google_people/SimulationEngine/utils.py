import uuid
from typing import Dict, Any, List


def generate_id() -> str:
    """Generate a unique identifier"""
    return str(uuid.uuid4())


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> None:
    """
    Validate that required fields are present in the data dictionary.
    
    Args:
        data: The data dictionary to validate
        required_fields: List of field names that must be present
        
    Raises:
        ValueError: If any required field is missing
    """
    missing_fields = []
    for field in required_fields:
        if field not in data or data[field] is None:
            missing_fields.append(field)
    
    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
