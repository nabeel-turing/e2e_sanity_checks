from typing import Dict, Any, Literal
from pydantic import BaseModel, Field, ValidationError, field_validator
import re # For regex validation

class PostDataModel(BaseModel):
    """Pydantic model for validating the structure of post_data."""
    author: str = Field(..., description="URN of the post author")
    commentary: str = Field(..., description="Content of the post")
    visibility: Literal['PUBLIC', 'CONNECTIONS', 'LOGGED_IN', 'CONTAINER'] = Field(
        ..., description="Visibility setting of the post"
    )

    @field_validator('author')
    @classmethod
    def check_author_urn_format(cls, value):
        """Validates the URN format for the author field."""
        # Simple regex based on examples: urn:li:(person|organization):<digits>
        urn_pattern = r'^urn:li:(person|organization):\d+$'
        if not re.match(urn_pattern, value):
            raise ValueError(f"Invalid author URN format: '{value}'. Expected format like 'urn:li:person:1' or 'urn:li:organization:1'.")
        return value