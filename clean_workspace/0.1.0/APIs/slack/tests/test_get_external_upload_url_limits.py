import unittest
from unittest.mock import patch

from slack.Files import get_external_upload_url
from slack.SimulationEngine.custom_errors import FileSizeLimitExceededError
from common_utils.base_case import BaseTestCaseWithErrorHandler


class TestGetExternalUploadUrlLimits(BaseTestCaseWithErrorHandler):
    """Additional tests covering new validation rules for get_external_upload_url."""

    def setUp(self):
        # Use a minimal DB for each test
        self.test_db = {"files": {}}

    # -------------------------------------------------------
    # File size validation
    # -------------------------------------------------------
    def test_size_exceeds_one_megabyte(self):
        """length > 1 MB should raise FileSizeLimitExceededError."""
        with patch("slack.Files.DB", self.test_db):
            self.assert_error_behavior(
                func_to_call=get_external_upload_url,
                expected_exception_type=FileSizeLimitExceededError,
                expected_message="File size exceeds the 50 MB limit.",
                filename="big.bin",
                length=52_428_801  # 1 byte over the 50MB limit
            )

    # -------------------------------------------------------
    # alt_txt length validation
    # -------------------------------------------------------
    def test_alt_txt_too_long(self):
        """alt_txt longer than 1000 characters should raise ValueError."""
        long_alt_txt = "a" * 1001
        with patch("slack.Files.DB", self.test_db):
            self.assert_error_behavior(
                func_to_call=get_external_upload_url,
                expected_exception_type=ValueError,
                expected_message="alt_txt cannot exceed 1000 characters.",
                filename="image.png",
                length=100,
                alt_txt=long_alt_txt
            ) 