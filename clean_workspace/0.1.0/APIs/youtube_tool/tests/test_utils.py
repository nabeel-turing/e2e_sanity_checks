import json
import os
import sys
import unittest
import requests
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from youtube_tool.SimulationEngine import utils
from common_utils.base_case import BaseTestCaseWithErrorHandler
from youtube_tool.SimulationEngine.custom_errors import EnvironmentError

class TestYouTubeToolUtils(BaseTestCaseWithErrorHandler):
    """Test cases for the YouTube Tool utility functions."""
    def setUp(self):
        """Set up the test environment."""
        super().setUp()
        utils.DB = {}
    
    def test_get_json_response_returns_correct_list(self):
        """Test that get_json_response returns a list."""
            
        gemini_output = {
                            "codeOutputState": {
                                "executionTrace": {
                                    "executions": [
                                        {
                                            "jsonOutput": "[{\"title\": \"Test Video\", \"url\": \"https://youtube.com/watch?v=test_video_id\", \"channel_name\": \"Test Channel\", \"view_count\": 1000}]"
                                        }
                                    ]
                                }
                            }
                        }
                                                    
        results = utils.get_json_response(gemini_output)
        self.assertIsInstance(results, list)
        self.assertEqual(results, [{"title": "Test Video", "url": "https://youtube.com/watch?v=test_video_id", "channel_name": "Test Channel", "view_count": 1000}])


    def test_get_json_response_returns_empty_list(self):
        """Test that get_json_response returns an empty list when there is no jsonOutput."""
            
        gemini_output = {
            "codeOutputState": {
                "executionTrace": {
                    "executions": [
                        {
                            "key": "value"
                        }
                    ]
                }
            }
        }
                                                    
        results = utils.get_json_response(gemini_output)
        self.assertIsInstance(results, list)
        self.assertEqual(results, [])

    def test_get_json_response_incorrect_structure_gemini_output(self):
        """Test that get_json_response returns None when the gemini output has incorrect structure."""
        gemini_output = """
        {
            "key": "value"
        }
        """
        results = utils.get_json_response(gemini_output)
        self.assertIsNone(results)

    def test_get_json_response_returns_none(self):
        """Test that get_json_response returns None when the gemini output is not a valid JSON."""
        gemini_output = []
        results = utils.get_json_response(gemini_output)
        self.assertIsNone(results)

        gemini_output = 123
        results = utils.get_json_response(gemini_output)
        self.assertIsNone(results)

    def test_get_recent_searches(self):
        """Test that get_recent_searches returns the correct list of recent searches."""
        recent_searches = utils.get_recent_searches()
        self.assertIsInstance(recent_searches, list)
        self.assertEqual(recent_searches, [])

    def test_add_recent_search(self):
        """Test that add_recent_search adds the search query to the recent searches list."""
        utils.add_recent_search(endpoint="search", parameters={"query": "test_query", "result_type": "VIDEO"}, result=[{"title": "Test Video", "url": "https://youtube.com/watch?v=test_video_id", "channel_name": "Test Channel", "view_count": 1000}])
        recent_searches = utils.get_recent_searches()
        self.assertEqual(recent_searches, [{"parameters": {"query": "test_query", "result_type": "VIDEO"}, "result": [{"title": "Test Video", "url": "https://youtube.com/watch?v=test_video_id", "channel_name": "Test Channel", "view_count": 1000}]}])

    def test_get_recent_searches_with_max_results(self):
        """Test that get_recent_searches returns the correct list of recent searches with max results."""
        utils.add_recent_search(endpoint="search", parameters={"query": "test_query", "result_type": "VIDEO"}, result=[{"title": "Test Video", "url": "https://youtube.com/watch?v=test_video_id", "channel_name": "Test Channel", "view_count": 1000}])
        utils.add_recent_search(endpoint="search", parameters={"query": "test_query2", "result_type": "VIDEO"}, result=[{"title": "Test Video 2", "url": "https://youtube.com/watch?v=test_video_id_2", "channel_name": "Test Channel 2", "view_count": 2000}])
        utils.add_recent_search(endpoint="search", parameters={"query": "test_query3", "result_type": "VIDEO"}, result=[{"title": "Test Video 3", "url": "https://youtube.com/watch?v=test_video_id_3", "channel_name": "Test Channel 3", "view_count": 3000}])
        recent_searches = utils.get_recent_searches(max_results=2)
        self.assertEqual(recent_searches, [{"parameters": {"query": "test_query3", "result_type": "VIDEO"}, "result": [{"title": "Test Video 3", "url": "https://youtube.com/watch?v=test_video_id_3", "channel_name": "Test Channel 3", "view_count": 3000}]}, {"parameters": {"query": "test_query2", "result_type": "VIDEO"}, "result": [{"title": "Test Video 2", "url": "https://youtube.com/watch?v=test_video_id_2", "channel_name": "Test Channel 2", "view_count": 2000}]}])


if __name__ == "__main__":
    unittest.main()
