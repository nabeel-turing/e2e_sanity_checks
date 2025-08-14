# google_maps_live/tests/test_places.py
import pytest
from unittest.mock import patch, MagicMock
from google_maps_live.places import query_places, lookup_place_details, analyze_places, show_on_map
from google_maps_live.SimulationEngine.models import PriceLevel, RankPreference
from google_maps_live.SimulationEngine.custom_errors import UndefinedLocationError, UserLocationError
from common_utils.base_case import BaseTestCaseWithErrorHandler


class TestQueryPlaces(BaseTestCaseWithErrorHandler):
    """Test cases for the query_places function."""
    
    @patch('google_maps_live.SimulationEngine.utils.get_gemini_response')
    def test_basic_place_search(self, mock_gemini):
        """Test basic place search functionality."""
        # Mock Gemini response with proper JSON structure
        mock_gemini.return_value = '''```json
        {
        "map_url": "https://maps.google.com/search?q=restaurants",
        "places": [
            {
            "id": "place_123",
            "name": "Joe's Pizza",
            "description": "Authentic Italian pizza restaurant",
            "rating": "4.2",
            "url": "https://joespizza.com",
            "map_url": "https://maps.google.com/place?q=Joe's+Pizza",
            "review_count": 150,
            "user_rating_count": 200,
            "address": "123 Main St, San Francisco, CA",
            "phone_number": "+1-555-0123",
            "photos": ["https://example.com/photo1.jpg"],
            "opening_hours": ["Monday: 11:00 AM - 10:00 PM", "Tuesday: 11:00 AM - 10:00 PM"],
            "distance": "0.5 miles",
            "distance_in_meters": 800
            },
            {
            "id": "place_456",
            "name": "Maria's Cafe",
            "description": "Cozy coffee shop with pastries",
            "rating": "4.5",
            "url": "https://mariascafe.com",
            "map_url": "https://maps.google.com/place?q=Maria's+Cafe",
            "review_count": 89,
            "user_rating_count": 120,
            "address": "456 Oak Ave, San Francisco, CA",
            "phone_number": "+1-555-0456",
            "photos": ["https://example.com/photo2.jpg"],
            "opening_hours": ["Monday: 7:00 AM - 8:00 PM", "Tuesday: 7:00 AM - 8:00 PM"],
            "distance": "0.8 miles",
            "distance_in_meters": 1280
            }
        ],
        "detours": null,
        "query": "restaurants"
        }
        ```'''
        
        result = query_places(query=["restaurants"])
        
        assert isinstance(result, dict)
        assert "map_url" in result
        assert "places" in result
        assert "detours" in result
        assert "query" in result
        assert len(result["places"]) > 0
        
        place = result["places"][0]
        assert "id" in place
        assert "name" in place
        assert "rating" in place
        assert "address" in place
        assert "phone_number" in place
    
    @patch('google_maps_live.SimulationEngine.utils.get_gemini_response')
    def test_place_search_with_multiple_queries(self, mock_gemini):
        """Test place search with multiple queries."""
        # Mock Gemini response with proper JSON structure
        mock_gemini.return_value = '''```json
{
  "map_url": "https://maps.google.com/search?q=restaurants+coffee+shops",
  "places": [
    {
      "id": "place_789",
      "name": "Starbucks",
      "description": "International coffee chain",
      "rating": "4.0",
      "url": "https://starbucks.com",
      "map_url": "https://maps.google.com/place?q=Starbucks",
      "review_count": 300,
      "user_rating_count": 450,
      "address": "789 Coffee St, San Francisco, CA",
      "phone_number": "+1-555-0789",
      "photos": ["https://example.com/photo3.jpg"],
      "opening_hours": ["Monday: 6:00 AM - 9:00 PM"],
      "distance": "0.3 miles",
      "distance_in_meters": 480
    },
    {
      "id": "place_101",
      "name": "Peet's Coffee",
      "description": "Premium coffee and tea",
      "rating": "4.3",
      "url": "https://peets.com",
      "map_url": "https://maps.google.com/place?q=Peet's+Coffee",
      "review_count": 120,
      "user_rating_count": 180,
      "address": "101 Tea Ave, San Francisco, CA",
      "phone_number": "+1-555-0101",
      "photos": ["https://example.com/photo4.jpg"],
      "opening_hours": ["Monday: 6:30 AM - 8:30 PM"],
      "distance": "0.6 miles",
      "distance_in_meters": 960
    }
  ],
  "detours": null,
  "query": "restaurants coffee shops"
}
```'''
        
        result = query_places(query=["restaurants", "coffee shops"])
        
        assert len(result["places"]) == 2
        assert result["query"] == "restaurants coffee shops"
    
    @patch('google_maps_live.SimulationEngine.utils.get_gemini_response')
    def test_place_search_with_location_bias(self, mock_gemini):
        """Test place search with location bias."""
        # Mock Gemini response with proper JSON structure
        mock_gemini.return_value = '''```json
{
  "map_url": "https://maps.google.com/search?q=restaurants&location=San+Francisco,+CA",
  "places": [
    {
      "id": "place_202",
      "name": "Fisherman's Wharf",
      "description": "Seafood restaurant with waterfront views",
      "rating": "4.4",
      "url": "https://fishermanswharf.com",
      "map_url": "https://maps.google.com/place?q=Fisherman's+Wharf",
      "review_count": 250,
      "user_rating_count": 320,
      "address": "202 Wharf St, San Francisco, CA",
      "phone_number": "+1-555-0202",
      "photos": ["https://example.com/photo5.jpg"],
      "opening_hours": ["Monday: 11:00 AM - 11:00 PM"],
      "distance": "0.2 miles",
      "distance_in_meters": 320
    }
  ],
  "detours": null,
  "query": "restaurants"
}
```'''
        
        result = query_places(
            query=["restaurants"],
            location_bias="San Francisco, CA"
        )
        
        assert isinstance(result, dict)
        assert "places" in result
    
    @patch('google_maps_live.SimulationEngine.utils.get_gemini_response')
    def test_place_search_with_user_location_environment_variables(self, mock_gemini):
        """Test place search with all UserLocation environment variables for location_bias parameter."""
        # Mock Gemini response with proper JSON structure
        mock_gemini.return_value = '''```json
{
  "map_url": "https://maps.google.com/search?q=restaurants&location=San+Francisco,+CA",
  "places": [
    {
      "id": "place_202",
      "name": "Fisherman's Wharf",
      "description": "Seafood restaurant with waterfront views",
      "rating": "4.4",
      "url": "https://fishermanswharf.com",
      "map_url": "https://maps.google.com/place?q=Fisherman's+Wharf",
      "review_count": 250,
      "user_rating_count": 320,
      "address": "202 Wharf St, San Francisco, CA",
      "phone_number": "+1-555-0202",
      "photos": ["https://example.com/photo5.jpg"],
      "opening_hours": ["Monday: 11:00 AM - 11:00 PM"],
      "distance": "0.2 miles",
      "distance_in_meters": 320
    }
  ],
  "detours": null,
  "query": "restaurants"
}
```'''
        
        # Test with MY_HOME environment variable
        with patch.dict('os.environ', {'MY_HOME': 'San Francisco, CA'}):
            result = query_places(
                query=["restaurants"],
                location_bias="MY_HOME"
            )
            assert isinstance(result, dict)
            assert "places" in result
            assert "map_url" in result
            assert "query" in result
        
        # Test with MY_LOCATION environment variable
        with patch.dict('os.environ', {'MY_LOCATION': 'Mountain View, CA'}):
            result = query_places(
                query=["restaurants"],
                location_bias="MY_LOCATION"
            )
            assert isinstance(result, dict)
            assert "places" in result
            assert "map_url" in result
            assert "query" in result
        
        # Test with MY_WORK environment variable
        with patch.dict('os.environ', {'MY_WORK': 'Palo Alto, CA'}):
            result = query_places(
                query=["restaurants"],
                location_bias="MY_WORK"
            )
            assert isinstance(result, dict)
            assert "places" in result
            assert "map_url" in result
            assert "query" in result
    
    def test_place_search_with_undefined_user_location_environment_variable(self):
        """Test that undefined UserLocation environment variable raises UndefinedLocationError."""
        # Test with MY_HOME not set
        self.assert_error_behavior(
            lambda: query_places(
                query=["restaurants"],
                location_bias="MY_HOME"
            ),
            UndefinedLocationError,
            "Environment variable for 'MY_HOME' is not defined."
        )
        
        # Test with MY_LOCATION not set
        self.assert_error_behavior(
            lambda: query_places(
                query=["restaurants"],
                location_bias="MY_LOCATION"
            ),
            UndefinedLocationError,
            "Environment variable for 'MY_LOCATION' is not defined."
        )
        
        # Test with MY_WORK not set
        self.assert_error_behavior(
            lambda: query_places(
                query=["restaurants"],
                location_bias="MY_WORK"
            ),
            UndefinedLocationError,
            "Environment variable for 'MY_WORK' is not defined."
        )
    
    def test_place_search_with_invalid_user_location_value(self):
        """Test that invalid UserLocation value is accepted by Pydantic model but fails when used."""
        from google_maps_live.SimulationEngine.models import QueryPlacesInput
        
        # The Pydantic model should accept invalid location bias values
        # since they might be valid place names or coordinates
        model = QueryPlacesInput(
            query=["restaurants"],
            location_bias="INVALID_LOCATION"
        )
        
        # The invalid value should be returned as-is
        assert model.location_bias == "INVALID_LOCATION"
        
        # However, when we try to use it in a function that calls get_location_from_env,
        # it should raise UserLocationError. Let's test that directly:
        from google_maps_live.SimulationEngine.utils import get_location_from_env
        
        with self.assertRaises(UserLocationError) as context:
            get_location_from_env("INVALID_LOCATION")
        
        self.assertEqual(
            str(context.exception),
            "Invalid location variable: 'INVALID_LOCATION'. Must be one of MY_HOME, MY_LOCATION, MY_WORK"
        )
    
    @patch('google_maps_live.SimulationEngine.utils.get_gemini_response')
    def test_place_search_with_rating_filter(self, mock_gemini):
        """Test place search with minimum rating filter."""
        # Mock Gemini response with proper JSON structure
        mock_gemini.return_value = '''```json
{
  "map_url": "https://maps.google.com/search?q=restaurants&min_rating=4.0",
  "places": [
    {
      "id": "place_303",
      "name": "Gourmet Bistro",
      "description": "Fine dining with French cuisine",
      "rating": "4.8",
      "url": "https://gourmetbistro.com",
      "map_url": "https://maps.google.com/place?q=Gourmet+Bistro",
      "review_count": 180,
      "user_rating_count": 220,
      "address": "303 Gourmet Blvd, San Francisco, CA",
      "phone_number": "+1-555-0303",
      "photos": ["https://example.com/photo6.jpg"],
      "opening_hours": ["Monday: 5:00 PM - 10:00 PM"],
      "distance": "1.2 miles",
      "distance_in_meters": 1920
    }
  ],
  "detours": null,
  "query": "restaurants"
}
```'''
        
        result = query_places(
            query=["restaurants"],
            min_rating=4.0
        )
        
        assert isinstance(result, dict)
        assert "places" in result
    
    @patch('google_maps_live.SimulationEngine.utils.get_gemini_response')
    def test_place_search_with_price_levels(self, mock_gemini):
        """Test place search with price level filters."""
        # Mock Gemini response with proper JSON structure
        mock_gemini.return_value = '''```json
{
  "map_url": "https://maps.google.com/search?q=restaurants&price_levels=moderate,expensive",
  "places": [
    {
      "id": "place_404",
      "name": "Mid-Range Bistro",
      "description": "Casual dining with moderate prices",
      "rating": "4.1",
      "url": "https://midrangebistro.com",
      "map_url": "https://maps.google.com/place?q=Mid-Range+Bistro",
      "review_count": 95,
      "user_rating_count": 130,
      "address": "404 Mid St, San Francisco, CA",
      "phone_number": "+1-555-0404",
      "photos": ["https://example.com/photo7.jpg"],
      "opening_hours": ["Monday: 11:30 AM - 9:30 PM"],
      "distance": "0.7 miles",
      "distance_in_meters": 1120
    }
  ],
  "detours": null,
  "query": "restaurants"
}
```'''
        
        result = query_places(
            query=["restaurants"],
            price_levels=["moderate", "expensive"]
        )
        
        assert isinstance(result, dict)
        assert "places" in result
    
    @patch('google_maps_live.SimulationEngine.utils.get_gemini_response')
    def test_place_search_with_rank_preference(self, mock_gemini):
        """Test place search with rank preference."""
        # Mock Gemini response with proper JSON structure
        mock_gemini.return_value = '''```json
{
  "map_url": "https://maps.google.com/search?q=restaurants&rank_preference=distance",
  "places": [
    {
      "id": "place_505",
      "name": "Close Pizza",
      "description": "Neighborhood pizza place",
      "rating": "4.0",
      "url": "https://closepizza.com",
      "map_url": "https://maps.google.com/place?q=Close+Pizza",
      "review_count": 75,
      "user_rating_count": 100,
      "address": "505 Close Ave, San Francisco, CA",
      "phone_number": "+1-555-0505",
      "photos": ["https://example.com/photo8.jpg"],
      "opening_hours": ["Monday: 12:00 PM - 10:00 PM"],
      "distance": "0.5 miles",
      "distance_in_meters": 800
    }
  ],
  "detours": null,
  "query": "restaurants"
}
```'''
        
        result = query_places(
            query=["restaurants"],
            rank_preference="distance"
        )
        
        assert isinstance(result, dict)
        assert "places" in result
    
    @patch('google_maps_live.SimulationEngine.utils.get_gemini_response')
    def test_place_search_with_open_now_filter(self, mock_gemini):
        """Test place search with open now filter."""
        # Mock Gemini response with proper JSON structure
        mock_gemini.return_value = '''```json
{
  "map_url": "https://maps.google.com/search?q=restaurants&open_now=true",
  "places": [
    {
      "id": "place_606",
      "name": "24/7 Diner",
      "description": "Always open diner with comfort food",
      "rating": "3.8",
      "url": "https://247diner.com",
      "map_url": "https://maps.google.com/place?q=24/7+Diner",
      "review_count": 200,
      "user_rating_count": 280,
      "address": "606 Night St, San Francisco, CA",
      "phone_number": "+1-555-0606",
      "photos": ["https://example.com/photo9.jpg"],
      "opening_hours": ["Monday: 24 hours"],
      "distance": "1.0 miles",
      "distance_in_meters": 1600
    }
  ],
  "detours": null,
  "query": "restaurants"
}
```'''
        
        result = query_places(
            query=["restaurants"],
            only_open_now=True
        )
        
        assert isinstance(result, dict)
        assert "places" in result
    
    def test_empty_query_list(self):
        """Test that empty query list raises ValueError."""
        self.assert_error_behavior(
            lambda: query_places(query=[]),
            ValueError,
            "Query list cannot be empty"
        )
    
    def test_invalid_min_rating(self):
        """Test that invalid min_rating raises ValueError."""
        self.assert_error_behavior(
            lambda: query_places(
                query=["restaurants"],
                min_rating=6.0
            ),
            ValueError,
            "min_rating must be between 1.0 and 5.0"
        )
    
    def test_invalid_price_levels(self):
        """Test that invalid price levels raise ValueError."""
        self.assert_error_behavior(
            lambda: query_places(
                query=["restaurants"],
                price_levels=["invalid_level"]
            ),
            ValueError,
            "Invalid price level"
        )
    
    def test_invalid_rank_preference(self):
        """Test that invalid rank preference raises ValueError."""
        self.assert_error_behavior(
            lambda: query_places(
                query=["restaurants"],
                rank_preference="invalid_preference"
            ),
            ValueError,
            "Invalid rank_preference"
        )


class TestLookupPlaceDetails(BaseTestCaseWithErrorHandler):
    """Test cases for the lookup_place_details function."""
    
    @patch('google_maps_live.places.get_gemini_response')
    def test_basic_place_details_lookup(self, mock_gemini):
        """Test basic place details lookup functionality."""
        # Mock Gemini response with proper JSON structure
        mock_gemini.return_value = '''```json
[
  {
    "id": "place_123",
    "name": "Joe's Pizza",
    "description": "Authentic Italian pizza restaurant with wood-fired ovens",
    "rating": "4.2",
    "url": "https://joespizza.com",
    "map_url": "https://maps.google.com/place?q=Joe's+Pizza",
    "review_count": 150,
    "user_rating_count": 200,
    "address": "123 Main St, San Francisco, CA 94102",
    "phone_number": "+1-555-0123",
    "photos": ["https://example.com/photo1.jpg", "https://example.com/photo2.jpg"],
    "opening_hours": ["Monday: 11:00 AM - 10:00 PM", "Tuesday: 11:00 AM - 10:00 PM", "Wednesday: 11:00 AM - 10:00 PM"],
    "distance": "0.5 miles",
    "distance_in_meters": 800
  },
  {
    "id": "place_456",
    "name": "Maria's Cafe",
    "description": "Cozy coffee shop with artisanal pastries and specialty coffee",
    "rating": "4.5",
    "url": "https://mariascafe.com",
    "map_url": "https://maps.google.com/place?q=Maria's+Cafe",
    "review_count": 89,
    "user_rating_count": 120,
    "address": "456 Oak Ave, San Francisco, CA 94103",
    "phone_number": "+1-555-0456",
    "photos": ["https://example.com/photo3.jpg", "https://example.com/photo4.jpg"],
    "opening_hours": ["Monday: 7:00 AM - 8:00 PM", "Tuesday: 7:00 AM - 8:00 PM", "Wednesday: 7:00 AM - 8:00 PM"],
    "distance": "0.8 miles",
    "distance_in_meters": 1280
  }
]
```'''
        
        result = lookup_place_details(place_ids=["place_123", "place_456"])
        
        assert isinstance(result, list)
        assert len(result) == 2
        
        place = result[0]
        assert "id" in place
        assert "name" in place
        assert "description" in place
        assert "rating" in place
        assert "address" in place
        assert "phone_number" in place
        assert "photos" in place
        assert "opening_hours" in place
        assert "distance" in place
        assert "distance_in_meters" in place
    
    @patch('google_maps_live.places.get_gemini_response')
    def test_place_details_with_semantic_query(self, mock_gemini):
        """Test place details lookup with semantic query."""
        # Mock Gemini response with proper JSON structure
        mock_gemini.return_value = '''```json
[
  {
    "id": "place_123",
    "name": "Joe's Pizza",
    "description": "Joe's Pizza has excellent pizza with fresh ingredients. Customers love the authentic taste and generous portions. The restaurant is known for its traditional Italian recipes and friendly service.",
    "rating": "4.2",
    "url": "https://joespizza.com",
    "map_url": "https://maps.google.com/place?q=Joe's+Pizza",
    "review_count": 150,
    "user_rating_count": 200,
    "address": "123 Main St, San Francisco, CA 94102",
    "phone_number": "+1-555-0123",
    "photos": ["https://example.com/photo1.jpg"],
    "opening_hours": ["Monday: 11:00 AM - 10:00 PM"],
    "distance": "0.5 miles",
    "distance_in_meters": 800
  }
]
```'''
        
        result = lookup_place_details(
            place_ids=["place_123"],
            query="reviews about food quality"
        )
        
        assert isinstance(result, list)
        assert len(result) == 1
    
    def test_empty_place_ids_list(self):
        """Test that empty place_ids list raises ValueError."""
        self.assert_error_behavior(
            lambda: lookup_place_details(place_ids=[]),
            ValueError,
            "place_ids list cannot be empty"
        )


class TestAnalyzePlaces(BaseTestCaseWithErrorHandler):
    """Test cases for the analyze_places function."""
    
    @patch('google_maps_live.places.get_model_from_gemini_response')
    def test_basic_place_analysis(self, mock_get_model):
        """Test basic place analysis functionality."""
        # Mock the AnalyzeResult model response
        from google_maps_live.SimulationEngine.models import AnalyzeResult
        
        mock_analyze_result = AnalyzeResult(
            map_answer="Analysis of places: Joe's Pizza offers authentic Italian cuisine with a cozy atmosphere. Maria's Cafe provides excellent coffee and pastries in a modern setting. Both places have great customer service and reasonable prices.",
            web_answers=[
                {
                    "url": "https://example.com/review1",
                    "answer": "Joe's Pizza has been serving authentic Italian cuisine for over 20 years with traditional recipes passed down through generations."
                },
                {
                    "url": "https://example.com/review2",
                    "answer": "Maria's Cafe is known for its artisanal coffee beans and freshly baked pastries made daily in their on-site bakery."
                }
            ]
        )
        mock_get_model.return_value = mock_analyze_result
        
        result = analyze_places(
            place_ids=["place_123", "place_456"],
            question="What are the best features of these places?"
        )
        
        assert isinstance(result, dict)
        assert "map_answer" in result
        assert "web_answers" in result
        
        assert isinstance(result["web_answers"], list)
        assert len(result["web_answers"]) > 0
        
        web_answer = result["web_answers"][0]
        assert "url" in web_answer
        assert "answer" in web_answer
    
    @patch('google_maps_live.places.get_model_from_gemini_response')
    def test_analysis_with_single_place(self, mock_get_model):
        """Test analysis with single place."""
        # Mock the AnalyzeResult model response
        from google_maps_live.SimulationEngine.models import AnalyzeResult
        
        mock_analyze_result = AnalyzeResult(
            map_answer="Joe's Pizza has a warm and welcoming atmosphere with rustic decor, soft lighting, and comfortable seating. The restaurant creates a cozy dining experience perfect for families and casual gatherings.",
            web_answers=[
                {
                    "url": "https://example.com/atmosphere-review",
                    "answer": "The restaurant features exposed brick walls, vintage Italian posters, and ambient lighting that creates an authentic trattoria atmosphere."
                }
            ]
        )
        mock_get_model.return_value = mock_analyze_result
        
        result = analyze_places(
            place_ids=["place_123"],
            question="What is the atmosphere like?"
        )
        
        assert isinstance(result, dict)
        assert "map_answer" in result
    
    def test_empty_place_ids_list(self):
        """Test that empty place_ids list raises ValueError."""
        self.assert_error_behavior(
            lambda: analyze_places(
                place_ids=[],
                question="What are the features?"
            ),
            ValueError,
            "place_ids list cannot be empty"
        )
    
    def test_empty_question(self):
        """Test that empty question raises ValueError."""
        self.assert_error_behavior(
            lambda: analyze_places(
                place_ids=["place_123"],
                question=""
            ),
            ValueError,
            "question cannot be empty"
        )
    
    def test_whitespace_only_question(self):
        """Test that whitespace-only question raises ValueError."""
        self.assert_error_behavior(
            lambda: analyze_places(
                place_ids=["place_123"],
                question="   "
            ),
            ValueError,
            "question cannot be empty"
        )


class TestShowOnMap(BaseTestCaseWithErrorHandler):
    """Test cases for the show_on_map function."""
    
    @patch('google_maps_live.places.get_model_from_gemini_response')
    def test_basic_map_display(self, mock_get_model):
        """Test basic map display functionality."""
        # Mock the ShowMapResult model response
        from google_maps_live.SimulationEngine.models import ShowMapResult
        
        mock_show_map_result = ShowMapResult(
            content_id="map_content_123"
        )
        mock_get_model.return_value = mock_show_map_result
        
        result = show_on_map(places=["place_123", "place_456"])
        
        assert isinstance(result, dict)
        assert "content_id" in result
    
    @patch('google_maps_live.places.get_model_from_gemini_response')
    def test_map_display_with_place_ids(self, mock_get_model):
        """Test map display with place IDs."""
        # Mock the ShowMapResult model response
        from google_maps_live.SimulationEngine.models import ShowMapResult
        
        mock_show_map_result = ShowMapResult(
            content_id="map_content_789"
        )
        mock_get_model.return_value = mock_show_map_result
        
        result = show_on_map(places=["place_id://place_123", "place_id://place_456"])
        
        assert isinstance(result, dict)
        assert "content_id" in result
    
    @patch('google_maps_live.places.get_model_from_gemini_response')
    def test_map_display_with_place_names(self, mock_get_model):
        """Test map display with place names."""
        # Mock the ShowMapResult model response
        from google_maps_live.SimulationEngine.models import ShowMapResult
        
        mock_show_map_result = ShowMapResult(
            content_id="map_content_202"
        )
        mock_get_model.return_value = mock_show_map_result
        
        result = show_on_map(places=["San Francisco, CA", "Mountain View, CA"])
        
        assert isinstance(result, dict)
        assert "content_id" in result
    
    @patch('google_maps_live.places.get_model_from_gemini_response')
    def test_map_display_without_places(self, mock_get_model):
        """Test map display without specifying places."""
        # Mock the ShowMapResult model response
        from google_maps_live.SimulationEngine.models import ShowMapResult
        
        mock_show_map_result = ShowMapResult(
            content_id="map_content_404"
        )
        mock_get_model.return_value = mock_show_map_result
        
        result = show_on_map()
        
        assert isinstance(result, dict)
        assert "content_id" in result
    
    def test_empty_places_list(self):
        """Test that empty places list raises ValueError."""
        self.assert_error_behavior(
            lambda: show_on_map(places=[]),
            ValueError,
            "places list cannot be empty when provided"
        ) 