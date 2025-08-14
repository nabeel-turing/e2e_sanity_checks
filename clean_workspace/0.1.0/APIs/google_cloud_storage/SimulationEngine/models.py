from __future__ import annotations

from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator

# --- Enums ---

class BucketStorageClass(str, Enum):
    """Valid storage class values for buckets."""
    STANDARD = "STANDARD"
    NEARLINE = "NEARLINE" 
    COLDLINE = "COLDLINE"
    ARCHIVE = "ARCHIVE"
    MULTI_REGIONAL = "MULTI_REGIONAL"
    REGIONAL = "REGIONAL"
    DURABLE_REDUCED_AVAILABILITY = "DURABLE_REDUCED_AVAILABILITY"

class BucketRPO(str, Enum):
    """Valid RPO (Recovery Point Objective) values."""
    DEFAULT = "DEFAULT"
    ASYNC_TURBO = "ASYNC_TURBO"

class BucketProjection(str, Enum):
    """Valid projection values for bucket responses."""
    FULL = "full"
    NO_ACL = "noAcl"

class PredefinedBucketAcl(str, Enum):
    """Valid predefined ACL values for buckets."""
    AUTHENTICATED_READ = "authenticatedRead"
    PRIVATE = "private"
    PROJECT_PRIVATE = "projectPrivate"
    PUBLIC_READ = "publicRead"
    PUBLIC_READ_WRITE = "publicReadWrite"

class PredefinedDefaultObjectAcl(str, Enum):
    """Valid predefined default object ACL values."""
    AUTHENTICATED_READ = "authenticatedRead"
    BUCKET_OWNER_FULL_CONTROL = "bucketOwnerFullControl"
    BUCKET_OWNER_READ = "bucketOwnerRead"
    PRIVATE = "private"
    PROJECT_PRIVATE = "projectPrivate"
    PUBLIC_READ = "publicRead"

class LifecycleActionType(str, Enum):
    """Valid lifecycle action types."""
    DELETE = "Delete"
    SET_STORAGE_CLASS = "SetStorageClass"
    ABORT_INCOMPLETE_MULTIPART_UPLOAD = "AbortIncompleteMultipartUpload"

class PublicAccessPrevention(str, Enum):
    """Valid public access prevention values."""
    INHERITED = "inherited"
    ENFORCED = "enforced"

class IpFilterMode(str, Enum):
    """Valid IP filter mode values."""
    ENABLED = "Enabled"
    DISABLED = "Disabled"

# --- Nested Models ---

class BucketBilling(BaseModel):
    """Bucket billing configuration."""
    requesterPays: Optional[bool] = False

    class Config:
        extra = "forbid"

class CorsConfiguration(BaseModel):
    """CORS configuration for buckets."""
    maxAgeSeconds: Optional[int] = None
    method: Optional[List[str]] = None
    origin: Optional[List[str]] = None
    responseHeader: Optional[List[str]] = None

    class Config:
        extra = "forbid"

class CustomPlacementConfig(BaseModel):
    """Custom placement configuration for dual regions."""
    dataLocations: List[str]

    class Config:
        extra = "forbid"

class HierarchicalNamespace(BaseModel):
    """Hierarchical namespace configuration."""
    enabled: Optional[bool] = False

    class Config:
        extra = "forbid"

class UniformBucketLevelAccess(BaseModel):
    """Uniform bucket level access configuration."""
    enabled: Optional[bool] = False
    lockedTime: Optional[str] = None

    class Config:
        extra = "forbid"

class BucketPolicyOnly(BaseModel):
    """Bucket policy only configuration (legacy)."""
    enabled: Optional[bool] = False
    lockedTime: Optional[str] = None

    class Config:
        extra = "forbid"

class IamConfiguration(BaseModel):
    """IAM configuration for buckets."""
    uniformBucketLevelAccess: Optional[UniformBucketLevelAccess] = None
    bucketPolicyOnly: Optional[BucketPolicyOnly] = None
    publicAccessPrevention: Optional[PublicAccessPrevention] = None

    class Config:
        extra = "forbid"

class PublicNetworkSource(BaseModel):
    """Public network source configuration for IP filtering."""
    allowedIpCidrRanges: Optional[List[str]] = None

    class Config:
        extra = "forbid"

class VpcNetworkSource(BaseModel):
    """VPC network source configuration for IP filtering."""
    network: str
    allowedIpCidrRanges: Optional[List[str]] = None

    class Config:
        extra = "forbid"

class IpFilter(BaseModel):
    """IP filter configuration."""
    mode: Optional[IpFilterMode] = None
    publicNetworkSource: Optional[PublicNetworkSource] = None
    vpcNetworkSources: Optional[List[VpcNetworkSource]] = None
    allowCrossOrgVpcs: Optional[bool] = None
    allowAllServiceAgentAccess: Optional[bool] = None

    class Config:
        extra = "forbid"

class LifecycleAction(BaseModel):
    """Lifecycle rule action."""
    type: LifecycleActionType
    storageClass: Optional[BucketStorageClass] = None

    class Config:
        extra = "forbid"
        use_enum_values = True

class LifecycleCondition(BaseModel):
    """Lifecycle rule condition."""
    age: Optional[int] = None
    createdBefore: Optional[str] = None
    customTimeBefore: Optional[str] = None
    daysSinceCustomTime: Optional[int] = None
    daysSinceNoncurrentTime: Optional[int] = None
    isLive: Optional[bool] = None
    matchesPattern: Optional[str] = None
    matchesPrefix: Optional[List[str]] = None
    matchesSuffix: Optional[List[str]] = None
    matchesStorageClass: Optional[List[BucketStorageClass]] = None
    noncurrentTimeBefore: Optional[str] = None
    numNewerVersions: Optional[int] = None

    class Config:
        extra = "forbid"
        use_enum_values = True

class LifecycleRule(BaseModel):
    """Lifecycle management rule."""
    action: LifecycleAction
    condition: LifecycleCondition

    class Config:
        extra = "forbid"

class Lifecycle(BaseModel):
    """Lifecycle configuration."""
    rule: Optional[List[LifecycleRule]] = None

    class Config:
        extra = "forbid"

class Autoclass(BaseModel):
    """Autoclass configuration."""
    enabled: Optional[bool] = False
    toggleTime: Optional[str] = None
    terminalStorageClass: Optional[BucketStorageClass] = None
    terminalStorageClassUpdateTime: Optional[str] = None

    class Config:
        extra = "forbid"
        use_enum_values = True

class Versioning(BaseModel):
    """Versioning configuration."""
    enabled: Optional[bool] = False

    class Config:
        extra = "forbid"

class Website(BaseModel):
    """Website configuration."""
    mainPageSuffix: Optional[str] = None
    notFoundPage: Optional[str] = None

    class Config:
        extra = "forbid"

class Logging(BaseModel):
    """Logging configuration."""
    logBucket: Optional[str] = None
    logObjectPrefix: Optional[str] = None

    class Config:
        extra = "forbid"

class RetentionPolicy(BaseModel):
    """Retention policy configuration."""
    effectiveTime: Optional[str] = None
    isLocked: Optional[bool] = False
    retentionPeriod: Optional[str] = None

    class Config:
        extra = "forbid"

class ObjectRetention(BaseModel):
    """Object retention configuration."""
    mode: Optional[str] = None

    class Config:
        extra = "forbid"

class SoftDeletePolicy(BaseModel):
    """Soft delete policy configuration."""
    retentionDurationSeconds: Optional[str] = None
    effectiveTime: Optional[str] = None

    class Config:
        extra = "forbid"

class EncryptionConfiguration(BaseModel):
    """Encryption configuration."""
    defaultKmsKeyName: Optional[str] = None

    class Config:
        extra = "forbid"

class Owner(BaseModel):
    """Bucket owner information."""
    entity: Optional[str] = None
    entityId: Optional[str] = None

    class Config:
        extra = "forbid"

# --- Main Bucket Request Model ---

class BucketRequest(BaseModel):
    """
    Pydantic model for validating bucket requests in patch/update operations.
    Based on Google Cloud Storage Bucket schema.
    """
    # Core properties
    name: Optional[str] = None
    storageClass: Optional[BucketStorageClass] = None
    location: Optional[str] = None
    
    # Configuration objects
    billing: Optional[BucketBilling] = None
    cors: Optional[List[CorsConfiguration]] = None
    customPlacementConfig: Optional[CustomPlacementConfig] = None
    hierarchicalNamespace: Optional[HierarchicalNamespace] = None
    iamConfiguration: Optional[IamConfiguration] = None
    ipFilter: Optional[IpFilter] = None
    lifecycle: Optional[Lifecycle] = None
    autoclass: Optional[Autoclass] = None
    versioning: Optional[Versioning] = None
    website: Optional[Website] = None
    logging: Optional[Logging] = None
    retentionPolicy: Optional[RetentionPolicy] = None
    objectRetention: Optional[ObjectRetention] = None
    softDeletePolicy: Optional[SoftDeletePolicy] = None
    encryption: Optional[EncryptionConfiguration] = None
    owner: Optional[Owner] = None
    
    # Simple properties
    labels: Optional[Dict[str, str]] = None
    defaultEventBasedHold: Optional[bool] = None
    rpo: Optional[BucketRPO] = None
    locationType: Optional[str] = None
    projectNumber: Optional[str] = None
    satisfiesPZS: Optional[bool] = None
    satisfiesPZI: Optional[bool] = None
    
    # Internal simulation properties (not part of actual API)
    project: Optional[str] = None
    softDeleted: Optional[bool] = None
    objects: Optional[List[str]] = None
    enableObjectRetention: Optional[bool] = None

    @field_validator('location')
    @classmethod
    def validate_location(cls, v: Optional[str]) -> Optional[str]:
        """Validate location is not empty string."""
        if v is not None and len(v.strip()) == 0:
            raise ValueError("Location cannot be empty string")
        return v

    @field_validator('labels')
    @classmethod  
    def validate_labels(cls, v: Optional[Dict[str, str]]) -> Optional[Dict[str, str]]:
        """Validate label keys and values."""
        if v is not None:
            for key, value in v.items():
                if not isinstance(key, str) or not isinstance(value, str):
                    raise ValueError("All label keys and values must be strings")
                if len(key) > 63 or len(value) > 63:
                    raise ValueError("Label keys and values must be 63 characters or less")
        return v

    class Config:
        extra = "forbid"  # Reject unknown fields
        use_enum_values = True
        validate_assignment = True