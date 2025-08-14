import json
import os
import sys
import unittest
import requests
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from google_search.SimulationEngine import utils
from common_utils.base_case import BaseTestCaseWithErrorHandler


class TestGoogleSearchUtils(BaseTestCaseWithErrorHandler):
    """Test cases for Google Search utility functions."""

    def setUp(self):
        """Set up test environment."""
        super().setUp()
        # Clear any stored API keys from environment before each test
        for key in ["GOOGLE_API_KEY", "GEMINI_API_KEY"]:
            if key in os.environ:
                del os.environ[key]

    def test_set_google_api_key_valid(self):
        """Test that set_google_api_key stores a valid API key in environment."""
        test_key = "test_api_key_123"
        utils.set_google_api_key(test_key)
        
        self.assertEqual(os.environ.get("GOOGLE_API_KEY"), test_key)

    def test_set_google_api_key_invalid_empty(self):
        """Test that set_google_api_key raises error for empty key."""
        self.assert_error_behavior(
            func_to_call=utils.set_google_api_key,
            expected_exception_type=ValueError,
            expected_message="API key must be a non-empty string",
            api_key=""
        )

    def test_set_google_api_key_invalid_none(self):
        """Test that set_google_api_key raises error for None key."""
        self.assert_error_behavior(
            func_to_call=utils.set_google_api_key,
            expected_exception_type=ValueError,
            expected_message="API key must be a non-empty string",
            api_key=None
        )

    def test_set_google_api_key_invalid_type(self):
        """Test that set_google_api_key raises error for non-string key."""
        self.assert_error_behavior(
            func_to_call=utils.set_google_api_key,
            expected_exception_type=ValueError,
            expected_message="API key must be a non-empty string",
            api_key=123
        )

    def test_get_google_api_key_from_environment(self):
        """Test that get_google_api_key returns key from environment."""
        test_key = "test_api_key_456"
        os.environ["GOOGLE_API_KEY"] = test_key
        
        result = utils.get_google_api_key()
        self.assertEqual(result, test_key)

    def test_get_google_api_key_none_when_not_found(self):
        """Test that get_google_api_key returns None when no key is found."""
        result = utils.get_google_api_key()
        self.assertIsNone(result)

    def test_get_gemini_api_key_from_environment(self):
        """Test that get_google_api_key returns GEMINI_API_KEY from environment."""
        test_key = "test_gemini_api_key_789"
        os.environ["GEMINI_API_KEY"] = test_key
        
        result = utils.get_google_api_key()
        self.assertEqual(result, test_key)

    def test_get_google_api_key_precedence(self):
        """Test that GOOGLE_API_KEY takes precedence over GEMINI_API_KEY."""
        google_key = "google_key"
        gemini_key = "gemini_key"
        os.environ["GOOGLE_API_KEY"] = google_key
        os.environ["GEMINI_API_KEY"] = gemini_key
        
        result = utils.get_google_api_key()
        self.assertEqual(result, google_key)

    def test_get_recent_searches_empty(self):
        """Test get_recent_searches returns an empty list."""
        with patch('google_search.SimulationEngine.utils.DB') as mock_db:
            mock_db.get.return_value = []
            self.assertEqual(utils.get_recent_searches(), [])
            mock_db.get.assert_called_once_with("recent_searches", [])

    def test_get_recent_searches_with_items(self):
        """Test get_recent_searches returns a list of items."""
        with patch('google_search.SimulationEngine.utils.DB') as mock_db:
            searches = [{"query": "test", "result": "test result"}]
            mock_db.get.return_value = searches
            self.assertEqual(utils.get_recent_searches(), searches)

    def test_add_recent_search_to_empty_list(self):
        """Test add_recent_search adds to an empty list."""
        with patch('google_search.SimulationEngine.utils.DB') as mock_db:
            db_dict = {}
            mock_db.get.return_value = []
            mock_db.__setitem__.side_effect = db_dict.__setitem__
            
            result = {"query": "test", "result": "result"}
            utils.add_recent_search(result)
            
            self.assertEqual(db_dict["recent_searches"], [result])

    def test_add_recent_search_to_existing_list(self):
        """Test add_recent_search prepends to an existing list."""
        with patch('google_search.SimulationEngine.utils.DB') as mock_db:
            db_dict = {}
            initial_list = [{"query": "old", "result": "old_result"}]
            mock_db.get.return_value = initial_list
            mock_db.__setitem__.side_effect = db_dict.__setitem__

            new_result = {"query": "new", "result": "new_result"}
            utils.add_recent_search(new_result)
            
            self.assertEqual(db_dict["recent_searches"], [new_result, initial_list[1]])

    def test_add_recent_search_respects_limit(self):
        """Test add_recent_search does not exceed the 50-item limit."""
        with patch('google_search.SimulationEngine.utils.DB') as mock_db:
            db_dict = {}
            # Create a list of 50 items
            fifty_items = [{"query": f"q{i}", "result": f"r{i}"} for i in range(50)]
            mock_db.get.return_value = fifty_items
            mock_db.__setitem__.side_effect = db_dict.__setitem__
            
            new_result = {"query": "new", "result": "new_result"}
            utils.add_recent_search(new_result)
            
            self.assertEqual(len(db_dict["recent_searches"]), 50)
            self.assertEqual(db_dict["recent_searches"][0], new_result)
            # The last item of the original list should be gone
            self.assertNotIn(fifty_items[-1], db_dict["recent_searches"])

    @unittest.skip("Skipping this test as there is no .env file on github and the test needs that to be run.")
    def test_get_gemini_response_returns_string(self):
        """Test that get_gemini_response returns a string."""
        with patch('google_search.SimulationEngine.utils.requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                'candidates': [{
                    'content': {
                        'parts': [{'text': 'Test response from Gemini'}]
                    }
                }]
            }
            mock_post.return_value = mock_response
            
            result = utils.get_gemini_response("test query")
            self.assertIsInstance(result, str)
            self.assertEqual(result, "Test response from Gemini")

    def test_get_gemini_response_missing_api_key(self):
        """Test that get_gemini_response raises error when API key is missing."""
        with patch.dict(os.environ, {}, clear=True):
            self.assert_error_behavior(
                func_to_call=utils.get_gemini_response,
                expected_exception_type=ValueError,
                expected_message="Google or Gemini API Key not found. Please create a .env file in the project root with GOOGLE_API_KEY or GEMINI_API_KEY, or set it as an environment variable.",
                query_text="test query"
            )

    def test_get_gemini_response_missing_live_api_url(self):
        """Test that get_gemini_response raises error when LIVE_API_URL is missing."""
        with patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_key'}, clear=True):
            self.assert_error_behavior(
                func_to_call=utils.get_gemini_response,
                expected_exception_type=ValueError,
                expected_message="LIVE API URL not found. Please create a .env file in the project root with LIVE_API_URL, or set it as an environment variable.",
                query_text="test query"
            )

    def test_get_gemini_response_with_google_api_key(self):
        """Test that get_gemini_response works with GOOGLE_API_KEY."""
        with patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_key', 'LIVE_API_URL': 'https://test-api.com'}, clear=True):
            with patch('google_search.SimulationEngine.utils.requests.post') as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    'candidates': [{
                        'content': {
                            'parts': [{'text': 'Test response'}]
                        }
                    }]
                }
                mock_post.return_value = mock_response
                
                result = utils.get_gemini_response("test query")
                self.assertEqual(result, "Test response")

    def test_get_gemini_response_with_gemini_api_key(self):
        """Test that get_gemini_response works with GEMINI_API_KEY."""
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key_gemini', 'LIVE_API_URL': 'https://test-api.com'}, clear=True):
            with patch('google_search.SimulationEngine.utils.requests.post') as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    'candidates': [{
                        'content': {
                            'parts': [{'text': 'Test response with gemini key'}]
                        }
                    }]
                }
                mock_post.return_value = mock_response

                result = utils.get_gemini_response("test query")
                self.assertEqual(result, "Test response with gemini key")
                
                # Verify the correct URL was called with the gemini key
                expected_url = "https://test-api.com?key=test_key_gemini"
                mock_post.assert_called_once()
                call_args = mock_post.call_args
                self.assertEqual(call_args[0][0], expected_url)

    def test_get_gemini_response_with_overridden_api_key(self):
        """Test that get_gemini_response works with overridden API key."""
        with patch.dict(os.environ, {'LIVE_API_URL': 'https://test-api.com'}, clear=True):
            with patch('google_search.SimulationEngine.utils.requests.post') as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    'candidates': [{
                        'content': {
                            'parts': [{'text': 'Test response with overridden key'}]
                        }
                    }]
                }
                mock_post.return_value = mock_response
                
                result = utils.get_gemini_response("test query", api_key="overridden_key")
                self.assertEqual(result, "Test response with overridden key")
                
                # Verify the correct URL was called with overridden key
                expected_url = "https://test-api.com?key=overridden_key"
                mock_post.assert_called_once()
                call_args = mock_post.call_args
                self.assertEqual(call_args[0][0], expected_url)

    def test_get_gemini_response_with_set_api_key(self):
        """Test that get_gemini_response works with API key set via set_google_api_key."""
        with patch.dict(os.environ, {'LIVE_API_URL': 'https://test-api.com'}, clear=True):
            with patch('google_search.SimulationEngine.utils.requests.post') as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    'candidates': [{
                        'content': {
                            'parts': [{'text': 'Test response with set key'}]
                        }
                    }]
                }
                mock_post.return_value = mock_response
                
                # Set API key via utility function
                utils.set_google_api_key("set_api_key")
                
                result = utils.get_gemini_response("test query")
                self.assertEqual(result, "Test response with set key")
                
                # Verify the correct URL was called with set key
                expected_url = "https://test-api.com?key=set_api_key"
                mock_post.assert_called_once()
                call_args = mock_post.call_args
                self.assertEqual(call_args[0][0], expected_url)

    def test_get_gemini_response_http_error(self):
        """Test that get_gemini_response handles HTTP errors."""
        with patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_key', 'LIVE_API_URL': 'https://test-api.com'}, clear=True):
            with patch('google_search.SimulationEngine.utils.requests.post') as mock_post:
                mock_post.side_effect = requests.exceptions.RequestException("HTTP Error")
                
                result = utils.get_gemini_response("test query")
                self.assertIsNone(result)

    def test_get_gemini_response_json_decode_error(self):
        """Test that get_gemini_response handles JSON decode errors."""
        with patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_key', 'LIVE_API_URL': 'https://test-api.com'}, clear=True):
            with patch('google_search.SimulationEngine.utils.requests.post') as mock_post:
                mock_response = MagicMock()
                mock_response.json.side_effect = json.JSONDecodeError("JSON Error", "test", 0)
                mock_post.return_value = mock_response
                
                result = utils.get_gemini_response("test query")
                self.assertIsNone(result)

    def test_get_gemini_response_correct_url_and_headers(self):
        """Test that get_gemini_response uses correct URL and headers."""
        with patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_key', 'LIVE_API_URL': 'https://test-api.com'}, clear=True):
            with patch('google_search.SimulationEngine.utils.requests.post') as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    'candidates': [{
                        'content': {
                            'parts': [{'text': 'Test response'}]
                        }
                    }]
                }
                mock_post.return_value = mock_response
                
                utils.get_gemini_response("test query")
                
                # Verify the correct URL was called
                expected_url = "https://test-api.com?key=test_key"
                mock_post.assert_called_once()
                call_args = mock_post.call_args
                self.assertEqual(call_args[0][0], expected_url)
                
                # Verify headers
                self.assertEqual(call_args[1]['headers'], {"Content-Type": "application/json"})

    def test_get_gemini_response_correct_data_structure(self):
        """Test that get_gemini_response sends correct data structure."""
        with patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_key', 'LIVE_API_URL': 'https://test-api.com'}, clear=True):
            with patch('google_search.SimulationEngine.utils.requests.post') as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    'candidates': [{
                        'content': {
                            'parts': [{'text': 'Test response'}]
                        }
                    }]
                }
                mock_post.return_value = mock_response
                
                utils.get_gemini_response("test query")
                
                # Verify the data structure
                call_args = mock_post.call_args
                data = call_args[1]['json']
                expected_data = {
                    "model": "models/chat-bard-003",
                    "generationConfig": {"candidateCount": 1},
                    "contents": [{"role": "user", "parts": {"text": "Use @Google Search to search exactly this query, do not alter it: 'test query'"}}]
                }
                self.assertEqual(data, expected_data)

    def test_get_gemini_response_with_long_query(self):
        """Test that get_gemini_response handles long queries."""
        with patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_key', 'LIVE_API_URL': 'https://test-api.com'}, clear=True):
            with patch('google_search.SimulationEngine.utils.requests.post') as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    'candidates': [{
                        'content': {
                            'parts': [{'text': 'Long response'}]
                        }
                    }]
                }
                mock_post.return_value = mock_response
                
                long_query = "This is a very long query with many words and should be handled properly by the API"
                result = utils.get_gemini_response(long_query)
                self.assertEqual(result, "Long response")

    def test_get_gemini_response_with_special_characters(self):
        """Test that get_gemini_response handles special characters in queries."""
        with patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_key', 'LIVE_API_URL': 'https://test-api.com'}, clear=True):
            with patch('google_search.SimulationEngine.utils.requests.post') as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    'candidates': [{
                        'content': {
                            'parts': [{'text': 'Special response'}]
                        }
                    }]
                }
                mock_post.return_value = mock_response
                
                special_query = "Query with special chars: @#$%^&*()_+-=[]{}|;':\",./<>?"
                result = utils.get_gemini_response(special_query)
                self.assertEqual(result, "Special response")

    def test_get_gemini_response_empty_query(self):
        """Test that get_gemini_response handles empty queries."""
        with patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_key', 'LIVE_API_URL': 'https://test-api.com'}, clear=True):
            with patch('google_search.SimulationEngine.utils.requests.post') as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    'candidates': [{
                        'content': {
                            'parts': [{'text': 'Empty query response'}]
                        }
                    }]
                }
                mock_post.return_value = mock_response
                
                result = utils.get_gemini_response("")
                self.assertEqual(result, "Empty query response")

    def test_get_gemini_response_whitespace_query(self):
        """Test that get_gemini_response handles whitespace-only queries."""
        with patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_key', 'LIVE_API_URL': 'https://test-api.com'}, clear=True):
            with patch('google_search.SimulationEngine.utils.requests.post') as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    'candidates': [{
                        'content': {
                            'parts': [{'text': 'Whitespace response'}]
                        }
                    }]
                }
                mock_post.return_value = mock_response
                
                result = utils.get_gemini_response("   ")
                self.assertEqual(result, "Whitespace response")


if __name__ == "__main__":
    unittest.main()
