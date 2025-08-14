import json
import unittest
import os
import sys
from datetime import datetime

from typing import Dict, Any, List, Tuple, Optional, Union

from google_cloud_storage.SimulationEngine.db import DB
from google_cloud_storage.SimulationEngine.custom_errors import InvalidProjectionValueError, MissingGenerationError, NotSoftDeletedError
from google_cloud_storage.SimulationEngine.custom_errors import BucketNotFoundError, MetagenerationMismatchError, BucketNotEmptyError, GenerationMismatchError
from pydantic import ValidationError
from google_cloud_storage.SimulationEngine.models import (
        BucketRequest, 
        BucketProjection, 
        PredefinedBucketAcl, 
        PredefinedDefaultObjectAcl
    )

def delete(
    bucket: str,
    if_metageneration_match: Optional[str] = None,
    if_metageneration_not_match: Optional[str] = None
) -> Dict[str, Any]:
    """
    Deletes an empty bucket.

    Deletions are permanent unless soft delete is enabled on the bucket. This function
    checks for metageneration match conditions and ensures the bucket is empty before deletion.

    Args:
        bucket (str): Name of the bucket to delete.
        if_metageneration_match (Optional[str]): If set, deletes only if the bucket's metageneration
            matches this value.
        if_metageneration_not_match (Optional[str]): If set, deletes only if the bucket's metageneration
            does not match this value.

    Returns:
        Dict[str, Any]:
        - A `message` key indicating success with the following value
            - bucket deleted successfully

    Raises:
        TypeError: If 'bucket' is not a string, or if 'if_metageneration_match' or
                   'if_metageneration_not_match' are provided and are not strings.
        BucketNotFoundError: If the specified bucket does not exist in the DB.
        MetagenerationMismatchError: If 'if_metageneration_match' or 'if_metageneration_not_match'
                                     conditions are not met.
        BucketNotEmptyError: If the bucket is not empty and cannot be deleted.
    """
    # --- Input Validation ---
    if not isinstance(bucket, str):
        raise TypeError(f"Argument 'bucket' must be a string, got {type(bucket).__name__}.")
    if if_metageneration_match is not None and not isinstance(if_metageneration_match, str):
        raise TypeError(f"Argument 'if_metageneration_match' must be a string or None, got {type(if_metageneration_match).__name__}.")
    if if_metageneration_not_match is not None and not isinstance(if_metageneration_not_match, str):
        raise TypeError(f"Argument 'if_metageneration_not_match' must be a string or None, got {type(if_metageneration_not_match).__name__}.")

    # --- Core Logic ---
    # Assume DB is accessible here
    if bucket not in DB["buckets"]:
        raise BucketNotFoundError(f"Bucket '{bucket}' not found.")

    bucket_data = DB["buckets"][bucket]

    # Check metageneration conditions
    current_metageneration = bucket_data.get("metageneration")
    if if_metageneration_match is not None:
        if current_metageneration != if_metageneration_match:
            raise MetagenerationMismatchError(f"Metageneration mismatch: Required match '{if_metageneration_match}', found '{current_metageneration}'.")
    if if_metageneration_not_match is not None:
        if current_metageneration == if_metageneration_not_match:
            raise MetagenerationMismatchError(f"Metageneration mismatch: Required non-match '{if_metageneration_not_match}', found '{current_metageneration}'.")

    # Check if bucket is empty
    if bucket_data.get("objects") and len(bucket_data["objects"]) > 0:
        raise BucketNotEmptyError(f"Bucket '{bucket}' is not empty.")

    # Perform deletion
    del DB["buckets"][bucket]

    return {"message": f"Bucket '{bucket}' deleted successfully"}


def restore(
    bucket: str,
    generation: str,
    projection: str = "full",
    user_project: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Restores a soft-deleted bucket.

    This function restores a bucket only if it exists, is soft-deleted, and its generation
    matches the provided generation value.

    Args:
        bucket (str): Name of the bucket to restore.
        generation (str): The generation of the bucket for verification.
        projection (str): Set of properties to return
            One of:
            -"full" (default)
            -"noAcl"
        user_project (Optional[str]): The project to be billed for the request; required for Requester Pays buckets.

    Returns:
        Dict[str, Any]:
        - An `error` key indicating an error describing why the restore
          did not occur with one of the following values:
            - bucket not found
            - bucket is not soft deleted
            - generation mismatch
        - On success, returns a dictionary with:
            - message (str): bucket restored successfully
            - bucket (Dict[str, Any]): Restored bucket metadata, including:
                - acl (List[BucketAccessControl])
                - billing (Dict[str, bool]):
                    - requesterPays (bool)
                - cors (List[Dict[str, Any]]):
                    - maxAgeSeconds (int)
                    - method (List[str])
                    - origin (List[str])
                    - responseHeader (List[str])
                - customPlacementConfig (Dict[str, List[str]]):
                    - dataLocations (List[str])
                - defaultEventBasedHold (bool)
                - defaultObjectAcl (List[ObjectAccessControl])
                - encryption (Dict[str, str]):
                    - defaultKmsKeyName (str)
                - etag (str)
                - hierarchicalNamespace (Dict[str, bool]):
                    - enabled (bool)
                - iamConfiguration (Dict[str, Any]):
                    - bucketPolicyOnly (Dict[str, Any]):
                        - enabled (bool)
                        - lockedTime (str)
                    - uniformBucketLevelAccess (Dict[str, Any]):
                        - enabled (bool)
                        - lockedTime (str)
                    - publicAccessPrevention (str)
                - id (str)
                - ipFilter (Dict[str, Any]):
                    - mode (str)
                    - publicNetworkSource (Dict[str, List[str]]):
                        - allowedIpCidrRanges (List[str])
                    - vpcNetworkSources (List[Dict[str, Any]]):
                        - network (str)
                        - allowedIpCidrRanges (List[str])
                - kind (str)
                - labels (Dict[str, str])
                - lifecycle (Dict[str, List[Dict[str, Any]]]):
                    - rule:
                        - action (Dict[str, str]):
                            - type (str)
                            - storageClass (str)
                        - condition (Dict[str, Any]):
                            - age (int)
                            - createdBefore (str)
                            - customTimeBefore (str)
                            - daysSinceCustomTime (int)
                            - daysSinceNoncurrentTime (int)
                            - isLive (bool)
                            - matchesPattern (str)
                            - matchesPrefix (List[str])
                            - matchesSuffix (List[str])
                            - matchesStorageClass (List[str])
                            - noncurrentTimeBefore (str)
                            - numNewerVersions (int)
                - autoclass (Dict[str, Any]):
                    - enabled (bool)
                    - toggleTime (str)
                    - terminalStorageClass (str)
                    - terminalStorageClassUpdateTime (str)
                - location (str)
                - locationType (str)
                - logging (Dict[str, str]):
                    - logBucket (str)
                    - logObjectPrefix (str)
                - generation (str)
                - metageneration (str)
                - name (str)
                - owner (Dict[str, str]):
                    - entity (str)
                    - entityId (str)
                - projectNumber (str)
                - retentionPolicy (Dict[str, Any]):
                    - effectiveTime (str)
                    - isLocked (bool)
                    - retentionPeriod (str)
                - objectRetention (Dict[str, str]):
                    - mode (str)
                - rpo (str)
                - selfLink (str)
                - softDeletePolicy (Dict[str, str]):
                    - retentionDurationSeconds (str)
                    - effectiveTime (str)
                - storageClass (str)
                - timeCreated (str)
                - updated (str)
                - softDeleteTime (str)
                - hardDeleteTime (str)
                - versioning (Dict[str, bool]):
                    - enabled (bool)
                - website (Dict[str, str]):
                    - mainPageSuffix (str)
                    - notFoundPage (str)
                - satisfiesPZS (bool)
                - satisfiesPZI (bool)
    """

    if bucket not in DB["buckets"]:
        return {"error": "Bucket not found"}
    bucket_data = DB["buckets"][bucket]
    if not bucket_data.get("softDeleted"):
        return {"error": "Bucket is not soft deleted"}
    if bucket_data.get("generation") != generation:
        return {"error": "Generation mismatch"}

    bucket_data["softDeleted"] = False
    return {
        "message": f"Bucket '{bucket}' restored successfully",
        "bucket": bucket_data,
    }


def relocate(bucket: str) -> Dict[str, Any]:
    """
    Initiates a long-running Relocate Bucket operation on the specified bucket.

    Args:
        bucket (str): Name of the bucket to be relocated.

    Returns:
        Dict[str, Any]:
        - On error:
            - "error" (str): "Bucket not found"
        - On success:
            - dictionary with the following keys:
                - done (bool): False — indicates the operation is in progress.
                - error (dict): Present only if an error occurred. Matches GoogleRpcStatus schema:
                    - code (int) : The status code, which should be an enum value of google.rpc.Code.
                    - message (str) : A developer-facing error message, which should be in English.
                    - details (list[dict]) : A list of messages that carry the error details. There is a common set of message types for APIs to use.
                - metadata (dict): Optional metadata related to the operation.
                - name (str): Unique operation name, e.g., operations/relocate-bucket-<bucket>.
                - response (dict): Result returned when operation completes.
                - selfLink (str): URI of the operation resource.
                - kind (str): Always "storage#operation".
    """
    if bucket not in DB["buckets"]:
        return {"error": "Bucket not found"}

    return {"message": f"Relocation initiated for bucket '{bucket}'"}


def get(
    bucket: str,
    generation: Optional[str] = None,
    soft_deleted: bool = False,
    if_metageneration_match: Optional[str] = None,
    if_metageneration_not_match: Optional[str] = None,
    projection: str = "noAcl"
) -> Dict[str, Any]:
    """
    Returns metadata for the specified bucket.

    This function supports conditional fetches based on metageneration and supports
    retrieval of soft-deleted buckets if specified.

    Args:
        bucket (str): Name of the bucket to retrieve metadata for.
        generation (Optional[str]): If specified, fetches the version of the bucket
            matching this generation. Required if soft_deleted is True.
        soft_deleted (bool): If True, retrieves the soft-deleted version of the bucket.
        if_metageneration_match (Optional[str]): Returns metadata only if the bucket's
            metageneration matches this value.
        if_metageneration_not_match (Optional[str]): Returns metadata only if the bucket's
            metageneration does not match this value.
        projection (str): Set of properties to return. Acceptable values:
            - "full": Includes all properties.
            - "noAcl": Excludes owner, acl, and defaultObjectAcl. Default is "noAcl".

    Returns:
        Dict[str, Any]: On a successful call, returns a dictionary containing the bucket resource.
            - "bucket" (Dict[str, Any]): A dictionary with the bucket's metadata. If 'projection' is "noAcl" (the default), `acl` and `defaultObjectAcl` are omitted. The structure includes:
                - acl (List[BucketAccessControl])
                - billing (Dict[str, bool]):
                    - requesterPays (bool)
                - cors (List[Dict[str, Any]]):
                    - maxAgeSeconds (int)
                    - method (List[str])
                    - origin (List[str])
                    - responseHeader (List[str])
                - customPlacementConfig (Dict[str, List[str]]):
                    - dataLocations (List[str])
                - defaultEventBasedHold (bool)
                - defaultObjectAcl (List[ObjectAccessControl])
                - encryption (Dict[str, str]):
                    - defaultKmsKeyName (str)
                - etag (str)
                - hierarchicalNamespace (Dict[str, bool]):
                    - enabled (bool)
                - iamConfiguration (Dict[str, Any]):
                    - bucketPolicyOnly (Dict[str, Any]):
                        - enabled (bool)
                        - lockedTime (str)
                    - uniformBucketLevelAccess (Dict[str, Any]):
                        - enabled (bool)
                        - lockedTime (str)
                    - publicAccessPrevention (str)
                - id (str)
                - ipFilter (Dict[str, Any]):
                    - mode (str)
                    - publicNetworkSource (Dict[str, List[str]]):
                        - allowedIpCidrRanges (List[str])
                    - vpcNetworkSources (List[Dict[str, Any]]):
                        - network (str)
                        - allowedIpCidrRanges (List[str])
                - kind (str)
                - labels (Dict[str, str])
                - lifecycle (Dict[str, List[Dict[str, Any]]]):
                    - rule:
                        - action (Dict[str, str]):
                            - type (str)
                            - storageClass (str)
                        - condition (Dict[str, Any]):
                            - age (int)
                            - createdBefore (str)
                            - customTimeBefore (str)
                            - daysSinceCustomTime (int)
                            - daysSinceNoncurrentTime (int)
                            - isLive (bool)
                            - matchesPattern (str)
                            - matchesPrefix (List[str])
                            - matchesSuffix (List[str])
                            - matchesStorageClass (List[str])
                            - noncurrentTimeBefore (str)
                            - numNewerVersions (int)
                - autoclass (Dict[str, Any]):
                    - enabled (bool)
                    - toggleTime (str)
                    - terminalStorageClass (str)
                    - terminalStorageClassUpdateTime (str)
                - location (str)
                - locationType (str)
                - logging (Dict[str, str]):
                    - logBucket (str)
                    - logObjectPrefix (str)
                - generation (str)
                - metageneration (str)
                - name (str)
                - owner (Dict[str, str]):
                    - entity (str)
                    - entityId (str)
                - projectNumber (str)
                - retentionPolicy (Dict[str, Any]):
                    - effectiveTime (str)
                    - isLocked (bool)
                    - retentionPeriod (str)
                - objectRetention (Dict[str, str]):
                    - mode (str)
                - rpo (str)
                - selfLink (str)
                - softDeletePolicy (Dict[str, str]):
                    - retentionDurationSeconds (str)
                    - effectiveTime (str)
                - storageClass (str)
                - timeCreated (str)
                - updated (str)
                - softDeleteTime (str)
                - hardDeleteTime (str)
                - versioning (Dict[str, bool]):
                    - enabled (bool)
                - website (Dict[str, str]):
                    - mainPageSuffix (str)
                    - notFoundPage (str)
                - satisfiesPZS (bool)
                - satisfiesPZI (bool)

    Raises:
        TypeError: If any argument is of an incorrect type.
        InvalidProjectionValueError: If 'projection' is not one of "full" or "noAcl".
        MissingGenerationError: If 'soft_deleted' is True but 'generation' is not provided.
        BucketNotFoundError: If the specified bucket does not exist.
        NotSoftDeletedError: If 'soft_deleted' is True but the bucket is not soft-deleted.
        GenerationMismatchError: If 'soft_deleted' is True and the provided 'generation' 
                                  does not match the bucket's generation.
        MetagenerationMismatchError: If 'if_metageneration_match' or
                                     'if_metageneration_not_match' conditions are not met.
    """
    # --- Input Validation Logic ---
    if not isinstance(bucket, str):
        raise TypeError("Argument 'bucket' must be a string.")
    if generation is not None and not isinstance(generation, str):
        raise TypeError("Argument 'generation' must be a string or None.")
    if not isinstance(soft_deleted, bool):
        raise TypeError("Argument 'soft_deleted' must be a boolean.")
    if if_metageneration_match is not None and not isinstance(if_metageneration_match, str):
        raise TypeError("Argument 'if_metageneration_match' must be a string or None.")
    if if_metageneration_not_match is not None and not isinstance(if_metageneration_not_match, str):
        raise TypeError("Argument 'if_metageneration_not_match' must be a string or None.")
    if not isinstance(projection, str):
        raise TypeError("Argument 'projection' must be a string.")
    
    if projection not in ("full", "noAcl"):
        raise InvalidProjectionValueError(
            f"Invalid value for 'projection': '{projection}'. Must be 'full' or 'noAcl'."
        )

    if soft_deleted and generation is None:
        raise MissingGenerationError(
            "Argument 'generation' is required when 'soft_deleted' is True."
        )
    # --- End of Input Validation Logic ---

    # --- Core Functionality ---
    if bucket not in DB["buckets"]:
        raise BucketNotFoundError(f"Bucket '{bucket}' not found.") # Raise custom error

    bucket_data = DB["buckets"][bucket]
    current_metageneration = bucket_data.get("metageneration") # Store for reuse

    if soft_deleted: # generation is guaranteed to be non-None here due to validation
        if not bucket_data.get("softDeleted"):
            raise NotSoftDeletedError(f"Bucket '{bucket}' is not soft deleted.") # Raise custom error
        if bucket_data.get("generation") != generation:
            # Include bucket name in the message for better context
            raise GenerationMismatchError(
                f"Generation mismatch for bucket '{bucket}': Required '{generation}', found '{bucket_data.get('generation')}'."
            ) # Raise custom error

    if if_metageneration_match is not None: # Changed from direct truthiness check
        if current_metageneration != if_metageneration_match:
            raise MetagenerationMismatchError(
                f"Metageneration mismatch for bucket '{bucket}': Required match '{if_metageneration_match}', found '{current_metageneration}'."
            ) # Raise custom error
            
    if if_metageneration_not_match is not None: # Changed from direct truthiness check
        if current_metageneration == if_metageneration_not_match:
            raise MetagenerationMismatchError(
                f"Metageneration mismatch for bucket '{bucket}': Required non-match '{if_metageneration_not_match}', found '{current_metageneration}'."
            ) # Raise custom error

    # If all checks pass, return the bucket data based on projection
    if projection == "full":
        return {"bucket": bucket_data}
    else:
        return {
            "bucket": {
                k: v
                for k, v in bucket_data.items()
                if k not in ["acl", "defaultObjectAcl"]
            }
        }
    # --- End of Core Functionality ---


def getIamPolicy(
    bucket: str,
    options_requested_policy_version: Optional[int] = None,
    user_project: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Returns an IAM policy for the specified bucket.

    Args:
        bucket (str): Name of the bucket whose IAM policy is being requested.
        options_requested_policy_version (Optional[int]): The desired IAM policy format version
            to be returned. Must be >= 1 if specified.
        user_project (Optional[str]): The project to be billed for this request. Required for
            Requester Pays buckets.

    Returns:
        Dict[str, Any]:
        - On error:
            - An "error" Keyword with one of the following values:
                - bucket not found
                - invalid policy version
        - On success:
            - iamPolicy (Dict[str, Any]): A policy object describing access control for the bucket.
                - bindings (List[Dict[str, Any]]): List of role-member mappings with optional condition:
                    - role (str): The IAM role string (e.g. roles/storage.admin).
                    - members (List[str]): List of member identifiers (e.g. user:alice@example.com).
                    - condition (Optional[Dict[str, Any]]): An optional condition that restricts when the binding is applied.
                    Includes:
                        - title (str): Short label for the expression.
                        - description (str): Optional description of the expression's intent.
                        - expression (str): Common Expression Language (CEL) syntax string.
                        - location (str): Optional location string for debugging (e.g., file or position).
                - etag (str): HTTP 1.1 entity tag for the policy.
                - kind (str): Resource kind, always "storage#policy".
                - resourceId (str): The resource ID the policy applies to.
                - version (int): IAM policy format version.
    """
    if bucket not in DB["buckets"]:
        return {"error": "Bucket not found"}

    bucket_data = DB["buckets"][bucket]
    iam_policy = bucket_data.get("iamPolicy", {"bindings": []})
    if options_requested_policy_version and options_requested_policy_version < 1:
        return {"error": "invalid policy version"}
    return {"iamPolicy": iam_policy}


def getStorageLayout(bucket: str, prefix: Optional[str] = None) -> Dict[str, Any]:
    """
    Returns the storage layout configuration for the specified bucket.

    This operation requires the `storage.objects.list` permission. If a `prefix` is specified,
    it can be used to restrict access validation under that specific prefix.

    Args:
        bucket (str): Name of the bucket whose storage layout is to be retrieved.
        prefix (Optional[str]): Optional prefix used for permission checks. Useful when the caller
            only has permission under a specific path within the bucket.

    Returns:
        Dict[str, Any]:
        - On error:
            - An "error" Keyword with the following value:
                - "Bucket not found"
        - On success:
            - storageLayout (Dict[str, Any]) with the following keys:
                - bucket (str): The name of the bucket.
                - customPlacementConfig (Dict[str, List[str]]):
                    - dataLocations (List[str]): Regional locations where data is placed.
                - hierarchicalNamespace (Dict[str, bool]):
                    - enabled (bool): True if hierarchical namespace is enabled.
                - kind (str): Always "storage#storageLayout".
                - location (str): The physical location of the bucket.
                - locationType (str): Type of location configuration (e.g., multi-region, region).
    """
    if bucket not in DB["buckets"]:
        return {"error": "Bucket not found"}
    bucket_data = DB["buckets"][bucket]
    storage_layout = bucket_data.get("storageLayout", {})
    return {"storageLayout": storage_layout}


def insert(
    project: str,
    bucket_request: Optional[Dict[str, Any]] = None,
    predefinedAcl: Optional[str] = None,
    predefined_default_object_acl: Optional[str] = None,
    projection: str = "noAcl",
    user_project: Optional[str] = None,
    enableObjectRetention: bool = False,
) -> Dict[str, Any]:
    """
    Creates a new bucket.

    Args:
        project (str): A valid API project identifier.
        bucket_request (Optional[Dict[str, Any]]): A dictionary representing the bucket properties
            to create. Will be validated against the BucketRequest model. If not provided, a default
            bucket with auto-generated name will be created. Supported keys:
            - name (str): Bucket name (required if provided)
            - storageClass (str): Storage class (STANDARD, NEARLINE, COLDLINE, ARCHIVE, etc.)
            - location (str): Bucket location
            - billing (Dict[str, bool]): Billing configuration
                - requesterPays (bool): Whether requester pays is enabled
            - cors (List[Dict[str, Any]]): CORS configuration rules
                - maxAgeSeconds (int): Max age for preflight cache
                - method (List[str]): HTTP methods allowed
                - origin (List[str]): Origins allowed
                - responseHeader (List[str]): Headers allowed in response
            - customPlacementConfig (Dict[str, List[str]]): Custom dual region placement
                - dataLocations (List[str]): List of regional locations
            - hierarchicalNamespace (Dict[str, bool]): Hierarchical namespace config
                - enabled (bool): Whether hierarchical namespace is enabled
            - iamConfiguration (Dict[str, Any]): IAM configuration
                - uniformBucketLevelAccess (Dict[str, Any]): Uniform bucket-level access config
                    - enabled (bool): Whether enabled
                    - lockedTime (str): When it was locked (RFC 3339 format)
                - bucketPolicyOnly (Dict[str, Any]): Legacy bucket policy only config
                    - enabled (bool): Whether enabled
                    - lockedTime (str): When it was locked (RFC 3339 format)
                - publicAccessPrevention (str): Public access prevention ("inherited" or "enforced")
            - ipFilter (Dict[str, Any]): IP filter configuration
                - mode (str): Filter mode ("Enabled" or "Disabled")
                - publicNetworkSource (Dict[str, List[str]]): Public network sources
                    - allowedIpCidrRanges (List[str]): List of allowed IP CIDR ranges
                - vpcNetworkSources (List[Dict[str, Any]]): VPC network sources
                    - network (str): VPC network resource name
                    - allowedIpCidrRanges (List[str]): List of allowed IP CIDR ranges
            - lifecycle (Dict[str, List[Dict[str, Any]]]): Lifecycle management rules
                - rule (List[Dict[str, Any]]): List of lifecycle rules
                    - action (Dict[str, str]): Action to take
                        - type (str): Action type (Delete, SetStorageClass, AbortIncompleteMultipartUpload)
                        - storageClass (str): Target storage class for SetStorageClass action
                    - condition (Dict[str, Any]): Conditions for applying the rule
                        - age (int): Age of object in days
                        - createdBefore (str): Date in RFC 3339 format
                        - customTimeBefore (str): Date in RFC 3339 format
                        - daysSinceCustomTime (int): Days since custom time
                        - daysSinceNoncurrentTime (int): Days since noncurrent time
                        - isLive (bool): Whether object is live
                        - matchesPattern (str): Regular expression pattern
                        - matchesPrefix (List[str]): Object name prefixes
                        - matchesSuffix (List[str]): Object name suffixes
                        - matchesStorageClass (List[str]): Storage classes to match
                        - noncurrentTimeBefore (str): Date in RFC 3339 format
                        - numNewerVersions (int): Number of newer versions
            - autoclass (Dict[str, Any]): Autoclass configuration
                - enabled (bool): Whether autoclass is enabled
                - toggleTime (str): Time autoclass was toggled (RFC 3339 format)
                - terminalStorageClass (str): Terminal storage class (NEARLINE or ARCHIVE)
                - terminalStorageClassUpdateTime (str): Time terminal class was updated (RFC 3339)
            - versioning (Dict[str, bool]): Versioning configuration
                - enabled (bool): Whether versioning is enabled
            - website (Dict[str, str]): Website configuration
                - mainPageSuffix (str): Main page suffix (e.g., "index.html")
                - notFoundPage (str): 404 page (e.g., "404.html")
            - logging (Dict[str, str]): Access logging configuration
                - logBucket (str): Destination bucket for logs
                - logObjectPrefix (str): Prefix for log objects
            - retentionPolicy (Dict[str, Any]): Retention policy
                - effectiveTime (str): When policy became effective (RFC 3339 format)
                - isLocked (bool): Whether policy is locked
                - retentionPeriod (str): Retention period in seconds
            - objectRetention (Dict[str, str]): Object retention configuration
                - mode (str): Object retention mode
            - softDeletePolicy (Dict[str, str]): Soft delete policy
                - retentionDurationSeconds (str): Retention duration in seconds
                - effectiveTime (str): When policy became effective (RFC 3339 format)
            - encryption (Dict[str, str]): Encryption configuration
                - defaultKmsKeyName (str): Default KMS key resource name
            - owner (Dict[str, str]): Bucket owner information
                - entity (str): Owner entity
                - entityId (str): Owner entity ID
            - labels (Dict[str, str]): User-defined labels (key-value pairs)
            - defaultEventBasedHold (bool): Default event-based hold for new objects
            - rpo (str): Recovery Point Objective ("DEFAULT" or "ASYNC_TURBO")
            - locationType (str): Type of location (e.g., "region", "dual-region")
            - projectNumber (str): Project number bucket belongs to
            - satisfiesPZS (bool): Whether bucket satisfies Zone Separation
            - satisfiesPZI (bool): Whether bucket satisfies Zone Isolation
            Defaults to None.
        predefinedAcl (Optional[str]): Apply a predefined set of access controls to this bucket.
            Valid values:
            - "authenticatedRead": Project team owners get OWNER access, allAuthenticatedUsers get READER access
            - "private": Project team owners get OWNER access
            - "projectPrivate": Project team members get access according to their roles
            - "publicRead": Project team owners get OWNER access, allUsers get READER access
            - "publicReadWrite": Project team owners get OWNER access, allUsers get WRITER access
            Defaults to None.
        predefined_default_object_acl (Optional[str]): Apply a predefined set of default object
            access controls to this bucket. Valid values:
            - "authenticatedRead": Object owner gets OWNER access, allAuthenticatedUsers get READER access
            - "bucketOwnerFullControl": Object owner gets OWNER access, project team owners get OWNER access
            - "bucketOwnerRead": Object owner gets OWNER access, project team owners get READER access
            - "private": Object owner gets OWNER access
            - "projectPrivate": Object owner gets OWNER access, project team members get access according to roles
            - "publicRead": Object owner gets OWNER access, allUsers get READER access
            Defaults to None.
        projection (str): Set of properties to return in the response. Valid values:
            - "full": Include all properties
            - "noAcl": Omit owner, acl and defaultObjectAcl properties
            Defaults to "noAcl".
        user_project (Optional[str]): The project to be billed for this request. Required for
            Requester Pays buckets. Defaults to None.
        enableObjectRetention (bool): If True, enables object retention on the bucket.
            Defaults to False.

    Returns:
        Dict[str, Any]:
        - On success (if projection is "full" otherwise `acl` and `defaultObjectAcl` are omitted):
            - "bucket" (Dict[str, Any]) with the following keys:
                - name (str): Bucket name
                - id (str): Bucket ID
                - kind (str): Resource kind (always "storage#bucket")
                - storageClass (str): Current storage class
                - location (str): Bucket location
                - metageneration (str): Current metageneration (incremented after update)
                - generation (str): Bucket generation
                - timeCreated (str): Creation time (RFC 3339 format)
                - updated (str): Last update time (RFC 3339 format)
                - etag (str): Entity tag for the bucket
                - projectNumber (str): Project number
                - acl (List[Dict[str, Any]]): Access control list (omitted if projection="noAcl")
                    - bucket (str): Name of the bucket
                    - domain (str): Domain associated with the entity
                    - email (str): Email address associated with the entity
                    - entity (str): The entity holding the permission
                    - entityId (str): ID for the entity
                    - etag (str): HTTP 1.1 Entity tag for the access-control entry
                    - id (str): ID of the access-control entry
                    - kind (str): Always "storage#bucketAccessControl"
                    - projectTeam (Dict[str, str]): Project team associated with entity
                        - projectNumber (str): Project number
                        - team (str): Team name
                    - role (str): Access permission for the entity
                    - selfLink (str): Link to this access-control entry
                - defaultObjectAcl (List[Dict[str, Any]]): Default object ACL (omitted if projection="noAcl")
                    - bucket (str): Name of the bucket
                    - domain (str): Domain associated with the entity
                    - email (str): Email address associated with the entity
                    - entity (str): The entity holding the permission
                    - entityId (str): ID for the entity
                    - etag (str): HTTP 1.1 Entity tag for the access-control entry
                    - generation (str): Content generation of the object
                    - id (str): ID of the access-control entry
                    - kind (str): Always "storage#objectAccessControl"
                    - object (str): Name of the object
                    - projectTeam (Dict[str, str]): Project team associated with entity
                        - projectNumber (str): Project number
                        - team (str): Team name
                    - role (str): Access permission for the entity
                    - selfLink (str): Link to this access-control entry
                - billing (Dict[str, bool]): Billing configuration
                    - requesterPays (bool): Whether requester pays is enabled
                - cors (List[Dict[str, Any]]): CORS configuration rules
                    - maxAgeSeconds (int): Max age for preflight cache
                    - method (List[str]): HTTP methods allowed
                    - origin (List[str]): Origins allowed
                    - responseHeader (List[str]): Headers allowed in response
                - versioning (Dict[str, bool]): Versioning configuration
                    - enabled (bool): Whether versioning is enabled
                - lifecycle (Dict[str, List[Dict[str, Any]]]): Lifecycle configuration
                    - rule (List[Dict[str, Any]]): List of lifecycle rules
                        - action (Dict[str, str]): Action to take
                            - type (str): Action type (Delete, SetStorageClass, etc.)
                            - storageClass (str): Target storage class for SetStorageClass
                        - condition (Dict[str, Any]): Conditions for applying the rule
                            - age (int): Age of object in days
                            - createdBefore (str): Date in RFC 3339 format
                            - customTimeBefore (str): Date in RFC 3339 format
                            - daysSinceCustomTime (int): Days since custom time
                            - daysSinceNoncurrentTime (int): Days since noncurrent time
                            - isLive (bool): Whether object is live
                            - matchesPattern (str): Regular expression pattern
                            - matchesPrefix (List[str]): Object name prefixes
                            - matchesSuffix (List[str]): Object name suffixes
                            - matchesStorageClass (List[str]): Storage classes to match
                            - noncurrentTimeBefore (str): Date in RFC 3339 format
                            - numNewerVersions (int): Number of newer versions
                - customPlacementConfig (Dict[str, List[str]]): Custom dual region placement
                    - dataLocations (List[str]): List of regional locations
                - hierarchicalNamespace (Dict[str, bool]): Hierarchical namespace config
                    - enabled (bool): Whether hierarchical namespace is enabled
                - iamConfiguration (Dict[str, Any]): IAM configuration
                    - uniformBucketLevelAccess (Dict[str, Any]): Uniform bucket-level access config
                        - enabled (bool): Whether enabled
                        - lockedTime (str): When it was locked (RFC 3339 format)
                    - bucketPolicyOnly (Dict[str, Any]): Legacy bucket policy only config
                        - enabled (bool): Whether enabled
                        - lockedTime (str): When it was locked (RFC 3339 format)
                    - publicAccessPrevention (str): Public access prevention setting
                - ipFilter (Dict[str, Any]): IP filter configuration
                    - mode (str): Filter mode ("Enabled" or "Disabled")
                    - publicNetworkSource (Dict[str, List[str]]): Public network sources
                        - allowedIpCidrRanges (List[str]): List of allowed IP CIDR ranges
                    - vpcNetworkSources (List[Dict[str, Any]]): VPC network sources
                        - network (str): VPC network resource name
                        - allowedIpCidrRanges (List[str]): List of allowed IP CIDR ranges
                - autoclass (Dict[str, Any]): Autoclass configuration
                    - enabled (bool): Whether autoclass is enabled
                    - toggleTime (str): Time autoclass was toggled (RFC 3339 format)
                    - terminalStorageClass (str): Terminal storage class (NEARLINE or ARCHIVE)
                    - terminalStorageClassUpdateTime (str): Time terminal class was updated (RFC 3339)
                - website (Dict[str, str]): Website configuration
                    - mainPageSuffix (str): Main page suffix (e.g., "index.html")
                    - notFoundPage (str): 404 page (e.g., "404.html")
                - logging (Dict[str, str]): Access logging configuration
                    - logBucket (str): Destination bucket for logs
                    - logObjectPrefix (str): Prefix for log objects
                - retentionPolicy (Dict[str, Any]): Retention policy
                    - effectiveTime (str): When policy became effective (RFC 3339 format)
                    - isLocked (bool): Whether policy is locked
                    - retentionPeriod (str): Retention period in seconds
                - objectRetention (Dict[str, str]): Object retention configuration
                    - mode (str): Object retention mode
                - softDeletePolicy (Dict[str, str]): Soft delete policy
                    - retentionDurationSeconds (str): Retention duration in seconds
                    - effectiveTime (str): When policy became effective (RFC 3339 format)
                - encryption (Dict[str, str]): Encryption configuration
                    - defaultKmsKeyName (str): Default KMS key resource name
                - owner (Dict[str, str]): Bucket owner information
                    - entity (str): Owner entity
                    - entityId (str): Owner entity ID
                - labels (Dict[str, str]): User-defined labels (key-value pairs)
                - defaultEventBasedHold (bool): Default event-based hold for new objects
                - rpo (str): Recovery Point Objective ("DEFAULT" or "ASYNC_TURBO")
                - locationType (str): Type of location (e.g., "region", "dual-region")
                - satisfiesPZS (bool): Whether bucket satisfies Zone Separation
                - satisfiesPZI (bool): Whether bucket satisfies Zone Isolation
                - enableObjectRetention (bool): Whether object retention is enabled

    Raises:
        ValueError: If bucket_request validation fails, bucket name is missing, or bucket already exists.
        TypeError: If bucket_request is not a dictionary.
    """
     # Input validation
    if not isinstance(project, str):
        raise TypeError("Project must be a string")
    
    # Provide default bucket_request if none provided (for backward compatibility)
    if bucket_request is None:
        bucket_name = f"bucket-{len(DB.get('buckets', {})) + 1}"
        bucket_request = {
            "name": bucket_name,
            "location": "US",
            "storageClass": "STANDARD"
        }
        
    if not isinstance(bucket_request, dict):
        raise TypeError("Invalid bucket_request; must be a dictionary")

    # Validate predefinedAcl using enum if available
    if predefinedAcl is not None:
        if PredefinedBucketAcl:
            valid_acls = [acl.value for acl in PredefinedBucketAcl]
        else:
            valid_acls = ["authenticatedRead", "private", "projectPrivate", "publicRead", "publicReadWrite"]
        
        if predefinedAcl not in valid_acls:
            raise ValueError(f"Invalid predefinedAcl. Must be one of: {valid_acls}")

    # Validate predefined_default_object_acl using enum if available
    if predefined_default_object_acl is not None:
        if PredefinedDefaultObjectAcl:
            valid_default_acls = [acl.value for acl in PredefinedDefaultObjectAcl]
        else:
            valid_default_acls = ["authenticatedRead", "bucketOwnerFullControl", "bucketOwnerRead", 
                                 "private", "projectPrivate", "publicRead"]
        
        if predefined_default_object_acl not in valid_default_acls:
            raise ValueError(f"Invalid predefined_default_object_acl. Must be one of: {valid_default_acls}")

    # Validate projection using enum if available
    if projection is not None:
        if BucketProjection:
            valid_projections = [proj.value for proj in BucketProjection]
        else:
            valid_projections = ["full", "noAcl"]
            
        if projection not in valid_projections:
            raise ValueError(f"Invalid projection. Must be one of: {valid_projections}")

    try:
        # Validate the bucket request using Pydantic model
        if BucketRequest:
            validated_bucket = BucketRequest(**bucket_request)
            validated_data = validated_bucket.model_dump(exclude_none=True)
        else:
            # Fallback when models not available - basic validation
            validated_data = bucket_request.copy()
            
            # Basic validation for common fields when models not available
            if "storageClass" in validated_data:
                valid_storage_classes = ["STANDARD", "NEARLINE", "COLDLINE", "ARCHIVE", 
                                       "MULTI_REGIONAL", "REGIONAL", "DURABLE_REDUCED_AVAILABILITY"]
                if validated_data["storageClass"] not in valid_storage_classes:
                    raise ValueError(f"Invalid storageClass. Must be one of: {valid_storage_classes}")
                    
            if "rpo" in validated_data:
                valid_rpo_values = ["DEFAULT", "ASYNC_TURBO"]
                if validated_data["rpo"] not in valid_rpo_values:
                    raise ValueError(f"Invalid rpo. Must be one of: {valid_rpo_values}")
                    
            if "location" in validated_data and validated_data["location"] == "":
                raise ValueError("Location cannot be empty string")

        # Extract required fields
        bucket_name = validated_data.get("name")
        if not bucket_name:
            raise ValueError("Bucket name is required")

        # Check if bucket already exists
        if bucket_name in DB.get("buckets", {}):
            raise ValueError(f"Bucket {bucket_name} already exists")

        # Set defaults for required fields
        current_time = datetime.now().isoformat() + "Z"
        bucket_data = {
            "name": bucket_name,
            "project": project,
            "id": f"{project}/{bucket_name}",
            "metageneration": "1",
            "generation": "1",
            "kind": "storage#bucket",
            "timeCreated": current_time,
            "updated": current_time,
            "softDeleted": False,
            "objects": [],
            "enableObjectRetention": enableObjectRetention,
            "iamPolicy": {"bindings": []},
            "storageLayout": {},
            "storageClass": "STANDARD",  # Default storage class
            "location": "US",  # Default location
            "etag": f"etag-{bucket_name}-{current_time}",
            "selfLink": f"https://www.googleapis.com/storage/v1/b/{bucket_name}",
            "projectNumber": "123456789012"  # Standard 12-digit project number format
        }

        # Merge validated data with defaults (validated data takes precedence)
        for key, value in validated_data.items():
            if value is not None:  # Only update with non-None values
                bucket_data[key] = value

        # Apply predefined ACLs if specified (these override bucket_request values)
        if predefinedAcl:
            bucket_data["acl"] = predefinedAcl
        else:
            bucket_data["acl"] = []
            
        if predefined_default_object_acl:
            bucket_data["defaultObjectAcl"] = predefined_default_object_acl
        else:
            bucket_data["defaultObjectAcl"] = []

        # Ensure critical fields are set correctly (these should not be overridden)
        bucket_data["project"] = project
        bucket_data["enableObjectRetention"] = enableObjectRetention
        bucket_data["kind"] = "storage#bucket"  # Always ensure this is correct

        # Initialize DB if needed
        if "buckets" not in DB:
            DB["buckets"] = {}
            
        # Store the bucket
        DB["buckets"][bucket_name] = bucket_data

        # Apply projection for response
        if projection == "noAcl":
            response_data = {k: v for k, v in bucket_data.items() 
                            if k not in ["acl", "defaultObjectAcl"]}
        else:
            response_data = bucket_data.copy()

        return {"bucket": response_data}

    except ValidationError as e:
        error_details = []
        for error in e.errors():
            field = ".".join(str(x) for x in error["loc"])
            error_details.append(f"{field}: {error['msg']}")
        raise ValueError(f"Validation error: {'; '.join(error_details)}")
    except Exception as e:
        if isinstance(e, (ValueError, TypeError)):
            raise
        raise ValueError(f"Validation error: {str(e)}")


def list(
    project: str,
    max_results: int = 1000,
    page_token: Optional[str] = None,
    prefix: Optional[str] = None,
    soft_deleted: bool = False,
    projection: str = "noAcl",
    user_project: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retrieves a list of buckets for a given project.

    Args:
        project (str): A valid API project identifier.
        max_results (int): Maximum number of buckets to return. Defaults to 1000.
        page_token (Optional[str]): Token indicating the starting point for the next page of results.
        prefix (Optional[str]): Filter to include only buckets whose names begin with this prefix.
        soft_deleted (bool): If True, only returns soft-deleted buckets.
        projection (str): Properties to return for each bucket. Allowed values:
            - "full": Include all properties.
            - "noAcl": Exclude ACL-related properties. Default is "noAcl".
        user_project (Optional[str]): The project to be billed for the request.

    Returns:
        Dict[str, Any]:
        - items (List[Dict[str, Any]]): List of matching bucket metadata dictionaries.
            - list of dictionaries with the following keys(if projection is not "full" the keys acl and defaultObjectAcl are omitted):
                - acl (List[BucketAccessControl])
                - billing (Dict[str, bool]):
                    - requesterPays (bool)
                - cors (List[Dict[str, Any]]):
                    - maxAgeSeconds (int)
                    - method (List[str])
                    - origin (List[str])
                    - responseHeader (List[str])
                - customPlacementConfig (Dict[str, List[str]]):
                    - dataLocations (List[str])
                - defaultEventBasedHold (bool)
                - defaultObjectAcl (List[ObjectAccessControl])
                - encryption (Dict[str, str]):
                    - defaultKmsKeyName (str)
                - etag (str)
                - hierarchicalNamespace (Dict[str, bool]):
                    - enabled (bool)
                - iamConfiguration (Dict[str, Any]):
                    - bucketPolicyOnly (Dict[str, Any]):
                        - enabled (bool)
                        - lockedTime (str)
                    - uniformBucketLevelAccess (Dict[str, Any]):
                        - enabled (bool)
                        - lockedTime (str)
                    - publicAccessPrevention (str)
                - id (str)
                - ipFilter (Dict[str, Any]):
                    - mode (str)
                    - publicNetworkSource (Dict[str, List[str]]):
                        - allowedIpCidrRanges (List[str])
                    - vpcNetworkSources (List[Dict[str, Any]]):
                        - network (str)
                        - allowedIpCidrRanges (List[str])
                - kind (str)
                - labels (Dict[str, str])
                - lifecycle (Dict[str, List[Dict[str, Any]]]):
                    - rule:
                        - action (Dict[str, str]):
                            - type (str)
                            - storageClass (str)
                        - condition (Dict[str, Any]):
                            - age (int)
                            - createdBefore (str)
                            - customTimeBefore (str)
                            - daysSinceCustomTime (int)
                            - daysSinceNoncurrentTime (int)
                            - isLive (bool)
                            - matchesPattern (str)
                            - matchesPrefix (List[str])
                            - matchesSuffix (List[str])
                            - matchesStorageClass (List[str])
                            - noncurrentTimeBefore (str)
                            - numNewerVersions (int)
                - autoclass (Dict[str, Any]):
                    - enabled (bool)
                    - toggleTime (str)
                    - terminalStorageClass (str)
                    - terminalStorageClassUpdateTime (str)
                - location (str)
                - locationType (str)
                - logging (Dict[str, str]):
                    - logBucket (str)
                    - logObjectPrefix (str)
                - generation (str)
                - metageneration (str)
                - name (str)
                - owner (Dict[str, str]):
                    - entity (str)
                    - entityId (str)
                - projectNumber (str)
                - retentionPolicy (Dict[str, Any]):
                    - effectiveTime (str)
                    - isLocked (bool)
                    - retentionPeriod (str)
                - objectRetention (Dict[str, str]):
                    - mode (str)
                - rpo (str)
                - selfLink (str)
                - softDeletePolicy (Dict[str, str]):
                    - retentionDurationSeconds (str)
                    - effectiveTime (str)
                - storageClass (str)
                - timeCreated (str)
                - updated (str)
                - softDeleteTime (str)
                - hardDeleteTime (str)
                - versioning (Dict[str, bool]):
                    - enabled (bool)
                - website (Dict[str, str]):
                    - mainPageSuffix (str)
                    - notFoundPage (str)
                - satisfiesPZS (bool)
                - satisfiesPZI (bool)

        - nextPageToken (Optional[str]): Token for the next page of results, if available.
    """
    matching_buckets = []
    for bucket_name, bucket_data in DB["buckets"].items():
        if bucket_data["project"] == project:
            if prefix and not bucket_name.startswith(prefix):
                continue
            if soft_deleted and not bucket_data.get("softDeleted", False):
                continue
            if not soft_deleted and bucket_data.get("softDeleted", False):
                continue
            if projection == "full":
                matching_buckets.append(bucket_data)
            else:
                matching_buckets.append(
                    {
                        k: v
                        for k, v in bucket_data.items()
                        if k not in ["acl", "defaultObjectAcl"]
                    }
                )
    return {"items": matching_buckets[:max_results]}


def lockRetentionPolicy(
    bucket: str,
    if_metageneration_match: str,
    user_project: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Locks retention policy on a bucket.

    This operation sets the `retentionPolicyLocked` flag to True, preventing future changes
    to the retention policy. The action is conditional on the bucket's current metageneration
    matching the specified value.

    Args:
        bucket (str): Name of the bucket on which to lock the retention policy.
        if_metageneration_match (str): Locks only if the bucket's metageneration matches this value.
        user_project (Optional[str]): The project to be billed for the request. Required for
            Requester Pays buckets.

    Returns:
        Dict[str, Any]:
        - On error:
            - 'error' keyword with one of the following values:
                - bucket not found
                - metageneration mismatch
        - On success:
            - "bucket" keyword with the following value:
                - dictionary with the following keys:
                    - acl (List[BucketAccessControl])
                    - billing (Dict[str, bool]):
                        - requesterPays (bool)
                    - cors (List[Dict[str, Any]]):
                        - maxAgeSeconds (int)
                        - method (List[str])
                        - origin (List[str])
                        - responseHeader (List[str])
                    - customPlacementConfig (Dict[str, List[str]]):
                        - dataLocations (List[str])
                    - defaultEventBasedHold (bool)
                    - defaultObjectAcl (List[ObjectAccessControl])
                    - encryption (Dict[str, str]):
                        - defaultKmsKeyName (str)
                    - etag (str)
                    - hierarchicalNamespace (Dict[str, bool]):
                        - enabled (bool)
                    - iamConfiguration (Dict[str, Any]):
                        - bucketPolicyOnly (Dict[str, Any]):
                            - enabled (bool)
                            - lockedTime (str)
                        - uniformBucketLevelAccess (Dict[str, Any]):
                            - enabled (bool)
                            - lockedTime (str)
                        - publicAccessPrevention (str)
                    - id (str)
                    - ipFilter (Dict[str, Any]):
                        - mode (str)
                        - publicNetworkSource (Dict[str, List[str]]):
                            - allowedIpCidrRanges (List[str])
                        - vpcNetworkSources (List[Dict[str, Any]]):
                            - network (str)
                            - allowedIpCidrRanges (List[str])
                    - kind (str)
                    - labels (Dict[str, str])
                    - lifecycle (Dict[str, List[Dict[str, Any]]]):
                        - rule:
                            - action (Dict[str, str]):
                                - type (str)
                                - storageClass (str)
                            - condition (Dict[str, Any]):
                                - age (int)
                                - createdBefore (str)
                                - customTimeBefore (str)
                                - daysSinceCustomTime (int)
                                - daysSinceNoncurrentTime (int)
                                - isLive (bool)
                                - matchesPattern (str)
                                - matchesPrefix (List[str])
                                - matchesSuffix (List[str])
                                - matchesStorageClass (List[str])
                                - noncurrentTimeBefore (str)
                                - numNewerVersions (int)
                    - autoclass (Dict[str, Any]):
                        - enabled (bool)
                        - toggleTime (str)
                        - terminalStorageClass (str)
                        - terminalStorageClassUpdateTime (str)
                    - location (str)
                    - locationType (str)
                    - logging (Dict[str, str]):
                        - logBucket (str)
                        - logObjectPrefix (str)
                    - generation (str)
                    - metageneration (str)
                    - name (str)
                    - owner (Dict[str, str]):
                        - entity (str)
                        - entityId (str)
                    - projectNumber (str)
                    - retentionPolicy (Dict[str, Any]):
                        - effectiveTime (str)
                        - isLocked (bool)
                        - retentionPeriod (str)
                    - objectRetention (Dict[str, str]):
                        - mode (str)
                    - rpo (str)
                    - selfLink (str)
                    - softDeletePolicy (Dict[str, str]):
                        - retentionDurationSeconds (str)
                        - effectiveTime (str)
                    - storageClass (str)
                    - timeCreated (str)
                    - updated (str)
                    - softDeleteTime (str)
                    - hardDeleteTime (str)
                    - versioning (Dict[str, bool]):
                        - enabled (bool)
                    - website (Dict[str, str]):
                        - mainPageSuffix (str)
                        - notFoundPage (str)
                    - satisfiesPZS (bool)
                    - satisfiesPZI (bool)
    """
    if bucket not in DB["buckets"]:
        return {"error": "Bucket not found"}
    bucket_data = DB["buckets"][bucket]
    if bucket_data.get("metageneration") != if_metageneration_match:
        return {"error": "Metageneration mismatch"}
    bucket_data["retentionPolicyLocked"] = True
    return {"message": f"Retention policy locked for bucket '{bucket}'"}


def patch(
    bucket: str,
    if_metageneration_match: Optional[str] = None,
    if_metageneration_not_match: Optional[str] = None,
    predefinedAcl: Optional[str] = None,
    predefined_default_object_acl: Optional[str] = None,
    projection: Optional[str] = None,
    user_project: Optional[str] = None,
    bucket_request: Optional[Dict[str, Any]] = None,
) -> Tuple[Dict[str, Any], int]:
    """
    Patches a bucket.

    Changes to the bucket are readable immediately after writing, but configuration changes
    may take time to propagate. This operation may be conditional on metageneration match.
    Only the fields specified in bucket_request are updated; other fields remain unchanged.

    Args:
        bucket (str): Name of the bucket to update.
        if_metageneration_match (Optional[str]): Makes the patch conditional on whether the
            bucket's current metageneration matches this value. Defaults to None.
        if_metageneration_not_match (Optional[str]): Makes the patch conditional on whether the
            bucket's current metageneration does not match this value. Defaults to None.
        predefinedAcl (Optional[str]): Apply a predefined set of access controls to the bucket.
            Valid values:
            - "authenticatedRead": Project team owners get OWNER access, allAuthenticatedUsers get READER access
            - "private": Project team owners get OWNER access
            - "projectPrivate": Project team members get access according to their roles
            - "publicRead": Project team owners get OWNER access, allUsers get READER access
            - "publicReadWrite": Project team owners get OWNER access, allUsers get WRITER access
            Defaults to None.
        predefined_default_object_acl (Optional[str]): Apply a predefined set of default object
            access controls to the bucket. Valid values:
            - "authenticatedRead": Object owner gets OWNER access, allAuthenticatedUsers get READER access
            - "bucketOwnerFullControl": Object owner gets OWNER access, project team owners get OWNER access
            - "bucketOwnerRead": Object owner gets OWNER access, project team owners get READER access
            - "private": Object owner gets OWNER access
            - "projectPrivate": Object owner gets OWNER access, project team members get access according to roles
            - "publicRead": Object owner gets OWNER access, allUsers get READER access
            Defaults to None.
        projection (Optional[str]): Set of properties to return in the response. Valid values:
            - "full": Include all properties
            - "noAcl": Omit owner, acl and defaultObjectAcl properties
            Defaults to None (returns all properties).
        user_project (Optional[str]): The project to be billed for this request. Required for
            Requester Pays buckets. Defaults to None.
        bucket_request (Optional[Dict[str, Any]]): A dictionary representing the bucket properties
            to update. Will be validated against the BucketRequest model. Supported keys:
            - name (str): Bucket name
            - storageClass (str): Storage class (STANDARD, NEARLINE, COLDLINE, ARCHIVE, etc.)
            - location (str): Bucket location
            - billing (Dict[str, bool]): Billing configuration
                - requesterPays (bool): Whether requester pays is enabled
            - cors (List[Dict[str, Any]]): CORS configuration rules
                - maxAgeSeconds (int): Max age for preflight cache
                - method (List[str]): HTTP methods allowed
                - origin (List[str]): Origins allowed
                - responseHeader (List[str]): Headers allowed in response
            - customPlacementConfig (Dict[str, List[str]]): Custom dual region placement
                - dataLocations (List[str]): List of regional locations
            - hierarchicalNamespace (Dict[str, bool]): Hierarchical namespace config
                - enabled (bool): Whether hierarchical namespace is enabled
            - iamConfiguration (Dict[str, Any]): IAM configuration
                - uniformBucketLevelAccess (Dict[str, Any]): Uniform bucket-level access config
                    - enabled (bool): Whether enabled
                    - lockedTime (str): When it was locked (RFC 3339 format)
                - bucketPolicyOnly (Dict[str, Any]): Legacy bucket policy only config
                    - enabled (bool): Whether enabled
                    - lockedTime (str): When it was locked (RFC 3339 format)
                - publicAccessPrevention (str): Public access prevention ("inherited" or "enforced")
            - ipFilter (Dict[str, Any]): IP filter configuration
                - mode (str): Filter mode ("Enabled" or "Disabled")
                - publicNetworkSource (Dict[str, List[str]]): Public network sources
                    - allowedIpCidrRanges (List[str]): List of allowed IP CIDR ranges
                - vpcNetworkSources (List[Dict[str, Any]]): VPC network sources
                    - network (str): VPC network resource name
                    - allowedIpCidrRanges (List[str]): List of allowed IP CIDR ranges
            - lifecycle (Dict[str, List[Dict[str, Any]]]): Lifecycle management rules
                - rule (List[Dict[str, Any]]): List of lifecycle rules
                    - action (Dict[str, str]): Action to take
                        - type (str): Action type (Delete, SetStorageClass, AbortIncompleteMultipartUpload)
                        - storageClass (str): Target storage class for SetStorageClass action
                    - condition (Dict[str, Any]): Conditions for applying the rule
                        - age (int): Age of object in days
                        - createdBefore (str): Date in RFC 3339 format
                        - customTimeBefore (str): Date in RFC 3339 format
                        - daysSinceCustomTime (int): Days since custom time
                        - daysSinceNoncurrentTime (int): Days since noncurrent time
                        - isLive (bool): Whether object is live
                        - matchesPattern (str): Regular expression pattern
                        - matchesPrefix (List[str]): Object name prefixes
                        - matchesSuffix (List[str]): Object name suffixes
                        - matchesStorageClass (List[str]): Storage classes to match
                        - noncurrentTimeBefore (str): Date in RFC 3339 format
                        - numNewerVersions (int): Number of newer versions
            - autoclass (Dict[str, Any]): Autoclass configuration
                - enabled (bool): Whether autoclass is enabled
                - toggleTime (str): Time autoclass was toggled (RFC 3339 format)
                - terminalStorageClass (str): Terminal storage class (NEARLINE or ARCHIVE)
                - terminalStorageClassUpdateTime (str): Time terminal class was updated (RFC 3339)
            - versioning (Dict[str, bool]): Versioning configuration
                - enabled (bool): Whether versioning is enabled
            - website (Dict[str, str]): Website configuration
                - mainPageSuffix (str): Main page suffix (e.g., "index.html")
                - notFoundPage (str): 404 page (e.g., "404.html")
            - logging (Dict[str, str]): Access logging configuration
                - logBucket (str): Destination bucket for logs
                - logObjectPrefix (str): Prefix for log objects
            - retentionPolicy (Dict[str, Any]): Retention policy
                - effectiveTime (str): When policy became effective (RFC 3339 format)
                - isLocked (bool): Whether policy is locked
                - retentionPeriod (str): Retention period in seconds
            - objectRetention (Dict[str, str]): Object retention configuration
                - mode (str): Object retention mode
            - softDeletePolicy (Dict[str, str]): Soft delete policy
                - retentionDurationSeconds (str): Retention duration in seconds
                - effectiveTime (str): When policy became effective (RFC 3339 format)
            - encryption (Dict[str, str]): Encryption configuration
                - defaultKmsKeyName (str): Default KMS key resource name
            - owner (Dict[str, str]): Bucket owner information
                - entity (str): Owner entity
                - entityId (str): Owner entity ID
            - labels (Dict[str, str]): User-defined labels (key-value pairs)
            - defaultEventBasedHold (bool): Default event-based hold for new objects
            - rpo (str): Recovery Point Objective ("DEFAULT" or "ASYNC_TURBO")
            - locationType (str): Type of location (e.g., "region", "dual-region")
            - projectNumber (str): Project number bucket belongs to
            - satisfiesPZS (bool): Whether bucket satisfies Zone Separation
            - satisfiesPZI (bool): Whether bucket satisfies Zone Isolation
            Defaults to None.

    Returns:
        Tuple[Dict[str, Any], int]: A tuple containing:
            - Dictionary with bucket metadata (filtered by projection if specified):
                - name (str): Bucket name
                - id (str): Bucket ID
                - kind (str): Resource kind (always "storage#bucket")
                - storageClass (str): Current storage class
                - location (str): Bucket location
                - metageneration (str): Current metageneration (incremented after update)
                - generation (str): Bucket generation
                - timeCreated (str): Creation time (RFC 3339 format)
                - updated (str): Last update time (RFC 3339 format)
                - etag (str): Entity tag for the bucket
                - projectNumber (str): Project number
                - acl (List[Dict[str, Any]]): Access control list (omitted if projection="noAcl")
                    - bucket (str): Name of the bucket
                    - domain (str): Domain associated with the entity
                    - email (str): Email address associated with the entity
                    - entity (str): The entity holding the permission
                    - entityId (str): ID for the entity
                    - etag (str): HTTP 1.1 Entity tag for the access-control entry
                    - id (str): ID of the access-control entry
                    - kind (str): Always "storage#bucketAccessControl"
                    - projectTeam (Dict[str, str]): Project team associated with entity
                        - projectNumber (str): Project number
                        - team (str): Team name
                    - role (str): Access permission for the entity
                    - selfLink (str): Link to this access-control entry
                - defaultObjectAcl (List[Dict[str, Any]]): Default object ACL (omitted if projection="noAcl")
                    - bucket (str): Name of the bucket
                    - domain (str): Domain associated with the entity
                    - email (str): Email address associated with the entity
                    - entity (str): The entity holding the permission
                    - entityId (str): ID for the entity
                    - etag (str): HTTP 1.1 Entity tag for the access-control entry
                    - generation (str): Content generation of the object
                    - id (str): ID of the access-control entry
                    - kind (str): Always "storage#objectAccessControl"
                    - object (str): Name of the object
                    - projectTeam (Dict[str, str]): Project team associated with entity
                        - projectNumber (str): Project number
                        - team (str): Team name
                    - role (str): Access permission for the entity
                    - selfLink (str): Link to this access-control entry
                - billing (Dict[str, bool]): Billing configuration
                    - requesterPays (bool): Whether requester pays is enabled
                - cors (List[Dict[str, Any]]): CORS configuration rules
                    - maxAgeSeconds (int): Max age for preflight cache
                    - method (List[str]): HTTP methods allowed
                    - origin (List[str]): Origins allowed
                    - responseHeader (List[str]): Headers allowed in response
                - versioning (Dict[str, bool]): Versioning configuration
                    - enabled (bool): Whether versioning is enabled
                - lifecycle (Dict[str, List[Dict[str, Any]]]): Lifecycle configuration
                    - rule (List[Dict[str, Any]]): List of lifecycle rules
                        - action (Dict[str, str]): Action to take
                            - type (str): Action type (Delete, SetStorageClass, etc.)
                            - storageClass (str): Target storage class for SetStorageClass
                        - condition (Dict[str, Any]): Conditions for applying the rule
                            - age (int): Age of object in days
                            - createdBefore (str): Date in RFC 3339 format
                            - customTimeBefore (str): Date in RFC 3339 format
                            - daysSinceCustomTime (int): Days since custom time
                            - daysSinceNoncurrentTime (int): Days since noncurrent time
                            - isLive (bool): Whether object is live
                            - matchesPattern (str): Regular expression pattern
                            - matchesPrefix (List[str]): Object name prefixes
                            - matchesSuffix (List[str]): Object name suffixes
                            - matchesStorageClass (List[str]): Storage classes to match
                            - noncurrentTimeBefore (str): Date in RFC 3339 format
                            - numNewerVersions (int): Number of newer versions
                - customPlacementConfig (Dict[str, List[str]]): Custom dual region placement
                    - dataLocations (List[str]): List of regional locations
                - hierarchicalNamespace (Dict[str, bool]): Hierarchical namespace config
                    - enabled (bool): Whether hierarchical namespace is enabled
                - iamConfiguration (Dict[str, Any]): IAM configuration
                    - uniformBucketLevelAccess (Dict[str, Any]): Uniform bucket-level access config
                        - enabled (bool): Whether enabled
                        - lockedTime (str): When it was locked (RFC 3339 format)
                    - bucketPolicyOnly (Dict[str, Any]): Legacy bucket policy only config
                        - enabled (bool): Whether enabled
                        - lockedTime (str): When it was locked (RFC 3339 format)
                    - publicAccessPrevention (str): Public access prevention setting
                - autoclass (Dict[str, Any]): Autoclass configuration
                    - enabled (bool): Whether autoclass is enabled
                    - toggleTime (str): Time autoclass was toggled (RFC 3339 format)
                    - terminalStorageClass (str): Terminal storage class
                    - terminalStorageClassUpdateTime (str): Time terminal class was updated
                - website (Dict[str, str]): Website configuration
                    - mainPageSuffix (str): Main page suffix
                    - notFoundPage (str): 404 page
                - logging (Dict[str, str]): Access logging configuration
                    - logBucket (str): Destination bucket for logs
                    - logObjectPrefix (str): Prefix for log objects
                - retentionPolicy (Dict[str, Any]): Retention policy
                    - effectiveTime (str): When policy became effective (RFC 3339 format)
                    - isLocked (bool): Whether policy is locked
                    - retentionPeriod (str): Retention period in seconds
                - objectRetention (Dict[str, str]): Object retention configuration
                    - mode (str): Object retention mode
                - softDeletePolicy (Dict[str, str]): Soft delete policy
                    - retentionDurationSeconds (str): Retention duration in seconds
                    - effectiveTime (str): When policy became effective (RFC 3339 format)
                - encryption (Dict[str, str]): Encryption configuration
                    - defaultKmsKeyName (str): Default KMS key resource name
                - owner (Dict[str, str]): Bucket owner information
                    - entity (str): Owner entity
                    - entityId (str): Owner entity ID
                - labels (Dict[str, str]): User-defined labels (key-value pairs)
                - [Additional fields as specified in bucket_request]
            - HTTP status code (200 for success, 400/404/412 for errors)

    Raises:
        TypeError: If bucket is not a string, or if optional string parameters are not strings.
        ValueError: If predefinedAcl, predefined_default_object_acl, or projection have invalid values.
        ValidationError: If bucket_request contains invalid data according to BucketRequest model.
    """
    # Input validation
    if not isinstance(bucket, str):
        return {"error": "Bucket name must be a string"}, 400
    
    if if_metageneration_match is not None and not isinstance(if_metageneration_match, str):
        return {"error": "if_metageneration_match must be a string or None"}, 400
        
    if if_metageneration_not_match is not None and not isinstance(if_metageneration_not_match, str):
        return {"error": "if_metageneration_not_match must be a string or None"}, 400

    # Validate predefinedAcl using enum if available
    if predefinedAcl is not None:
        if PredefinedBucketAcl:
            valid_acls = [acl.value for acl in PredefinedBucketAcl]
        else:
            valid_acls = ["authenticatedRead", "private", "projectPrivate", "publicRead", "publicReadWrite"]
        
        if predefinedAcl not in valid_acls:
            return {"error": f"Invalid predefinedAcl. Must be one of: {valid_acls}"}, 400

    # Validate predefined_default_object_acl using enum if available  
    if predefined_default_object_acl is not None:
        if PredefinedDefaultObjectAcl:
            valid_default_acls = [acl.value for acl in PredefinedDefaultObjectAcl]
        else:
            valid_default_acls = ["authenticatedRead", "bucketOwnerFullControl", "bucketOwnerRead", 
                                 "private", "projectPrivate", "publicRead"]
        
        if predefined_default_object_acl not in valid_default_acls:
            return {"error": f"Invalid predefined_default_object_acl. Must be one of: {valid_default_acls}"}, 400

    # Validate projection using enum if available
    if projection is not None:
        if BucketProjection:
            valid_projections = [proj.value for proj in BucketProjection]
        else:
            valid_projections = ["full", "noAcl"]
            
        if projection not in valid_projections:
            return {"error": f"Invalid projection. Must be one of: {valid_projections}"}, 400

    # Check if bucket exists
    if bucket not in DB.get("buckets", {}):
        return {"error": f"Bucket {bucket} not found"}, 404

    bucket_data = DB["buckets"][bucket]

    # Check metageneration conditions
    current_metageneration = str(bucket_data.get("metageneration", 0))
    
    if (if_metageneration_match is not None and 
        current_metageneration != if_metageneration_match):
        return {"error": "Metageneration mismatch"}, 412

    if (if_metageneration_not_match is not None and 
        current_metageneration == if_metageneration_not_match):
        return {"error": "Metageneration mismatch"}, 412

    # Apply predefined ACLs
    if predefinedAcl:
        bucket_data["acl"] = predefinedAcl
    if predefined_default_object_acl:
        bucket_data["defaultObjectAcl"] = predefined_default_object_acl

    # Validate and merge bucket_request if provided
    if bucket_request is not None:
        if not isinstance(bucket_request, dict):
            return {"error": "Invalid bucket_request; must be a dictionary"}, 400
        
        try:
            # Remove protected fields first so Pydantic does not reject them.
            protected_fields = ['id', 'kind', 'timeCreated', 'generation']
            sanitized_request = {k: v for k, v in bucket_request.items() if k not in protected_fields}

            if BucketRequest:
                # Validate the sanitized bucket request using Pydantic model
                validated_bucket = BucketRequest(**sanitized_request)
                validated_data = validated_bucket.model_dump(exclude_unset=True, exclude_none=True)
            else:
                validated_data = sanitized_request.copy()

            # Basic manual validations when Pydantic model is unavailable
            if "storageClass" in validated_data:
                valid_storage_classes = [
                    "STANDARD", "NEARLINE", "COLDLINE", "ARCHIVE",
                    "MULTI_REGIONAL", "REGIONAL", "DURABLE_REDUCED_AVAILABILITY",
                ]
                if validated_data["storageClass"] not in valid_storage_classes:
                    return {"error": f"Invalid storageClass. Must be one of: {valid_storage_classes}"}, 400

            if "rpo" in validated_data:
                valid_rpo_values = ["DEFAULT", "ASYNC_TURBO"]
                if validated_data["rpo"] not in valid_rpo_values:
                    return {"error": f"Invalid rpo. Must be one of: {valid_rpo_values}"}, 400

            if "location" in validated_data and validated_data["location"] == "":
                return {"error": "Location cannot be empty string"}, 400
            
            # Merge validated data into bucket_data (patch semantics)
            for key, value in validated_data.items():
                bucket_data[key] = value
                
        except ValidationError as e:
            error_details = []
            for error in e.errors():
                field = ".".join(str(x) for x in error["loc"])
                error_details.append(f"{field}: {error['msg']}")
            return {"error": f"Validation error: {'; '.join(error_details)}"}, 400
        except Exception as e:
            return {"error": f"Validation error: {str(e)}"}, 400

    # Increment metageneration (simulating change)
    bucket_data["metageneration"] = str(int(bucket_data.get("metageneration", 0)) + 1)
    
    # Update the updated timestamp
    bucket_data["updated"] = datetime.now().isoformat() + "Z"

    # Store updated data
    DB["buckets"][bucket] = bucket_data

    # Apply projection for response
    if projection == "noAcl":
        response_data = {k: v for k, v in bucket_data.items() 
                        if k not in ["acl", "defaultObjectAcl"]}
    else:
        response_data = bucket_data.copy()

    return response_data, 200



def setIamPolicy(
    bucket: str,
    user_project: Optional[str] = None,
) -> Tuple[Dict[str, Any], int]:
    """
    Updates an IAM policy for the specified bucket.

    Args:
        bucket (str): Name of the bucket whose IAM policy is being updated.
        user_project (Optional[str]): The project to be billed for this request. Required for
            Requester Pays buckets.

    Returns:
        Tuple[Dict[str, Any], int]:
        - On error:
            - {"error": "Bucket <name> not found"}, 404
        - On success:
            - The updated IAM policy object (Dict)
                - bindings (List[Dict[str, Any]]): Associations between roles and members. Each binding may contain:
                    - role (str): Role string assigned to members.
                      One of:
                        - roles/storage.admin
                        - roles/storage.objectViewer
                        - roles/storage.objectCreator
                        - roles/storage.objectAdmin
                        - roles/storage.legacyObjectReader
                        - roles/storage.legacyObjectOwner
                        - roles/storage.legacyBucketReader
                        - roles/storage.legacyBucketWriter
                        - roles/storage.legacyBucketOwner
                    - members (List[str]): Members granted the role.
                      One of:
                        - allUsers
                        - allAuthenticatedUsers
                        - user:<email>
                        - group:<email>
                        - domain:<domain>
                        - serviceAccount:<email>
                        - projectOwner:<projectId>
                        - projectEditor:<projectId>
                        - projectViewer:<projectId>
                    - condition (Optional[Dict[str, Any]]): A condition expression that limits when
                      the binding applies, following the `Expr` format:
                        - title (str): Short description of the condition.
                        - description (str): Detailed explanation.
                        - expression (str): CEL syntax expression.
                        - location (str): Optional location for debugging reference.
                - etag (str): HTTP 1.1 entity tag for the policy.
                - kind (str): Always "storage#policy".
                - resourceId (str): The full ID of the bucket this policy applies to.
                - version (int): IAM policy format version.
            - HTTP status code 200
    """
    if bucket not in DB.get("buckets", {}):
        return {"error": f"Bucket {bucket} not found"}, 404

    # Simulate setting IAM policy
    DB["buckets"][bucket]["iamPolicy"] = {"bindings": []}

    return DB["buckets"][bucket]["iamPolicy"], 200


def testIamPermissions(
    bucket: str,
    permissions: str,
    user_project: Optional[str] = None,
) -> Tuple[Dict[str, Any], int]:
    """
    Tests a set of permissions on the given bucket to see which, if any, are held by the caller.

    Args:
        bucket (str): Name of the bucket on which permissions are being tested.
        permissions (str): The list of permissions to test.
            One of:
            - storage.buckets.delete
            - storage.buckets.get
            - storage.buckets.getIamPolicy
            - storage.buckets.create
            - storage.buckets.list
            - storage.buckets.setIamPolicy
            - storage.buckets.update
            - storage.objects.delete
            - storage.objects.get
            - storage.objects.getIamPolicy
            - storage.objects.create
            - storage.objects.list
            - storage.objects.setIamPolicy
            - storage.objects.update
            - storage.managedFolders.delete
            - storage.managedFolders.get
            - storage.managedFolders.getIamPolicy
            - storage.managedFolders.create
            - storage.managedFolders.list
            - storage.managedFolders.setIamPolicy
        user_project (Optional[str]): The project to be billed for this request. Required for
            Requester Pays buckets.

    Returns:
        Tuple[Dict[str, Any], int]:
        - On error:
            - {"error": "Bucket <name> not found"}, 404
        - On success:
            - TestIamPermissionsResponse (Dict[str, Any]):
                - kind (str): Always "storage#testIamPermissionsResponse".
                - permissions (List[str]): A subset of the requested permissions that the caller has.

        Supported Permissions:
            - storage.buckets.delete
            - storage.buckets.get
            - storage.buckets.getIamPolicy
            - storage.buckets.create
            - storage.buckets.list
            - storage.buckets.setIamPolicy
            - storage.buckets.update
            - storage.objects.delete
            - storage.objects.get
            - storage.objects.getIamPolicy
            - storage.objects.create
            - storage.objects.list
            - storage.objects.setIamPolicy
            - storage.objects.update
            - storage.managedFolders.delete
            - storage.managedFolders.get
            - storage.managedFolders.getIamPolicy
            - storage.managedFolders.create
            - storage.managedFolders.list
            - storage.managedFolders.setIamPolicy
    """
    if bucket not in DB.get("buckets", {}):
        return {"error": f"Bucket {bucket} not found"}, 404

    # Simulate testing permissions
    return {"permissions": [permissions]}, 200


def update(
    bucket: str,
    if_metageneration_match: Optional[str] = None,
    if_metageneration_not_match: Optional[str] = None,
    predefinedAcl: Optional[str] = None,
    predefined_default_object_acl: Optional[str] = None,
    projection: Optional[str] = None,
    user_project: Optional[str] = None,
    bucket_request: Optional[Dict[str, Any]] = None,
) -> Tuple[Dict[str, Any], int]:
    """
    Updates a bucket with complete replacement using PUT semantics.

    Changes to the bucket will be readable immediately after writing, but configuration changes
    may take time to propagate. Unlike patch(), this operation completely replaces the bucket
    configuration with the provided bucket_request data, requiring bucket_request to be provided.

    Args:
        bucket (str): Name of the bucket to update.
        if_metageneration_match (Optional[str]): Makes the update conditional on whether the
            bucket's current metageneration matches this value. Defaults to None.
        if_metageneration_not_match (Optional[str]): Makes the update conditional on whether the
            bucket's current metageneration does not match this value. Defaults to None.
        predefinedAcl (Optional[str]): Apply a predefined set of access controls to the bucket.
            Valid values:
            - "authenticatedRead": Project team owners get OWNER access, allAuthenticatedUsers get READER access
            - "private": Project team owners get OWNER access
            - "projectPrivate": Project team members get access according to their roles
            - "publicRead": Project team owners get OWNER access, allUsers get READER access
            - "publicReadWrite": Project team owners get OWNER access, allUsers get WRITER access
            Defaults to None.
        predefined_default_object_acl (Optional[str]): Apply a predefined set of default object
            access controls to the bucket. Valid values:
            - "authenticatedRead": Object owner gets OWNER access, allAuthenticatedUsers get READER access
            - "bucketOwnerFullControl": Object owner gets OWNER access, project team owners get OWNER access
            - "bucketOwnerRead": Object owner gets OWNER access, project team owners get READER access
            - "private": Object owner gets OWNER access
            - "projectPrivate": Object owner gets OWNER access, project team members get access according to roles
            - "publicRead": Object owner gets OWNER access, allUsers get READER access
            Defaults to None.
        projection (Optional[str]): Set of properties to return in the response. Valid values:
            - "full": Include all properties
            - "noAcl": Omit owner, acl and defaultObjectAcl properties
            Defaults to None (returns all properties).
        user_project (Optional[str]): The project to be billed for this request. Required for
            Requester Pays buckets. Defaults to None.
        bucket_request (Optional[Dict[str, Any]]): A dictionary representing the complete bucket
            configuration to replace existing configuration. REQUIRED for update operation.
            Will be validated against the BucketRequest model. Supported keys:
            - name (str): Bucket name (will be preserved as original bucket name)
            - storageClass (str): Storage class (STANDARD, NEARLINE, COLDLINE, ARCHIVE, etc.)
            - location (str): Bucket location
            - billing (Dict[str, bool]): Billing configuration
                - requesterPays (bool): Whether requester pays is enabled
            - cors (List[Dict[str, Any]]): CORS configuration rules
                - maxAgeSeconds (int): Max age for preflight cache
                - method (List[str]): HTTP methods allowed
                - origin (List[str]): Origins allowed
                - responseHeader (List[str]): Headers allowed in response
            - customPlacementConfig (Dict[str, List[str]]): Custom dual region placement
                - dataLocations (List[str]): List of regional locations
            - hierarchicalNamespace (Dict[str, bool]): Hierarchical namespace config
                - enabled (bool): Whether hierarchical namespace is enabled
            - iamConfiguration (Dict[str, Any]): IAM configuration
                - uniformBucketLevelAccess (Dict[str, Any]): Uniform bucket-level access config
                    - enabled (bool): Whether enabled
                    - lockedTime (str): When it was locked (RFC 3339 format)
                - bucketPolicyOnly (Dict[str, Any]): Legacy bucket policy only config
                    - enabled (bool): Whether enabled
                    - lockedTime (str): When it was locked (RFC 3339 format)
                - publicAccessPrevention (str): Public access prevention ("inherited" or "enforced")
            - ipFilter (Dict[str, Any]): IP filter configuration
                - mode (str): Filter mode ("Enabled" or "Disabled")
                - publicNetworkSource (Dict[str, List[str]]): Public network sources
                    - allowedIpCidrRanges (List[str]): List of allowed IP CIDR ranges
                - vpcNetworkSources (List[Dict[str, Any]]): VPC network sources
                    - network (str): VPC network resource name
                    - allowedIpCidrRanges (List[str]): List of allowed IP CIDR ranges
            - lifecycle (Dict[str, List[Dict[str, Any]]]): Lifecycle management rules
                - rule (List[Dict[str, Any]]): List of lifecycle rules
                    - action (Dict[str, str]): Action to take
                        - type (str): Action type (Delete, SetStorageClass, AbortIncompleteMultipartUpload)
                        - storageClass (str): Target storage class for SetStorageClass action
                    - condition (Dict[str, Any]): Conditions for applying the rule
                        - age (int): Age of object in days
                        - createdBefore (str): Date in RFC 3339 format
                        - customTimeBefore (str): Date in RFC 3339 format
                        - daysSinceCustomTime (int): Days since custom time
                        - daysSinceNoncurrentTime (int): Days since noncurrent time
                        - isLive (bool): Whether object is live
                        - matchesPattern (str): Regular expression pattern
                        - matchesPrefix (List[str]): Object name prefixes
                        - matchesSuffix (List[str]): Object name suffixes
                        - matchesStorageClass (List[str]): Storage classes to match
                        - noncurrentTimeBefore (str): Date in RFC 3339 format
                        - numNewerVersions (int): Number of newer versions
            - autoclass (Dict[str, Any]): Autoclass configuration
                - enabled (bool): Whether autoclass is enabled
                - toggleTime (str): Time autoclass was toggled (RFC 3339 format)
                - terminalStorageClass (str): Terminal storage class (NEARLINE or ARCHIVE)
                - terminalStorageClassUpdateTime (str): Time terminal class was updated (RFC 3339)
            - versioning (Dict[str, bool]): Versioning configuration
                - enabled (bool): Whether versioning is enabled
            - website (Dict[str, str]): Website configuration
                - mainPageSuffix (str): Main page suffix (e.g., "index.html")
                - notFoundPage (str): 404 page (e.g., "404.html")
            - logging (Dict[str, str]): Access logging configuration
                - logBucket (str): Destination bucket for logs
                - logObjectPrefix (str): Prefix for log objects
            - retentionPolicy (Dict[str, Any]): Retention policy
                - effectiveTime (str): When policy became effective (RFC 3339 format)
                - isLocked (bool): Whether policy is locked
                - retentionPeriod (str): Retention period in seconds
            - objectRetention (Dict[str, str]): Object retention configuration
                - mode (str): Object retention mode
            - softDeletePolicy (Dict[str, str]): Soft delete policy
                - retentionDurationSeconds (str): Retention duration in seconds
                - effectiveTime (str): When policy became effective (RFC 3339 format)
            - encryption (Dict[str, str]): Encryption configuration
                - defaultKmsKeyName (str): Default KMS key resource name
            - owner (Dict[str, str]): Bucket owner information
                - entity (str): Owner entity
                - entityId (str): Owner entity ID
            - labels (Dict[str, str]): User-defined labels (key-value pairs)
            - defaultEventBasedHold (bool): Default event-based hold for new objects
            - rpo (str): Recovery Point Objective ("DEFAULT" or "ASYNC_TURBO")
            - locationType (str): Type of location (e.g., "region", "dual-region")
            - projectNumber (str): Project number bucket belongs to
            - satisfiesPZS (bool): Whether bucket satisfies Zone Separation
            - satisfiesPZI (bool): Whether bucket satisfies Zone Isolation
            Defaults to None but REQUIRED for update operation.

    Returns:
        Tuple[Dict[str, Any], int]: A tuple containing:
            - Dictionary with complete bucket metadata (filtered by projection if specified):
                - name (str): Bucket name (preserved from original)
                - id (str): Bucket ID (preserved from original)
                - kind (str): Resource kind (always "storage#bucket")
                - storageClass (str): Storage class from bucket_request
                - location (str): Location from bucket_request
                - metageneration (str): Incremented metageneration
                - generation (str): Bucket generation (preserved from original)
                - timeCreated (str): Original creation time (preserved)
                - updated (str): Current update time (RFC 3339 format)
                - etag (str): Updated entity tag
                - projectNumber (str): Project number (preserved from original)
                - project (str): Project ID (preserved from original)
                - acl (List[Dict[str, Any]]): Access control list (omitted if projection="noAcl")
                - defaultObjectAcl (List[Dict[str, Any]]): Default object ACL (omitted if projection="noAcl")
                - billing (Dict[str, bool]): Billing configuration from bucket_request
                - cors (List[Dict[str, Any]]): CORS configuration from bucket_request
                - versioning (Dict[str, bool]): Versioning configuration from bucket_request
                - lifecycle (Dict[str, List[Dict[str, Any]]]): Lifecycle config from bucket_request
                - [All other fields as specified in bucket_request]
            - HTTP status code (200 for success, 400/404/412 for errors)

    Raises:
        TypeError: If bucket is not a string, or if optional string parameters are not strings.
        ValueError: If predefinedAcl, predefined_default_object_acl, or projection have invalid values.
        ValidationError: If bucket_request contains invalid data according to BucketRequest model.
        AttributeError: If bucket_request is None (required for update operation).
    """
    # Input validation
    if not isinstance(bucket, str):
        return {"error": "Bucket name must be a string"}, 400
    
    if if_metageneration_match is not None and not isinstance(if_metageneration_match, str):
        return {"error": "if_metageneration_match must be a string or None"}, 400
        
    if if_metageneration_not_match is not None and not isinstance(if_metageneration_not_match, str):
        return {"error": "if_metageneration_not_match must be a string or None"}, 400

    # Validate predefinedAcl using enum if available
    if predefinedAcl is not None:
        if PredefinedBucketAcl:
            valid_acls = [acl.value for acl in PredefinedBucketAcl]
        else:
            valid_acls = ["authenticatedRead", "private", "projectPrivate", "publicRead", "publicReadWrite"]
        
        if predefinedAcl not in valid_acls:
            return {"error": f"Invalid predefinedAcl. Must be one of: {valid_acls}"}, 400

    # Validate predefined_default_object_acl using enum if available
    if predefined_default_object_acl is not None:
        if PredefinedDefaultObjectAcl:
            valid_default_acls = [acl.value for acl in PredefinedDefaultObjectAcl]
        else:
            valid_default_acls = ["authenticatedRead", "bucketOwnerFullControl", "bucketOwnerRead", 
                                 "private", "projectPrivate", "publicRead"]
        
        if predefined_default_object_acl not in valid_default_acls:
            return {"error": f"Invalid predefined_default_object_acl. Must be one of: {valid_default_acls}"}, 400

    # Validate projection using enum if available
    if projection is not None:
        if BucketProjection:
            valid_projections = [proj.value for proj in BucketProjection]
        else:
            valid_projections = ["full", "noAcl"]
            
        if projection not in valid_projections:
            return {"error": f"Invalid projection. Must be one of: {valid_projections}"}, 400

    # Check if bucket exists
    if bucket not in DB.get("buckets", {}):
        return {"error": f"Bucket {bucket} not found"}, 404

    bucket_data = DB["buckets"][bucket]

    # Check metageneration conditions
    current_metageneration = str(bucket_data.get("metageneration", 0))
    
    if (if_metageneration_match is not None and 
        current_metageneration != if_metageneration_match):
        return {"error": "Metageneration mismatch"}, 412

    if (if_metageneration_not_match is not None and 
        current_metageneration == if_metageneration_not_match):
        return {"error": "Metageneration mismatch"}, 412

    # For update (PUT), we need bucket_request to be provided
    if bucket_request is None:
        return {"error": "bucket_request is required for update operation"}, 400
        
    if not isinstance(bucket_request, dict):
        return {"error": "Invalid bucket_request; must be a dictionary"}, 400

    try:
        protected_fields = ['id', 'kind', 'timeCreated', 'generation']
        sanitized_request = {k: v for k, v in bucket_request.items() if k not in protected_fields}
            
        if BucketRequest:
            # Validate the sanitized request using Pydantic model
            validated_bucket = BucketRequest(**sanitized_request)
            validated_data = validated_bucket.model_dump(exclude_none=False)
        else:
            # Fallback when models not available
            validated_data = sanitized_request.copy()
        
        # Preserve certain fields that should not be overridden
        preserved_fields = {
            'name': bucket_data.get('name', bucket),  # Keep original bucket name
            'id': bucket_data.get('id'),
            'kind': 'storage#bucket',
            'timeCreated': bucket_data.get('timeCreated'),
            'generation': bucket_data.get('generation'),
            'project': bucket_data.get('project'),  # Preserve project association
        }
        
        # Start with validated data and overlay preserved fields
        new_bucket_data = validated_data.copy()
        for key, value in preserved_fields.items():
            if value is not None:
                new_bucket_data[key] = value
        
        # Apply predefined ACLs if specified (they override bucket_request)
        if predefinedAcl:
            new_bucket_data["acl"] = predefinedAcl
        if predefined_default_object_acl:
            new_bucket_data["defaultObjectAcl"] = predefined_default_object_acl
            
    except ValidationError as e:
        error_details = []
        for error in e.errors():
            field = ".".join(str(x) for x in error["loc"])
            error_details.append(f"{field}: {error['msg']}")
        return {"error": f"Validation error: {'; '.join(error_details)}"}, 400
    except Exception as e:
        return {"error": f"Validation error: {str(e)}"}, 400

    # Increment metageneration (simulating change)
    new_bucket_data["metageneration"] = str(int(bucket_data.get("metageneration", 0)) + 1)
    
    # Update the updated timestamp
    new_bucket_data["updated"] = datetime.now().isoformat() + "Z"

    # Replace the bucket data completely (update semantics)
    DB["buckets"][bucket] = new_bucket_data

    # Apply projection for response
    if projection == "noAcl":
        response_data = {k: v for k, v in new_bucket_data.items() 
                        if k not in ["acl", "defaultObjectAcl"]}
    else:
        response_data = new_bucket_data.copy()

    return response_data, 200