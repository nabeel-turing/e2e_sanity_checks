from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, List
import re


class JiraAssignee(BaseModel):
    """Represents a Jira issue assignee."""
    name: str

    class Config:
        strict = True


class JiraAttachment(BaseModel):
    """Represents a Jira issue attachment metadata."""
    id: int
    filename: str
    fileSize: int
    mimeType: str
    created: str
    checksum: str
    content: str

    @field_validator("filename")
    @classmethod
    def validate_filename(cls, filename: str) -> str:
        """Validate that the filename only contains allowed characters."""
        allowed_chars_pattern = r"^[a-zA-Z0-9_.-]+$"
        if not re.match(allowed_chars_pattern, filename):
            raise ValueError(
                "Filename can only contain alphanumeric characters, "
                "underscores, hyphens, and periods."
            )
        return filename

    class Config:
        strict = True

      
class JiraIssueFields(BaseModel):
    """Represents the fields of a Jira issue."""
    project: str
    summary: str
    description: str
    issuetype: str
    priority: str
    status: str
    assignee: JiraAssignee
    attachments: Optional[List[JiraAttachment]] = []
    due_date: Optional[str] = None
    comments: Optional[List[str]] = []

    class Config:
        strict = True


class JiraIssueResponse(BaseModel):
    """Represents the response from creating a Jira issue."""
    id: str
    fields: JiraIssueFields

    class Config:
        strict = True


class JiraIssueCreationFields(BaseModel):
    """Represents the fields for creating a Jira issue."""
    project: str
    summary: str
    description: str
    issuetype: str
    priority: str
    assignee: JiraAssignee
    status: str = "Open"

    class Config:
        strict = True

      
class ProfilePayload(BaseModel):
    bio: Optional[str] = None
    joined: Optional[str] = None

class SettingsPayload(BaseModel):
    theme: Optional[str] = "light"
    notifications: Optional[bool] = True

class DraftPayload(BaseModel):
    id: str
    subject: str
    body: str
    timestamp: str

class MessagePayload(BaseModel):
    id: str
    sender: str = Field(..., alias='from')
    to: str
    subject: str
    timestamp: str

class ThreadPayload(BaseModel):
    id: str
    messageIds: List[str]

class HistoryPayload(BaseModel):
    action: str
    timestamp: str

class SendAsPayload(BaseModel):
    alias: str
    default: bool

class UserCreationPayload(BaseModel):
    """
    Pydantic model for validating the input payload for user creation.
    """
    name: str
    emailAddress: EmailStr
    displayName: str
    profile: Optional[ProfilePayload] = None
    groups: Optional[List[str]] = None
    drafts: Optional[List[DraftPayload]] = None
    messages: Optional[List[MessagePayload]] = None
    threads: Optional[List[ThreadPayload]] = None
    labels: Optional[List[str]] = None
    settings: Optional[SettingsPayload] = None
    history: Optional[List[HistoryPayload]] = None
    watch: Optional[List[str]] = None
    sendAs: Optional[List[SendAsPayload]] = None

    class Config:
        strict = True


class IssueFieldsUpdateModel(BaseModel):
    """
    Pydantic model for validating the 'fields' argument of update_issue.
    All fields are optional for an update operation.
    """
    summary: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    assignee: Optional[JiraAssignee] = None
    issuetype: Optional[str] = None
    project: Optional[str] = None
    due_date: Optional[str] = None
    comments: Optional[List[str]] = None

    class Config:
        extra = 'forbid' # Forbid any extra fields not defined in the model
        strict = True


class IssueReference(BaseModel):
    """Represents a reference to an issue in a link."""
    key: str = Field(..., min_length=1, description="The key of the issue")

    class Config:
        strict = True


class IssueLinkCreationInput(BaseModel):
    """
    Pydantic model for validating input to create_issue_link function.
    """
    type: str = Field(..., min_length=1, description="The type of issue link to create")
    inwardIssue: IssueReference = Field(..., description="The inward issue reference")
    outwardIssue: IssueReference = Field(..., description="The outward issue reference")

    class Config:
        strict = True

