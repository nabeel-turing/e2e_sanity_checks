from typing import Optional, Literal
from pydantic import BaseModel

class DesignTypeInputModel(BaseModel):
    """
    Pydantic model for validating the 'design_type' dictionary.
    The 'preset' field is derived from the docstring example "preset like 'doc'".
    It is Optional, allowing 'design_type' to be an empty dictionary ({})
    or include the preset (e.g., {"preset": "doc"}), or {"preset": null}.
    """
    preset: Optional[
        Literal[
            'doc', 
            'whiteboard', 
            'presentation', 
            'canvas', 
            'banner', 
            'flyer', 
            'social', 
            'video', 
            'infographic', 
            'poster'
        ]
    ] = None
    
