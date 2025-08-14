import unittest
from unittest.mock import patch
import re
import copy
from typing import List, Dict, Any

# Assuming the utils and db are in SimulationEngine directory, relative to APIs/github/
from ..SimulationEngine.utils import create_repository_label, list_repository_labels, list_repository_collaborators
from ..SimulationEngine.db import DB
from ..SimulationEngine.custom_errors import ValidationError, NotFoundError
from ..SimulationEngine import utils
from common_utils.base_case import BaseTestCaseWithErrorHandler


class TestLabelFunctions(unittest.TestCase):

    def setUp(self):
        """Set up a clean database for each test."""
        DB.clear()
        DB.update({
            "Users": [
                {"id": 1, "login": "testuser"}
            ],
            "Repositories": [
                {
                    "id": 101,
                    "name": "test-repo",
                    "full_name": "testuser/test-repo",
                    "owner": {"id": 1, "login": "testuser"}
                }
            ],
            "RepositoryLabels": []
        })

    # --- Tests for create_repository_label ---

    def test_create_label_success(self):
        """Test successful creation of a new label with explicit color."""
        label = create_repository_label(
            repository_id=101,
            name="bug",
            color="d73a4a",
            description="Something isn't working",
            default=True
        )
        self.assertEqual(label["name"], "bug")
        self.assertEqual(label["color"], "d73a4a")
        self.assertEqual(label["repository_id"], 101)
        self.assertTrue(label["default"])
        self.assertIn(label, DB["RepositoryLabels"])

    def test_create_label_success_random_color(self):
        """Test successful creation of a new label with no color provided (random color assigned)."""
        label = create_repository_label(
            repository_id=101,
            name="random-color-label",
            description="Label with random color",
            default=False
        )
        self.assertEqual(label["name"], "random-color-label")
        self.assertEqual(label["repository_id"], 101)
        self.assertIsInstance(label["color"], str)
        self.assertEqual(len(label["color"]), 6)
        self.assertRegex(label["color"], r"^[0-9a-fA-F]{6}$")
        self.assertIn(label, DB["RepositoryLabels"])

    def test_create_label_random_color_is_unique(self):
        """Test that a randomly generated color is not used by another label in the same repository."""
        # Add a label with a known color
        create_repository_label(repository_id=101, name="existing", color="abcdef")
        # Create a label with no color (should not get 'abcdef')
        label = create_repository_label(repository_id=101, name="new-random")
        self.assertNotEqual(label["color"].lower(), "abcdef")
        # Add a bunch of labels to fill up the color space (simulate collision attempts)
        used_colors = {label["color"].lower() for label in DB["RepositoryLabels"]}
        for _ in range(10):
            new_label = create_repository_label(repository_id=101, name=f"rand-{_}")
            self.assertNotIn(new_label["color"].lower(), used_colors)
            used_colors.add(new_label["color"].lower())

    def test_create_label_repo_not_found(self):
        """Test creating a label for a non-existent repository."""
        with self.assertRaisesRegex(NotFoundError, "Repository with ID 999 not found."):
            create_repository_label(repository_id=999, name="bug", color="d73a4a")

    def test_create_label_no_repo_id(self):
        """Test creating a label without providing a repository ID."""
        with self.assertRaisesRegex(ValidationError, "Repository ID is required."):
            create_repository_label(repository_id=None, name="bug", color="d73a4a")

    def test_create_label_duplicate_name(self):
        """Test creating a label with a duplicate name in the same repository."""
        create_repository_label(repository_id=101, name="bug", color="d73a4a")
        with self.assertRaisesRegex(ValidationError, "Label with name 'bug' already exists for this repository."):
            create_repository_label(repository_id=101, name="bug", color="f29513")

    def test_create_label_duplicate_name_case_insensitive(self):
        """Test creating a label with a case-insensitive duplicate name."""
        create_repository_label(repository_id=101, name="bug", color="d73a4a")
        with self.assertRaisesRegex(ValidationError, "Label with name 'Bug' already exists for this repository."):
            create_repository_label(repository_id=101, name="Bug", color="f29513")
            
    def test_create_label_name_uniqueness_across_repos(self):
        """Test that label names can be the same across different repositories."""
        DB["Repositories"].append({
            "id": 102,
            "name": "another-repo",
            "full_name": "testuser/another-repo",
            "owner": {"id": 1, "login": "testuser"}
        })
        create_repository_label(repository_id=101, name="bug", color="d73a4a")
        try:
            label = create_repository_label(repository_id=102, name="bug", color="d73a4a")
            self.assertEqual(label['repository_id'], 102)
        except ValidationError:
            self.fail("create_repository_label raised ValidationError unexpectedly for different repos.")

    def test_create_label_invalid_name_too_long(self):
        """Test creating a label with a name that is too long."""
        long_name = "a" * 51
        with self.assertRaisesRegex(ValidationError, "Label name must be a string between 1 and 50 characters."):
            create_repository_label(repository_id=101, name=long_name, color="d73a4a")

    def test_create_label_invalid_name_empty(self):
        """Test creating a label with an empty name."""
        with self.assertRaisesRegex(ValidationError, "Label name must be a string between 1 and 50 characters."):
            create_repository_label(repository_id=101, name="", color="d73a4a")
            
    def test_create_label_invalid_color_format(self):
        """Test creating a label with an invalid color format."""
        with self.assertRaisesRegex(ValidationError, "Color must be a 6-character hexadecimal string"):
            create_repository_label(repository_id=101, name="bug", color="d73a4") # 5 chars
        with self.assertRaisesRegex(ValidationError, "Color must be a 6-character hexadecimal string"):
            create_repository_label(repository_id=101, name="bug", color="d73a4a1") # 7 chars
        with self.assertRaisesRegex(ValidationError, "Color must be a 6-character hexadecimal string"):
            create_repository_label(repository_id=101, name="bug", color="ggghhh") # invalid hex

    def test_create_label_invalid_description_too_long(self):
        """Test creating a label with a description that is too long."""
        long_desc = "d" * 101
        with self.assertRaisesRegex(ValidationError, "Description must be at most 100 characters."):
            create_repository_label(repository_id=101, name="bug", color="d73a4a", description=long_desc)

    def test_create_label_default_handling(self):
        """Test that setting a new default label unsets the old one."""
        label1 = create_repository_label(repository_id=101, name="default1", color="d73a4a", default=True)
        self.assertTrue(label1["default"])
        
        label2 = create_repository_label(repository_id=101, name="default2", color="f29513", default=True)
        self.assertTrue(label2["default"])

        # Check that the first label is no longer the default
        updated_label1 = next(l for l in DB["RepositoryLabels"] if l["id"] == label1["id"])
        self.assertFalse(updated_label1["default"])

    def test_create_label_no_default_specified(self):
        """Test that a label is not default if 'default' is not specified."""
        label = create_repository_label(repository_id=101, name="bug", color="d73a4a")
        self.assertFalse(label["default"])

    def test_create_label_no_color_and_duplicate_color_in_other_repo(self):
        """Test that random color generation does not consider colors in other repositories."""
        # Add a label with color 'aabbcc' in repo 102
        DB["Repositories"].append({
            "id": 102,
            "name": "another-repo",
            "full_name": "testuser/another-repo",
            "owner": {"id": 1, "login": "testuser"}
        })
        create_repository_label(repository_id=102, name="other", color="aabbcc")
        # Now create a label in repo 101 with no color; it can use 'aabbcc'
        label = create_repository_label(repository_id=101, name="rand-in-101")
        self.assertEqual(label["repository_id"], 101)
        self.assertEqual(len(label["color"]), 6)
        self.assertRegex(label["color"], r"^[0-9a-fA-F]{6}$")

    # --- Tests for list_repository_labels ---

    def test_list_labels_success(self):
        """Test listing labels from a repository that has them."""
        create_repository_label(repository_id=101, name="bug", color="d73a4a")
        create_repository_label(repository_id=101, name="feature", color="f29513")
        
        labels = list_repository_labels(repository_id=101)
        self.assertEqual(len(labels), 2)
        self.assertEqual({l['name'] for l in labels}, {"bug", "feature"})

    def test_list_labels_repo_not_found(self):
        """Test listing labels for a non-existent repository."""
        with self.assertRaisesRegex(NotFoundError, "Repository with ID 999 not found."):
            list_repository_labels(repository_id=999)

    def test_list_labels_no_repo_id(self):
        """Test listing labels without providing a repository ID."""
        with self.assertRaisesRegex(ValidationError, "Repository ID is required."):
            list_repository_labels(repository_id=None)

    def test_list_labels_empty_for_repo_with_no_labels(self):
        """Test listing labels for a repository that has no labels."""
        labels = list_repository_labels(repository_id=101)
        self.assertEqual(labels, [])
        
    def test_list_labels_does_not_show_labels_from_other_repos(self):
        """Test that listing labels only returns labels for the specified repository."""
        DB["Repositories"].append({
            "id": 102,
            "name": "another-repo",
            "full_name": "testuser/another-repo",
            "owner": {"id": 1, "login": "testuser"}
        })
        create_repository_label(repository_id=101, name="repo1-label", color="d73a4a")
        create_repository_label(repository_id=102, name="repo2-label", color="f29513")
        
        labels = list_repository_labels(repository_id=101)
        self.assertEqual(len(labels), 1)
        self.assertEqual(labels[0]['name'], 'repo1-label')

    def test_create_label_with_non_string_description_raises(self):
        """Test that creating a label with a non-string description raises ValidationError."""
        DB["Repositories"].append({
            "id": 101,
            "name": "test-repo",
            "full_name": "testuser/test-repo",
            "owner": {"id": 1, "login": "testuser"}
        })
        # Try with an integer description
        with self.assertRaisesRegex(ValidationError, "Description must be a string."):
            create_repository_label(repository_id=101, name="bug", color="d73a4a", description=123)
        # Try with a list description
        with self.assertRaisesRegex(ValidationError, "Description must be a string."):
            create_repository_label(repository_id=101, name="feature", color="f29513", description=["not", "a", "string"])

class TestCollaboratorFunctions(unittest.TestCase):

    def setUp(self):
        """Set up a clean database for each test."""
        DB.clear()
        DB.update({
            "Users": [
                {"id": 1, "login": "testuser"},
                {"id": 2, "login": "collaborator1"},
                {"id": 3, "login": "collaborator2"}
            ],
            "Repositories": [
                {
                    "id": 101,
                    "name": "test-repo",
                    "full_name": "testuser/test-repo",
                    "owner": {"id": 1, "login": "testuser"}
                },
                {
                    "id": 102,
                    "name": "another-repo",
                    "full_name": "testuser/another-repo",
                    "owner": {"id": 1, "login": "testuser"}
                }
            ],
            "RepositoryCollaborators": [
                {"repository_id": 101, "user_id": 2, "permission": "write"},
                {"repository_id": 101, "user_id": 3, "permission": "read"},
                {"repository_id": 102, "user_id": 2, "permission": "admin"}
            ]
        })

    def assertRepositoryDict(self, repo, expected):
        """Helper to assert the repository dict structure and values."""
        self.assertIsInstance(repo, dict)
        for key in [
            "id", "node_id", "name", "full_name", "private", "owner",
            "description", "fork", "created_at", "updated_at", "pushed_at", "default_branch"
        ]:
            self.assertIn(key, repo)
        # Check a few expected values
        for k, v in expected.items():
            self.assertEqual(repo[k], v)

    def test_list_all_collaborators_for_repo(self):
        """Test listing all collaborators for a specific repository."""
        collaborators = list_repository_collaborators(repository_id=101)
        self.assertEqual(len(collaborators), 2)
        user_ids = {c['user_id'] for c in collaborators}
        self.assertEqual(user_ids, {2, 3})
        # Check repository dict is present and correct
        for c in collaborators:
            repo = c.get("repository")
            self.assertIsInstance(repo, dict)
            self.assertEqual(repo["id"], 101)
            self.assertEqual(repo["name"], "test-repo")
            self.assertEqual(repo["full_name"], "testuser/test-repo")
            self.assertEqual(repo["owner"]["id"], 1)
            self.assertEqual(repo["owner"]["login"], "testuser")

    def test_list_collaborators_no_filters(self):
        """Test listing all collaborators when no filters are applied."""
        collaborators = list_repository_collaborators()
        self.assertEqual(len(collaborators), 3)
        for c in collaborators:
            repo = c.get("repository")
            self.assertIsInstance(repo, dict)
            self.assertIn(repo["id"], [101, 102])

    def test_filter_by_user_id(self):
        """Test filtering collaborators by user_id."""
        collaborators = list_repository_collaborators(user_id=2)
        self.assertEqual(len(collaborators), 2)
        repo_ids = {c['repository_id'] for c in collaborators}
        self.assertEqual(repo_ids, {101, 102})
        for c in collaborators:
            repo = c.get("repository")
            self.assertIsInstance(repo, dict)
            self.assertEqual(repo["id"], c["repository_id"])

    def test_filter_by_permission(self):
        """Test filtering collaborators by permission."""
        collaborators = list_repository_collaborators(permission="write")
        self.assertEqual(len(collaborators), 1)
        self.assertEqual(collaborators[0]['user_id'], 2)
        self.assertEqual(collaborators[0]['repository_id'], 101)
        repo = collaborators[0].get("repository")
        self.assertIsInstance(repo, dict)
        self.assertEqual(repo["id"], 101)
        self.assertEqual(repo["name"], "test-repo")

    def test_filter_by_repository_id_and_permission(self):
        """Test filtering collaborators by both repository_id and permission."""
        collaborators = list_repository_collaborators(repository_id=101, permission="read")
        self.assertEqual(len(collaborators), 1)
        self.assertEqual(collaborators[0]['user_id'], 3)
        repo = collaborators[0].get("repository")
        self.assertIsInstance(repo, dict)
        self.assertEqual(repo["id"], 101)

    def test_filter_by_user_id_and_repository_id(self):
        """Test filtering by user_id and repository_id."""
        collaborators = list_repository_collaborators(user_id=2, repository_id=102)
        self.assertEqual(len(collaborators), 1)
        self.assertEqual(collaborators[0]['permission'], 'admin')
        repo = collaborators[0].get("repository")
        self.assertIsInstance(repo, dict)
        self.assertEqual(repo["id"], 102)
        self.assertEqual(repo["name"], "another-repo")

    def test_filter_with_no_results(self):
        """Test a filter combination that returns no results."""
        collaborators = list_repository_collaborators(repository_id=102, permission="write")
        self.assertEqual(len(collaborators), 0)

    def test_list_collaborators_for_repo_with_none(self):
        """Test listing collaborators for a repository with no collaborators."""
        DB["Repositories"].append({
            "id": 103,
            "name": "empty-repo",
            "full_name": "testuser/empty-repo",
            "owner": {"id": 1, "login": "testuser"}
        })
        collaborators = list_repository_collaborators(repository_id=103)
        self.assertEqual(len(collaborators), 0)

class TestListPublicRepositories(unittest.TestCase):
    def setUp(self):
        """Set up a clean database for each test."""
        DB.clear()
        DB.update({
            "Users": [
                {"id": 1, "login": "alice_dev"},
                {"id": 2, "login": "bob_coder"}
            ],
            "Repositories": [
                {
                    "id": 101,
                    "node_id": "MDEwOlJlcG9zaXRvcnkxMDE=",
                    "name": "sim-engine",
                    "full_name": "alice_dev/sim-engine",
                    "private": False,
                    "owner": {"login": "alice_dev", "id": 1, "type": "User"},
                    "description": "A simulation engine for complex systems.",
                    "fork": False,
                    "created_at": "2024-01-10T09:00:00Z",
                    "updated_at": "2025-05-15T17:30:00Z",
                    "pushed_at": "2025-05-15T17:30:00Z",
                    "default_branch": "main"
                },
                {
                    "id": 102,
                    "node_id": "MDEwOlJlcG9zaXRvcnkxMDI=",
                    "name": "private-repo",
                    "full_name": "bob_coder/private-repo",
                    "private": True,
                    "owner": {"login": "bob_coder", "id": 2, "type": "User"},
                    "description": "A private repo.",
                    "fork": False,
                    "created_at": "2024-02-10T09:00:00Z",
                    "updated_at": "2025-05-15T17:30:00Z",
                    "pushed_at": "2025-05-15T17:30:00Z",
                    "default_branch": "main"
                },
                {
                    "id": 103,
                    "node_id": "MDEwOlJlcG9zaXRvcnkxMDM=",
                    "name": "public-repo-2",
                    "full_name": "bob_coder/public-repo-2",
                    "private": False,
                    "owner": {"login": "bob_coder", "id": 2, "type": "User"},
                    "description": "Another public repo.",
                    "fork": False,
                    "created_at": "2024-03-10T09:00:00Z",
                    "updated_at": "2025-05-15T17:30:00Z",
                    "pushed_at": "2025-05-15T17:30:00Z",
                    "default_branch": "main"
                }
            ]
        })

    def test_list_public_repositories_returns_only_public(self):
        """Test that only public repositories are returned."""
        from ..SimulationEngine.utils import list_public_repositories
        repos = list_public_repositories()
        self.assertEqual(len(repos), 2)
        ids = {repo["id"] for repo in repos}
        self.assertIn(101, ids)
        self.assertIn(103, ids)
        self.assertNotIn(102, ids)
        for repo in repos:
            self.assertFalse(repo["private"])

    def test_list_public_repositories_structure(self):
        """Test that returned repositories have the correct structure."""
        from ..SimulationEngine.utils import list_public_repositories
        repos = list_public_repositories()
        for repo in repos:
            for key in [
                "id", "node_id", "name", "full_name", "private", "owner",
                "description", "fork", "created_at", "updated_at", "pushed_at", "default_branch"
            ]:
                self.assertIn(key, repo)
            self.assertIsInstance(repo["owner"], dict)
            for owner_key in ["login", "id", "type"]:
                self.assertIn(owner_key, repo["owner"])

    def test_list_public_repositories_pagination(self):
        """Test pagination returns correct number of repositories per page."""
        from ..SimulationEngine.utils import list_public_repositories
        # Add more public repos for pagination
        for i in range(104, 110):
            DB["Repositories"].append({
                "id": i,
                "node_id": f"node-{i}",
                "name": f"public-repo-{i}",
                "full_name": f"user/public-repo-{i}",
                "private": False,
                "owner": {"login": "user", "id": 99, "type": "User"},
                "description": "",
                "fork": False,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "pushed_at": "2024-01-01T00:00:00Z",
                "default_branch": "main"
            })
        # There should now be 2 + 6 = 8 public repos
        repos_page_1 = list_public_repositories(page=1, per_page=3)
        repos_page_2 = list_public_repositories(page=2, per_page=3)
        repos_page_3 = list_public_repositories(page=3, per_page=3)
        self.assertEqual(len(repos_page_1), 3)
        self.assertEqual(len(repos_page_2), 3)
        self.assertEqual(len(repos_page_3), 2)  # 8 total, so last page has 2

    def test_list_public_repositories_page_out_of_range(self):
        """Test that requesting a page out of range returns an empty list."""
        from ..SimulationEngine.utils import list_public_repositories
        repos = list_public_repositories(page=100, per_page=10)
        self.assertEqual(repos, [])

    def test_list_public_repositories_invalid_page_and_per_page(self):
        """Test that invalid page/per_page values are handled gracefully."""
        from ..SimulationEngine.utils import list_public_repositories
        # Negative page/per_page should default to 1/30
        repos = list_public_repositories(page=-1, per_page=-5)
        # All public repos should be returned (since <30)
        public_count = sum(1 for r in DB["Repositories"] if not r.get("private", False))
        self.assertEqual(len(repos), public_count)


class TestUtilityFunctions(BaseTestCaseWithErrorHandler):
    """Test cases for utility functions in utils.py"""
    
    @classmethod
    def setUpClass(cls):
        cls.original_db = copy.deepcopy(DB)

    @classmethod
    def tearDownClass(cls):
        DB.clear()
        DB.update(cls.original_db)

    def setUp(self):
        self.DB = DB
        self.DB.clear()
        
        self.repo_id = 101
        self.commit_sha_1 = "abcdef1234567890abcdef1234567890abcdef12"
        self.commit_sha_2 = "fedcba0987654321fedcba0987654321fedcba09"
        
    def test_count_lines_with_regular_text(self):
        """Test _count_lines with regular text content."""
        content = "Line 1\nLine 2\nLine 3\n"
        result = utils._count_lines(content)
        self.assertEqual(result, 3)
        
    def test_count_lines_with_empty_string(self):
        """Test _count_lines with empty string."""
        content = ""
        result = utils._count_lines(content)
        self.assertEqual(result, 0)
        
    def test_count_lines_with_none(self):
        """Test _count_lines with None (binary files)."""
        content = None
        result = utils._count_lines(content)
        self.assertEqual(result, 0)
        
    def test_count_lines_with_single_line_no_newline(self):
        """Test _count_lines with single line without trailing newline."""
        content = "Single line without newline"
        result = utils._count_lines(content)
        self.assertEqual(result, 1)
        
    def test_count_lines_with_only_newlines(self):
        """Test _count_lines with only newline characters."""
        content = "\n\n\n"
        result = utils._count_lines(content)
        self.assertEqual(result, 3)
        
    def test_get_files_from_commit_with_files(self):
        """Test _get_files_from_commit when commit has files."""
        # Set up FileContents in database using correct dictionary format
        self.DB['FileContents'] = {
            f'{self.repo_id}:{self.commit_sha_1}:file1.py': {
                'type': 'file',
                'sha': 'abc123',
                'content': 'print("hello")\n',
                'path': 'file1.py',
                'name': 'file1.py',
                'size': 15
            },
            f'{self.repo_id}:{self.commit_sha_1}:file2.txt': {
                'type': 'file',
                'sha': 'def456',
                'content': 'Some text content\nLine 2\n',
                'path': 'file2.txt',
                'name': 'file2.txt',
                'size': 25
            },
            f'{self.repo_id}:{self.commit_sha_2}:other_file.py': {
                'type': 'file',
                'sha': 'ghi789',
                'content': 'print("other")\n',
                'path': 'other_file.py',
                'name': 'other_file.py',
                'size': 16
            }
        }
        
        result = utils._get_files_from_commit(self.repo_id, self.commit_sha_1)
        
        # Should return only files from the specified commit
        self.assertEqual(len(result), 2)
        self.assertIn('file1.py', result)
        self.assertIn('file2.txt', result)
        self.assertNotIn('other_file.py', result)
        
        # Check content and sha are correct
        self.assertEqual(result['file1.py']['content'], 'print("hello")\n')
        self.assertEqual(result['file1.py']['sha'], 'abc123')
        self.assertEqual(result['file2.txt']['content'], 'Some text content\nLine 2\n')
        self.assertEqual(result['file2.txt']['sha'], 'def456')
        
    def test_get_files_from_commit_no_files(self):
        """Test _get_files_from_commit when commit has no files."""
        # Set up FileContents but for different commit
        self.DB['FileContents'] = {
            f'{self.repo_id}:{self.commit_sha_2}:some_file.py': {
                'type': 'file',
                'sha': 'xyz123',
                'content': 'content',
                'path': 'some_file.py',
                'name': 'some_file.py',
                'size': 7
            }
        }
        
        result = utils._get_files_from_commit(self.repo_id, self.commit_sha_1)
        
        # Should return empty dict
        self.assertEqual(result, {})
        
    def test_get_files_from_commit_empty_database(self):
        """Test _get_files_from_commit when FileContents table is empty."""
        self.DB['FileContents'] = {}
        
        result = utils._get_files_from_commit(self.repo_id, self.commit_sha_1)
        
        # Should return empty dict
        self.assertEqual(result, {})
        
    def test_get_files_from_commit_no_filecontents_table(self):
        """Test _get_files_from_commit when FileContents table doesn't exist."""
        # Don't set FileContents in DB
        
        result = utils._get_files_from_commit(self.repo_id, self.commit_sha_1)
        
        # Should return empty dict
        self.assertEqual(result, {})
        
    def test_get_files_from_commit_with_binary_files(self):
        """Test _get_files_from_commit with binary files (content=None)."""
        self.DB['FileContents'] = {
            f'{self.repo_id}:{self.commit_sha_1}:image.png': {
                'type': 'file',
                'sha': 'binary123',
                'content': None,  # Binary file
                'path': 'image.png',
                'name': 'image.png',
                'size': 1024
            },
            f'{self.repo_id}:{self.commit_sha_1}:text.txt': {
                'type': 'file',
                'sha': 'text123',
                'content': 'Text content\n',
                'path': 'text.txt',
                'name': 'text.txt',
                'size': 13
            }
        }
        
        result = utils._get_files_from_commit(self.repo_id, self.commit_sha_1)
        
        self.assertEqual(len(result), 2)
        self.assertIsNone(result['image.png']['content'])  # Binary files have None content (real-world behavior)
        self.assertEqual(result['image.png']['sha'], 'binary123')
        self.assertEqual(result['text.txt']['content'], 'Text content\n')
        self.assertEqual(result['text.txt']['sha'], 'text123')
        
    def test_calculate_file_changes_added_files(self):
        """Test _calculate_file_changes with added files."""
        base_files = {}
        head_files = {
            'new_file.py': {'sha': 'abc123', 'content': 'def new_function():\n    return "hello"\n'},
            'another_new.txt': {'sha': 'def456', 'content': 'New content\n'}
        }
        
        result = utils._calculate_file_changes(base_files, head_files)
        
        self.assertEqual(len(result), 2)
        
        # Check first added file
        new_file = next(f for f in result if f['filename'] == 'new_file.py')
        self.assertEqual(new_file['status'], 'added')
        self.assertEqual(new_file['sha'], 'abc123')
        self.assertEqual(new_file['additions'], 2)
        self.assertEqual(new_file['deletions'], 0)
        self.assertEqual(new_file['changes'], 2)
        
        # Check second added file
        another_file = next(f for f in result if f['filename'] == 'another_new.txt')
        self.assertEqual(another_file['status'], 'added')
        self.assertEqual(another_file['sha'], 'def456')
        self.assertEqual(another_file['additions'], 1)
        self.assertEqual(another_file['deletions'], 0)
        self.assertEqual(another_file['changes'], 1)
        
    def test_calculate_file_changes_removed_files(self):
        """Test _calculate_file_changes with removed files."""
        base_files = {
            'old_file.py': {'sha': 'abc123', 'content': 'def old_function():\n    return "goodbye"\n'},
            'deprecated.txt': {'sha': 'def456', 'content': 'Old content\nLine 2\n'}
        }
        head_files = {}
        
        result = utils._calculate_file_changes(base_files, head_files)
        
        self.assertEqual(len(result), 2)
        
        # Check first removed file
        old_file = next(f for f in result if f['filename'] == 'old_file.py')
        self.assertEqual(old_file['status'], 'removed')
        self.assertEqual(old_file['sha'], 'abc123')
        self.assertEqual(old_file['additions'], 0)
        self.assertEqual(old_file['deletions'], 2)
        self.assertEqual(old_file['changes'], 2)
        
        # Check second removed file
        deprecated_file = next(f for f in result if f['filename'] == 'deprecated.txt')
        self.assertEqual(deprecated_file['status'], 'removed')
        self.assertEqual(deprecated_file['sha'], 'def456')
        self.assertEqual(deprecated_file['additions'], 0)
        self.assertEqual(deprecated_file['deletions'], 2)
        self.assertEqual(deprecated_file['changes'], 2)
        
    def test_calculate_file_changes_modified_files(self):
        """Test _calculate_file_changes with modified files."""
        base_files = {
            'modified.py': {'sha': 'abc123', 'content': 'Original content\n'},
            'expanded.txt': {'sha': 'def456', 'content': 'Line 1\n'}
        }
        head_files = {
            'modified.py': {'sha': 'abc456', 'content': 'Updated content\nWith extra line\n'},
            'expanded.txt': {'sha': 'def789', 'content': 'Line 1\nLine 2\nLine 3\n'}
        }
        
        result = utils._calculate_file_changes(base_files, head_files)
        
        self.assertEqual(len(result), 2)
        
        # Check first modified file
        modified_file = next(f for f in result if f['filename'] == 'modified.py')
        self.assertEqual(modified_file['status'], 'modified')
        self.assertEqual(modified_file['sha'], 'abc456')
        self.assertEqual(modified_file['additions'], 2)  # Both lines in head are new (different from base)
        self.assertEqual(modified_file['deletions'], 1)  # Original line was removed
        self.assertEqual(modified_file['changes'], 3)
        
        # Check second modified file
        expanded_file = next(f for f in result if f['filename'] == 'expanded.txt')
        self.assertEqual(expanded_file['status'], 'modified')
        self.assertEqual(expanded_file['sha'], 'def789')
        self.assertEqual(expanded_file['additions'], 2)  # 3 lines - 1 line = 2 additions
        self.assertEqual(expanded_file['deletions'], 0)
        self.assertEqual(expanded_file['changes'], 2)
        
    def test_calculate_file_changes_mixed_operations(self):
        """Test _calculate_file_changes with mixed add/remove/modify operations."""
        base_files = {
            'keep_same.txt': {'sha': 'same123', 'content': 'Unchanged content\n'},
            'to_modify.py': {'sha': 'old123', 'content': 'Old code\n'},
            'to_remove.md': {'sha': 'remove123', 'content': 'Will be deleted\n'}
        }
        head_files = {
            'keep_same.txt': {'sha': 'same123', 'content': 'Unchanged content\n'},  # Same SHA and content
            'to_modify.py': {'sha': 'new123', 'content': 'New code\nExtra line\n'},  # Modified
            'new_file.js': {'sha': 'add123', 'content': 'console.log("new");\n'}  # Added
            # to_remove.md is missing (removed)
        }
        
        result = utils._calculate_file_changes(base_files, head_files)
        
        # Should return 3 files: 1 modified, 1 removed, 1 added
        # keep_same.txt should not appear since it's unchanged (same SHA)
        self.assertEqual(len(result), 3)
        
        file_statuses = {f['filename']: f['status'] for f in result}
        self.assertEqual(file_statuses['to_modify.py'], 'modified')
        self.assertEqual(file_statuses['to_remove.md'], 'removed')
        self.assertEqual(file_statuses['new_file.js'], 'added')
        
    def test_calculate_file_changes_no_changes(self):
        """Test _calculate_file_changes when no files are changed."""
        files = {
            'unchanged1.txt': {'sha': 'same123', 'content': 'Same content\n'},
            'unchanged2.py': {'sha': 'same456', 'content': 'def same():\n    pass\n'}
        }
        
        result = utils._calculate_file_changes(files, files)
        
        # Should return empty list when no files changed (same SHAs)
        self.assertEqual(result, [])
        
    def test_calculate_file_changes_binary_files(self):
        """Test _calculate_file_changes with binary files."""
        base_files = {
            'image.png': {'sha': 'binary123', 'content': None},  # Binary file
            'doc.pdf': {'sha': 'binary456', 'content': None}     # Binary file
        }
        head_files = {
            'image.png': {'sha': 'binary123', 'content': None},  # Same binary file (no change)
            'doc.pdf': {'sha': 'text123', 'content': 'converted to text'},  # Binary to text
            'new_image.jpg': {'sha': 'binary789', 'content': None}  # New binary file
        }
        
        result = utils._calculate_file_changes(base_files, head_files)
        
        self.assertEqual(len(result), 2)  # doc.pdf modified, new_image.jpg added
        
        # Check converted file
        doc_file = next(f for f in result if f['filename'] == 'doc.pdf')
        self.assertEqual(doc_file['status'], 'modified')
        self.assertEqual(doc_file['sha'], 'text123')
        self.assertEqual(doc_file['additions'], 1)  # Text content has 1 line
        self.assertEqual(doc_file['deletions'], 0)  # Binary content counts as 0 lines
        
        # Check new binary file
        new_image = next(f for f in result if f['filename'] == 'new_image.jpg')
        self.assertEqual(new_image['status'], 'added')
        self.assertEqual(new_image['sha'], 'binary789')
        self.assertEqual(new_image['additions'], 0)  # Binary file
        self.assertEqual(new_image['deletions'], 0)
        
    def test_calculate_file_changes_empty_files(self):
        """Test _calculate_file_changes with empty files."""
        base_files = {
            'empty.txt': {'sha': 'empty123', 'content': ''},
            'has_content.txt': {'sha': 'content123', 'content': 'Some content\n'}
        }
        head_files = {
            'empty.txt': {'sha': 'content456', 'content': 'Now has content\n'},  # Empty to content
            'has_content.txt': {'sha': 'empty456', 'content': ''},  # Content to empty
            'new_empty.txt': {'sha': 'empty789', 'content': ''}  # New empty file
        }
        
        result = utils._calculate_file_changes(base_files, head_files)
        
        self.assertEqual(len(result), 3)
        
        file_changes = {f['filename']: f for f in result}
        
        # Empty file that gained content
        empty_file = file_changes['empty.txt']
        self.assertEqual(empty_file['status'], 'modified')
        self.assertEqual(empty_file['sha'], 'content456')
        self.assertEqual(empty_file['additions'], 1)
        self.assertEqual(empty_file['deletions'], 0)
        
        # File that became empty
        has_content = file_changes['has_content.txt']
        self.assertEqual(has_content['status'], 'modified')
        self.assertEqual(has_content['sha'], 'empty456')
        self.assertEqual(has_content['additions'], 0)
        self.assertEqual(has_content['deletions'], 1)
        
        # New empty file
        new_empty = file_changes['new_empty.txt']
        self.assertEqual(new_empty['status'], 'added')
        self.assertEqual(new_empty['sha'], 'empty789')
        self.assertEqual(new_empty['additions'], 0)
        self.assertEqual(new_empty['deletions'], 0)
    
    def test_calculate_file_changes_renamed_file(self):
        """Test _calculate_file_changes when a file is renamed."""
        base_files = {
            "old_name.txt": {"sha": "abc123", "content": "Hello World"}
        }
        head_files = {
            "new_name.txt": {"sha": "abc123", "content": "Hello World"}  # Same SHA, different path
        }
        
        result = utils._calculate_file_changes(base_files, head_files)
        
        # Should detect one rename
        self.assertEqual(len(result), 1)
        
        change = result[0]
        self.assertEqual(change["status"], "renamed")
        self.assertEqual(change["filename"], "new_name.txt")
        self.assertEqual(change["previous_filename"], "old_name.txt")
        self.assertEqual(change["sha"], "abc123")
        self.assertEqual(change["additions"], 0)
        self.assertEqual(change["deletions"], 0)
        self.assertEqual(change["changes"], 0)
        self.assertIsNone(change["patch"])


if __name__ == '__main__':
    unittest.main() 