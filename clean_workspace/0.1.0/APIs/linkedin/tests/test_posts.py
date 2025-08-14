import unittest
from common_utils.base_case import BaseTestCaseWithErrorHandler
import linkedin as LinkedinAPI
from .common import reset_db


class TestPosts(BaseTestCaseWithErrorHandler):
    def setUp(self):
        LinkedinAPI.DB.clear()
        LinkedinAPI.DB.update(
            {
                "people": {},
                "organizations": {},
                "organizationAcls": {},
                "posts": {},
                "next_person_id": 1,
                "next_org_id": 1,
                "next_acl_id": 1,
                "next_post_id": 1,
                "current_person_id": None,
            }
        )

    def create_default_person(self):
        """
        Create a person and mark them as the current authenticated member.
        """
        person = {
            "firstName": {
                "localized": {"en_US": "Example"},
                "preferredLocale": {"country": "US", "language": "en"},
            },
            "localizedFirstName": "Example",
            "lastName": {
                "localized": {"en_US": "User"},
                "preferredLocale": {"country": "US", "language": "en"},
            },
            "localizedLastName": "User",
            "vanityName": "example-user",
        }
        # With next_person_id starting at 1, the new person gets id "1".
        person["id"] = "1"
        LinkedinAPI.DB["people"]["1"] = person
        LinkedinAPI.DB["current_person_id"] = "1"
        LinkedinAPI.DB["next_person_id"] = 2
        return person

    def create_post(self, author, commentary, visibility="PUBLIC"):
        """
        Create a post.
        """
        post = {"author": author, "commentary": commentary, "visibility": visibility}
        response = LinkedinAPI.Posts.create_post(post)
        self.assertIn("data", response)
        return response["data"]

    def test_create_post(self):
        self.create_default_person()
        post_data = {
            "author": "urn:li:person:1",
            "commentary": "New post from a person",
            "visibility": "PUBLIC",
        }
        response = LinkedinAPI.Posts.create_post(post_data)
        self.assertIn("data", response)
        created_post = response["data"]
        self.assertEqual(created_post["commentary"], "New post from a person")
        # The first post gets id "1"
        self.assertEqual(created_post["id"], "1")

    def test_get_post_success(self):
        self.create_default_person()
        post = self.create_post("urn:li:person:1", "Test post content")
        response = LinkedinAPI.Posts.get_post(post["id"])
        self.assertIn("data", response)
        self.assertEqual(response["data"]["id"], post["id"])

    def test_get_post_failure_nonexistent(self):
        response = LinkedinAPI.Posts.get_post("999")
        self.assertIn("error", response)

    def test_find_posts_by_author_success(self):
        """
        Verify that find_posts_by_author returns only posts created by the specified author.
        """
        self.create_default_person()  # Creates person with id "1"
        # Create two posts for author "urn:li:person:1"
        post1 = self.create_post("urn:li:person:1", "First post content")
        post2 = self.create_post("urn:li:person:1", "Second post content")
        # Create a post for a different author
        self.create_post("urn:li:person:2", "Third post content")
        response = LinkedinAPI.Posts.find_posts_by_author("urn:li:person:1")
        self.assertIn("data", response)
        self.assertEqual(len(response["data"]), 2)
        post_ids = [post["id"] for post in response["data"]]
        self.assertIn(post1["id"], post_ids)
        self.assertIn(post2["id"], post_ids)

    def test_find_posts_by_author_pagination(self):
        """
        Verify that pagination works as expected for find_posts_by_author.
        """
        self.create_default_person()  # Create default person "urn:li:person:1"
        # Create five posts for author "urn:li:person:1"
        posts = [
            self.create_post("urn:li:person:1", f"Post content {i}") for i in range(5)
        ]
        # Retrieve posts using pagination: start at index 2, count 2.
        response = LinkedinAPI.Posts.find_posts_by_author(
            "urn:li:person:1", start=2, count=2
        )
        self.assertIn("data", response)
        self.assertEqual(len(response["data"]), 2)
        expected_ids = [posts[2]["id"], posts[3]["id"]]
        actual_ids = [post["id"] for post in response["data"]]
        self.assertEqual(expected_ids, actual_ids)

    def test_find_posts_by_author_no_match(self):
        """
        Verify that find_posts_by_author returns an empty list when there are no posts for the given author.
        """
        response = LinkedinAPI.Posts.find_posts_by_author("urn:li:person:999")
        self.assertIn("data", response)
        self.assertEqual(len(response["data"]), 0)

    def test_update_post_success(self):
        self.create_default_person()
        post = self.create_post("urn:li:person:1", "Original post content")
        post_data = {
            "author": "urn:li:person:1",
            "commentary": "Updated post content",
            "visibility": "PUBLIC",
        }
        response = LinkedinAPI.Posts.update_post(post["id"], post_data)
        self.assertIn("data", response)
        self.assertEqual(response["data"]["commentary"], "Updated post content")

    def test_update_post_failure_nonexistent(self):
        post_data = {
            "author": "urn:li:person:1",
            "commentary": "Nonexistent post update",
            "visibility": "PUBLIC",
        }
        response = LinkedinAPI.Posts.update_post("999", post_data)
        self.assertIn("error", response)

    def test_delete_post_success(self):
        self.create_default_person()
        post = self.create_post("urn:li:person:1", "Post to be deleted")
        response = LinkedinAPI.Posts.delete_post(post["id"])
        self.assertIn("status", response)
        response = LinkedinAPI.Posts.get_post(post["id"])
        self.assertIn("error", response)

    def test_delete_post_failure_nonexistent(self):
        response = LinkedinAPI.Posts.delete_post("999")
        self.assertIn("error", response)
