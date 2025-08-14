# APIs/hubspot/MarketingEmails.py
from typing import Dict, Any, Union, Optional
import uuid
from hubspot.SimulationEngine.db import DB


def create(
    name: str,
    subject: Optional[str] = None,
    htmlBody: Optional[str] = None,
    isTransactional: Optional[bool] = False,
    status: Optional[str] = None,
    discount_code: Optional[str] = None,
    expiration: Optional[str] = None,
    launch_date: Optional[str] = None,
    sale_end_date: Optional[str] = None,
    reward_points: Optional[int] = None,
    access_code: Optional[str] = None,
) -> Dict[str, Any]:
    """Creates a new marketing email.

    Args:
        name(str): The internal name of the email (required).
        subject(Optional[str]): The email subject line. Default is None.
        htmlBody(Optional[str]): The HTML body of the email. Default is None.
        isTransactional(Optional[bool]): Whether this is a transactional email. Default is False.
        status(Optional[str]): The status of the email (e.g. 'scheduled', 'sent'). Default is None.
        discount_code(Optional[str]): Discount code for promotional emails. Default is None.
        expiration(Optional[str]): Expiration date for time-limited offers. Default is None.
        launch_date(Optional[str]): Launch date for product announcements. Default is None.
        sale_end_date(Optional[str]): End date for sales promotions. Default is None.
        reward_points(Optional[int]): Number of reward points for loyalty program emails. Default is None.
        access_code(Optional[str]): Access code for VIP or exclusive offers. Default is None.

    Returns:
        Dict[str, Any]: A dictionary containing the new email's ID and a success message, or an error message.
        - email_id(str): The unique ID of the marketing email.
        - success(bool): Whether the email was created successfully.
        - message(str): A message indicating the success or failure of the email creation.
    """

    if not isinstance(name, str) or not name:
        return {"success": False, "message": "Name must be a non-empty string."}
    # Find next available email_id

    email_id = str(uuid.uuid4())

    DB["marketing_emails"][email_id] = {
        "name": name,
        "subject": subject,
        "htmlBody": htmlBody,
        "isTransactional": isTransactional,
        "status": status,
        "discount_code": discount_code,
        "expiration": expiration,
        "launch_date": launch_date,
        "sale_end_date": sale_end_date,
        "reward_points": reward_points,
        "access_code": access_code,
    }
    return {
        "success": True,
        "message": "Marketing email created successfully.",
        "email_id": email_id,
    }


def getById(email_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves a marketing email by its ID.
    Args:
        email_id(str): The unique ID of the marketing email (required).

    Returns:
        Optional[Dict[str, Any]]: The marketing email object if found, or None if not found.
            - email_id(str): The unique ID of the marketing email.
            - name(str): The internal name of the email.
            - subject(str): The email subject line.
            - htmlBody(str): The HTML body of the email.
            - isTransactional(bool): Whether the email is transactional.
            - status(str): The status of the email (e.g. 'scheduled', 'sent').
            - discount_code(str): Discount code for promotional emails.
            - expiration(str): Expiration date for time-limited offers.
            - launch_date(str): Launch date for product announcements.
            - sale_end_date(str): End date for sales promotions.
            - reward_points(int): Number of reward points for loyalty program emails.
            - access_code(str): Access code for VIP or exclusive offers.
        None: If the email is not found.
    """

    email = DB["marketing_emails"].get(email_id)

    return email if email else None


def update(
    email_id: str,
    name: Optional[str] = None,
    subject: Optional[str] = None,
    htmlBody: Optional[str] = None,
    isTransactional: Optional[bool] = None,
    status: Optional[str] = None,
    discount_code: Optional[str] = None,
    expiration: Optional[str] = None,
    launch_date: Optional[str] = None,
    sale_end_date: Optional[str] = None,
    reward_points: Optional[int] = None,
    access_code: Optional[str] = None,
) -> Dict[str, Any]:
    """Updates an existing marketing email.

    Args:
        email_id(str): The unique ID of the marketing email to update (required).
        name(Optional[str]): The internal name of the email.
        subject(Optional[str]): The email subject line.
        htmlBody(Optional[str]): The HTML body of the email.
        isTransactional(Optional[bool]): Whether this is a transactional email.
        status(Optional[str]): The status of the email (e.g. 'scheduled', 'sent').
        discount_code(Optional[str]): Discount code for promotional emails.
        expiration(Optional[str]): Expiration date for time-limited offers.
        launch_date(Optional[str]): Launch date for product announcements.
        sale_end_date(Optional[str]): End date for sales promotions.
        reward_points(Optional[int]): Number of reward points for loyalty program emails.
        access_code(Optional[str]): Access code for VIP or exclusive offers.

    Returns:
        Dict[str, Any]: A dictionary indicating success or failure and a message.
        - success(bool): Whether the email was updated successfully.
        - message(str): A message indicating the success or failure of the email update.
    """
    if email_id not in DB["marketing_emails"]:
        return {"success": False, "message": "Marketing email not found."}

    update_data = {}
    if name is not None:
        update_data["name"] = name
    if subject is not None:
        update_data["subject"] = subject
    if htmlBody is not None:
        update_data["htmlBody"] = htmlBody
    if isTransactional is not None:
        update_data["isTransactional"] = isTransactional
    if status is not None:
        update_data["status"] = status
    if discount_code is not None:
        update_data["discount_code"] = discount_code
    if expiration is not None:
        update_data["expiration"] = expiration
    if launch_date is not None:
        update_data["launch_date"] = launch_date
    if sale_end_date is not None:
        update_data["sale_end_date"] = sale_end_date
    if reward_points is not None:
        update_data["reward_points"] = reward_points
    if access_code is not None:
        update_data["access_code"] = access_code

    DB["marketing_emails"][email_id].update(update_data)
    return {"success": True, "message": "Marketing email updated successfully."}


def delete(email_id: str) -> Dict[str, Any]:
    """Deletes a marketing email.

    Args:
        email_id(str): The unique ID of the marketing email to delete (required).

    Returns:
        Dict[str, Any]: A dictionary indicating success or failure and a message.
            - success(bool): Whether the email was deleted successfully.
            - message(str): A message indicating the success or failure of the email deletion.
    """
    if email_id not in DB["marketing_emails"]:
        return {"success": False, "message": "Marketing email not found."}

    del DB["marketing_emails"][email_id]
    return {"success": True, "message": "Marketing email deleted successfully."}


def clone(email_id: str, name: str) -> Dict[str, Any]:
    """Clones an existing marketing email.

    Args:
        email_id(str): The ID of the marketing email to clone (required).
        name(str): The name for the new, cloned email (required).

    Returns:
        Dict[str, Any]: A dictionary containing the new email's ID and a success message, or an error message.
            - email_id(str): The unique ID of the marketing email.
            - success(bool): Whether the email was cloned successfully.
            - message(str): A message indicating the success or failure of the email cloning.
    """
    if email_id not in DB["marketing_emails"]:
        return {"success": False, "message": "Marketing email not found."}

    original_email = DB["marketing_emails"][email_id]
    # Find next available email_id
    next_id = str(uuid.uuid4())

    DB["marketing_emails"][next_id] = original_email.copy()  # Create a shallow copy
    DB["marketing_emails"][next_id]["name"] = name

    return {
        "success": True,
        "message": "Marketing email cloned successfully.",
        "email_id": next_id,
    }
