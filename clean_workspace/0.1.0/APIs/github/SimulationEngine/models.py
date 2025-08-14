from typing import List, Dict, Optional, Union, Any, Literal
from datetime import datetime
from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
    FieldValidationInfo,
)


# --- Common Field Definitions ---
AuthorAssociationType = Literal[
    "COLLABORATOR",
    "CONTRIBUTOR",
    "FIRST_TIMER",
    "FIRST_TIME_CONTRIBUTOR",
    "MANNEQUIN",
    "MEMBER",
    "NONE",
    "OWNER",
]

AUTHOR_ASSOCIATION_FIELD = Field(
    ...,
    json_schema_extra={"enum": [
        "COLLABORATOR",
        "CONTRIBUTOR",
        "FIRST_TIMER",
        "FIRST_TIME_CONTRIBUTOR",
        "MANNEQUIN",
        "MEMBER",
        "NONE",
        "OWNER",
    ]}
)


# --- Configuration for Pydantic Models ---
class BaseGitHubModel(BaseModel):
    class Config:
        populate_by_name = True  # Allows using alias for fields like "+1"
        extra = "ignore"  # Ignores extra fields not defined in the model during parsing


# --- Helper Regex Patterns ---
SHA_PATTERN = r"^[a-f0-9]{40}$"
HEX_COLOR_PATTERN = r"^[a-fA-F0-9]{6}$"
NODE_ID_PATTERN = r"^[A-Za-z0-9+/=]+$"  # Basic Base64-like pattern


# --- Base User Models ---
class UserSimple(BaseGitHubModel):
    login: str = Field(..., description="Username of the user.")
    id: int = Field(..., description="User ID of the user.")


class CurrentUser(UserSimple):
    """Model for the currently authenticated user"""
    pass


class BaseUser(UserSimple):
    node_id: Optional[str] = Field(
        None, description="Global node ID of the user.", pattern=NODE_ID_PATTERN
    )
    type: Optional[str] = Field(
        None, description="Type of account, e.g., 'User' or 'Organization'."
    )
    site_admin: Optional[bool] = Field(
        None, description="Whether the user is a site administrator."
    )


class User(BaseUser):
    name: Optional[str] = Field(None, description="The user's full name.")
    email: Optional[str] = Field(
        None, description="The user's publicly visible email address."
    )
    company: Optional[str] = Field(None, description="The user's company.")
    location: Optional[str] = Field(None, description="The user's location.")
    bio: Optional[str] = Field(None, description="The user's biography.")
    public_repos: Optional[int] = Field(
        None, ge=0, description="The number of public repositories."
    )
    public_gists: Optional[int] = Field(
        None, ge=0, description="The number of public gists."
    )
    followers: Optional[int] = Field(None, ge=0, description="The number of followers.")
    following: Optional[int] = Field(
        None, ge=0, description="The number of users the user is following."
    )
    created_at: Optional[datetime] = Field(
        None, description="ISO 8601 timestamp for when the account was created."
    )
    updated_at: Optional[datetime] = Field(
        None, description="ISO 8601 timestamp for when the account was last updated."
    )
    score: Optional[float] = Field(
        None, description="Search score if the user is from search results."
    )


# --- Repository Models ---
class LicenseNested(BaseGitHubModel):
    key: str = Field(..., description="License key (e.g., 'mit').")
    name: str = Field(..., description="License name (e.g., 'MIT License').")
    spdx_id: str = Field(..., description="SPDX identifier for the license.")

class ForkDetails(BaseModel):
    """Details about the fork lineage."""
    parent_id: int = Field(..., description="The ID of the direct parent repository.")
    parent_full_name: str = Field(..., description="The full name of the direct parent repository.")
    source_id: int = Field(..., description="The ID of the ultimate source repository in the fork network.")
    source_full_name: str = Field(..., description="The full name of the ultimate source repository.")

class Repository(BaseGitHubModel):
    id: int = Field(..., description="Unique identifier for the repository.")
    node_id: str = Field(
        ...,
        description="A global identifier for the repository.",
        pattern=NODE_ID_PATTERN,
    )
    name: str = Field(..., description="The name of the repository.")
    full_name: str = Field(
        ..., description="The full name of the repository (owner/name)."
    )
    private: bool = Field(
        ..., description="Indicates whether the repository is private."
    )
    owner: BaseUser  # The user or organization that owns the repository.
    description: Optional[str] = Field(
        None, description="A description of the repository."
    )
    fork: bool = Field(..., description="Indicates whether the repository is a fork.")
    created_at: datetime = Field(
        ..., description="Timestamp for when the repository was created."
    )
    updated_at: datetime = Field(
        ..., description="Timestamp for when the repository was last updated."
    )
    pushed_at: datetime = Field(
        ..., description="Timestamp for when the repository was last pushed to."
    )
    size: int = Field(..., ge=0, description="The size of the repository in kilobytes.")
    stargazers_count: Optional[int] = Field(
        default=0, ge=0, description="Number of stargazers."
    )
    watchers_count: Optional[int] = Field(
        default=0, ge=0, description="Number of watchers."
    )
    language: Optional[str] = Field(
        None, description="The primary language of the repository."
    )
    has_issues: Optional[bool] = Field(
        default=True, description="Whether issues are enabled."
    )
    has_projects: Optional[bool] = Field(
        default=True, description="Whether projects are enabled."
    )
    has_downloads: Optional[bool] = Field(
        default=True, description="Whether downloads are enabled."
    )
    has_wiki: Optional[bool] = Field(
        default=True, description="Whether the wiki is enabled."
    )
    has_pages: Optional[bool] = Field(
        default=False, description="Whether GitHub Pages are enabled."
    )
    forks_count: Optional[int] = Field(default=0, ge=0, description="Number of forks.")
    archived: Optional[bool] = Field(
        default=False, description="Whether the repository is archived."
    )
    disabled: Optional[bool] = Field(
        default=False, description="Whether the repository is disabled."
    )
    open_issues_count: Optional[int] = Field(
        default=0, ge=0, description="Number of open issues."
    )
    license: Optional[LicenseNested] = None
    allow_forking: Optional[bool] = Field(
        default=True, description="Whether forking is allowed."
    )
    is_template: Optional[bool] = Field(
        default=False, description="Whether this repository is a template repository."
    )
    web_commit_signoff_required: Optional[bool] = Field(
        default=False, description="Whether web commit signoff is required."
    )
    topics: Optional[List[str]] = Field(default_factory=list)
    visibility: Optional[str] = Field(
        default="public", description="Visibility of the repository."
    )  # e.g., "public", "private"
    default_branch: Optional[str] = Field(
        None, description="The default branch of the repository."
    )
    forks: Optional[int] = Field(None, ge=0)
    open_issues: Optional[int] = Field(None, ge=0)
    watchers: Optional[int] = Field(None, ge=0)
    score: Optional[float] = Field(
        None, description="Search score if from search results."
    )
    fork_details: Optional[ForkDetails] = Field(
        None, description="Details about the fork lineage if the repository is a fork."
    )

    @model_validator(mode="before")
    @classmethod
    def fill_aliases_and_defaults(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if data.get("forks_count") is not None and data.get("forks") is None:
                data["forks"] = data["forks_count"]
            if (
                data.get("open_issues_count") is not None
                and data.get("open_issues") is None
            ):
                data["open_issues"] = data["open_issues_count"]
            if data.get("watchers_count") is not None and data.get("watchers") is None:
                data["watchers"] = data["watchers_count"]
            for count_field in [
                "stargazers_count",
                "watchers_count",
                "forks_count",
                "open_issues_count",
            ]:
                if (
                    data.get(count_field) is None
                    and cls.model_fields[count_field].default is not None
                ):
                    data[count_field] = cls.model_fields[count_field].default
        return data


# --- Repository Permissions Models (NEW) ---
# Suggested roles: "read", "write", "admin". You can expand this or use an Enum.
class RepositoryCollaborator(BaseGitHubModel):
    repository_id: int = Field(..., description="ID of the repository.")
    user_id: int = Field(..., description="ID of the user (collaborator).")
    permission: str = Field(
        ...,
        description="Permission level for the user in this repository (e.g., 'read', 'write', 'admin').",
    )


# --- Issue Models ---
class Label(BaseGitHubModel):
    id: int
    node_id: str = Field(..., pattern=NODE_ID_PATTERN)
    repository_id: int = Field(
        ..., description="ID of the repository this label belongs to."
    )
    name: str
    color: Optional[str] = Field(..., pattern=HEX_COLOR_PATTERN)
    description: Optional[str] = None
    default: Optional[bool] = None


class Milestone(BaseGitHubModel):
    id: int
    node_id: str = Field(..., pattern=NODE_ID_PATTERN)
    repository_id: int = Field(
        ..., description="ID of the repository this milestone belongs to."
    )
    number: int = Field(
        ..., description="The number of the milestone, unique per repository."
    )
    title: str
    description: Optional[str] = None
    creator: Optional[BaseUser] = None
    open_issues: int = Field(..., ge=0)
    closed_issues: int = Field(..., ge=0)
    state: str  # e.g., "open", "closed"
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None
    due_on: Optional[datetime] = None


class Reactions(BaseGitHubModel):
    total_count: int = Field(..., ge=0)
    plus_one: int = Field(..., alias="+1", ge=0)
    minus_one: int = Field(..., alias="-1", ge=0)
    laugh: int = Field(..., ge=0)
    hooray: int = Field(..., ge=0)
    confused: int = Field(..., ge=0)
    heart: int = Field(..., ge=0)
    rocket: int = Field(..., ge=0)
    eyes: int = Field(..., ge=0)


class Issue(BaseGitHubModel):
    id: int
    node_id: str = Field(..., pattern=NODE_ID_PATTERN)
    repository_id: int = Field(
        ..., description="ID of the repository this issue belongs to."
    )
    number: int = Field(..., description="Issue number, unique per repository.")
    title: str
    user: BaseUser  # Creator
    labels: List[Label] = Field(default_factory=list)
    state: str  # e.g., "open", "closed"
    locked: bool
    assignee: Optional[BaseUser] = None
    assignees: List[BaseUser] = Field(default_factory=list)
    milestone: Optional[Milestone] = None
    comments: int = Field(..., ge=0)
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None
    body: Optional[str] = None
    author_association: AuthorAssociationType = AUTHOR_ASSOCIATION_FIELD
    active_lock_reason: Optional[str] = None
    reactions: Optional[Reactions] = None
    score: Optional[float] = Field(
        None, description="Search score if from search results."
    )


class IssueComment(BaseGitHubModel):
    id: int
    node_id: str = Field(..., pattern=NODE_ID_PATTERN)
    issue_id: int = Field(..., description="ID of the issue this comment belongs to.")
    repository_id: int = Field(
        ..., description="ID of the repository this comment's issue belongs to."
    )  # Redundant if issue_id allows lookup, but explicit.
    user: UserSimple  # Commenter
    created_at: datetime
    updated_at: datetime
    author_association: AuthorAssociationType = AUTHOR_ASSOCIATION_FIELD
    body: str


# --- Pull Request Models ---
class PullRequestBranchInfo(BaseGitHubModel):
    label: str
    ref: str
    sha: str = Field(..., pattern=SHA_PATTERN)
    user: BaseUser
    repo: Repository  # This allows full repo details for head/base if needed, or could be simplified to repo_id


class PullRequest(BaseGitHubModel):
    id: int
    node_id: str = Field(..., pattern=NODE_ID_PATTERN)
    # repository_id: int # MODIFIED: Added this to link PR to its repository directly
    number: int  # PR number is unique per repository
    title: str
    user: BaseUser  # Creator of the PR
    labels: List[Label] = Field(default_factory=list)
    state: str  # e.g., "open", "closed", "merged"
    locked: bool
    assignee: Optional[BaseUser] = None
    assignees: List[BaseUser] = Field(default_factory=list)
    milestone: Optional[Milestone] = None
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None
    merged_at: Optional[datetime] = None
    body: Optional[str] = None
    author_association: AuthorAssociationType = AUTHOR_ASSOCIATION_FIELD
    draft: Optional[bool] = Field(default=False)
    merged: Optional[bool] = Field(default=False)
    mergeable: Optional[bool] = None
    rebaseable: Optional[bool] = None
    mergeable_state: Optional[str] = None  # e.g., "clean", "dirty", "unknown"
    merged_by: Optional[BaseUser] = None
    comments: Optional[int] = Field(
        None, ge=0, description="Number of issue-style comments."
    )
    review_comments: Optional[int] = Field(
        None, ge=0, description="Number of diff review comments."
    )
    commits: Optional[int] = Field(
        None, ge=0, description="Number of commits in the PR."
    )
    additions: Optional[int] = Field(None, ge=0)
    deletions: Optional[int] = Field(None, ge=0)
    changed_files: Optional[int] = Field(None, ge=0)
    head: PullRequestBranchInfo  # Describes the head branch of the PR
    base: PullRequestBranchInfo  # Describes the base branch of the PR
    # The repository ID can be inferred from head.repo.id or base.repo.id
    # but adding it explicitly can simplify queries if PRs are in a flat list.
    # For now, relying on head/base repo.

    @model_validator(mode="after")
    def check_merged_state(self) -> "PullRequest":
        if self.merged_at is not None and self.merged is False:
            self.merged = True  # Ensure merged is true if merged_at is set
        if (
            self.state == "closed"
            and self.merged_at is not None
            and self.merged is not True
        ):
            # If closed and has merged_at, it should be marked as merged
            self.merged = True
        return self


class PullRequestReviewComment(BaseGitHubModel):
    id: int
    node_id: str = Field(..., pattern=NODE_ID_PATTERN)
    pull_request_review_id: Optional[int] = Field(
        None,
        description="ID of the review this comment belongs to. Null if standalone comment.",
    )
    # base_repository_id: int # This might be redundant if pull_request_number helps locate PR which has repo link
    # pull_request_number: int
    # Instead of base_repository_id and pull_request_number, linking directly to PullRequest ID might be better
    pull_request_id: int = Field(
        ..., description="ID of the pull request this comment belongs to."
    )
    user: UserSimple
    body: str
    commit_id: str = Field(
        ..., pattern=SHA_PATTERN, description="SHA of the commit the comment is on."
    )
    path: str = Field(..., description="Relative path of the file commented on.")
    position: Optional[int] = Field(
        None,
        description="Line index in the diff to which the comment applies (if applicable).",
    )
    original_position: Optional[int] = Field(None)
    diff_hunk: Optional[str] = Field(None)
    created_at: datetime
    updated_at: datetime
    author_association: AuthorAssociationType = AUTHOR_ASSOCIATION_FIELD
    start_line: Optional[int] = None
    original_start_line: Optional[int] = None
    start_side: Optional[str] = None  # "LEFT" or "RIGHT"
    line: Optional[int] = None  # The line of the blob in the pull request diff.
    original_line: Optional[int] = None  # The line of the blob in the original diff.
    side: Optional[str] = None  # "LEFT" or "RIGHT"

class AddPullRequestReviewCommentResponse(BaseGitHubModel):
    """
    Represents the structure of the dictionary returned when a pull request review comment is added.
    """
    id: int = Field(..., description="The unique identifier for the comment.")
    pull_request_review_id: Optional[int] = Field(
        None,
        description="The ID of the review this comment is part of. Null if it's a standalone comment."
    )
    user: BaseUser = Field(
        ...,
        description="Object containing details about the commenter."
    )
    body: str = Field(..., description="The text content of the comment.")
    commit_id: str = Field(..., description="The SHA of the commit to which the comment pertains.")
    path: str = Field(..., description="The relative path of the file commented on.")
    position: Optional[int] = Field(
        None,
        description="The line index in the diff to which the comment pertains. Null if not applicable."
    )
    created_at: str = Field(..., description="The ISO 8601 timestamp for when the comment was created.")
    updated_at: str = Field(..., description="The ISO 8601 timestamp for when the comment was last updated.")


class PullRequestReview(BaseGitHubModel):
    id: int
    node_id: str = Field(..., pattern=NODE_ID_PATTERN)
    # base_repository_id: int
    # pull_request_number: int
    pull_request_id: int = Field(
        ..., description="ID of the pull request this review belongs to."
    )
    user: UserSimple
    body: Optional[str] = None
    state: str  # e.g., "APPROVED", "CHANGES_REQUESTED", "COMMENTED", "DISMISSED"
    commit_id: str = Field(
        ..., pattern=SHA_PATTERN, description="SHA of the commit the review is on."
    )
    submitted_at: Optional[datetime] = None
    author_association: AuthorAssociationType = AUTHOR_ASSOCIATION_FIELD


class PullRequestFile(BaseGitHubModel):
    sha: str = Field(..., description="Blob SHA of the file", pattern=SHA_PATTERN)
    filename: str
    status: str  # e.g., "added", "modified", "removed", "renamed"
    additions: int = Field(..., ge=0)
    deletions: int = Field(..., ge=0)
    changes: int = Field(..., ge=0)
    patch: Optional[str] = None

    @model_validator(mode="after")
    def check_changes_sum(self) -> "PullRequestFile":
        if self.additions + self.deletions != self.changes:
            raise ValueError(
                f"File changes ({self.changes}) must be the sum of additions ({self.additions}) and deletions ({self.deletions})"
            )
        return self

class PullRequestUser(BaseModel):
    """
    Represents a user associated with a pull request (e.g., creator, merger).
    """
    login: str
    id: int
    type: str

class PullRequestRepo(BaseModel):
    """
    Represents a repository associated with a pull request's base or head branch.
    """
    id: int
    name: str
    full_name: str
    private: bool

class PullRequestBranch(BaseModel):
    """
    Represents a base or head branch of a pull request.
    """
    label: str
    ref: str
    sha: str
    repo: Optional[PullRequestRepo] = None # repo for head branch can be null if fork was deleted
class PullRequestResponse(BaseModel):
    """
    Represents the detailed structure of a pull request as returned by the API.
    """
    id: int
    number: int
    state: str
    title: str
    body: Optional[str] = None
    user: PullRequestUser
    created_at: str  # ISO 8601 timestamp
    updated_at: str  # ISO 8601 timestamp
    closed_at: Optional[str] = None  # ISO 8601 timestamp
    merged_at: Optional[str] = None  # ISO 8601 timestamp
    base: PullRequestBranch
    head: PullRequestBranch
    draft: bool
    merged: bool
    mergeable: Optional[bool] = None
    mergeable_state: str
    merged_by: Optional[PullRequestUser] = None
    comments_count: int
    review_comments_count: int
    maintainer_can_modify: bool
    commits_count: int
    additions_count: int
    deletions_count: int
    changed_files_count: int
class MergePullRequestResponse(BaseModel):
    """
    A dictionary confirming the merge status.
    """
    sha: str = Field(..., description="The SHA (Secure Hash Algorithm) identifier of the merge commit.")
    merged: bool = Field(..., description="Indicates if the merge was successfully completed (True) or not (False).")
    message: str = Field(..., description="A human-readable message describing the outcome of the merge attempt (e.g., 'Pull Request successfully merged', 'Merge conflict').")
class StatusCheckDetail(BaseModel):
    """
    Details of a specific status check.
    """
    state: str  # State of the specific check (e.g., 'pending', 'success', 'failure', 'error').
    context: str  # The name or identifier of the status check service (e.g., 'ci/travis-ci', 'lint').
    description: Optional[str] = None  # A short human-readable description of the status.

class PullRequestCombinedStatus(BaseModel):
    """
    Represents the combined status of all status checks for a pull request.
    """
    state: str  # The overall status (e.g., 'pending', 'success', 'failure', 'error').
    sha: str  # The SHA of the commit for which status is reported.
    total_count: int  # The total number of status checks.
    statuses: List[StatusCheckDetail]  # A list of individual status check objects.


# This model might be better if it's not a top-level DB entry,
# but rather something returned by a function that processes PR files.
# Or, if stored, it should be clearly linked to a specific PR and repository.
class PullRequestFilesListForContext(BaseGitHubModel):
    pull_request_id: int  # Link to the PullRequest
    files: List[PullRequestFile]


# --- Commit Models ---
class GitActor(BaseGitHubModel):
    name: str
    email: str
    date: datetime


class Tree(BaseGitHubModel):
    sha: str = Field(..., pattern=SHA_PATTERN)
    # url: str # Not needed for simulation state


class CommitNested(BaseGitHubModel):
    author: GitActor
    committer: GitActor
    message: str
    tree: Tree
    comment_count: Optional[int] = Field(default=0, ge=0)
    # verification: Optional[Verification] # Not modeled for simplicity


class CommitParent(BaseGitHubModel):
    sha: str = Field(..., pattern=SHA_PATTERN)
    node_id: Optional[str] = Field(None, pattern=NODE_ID_PATTERN)
    # html_url: Optional[str] # Not needed


class CommitStats(BaseGitHubModel):
    total: int = Field(..., ge=0)
    additions: int = Field(..., ge=0)
    deletions: int = Field(..., ge=0)


class CommitFileChange(BaseGitHubModel):
    sha: str = Field(..., description="Blob SHA", pattern=SHA_PATTERN)
    filename: str
    status: str  # e.g., "added", "modified", "removed", "renamed"
    additions: int = Field(..., ge=0)
    deletions: int = Field(..., ge=0)
    changes: int = Field(..., ge=0)
    patch: Optional[str] = None
    # contents_url: Optional[str] # Not needed
    # blob_url: Optional[str] # Not needed

    @model_validator(mode="after")
    def check_file_changes_sum(self) -> "CommitFileChange":
        if self.additions + self.deletions != self.changes:
            raise ValueError(
                f"Commit file changes ({self.changes}) must be the sum of additions ({self.additions}) and deletions ({self.deletions})"
            )
        return self


class Commit(BaseGitHubModel):
    sha: str = Field(..., pattern=SHA_PATTERN)
    node_id: str = Field(..., pattern=NODE_ID_PATTERN)
    # repository_id: int # MODIFIED: Added to link commit to its repository
    commit: CommitNested
    author: Optional[BaseUser] = None  # GitHub user if linked
    committer: Optional[BaseUser] = None  # GitHub user if linked
    parents: List[CommitParent] = Field(default_factory=list)
    stats: Optional[CommitStats] = None
    files: Optional[List[CommitFileChange]] = Field(default_factory=list)
    # html_url: Optional[str] # Not needed
    # comments_url: Optional[str] # Not needed


# --- Branch Models ---
class BranchCommitInfo(BaseGitHubModel):
    sha: str = Field(..., pattern=SHA_PATTERN)
    # url: Optional[str] # Not needed for simulation state


class Branch(BaseGitHubModel):
    name: str
    commit: BranchCommitInfo
    protected: bool
    repository_id: int = Field(
        ..., description="ID of the repository this branch belongs to."
    )  # MODIFIED: Added


# This model seems to represent the *response* from a branch creation API call.
# It might be generated on-the-fly rather than stored long-term as is,
# or if stored, repo_full_name could be derived or `repository_id` could be added.
class BranchCreationObject(BaseGitHubModel):
    type: str = Field(..., description="Type of Git object, usually 'commit'")
    sha: str = Field(..., pattern=SHA_PATTERN)


class BranchCreationDetail(BaseGitHubModel):
    ref: str = Field(..., description="Full Git ref (e.g., 'refs/heads/new-branch')")
    node_id: str = Field(..., pattern=NODE_ID_PATTERN)
    object: BranchCreationObject
    # repo_full_name: Optional[str] = None # Can be derived if repository_id is known
    repository_id: Optional[int] = Field(
        None, description="ID of the repository where the branch was created."
    )


# --- File/Content Models ---
class FileContent(BaseGitHubModel):
    type: str = Field(..., pattern="^file$")  # Should always be "file"
    encoding: Optional[str] = Field(None)  # e.g., "base64"
    size: int = Field(..., ge=0)
    name: str
    path: str
    content: Optional[str] = Field(None)  # Base64 encoded content for simulation
    sha: str = Field(..., description="Git blob SHA of the file.", pattern=SHA_PATTERN)
    # Other URLs (html_url, git_url, download_url) and _links not needed for simulation state


class DirectoryContentItem(BaseGitHubModel):
    type: str  # "file" or "dir"
    size: int = Field(..., ge=0)  # For files, size in bytes. For dirs, typically 0.
    name: str
    path: str
    sha: str = Field(..., pattern=SHA_PATTERN)  # Blob SHA for files, Tree SHA for dirs
    # Other URLs and _links not needed

    @field_validator("type")
    @classmethod
    def check_type_value(cls, v: str, info: FieldValidationInfo) -> str:
        if v not in ("file", "dir"):
            raise ValueError("Type must be 'file' or 'dir'")
        return v


# --- Code Scanning Models ---
class CodeScanningRule(BaseGitHubModel):
    id: str  # e.g., "js/unsafe-external-link"
    severity: Optional[str] = None  # e.g., "error", "warning", "note"
    description: str
    name: Optional[str] = Field(None)
    full_description: Optional[str] = Field(None)
    tags: Optional[List[str]] = Field(default_factory=list)
    # help_uri: Optional[str] # Not modeled


class CodeScanningTool(BaseGitHubModel):
    name: str
    version: Optional[str] = None
    guid: Optional[str] = Field(None)


class CodeScanningLocation(BaseGitHubModel):
    path: str
    start_line: int = Field(..., gt=0)
    end_line: int = Field(..., gt=0)
    start_column: Optional[int] = Field(None, gt=0)
    end_column: Optional[int] = Field(None, gt=0)

    @field_validator("end_line")
    @classmethod
    def check_end_line(cls, v: int, info: FieldValidationInfo) -> int:
        start_line = info.data.get("start_line")
        if start_line is not None and v < start_line:
            raise ValueError("end_line must be greater than or equal to start_line")
        return v

    @field_validator("end_column")
    @classmethod
    def check_end_column(
        cls, v: Optional[int], info: FieldValidationInfo
    ) -> Optional[int]:
        if v is not None:
            start_column = info.data.get("start_column")
            start_line = info.data.get("start_line")
            current_end_line = info.data.get("end_line")
            if (
                start_column is not None
                and start_line is not None
                and current_end_line is not None
            ):
                if start_line == current_end_line and v < start_column:
                    raise ValueError(
                        "end_column must be >= start_column for single-line locations"
                    )
        return v


class CodeScanningMessage(BaseGitHubModel):
    text: str


class CodeScanningInstance(BaseGitHubModel):
    ref: str  # e.g., "refs/heads/main"
    analysis_key: str
    category: Optional[str] = None
    state: str  # e.g., "open", "fixed"
    location: CodeScanningLocation
    message: CodeScanningMessage
    classifications: Optional[List[str]] = Field(default_factory=list)
    environment: Optional[str] = Field(None)
    commit_sha: Optional[str] = Field(None, pattern=SHA_PATTERN)


class CodeScanningAlert(BaseGitHubModel):
    number: int  # Alert number, unique per repository
    repository_id: int = Field(
        ..., description="ID of the repository this alert belongs to."
    )
    created_at: datetime
    updated_at: Optional[datetime] = None
    # url: str # Not needed
    # html_url: str # Not needed
    state: str  # e.g., "open", "dismissed", "fixed"
    dismissed_by: Optional[UserSimple] = None
    dismissed_at: Optional[datetime] = None
    dismissed_reason: Optional[str] = (
        None  # e.g., "false positive", "won't fix", "used in tests"
    )
    rule: CodeScanningRule
    tool: CodeScanningTool
    most_recent_instance: CodeScanningInstance


# --- Secret Scanning Models ---
class SecretScanningAlert(BaseGitHubModel):
    number: int  # Alert number, unique per repository
    repository_id: int = Field(
        ..., description="ID of the repository this alert belongs to."
    )
    created_at: datetime
    # url: str # Not needed
    # html_url: str # Not needed
    state: str  # e.g., "open", "resolved"
    secret_type: str
    secret_type_display_name: Optional[str] = Field(None)
    secret: Optional[str] = Field(None)  # The secret string
    resolution: Optional[str] = (
        None  # e.g., "false_positive", "wont_fix", "revoked", "used_in_tests"
    )
    resolved_by: Optional[UserSimple] = None
    resolved_at: Optional[datetime] = None
    resolution_comment: Optional[str] = None
    # push_protection_bypassed: Optional[bool] # Might be advanced
    # push_protection_bypassed_by: Optional[UserSimple]
    # push_protection_bypassed_at: Optional[datetime]


# --- Code Search Result Models ---
class CodeSearchResultRepository(BaseGitHubModel):  # Used within CodeSearchResultItem
    id: int
    name: str
    full_name: str
    owner: UserSimple
    # private: bool # Often included in search results for context
    # html_url: str # Not needed


class CodeSearchResultItem(BaseGitHubModel):  # Represents one item in search results
    name: str
    path: str
    sha: str = Field(..., pattern=SHA_PATTERN)
    repository: CodeSearchResultRepository
    score: float
    # Other fields like git_url, html_url, text_matches not modeled for DB state simplicity


# --- New Models for Commit Statuses/Checks ---
class CommitStatusItem(BaseGitHubModel):  # Individual status check
    context: str = Field(
        ..., description="The name or identifier of the status check service."
    )
    state: str = Field(
        ...,
        description="State of the specific check (e.g., 'pending', 'success', 'failure', 'error').",
    )
    description: Optional[str] = Field(
        None, description="A short human-readable description of the status."
    )
    # target_url: Optional[str] = Field(None) # Not modeled
    created_at: Optional[datetime] = Field(
        None, description="Timestamp for when this status was created."
    )
    updated_at: Optional[datetime] = Field(
        None, description="Timestamp for when this status was last updated."
    )
    # creator: Optional[UserSimple] # Optional creator of the status


class CombinedStatus(BaseGitHubModel):  # Overall status for a commit
    sha: str = Field(
        ...,
        pattern=SHA_PATTERN,
        description="The SHA of the commit for which status is reported.",
    )
    repository_id: int = Field(
        ..., description="ID of the repository this commit status belongs to."
    )
    state: str = Field(
        ...,
        description="The overall status (e.g., 'pending', 'success', 'failure', 'error').",
    )
    total_count: int = Field(
        ..., ge=0, description="The total number of status checks."
    )
    statuses: List[CommitStatusItem] = Field(
        default_factory=list, description="A list of individual status check objects."
    )
    # commit_url: Optional[str] # Not needed
    # repository: Optional[Repository] # Could be redundant if repo_id is present


# --- Main DB Model ---
class GitHubDB(BaseGitHubModel):
    DB_Schema_Version: str
    Generated_At: datetime

    LoggedInUser: CurrentUser = Field(..., alias="CurrentUser", description="The currently authenticated user")
    Users: List[User] = Field(default_factory=list)
    Repositories: List[Repository] = Field(default_factory=list)
    RepositoryCollaborators: List[RepositoryCollaborator] = Field(  # NEW
        default_factory=list, description="Stores user permissions for repositories."
    )

    RepositoryLabels: List[Label] = Field(
        default_factory=list,
        description="All defined labels across all accessible repositories.",
    )  # Or consider nesting labels within Repository model if strictly per-repo and not shared
    Milestones: List[Milestone] = Field(
        default_factory=list,
        description="All defined milestones across all accessible repositories.",
    )

    Issues: List[Issue] = Field(default_factory=list)
    IssueComments: List[IssueComment] = Field(default_factory=list)

    PullRequests: List[PullRequest] = Field(default_factory=list)
    PullRequestReviewComments: List[PullRequestReviewComment] = Field(
        default_factory=list
    )
    PullRequestReviews: List[PullRequestReview] = Field(default_factory=list)

    Commits: List[Commit] = Field(
        default_factory=list
    )  # Consider adding repository_id to Commit if storing flat
    Branches: List[Branch] = Field(
        default_factory=list
    )  # Branch model now has repository_id

    # Collections for specific response types or temporary data, review if they need to be long-term DB state
    BranchCreationDetailsCollection: List[BranchCreationDetail] = Field(
        default_factory=list
    )
    PullRequestFilesCollection: List[PullRequestFilesListForContext] = Field(
        default_factory=list
    )
    CodeSearchResultsCollection: List[CodeSearchResultItem] = Field(
        default_factory=list
    )  # Typically search results are not stored in the DB itself

    # Security Alerts - these need repository_id to be queryable per repo
    CodeScanningAlerts: List[CodeScanningAlert] = Field(default_factory=list)
    SecretScanningAlerts: List[SecretScanningAlert] = Field(default_factory=list)

    # Commit Statuses - needs repository_id for CombinedStatus
    CommitCombinedStatuses: List[CombinedStatus] = Field(default_factory=list)

    # FileContents: Stores content for specific paths, likely at a certain ref (commit SHA).
    # Keying strategy is crucial, e.g., "repo_id/commit_sha/path" or "repo_id/blob_sha" for blobs.
    # For simplicity, if storing path-based content for specific commits:
    # FileContents: Dict[str, Union[FileContent, List[DirectoryContentItem]]]
    # Example key: f"{repository_id}:{commit_sha}:{file_or_dir_path}"
    # Or, a more Git-like approach would be separate 'blobs' and 'trees' stores.
    # The current model supports one way of storing path-specific views.
    FileContents: Dict[str, Union[FileContent, List[DirectoryContentItem]]] = Field(
        default_factory=dict,
        description="Stores file or directory content. Key might be 'repo_id/commit_sha/path'.",
    )

    @field_validator("FileContents", mode="before")
    @classmethod
    def validate_and_parse_file_contents_structure(
        cls, v_dict_raw: Any, info: FieldValidationInfo
    ) -> Dict[str, Union[FileContent, List[DirectoryContentItem]]]:
        if not isinstance(v_dict_raw, dict):
            if v_dict_raw is None:
                return {}
            raise ValueError("FileContents must be a dictionary.")

        parsed_contents_map: Dict[
            str, Union[FileContent, List[DirectoryContentItem]]
        ] = {}
        for key, raw_value in v_dict_raw.items():
            try:
                if isinstance(raw_value, dict) and raw_value.get("type") == "file":
                    parsed_contents_map[key] = FileContent.model_validate(raw_value)
                elif isinstance(raw_value, list):
                    parsed_contents_map[key] = [
                        DirectoryContentItem.model_validate(item) for item in raw_value
                    ]
                elif isinstance(raw_value, dict) and raw_value.get("type") == "dir":
                    raise ValueError(
                        f"FileContents item '{key}' for a directory should be a list of its items, not a direct 'dir' type dictionary."
                    )
                else:
                    raise ValueError(
                        f"FileContents item '{key}' must be a dictionary with type='file' (for a file) "
                        f"or a list (for a directory's content). Found: {type(raw_value)} with value {raw_value}"
                    )
            except Exception as e:
                if isinstance(e, ValueError):
                    raise e
                raise ValueError(f"Error validating FileContents item '{key}': {e}")
        return parsed_contents_map

# New model for the GitHub user part of the commit, as it includes gravatar_id
class ListCommitsResponseGitHubUser(BaseGitHubModel):
    """
    Represents the GitHub user account that authored or committed the commit,
    as described in the list_commits function's return type.
    """
    login: str = Field(..., description="The GitHub username of the user.")
    id: int = Field(..., description="The unique GitHub ID of the user.")
    node_id: str = Field(..., description="The global node ID of the user.")
    gravatar_id: str = Field(
        ..., description="The Gravatar ID for the user."
    ) # This field is specific to the function's docstring
    type: str = Field(..., description="The type of GitHub account (e.g., 'User', 'Bot').")
    site_admin: bool = Field(
        ..., description="Indicates if the user is a site administrator on GitHub."
    )

# New model for the core commit information, as comment_count is non-optional
# and it uses the specific GitActor and Tree structures.
class ListCommitsResponseCoreCommit(BaseGitHubModel):
    """
    Represents the core commit information within a commit object returned by list_commits.
    """
    # Assuming GitActor can be imported and is suitable.
    # from .SimulationEngine.models import GitActor
    # If GitActor needs to be defined here because it's slightly different for the response:
    class _GitActor(BaseGitHubModel): # Renamed to avoid conflict if GitActor is imported
        name: str
        email: str
        date: datetime # Docstring says "str (ISO 8601 format)", Pydantic can parse to datetime

    # Assuming Tree can be imported and is suitable.
    # from .SimulationEngine.models import Tree
    # If Tree needs to be defined here:
    class _Tree(BaseGitHubModel): # Renamed to avoid conflict if Tree is imported
        sha: str

    author: _GitActor = Field(
        ...,
        description="Details of the original author of the commit."
    )
    committer: _GitActor = Field(
        ...,
        description="Details of the user who committed the changes."
    )
    message: str = Field(..., description="The commit message.")
    tree: _Tree = Field(
        ..., description="Details of the tree object associated with this commit."
    )
    comment_count: int = Field(
        ..., description="The number of comments on the commit."
    ) # Non-optional, as per docstring

# New model for parent commits, as node_id is non-optional
class ListCommitsResponseParent(BaseGitHubModel):
    """
    Represents a parent commit object as described in the list_commits function's return type.
    """
    sha: str = Field(..., description="The SHA of a parent commit.")
    node_id: str = Field(
        ..., description="The global node ID of the parent commit."
    ) # Non-optional, as per docstring

# Main model for each item in the list returned by list_commits
class ListCommitsResponseItem(BaseGitHubModel):
    """
    Represents a single commit object in the list returned by the list_commits function.
    """
    sha: str = Field(..., description="The SHA identifier of the commit.")
    node_id: str = Field(..., description="The global node ID of the commit.")
    commit: ListCommitsResponseCoreCommit = Field(
        ..., description="Core commit information."
    )
    author: Optional[ListCommitsResponseGitHubUser] = Field(
        None,
        description="The GitHub user account that authored the commit, if linked."
    )
    committer: Optional[ListCommitsResponseGitHubUser] = Field(
        None,
        description="The GitHub user account that committed the changes, if linked."
    )
    parents: List[ListCommitsResponseParent] = Field(
        ..., description="A list of parent commit objects."
    )

# --- Implementation Specific Models ---

class IssueResponseUser(BaseGitHubModel):
    """
    Represents the user structure within an issue response.
    This is a variation of the existing 'BaseUser' where fields like
    node_id, type, and site_admin are non-optional as per the function's docstring.
    """
    login: str
    id: int
    node_id: str
    type: str  # e.g., 'User', 'Bot'
    site_admin: bool


class IssueResponseLabel(BaseGitHubModel):
    """
    Represents a label associated with an issue in the response.
    This is a variation of the existing 'Label' model, notably lacking 'repository_id'
    and having 'default' as a non-optional boolean, as per the function's docstring.
    """
    id: int
    node_id: str
    name: str
    color: str  # Hex color code
    description: Optional[str] = None
    default: bool


class IssueResponseMilestone(BaseGitHubModel):
    """
    Represents a milestone associated with an issue in the response.
    This is a variation of the existing 'Milestone' model, lacking 'repository_id'
    and using string representations for timestamps, as per the function's docstring.
    """
    id: int
    node_id: str
    number: int
    title: str
    description: Optional[str] = None
    creator: IssueResponseUser  # Uses the IssueResponseUser defined above
    open_issues: int
    closed_issues: int
    state: str  # e.g., 'open', 'closed'
    created_at: str  # ISO 8601 timestamp
    updated_at: str  # ISO 8601 timestamp
    closed_at: Optional[str] = None  # ISO 8601 timestamp
    due_on: Optional[str] = None  # ISO 8601 timestamp


class ListIssuesResponseItem(BaseGitHubModel):
    """
    Represents a single issue item in the list returned by the list_issues function.
    This model details the structure of the dictionary described in the function's docstring.
    """
    id: int
    node_id: str
    number: int
    title: str
    user: IssueResponseUser
    labels: List[IssueResponseLabel]
    state: str
    locked: bool
    active_lock_reason: Optional[str] = None
    assignee: Optional[IssueResponseUser] = None
    assignees: List[IssueResponseUser]
    milestone: Optional[IssueResponseMilestone] = None
    comments: int
    created_at: str  # ISO 8601 timestamp
    updated_at: str  # ISO 8601 timestamp
    closed_at: Optional[str] = None  # ISO 8601 timestamp
    body: Optional[str] = None
    reactions: Reactions  # Use the existing Reactions model with proper field aliases
    author_association: str

# --- create_or_update_repository_file ---

# The function arguments are all simple types (str, Optional[str]),
# so no Pydantic models are generated for arguments.
# The following models are for the complex dictionary structure described in the "Returns:" section.

class CommitUserDetails(BaseModel):
    """Details of a commit author or committer."""
    name: str
    email: str
    date: str  # Timestamp in ISO 8601 format (e.g., 'YYYY-MM-DDTHH:MM:SSZ')

class FileContentDetails(BaseModel):
    """Details of a created/updated file."""
    name: str
    path: str
    sha: str # SHA (blob) of the file content
    size: int
    type: str # Typically 'file'

class CommitDetails(BaseModel):
    """Details of the commit that created/updated the file."""
    sha: str
    message: str
    author: CommitUserDetails
    committer: CommitUserDetails

class CreateOrUpdateFileResponse(BaseModel):
    """
    Represents the structure of the dictionary returned by the
    create_or_update_file function.
    """
    content: FileContentDetails
    commit: CommitDetails
# --- push_repository_files ---
class FilePushItem(BaseModel):
    """
    Represents a single file to be pushed, including its path and content.
    """
    path: str
    content: str

class PushOperationResult(BaseModel):
    """
    Details of the successful push operation, including commit information.
    """
    commit_sha: str
    tree_sha: str
    message: str

class AuthenticatedUser(BaseModel):
    """
    Represents the details of an authenticated user.
    """
    login: str = Field(..., description="The user's username.")
    id: int = Field(..., description="The unique ID of the user.")
    node_id: str = Field(..., description="The global node ID of the user.")
    name: Optional[str] = Field(None, description="The user's full name.")
    email: Optional[str] = Field(None, description="The user's publicly visible email address.")
    company: Optional[str] = Field(None, description="The user's company.")
    location: Optional[str] = Field(None, description="The user's location.")
    bio: Optional[str] = Field(None, description="The user's biography.")
    public_repos: int = Field(..., description="The number of public repositories.")
    public_gists: int = Field(..., description="The number of public gists.")
    followers: int = Field(..., description="The number of followers.")
    following: int = Field(..., description="The number of users the user is following.")
    created_at: str = Field(..., description="ISO 8601 timestamp for when the account was created.")
    updated_at: str = Field(..., description="ISO 8601 timestamp for when the account was last updated.")
    type: str = Field(..., description="The type of account, e.g., 'User' or 'Organization'.")
    

# --- Model for Pull Request Review Comment Input ---
class PullRequestReviewCommentInput(BaseModel):
    """
    Input structure for creating a new review comment as part of a pull request review.
    """
    path: str = Field(..., description="The relative path to the file being commented on.")
    body: str = Field(..., description="The text of the review comment.")
    position: Optional[int] = Field(default=None, ge=1, description="The line index in the diff to which the comment applies. Required if 'line' is not provided.")
    line: Optional[int] = Field(default=None, ge=1, description="The line of the blob in the pull request diff that the comment applies to. Required if 'position' is not provided.")
    side: Optional[Literal["LEFT", "RIGHT"]] = Field(default="RIGHT", description="In a split diff view, the side of the diff that the pull request's changes appear on.")
    start_line: Optional[int] = Field(default=None, ge=1, description="For a multi-line comment, the first line of the range that your comment applies to.")
    end_line: Optional[int] = Field(default=None, ge=1, description="For a multi-line comment, the last line of the range that your comment applies to.")
    start_side: Optional[Literal["LEFT", "RIGHT"]] = Field(default=None, description="For a multi-line comment, in a split diff view, the side of the diff for the start_line.")

    @model_validator(mode='after')
    def check_position_or_line(self) -> 'PullRequestReviewCommentInput':
        """Ensures that either 'position' or 'line' is provided."""
        if self.position is None and self.line is None:
            raise ValueError("Either 'position' or 'line' must be provided for a comment.")
        return self

    @model_validator(mode='after')
    def check_multiline_comment_fields(self) -> 'PullRequestReviewCommentInput':
        """Validates fields related to multi-line comments."""
        if self.start_line is not None:
            if self.line is None:
                raise ValueError("'line' must be provided when 'start_line' is present.")
            if self.start_line > self.line:
                raise ValueError("'start_line' must be less than or equal to 'line'.")
        return self

# --- create_repository_branch ---
class GitObject(BaseModel):
    """
    Represents a single Git object that returns from the create_repository_branch function, including its type and SHA.
    """
    type: str
    sha: str

class BranchCreationResult(BaseModel):
    """
    Details of the successful branch creation operation, including the branch reference and the Git object details.
    """
    ref: str
    node_id: str
    object: GitObject

# repositories.create_repository
class RepositoryOwner(BaseModel):
    """Details of the repository owner."""
    login: str
    id: int
    type: str

class CreateRepositoryReturn(BaseModel):
    """A dictionary containing the details of the newly created repository."""
    id: int
    node_id: str
    name: str
    full_name: str
    private: bool
    owner: RepositoryOwner
    description: Optional[str] = None
    fork: bool
    created_at: str  # ISO 8601 timestamp
    updated_at: str  # ISO 8601 timestamp
    pushed_at: Optional[str] = None  # ISO 8601 timestamp
    default_branch: Optional[str] = None


class ListBranchesResponseItem(BaseGitHubModel):
    """
    Represents a single branch object as returned by the list_branches function.
    This model captures the structure described in the function's docstring.
    """
    name: str
    commit: BranchCommitInfo
    protected: bool

class ForkedRepositoryOwner(BaseGitHubModel):
    """
    Describes the owner of the forked repository, as specified in the fork_repository function's return details.
    This model is used because the 'type' field is specified as non-optional in the docstring,
    differing from the Optional 'type' in the existing 'BaseUser' model.
    """
    login: str = Field(..., description="The login name of the owner.")
    id: int = Field(..., description="The unique identifier of the owner.")
    type: str = Field(..., description="The type of owner (e.g., 'User', 'Organization').")

class ForkedRepositoryOutput(BaseGitHubModel):
    """
    Represents the detailed structure of a newly forked repository, as returned by the fork_repository function.
    This model is defined because the function's return signature specifies a Dict[str, Any] with a
    precise set of fields that is a subset of the more general 'Repository' model,
    and includes specific constraints (e.g., owner type, fork always True).
    """
    id: int = Field(..., description="The unique identifier for the repository.")
    name: str = Field(..., description="The name of the repository.")
    full_name: str = Field(..., description="The full name of the repository, in the format 'owner_login/repository_name'.")
    owner: ForkedRepositoryOwner = Field(..., description="An object describing the owner of the forked repository.")
    private: bool = Field(..., description="True if the repository is private, false otherwise.")
    description: Optional[str] = Field(None, description="A short description of the repository.")
    fork: Literal[True] = Field(..., description="True, indicating that this repository is a fork.")

class PullRequestItemComment(PullRequestReviewComment):
    pull_request_id: Optional[int] = Field(None, description="ID of the pull request this comment belongs to.")


class AddIssueCommentResponse(BaseModel):
    """
    Represents the dictionary returned by the add_issue_comment function,
    detailing the newly created comment.
    """
    id: int
    node_id: str
    user: 'UserSimple'
    created_at: str     # ISO 8601 timestamp
    updated_at: str     # ISO 8601 timestamp
    author_association: str
    body: str
