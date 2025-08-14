from typing import Optional, List, Dict, Any, Literal, Union
from pydantic import BaseModel, Field, EmailStr, field_validator
from enum import Enum
import re


class PermissionBodyModel(BaseModel):
    """
    Pydantic model for validating the 'body' argument of the create function.
    Reflects the structure described in the function's docstring.
    """
    role: Optional[Literal['viewer', 'commenter', 'editor', 'owner', "organizer"]] = Field(
        None,
        description="The role granted by this permission."
    )
    type: Optional[Literal['user', 'group', 'domain', 'anyone']] = Field(
        None,
        description="The type of the grantee."
    )
    emailAddress: Optional[str] = Field(
        None,
        description="The email address of the user or group to grant the permission to."
    )
    domain: Optional[str] = Field(
        None,
        description="The domain name of the entity this permission refers to."
    )
    allowFileDiscovery: Optional[bool] = Field(
        None,
        description="Whether the permission allows the file to be discovered through search."
    )
    expirationTime: Optional[str] = Field(
        None,
        description="The time at which this permission will expire (e.g., RFC3339 datetime string)."
    )

    class Config:
        extra = 'allow' # Or 'ignore' or 'forbid' depending on desired behavior for extra fields. 'allow' matches original Dict[str, Any] flexibility.

        
class QuotedFileContentModel(BaseModel):
    value: str
    mimeType: str


class AuthorModel(BaseModel):
    displayName: str
    emailAddress: EmailStr
    photoLink: Optional[str] = None  # Could be pydantic.HttpUrl for stricter validation if desired


class BodyInputModel(BaseModel):
    content: str
    author: Optional[AuthorModel] = None

    class Config:
        extra = 'allow'


# Nested model for the 'restrictions' dictionary within the body
class DriveRestrictionsUpdateModel(BaseModel):
    adminManagedRestrictions: Optional[bool] = None
    copyRequiresWriterPermission: Optional[bool] = None
    domainUsersOnly: Optional[bool] = None
    driveMembersOnly: Optional[bool] = None

    # Explicitly set to forbid extra fields for Pydantic v2
    model_config = {
        "extra": "forbid"
    }

    
# Main model for the 'body' argument
class DriveUpdateBodyModel(BaseModel):
    name: Optional[str] = None
    restrictions: Optional[DriveRestrictionsUpdateModel] = None
    hidden: Optional[bool] = None
    themeId: Optional[str] = None

    # Explicitly set to forbid extra fields for Pydantic v2
    model_config = {
        "extra": "forbid"
    }


class PermissionItemModel(BaseModel):
    id: str
    role: str
    type: str
    emailAddress: Optional[str] = None

class PermissionResourceModel(BaseModel):
    """Defines the structure of a single permission resource."""
    kind: Literal['drive#permission']
    id: str
    role: Literal['viewer', 'commenter', 'editor', 'owner', 'writer', 'reader']
    type: Literal['user', 'group', 'domain', 'anyone']
    emailAddress: Optional[str] = None
    domain: Optional[str] = None
    allowFileDiscovery: Optional[bool] = None
    expirationTime: Optional[str] = None
    displayName: Optional[str] = None

class PermissionListModel(BaseModel):
    """Defines the structure for a list of permissions."""
    kind: Literal['drive#permissionList']
    permissions: List[PermissionItemModel]

class FileBodyModel(BaseModel):
    name: Optional[str] = None
    mimeType: Optional[str] = None
    parents: Optional[List[str]] = None
    size: Optional[str] = None  # Validated as string, original logic converts to int
    permissions: Optional[List[PermissionItemModel]] = None


class MediaBodyModel(BaseModel):
    size: Optional[int] = Field(None, ge=0)
    md5Checksum: Optional[str] = None
    sha1Checksum: Optional[str] = None
    sha256Checksum: Optional[str] = None
    mimeType: Optional[str] = None
    imageMediaMetadata: Optional[Dict[str, Any]] = None
    videoMediaMetadata: Optional[Dict[str, Any]] = None
    # Content upload support
    filePath: Optional[str] = Field(None, description="Path to file for content upload")

    class Config:
        extra = 'forbid'

     
class UpdateBodyModel(BaseModel):
    """
    Pydantic model for validating the 'body' parameter of the update function.
    It reflects the structure described in the function's docstring.
    """
    name: Optional[str] = None
    mimeType: Optional[str] = None
    parents: Optional[List[str]] = None
    permissions: Optional[List[Dict[str, Any]]] = None # Based on docstring: List[Dict[str, Any]]

    class Config:
        extra = 'forbid' # Forbid any fields not defined in this model

        
class FileCopyBodyModel(BaseModel):
    """
    Pydantic model for validating the 'body' parameter of the copy function.
    All fields are optional as the copy logic provides defaults or handles their absence.
    """
    name: Optional[str] = None
    parents: Optional[List[str]] = None
    permissions: Optional[List[Dict[str, Any]]] = None # Structure of permission objects can be complex, using Dict[str, Any] for now.


class PermissionBodyUpdateModel(BaseModel):
    """
    Pydantic model for validating the 'body' parameter of the update function.
    Represents the permission properties to update.
    """
    role: Optional[Literal['viewer', 'commenter', 'editor', 'writer', 'owner']] = None
    type: Optional[Literal['user', 'group', 'domain', 'anyone']] = None
    emailAddress: Optional[str] = None # Not using EmailStr to strictly follow docstring 'Optional[str]'
    domain: Optional[str] = None
    allowFileDiscovery: Optional[bool] = None
    expirationTime: Optional[str] = None # Assuming string format, could be pydantic.AwareDatetime etc. if known

    class Config:
        extra = 'ignore' # Allow extra fields in input, but they won't be part of the model

    
class RestrictionsModel(BaseModel):
    adminManagedRestrictions: bool
    copyRequiresWriterPermission: bool
    domainUsersOnly: bool
    driveMembersOnly: bool

      
class CreateDriveBodyInputModel(BaseModel):
    """Pydantic model for validating the 'body' argument of the create function."""
    name: Optional[str] = None
    restrictions: Optional[DriveRestrictionsUpdateModel] = None
    hidden: Optional[bool] = None
    themeId: Optional[str] = None

    # Explicitly set to forbid extra fields for Pydantic v2
    model_config = {
        "extra": "forbid"
    }


class UserInfo(BaseModel):
    """
    Model representing user information in comments.
    
    Attributes:
        displayName: The display name of the user.
        emailAddress: The email address of the user.
    """
    displayName: str = Field(..., min_length=1, description="Display name of the user")
    emailAddress: EmailStr = Field(..., description="Email address of the user")
    
    @field_validator('displayName')
    @classmethod
    def validate_display_name(cls, v):
        """Validate display name."""
        if not v or not v.strip():
            raise ValueError('Display name cannot be empty or only whitespace')
        return v.strip()


class QuotedFileContent(BaseModel):
    """
    Model representing quoted file content in comments.
    
    Attributes:
        value: The quoted content itself.
        mimeType: The MIME type of the quoted content.
    """
    value: str = Field(..., description="The quoted content")
    mimeType: str = Field(..., description="MIME type of the quoted content")
    
    @field_validator('value')
    @classmethod
    def validate_value(cls, v):
        """Validate quoted content value."""
        if v is None:
            raise ValueError('Quoted content value cannot be None')
        return v
    
    @field_validator('mimeType')
    @classmethod
    def validate_mime_type(cls, v):
        """Validate MIME type format."""
        if not v or not v.strip():
            raise ValueError('MIME type cannot be empty')
        # Basic MIME type validation (type/subtype)
        mime_pattern = r'^[a-zA-Z][a-zA-Z0-9][a-zA-Z0-9\-]*\/[a-zA-Z0-9][a-zA-Z0-9\-\.]*$'
        if not re.match(mime_pattern, v):
            raise ValueError('Invalid MIME type format')
        return v


class CommentCreateInput(BaseModel):
    """
    Model for creating a comment on a Google Drive file.
    
    Attributes:
        fileId: The ID of the file to comment on.
        content: The plain text content of the comment.
        author: Optional author information.
        quotedFileContent: Optional quoted file content.
        anchor: Optional anchor point for the comment.
        resolved: Optional resolution status.
    """
    fileId: str = Field(..., min_length=1, description="File ID to comment on")
    content: str = Field(..., min_length=1, description="Comment content")
    author: Optional[UserInfo] = Field(None, description="Author information")
    quotedFileContent: Optional[QuotedFileContent] = Field(None, description="Quoted file content")
    anchor: Optional[str] = Field(None, description="Anchor point for the comment")
    resolved: Optional[bool] = Field(False, description="Whether the comment is resolved")
    
    model_config = {
        "extra": "forbid"
    }
    
    @field_validator('fileId')
    @classmethod
    def validate_file_id(cls, v):
        """Validate file ID format."""
        if not v or not v.strip():
            raise ValueError('File ID cannot be empty')
        # Google Drive file IDs are typically alphanumeric with some special characters
        if not re.match(r'^[a-zA-Z0-9_-]+$', v.strip()):
            raise ValueError('Invalid file ID format')
        return v.strip()
    
    @field_validator('content')
    @classmethod
    def validate_content(cls, v):
        """Validate comment content."""
        if not v or not v.strip():
            raise ValueError('Comment content cannot be empty')
        return v.strip()
    
    @field_validator('anchor')
    @classmethod
    def validate_anchor(cls, v):
        """Validate anchor format if provided."""
        if v is not None and not isinstance(v, str):
            raise ValueError('Anchor must be a string')
        return v


class ChannelResourceModel(BaseModel):
    """
    Pydantic model for validating channel resource properties.
    Used by the Channels.stop function to validate the resource parameter.
    """
    id: Optional[str] = Field(None, description="The ID of the channel.")
    resourceId: Optional[str] = Field(None, description="The ID of the resource being watched.")
    resourceUri: Optional[str] = Field(None, description="The URI of the resource being watched.")
    token: Optional[str] = Field(None, description="The token used to authenticate the channel.")
    expiration: Optional[str] = Field(None, description="The time at which the channel will expire (RFC3339 format).")
    type: Optional[str] = Field(None, description="The type of the channel.")
    address: Optional[str] = Field(None, description="The address where notifications are delivered.")
    payload: Optional[bool] = Field(None, description="Whether to include the payload in notifications.")
    params: Optional[Dict[str, Any]] = Field(None, description="Additional parameters for the channel.")

    @field_validator('id')
    @classmethod
    def validate_id(cls, v):
        """Validate channel ID format."""
        if v is not None and not isinstance(v, str):
            raise ValueError('Channel ID must be a string')
        if v is not None and v != '' and not v.strip():
            raise ValueError('Channel ID cannot be empty or only whitespace')
        return v.strip() if v and v.strip() else v

    @field_validator('resourceUri')
    @classmethod
    def validate_resource_uri(cls, v):
        """Validate resource URI format."""
        if v is not None and not isinstance(v, str):
            raise ValueError('Resource URI must be a string')
        if v is not None and not v.strip():
            raise ValueError('Resource URI cannot be empty or only whitespace')
        return v.strip() if v else v

    @field_validator('address')
    @classmethod
    def validate_address(cls, v):
        """Validate address format."""
        if v is not None and not isinstance(v, str):
            raise ValueError('Address must be a string')
        if v is not None and not v.strip():
            raise ValueError('Address cannot be empty or only whitespace')
        return v.strip() if v else v

    @field_validator('expiration')
    @classmethod
    def validate_expiration(cls, v):
        """Validate expiration format (should be RFC3339 datetime)."""
        if v is not None and not isinstance(v, str):
            raise ValueError('Expiration must be a string')
        if v is not None and not v.strip():
            raise ValueError('Expiration cannot be empty or only whitespace')
        # Basic validation - could be enhanced with actual RFC3339 parsing
        return v.strip() if v else v

    model_config = {
        "extra": "allow"  # Allow extra fields for flexibility
    }


class DocumentElementModel(BaseModel):
    """
    Model representing a single document element with ID and text content.
    Used for Google Docs structured content.
    
    Attributes:
        elementId: Unique identifier for the document element
        text: Text content of the element
    """
    elementId: str = Field(..., description="Unique identifier for the document element")
    text: str = Field(..., description="Text content of the element")
    
    @field_validator('elementId')
    @classmethod
    def validate_element_id(cls, v):
        """Validate element ID format."""
        if not v or not v.strip():
            raise ValueError('Element ID cannot be empty')
        return v.strip()
    
    @field_validator('text')
    @classmethod
    def validate_text(cls, v):
        """Validate text content."""
        if v is None:
            return ""
        return v


class FileContentModel(BaseModel):
    """
    Model representing file content with metadata.
    
    Attributes:
        data: Encoded content data
        encoding: Content encoding (typically 'base64')
        checksum: SHA256 checksum for integrity verification
        version: Content version
        lastContentUpdate: Timestamp of last content update
    """
    data: str = Field(..., description="Encoded content data")
    encoding: str = Field(default="base64", description="Content encoding")
    checksum: str = Field(..., description="SHA256 checksum for integrity")
    version: str = Field(default="1.0", description="Content version")
    lastContentUpdate: str = Field(..., description="Timestamp of last content update")
    
    @field_validator('data', 'encoding')
    @classmethod
    def validate_data(cls, v, w):
        """Validate base64 data format only when encoding is 'base64'."""
        if w != 'base64':
            return v
        if not v or not v.strip():
            raise ValueError('Content data cannot be empty')
        # Basic base64 validation (could be enhanced)
        import base64
        try:
            # Remove padding if present for validation
            data_to_validate = v.rstrip('=')
            base64.b64decode(data_to_validate + '=' * (-len(data_to_validate) % 4))
        except Exception:
            raise ValueError('Invalid base64 data format')
        return v
    
    @field_validator('encoding')
    @classmethod
    def validate_encoding(cls, v):
        """Validate encoding format."""
        if not v or not v.strip():
            raise ValueError('Encoding cannot be empty')
        return v.strip()
    
    @field_validator('checksum', 'encoding')
    @classmethod
    def validate_checksum(cls, v, w):
        """Validate checksum format."""
        if w != 'base64':
            return v
        if not v or not v.strip():
            raise ValueError('Checksum cannot be empty')
        # Basic SHA256 format validation
        if not v.startswith('sha256:'):
            raise ValueError('Checksum must start with "sha256:"')
        if len(v) < 8:  # sha256: + at least 1 character
            raise ValueError('Invalid checksum format')
        return v
    
    @field_validator('version')
    @classmethod
    def validate_version(cls, v):
        """Validate version format."""
        if not v or not v.strip():
            raise ValueError('Version cannot be empty')
        return v.strip()
    
    @field_validator('lastContentUpdate')
    @classmethod
    def validate_last_content_update(cls, v):
        """Validate timestamp format."""
        if not v or not v.strip():
            raise ValueError('Last content update timestamp cannot be empty')
        # Basic RFC3339 validation (could be enhanced)
        import re
        rfc3339_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$'
        if not re.match(rfc3339_pattern, v.strip()):
            raise ValueError('Invalid timestamp format (expected RFC3339)')
        return v.strip()


# Union type for file content - supports both formats
FileContentUnion = Union[FileContentModel, List[DocumentElementModel]]


class RevisionContentModel(BaseModel):
    """
    Model representing revision content with minimal metadata.
    This is a simplified version of FileContentModel for revision storage.
    
    Attributes:
        data: Base64 encoded content data
        encoding: Content encoding (typically 'base64')
        checksum: SHA256 checksum for integrity verification
    """
    data: str = Field(..., description="Base64 encoded content data")
    encoding: str = Field(default="base64", description="Content encoding")
    checksum: str = Field(..., description="SHA256 checksum for integrity")
    
    @field_validator('data', 'encoding')
    @classmethod
    def validate_data(cls, v, w):
        """Validate base64 data format only when encoding is 'base64'."""
        if w != 'base64':
            return v
        if not v or not v.strip():
            raise ValueError('Content data cannot be empty')
        # Basic base64 validation (could be enhanced)
        import base64
        try:
            # Remove padding if present for validation
            data_to_validate = v.rstrip('=')
            base64.b64decode(data_to_validate + '=' * (-len(data_to_validate) % 4))
        except Exception:
            raise ValueError('Invalid base64 data format')
        return v
    
    @field_validator('encoding')
    @classmethod
    def validate_encoding(cls, v):
        """Validate encoding format."""
        if not v or not v.strip():
            raise ValueError('Encoding cannot be empty')
        return v.strip()
    
    @field_validator('checksum')
    @classmethod
    def validate_checksum(cls, v):
        """Validate checksum format."""
        if not v or not v.strip():
            raise ValueError('Checksum cannot be empty')
        # Basic SHA256 format validation
        if not v.startswith('sha256:'):
            raise ValueError('Checksum must start with "sha256:"')
        if len(v) < 8:  # sha256: + at least 1 character
            raise ValueError('Invalid checksum format')
        return v


class RevisionModel(BaseModel):
    """
    Model representing a file revision.
    
    Attributes:
        id: Unique revision identifier
        mimeType: MIME type of the revision
        modifiedTime: When the revision was created
        keepForever: Whether to keep this revision forever
        originalFilename: Original filename
        size: File size in bytes
        content: Revision content with metadata
    """
    id: str = Field(..., description="Unique revision identifier")
    mimeType: str = Field(..., description="MIME type of the revision")
    modifiedTime: str = Field(..., description="When the revision was created")
    keepForever: bool = Field(default=False, description="Whether to keep this revision forever")
    originalFilename: str = Field(..., description="Original filename")
    size: str = Field(..., description="File size in bytes")
    content: RevisionContentModel = Field(..., description="Revision content with metadata")
    
    @field_validator('id')
    @classmethod
    def validate_id(cls, v):
        """Validate revision ID format."""
        if not v or not v.strip():
            raise ValueError('Revision ID cannot be empty')
        return v.strip()
    
    @field_validator('mimeType')
    @classmethod
    def validate_mime_type(cls, v):
        """Validate MIME type format."""
        if not v or not v.strip():
            raise ValueError('MIME type cannot be empty')
        # Basic MIME type validation (type/subtype)
        mime_pattern = r'^[a-zA-Z][a-zA-Z0-9][a-zA-Z0-9\-]*\/[a-zA-Z0-9][a-zA-Z0-9\-\.]*$'
        if not re.match(mime_pattern, v.strip()):
            raise ValueError('Invalid MIME type format')
        return v.strip()
    
    @field_validator('modifiedTime')
    @classmethod
    def validate_modified_time(cls, v):
        """Validate timestamp format."""
        if not v or not v.strip():
            raise ValueError('Modified time cannot be empty')
        # Basic RFC3339 validation (could be enhanced)
        import re
        rfc3339_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$'
        if not re.match(rfc3339_pattern, v.strip()):
            raise ValueError('Invalid timestamp format (expected RFC3339)')
        return v.strip()
    
    @field_validator('originalFilename')
    @classmethod
    def validate_original_filename(cls, v):
        """Validate original filename."""
        if not v or not v.strip():
            raise ValueError('Original filename cannot be empty')
        return v.strip()
    
    @field_validator('size')
    @classmethod
    def validate_size(cls, v):
        """Validate size format."""
        if not v or not v.strip():
            raise ValueError('Size cannot be empty')
        try:
            int(v.strip())
        except ValueError:
            raise ValueError('Size must be a valid integer')
        return v.strip()


class ExportFormatsModel(BaseModel):
    """
    Model representing export formats for a file.
    
    This model accepts any MIME type as a key and validates that the value
    is a valid base64 encoded string.
    """
    
    @field_validator('*')
    @classmethod
    def validate_export_format_value(cls, v):
        """Validate that any export format value is valid base64."""
        if v is not None:
            if not v.strip():
                raise ValueError('Export format data cannot be empty if provided')
            # Basic base64 validation
            import base64
            try:
                data_to_validate = v.rstrip('=')
                base64.b64decode(data_to_validate + '=' * (-len(data_to_validate) % 4))
            except Exception:
                raise ValueError('Invalid base64 data format for export format')
        return v
    
    model_config = {
        "extra": "allow",  # Allow any MIME type keys
        "validate_assignment": True  # Validate when values are assigned
    }
    
    def __init__(self, **data):
        # Validate all values before calling parent constructor
        for key, value in data.items():
            if value is not None:
                if not value.strip():
                    raise ValueError(f'Export format data for {key} cannot be empty if provided')
                # Basic base64 validation
                import base64
                try:
                    data_to_validate = value.rstrip('=')
                    base64.b64decode(data_to_validate + '=' * (-len(data_to_validate) % 4))
                except Exception:
                    raise ValueError(f'Invalid base64 data format for export format {key}')
        super().__init__(**data)


class FileWithContentModel(BaseModel):
    """
    Extended file model that includes content, revisions, and export formats.
    This extends the basic file structure with the new content schema.
    """
    # Basic file properties (from existing models)
    id: str = Field(..., description="File ID")
    driveId: Optional[str] = Field(None, description="Drive ID")
    name: str = Field(..., description="File name")
    mimeType: str = Field(..., description="MIME type")
    createdTime: str = Field(..., description="Creation timestamp")
    modifiedTime: str = Field(..., description="Modification timestamp")
    trashed: bool = Field(default=False, description="Whether file is trashed")
    starred: bool = Field(default=False, description="Whether file is starred")
    parents: List[str] = Field(default_factory=list, description="Parent folder IDs")
    owners: List[str] = Field(..., description="File owners")
    size: str = Field(..., description="File size")
    permissions: List[Dict[str, Any]] = Field(default_factory=list, description="File permissions")
    
    # New content schema properties
    content: Optional[FileContentUnion] = Field(None, description="File content with metadata or document elements")
    revisions: List[RevisionModel] = Field(default_factory=list, description="File revisions")
    exportFormats: Optional[Dict[str, str]] = Field(None, description="Export formats")
    
    @field_validator('id')
    @classmethod
    def validate_id(cls, v):
        """Validate file ID format."""
        if not v or not v.strip():
            raise ValueError('File ID cannot be empty')
        return v.strip()
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Validate file name."""
        if not v or not v.strip():
            raise ValueError('File name cannot be empty')
        return v.strip()
    
    @field_validator('mimeType')
    @classmethod
    def validate_mime_type(cls, v):
        """Validate MIME type format."""
        if not v or not v.strip():
            raise ValueError('MIME type cannot be empty')
        # Basic MIME type validation (type/subtype)
        mime_pattern = r'^[a-zA-Z][a-zA-Z0-9][a-zA-Z0-9\-]*\/[a-zA-Z0-9][a-zA-Z0-9\-\.]*$'
        if not re.match(mime_pattern, v.strip()):
            raise ValueError('Invalid MIME type format')
        return v.strip()
    
    @field_validator('createdTime', 'modifiedTime')
    @classmethod
    def validate_timestamp(cls, v):
        """Validate timestamp format."""
        if not v or not v.strip():
            raise ValueError('Timestamp cannot be empty')
        # Basic RFC3339 validation (could be enhanced)
        import re
        rfc3339_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$'
        if not re.match(rfc3339_pattern, v.strip()):
            raise ValueError('Invalid timestamp format (expected RFC3339)')
        return v.strip()
    
    @field_validator('size')
    @classmethod
    def validate_size(cls, v):
        """Validate size format."""
        if not v or not v.strip():
            raise ValueError('Size cannot be empty')
        try:
            int(v.strip())
        except ValueError:
            raise ValueError('Size must be a valid integer')
        return v.strip()
    
    model_config = {
        "extra": "allow"  # Allow additional fields for flexibility
    }

class MaxCacheSizeModel(Enum):
    max_cache_size = 100

class AddFileContentResponseModel(BaseModel):
    file_id: str
    content_added: bool
    size: int
    checksum: str
    mime_type: str

class UpdateFileContentResponseModel(BaseModel):
    file_id: str
    content_updated: bool
    new_size: int
    new_checksum: str
    new_version: str

class CreateRevisionResponseModel(BaseModel):
    revision_id: str
    revision_created: bool
    size: int
    checksum: str

class GetFileContentResponseModel(BaseModel):
    file_id: str
    revision_id: Optional[str] = None
    content: FileContentUnion
    mime_type: str
    size: int
    modified_time: str

class ExportFileContentResponseModel(BaseModel):
    file_id: str
    exported: bool
    target_mime: str
    content: bytes
    size: int
    cached: bool

class CacheExportFormatResponseModel(BaseModel):
    file_id: str
    format_cached: bool
    format_mime: str
    cache_size: int
    content_size: int

class DeleteRevisionResponseModel(BaseModel):
    file_id: str
    revision_deleted: bool
    revision_id: str
    deleted_size: int

class ClearExportCacheResponseModel(BaseModel):
    file_id: str
    cache_cleared: bool
    cleared_formats: int

class GetExportCacheInfoResponseModel(BaseModel):
    file_id: str
    cached_formats: List[str]
    cache_size: int
    max_cache_size: int

class FileEncodeReturnModel(BaseModel):
    """
    Validation model for the return data from DriveFileProcessor.encode_file_to_base64 method.
    
    Attributes:
        data: Base64 encoded content or text content
        encoding: Content encoding ('text' or 'base64')
        mime_type: MIME type of the file
        size_bytes: File size in bytes
        checksum: SHA256 checksum for integrity verification
        filename: Original filename
        created_time: Timestamp when the file was encoded
    """
    data: str = Field(..., description="Base64 encoded content or text content")
    encoding: str = Field(..., description="Content encoding ('text' or 'base64')")
    mime_type: str = Field(..., description="MIME type of the file")
    size_bytes: int = Field(..., ge=0, description="File size in bytes")
    checksum: str = Field(..., description="SHA256 checksum for integrity verification")
    filename: str = Field(..., description="Original filename")
    created_time: str = Field(..., description="Timestamp when the file was encoded")
    
    @field_validator('data')
    @classmethod
    def validate_data(cls, v):
        """Validate that data is not empty."""
        if not v or not v.strip():
            raise ValueError('Data cannot be empty')
        return v.strip()
    
    @field_validator('encoding')
    @classmethod
    def validate_encoding(cls, v):
        """Validate encoding type."""
        valid_encodings = {'text', 'base64'}
        if v not in valid_encodings:
            raise ValueError(f'Encoding must be one of: {valid_encodings}')
        return v
    
    @field_validator('mime_type')
    @classmethod
    def validate_mime_type(cls, v):
        """Validate MIME type format."""
        if not v or not v.strip():
            raise ValueError('MIME type cannot be empty')
        # Basic MIME type validation (type/subtype)
        mime_pattern = r'^[a-zA-Z][a-zA-Z0-9][a-zA-Z0-9\-]*\/[a-zA-Z0-9][a-zA-Z0-9\-\.]*$'
        if not re.match(mime_pattern, v.strip()):
            raise ValueError('Invalid MIME type format')
        return v.strip()
    
    @field_validator('checksum')
    @classmethod
    def validate_checksum(cls, v):
        """Validate checksum format."""
        if not v or not v.strip():
            raise ValueError('Checksum cannot be empty')
        # Validate SHA256 format: sha256:hash
        if not v.startswith('sha256:'):
            raise ValueError('Checksum must start with "sha256:"')
        hash_part = v[7:]  # Remove 'sha256:' prefix
        if len(hash_part) != 64 or not all(c in '0123456789abcdef' for c in hash_part.lower()):
            raise ValueError('Invalid SHA256 hash format')
        return v
    
    @field_validator('filename')
    @classmethod
    def validate_filename(cls, v):
        """Validate filename."""
        if not v or not v.strip():
            raise ValueError('Filename cannot be empty')
        return v.strip()
    
    @field_validator('created_time')
    @classmethod
    def validate_created_time(cls, v):
        """Validate timestamp format."""
        if not v or not v.strip():
            raise ValueError('Created time cannot be empty')
        # Basic RFC3339 validation
        rfc3339_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$'
        if not re.match(rfc3339_pattern, v.strip()):
            raise ValueError('Invalid timestamp format (expected RFC3339)')
        return v.strip()


class GoogleWorkspaceDocumentModel(BaseModel):
    """
    Validation model for the return data from DriveFileProcessor.create_google_workspace_document method.
    
    Attributes:
        id: Unique file ID
        name: Document name
        mimeType: MIME type of the document
        createdTime: Creation timestamp
        modifiedTime: Modification timestamp
        size: File size (string representation)
        trashed: Whether file is trashed
        starred: Whether file is starred
        parents: List of parent folder IDs
        owners: List of file owners
        permissions: List of file permissions
    """
    id: str = Field(..., description="Unique file ID")
    name: str = Field(..., description="Document name")
    mimeType: str = Field(..., description="MIME type of the document")
    createdTime: str = Field(..., description="Creation timestamp")
    modifiedTime: str = Field(..., description="Modification timestamp")
    size: str = Field(..., description="File size (string representation)")
    trashed: bool = Field(default=False, description="Whether file is trashed")
    starred: bool = Field(default=False, description="Whether file is starred")
    parents: List[str] = Field(default_factory=list, description="List of parent folder IDs")
    owners: List[str] = Field(default_factory=list, description="List of file owners")
    permissions: List[Dict[str, Any]] = Field(default_factory=list, description="List of file permissions")
    
    @field_validator('id')
    @classmethod
    def validate_id(cls, v):
        """Validate file ID format."""
        if not v or not v.strip():
            raise ValueError('File ID cannot be empty')
        # Validate file ID format (file_1, file_2, etc.)
        if not re.match(r'^file_\d+$', v.strip()):
            raise ValueError('File ID must be in format "file_N" where N is a number')
        return v.strip()
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Validate document name."""
        if not v or not v.strip():
            raise ValueError('Document name cannot be empty')
        return v.strip()
    
    @field_validator('mimeType')
    @classmethod
    def validate_mime_type(cls, v):
        """Validate MIME type for Google Workspace documents."""
        if not v or not v.strip():
            raise ValueError('MIME type cannot be empty')
        valid_google_mime_types = {
            'application/vnd.google-apps.document',
            'application/vnd.google-apps.spreadsheet',
            'application/vnd.google-apps.presentation',
            'application/vnd.google-apps.drawing',
            'application/vnd.google-apps.form'
        }
        if v.strip() not in valid_google_mime_types:
            raise ValueError(f'MIME type must be one of: {valid_google_mime_types}')
        return v.strip()
    
    @field_validator('createdTime', 'modifiedTime')
    @classmethod
    def validate_timestamp(cls, v):
        """Validate timestamp format."""
        if not v or not v.strip():
            raise ValueError('Timestamp cannot be empty')
        # Basic RFC3339 validation
        rfc3339_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$'
        if not re.match(rfc3339_pattern, v.strip()):
            raise ValueError('Invalid timestamp format (expected RFC3339)')
        return v.strip()
    
    @field_validator('size')
    @classmethod
    def validate_size(cls, v):
        """Validate size format."""
        if not v or not v.strip():
            raise ValueError('Size cannot be empty')
        # For Google Workspace documents, size is typically "0" as string
        if v.strip() != "0":
            try:
                int(v.strip())
            except ValueError:
                raise ValueError('Size must be a valid integer or "0"')
        return v.strip()
    
    @field_validator('parents')
    @classmethod
    def validate_parents(cls, v):
        """Validate parents list."""
        if v is None:
            return []
        # Validate that all parent IDs are non-empty strings
        for parent_id in v:
            if not isinstance(parent_id, str) or not parent_id.strip():
                raise ValueError('All parent IDs must be non-empty strings')
        return v
    
    @field_validator('owners')
    @classmethod
    def validate_owners(cls, v):
        """Validate owners list."""
        if v is None:
            return []
        # Validate that all owner IDs are non-empty strings
        for owner_id in v:
            if not isinstance(owner_id, str) or not owner_id.strip():
                raise ValueError('All owner IDs must be non-empty strings')
        return v
    
    @field_validator('permissions')
    @classmethod
    def validate_permissions(cls, v):
        """Validate permissions list."""
        if v is None:
            return []
        # Validate that all permissions are dictionaries
        for permission in v:
            if not isinstance(permission, dict):
                raise ValueError('All permissions must be dictionaries')
        return v


class FileReadReturnModel(BaseModel):
    """
    Validation model for the return data from read_file function.
    
    Attributes:
        content: File content (text or base64 encoded)
        encoding: Content encoding ('text' or 'base64')
        mime_type: MIME type of the file
        size_bytes: File size in bytes
    """
    content: str = Field(..., description="File content (text or base64 encoded)")
    encoding: str = Field(..., description="Content encoding ('text' or 'base64')")
    mime_type: str = Field(..., description="MIME type of the file")
    size_bytes: int = Field(..., ge=0, description="File size in bytes")
    
    @field_validator('content')
    @classmethod
    def validate_content(cls, v):
        """Validate that content is not empty."""
        if not v or not v.strip():
            raise ValueError('Content cannot be empty')
        return v.strip()
    
    @field_validator('encoding')
    @classmethod
    def validate_encoding(cls, v):
        """Validate encoding type."""
        valid_encodings = {'text', 'base64'}
        if v not in valid_encodings:
            raise ValueError(f'Encoding must be one of: {valid_encodings}')
        return v
    
    @field_validator('mime_type')
    @classmethod
    def validate_mime_type(cls, v):
        """Validate MIME type format."""
        if not v or not v.strip():
            raise ValueError('MIME type cannot be empty')
        # Basic MIME type validation (type/subtype)
        mime_pattern = r'^[a-zA-Z][a-zA-Z0-9][a-zA-Z0-9\-]*\/[a-zA-Z0-9][a-zA-Z0-9\-\.]*$'
        if not re.match(mime_pattern, v.strip()):
            raise ValueError('Invalid MIME type format')
        return v.strip()

      
class SharedDriveForSearch(BaseModel):
    id: Optional[str] = Field(None, description="Drive ID")
    name: Optional[str] = Field(None, description="The name of the shared drive")
    hidden: Optional[bool] = Field(None, description="Whether the shared drive is hidden from default view")
    themeId: Optional[str] = Field(None, description="Theme applied to the shared drive")
    createdTime: Optional[str] = Field(None, description="ISO timestamp when the drive was created")

class PermissionModel(BaseModel):
    id: str
    role: str
    type: str
    emailAddress: Optional[str] = None

class DriveFileForSearch(BaseModel):
    name: Optional[str] = Field(None, description="The file's name")
    mimeType: Optional[str] = Field(None, description="MIME type of the file")
    trashed: Optional[bool] = Field(None, description="Whether the file is in the trash")
    starred: Optional[bool] = Field(None, description="Whether the file is starred")
    createdTime: Optional[str] = Field(None, description="ISO timestamp when file was created")
    modifiedTime: Optional[str] = Field(None, description="ISO timestamp when file was last modified")
    parents: Optional[List[str]] = Field(None, description="List of parent folder IDs")
    id: Optional[str] = Field(None, description="The file's unique ID")
    description: Optional[str] = Field(None, description="The file's description")

