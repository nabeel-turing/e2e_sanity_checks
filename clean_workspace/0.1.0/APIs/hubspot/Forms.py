# APIs/hubspot/Forms.py
from typing import Optional, Dict, Any, List
import uuid
from hubspot.SimulationEngine.db import DB
import datetime


def get_forms(
    after: Optional[str] = None,
    limit: Optional[int] = None,
    created_at: Optional[str] = None,
    created_at__gt: Optional[str] = None,
    created_at__gte: Optional[str] = None,
    created_at__lt: Optional[str] = None,
    created_at__lte: Optional[str] = None,
    updated_at: Optional[str] = None,
    updated_at__gt: Optional[str] = None,
    updated_at__gte: Optional[str] = None,
    updated_at__lt: Optional[str] = None,
    updated_at__lte: Optional[str] = None,
    name: Optional[str] = None,
    id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get all Marketing Forms.

    Args:
        after(Optional[str]): The id of the form to start after.
        limit(Optional[int]): The maximum number of forms to return.
        created_at(Optional[str]): The date the form was created.
        created_at__gt(Optional[str]): The date the form was created after.
        created_at__gte(Optional[str]): The date the form was created after or equal to.
        created_at__lt(Optional[str]): The date the form was created before.
        created_at__lte(Optional[str]): The date the form was created before or equal to.
        updated_at(Optional[str]): The date the form was updated.
        updated_at__gt(Optional[str]): The date the form was updated after.
        updated_at__gte(Optional[str]): The date the form was updated after or equal to.
        updated_at__lt(Optional[str]): The date the form was updated before.
        updated_at__lte(Optional[str]): The date the form was updated before or equal to.
        name(Optional[str]): The name of the form.
        id(Optional[str]): The id of the form.

    Returns:
        Dict[str, Any]: A dictionary containing the forms.
            - results(List[Dict[str, Any]]): A list of dictionaries containing the forms.
                - id(str): The id of the form.
                - name(str): The name of the form.
                - submit_text(str): The submit text of the form.
                - fieldGroups(List[Dict[str, Any]]): The field groups of the form.
                    - groupType(str): The type of the field group.
                    - richTextType(str): The type of rich text included. The default value is text.
                    - richText(str): A block of rich text or an image. Those can be used to add extra information for the customers filling in the form. If the field group includes fields, the rich text will be displayed before the fields.
                    - fields(List[Dict[str, Any]]): The fields of the field group.
                        - fieldType(str): The type of the field. Can be one of: email, phone, mobile_phone, single_line_text, multi_line_text, number, single_checkbox, multiple_checkboxes, dropdown, radio, datepicker, file, payment_link_radio
                        - name(str): The name of the field.
                        - label(str): The label of the field.
                        - required(bool): Whether the field is required.
                        - placeholder(Optional[str]): The placeholder text of the field.
                        - defaultValue(Optional[str]): The default value of the field.
                        - options(Optional[List[str]]): The options of the field.
                        - hidden(Optional[bool]): Whether the field is hidden.
                - redirect_url(str): The redirect url of the form.
                - created_at(str): The date the form was created.
                - updated_at(str): The date the form was updated.
                - legalConsentOptions(Optional[Dict[str, Any]]): The legal consent options of the form. Default is None.
                    - explicitConsentToProcess(Dict[str, Any]): Explicit consent options
                        - communicationsCheckboxes(List[Dict[str, Any]]): List of communication checkboxes
                            - subscriptionTypeId(int): The subscription type ID
                            - label(str): The main label for the form field
                            - required(bool): Whether this checkbox is required
                        - communicationConsentText(str): Communication consent text
                        - consentToProcessCheckboxLabel(str): Label for consent checkbox
                        - consentToProcessFooterText(str): Footer text for consent
                        - type(str): Type of consent
                        - privacyText(str): Privacy text
                        - consentToProcessText(str): Consent to process text
                    - implicitConsentToProcess(Dict[str, Any]): Implicit consent options
                        - communicationsCheckboxes(List[Dict[str, Any]]): List of communication checkboxes
                            - subscriptionTypeId(int): The subscription type ID
                            - label(str): The main label for the form field
                            - required(bool): Whether this checkbox is required
                        - communicationConsentText(str): Communication consent text
                        - type(str): Type of consent
                        - privacyText(str): Privacy text
                        - consentToProcessText(str): Consent to process text
                    - legitimateInterest(Dict[str, Any]): Legitimate interest options
                        - lawfulBasis(str): The lawful basis for the consent
                        - type(str): The type of the legitimate interest
                        - privacyText(str): The privacy text of the legitimate interest
            - total(int): The total number of forms.
            - paging(Optional[Dict[str, Any]]): The paging information.
                - next(Optional[Dict[str, Any]]): The next page of forms.
                    - after(Optional[str]): The id of the form to start after.
    """
    forms_list = list(DB["forms"].values())

    # Filtering
    if created_at:
        created_at_dt = datetime.datetime.fromisoformat(
            created_at.replace("Z", "+00:00")
        )
        forms_list = [
            f
            for f in forms_list
            if datetime.datetime.fromisoformat(f["createdAt"].replace("Z", "+00:00"))
            == created_at_dt
        ]
    if created_at__gt:
        created_at_gt_dt = datetime.datetime.fromisoformat(
            created_at__gt.replace("Z", "+00:00")
        )
        forms_list = [
            f
            for f in forms_list
            if datetime.datetime.fromisoformat(f["createdAt"].replace("Z", "+00:00"))
            > created_at_gt_dt
        ]
    if created_at__gte:
        created_at__gte_dt = datetime.datetime.fromisoformat(
            created_at__gte.replace("Z", "+00:00")
        )
        forms_list = [
            f
            for f in forms_list
            if datetime.datetime.fromisoformat(f["createdAt"].replace("Z", "+00:00"))
            >= created_at__gte_dt
        ]
    if created_at__lt:
        created_at__lt_dt = datetime.datetime.fromisoformat(
            created_at__lt.replace("Z", "+00:00")
        )
        forms_list = [
            f
            for f in forms_list
            if datetime.datetime.fromisoformat(f["createdAt"].replace("Z", "+00:00"))
            < created_at__lt_dt
        ]
    if created_at__lte:
        created_at__lte_dt = datetime.datetime.fromisoformat(
            created_at__lte.replace("Z", "+00:00")
        )
        forms_list = [
            f
            for f in forms_list
            if datetime.datetime.fromisoformat(f["createdAt"].replace("Z", "+00:00"))
            <= created_at__lte_dt
        ]

    if updated_at:
        updated_at_dt = datetime.datetime.fromisoformat(
            updated_at.replace("Z", "+00:00")
        )
        forms_list = [
            f
            for f in forms_list
            if datetime.datetime.fromisoformat(f["updatedAt"].replace("Z", "+00:00"))
            == updated_at_dt
        ]
    if updated_at__gt:
        updated_at__gt_dt = datetime.datetime.fromisoformat(
            updated_at__gt.replace("Z", "+00:00")
        )
        forms_list = [
            f
            for f in forms_list
            if datetime.datetime.fromisoformat(f["updatedAt"].replace("Z", "+00:00"))
            > updated_at__gt_dt
        ]
    if updated_at__gte:
        updated_at__gte_dt = datetime.datetime.fromisoformat(
            updated_at__gte.replace("Z", "+00:00")
        )
        forms_list = [
            f
            for f in forms_list
            if datetime.datetime.fromisoformat(f["updatedAt"].replace("Z", "+00:00"))
            >= updated_at__gte_dt
        ]
    if updated_at__lt:
        updated_at__lt_dt = datetime.datetime.fromisoformat(
            updated_at__lt.replace("Z", "+00:00")
        )
        forms_list = [
            f
            for f in forms_list
            if datetime.datetime.fromisoformat(f["updatedAt"].replace("Z", "+00:00"))
            < updated_at__lt_dt
        ]
    if updated_at__lte:
        updated_at__lte_dt = datetime.datetime.fromisoformat(
            updated_at__lte.replace("Z", "+00:00")
        )
        forms_list = [
            f
            for f in forms_list
            if datetime.datetime.fromisoformat(f["updatedAt"].replace("Z", "+00:00"))
            <= updated_at__lte_dt
        ]
    if name:
        forms_list = [f for f in forms_list if f.get("name") == name]
    if id:
        forms_list = [f for f in forms_list if f.get("id") == id]

    # Pagination (using after and limit)
    total_count = len(forms_list)
    start_index = 0

    if after:
        try:
            # Find the index of the form with the given 'after' ID
            start_index = (
                next(i for i, form in enumerate(forms_list) if form["id"] == after) + 1
            )
        except StopIteration:
            # If 'after' ID not found, return empty results (or raise an error)
            return {"results": [], "total": total_count, "paging": None}
            # Alternative: raise ValueError(f"Form with id '{after}' not found")

    forms_list = forms_list[start_index:]

    if limit is not None:
        forms_list = forms_list[:limit]

    # Construct paging information
    paging = None
    if (
        limit is not None
        and len(forms_list) == limit
        and start_index + limit < total_count
    ):
        next_after = forms_list[-1]["id"]
        paging = {"next": {"after": next_after}}

    return {"results": forms_list, "total": total_count, "paging": paging}


def create_form(
    name: str,
    submitText: str,
    fieldGroups: List[Dict[str, Any]],
    legalConsentOptions: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Create a new Marketing Form.

    Args:
        name(str): The name of the form.
        submitText(str): The submit text of the form.
        fieldGroups(List[Dict[str, Any]]): The field groups of the form.
            - groupType(str): The type of the field group.
            - richTextType(str): The type of rich text included. The default value is text.
            - richText(str): A block of rich text or an image. Those can be used to add extra information for the customers filling in the form. If the field group includes fields, the rich text will be displayed before the fields.
            - fields(List[Dict[str, Any]]): The fields of the field group.
                - fieldType(str): The type of the field. Can be one of: email, phone, mobile_phone, single_line_text, multi_line_text, number, single_checkbox, multiple_checkboxes, dropdown, radio, datepicker, file, payment_link_radio
                - name(str): The name of the field.
                - label(str): The label of the field.
                - required(bool): Whether the field is required.
                - placeholder(Optional[str]): The placeholder text of the field.
                - defaultValue(Optional[str]): The default value of the field.
                - options(Optional[List[str]]): The options of the field.
                - hidden(Optional[bool]): Whether the field is hidden.
        legalConsentOptions(Optional[Dict[str, Any]]): The legal consent options of the form. Default is None.
            - explicitConsentToProcess(Optional[Dict[str, Any]]): Explicit consent options
                - communicationsCheckboxes(List[Dict[str, Any]]): List of communication checkboxes
                    - subscriptionTypeId(int): The subscription type ID
                    - label(str): The main label for the form field
                    - required(bool): Whether this checkbox is required
                - communicationConsentText(str): Communication consent text
                - consentToProcessCheckboxLabel(str): Label for consent checkbox
                - consentToProcessFooterText(str): Footer text for consent
                - type(str): Type of consent
                - privacyText(str): Privacy text
                - consentToProcessText(str): Consent to process text
            - implicitConsentToProcess(Optional[Dict[str, Any]]): Implicit consent options
                - communicationsCheckboxes(Optional[List[Dict[str, Any]]]): List of communication checkboxes
                    - subscriptionTypeId(int): The subscription type ID
                    - label(str): The main label for the form field
                    - required(bool): Whether this checkbox is required
                - communicationConsentText(str): Communication consent text
                - type(str): Type of consent
                - privacyText(str): Privacy text
                - consentToProcessText(str): Consent to process text
            - legitimateInterest(Optional[Dict[str, Any]]): Legitimate interest options
                - lawfulBasis(str): The lawful basis for the consent
                - type(str): The type of the legitimate interest
                - privacyText(str): The privacy text of the legitimate interest

    Returns:
        Dict[str, Any]: The new form with the same structure as the input parameters.
            - id(str): The id of the form.
            - name(str): The name of the form.
            - submitText(str): The submit text of the form.
            - fieldGroups(List[Dict[str, Any]]): The field groups of the form.
                - groupType(str): The type of the field group.
                - richTextType(str): The type of rich text included. The default value is text.
                - richText(str): A block of rich text or an image. Those can be used to add extra information for the customers filling in the form. If the field group includes fields, the rich text will be displayed before the fields.
                - fields(List[Dict[str, Any]]): The fields of the field group.
                    - fieldType(str): The type of the field. Can be one of: email, phone, mobile_phone, single_line_text, multi_line_text, number, single_checkbox, multiple_checkboxes, dropdown, radio, datepicker, file, payment_link_radio
                    - name(str): The name of the field.
                    - label(str): The label of the field.
                    - required(bool): Whether the field is required.
                    - placeholder(Optional[str]): The placeholder text of the field.
                    - defaultValue(Optional[str]): The default value of the field.
                    - options(Optional[List[str]]): The options of the field.
                    - hidden(Optional[bool]): Whether the field is hidden.
            - legalConsentOptions(Optional[Dict[str, Any]]): The legal consent options of the form. Default is None.
                - explicitConsentToProcess(Optional[Dict[str, Any]]): Explicit consent options
                    - communicationsCheckboxes(List[Dict[str, Any]]): List of communication checkboxes
                        - subscriptionTypeId(int): The subscription type ID
                        - label(str): The main label for the form field
                        - required(bool): Whether this checkbox is required
                    - communicationConsentText(str): Communication consent text
                    - consentToProcessCheckboxLabel(str): Label for consent checkbox
                    - consentToProcessFooterText(str): Footer text for consent
                    - type(str): Type of consent
                    - privacyText(str): Privacy text
                    - consentToProcessText(str): Consent to process text
                - implicitConsentToProcess(Optional[Dict[str, Any]]): Implicit consent options
                    - communicationsCheckboxes(List[Dict[str, Any]]): List of communication checkboxes
                        - subscriptionTypeId(int): The subscription type ID
                        - label(str): The main label for the form field
                        - required(bool): Whether this checkbox is required
                    - communicationConsentText(str): Communication consent text
                    - type(str): Type of consent
                    - privacyText(str): Privacy text
                    - consentToProcessText(str): Consent to process text
                - legitimateInterest(Optional[Dict[str, Any]]): Legitimate interest options
                    - lawfulBasis(str): The lawful basis for the consent
                    - type(str): The type of the legitimate interest
                    - privacyText(str): The privacy text of the legitimate interest
            - createdAt(str): The date the form was created.
            - updatedAt(str): The date the form was updated.
    """
    new_form_id = str(uuid.uuid4())
    now = datetime.datetime.now(datetime.timezone.utc).isoformat() + "Z"
    new_form = {
        "id": new_form_id,
        "name": name,
        "submitText": submitText,
        "fieldGroups": fieldGroups,
        "legalConsentOptions": legalConsentOptions,
        "createdAt": now,
        "updatedAt": now,
    }
    DB["forms"][new_form_id] = new_form
    return new_form


def get_form(formId: str) -> Dict[str, Any]:
    """
    Get a Marketing Form by ID.

    Args:
        formId(str): The id of the form.

    Returns:
        Dict[str, Any]: The form.
            - id(str): The id of the form.
            - name(str): The name of the form.
            - submitText(str): The submit text of the form.
            - fieldGroups(List[Dict[str, Any]]): The field groups of the form.
                - group_type(str): The type of the field group.
                - fields(List[str]): The fields of the field group.
            - legalConsentOptions(Optional[Dict[str, Any]]): The legal consent options of the form. Default is None.
                - explicitConsentToProcess(Optional[Dict[str, Any]]): Explicit consent options
                    - communicationsCheckboxes(List[Dict[str, Any]]): List of communication checkboxes
                        - subscriptionTypeId(int): The subscription type ID
                        - label(str): The main label for the form field
                        - required(bool): Whether this checkbox is required
                    - communicationConsentText(str): Communication consent text
                    - consentToProcessCheckboxLabel(str): Label for consent checkbox
                    - consentToProcessFooterText(str): Footer text for consent
                    - type(str): Type of consent
                    - privacyText(str): Privacy text
                    - consentToProcessText(str): Consent to process text
                - implicitConsentToProcess(Optional[Dict[str, Any]]): Implicit consent options
                    - communicationsCheckboxes(List[Dict[str, Any]]): List of communication checkboxes
                        - subscriptionTypeId(int): The subscription type ID
                        - label(str): The main label for the form field
                        - required(bool): Whether this checkbox is required
                    - communicationConsentText(str): Communication consent text
                    - type(str): Type of consent
                    - privacyText(str): Privacy text
                    - consentToProcessText(str): Consent to process text
                - legitimateInterest(Optional[Dict[str, Any]]): Legitimate interest options
                    - lawfulBasis(str): The lawful basis for the consent
                    - type(str): The type of the legitimate interest
                    - privacyText(str): The privacy text of the legitimate interest
            - createdAt(str): The date the form was created.
            - updatedAt(str): The date the form was updated.
    Raises:
        ValueError: If the form is not found.
    """
    if formId not in DB["forms"]:
        raise ValueError(
            f"Form with id '{formId}' not found"
        )  # Consistent error handling
    return DB["forms"][formId]


def update_form(
    formId: str,
    name: Optional[str] = None,
    submitText: Optional[str] = None,
    fieldGroups: Optional[List[Dict[str, Any]]] = None,
    legalConsentOptions: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Update a Marketing Form.

    Args:
        formId(str): The id of the form to update.
        name(Optional[str]): The new name of the form.
        submitText(Optional[str]): The new submit text of the form.
        fieldGroups(Optional[List[Dict[str, Any]]]): The new field groups of the form.
            - groupType(str): The type of the field group.
            - richTextType(str): The type of rich text included. The default value is text.
            - richText(str): A block of rich text or an image. Those can be used to add extra information for the customers filling in the form. If the field group includes fields, the rich text will be displayed before the fields.
            - fields(List[Dict[str, Any]]): The fields of the field group.
                - fieldType(str): The type of the field. Can be one of: email, phone, mobile_phone, single_line_text, multi_line_text, number, single_checkbox, multiple_checkboxes, dropdown, radio, datepicker, file, payment_link_radio
                - name(str): The name of the field.
                - label(str): The label of the field.
                - required(bool): Whether the field is required.
                - placeholder(Optional[str]): The placeholder text of the field.
                - defaultValue(Optional[str]): The default value of the field.
                - options(Optional[List[str]]): The options of the field.
                - hidden(Optional[bool]): Whether the field is hidden.
        legalConsentOptions(Optional[Dict[str, Any]]): The new legal consent options of the form. Default is None.
            - explicitConsentToProcess(Optional[Dict[str, Any]]): Explicit consent options
                - communicationsCheckboxes(List[Dict[str, Any]]): List of communication checkboxes
                    - subscriptionTypeId(int): The subscription type ID
                    - label(str): The main label for the form field
                    - required(bool): Whether this checkbox is required
                - communicationConsentText(str): Communication consent text
                - consentToProcessCheckboxLabel(str): Label for consent checkbox
                - consentToProcessFooterText(str): Footer text for consent
                - type(str): Type of consent
                - privacyText(str): Privacy text
                - consentToProcessText(str): Consent to process text
            - implicitConsentToProcess(Optional[Dict[str, Any]]): Implicit consent options
                - communicationsCheckboxes(List[Dict[str, Any]]): List of communication checkboxes
                    - subscriptionTypeId(int): The subscription type ID
                    - label(str): The main label for the form field
                    - required(bool): Whether this checkbox is required
                - communicationConsentText(str): Communication consent text
                - type(str): Type of consent
                - privacyText(str): Privacy text
                - consentToProcessText(str): Consent to process text
            - legitimateInterest(Optional[Dict[str, Any]]): Legitimate interest options
                - lawfulBasis(str): The lawful basis for the consent
                - type(str): The type of the legitimate interest
                - privacyText(str): The privacy text of the legitimate interest

    Returns:
        Dict[str, Any]: The updated form with the same structure as the input parameters.
            - id(str): The id of the form.
            - name(str): The name of the form.
            - submitText(str): The submit text of the form.
            - fieldGroups(List[Dict[str, Any]]): The field groups of the form.
                - groupType(str): The type of the field group.
                - richTextType(str): The type of rich text included. The default value is text.
                - richText(str): A block of rich text or an image. Those can be used to add extra information for the customers filling in the form. If the field group includes fields, the rich text will be displayed before the fields.
                - fields(List[Dict[str, Any]]): The fields of the field group.
                    - fieldType(str): The type of the field. Can be one of: email, phone, mobile_phone, single_line_text, multi_line_text, number, single_checkbox, multiple_checkboxes, dropdown, radio, datepicker, file, payment_link_radio
                    - name(str): The name of the field.
                    - label(str): The label of the field.
                    - required(bool): Whether the field is required.
                    - placeholder(Optional[str]): The placeholder text of the field.
                    - defaultValue(Optional[str]): The default value of the field.
                    - options(Optional[List[str]]): The options of the field.
                    - hidden(Optional[bool]): Whether the field is hidden.
            - legalConsentOptions(Optional[Dict[str, Any]]): The legal consent options of the form. Default is None.
                - explicitConsentToProcess(Optional[Dict[str, Any]]): Explicit consent options
                    - communicationsCheckboxes(List[Dict[str, Any]]): List of communication checkboxes
                        - subscriptionTypeId(int): The subscription type ID
                        - label(str): The main label for the form field
                        - required(bool): Whether this checkbox is required
                    - communicationConsentText(str): Communication consent text
                    - consentToProcessCheckboxLabel(str): Label for consent checkbox
                    - consentToProcessFooterText(str): Footer text for consent
                    - type(str): Type of consent
                    - privacyText(str): Privacy text
                    - consentToProcessText(str): Consent to process text
                - implicitConsentToProcess(Optional[Dict[str, Any]]): Implicit consent options
                    - communicationsCheckboxes(List[Dict[str, Any]]): List of communication checkboxes
                        - subscriptionTypeId(int): The subscription type ID
                        - label(str): The main label for the form field
                        - required(bool): Whether this checkbox is required
                    - communicationConsentText(str): Communication consent text
                    - type(str): Type of consent
                    - privacyText(str): Privacy text
                    - consentToProcessText(str): Consent to process text
                - legitimateInterest(Optional[Dict[str, Any]]): Legitimate interest options
                    - lawfulBasis(str): The lawful basis for the consent
                    - type(str): The type of the legitimate interest
                    - privacyText(str): The privacy text of the legitimate interest
            - createdAt(str): The date the form was created.
            - updatedAt(str): The date the form was updated.

    """

    if formId not in DB["forms"]:
        raise ValueError(f"Form with ID '{formId}' not found.")

    form = DB["forms"][formId]
    if name is not None:
        form["name"] = name
    if submitText is not None:
        form["submitText"] = submitText
    if fieldGroups is not None:
        form["fieldGroups"] = fieldGroups
    if legalConsentOptions is not None:
        form["legalConsentOptions"] = legalConsentOptions

    form["updatedAt"] = datetime.datetime.now(datetime.timezone.utc).isoformat() + "Z"
    return form


def delete_form(formId: str) -> None:
    """
    Archive a form

    Args:
        formId(str): The id of the form to archive.

    Returns:
        None
    """
    if formId not in DB["forms"]:
        return {"error": f"Form with ID '{formId}' not found."}
    del DB["forms"][formId]
