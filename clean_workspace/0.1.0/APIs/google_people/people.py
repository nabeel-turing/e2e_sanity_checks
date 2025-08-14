"""
Google People API - People Resource

This module provides simulation of the Google People API people resource methods.
It handles contact management, profile operations, and contact information.

The Google People API allows you to:
- Get, create, update, and delete people contacts
- List and search through connections
- Batch retrieve multiple people
- Access directory people (for Google Workspace domains)
- Manage contact information including names, emails, phone numbers, addresses, etc.

For more information, see: https://developers.google.com/people/api/rest/v1/people
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

from .SimulationEngine.db import DB
from .SimulationEngine.utils import generate_id
from google_people.SimulationEngine.models import (
    GetContactRequest, CreateContactRequest, UpdateContactRequest, DeleteContactRequest,
    ListConnectionsRequest, SearchPeopleRequest, BatchGetRequest,
    GetDirectoryPersonRequest, ListDirectoryPeopleRequest, SearchDirectoryPeopleRequest,
    Person, GetContactResponse, CreateContactResponse, UpdateContactResponse, DeleteContactResponse,
    ListConnectionsResponse, SearchPeopleResponse, BatchGetResponse,
    ListDirectoryPeopleResponse, SearchDirectoryPeopleResponse
)

logger = logging.getLogger(__name__)


def get_contact(resource_name: str, person_fields: Optional[str] = None,
                sources: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Get a single person by resource name.
    
    This method retrieves a specific person from the user's contacts using their resource name.
    The resource name is a unique identifier that follows the format "people/{personId}".
    
    Args:
        resource_name (str): The resource name of the person to retrieve. Must start with "people/".
                            Example: "people/123456789"
        person_fields (Optional[str]): Comma-separated list of person fields to include in the response.
                                      Valid fields: names, emailAddresses, phoneNumbers, addresses,
                                      organizations, birthdays, photos, urls, userDefined, resourceName,
                                      etag, created, updated. If not specified, all fields are returned.
        sources (Optional[List[str]]): List of sources to retrieve data from. Valid sources include
                                      "READ_SOURCE_TYPE_PROFILE", "READ_SOURCE_TYPE_CONTACT",
                                      "READ_SOURCE_TYPE_DOMAIN_PROFILE", "READ_SOURCE_TYPE_DIRECTORY".
    
    Returns:
        Dict[str, Any]: A dictionary containing the person data with the following structure:
            {
                "resourceName": "people/123456789",
                "etag": "etag_123456789",
                "names": [...],
                "emailAddresses": [...],
                "phoneNumbers": [...],
                "addresses": [...],
                "organizations": [...],
                "birthdays": [...],
                "photos": [...],
                "urls": [...],
                "userDefined": [...],
                "created": "2023-01-15T10:30:00Z",
                "updated": "2024-01-15T14:20:00Z"
            }
    
    Raises:
        ValueError: If the resource name is invalid or the person is not found.
        ValidationError: If the input parameters fail validation.
    

    """
    # Validate input using Pydantic model
    request = GetContactRequest(
        resource_name=resource_name,
        person_fields=person_fields,
        sources=sources
    )
    
    logger.info(f"Getting person with resource name: {request.resource_name}")

    db = DB
    people_data = db.get("people", {})

    if request.resource_name not in people_data:
        raise ValueError(f"Person with resource name '{request.resource_name}' not found")

    person = people_data[request.resource_name].copy()

    # Filter by person_fields if specified
    if request.person_fields:
        field_list = [field.strip() for field in request.person_fields.split(",")]
        filtered_person = {}
        for field in field_list:
            if field in person:
                filtered_person[field] = person[field]
        person = filtered_person

    response_data = {
        "resourceName": request.resource_name,
        "etag": person.get("etag", "etag123"),
        **person
    }
    
    # Validate response using Pydantic model
    return response_data


def create_contact(person_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new person contact.
    
    This method creates a new contact in the user's Google Contacts. The contact must have
    at least one name and one email address. The resource name is automatically generated.
    
    Args:
        person_data (Dict[str, Any]): Dictionary containing person information. Must include:
            - names (List[Dict]): At least one name object with displayName, givenName, or familyName
            - emailAddresses (List[Dict]): At least one email address object with value
            Optional fields:
            - phoneNumbers (List[Dict]): Phone number objects
            - addresses (List[Dict]): Address objects
            - organizations (List[Dict]): Organization objects
            - birthdays (List[Dict]): Birthday objects
            - photos (List[Dict]): Photo objects
            - urls (List[Dict]): URL objects
            - userDefined (List[Dict]): User-defined field objects
    
    Returns:
        Dict[str, Any]: A dictionary containing the created person data with the following structure:
            {
                "resourceName": "people/123456789",
                "etag": "etag_123456789",
                "names": [...],
                "emailAddresses": [...],
                "phoneNumbers": [...],
                "addresses": [...],
                "organizations": [...],
                "birthdays": [...],
                "photos": [...],
                "urls": [...],
                "userDefined": [...],
                "created": "2024-01-15T10:30:00Z",
                "updated": "2024-01-15T10:30:00Z"
            }
    
    Raises:
        ValueError: If required fields are missing or invalid.
        ValidationError: If the input data fails validation.
    

    """
    # Validate input using Pydantic model
    person = Person(**person_data)
    request = CreateContactRequest(person_data=person)
    
    logger.info("Creating new person contact")

    db = DB
    people_data = db.get("people", {})

    # Generate resource name
    resource_name = f"people/{generate_id()}"

    # Create person object
    person_obj = {
        "resourceName": resource_name,
        "etag": f"etag_{generate_id()}",
        "names": request.person_data.names or [],
        "emailAddresses": request.person_data.email_addresses or [],
        "phoneNumbers": request.person_data.phone_numbers or [],
        "addresses": request.person_data.addresses or [],
        "organizations": request.person_data.organizations or [],
        "birthdays": request.person_data.birthdays or [],
        "photos": request.person_data.photos or [],
        "urls": request.person_data.urls or [],
        "userDefined": request.person_data.user_defined or [],
        "created": datetime.now().isoformat() + "Z",
        "updated": datetime.now().isoformat() + "Z"
    }

    response = CreateContactResponse(**person_obj).model_dump(by_alias=True)
    people_data[resource_name] = response
    db.set("people", people_data)
    logger.info(f"Created person with resource name: {resource_name}")

    return response


def update_contact(resource_name: str, person_data: Dict[str, Any],
                   update_person_fields: Optional[str] = None) -> Dict[str, Any]:
    """
    Update an existing person contact.
    
    This method updates an existing contact in the user's Google Contacts. You can update
    all fields or specify only certain fields to update using the update_person_fields parameter.
    
    Args:
        resource_name (str): The resource name of the person to update. Must start with "people/".
                            Example: "people/123456789"
        person_data (Dict[str, Any]): Dictionary containing updated person information.
                                     Only the fields you want to update need to be included.
        update_person_fields (Optional[str]): Comma-separated list of person fields to update.
                                             If specified, only these fields will be updated.
                                             If not specified, all provided fields will be updated.
                                             Valid fields: names, emailAddresses, phoneNumbers,
                                             addresses, organizations, birthdays, photos, urls, userDefined
    
    Returns:
        Dict[str, Any]: A dictionary containing the updated person data with the same structure
                       as the create_contact response, but with updated timestamps.
    
    Raises:
        ValueError: If the resource name is invalid or the person is not found.
        ValidationError: If the input parameters fail validation.
    

    """
    # Validate input using Pydantic model
    person = Person(**person_data)
    request = UpdateContactRequest(
        resource_name=resource_name,
        person_data=person,
        update_person_fields=update_person_fields
    )
    
    logger.info(f"Updating person with resource name: {request.resource_name}")

    db = DB
    people_data = db.get("people", {})

    if request.resource_name not in people_data:
        raise ValueError(f"Person with resource name '{request.resource_name}' not found")

    existing_person = people_data[request.resource_name]

    # Update only specified fields if update_person_fields is provided
    if request.update_person_fields:
        field_list = [field.strip() for field in request.update_person_fields.split(",")]
        for field in field_list:
            if hasattr(request.person_data, field):
                field_value = getattr(request.person_data, field)
                if field_value is not None:
                    existing_person[field] = field_value
    else:
        # Update all provided fields
        person_dict = request.person_data.dict(exclude_unset=True, by_alias=True)
        existing_person.update(person_dict)

    # Update timestamp
    existing_person["updated"] = datetime.now().isoformat() + "Z"
    existing_person["etag"] = f"etag_{generate_id()}"

    # Save to database
    people_data[request.resource_name] = existing_person
    db.set("people", people_data)

    logger.info(f"Updated person with resource name: {request.resource_name}")

    return existing_person


def delete_contact(resource_name: str) -> Dict[str, Any]:
    """
    Delete a person contact.
    
    This method permanently deletes a contact from the user's Google Contacts.
    The deletion cannot be undone.
    
    Args:
        resource_name (str): The resource name of the person to delete. Must start with "people/".
                            Example: "people/123456789"
    
    Returns:
        Dict[str, Any]: A dictionary containing deletion confirmation with the following structure:
            {
                "success": True,
                "deletedResourceName": "people/123456789",
                "message": "Person deleted successfully"
            }
    
    Raises:
        ValueError: If the resource name is invalid or the person is not found.
        ValidationError: If the input parameters fail validation.
    

    """
    # Validate input using Pydantic model
    request = DeleteContactRequest(resource_name=resource_name)
    
    logger.info(f"Deleting person with resource name: {request.resource_name}")

    db = DB
    people_data = db.get("people", {})

    if request.resource_name not in people_data:
        raise ValueError(f"Person with resource name '{request.resource_name}' not found")

    # Remove from database
    deleted_person = people_data.pop(request.resource_name)
    db.set("people", people_data)

    logger.info(f"Deleted person with resource name: {request.resource_name}")
    
    response_data = {
        "success": True,
        "deletedResourceName": request.resource_name,
        "message": "Person deleted successfully"
    }
    
    # Validate response using Pydantic model
    response = DeleteContactResponse(**response_data)
    return response.dict(by_alias=True)


def list_connections(resource_name: str = "people/me", person_fields: Optional[str] = None,
                     page_size: Optional[int] = None, page_token: Optional[str] = None,
                     sort_order: Optional[str] = None, sync_token: Optional[str] = None,
                     request_sync_token: Optional[bool] = None) -> Dict[str, Any]:
    """
    List people in the authenticated user's contacts (connections).
    
    This method retrieves a list of people in the authenticated user's contacts.
    The response can be paginated and supports various sorting options.
    
    Args:
        resource_name (str, optional): The resource name to return connections for.
                                      Defaults to "people/me" (the authenticated user).
                                      Must start with "people/".
        person_fields (Optional[str]): Comma-separated list of person fields to include in the response.
                                      Valid fields: names, emailAddresses, phoneNumbers, addresses,
                                      organizations, birthdays, photos, urls, userDefined, resourceName,
                                      etag, created, updated.
        page_size (Optional[int]): The number of connections to include in the response.
                                  Must be between 1 and 1000. Defaults to 100.
        page_token (Optional[str]): A page token, received from a previous response.
                                   Used for pagination.
        sort_order (Optional[str]): The order in which the connections should be sorted.
                                   Valid values: "LAST_MODIFIED_ASCENDING", "LAST_MODIFIED_DESCENDING",
                                   "FIRST_NAME_ASCENDING", "LAST_NAME_ASCENDING".
        sync_token (Optional[str]): A sync token, returned by a previous call.
                                   Used for incremental sync.
        request_sync_token (Optional[bool]): Whether the response should include a sync token.
                                            Defaults to False.
    
    Returns:
        Dict[str, Any]: A dictionary containing the list of connections with the following structure:
            {
                "connections": [
                    {
                        "resourceName": "people/123456789",
                        "etag": "etag_123456789",
                        "names": [...],
                        "emailAddresses": [...],
                        ...
                    }
                ],
                "nextPageToken": "next_page_token_string",
                "totalItems": 150,
                "nextSyncToken": "sync_token_string"
            }
    
    Raises:
        ValueError: If the resource name is invalid or parameters are invalid.
        ValidationError: If the input parameters fail validation.
    

    """
    # Validate input using Pydantic model
    request = ListConnectionsRequest(
        resource_name=resource_name,
        person_fields=person_fields,
        page_size=page_size,
        page_token=page_token,
        sort_order=sort_order,
        sync_token=sync_token,
        request_sync_token=request_sync_token
    )
    
    logger.info(f"Listing connections for resource: {request.resource_name}")

    db = DB
    people_data = db.get("people", {})

    # Filter people based on resource_name (simplified logic)
    connections = []
    for person_id, person in people_data.items():
        if person_id != request.resource_name:  # Exclude the requesting user
            connections.append(person)

    # Apply sorting if specified
    if request.sort_order:
        if request.sort_order == "FIRST_NAME_ASCENDING":
            connections.sort(key=lambda x: x.get("names", [{}])[0].get("givenName", ""))
        elif request.sort_order == "LAST_NAME_ASCENDING":
            connections.sort(key=lambda x: x.get("names", [{}])[0].get("familyName", ""))
        elif request.sort_order == "LAST_MODIFIED_DESCENDING":
            connections.sort(key=lambda x: x.get("updated", ""), reverse=True)
        elif request.sort_order == "LAST_MODIFIED_ASCENDING":
            connections.sort(key=lambda x: x.get("updated", ""))

    # Apply pagination
    if request.page_size:
        start_index = 0
        if request.page_token:
            try:
                start_index = int(request.page_token)
            except ValueError:
                start_index = 0

        end_index = start_index + request.page_size
        connections = connections[start_index:end_index]

        next_page_token = str(end_index) if end_index < len(people_data) else None
    else:
        next_page_token = None

    # Filter by person_fields if specified
    if request.person_fields:
        field_list = [field.strip() for field in request.person_fields.split(",")]
        filtered_connections = []
        for person in connections:
            filtered_person = {}
            for field in field_list:
                if field in person:
                    filtered_person[field] = person[field]
            filtered_connections.append(filtered_person)
        connections = filtered_connections

    response_data = {
        "connections": connections,
        "nextPageToken": next_page_token,
        "totalItems": len(connections)
    }

    # Add sync token if requested
    if request.request_sync_token:
        response_data["nextSyncToken"] = f"sync_{generate_id()}"

    # Validate response using Pydantic model
    response = ListConnectionsResponse(**response_data)
    return response.dict(by_alias=True)


def search_people(query: str, read_mask: Optional[str] = None,
                  sources: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Search for people in the authenticated user's contacts.
    
    This method searches through the authenticated user's contacts using a plain-text query.
    The search is performed across names, email addresses, and other contact information.
    
    Args:
        query (str): The plain-text query for the request. Must not be empty and cannot exceed 1000 characters.
                     The search is case-insensitive and performs partial matching.
        read_mask (Optional[str]): A field mask to restrict which fields on each person are returned.
                                  Valid fields: names, emailAddresses, phoneNumbers, addresses,
                                  organizations, birthdays, photos, urls, userDefined, resourceName,
                                  etag, created, updated.
        sources (Optional[List[str]]): List of sources to retrieve data from. Valid sources include
                                      "READ_SOURCE_TYPE_PROFILE", "READ_SOURCE_TYPE_CONTACT",
                                      "READ_SOURCE_TYPE_DOMAIN_PROFILE", "READ_SOURCE_TYPE_DIRECTORY".
    
    Returns:
        Dict[str, Any]: A dictionary containing the search results with the following structure:
            {
                "results": [
                    {
                        "resourceName": "people/123456789",
                        "etag": "etag_123456789",
                        "names": [...],
                        "emailAddresses": [...],
                        ...
                    }
                ],
                "totalItems": 5
            }
    
    Raises:
        ValueError: If the query is empty or invalid.
        ValidationError: If the input parameters fail validation.
    

    """
    # Validate input using Pydantic model
    request = SearchPeopleRequest(
        query=query,
        read_mask=read_mask,
        sources=sources
    )
    
    logger.info(f"Searching people with query: {request.query}")

    db = DB
    people_data = db.get("people", {})

    # Simple search implementation
    results = []
    query_lower = request.query.lower()

    for person_id, person in people_data.items():
        # Search in names
        for name in person.get("names", []):
            display_name = name.get("displayName", "").lower()
            given_name = name.get("givenName", "").lower()
            family_name = name.get("familyName", "").lower()
            if (query_lower in display_name or 
                query_lower in given_name or 
                query_lower in family_name):
                results.append(person)
                break

        # Search in email addresses
        for email in person.get("emailAddresses", []):
            email_value = email.get("value", "").lower()
            if query_lower in email_value:
                results.append(person)
                break

        # Search in organizations
        for org in person.get("organizations", []):
            org_name = org.get("name", "").lower()
            org_title = org.get("title", "").lower()
            if query_lower in org_name or query_lower in org_title:
                results.append(person)
                break

    # Remove duplicates
    unique_results = []
    seen_ids = set()
    for person in results:
        if person["resourceName"] not in seen_ids:
            unique_results.append(person)
            seen_ids.add(person["resourceName"])

    # Filter by read_mask if specified
    if request.read_mask:
        mask_fields = [field.strip() for field in request.read_mask.split(",")]
        filtered_results = []
        for person in unique_results:
            filtered_person = {}
            for field in mask_fields:
                if field in person:
                    filtered_person[field] = person[field]
            filtered_results.append(filtered_person)
        unique_results = filtered_results

    response_data = {
        "results": unique_results,
        "totalItems": len(unique_results)
    }

    # Validate response using Pydantic model
    response = SearchPeopleResponse(**response_data)
    return response.dict(by_alias=True)


def get_batch_get(resource_names: List[str], person_fields: Optional[str] = None,
                  sources: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Get a collection of people by resource names.
    
    This method retrieves multiple people from the user's contacts in a single request.
    This is more efficient than making multiple individual get_contact calls.
    
    Args:
        resource_names (List[str]): List of resource names of the people to retrieve.
                                   Must contain between 1 and 50 resource names.
                                   Each resource name must start with "people/".
                                   Example: ["people/123456789", "people/987654321"]
        person_fields (Optional[str]): Comma-separated list of person fields to include in the response.
                                      Valid fields: names, emailAddresses, phoneNumbers, addresses,
                                      organizations, birthdays, photos, urls, userDefined, resourceName,
                                      etag, created, updated.
        sources (Optional[List[str]]): List of sources to retrieve data from. Valid sources include
                                      "READ_SOURCE_TYPE_PROFILE", "READ_SOURCE_TYPE_CONTACT",
                                      "READ_SOURCE_TYPE_DOMAIN_PROFILE", "READ_SOURCE_TYPE_DIRECTORY".
    
    Returns:
        Dict[str, Any]: A dictionary containing the batch of people with the following structure:
            {
                "responses": [
                    {
                        "resourceName": "people/123456789",
                        "etag": "etag_123456789",
                        "names": [...],
                        "emailAddresses": [...],
                        ...
                    }
                ],
                "notFound": ["people/999999999"],
                "totalItems": 2
            }
    
    Raises:
        ValueError: If resource_names is empty or contains invalid resource names.
        ValidationError: If the input parameters fail validation.
    

    """
    # Validate input using Pydantic model
    request = BatchGetRequest(
        resource_names=resource_names,
        person_fields=person_fields,
        sources=sources
    )
    
    logger.info(f"Getting batch of people: {request.resource_names}")

    db = DB
    people_data = db.get("people", {})

    results = []
    not_found = []

    for resource_name in request.resource_names:
        if resource_name in people_data:
            person = people_data[resource_name].copy()

            # Filter by person_fields if specified
            if request.person_fields:
                field_list = [field.strip() for field in request.person_fields.split(",")]
                filtered_person = {}
                for field in field_list:
                    if field in person:
                        filtered_person[field] = person[field]
                person = filtered_person

            results.append(person)
        else:
            not_found.append(resource_name)

    response_data = {
        "responses": results,
        "notFound": not_found,
        "totalItems": len(results)
    }

    # Validate response using Pydantic model
    response = BatchGetResponse(**response_data)
    return response.dict(by_alias=True)


def get_directory_person(resource_name: str, read_mask: Optional[str] = None,
                         sources: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Get a single directory person by resource name.
    
    This method retrieves a specific person from the Google Workspace directory.
    Directory people are users in your organization's Google Workspace domain.
    
    Args:
        resource_name (str): The resource name of the directory person to retrieve.
                            Must start with "directoryPeople/".
                            Example: "directoryPeople/123456789"
        read_mask (Optional[str]): A field mask to restrict which fields on each person are returned.
                                  Valid fields: names, emailAddresses, phoneNumbers, addresses,
                                  organizations, birthdays, photos, urls, userDefined, resourceName,
                                  etag, created, updated.
        sources (Optional[List[str]]): List of sources to retrieve data from. Valid sources include
                                      "READ_SOURCE_TYPE_PROFILE", "READ_SOURCE_TYPE_CONTACT",
                                      "READ_SOURCE_TYPE_DOMAIN_PROFILE", "READ_SOURCE_TYPE_DIRECTORY".
    
    Returns:
        Dict[str, Any]: A dictionary containing the directory person data with the same structure
                       as a regular person, but sourced from the directory.
    
    Raises:
        ValueError: If the resource name is invalid or the directory person is not found.
        ValidationError: If the input parameters fail validation.
    

    """
    # Validate input using Pydantic model
    request = GetDirectoryPersonRequest(
        resource_name=resource_name,
        read_mask=read_mask,
        sources=sources
    )
    
    logger.info(f"Getting directory person with resource name: {request.resource_name}")

    db = DB
    directory_people_data = db.get("directoryPeople", {})

    if request.resource_name not in directory_people_data:
        raise ValueError(f"Directory person with resource name '{request.resource_name}' not found")

    directory_person = directory_people_data[request.resource_name].copy()

    # Filter by read_mask if specified
    if request.read_mask:
        mask_fields = [field.strip() for field in request.read_mask.split(",")]
        filtered_person = {}
        for field in mask_fields:
            if field in directory_person:
                filtered_person[field] = directory_person[field]
        directory_person = filtered_person

    response_data = {
        "resourceName": request.resource_name,
        "etag": directory_person.get("etag", "etag123"),
        **directory_person
    }

    return response_data


def list_directory_people(read_mask: Optional[str] = None, page_size: Optional[int] = None,
                          page_token: Optional[str] = None, sync_token: Optional[str] = None,
                          request_sync_token: Optional[bool] = None) -> Dict[str, Any]:
    """
    List directory people in the organization.
    
    This method retrieves a list of people from the Google Workspace directory.
    Directory people are users in your organization's Google Workspace domain.
    
    Args:
        read_mask (Optional[str]): A field mask to restrict which fields on each person are returned.
                                  Valid fields: names, emailAddresses, phoneNumbers, addresses,
                                  organizations, birthdays, photos, urls, userDefined, resourceName,
                                  etag, created, updated.
        page_size (Optional[int]): The number of directory people to include in the response.
                                  Must be between 1 and 1000. Defaults to 100.
        page_token (Optional[str]): A page token, received from a previous response.
                                   Used for pagination.
        sync_token (Optional[str]): A sync token, received from a previous response.
                                   Used for incremental sync.
        request_sync_token (Optional[bool]): Whether the response should include a sync token.
                                            Defaults to False.
    
    Returns:
        Dict[str, Any]: A dictionary containing the list of directory people with the following structure:
            {
                "people": [
                    {
                        "resourceName": "directoryPeople/123456789",
                        "etag": "etag_dir_123456789",
                        "names": [...],
                        "emailAddresses": [...],
                        ...
                    }
                ],
                "nextPageToken": "next_page_token_string",
                "totalItems": 50,
                "nextSyncToken": "sync_token_string"
            }
    
    Raises:
        ValueError: If read_mask is not provided or parameters are invalid.
        ValidationError: If the input parameters fail validation.
    

    """
    # Validate input using Pydantic model
    request = ListDirectoryPeopleRequest(
        read_mask=read_mask,
        page_size=page_size,
        page_token=page_token,
        sync_token=sync_token,
        request_sync_token=request_sync_token
    )
    
    logger.info("Listing directory people")

    if not request.read_mask:
        raise ValueError("read_mask is required for list_directory_people")

    db = DB
    directory_people_data = db.get("directoryPeople", {})

    # Convert to list
    people = list(directory_people_data.values())

    # Filter by read_mask
    mask_fields = [field.strip() for field in request.read_mask.split(",")]
    filtered_people = []
    for person in people:
        filtered_person = {}
        for field in mask_fields:
            if field in person:
                filtered_person[field] = person[field]
        filtered_people.append(filtered_person)

    # Apply pagination
    if request.page_size:
        start_index = 0
        if request.page_token:
            try:
                start_index = int(request.page_token)
            except ValueError:
                start_index = 0

        end_index = start_index + request.page_size
        filtered_people = filtered_people[start_index:end_index]

        next_page_token = str(end_index) if end_index < len(directory_people_data) else None
    else:
        next_page_token = None

    response_data = {
        "people": filtered_people,
        "nextPageToken": next_page_token,
        "totalItems": len(filtered_people)
    }

    # Add sync token if requested
    if request.request_sync_token:
        response_data["nextSyncToken"] = f"sync_{generate_id()}"

    # Validate response using Pydantic model
    response = ListDirectoryPeopleResponse(**response_data)
    return response.dict(by_alias=True)


def search_directory_people(query: str, read_mask: Optional[str] = None,
                            page_size: Optional[int] = None, page_token: Optional[str] = None,
                            sources: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Search for directory people in the organization.
    
    This method searches through the Google Workspace directory using a plain-text query.
    The search is performed across names, email addresses, and organization information.
    
    Args:
        query (str): The plain-text query for the request. Must not be empty and cannot exceed 1000 characters.
                     The search is case-insensitive and performs partial matching.
        read_mask (Optional[str]): A field mask to restrict which fields on each person are returned.
                                  Valid fields: names, emailAddresses, phoneNumbers, addresses,
                                  organizations, birthdays, photos, urls, userDefined, resourceName,
                                  etag, created, updated.
        page_size (Optional[int]): The number of directory people to include in the response.
                                  Must be between 1 and 1000. Defaults to 100.
        page_token (Optional[str]): A page token, received from a previous response.
                                   Used for pagination.
        sources (Optional[List[str]]): List of sources to retrieve data from. Valid sources include
                                      "READ_SOURCE_TYPE_PROFILE", "READ_SOURCE_TYPE_CONTACT",
                                      "READ_SOURCE_TYPE_DOMAIN_PROFILE", "READ_SOURCE_TYPE_DIRECTORY".
    
    Returns:
        Dict[str, Any]: A dictionary containing the search results with the following structure:
            {
                "results": [
                    {
                        "resourceName": "directoryPeople/123456789",
                        "etag": "etag_dir_123456789",
                        "names": [...],
                        "emailAddresses": [...],
                        ...
                    }
                ],
                "nextPageToken": "next_page_token_string",
                "totalItems": 5
            }
    
    Raises:
        ValueError: If the query is empty or read_mask is not provided.
        ValidationError: If the input parameters fail validation.
    

    """
    # Validate input using Pydantic model
    request = SearchDirectoryPeopleRequest(
        query=query,
        read_mask=read_mask,
        page_size=page_size,
        page_token=page_token,
        sources=sources
    )
    
    logger.info(f"Searching directory people with query: {request.query}")

    if not request.read_mask:
        raise ValueError("read_mask is required for search_directory_people")

    db = DB
    directory_people_data = db.get("directoryPeople", {})

    # Simple search implementation
    results = []
    query_lower = request.query.lower()

    for person_id, person in directory_people_data.items():
        # Search in names
        for name in person.get("names", []):
            display_name = name.get("displayName", "").lower()
            given_name = name.get("givenName", "").lower()
            family_name = name.get("familyName", "").lower()
            if (query_lower in display_name or 
                query_lower in given_name or 
                query_lower in family_name):
                results.append(person)
                break

        # Search in email addresses
        for email in person.get("emailAddresses", []):
            email_value = email.get("value", "").lower()
            if query_lower in email_value:
                results.append(person)
                break

        # Search in organizations
        for org in person.get("organizations", []):
            org_name = org.get("name", "").lower()
            org_title = org.get("title", "").lower()
            if query_lower in org_name or query_lower in org_title:
                results.append(person)
                break

    # Remove duplicates
    unique_results = []
    seen_ids = set()
    for person in results:
        if person["resourceName"] not in seen_ids:
            unique_results.append(person)
            seen_ids.add(person["resourceName"])

    # Filter by read_mask
    mask_fields = [field.strip() for field in request.read_mask.split(",")]
    filtered_results = []
    for person in unique_results:
        filtered_person = {}
        for field in mask_fields:
            if field in person:
                filtered_person[field] = person[field]
        filtered_results.append(filtered_person)

    # Apply pagination
    if request.page_size:
        start_index = 0
        if request.page_token:
            try:
                start_index = int(request.page_token)
            except ValueError:
                start_index = 0

        end_index = start_index + request.page_size
        filtered_results = filtered_results[start_index:end_index]

        next_page_token = str(end_index) if end_index < len(unique_results) else None
    else:
        next_page_token = None

    response_data = {
        "results": filtered_results,
        "nextPageToken": next_page_token,
        "totalItems": len(filtered_results)
    }

    # Validate response using Pydantic model
    response = SearchDirectoryPeopleResponse(**response_data)
    return response.dict(by_alias=True)
