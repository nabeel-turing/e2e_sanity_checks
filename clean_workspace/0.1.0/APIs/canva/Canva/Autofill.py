# canva/Canva/Autofill.py

from typing import Optional, Dict, Any
import uuid
import sys
import os

sys.path.append("APIs")

from canva.Canva.BrandTemplate import get_brand_template
from canva.Canva.Design import create_design
import canva


def create_autofill_job(
    brand_template_id: str, data: Dict[str, Any], title: Optional[str] = None
) -> Dict[str, Any]:
    """
    Creates an asynchronous job to autofill a design from a brand template with input data.

    Args:
        brand_template_id (str): ID of the input brand template.
        data (Dict[str, Any]): Dictionary of data fields to autofill. Each key maps to a field object with:
            - type (str): Required. One of "image", "text", or "chart".
            - asset_id (str, optional): Required if type is "image".
            - text (str, optional): Required if type is "text".
            - chart_data (dict, optional): Required if type is "chart". Structure:
                - rows (List[dict]): List of rows, where each row contains:
                    - cells (List[dict]): List of cells, each with:
                        - type (str): One of "string", "number", "boolean", "date".
                        - value: Value of the cell.
        title (Optional[str]): Optional title for the autofilled design. If not provided, defaults to the template's title.

    Returns:
        Dict[str, Any]: A dictionary representing the created autofill job, including:
            - id (str): Unique ID of the autofill job.
            - status (str): Status of the job. One of "success", "in_progress", or "failed".
            - result (dict, optional): Present only if status is "success". Includes:
                - type (str): "create_design"
                - design (dict):
                    - id (str): Design ID.
                    - title (str): Design title.
                    - url (str): Permanent URL to the design (if available).
                    - thumbnail (dict, optional):
                        - width (int)
                        - height (int)
                        - url (str): Thumbnail URL (expires in 15 minutes).
    """
    template = get_brand_template(brand_template_id)
    asset_id = "test_asset_id" if not 'asset_id' in data else data.get("asset_id")
    if not title:
        title = template.get("brand_template", {}).get("title", None)
    create_design(
        template.get("brand_template", {}).get("design_type", {}),
        asset_id=asset_id,
        title=title,
    )

    job_id = str(uuid.uuid4())
    job_entry = {
        "id": job_id,
        "status": "success",
        "result": {
            "type": "create_design",
            "design": {
                "id": brand_template_id,
                "title": title,
                "url": f"https://www.canva.com/design/{brand_template_id}/edit",
                "thumbnail": canva.SimulationEngine.db.DB["Designs"]
                .get(brand_template_id, {})
                .get("thumbnail", {}),
            },
        },
    }
    canva.SimulationEngine.db.DB["autofill_jobs"][job_id] = job_entry
    return job_entry


def get_autofill_job(job_id: str) -> Dict[str, Any]:
    """
    Retrieves the status and results of an autofill job by its ID.

    Args:
        job_id (str): The ID of the autofill job to retrieve.

    Returns:
        Dict[str, Any]: If found, returns job details:
            - id (str): Job ID.
            - status (str): Job status ("in_progress", "success", "failed").
            - result (dict, optional): Present only if status is "success". Includes:
                - type (str): "create_design"
                - design (dict):
                    - id (str): Design ID.
                    - title (str): Design title.
                    - url (str, optional): Permanent URL of the design.
                    - thumbnail (dict, optional):
                        - width (int)
                        - height (int)
                        - url (str): Thumbnail URL (expires in 15 minutes).
        If not found, returns:
            - error (str): Error message ("Job not found").
    """
    return canva.SimulationEngine.db.DB["autofill_jobs"].get(
        job_id, {"error": "Job not found"}
    )
