# APIs/tiktokApi/Tests/test_TikTok.py
import unittest
import tiktok as TikTokAPI
from tiktok.SimulationEngine.db import DB, save_state, load_state
from tiktok.SimulationEngine.utils import (
    _add_business_account,
    _update_business_account,
    _delete_business_account,
)
import os
from common_utils.base_case import BaseTestCaseWithErrorHandler


###############################################################################
# Unit Tests
###############################################################################
class TestTikTokAPI(BaseTestCaseWithErrorHandler):
    """
    Unit tests for the TikTok API simulation.
    """

    def setUp(self):
        """
        Set up the test environment.
        """
        DB.clear()
        DB.update({})

    def test_business_get_success(self):
        """
        Test successful retrieval of account data.
        """
        business_id = "test_account"
        _add_business_account(
            business_id, {"username": "testuser", "display_name": "Test User"}
        )
        response = TikTokAPI.Business.Get.get(
            access_token="test_token", business_id=business_id
        )
        self.assertEqual(response["code"], 200)
        self.assertEqual(response["data"]["username"], "testuser")

        response = TikTokAPI.Business.Get.get(
            access_token="test_token",
            business_id=business_id,
            fields=["username", "display_name"],
        )
        self.assertEqual(response["code"], 200)
        self.assertEqual(response["data"]["username"], "testuser")
        self.assertEqual(response["data"]["display_name"], "Test User")

    def test_business_get_not_found(self):
        """
        Test retrieval of non-existent account.
        """
        response = TikTokAPI.Business.Get.get(
            access_token="test_token", business_id="nonexistent"
        )
        self.assertEqual(response["code"], 404)

    def test_business_get_required_params(self):
        """
        Test missing required parameters.
        """
        response = TikTokAPI.Business.Get.get(
            access_token=None, business_id="test_account"
        )
        self.assertEqual(response["code"], 400)
        self.assertEqual(response["message"], "Access-Token is required")

        response = TikTokAPI.Business.Get.get(
            access_token="test_token", business_id=None
        )
        self.assertEqual(response["code"], 400)
        self.assertEqual(response["message"], "business_id is required")

    def test_business_get_date_range(self):
        """
        Test retrieval of account data with date range.
        """
        business_id = "test_account"
        DB[business_id] = {
            "username": "testuser",
            "display_name": "Test User",
            "profile": {"bio": "Test bio", "followers_count": 1000},
            "analytics": {"total_likes": 5000},
        }

        # Test valid date format
        result = TikTokAPI.Business.Get.get(
            access_token="test_token",
            business_id=business_id,
            start_date="13-01-2024",
            end_date="2024-01-31",
        )
        self.assertEqual(result["code"], 400)

        result = TikTokAPI.Business.Get.get(
            access_token="test_token",
            business_id=business_id,
            start_date="2024-01-13",
            end_date="2024-31-01",
        )

    def test_business_video_publish_success(self):
        """
        Test successful video publishing.
        """
        response = TikTokAPI.Business.Video.Publish.post(
            access_token="test_token",  # Provide a valid access_token
            content_type="application/json",
            business_id="test_account",
            video_url="http://example.com/video.mp4",
            post_info={"is_ai_generated": True},
        )
        self.assertEqual(response["code"], 200)
        self.assertIn("share_id", response["data"])

    def test_business_video_publish_required_params(self):
        """
        Test missing required parameters for video publishing.
        """
        response = TikTokAPI.Business.Video.Publish.post(
            access_token=None,
            content_type="application/json",
            business_id="test_account",
            video_url="http://example.com/video.mp4",
            post_info={},
        )
        self.assertEqual(response["code"], 400)
        self.assertEqual(response["message"], "Access-Token is required")

        response = TikTokAPI.Business.Video.Publish.post(
            access_token="test_token",
            content_type="invalid",
            business_id="test_account",
            video_url="http://example.com/video.mp4",
            post_info={},
        )
        self.assertEqual(response["code"], 400)
        self.assertEqual(response["message"], "Content-Type must be application/json")

        response = TikTokAPI.Business.Video.Publish.post(
            access_token="test_token",
            content_type="application/json",
            business_id=None,
            video_url="http://example.com/video.mp4",
            post_info={},
        )
        self.assertEqual(response["code"], 400)
        self.assertEqual(response["message"], "business_id is required")

        response = TikTokAPI.Business.Video.Publish.post(
            access_token="test_token",
            content_type="application/json",
            business_id="test_account",
            video_url=None,
            post_info={},
        )
        self.assertEqual(response["code"], 400)
        self.assertEqual(response["message"], "video_url is required")

        response = TikTokAPI.Business.Video.Publish.post(
            access_token="test_token",
            content_type="application/json",
            business_id="test_account",
            video_url="http://example.com/video.mp4",
            post_info=None,
        )
        self.assertEqual(response["code"], 400)
        self.assertEqual(response["message"], "post_info is required")

    def test_business_publish_status_success(self):
        """
        Test successful retrieval of publish status.
        """
        response = TikTokAPI.Business.Publish.Status.get(
            access_token="test_token",
            business_id="test_account",
            publish_id="test_publish_id",
        )
        self.assertEqual(response["code"], 200)
        self.assertIn("status", response["data"])

    def test_business_publish_status_required_params(self):
        """
        Test missing required parameters for publish status.
        """
        response = TikTokAPI.Business.Publish.Status.get(
            access_token=None, business_id="test_account", publish_id="test_publish_id"
        )
        self.assertEqual(response["code"], 400)
        self.assertEqual(response["message"], "Access-Token is required")

        response = TikTokAPI.Business.Publish.Status.get(
            access_token="test_token", business_id=None, publish_id="test_publish_id"
        )
        self.assertEqual(response["code"], 400)
        self.assertEqual(response["message"], "business_id is required")

        response = TikTokAPI.Business.Publish.Status.get(
            access_token="test_token", business_id="test_account", publish_id=None
        )
        self.assertEqual(response["code"], 400)
        self.assertEqual(response["message"], "publish_id is required")

    def test_helper_functions(self):
        """
        Test helper functions.
        """
        business_id = "test_account"
        _add_business_account(business_id, {"username": "testuser"})
        self.assertEqual(DB[business_id]["username"], "testuser")

        _update_business_account(business_id, {"username": "testuser2"})
        self.assertEqual(DB[business_id]["username"], "testuser2")

        _delete_business_account(business_id)
        self.assertEqual(DB, {})
        with self.assertRaises(ValueError):
            _delete_business_account(business_id)

        with self.assertRaises(ValueError):
            _update_business_account(business_id, {"username": "testuser2"})
