"""
Contract Management Module for Workday Strategic Sourcing API Simulation.

This module provides comprehensive functionality for managing contracts and contract types
in the Workday Strategic Sourcing system. It supports CRUD operations for both contracts
and contract types, with support for filtering, pagination, and relationship inclusion.
The module handles both internal IDs and external IDs for contract identification.
"""

from typing import List, Dict, Optional
from .SimulationEngine import db

def get(filter: Optional[Dict] = None, _include: Optional[str] = None, page: Optional[Dict] = None) -> List[Dict]:
    """
    Retrieve a list of contracts based on specified criteria.

    This function supports filtering, relationship inclusion, and pagination of contracts.
    Contracts can be filtered based on any attribute present in the contract object.

    Args:
        filter (Optional[Dict]): Dictionary containing filter criteria for contracts. Supported filters:
            - updated_at_from (str): Return contracts updated on or after timestamp
            - updated_at_to (str): Return contracts updated on or before timestamp
            - number_from (str): Find contracts with number >= specified
            - number_to (str): Find contracts with number <= specified
            - title_contains (str): Return contracts with title containing string
            - title_not_contains (str): Return contracts with title not containing string
            - description_contains (str): Return contracts with description containing string
            - description_not_contains (str): Return contracts with description not containing string
            - external_id_empty (bool): Return contracts with blank external_id
            - external_id_not_empty (bool): Return contracts with non-blank external_id
            - external_id_equals (str): Find contracts by specific external ID
            - external_id_not_equals (str): Find contracts excluding specified external ID
            - actual_start_date_from (str): Return contracts started on or after date
            - actual_start_date_to (str): Return contracts started on or before date
            - actual_end_date_from (str): Return contracts ended on or after date
            - actual_end_date_to (str): Return contracts ended on or before date
            - actual_spend_amount_from (float): Return contracts with spend >= amount
            - actual_spend_amount_to (float): Return contracts with spend <= amount
            - auto_renewal (List[str]): Auto-renewal mode ("yes", "no", "evergreen")
            - needs_attention_equals (bool): Return contracts with specified needs attention status
            - needs_attention_not_equals (bool): Return contracts with needs attention status not equal
            - renew_number_of_times_from (int): Find contracts renewing >= specified times
            - renew_number_of_times_to (int): Find contracts renewing <= specified times
            - state_equals (List[str]): Find contracts with specified states
            - terminated_note_contains (str): Return contracts with termination note containing string
            - terminated_note_not_contains (str): Return contracts with termination note not containing string
            - terminated_note_empty (str): Return contracts with empty termination note
            - terminated_note_not_empty (str): Return contracts with non-empty termination note
            - terminated_reason_contains (str): Return contracts with termination reason containing string
            - terminated_reason_not_contains (str): Return contracts with termination reason not containing string
            - terminated_reason_empty (str): Return contracts with empty termination reason
            - terminated_reason_not_empty (str): Return contracts with non-empty termination reason
            - contract_type_id_equals (int): Find contracts with specified contract type
            - contract_type_id_not_equals (int): Find contracts with different contract type
            - marked_as_needs_attention_at_from (str): Find contracts marked needs attention after date
            - marked_as_needs_attention_at_to (str): Find contracts marked needs attention before date
            - needs_attention_note_contains (str): Return contracts with needs attention note containing string
            - needs_attention_note_not_contains (str): Return contracts with needs attention note not containing string
            - needs_attention_note_empty (str): Return contracts with empty needs attention note
            - needs_attention_note_not_empty (str): Return contracts with non-empty needs attention note
            - needs_attention_reason_contains (str): Return contracts with needs attention reason containing string
            - needs_attention_reason_not_contains (str): Return contracts with needs attention reason not containing string
            - needs_attention_reason_empty (str): Return contracts with empty needs attention reason
            - needs_attention_reason_not_empty (str): Return contracts with non-empty needs attention reason
            - renewal_termination_notice_date_from (str): Find contracts with termination notice date >= specified
            - renewal_termination_notice_date_to (str): Find contracts with termination notice date <= specified
            - renewal_termination_reminder_date_from (str): Find contracts with termination reminder date >= specified
            - renewal_termination_reminder_date_to (str): Find contracts with termination reminder date <= specified
            - spend_category_id_equals (List[int]): Find contracts using specified Spend Category IDs
        _include (Optional[str]): Comma-separated list of relationships to include in response.
            Supported values: "contract_type", "spend_category", "supplier_company", 
            "docusign_envelopes", "adobe_sign_agreements"
        page (Optional[Dict]): Dictionary containing pagination parameters:
            - size (int): Number of results per page (default: 10, max: 100)

    Returns:
        List[Dict]: A list of contract dictionaries, where each contract contains any of the following keys:
            - type (str): Object type 
            - id (int): Contract identifier string
            - supplier_id (str): Supplier identifier
            - start_date (str): Contract start date
            - end_date (str): Contract end date
            - external_id (str): External contract identifier
            - attributes (dict): Contract attributes containing:
                - title (str): Contract title (max 255 characters)
                - description (str): Contract description
                - state (str): Current contract state ("draft", "requested", "in_progress", "out_for_approval", "approved", "active", "expired", "terminated")
                - state_label (str): Customer-specific contract state label
                - number (int): Contract number, generated sequentially
                - external_id (str): Customer provided unique contract identifier
                - actual_start_date (str): Contract start date
                - actual_end_date (str): Contract end date
                - actual_spend_amount (float): Actual spend amount
                - auto_renewal (str): Auto-renewal mode ("yes", "no", "evergreen")
                - marked_as_needs_attention_at (str): Date and time when contract was flagged as needs attention
                - needs_attention (bool): Whether contract needs attention
                - needs_attention_note (str): Notes on why contract needs attention
                - needs_attention_reason (str): Reason why contract needs attention
                - renew_number_of_times (int): Number of times contract should be renewed
                - renewal_term_unit (str): Term unit for renewals ("days", "weeks", "months", "years")
                - renewal_term_value (int): Number of term units between renewals
                - renewal_termination_notice_date (str): Date for termination notice
                - renewal_termination_notice_unit (str): Term unit for termination notice
                - renewal_termination_notice_value (int): Term units before end date for notice
                - renewal_termination_reminder_date (str): Date for termination reminder
                - renewal_termination_reminder_unit (str): Term unit for termination reminder
                - renewal_termination_reminder_value (int): Term units before notice for reminder
                - terminated_note (str): Termination notes
                - terminated_reason (str): Termination reason
                - updated_at (str): Last modification date
                - custom_fields (list): Custom field values
                - approved_at (str): Date and time of contract approval
                - approval_rounds (int): Times contract has been sent for approval
                - first_sent_for_approval_at (str): First approval request date
                - sent_for_approval_at (str): Last approval request date
                - public (bool): Public visibility of contract
            - relationships (dict): Contract relationships containing:
                - attachments (list): Contract attachments
                - supplier_company (dict): Associated supplier company
                - creator (dict): Contract creator
                - owner (dict): Contract owner
                - docusign_envelopes (list): Docusign envelopes
                - adobe_sign_agreements (list): Adobe Sign agreements
                - contract_type (dict): Contract type
                - spend_category (dict): Spend category
            - links (dict): Related links containing:
                - self (str): URL to the resource
    """
    contracts = list(db.DB["contracts"]["contracts"].values())
    if filter:
        contracts = [c for c in contracts if all(c.get(k) == v for k, v in filter.items())]
    if _include:
        # simulate include logic
        pass
    if page:
        contracts = contracts[:page.get("size", 50)]
    return contracts

def post(_include: Optional[str] = None, body: Optional[Dict] = None) -> Dict:
    """
    Create a new contract with the specified attributes.

    Args:
        _include (Optional[str]): Comma-separated list of relationships to include
            in the response. 
            Supported values: "contract_type", "spend_category", "supplier_company", "docusign_envelopes", "adobe_sign_agreements"
        body (Optional[Dict]): Dictionary containing contract creation data. Contains any of the following keys:
            - type (str): Required. Object type 
            - supplier_id (str): Supplier identifier
            - start_date (str): Contract start date
            - end_date (str): Contract end date
            - external_id (str): External contract identifier
            - attributes (dict): Required. Contract attributes containing:
                - title (str): Required. Contract title (max 255 characters)
                - description (str): Optional. Contract description
                - state (str): Required. Current contract state, one of:
                    - "draft"
                    - "requested"
                    - "in_progress"
                    - "out_for_approval"
                    - "approved"
                    - "active"
                    - "expired"
                    - "terminated"
                - state_label (str): Optional. Customer-specific contract state label
                - external_id (str): Optional. Customer provided unique contract identifier
                - actual_start_date (str): Optional. Contract start date
                - actual_end_date (str): Optional. Contract end date
                - actual_spend_amount (float): Optional. Actual spend amount
                - auto_renewal (str): Optional. Auto-renewal mode, one of:
                    - "yes"
                    - "no"
                    - "evergreen"
                - marked_as_needs_attention_at (str): Optional. Date when contract was flagged as needs attention
                - needs_attention (bool): Optional. Whether contract needs attention
                - needs_attention_note (str): Optional. Notes on why contract needs attention
                - needs_attention_reason (str): Optional. Reason why contract needs attention
                - renew_number_of_times (int): Optional. Number of times contract should be renewed
                - renewal_term_unit (str): Optional. Term unit for renewals, one of:
                    - "days"
                    - "weeks"
                    - "months"
                    - "years"
                - renewal_term_value (int): Optional. Number of term units between renewals
                - renewal_termination_notice_unit (str): Optional. Term unit for termination notice
                - renewal_termination_notice_value (int): Optional. Term units before end date for notice
                - renewal_termination_reminder_unit (str): Optional. Term unit for termination reminder
                - renewal_termination_reminder_value (int): Optional. Term units before notice for reminder
                - terminated_note (str): Optional. Termination notes
                - terminated_reason (str): Optional. Termination reason
                - custom_fields (List[Dict[str, Any]], optional): Optional. Custom field values
                - approval_rounds (int): Optional. Times contract has been sent for approval
                - public (bool): Optional. Public visibility of contract
            - relationships (dict): Required. Contract relationships containing:
                - owner (dict): Required. Contract owner with:
                    - type (str): Required. Object type
                    - id (int): Required. Owner identifier
                - supplier_company (dict): Required. Associated supplier company with:
                    - type (str): Required. Always "supplier_companies"
                    - id (int): Required. Supplier company identifier
                - contract_type (dict): Required. Contract type with:
                    - type (str): Required. Always "contract_types"
                    - id (int): Required. Contract type identifier
                - spend_category (dict): Optional. Spend category with:
                    - type (str): Required. Always "spend_categories"
                    - id (int): Required. Spend category identifier
                - payment_currency (dict): Optional. Payment currency with:
                    - type (str): Required. Always "payment_currencies"
                    - id (int): Required. Payment currency identifier

    Returns:
        Dict: The newly created contract object with any of the following keys:
            - type (str): Object type 
            - id (int): Contract identifier string
            - supplier_id (str): Supplier identifier
            - start_date (str): Contract start date
            - end_date (str): Contract end date
            - external_id (str): External contract identifier
            - attributes (dict): Contract attributes containing:
                - title (str): Contract title (max 255 characters)
                - description (str): Contract description
                - state (str): Current contract state ("draft", "requested", "in_progress", "out_for_approval", "approved", "active", "expired", "terminated")
                - state_label (str): Customer-specific contract state label
                - number (int): Contract number, generated sequentially
                - external_id (str): Customer provided unique contract identifier
                - actual_start_date (str): Contract start date
                - actual_end_date (str): Contract end date
                - actual_spend_amount (float): Actual spend amount
                - auto_renewal (str): Auto-renewal mode ("yes", "no", "evergreen")
                - marked_as_needs_attention_at (str): Date and time when contract was flagged as needs attention
                - needs_attention (bool): Whether contract needs attention
                - needs_attention_note (str): Notes on why contract needs attention
                - needs_attention_reason (str): Reason why contract needs attention
                - renew_number_of_times (int): Number of times contract should be renewed
                - renewal_term_unit (str): Term unit for renewals ("days", "weeks", "months", "years")
                - renewal_term_value (int): Number of term units between renewals
                - renewal_termination_notice_date (str): Date for termination notice
                - renewal_termination_notice_unit (str): Term unit for termination notice
                - renewal_termination_notice_value (int): Term units before end date for notice
                - renewal_termination_reminder_date (str): Date for termination reminder
                - renewal_termination_reminder_unit (str): Term unit for termination reminder
                - renewal_termination_reminder_value (int): Term units before notice for reminder
                - terminated_note (str): Termination notes
                - terminated_reason (str): Termination reason
                - updated_at (str): Last modification date
                - custom_fields (list): Custom field values
                - approved_at (str): Date and time of contract approval
                - approval_rounds (int): Times contract has been sent for approval
                - first_sent_for_approval_at (str): First approval request date
                - sent_for_approval_at (str): Last approval request date
                - public (bool): Public visibility of contract
            - relationships (dict): Contract relationships containing:
                - attachments (list): Contract attachments
                - supplier_company (dict): Associated supplier company
                - creator (dict): Contract creator
                - owner (dict): Contract owner
                - docusign_envelopes (list): Docusign envelopes
                - adobe_sign_agreements (list): Adobe Sign agreements
                - contract_type (dict): Contract type
                - spend_category (dict): Spend category
            - links (dict): Related links containing:
                - self (str): URL to the resource
    """
    if not body or "id" not in body:
        raise ValueError("Body must be provided and contain an 'id'.")
    contract_id = len(db.DB.get("contracts", {}).get("contracts", {})) + 1
    while contract_id in db.DB.get("contracts", {}).get("contracts", {}).keys():
        contract_id += 1
    body["id"] = contract_id
    if _include:
        # simulate include logic
        pass
    db.DB["contracts"]["contracts"][contract_id] = body
    return body

def get_contract_by_id(id: int, _include: Optional[str] = None) -> Dict:
    """
    Retrieve details of a specific contract by its internal ID.

    Args:
        id (int): The internal identifier of the contract to retrieve.
        _include (Optional[str]): Comma-separated list of relationships to include
            in the response. 
            Supported values: "contract_type", "spend_category", "supplier_company", "docusign_envelopes", "adobe_sign_agreements"

    Returns:
        Dict: The contract object. Contains any of the following keys:
            - type (str): Object type 
            - id (int): Contract identifier string
            - supplier_id (str): Supplier identifier
            - start_date (str): Contract start date
            - end_date (str): Contract end date
            - external_id (str): External contract identifier
            - attributes (dict): Contract attributes containing:
                - title (str): Contract title (max 255 characters)
                - description (str): Contract description
                - state (str): Current contract state ("draft", "requested", "in_progress", "out_for_approval", "approved", "active", "expired", "terminated")
                - state_label (str): Customer-specific contract state label
                - number (int): Contract number, generated sequentially
                - external_id (str): Customer provided unique contract identifier
                - actual_start_date (str): Contract start date
                - actual_end_date (str): Contract end date
                - actual_spend_amount (float): Actual spend amount
                - auto_renewal (str): Auto-renewal mode ("yes", "no", "evergreen")
                - marked_as_needs_attention_at (str): Date and time when contract was flagged as needs attention
                - needs_attention (bool): Whether contract needs attention
                - needs_attention_note (str): Notes on why contract needs attention
                - needs_attention_reason (str): Reason why contract needs attention
                - renew_number_of_times (int): Number of times contract should be renewed
                - renewal_term_unit (str): Term unit for renewals ("days", "weeks", "months", "years")
                - renewal_term_value (int): Number of term units between renewals
                - renewal_termination_notice_date (str): Date for termination notice
                - renewal_termination_notice_unit (str): Term unit for termination notice
                - renewal_termination_notice_value (int): Term units before end date for notice
                - renewal_termination_reminder_date (str): Date for termination reminder
                - renewal_termination_reminder_unit (str): Term unit for termination reminder
                - renewal_termination_reminder_value (int): Term units before notice for reminder
                - terminated_note (str): Termination notes
                - terminated_reason (str): Termination reason
                - updated_at (str): Last modification date
                - custom_fields (list): Custom field values
                - approved_at (str): Date and time of contract approval
                - approval_rounds (int): Times contract has been sent for approval
                - first_sent_for_approval_at (str): First approval request date
                - sent_for_approval_at (str): Last approval request date
                - public (bool): Public visibility of contract
            - relationships (dict): Contract relationships containing:
                - attachments (list): Contract attachments
                - supplier_company (dict): Associated supplier company
                - creator (dict): Contract creator
                - owner (dict): Contract owner
                - docusign_envelopes (list): Docusign envelopes
                - adobe_sign_agreements (list): Adobe Sign agreements
                - contract_type (dict): Contract type
                - spend_category (dict): Spend category
            - links (dict): Related links containing:
                - self (str): URL to the resource

    Raises:
        KeyError: If no contract exists with the specified ID.
    """
    if id not in db.DB["contracts"]["contracts"]:
        raise KeyError(f"Contract with id {id} not found.")
    if _include:
        # simulate include logic
        pass
    return db.DB["contracts"]["contracts"][id]

def patch_contract_by_id(id: int, _include: Optional[str] = None, body: Optional[Dict] = None) -> Dict:
    """
    Update an existing contract by its internal ID.

    Args:
        id (int): The internal identifier of the contract to update.
        _include (Optional[str]): Comma-separated list of relationships to include
            in the response.
            Supported values: "contract_type", "spend_category", "supplier_company", "docusign_envelopes", "adobe_sign_agreements"
        body (Optional[Dict]): Dictionary containing the fields to update. Includes any of the following keys:
            - type (str, required): Object type 
            - id (int, required): Contract identifier string
            - supplier_id (str): Supplier identifier
            - start_date (str): Contract start date
            - end_date (str): Contract end date
            - external_id (str): External contract identifier
            - attributes (dict): Contract attributes containing:
                - title (str): Contract title (max 255 characters)
                - description (str): Contract description
                - state (str): Current contract state ("draft", "requested", "in_progress", "out_for_approval", "approved", "active", "expired", "terminated")
                - state_label (str): Customer-specific contract state label
                - number (int): Contract number, generated sequentially
                - external_id (str): Customer provided unique contract identifier
                - actual_start_date (str): Contract start date
                - actual_end_date (str): Contract end date
                - actual_spend_amount (float): Actual spend amount
                - auto_renewal (str): Auto-renewal mode ("yes", "no", "evergreen")
                - marked_as_needs_attention_at (str): Date and time when contract was flagged as needs attention
                - needs_attention (bool): Whether contract needs attention
                - needs_attention_note (str): Notes on why contract needs attention
                - needs_attention_reason (str): Reason why contract needs attention
                - renew_number_of_times (int): Number of times contract should be renewed
                - renewal_term_unit (str): Term unit for renewals ("days", "weeks", "months", "years")
                - renewal_term_value (int): Number of term units between renewals
                - renewal_termination_notice_date (str): Date for termination notice
                - renewal_termination_notice_unit (str): Term unit for termination notice
                - renewal_termination_notice_value (int): Term units before end date for notice
                - renewal_termination_reminder_date (str): Date for termination reminder
                - renewal_termination_reminder_unit (str): Term unit for termination reminder
                - renewal_termination_reminder_value (int): Term units before notice for reminder
                - terminated_note (str): Termination notes
                - terminated_reason (str): Termination reason
                - updated_at (str): Last modification date
                - custom_fields (List[Dict[str, Any]], optional): Custom field values
                - approved_at (str): Date and time of contract approval
                - approval_rounds (int): Times contract has been sent for approval
                - first_sent_for_approval_at (str): First approval request date
                - sent_for_approval_at (str): Last approval request date
                - public (bool): Public visibility of contract
            - relationships (dict): Contract relationships containing:
                - attachments (List[Dict[str, Any]], optional): Contract attachments
                - supplier_company (dict): Associated supplier company
                - creator (dict): Contract creator
                - owner (dict): Contract owner
                - docusign_envelopes (List[Dict[str, Any]], optional): Docusign envelopes
                - adobe_sign_agreements (List[Dict[str, Any]], optional): Adobe Sign agreements
                - contract_type (dict): Contract type
                - spend_category (dict): Spend category

    Returns:
        Dict: The updated contract object. Contains any of the following keys:
            - type (str): Object type 
            - id (int): Contract identifier string
            - supplier_id (str): Supplier identifier
            - start_date (str): Contract start date
            - end_date (str): Contract end date
            - external_id (str): External contract identifier
            - attributes (dict): Contract attributes containing:
                - title (str): Contract title (max 255 characters)
                - description (str): Contract description
                - state (str): Current contract state ("draft", "requested", "in_progress", "out_for_approval", "approved", "active", "expired", "terminated")
                - state_label (str): Customer-specific contract state label
                - number (int): Contract number, generated sequentially
                - external_id (str): Customer provided unique contract identifier
                - actual_start_date (str): Contract start date
                - actual_end_date (str): Contract end date
                - actual_spend_amount (float): Actual spend amount
                - auto_renewal (str): Auto-renewal mode ("yes", "no", "evergreen")
                - marked_as_needs_attention_at (str): Date and time when contract was flagged as needs attention
                - needs_attention (bool): Whether contract needs attention
                - needs_attention_note (str): Notes on why contract needs attention
                - needs_attention_reason (str): Reason why contract needs attention
                - renew_number_of_times (int): Number of times contract should be renewed
                - renewal_term_unit (str): Term unit for renewals ("days", "weeks", "months", "years")
                - renewal_term_value (int): Number of term units between renewals
                - renewal_termination_notice_date (str): Date for termination notice
                - renewal_termination_notice_unit (str): Term unit for termination notice
                - renewal_termination_notice_value (int): Term units before end date for notice
                - renewal_termination_reminder_date (str): Date for termination reminder
                - renewal_termination_reminder_unit (str): Term unit for termination reminder
                - renewal_termination_reminder_value (int): Term units before notice for reminder
                - terminated_note (str): Termination notes
                - terminated_reason (str): Termination reason
                - updated_at (str): Last modification date
                - custom_fields (list): Custom field values
                - approved_at (str): Date and time of contract approval
                - approval_rounds (int): Times contract has been sent for approval
                - first_sent_for_approval_at (str): First approval request date
                - sent_for_approval_at (str): Last approval request date
                - public (bool): Public visibility of contract
            - relationships (dict): Contract relationships containing:
                - attachments (list): Contract attachments
                - supplier_company (dict): Associated supplier company
                - creator (dict): Contract creator
                - owner (dict): Contract owner
                - docusign_envelopes (list): Docusign envelopes
                - adobe_sign_agreements (list): Adobe Sign agreements
                - contract_type (dict): Contract type
                - spend_category (dict): Spend category
            - links (dict): Related links containing:
                - self (str): URL to the resource

    Raises:
        KeyError: If no contract exists with the specified ID.
        ValueError: If the body does not contain the correct 'id'.
    """
    if id not in db.DB["contracts"]["contracts"]:
        raise KeyError(f"Contract with id {id} not found.")
    if not body or body.get("id") != id:
        raise ValueError("Body must contain the correct 'id'.")
    db.DB["contracts"]["contracts"][id].update(body)
    return db.DB["contracts"]["contracts"][id]

def delete_contract_by_id(id: int) -> None:
    """
    Delete a contract by its internal ID.

    Args:
        id (int): The internal identifier of the contract to delete.

    Raises:
        KeyError: If no contract exists with the specified ID.
    """
    if id not in db.DB["contracts"]["contracts"]:
        raise KeyError(f"Contract with id {id} not found.")
    del db.DB["contracts"]["contracts"][id]

def get_contract_by_external_id(external_id: str, _include: Optional[str] = None) -> Dict:
    """
    Retrieve details of a specific contract by its external ID.

    Args:
        external_id (str): The external identifier of the contract to retrieve.
        _include (Optional[str]): Comma-separated list of relationships to include
            in the response.
            Supported values: "contract_type", "spend_category", "supplier_company", "docusign_envelopes", "adobe_sign_agreements"
    Returns:
        Dict: The contract object.
        Contains any of the following keys:
            - type (str): Object type 
            - id (int): Contract identifier string
            - supplier_id (str): Supplier identifier
            - start_date (str): Contract start date
            - end_date (str): Contract end date
            - external_id (str): External contract identifier
            - attributes (dict): Contract attributes containing:
                - title (str): Contract title (max 255 characters)
                - description (str): Contract description
                - state (str): Current contract state ("draft", "requested", "in_progress", "out_for_approval", "approved", "active", "expired", "terminated")
                - state_label (str): Customer-specific contract state label
                - number (int): Contract number, generated sequentially
                - external_id (str): Customer provided unique contract identifier
                - actual_start_date (str): Contract start date
                - actual_end_date (str): Contract end date
                - actual_spend_amount (float): Actual spend amount
                - auto_renewal (str): Auto-renewal mode ("yes", "no", "evergreen")
                - marked_as_needs_attention_at (str): Date and time when contract was flagged as needs attention
                - needs_attention (bool): Whether contract needs attention
                - needs_attention_note (str): Notes on why contract needs attention
                - needs_attention_reason (str): Reason why contract needs attention
                - renew_number_of_times (int): Number of times contract should be renewed
                - renewal_term_unit (str): Term unit for renewals ("days", "weeks", "months", "years")
                - renewal_term_value (int): Number of term units between renewals
                - renewal_termination_notice_date (str): Date for termination notice
                - renewal_termination_notice_unit (str): Term unit for termination notice
                - renewal_termination_notice_value (int): Term units before end date for notice
                - renewal_termination_reminder_date (str): Date for termination reminder
                - renewal_termination_reminder_unit (str): Term unit for termination reminder
                - renewal_termination_reminder_value (int): Term units before notice for reminder
                - terminated_note (str): Termination notes
                - terminated_reason (str): Termination reason
                - updated_at (str): Last modification date
                - custom_fields (list): Custom field values
                - approved_at (str): Date and time of contract approval
                - approval_rounds (int): Times contract has been sent for approval
                - first_sent_for_approval_at (str): First approval request date
                - sent_for_approval_at (str): Last approval request date
                - public (bool): Public visibility of contract
            - relationships (dict): Contract relationships containing:
                - attachments (list): Contract attachments
                - supplier_company (dict): Associated supplier company
                - creator (dict): Contract creator
                - owner (dict): Contract owner
                - docusign_envelopes (list): Docusign envelopes
                - adobe_sign_agreements (list): Adobe Sign agreements
                - contract_type (dict): Contract type
                - spend_category (dict): Spend category
            - links (dict): Related links containing:
                - self (str): URL to the resource

    Raises:
        KeyError: If no contract exists with the specified external ID.
    """
    for contract in db.DB["contracts"]["contracts"].values():
        if contract.get("external_id") == external_id:
            return contract
    raise KeyError(f"Contract with external_id {external_id} not found.")

def patch_contract_by_external_id(external_id: str, _include: Optional[str] = None, body: Optional[Dict] = None) -> Dict:
    """
    Update an existing contract by its external ID.

    Args:
        external_id (str): The external identifier of the contract to update.
        _include (Optional[str]): Comma-separated list of relationships to include
            in the response.
            Supported values: "contract_type", "spend_category", "supplier_company", "docusign_envelopes", "adobe_sign_agreements"
        body (Optional[Dict]): Dictionary containing the fields to update. Must include:
            - type (str): Object type 
            - id (int): Contract identifier string
            Can contain any of the following keys:
            - supplier_id (str): Supplier identifier
            - start_date (str): Contract start date
            - end_date (str): Contract end date
            - external_id (str): External contract identifier
            - attributes (dict): Contract attributes containing:
                - title (str): Contract title (max 255 characters)
                - description (str): Contract description
                - state (str): Current contract state ("draft", "requested", "in_progress", "out_for_approval", "approved", "active", "expired", "terminated")
                - state_label (str): Customer-specific contract state label
                - number (int): Contract number, generated sequentially
                - external_id (str): Customer provided unique contract identifier
                - actual_start_date (str): Contract start date
                - actual_end_date (str): Contract end date
                - actual_spend_amount (float): Actual spend amount
                - auto_renewal (str): Auto-renewal mode ("yes", "no", "evergreen")
                - marked_as_needs_attention_at (str): Date and time when contract was flagged as needs attention
                - needs_attention (bool): Whether contract needs attention
                - needs_attention_note (str): Notes on why contract needs attention
                - needs_attention_reason (str): Reason why contract needs attention
                - renew_number_of_times (int): Number of times contract should be renewed
                - renewal_term_unit (str): Term unit for renewals ("days", "weeks", "months", "years")
                - renewal_term_value (int): Number of term units between renewals
                - renewal_termination_notice_date (str): Date for termination notice
                - renewal_termination_notice_unit (str): Term unit for termination notice
                - renewal_termination_notice_value (int): Term units before end date for notice
                - renewal_termination_reminder_date (str): Date for termination reminder
                - renewal_termination_reminder_unit (str): Term unit for termination reminder
                - renewal_termination_reminder_value (int): Term units before notice for reminder
                - terminated_note (str): Termination notes
                - terminated_reason (str): Termination reason
                - updated_at (str): Last modification date
                - custom_fields (List[Dict[str, Any]], optional): Custom field values
                - approved_at (str): Date and time of contract approval
                - approval_rounds (int): Times contract has been sent for approval
                - first_sent_for_approval_at (str): First approval request date
                - sent_for_approval_at (str): Last approval request date
                - public (bool): Public visibility of contract
            - relationships (dict): Contract relationships containing:
                - attachments (List[Dict[str, Any]], optional): Contract attachments
                - supplier_company (dict): Associated supplier company
                - creator (dict): Contract creator
                - owner (dict): Contract owner
                - docusign_envelopes (List[Dict[str, Any]], optional): Docusign envelopes
                - adobe_sign_agreements (List[Dict[str, Any]], optional): Adobe Sign agreements
                - contract_type (dict): Contract type
                - spend_category (dict): Spend category
    Returns:
        Dict: The updated contract object. Contains any of the following keys:
            - type (str): Object type 
            - id (int): Contract identifier string
            - supplier_id (str): Supplier identifier
            - start_date (str): Contract start date
            - end_date (str): Contract end date
            - external_id (str): External contract identifier
            - attributes (dict): Contract attributes containing:
                - title (str): Contract title (max 255 characters)
                - description (str): Contract description
                - state (str): Current contract state ("draft", "requested", "in_progress", "out_for_approval", "approved", "active", "expired", "terminated")
                - state_label (str): Customer-specific contract state label
                - number (int): Contract number, generated sequentially
                - external_id (str): Customer provided unique contract identifier
                - actual_start_date (str): Contract start date
                - actual_end_date (str): Contract end date
                - actual_spend_amount (float): Actual spend amount
                - auto_renewal (str): Auto-renewal mode ("yes", "no", "evergreen")
                - marked_as_needs_attention_at (str): Date and time when contract was flagged as needs attention
                - needs_attention (bool): Whether contract needs attention
                - needs_attention_note (str): Notes on why contract needs attention
                - needs_attention_reason (str): Reason why contract needs attention
                - renew_number_of_times (int): Number of times contract should be renewed
                - renewal_term_unit (str): Term unit for renewals ("days", "weeks", "months", "years")
                - renewal_term_value (int): Number of term units between renewals
                - renewal_termination_notice_date (str): Date for termination notice
                - renewal_termination_notice_unit (str): Term unit for termination notice
                - renewal_termination_notice_value (int): Term units before end date for notice
                - renewal_termination_reminder_date (str): Date for termination reminder
                - renewal_termination_reminder_unit (str): Term unit for termination reminder
                - renewal_termination_reminder_value (int): Term units before notice for reminder
                - terminated_note (str): Termination notes
                - terminated_reason (str): Termination reason
                - updated_at (str): Last modification date
                - custom_fields (list): Custom field values
                - approved_at (str): Date and time of contract approval
                - approval_rounds (int): Times contract has been sent for approval
                - first_sent_for_approval_at (str): First approval request date
                - sent_for_approval_at (str): Last approval request date
                - public (bool): Public visibility of contract
            - relationships (dict): Contract relationships containing:
                - attachments (list): Contract attachments
                - supplier_company (dict): Associated supplier company
                - creator (dict): Contract creator
                - owner (dict): Contract owner
                - docusign_envelopes (list): Docusign envelopes
                - adobe_sign_agreements (list): Adobe Sign agreements
                - contract_type (dict): Contract type
                - spend_category (dict): Spend category
            - links (dict): Related links containing:
                - self (str): URL to the resource

    Raises:
        KeyError: If no contract exists with the specified external ID.
        ValueError: If the body does not contain the correct 'external_id'.
    """
    contract = None
    for c in db.DB["contracts"]["contracts"].values():
        if c.get("external_id") == external_id:
            contract = c
            break
    if not contract:
        raise KeyError(f"Contract with external_id {external_id} not found.")
    if not body or body.get("external_id") != external_id:
        raise ValueError("Body must contain the correct 'external_id'.")
    contract.update(body)
    return contract

def delete_contract_by_external_id(external_id: str) -> None:
    """
    Delete a contract by its external ID.

    Args:
        external_id (str): The external identifier of the contract to delete.

    Raises:
        KeyError: If no contract exists with the specified external ID.
    """
    contract_id = None
    for id, contract in db.DB["contracts"]["contracts"].items():
        if contract.get("external_id") == external_id:
            contract_id = id
            break
    if contract_id is None:
        raise KeyError(f"Contract with external_id {external_id} not found.")
    del db.DB["contracts"]["contracts"][contract_id]

def get_contracts_description() -> List[str]:
    """
    Retrieve a list of all available fields for the contract object.

    Returns:
        List[str]: A list of field names that can be present in a contract object.
    """
    if db.DB["contracts"]["contracts"]:
        return list(db.DB["contracts"]["contracts"][list(db.DB["contracts"]["contracts"].keys())[0]].keys())
    return []

def get_contract_types() -> List[Dict]:
    """
    Retrieve a list of all available contract types.

    Returns:
        List[Dict]: A list of contract type dictionaries, where each contains:
            - type (str): Object type, should always be "contract_types"
            - id (int): Contract type identifier string
            - name (str): Name of the contract type
            - external_id (str): External contract type identifier
            - links (dict): List of related links containing:
                - self (str): Normalized link to the resource
    """
    return list(db.DB["contracts"]["contract_types"].values())

def post_contract_types(body: Optional[Dict] = None) -> Dict:
    """
    Create a new contract type.

    Args:
        body (Optional[Dict]): Dictionary containing contract type creation data. Can contain any of the following keys:
            - type (str): Object type, should always be "contract_types"
            - name (str): Name of the contract type
            - external_id (str): External contract type identifier

    Returns:
        Dict: The newly created contract type object. Contains any of the following keys:
            - type (str): Object type, should always be "contract_types"
            - id (int): Contract type identifier string
            - name (str): Name of the contract type
            - external_id (str): External contract type identifier

    Raises:
        ValueError: If the body is not provided or does not contain an 'id'.
    """
    if not body or "id" not in body:
        raise ValueError("Body must be provided and contain an 'id'.")
    contract_type_id = len(db.DB.get("contracts", {}).get("contract_types", {})) + 1
    while contract_type_id in db.DB.get("contracts", {}).get("contract_types", {}).keys():
        contract_type_id += 1
    body["id"] = contract_type_id
    db.DB["contracts"]["contract_types"][contract_type_id] = body
    return body

def get_contract_type_by_id(id: int) -> Dict:
    """
    Retrieve details of a specific contract type by its internal ID.

    Args:
        id (int): The internal identifier of the contract type to retrieve.

    Returns:
        Dict: The contract type object. Contains any of the following keys:
            - type (str): Object type, should always be "contract_types"
            - id (int): Contract type identifier string
            - name (str): Name of the contract type
            - external_id (str): External contract type identifier

    Raises:
        KeyError: If no contract type exists with the specified ID.
    """
    if id not in db.DB["contracts"]["contract_types"]:
        raise KeyError(f"Contract type with id {id} not found.")
    return db.DB["contracts"]["contract_types"][id]

def patch_contract_type_by_id(id: int, body: Optional[Dict] = None) -> Dict:
    """
    Update an existing contract type by its internal ID. 

    Args:
        id (int): The internal identifier of the contract type to update.
        body (Optional[Dict]): Dictionary containing the fields to update. Must include:
            - id (int): Must match the id parameter in the URL
            - type (str): Object type, should always be "contract_types"
            Can contain any of the following keys:
            - name (str): Name of the contract type
            - external_id (str): External contract type identifier

    Returns:
        Dict: The updated contract type object. Contains any of the following keys:
            - type (str): Object type, should always be "contract_types"
            - id (int): Contract type identifier string
            - name (str): Name of the contract type
            - external_id (str): External contract type identifier

    Raises:
        KeyError: If no contract type exists with the specified ID.
        ValueError: If the body does not contain the correct 'id'.
    """
    if id not in db.DB["contracts"]["contract_types"]:
        raise KeyError(f"Contract type with id {id} not found.")
    if not body or body.get("id") != id:
        raise ValueError("Body must contain the correct 'id'.")
    db.DB["contracts"]["contract_types"][id].update(body)
    return db.DB["contracts"]["contract_types"][id]

def delete_contract_type_by_id(id: int) -> None:
    """
    Delete a contract type by its internal ID.

    Args:
        id (int): The internal identifier of the contract type to delete.

    Raises:
        KeyError: If no contract type exists with the specified ID.
    """
    if id not in db.DB["contracts"]["contract_types"]:
        raise KeyError(f"Contract type with id {id} not found.")
    del db.DB["contracts"]["contract_types"][id]

def get_contract_type_by_external_id(external_id: str) -> Dict:
    """
    Retrieve details of a specific contract type by its external ID.

    Args:
        external_id (str): The external identifier of the contract type to retrieve.

    Returns:
        Dict: The contract type object. Contains any of the following keys:
            - type (str): Object type, should always be "contract_types"
            - id (int): Contract type identifier string
            - name (str): Name of the contract type
            - external_id (str): External contract type identifier

    Raises:
        KeyError: If no contract type exists with the specified external ID.
    """
    for contract_type in db.DB["contracts"]["contract_types"].values():
        if contract_type.get("external_id") == external_id:
            return contract_type
    raise KeyError(f"Contract type with external_id {external_id} not found.")

def patch_contract_type_by_external_id(external_id: str, body: Optional[Dict] = None) -> Dict:
    """
    Update an existing contract type by its external ID.

    Args:
        external_id (str): The external identifier of the contract type to update.
        body (Optional[Dict]): Dictionary containing the fields to update. Must include:
            - external_id (str): Must match the external_id parameter in the URL
            - type (str): Object type, should always be "contract_types"
            Can contain any of the following keys:
            - name (str): Name of the contract type

    Returns:
        Dict: The updated contract type object. Contains any of the following keys:
            - type (str): Object type, should always be "contract_types"
            - id (int): Contract type identifier string
            - name (str): Name of the contract type
            - external_id (str): External contract type identifier

    Raises:
        KeyError: If no contract type exists with the specified external ID.
        ValueError: If the body does not contain the correct 'external_id'.
    """
    contract_type = None
    for c in db.DB["contracts"]["contract_types"].values():
        if c.get("external_id") == external_id:
            contract_type = c
            break
    if not contract_type:
        raise KeyError(f"Contract type with external_id {external_id} not found.")
    if not body or body.get("external_id") != external_id:
        raise ValueError("Body must contain the correct 'external_id'.")
    contract_type.update(body)
    return contract_type

def delete_contract_type_by_external_id(external_id: str) -> None:
    """
    Delete a contract type by its external ID.

    Args:
        external_id (str): The external identifier of the contract type to delete.

    Raises:
        KeyError: If no contract type exists with the specified external ID.
    """
    contract_type_id = None
    for id, contract_type in db.DB["contracts"]["contract_types"].items():
        if contract_type.get("external_id") == external_id:
            contract_type_id = id
            break
    if contract_type_id is None:
        raise KeyError(f"Contract type with external_id {external_id} not found.")
    del db.DB["contracts"]["contract_types"][contract_type_id] 