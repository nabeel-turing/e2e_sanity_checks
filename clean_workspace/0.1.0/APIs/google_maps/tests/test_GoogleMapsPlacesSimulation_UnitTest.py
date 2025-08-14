import unittest
import os
import json
import tempfile
import sys
from common_utils.base_case import BaseTestCaseWithErrorHandler

sys.path.append("APIs")

temp_db = {
    "place_empire": {
        "areaSummary": {
            "contentBlocks": [
                {
                    "content": {
                        "text": "An iconic skyscraper in Midtown Manhattan with sweeping city views.",
                        "languageCode": "en",
                    },
                    "flagContentUri": "https://maps.example.com/flag/empireAreaBlock",
                    "topic": "landmark",
                }
            ],
            "flagContentUri": "https://maps.example.com/flag/empireAreaSummary",
        },
        "userRatingCount": 25000,
        "servesBeer": False,
        "businessStatus": "OPERATIONAL",
        "formattedAddress": "20 W 34th St, New York, NY 10001, USA",
        "currentSecondaryOpeningHours": [
            {
                "nextCloseTime": "2025-03-15T23:00:00Z",
                "openNow": True,
                "nextOpenTime": "2025-03-16T09:00:00Z",
                "periods": [
                    {
                        "open": {
                            "day": 1,
                            "hour": 9,
                            "minute": 0,
                            "date": {"year": 2025, "month": 3, "day": 15},
                        },
                        "close": {
                            "day": 1,
                            "hour": 23,
                            "minute": 0,
                            "date": {"year": 2025, "month": 3, "day": 15},
                        },
                    }
                ],
                "specialDays": [],
                "weekdayDescriptions": [
                    "Mon: 09:00–23:00",
                    "Tue: 09:00–23:00",
                    "Wed: 09:00–23:00",
                    "Thu: 09:00–23:00",
                    "Fri: 09:00–23:00",
                    "Sat: 10:00–22:00",
                    "Sun: Closed",
                ],
                "secondaryHoursType": "VISIT",
            }
        ],
        "pureServiceAreaBusiness": False,
        "servesCoffee": False,
        "delivery": False,
        "takeout": False,
        "iconMaskBaseUri": "https://maps.example.com/icons/empire",
        "containingPlaces": [{"name": "Midtown Manhattan", "id": "region_midtown"}],
        "plusCode": {
            "globalCode": "87G8Q2MV+2V",
            "compoundCode": "Q2MV+2V New York, NY",
        },
        "restroom": True,
        "location": {"latitude": 40.748817, "longitude": -73.985428},
        "primaryTypeDisplayName": {"text": "Skyscraper", "languageCode": "en"},
        "utcOffsetMinutes": -300,
        "adrFormatAddress": "ADR: 20 W 34th St, New York, NY 10001, USA",
        "id": "place_empire",
        "evChargeOptions": {"connectorAggregation": [], "connectorCount": 0},
        "googleMapsUri": "https://maps.example.com/place/place_empire",
        "servesBreakfast": False,
        "goodForGroups": True,
        "goodForWatchingSports": False,
        "shortFormattedAddress": "20 W 34th St",
        "liveMusic": False,
        "websiteUri": "https://www.esbnyc.com",
        "photos": [
            {
                "flagContentUri": "https://maps.example.com/flag/empirePhoto1",
                "authorAttributions": [
                    {
                        "displayName": "NYC Photographer",
                        "uri": "https://example.com/nycphotographer",
                        "photoUri": "https://example.com/nycphotographer.jpg",
                    }
                ],
                "googleMapsUri": "https://maps.example.com/photo/empire1",
                "widthPx": 1200,
                "heightPx": 900,
                "name": "places/place_empire/photos/photo_1",
            }
        ],
        "reservable": False,
        "currentOpeningHours": {
            "nextCloseTime": "2025-03-15T23:00:00Z",
            "openNow": True,
            "nextOpenTime": "2025-03-16T09:00:00Z",
            "periods": [
                {
                    "open": {
                        "day": 1,
                        "hour": 9,
                        "minute": 0,
                        "date": {"year": 2025, "month": 3, "day": 15},
                    },
                    "close": {
                        "day": 1,
                        "hour": 23,
                        "minute": 0,
                        "date": {"year": 2025, "month": 3, "day": 15},
                    },
                }
            ],
            "specialDays": [],
            "weekdayDescriptions": [
                "Mon: 09:00–23:00",
                "Tue: 09:00–23:00",
                "Wed: 09:00–23:00",
                "Thu: 09:00–23:00",
                "Fri: 09:00–23:00",
                "Sat: 10:00–22:00",
                "Sun: Closed",
            ],
            "secondaryHoursType": "VISIT",
        },
        "servesVegetarianFood": False,
        "reviews": [
            {
                "googleMapsUri": "https://maps.example.com/review/empire_rev1",
                "authorAttribution": {
                    "displayName": "Travel Guru",
                    "uri": "https://example.com/travelguru",
                    "photoUri": "https://example.com/travelguru.jpg",
                },
                "relativePublishTimeDescription": "3 days ago",
                "publishTime": "2025-03-12T18:00:00Z",
                "flagContentUri": "https://maps.example.com/flag/empire_rev1",
                "rating": 4.7,
                "name": "review_empire_1",
                "text": {
                    "text": "A must-see landmark with incredible views!",
                    "languageCode": "en",
                },
                "originalText": {
                    "text": "A must-see landmark with incredible views!",
                    "languageCode": "en",
                },
            }
        ],
        "servesWine": False,
        "goodForChildren": True,
        "internationalPhoneNumber": "+1 212-736-3100",
        "menuForChildren": False,
        "servesCocktails": False,
        "priceLevel": "PRICE_LEVEL_VERY_EXPENSIVE",
        "timeZone": {"id": "America/New_York", "version": "2023a"},
        "servesDessert": False,
        "addressComponents": [
            {
                "shortText": "NYC",
                "types": ["locality", "political"],
                "languageCode": "en",
                "longText": "New York",
            }
        ],
        "viewport": {
            "low": {"latitude": 40.744, "longitude": -73.990},
            "high": {"latitude": 40.752, "longitude": -73.979},
        },
        "rating": 4.7,
        "iconBackgroundColor": "#000000",
        "servesBrunch": False,
        "priceRange": {
            "startPrice": {"units": "100", "nanos": 0, "currencyCode": "USD"},
            "endPrice": {"units": "300", "nanos": 0, "currencyCode": "USD"},
        },
        "primaryType": "skyscraper",
        "attributions": [
            {"provider": "NYC Gov", "providerUri": "https://www1.nyc.gov"}
        ],
        "regularOpeningHours": {
            "nextCloseTime": "2025-03-15T23:30:00Z",
            "openNow": True,
            "nextOpenTime": "2025-03-16T09:00:00Z",
            "periods": [
                {
                    "open": {
                        "day": 1,
                        "hour": 9,
                        "minute": 0,
                        "date": {"year": 2025, "month": 3, "day": 15},
                    },
                    "close": {
                        "day": 1,
                        "hour": 23,
                        "minute": 30,
                        "date": {"year": 2025, "month": 3, "day": 15},
                    },
                }
            ],
            "specialDays": [],
            "weekdayDescriptions": [
                "Mon: 09:00–23:30",
                "Tue: 09:00–23:30",
                "Wed: 09:00–23:30",
                "Thu: 09:00–23:30",
                "Fri: 09:00–23:30",
                "Sat: 10:00–22:00",
                "Sun: Closed",
            ],
            "secondaryHoursType": "VISIT",
        },
        "allowsDogs": False,
        "outdoorSeating": False,
        "dineIn": False,
        "name": "Empire State Building",
        "parkingOptions": {
            "freeStreetParking": False,
            "paidParkingLot": True,
            "freeGarageParking": False,
            "freeParkingLot": False,
            "paidGarageParking": True,
            "paidStreetParking": True,
            "valetParking": False,
        },
        "curbsidePickup": False,
        "googleMapsLinks": {
            "reviewsUri": "https://maps.example.com/place/place_empire/reviews",
            "writeAReviewUri": "https://maps.example.com/writeareview?place=place_empire",
            "photosUri": "https://maps.example.com/place/place_empire/photos",
            "directionsUri": "https://maps.example.com/directions?destination=place_empire",
            "placeUri": "https://maps.example.com/place/place_empire",
        },
        "servesDinner": False,
        "regularSecondaryOpeningHours": [],
        "editorialSummary": {
            "text": "An iconic landmark offering panoramic views of New York City.",
            "languageCode": "en",
        },
        "paymentOptions": {
            "acceptsNfc": False,
            "acceptsCreditCards": True,
            "acceptsDebitCards": True,
            "acceptsCashOnly": False,
        },
        "generativeSummary": {
            "descriptionFlagContentUri": "https://maps.example.com/flag/genDescEmpire",
            "overviewFlagContentUri": "https://maps.example.com/flag/genOverviewEmpire",
            "description": {
                "text": "A detailed AI-generated description of the Empire State Building.",
                "languageCode": "en",
            },
            "overview": {
                "text": "Panoramic views from one of the world's most famous skyscrapers.",
                "languageCode": "en",
            },
            "references": {"places": ["ref_empire_001"], "reviews": []},
        },
        "fuelOptions": {"fuelPrices": []},
        "accessibilityOptions": {
            "wheelchairAccessibleParking": True,
            "wheelchairAccessibleRestroom": True,
            "wheelchairAccessibleSeating": False,
            "wheelchairAccessibleEntrance": True,
        },
        "types": ["skyscraper", "landmark"],
        "subDestinations": [],
        "displayName": {"text": "Empire State Building", "languageCode": "en-US"},
        "addressDescriptor": {
            "landmarks": [
                {
                    "straightLineDistanceMeters": 100,
                    "types": ["landmark"],
                    "spatialRelationship": "NEAR",
                    "displayName": {"text": "Observation Deck", "languageCode": "en"},
                    "name": "landmark_empire_obs",
                    "placeId": "obs_empire",
                    "travelDistanceMeters": 120,
                }
            ],
            "areas": [
                {
                    "name": "Midtown",
                    "containment": "WITHIN",
                    "displayName": {"text": "Midtown Manhattan", "languageCode": "en"},
                    "placeId": "area_midtown",
                }
            ],
        },
        "servesLunch": False,
        "nationalPhoneNumber": "+1 212-736-3100",
    },
    "place_central": {
        "areaSummary": {
            "contentBlocks": [
                {
                    "content": {
                        "text": "A vast green oasis in the heart of New York City, offering recreational activities and scenic walks.",
                        "languageCode": "en",
                    },
                    "flagContentUri": "https://maps.example.com/flag/centralAreaBlock",
                    "topic": "park",
                }
            ],
            "flagContentUri": "https://maps.example.com/flag/centralAreaSummary",
        },
        "userRatingCount": 12000,
        "servesBeer": False,
        "businessStatus": "OPERATIONAL",
        "formattedAddress": "Central Park, New York, NY, USA",
        "currentSecondaryOpeningHours": [
            {
                "nextCloseTime": "2025-04-01T20:00:00Z",
                "openNow": True,
                "nextOpenTime": "2025-04-01T06:00:00Z",
                "periods": [
                    {
                        "open": {
                            "day": 0,
                            "hour": 6,
                            "minute": 0,
                            "date": {"year": 2025, "month": 4, "day": 1},
                        },
                        "close": {
                            "day": 0,
                            "hour": 20,
                            "minute": 0,
                            "date": {"year": 2025, "month": 4, "day": 1},
                        },
                    }
                ],
                "specialDays": [],
                "weekdayDescriptions": [
                    "Sun: 06:00–20:00",
                    "Mon: 06:00–20:00",
                    "Tue: 06:00–20:00",
                    "Wed: 06:00–20:00",
                    "Thu: 06:00–20:00",
                    "Fri: 06:00–20:00",
                    "Sat: 06:00–20:00",
                ],
                "secondaryHoursType": "VISIT",
            }
        ],
        "pureServiceAreaBusiness": False,
        "servesCoffee": True,
        "delivery": False,
        "takeout": False,
        "iconMaskBaseUri": "https://maps.example.com/icons/centralpark",
        "containingPlaces": [{"name": "Manhattan", "id": "region_manhattan"}],
        "plusCode": {
            "globalCode": "87G8Q8QX+2V",
            "compoundCode": "8QX+2V New York, NY",
        },
        "restroom": True,
        "location": {"latitude": 40.7829, "longitude": -73.9654},
        "primaryTypeDisplayName": {"text": "Park", "languageCode": "en"},
        "utcOffsetMinutes": -300,
        "adrFormatAddress": "Central Park, New York, NY, USA",
        "id": "place_central",
        "evChargeOptions": {"connectorAggregation": [], "connectorCount": 0},
        "googleMapsUri": "https://maps.example.com/place/place_central",
        "servesBreakfast": False,
        "goodForGroups": True,
        "goodForWatchingSports": True,
        "shortFormattedAddress": "Central Park",
        "liveMusic": True,
        "websiteUri": "https://www.centralparknyc.org",
        "photos": [
            {
                "flagContentUri": "https://maps.example.com/flag/centralPhoto1",
                "authorAttributions": [
                    {
                        "displayName": "Park Photographer",
                        "uri": "https://example.com/parkphotog",
                        "photoUri": "https://example.com/parkphotog.jpg",
                    }
                ],
                "googleMapsUri": "https://maps.example.com/photo/central1",
                "widthPx": 1024,
                "heightPx": 768,
                "name": "places/place_central/photos/photo_1",
            }
        ],
        "reservable": False,
        "currentOpeningHours": {
            "nextCloseTime": "2025-04-01T20:00:00Z",
            "openNow": True,
            "nextOpenTime": "2025-04-01T06:00:00Z",
            "periods": [
                {
                    "open": {
                        "day": 0,
                        "hour": 6,
                        "minute": 0,
                        "date": {"year": 2025, "month": 4, "day": 1},
                    },
                    "close": {
                        "day": 0,
                        "hour": 20,
                        "minute": 0,
                        "date": {"year": 2025, "month": 4, "day": 1},
                    },
                }
            ],
            "specialDays": [],
            "weekdayDescriptions": [
                "Sun: 06:00–20:00",
                "Mon: 06:00–20:00",
                "Tue: 06:00–20:00",
                "Wed: 06:00–20:00",
                "Thu: 06:00–20:00",
                "Fri: 06:00–20:00",
                "Sat: 06:00–20:00",
            ],
            "secondaryHoursType": "VISIT",
        },
        "servesVegetarianFood": True,
        "reviews": [
            {
                "googleMapsUri": "https://maps.example.com/review/central_rev1",
                "authorAttribution": {
                    "displayName": "Local Critic",
                    "uri": "https://example.com/localcritic",
                    "photoUri": "https://example.com/localcritic.jpg",
                },
                "relativePublishTimeDescription": "5 hours ago",
                "publishTime": "2025-04-01T16:00:00Z",
                "flagContentUri": "https://maps.example.com/flag/central_rev1",
                "rating": 4.3,
                "name": "review_central_1",
                "text": {
                    "text": "A serene escape in the midst of the city hustle.",
                    "languageCode": "en",
                },
                "originalText": {
                    "text": "A serene escape in the midst of the city hustle.",
                    "languageCode": "en",
                },
            }
        ],
        "servesWine": False,
        "goodForChildren": True,
        "internationalPhoneNumber": "+1 212-310-6600",
        "menuForChildren": False,
        "servesCocktails": False,
        "priceLevel": "PRICE_LEVEL_FREE",
        "timeZone": {"id": "America/New_York", "version": "2023a"},
        "servesDessert": False,
        "addressComponents": [
            {
                "shortText": "NY",
                "types": ["locality", "political"],
                "languageCode": "en",
                "longText": "New York",
            }
        ],
        "viewport": {
            "low": {"latitude": 40.771, "longitude": -73.981},
            "high": {"latitude": 40.796, "longitude": -73.949},
        },
        "rating": 4.3,
        "iconBackgroundColor": "#76A5AF",
        "servesBrunch": False,
        "priceRange": {
            "startPrice": {"units": "0", "nanos": 0, "currencyCode": "USD"},
            "endPrice": {"units": "0", "nanos": 0, "currencyCode": "USD"},
        },
        "primaryType": "park",
        "attributions": [
            {"provider": "NYC Parks", "providerUri": "https://www.nycgovparks.org"}
        ],
        "regularOpeningHours": {
            "nextCloseTime": "2025-04-01T20:30:00Z",
            "openNow": True,
            "nextOpenTime": "2025-04-01T06:00:00Z",
            "periods": [
                {
                    "open": {
                        "day": 0,
                        "hour": 6,
                        "minute": 0,
                        "date": {"year": 2025, "month": 4, "day": 1},
                    },
                    "close": {
                        "day": 0,
                        "hour": 20,
                        "minute": 30,
                        "date": {"year": 2025, "month": 4, "day": 1},
                    },
                }
            ],
            "specialDays": [],
            "weekdayDescriptions": [
                "Sun: 06:00–20:30",
                "Mon: 06:00–20:30",
                "Tue: 06:00–20:30",
                "Wed: 06:00–20:30",
                "Thu: 06:00–20:30",
                "Fri: 06:00–20:30",
                "Sat: 06:00–20:30",
            ],
            "secondaryHoursType": "VISIT",
        },
        "allowsDogs": True,
        "outdoorSeating": True,
        "dineIn": False,
        "name": "Central Park",
        "parkingOptions": {
            "freeStreetParking": True,
            "paidParkingLot": False,
            "freeGarageParking": False,
            "freeParkingLot": True,
            "paidGarageParking": False,
            "paidStreetParking": False,
            "valetParking": False,
        },
        "curbsidePickup": False,
        "googleMapsLinks": {
            "reviewsUri": "https://maps.example.com/place/place_central/reviews",
            "writeAReviewUri": "https://maps.example.com/writeareview?place=place_central",
            "photosUri": "https://maps.example.com/place/place_central/photos",
            "directionsUri": "https://maps.example.com/directions?destination=place_central",
            "placeUri": "https://maps.example.com/place/place_central",
        },
        "servesDinner": False,
        "regularSecondaryOpeningHours": [],
        "editorialSummary": {
            "text": "A vast green sanctuary amidst the concrete jungle, ideal for leisure and recreation.",
            "languageCode": "en",
        },
        "paymentOptions": {
            "acceptsNfc": False,
            "acceptsCreditCards": False,
            "acceptsDebitCards": False,
            "acceptsCashOnly": True,
        },
        "generativeSummary": {
            "descriptionFlagContentUri": "https://maps.example.com/flag/genDescCentral",
            "overviewFlagContentUri": "https://maps.example.com/flag/genOverviewCentral",
            "description": {
                "text": "An AI-generated detailed description of Central Park.",
                "languageCode": "en",
            },
            "overview": {
                "text": "A peaceful retreat offering scenic views and recreational activities.",
                "languageCode": "en",
            },
            "references": {"places": ["ref_central_001"], "reviews": []},
        },
        "fuelOptions": {"fuelPrices": []},
        "accessibilityOptions": {
            "wheelchairAccessibleParking": True,
            "wheelchairAccessibleRestroom": True,
            "wheelchairAccessibleSeating": True,
            "wheelchairAccessibleEntrance": True,
        },
        "types": ["park", "landmark"],
        "subDestinations": [],
        "displayName": {"text": "Central Park", "languageCode": "en-US"},
        "addressDescriptor": {
            "landmarks": [
                {
                    "straightLineDistanceMeters": 150.0,
                    "types": ["landmark"],
                    "spatialRelationship": "NEAR",
                    "displayName": {"text": "Bethesda Terrace", "languageCode": "en"},
                    "name": "landmark_central_1",
                    "placeId": "lm_central_1",
                    "travelDistanceMeters": 200.0,
                }
            ],
            "areas": [
                {
                    "name": "Manhattan",
                    "containment": "WITHIN",
                    "displayName": {"text": "Manhattan", "languageCode": "en"},
                    "placeId": "area_manhattan",
                }
            ],
        },
        "servesLunch": False,
        "nationalPhoneNumber": "+1 212-310-6600",
    },
}


import google_maps as GoogleMapsPlacesAPI


class TestGoogleMapsSaveLoadState(BaseTestCaseWithErrorHandler):
    """
    Tests for GoogleMaps.save_state and load_state.
    """

    def setUp(self):
        GoogleMapsPlacesAPI.SimulationEngine.db.DB.clear()
        GoogleMapsPlacesAPI.SimulationEngine.db.DB.update(temp_db)

    def test_save_and_load_state(self):
        # 1) Save the current DB to a temp file
        # with tempfile.NamedTemporaryFile(delete=False) as tmp:
        #     tmp_path = tmp.name
        tmp_path = "test_db.json"
        try:
            GoogleMapsPlacesAPI.save_state(tmp_path)
            # 2) Modify DB in-memory (simulate changes)
            original_db = GoogleMapsPlacesAPI.DB
            GoogleMapsPlacesAPI.SimulationEngine.db.DB = {}  # Clear the global DB

            # 3) Load from the temp file
            GoogleMapsPlacesAPI.load_state(tmp_path)

            # 4) Ensure DB is restored
            self.assertEqual(
                len(GoogleMapsPlacesAPI.SimulationEngine.db.DB), len(original_db)
            )
        finally:
            # Cleanup the temp file
            os.remove(tmp_path)


class TestPlacesCreatePlace(BaseTestCaseWithErrorHandler):
    """
    Tests for Places._create_place.
    Covers creation success, missing 'id', and duplicate 'id'.
    """

    def setUp(self):
        # Save original DB before each test
        GoogleMapsPlacesAPI.SimulationEngine.db.DB.clear()
        GoogleMapsPlacesAPI.SimulationEngine.db.DB.update(temp_db)

    def tearDown(self):
        # Restore DB after each test
        GoogleMapsPlacesAPI.SimulationEngine.db.DB.clear()
        GoogleMapsPlacesAPI.SimulationEngine.db.DB.update(temp_db)

    def test_create_place_success(self):
        new_place = {
            "id": "test_place_new",
            "name": "A Newly Created Place",
            "primaryType": "store",
        }
        created = GoogleMapsPlacesAPI.utils._create_place(new_place)
        place = GoogleMapsPlacesAPI.Places.get(name="places/test_place_new")
        self.assertEqual(place["id"], "test_place_new")

    def test_create_place_missing_id(self):
        place_data = {
            # intentionally no "id"
            "name": "Missing ID Place"
        }
        with self.assertRaises(ValueError):
            GoogleMapsPlacesAPI.utils._create_place(place_data)

    def test_create_place_duplicate_id(self):
        # "place_empire" is already in DB by default
        duplicate_place = {"id": "place_empire", "name": "Duplicate Place"}
        with self.assertRaises(ValueError):
            GoogleMapsPlacesAPI.utils._create_place(duplicate_place)


class TestPlacesAutocomplete(BaseTestCaseWithErrorHandler):
    """
    Ensure autocomplete lines are covered. We'll also temporarily transform DB
    so that DB.get(...) returns a dict.
    """

    def setUp(self):
        GoogleMapsPlacesAPI.SimulationEngine.db.DB.clear()
        GoogleMapsPlacesAPI.SimulationEngine.db.DB.update(temp_db)

    def tearDown(self):
        GoogleMapsPlacesAPI.SimulationEngine.db.DB.clear()
        GoogleMapsPlacesAPI.SimulationEngine.db.DB.update(temp_db)

    def test_autocomplete_dummy(self):
        # Transform DB from a list to a dict *just for coverage*.
        # Once the method runs, we revert it back.
        request_data = {"query": "emp"}
        response = GoogleMapsPlacesAPI.Places.autocomplete(request_data)
        self.assertIsInstance(response, dict)


class TestPlacesGet(BaseTestCaseWithErrorHandler):
    """
    Covers 'get' method with optional parameters, invalid resource, non-existent place.
    """

    def setUp(self):
        GoogleMapsPlacesAPI.SimulationEngine.db.DB.clear()
        GoogleMapsPlacesAPI.SimulationEngine.db.DB.update(temp_db)

    def test_get_valid_places(self):
        empire = GoogleMapsPlacesAPI.Places.get("places/place_empire")
        self.assertIsNotNone(empire)
        self.assertEqual(empire["id"], "place_empire")

        central = GoogleMapsPlacesAPI.Places.get("places/place_central")
        self.assertIsNotNone(central)
        self.assertEqual(central["id"], "place_central")

    def test_get_invalid_resource(self):
        with self.assertRaises(ValueError):
            GoogleMapsPlacesAPI.Places.get("invalid/place_empire")

    def test_get_non_existent_place(self):
        # resource name format is correct, but ID does not exist
        place = GoogleMapsPlacesAPI.Places.get("places/non_existent")
        self.assertIsNone(place)

    def test_get_with_optional_params(self):
        # Just to ensure lines referencing languageCode, sessionToken, regionCode are covered
        place = GoogleMapsPlacesAPI.Places.get(
            name="places/place_empire",
            languageCode="en",
            sessionToken="dummy",
            regionCode="US",
        )
        self.assertIsNotNone(place)
        self.assertEqual(place["id"], "place_empire")


class TestPlacesSearchNearby(BaseTestCaseWithErrorHandler):
    """
    Tests for searchNearby. Covers various filters, including unsupported.
    """

    def setUp(self):
        GoogleMapsPlacesAPI.SimulationEngine.db.DB.clear()
        GoogleMapsPlacesAPI.SimulationEngine.db.DB.update(temp_db)

    def test_search_nearby_basic_circle(self):
        request = {
            "maxResultCount": 10,
            "locationRestriction": {
                "circle": {
                    "center": {"latitude": 40.748817, "longitude": -73.985428},
                    "radius": 50,  # 50 meters
                }
            },
        }
        result = GoogleMapsPlacesAPI.Places.searchNearby(request)
        self.assertIn("places", result)
        self.assertEqual(len(result["places"]), 1)
        self.assertEqual(result["places"][0]["id"], "place_empire")

    def test_search_nearby_no_circle(self):
        request = {"maxResultCount": 10, "locationRestriction": {}}
        result = GoogleMapsPlacesAPI.Places.searchNearby(request)
        self.assertIn("places", result)
        # Should return both places by default
        self.assertGreaterEqual(len(result["places"]), 2)

    def test_search_nearby_included_excluded_primary_types(self):
        request = {
            "includedPrimaryTypes": ["skyscraper"],
            "excludedPrimaryTypes": ["park"],
            "locationRestriction": {
                "circle": {
                    "center": {"latitude": 40.0, "longitude": -74.0},
                    "radius": 10_000_000,
                }
            },
        }
        result = GoogleMapsPlacesAPI.Places.searchNearby(request)
        self.assertEqual(len(result["places"]), 1)
        self.assertEqual(result["places"][0]["id"], "place_empire")

    def test_search_nearby_included_excluded_types(self):
        request = {
            "includedTypes": ["landmark"],
            "excludedTypes": ["park"],
            "locationRestriction": {
                "circle": {
                    "center": {"latitude": 40.0, "longitude": -74.0},
                    "radius": 10_000_000,
                }
            },
        }
        result = GoogleMapsPlacesAPI.Places.searchNearby(request)
        # Empire is "skyscraper, landmark"
        # Central is "park, landmark"
        # We exclude "park" => exclude central
        self.assertEqual(len(result["places"]), 1)
        self.assertEqual(result["places"][0]["id"], "place_empire")

    def test_search_nearby_language_code_mismatch(self):
        request = {
            "languageCode": "ja",
            "locationRestriction": {
                "circle": {
                    "center": {"latitude": 40.0, "longitude": -74.0},
                    "radius": 10_000_000,
                }
            },
        }
        result = GoogleMapsPlacesAPI.Places.searchNearby(request)
        self.assertEqual(len(result["places"]), 0)

    def test_search_nearby_unsupported_params(self):
        # regionCode, rankPreference, routingParameters are not fully supported
        request = {
            "locationRestriction": {
                "circle": {
                    "center": {"latitude": 40.0, "longitude": -74.0},
                    "radius": 9999999,
                }
            },
            "regionCode": "US",
            "rankPreference": "DISTANCE",
            "routingParameters": {"travelMode": "DRIVING"},
        }
        result = GoogleMapsPlacesAPI.Places.searchNearby(request)
        self.assertIn("places", result)


class TestPlacesSearchText(BaseTestCaseWithErrorHandler):
    """
    Tests for searchText. Covers textQuery, priceLevels, openNow, minRating, locationRestriction, etc.
    """

    def setUp(self):
        GoogleMapsPlacesAPI.SimulationEngine.db.DB.clear()
        GoogleMapsPlacesAPI.SimulationEngine.db.DB.update(temp_db)

    def tearDown(self):
        GoogleMapsPlacesAPI.SimulationEngine.db.DB.clear()
        GoogleMapsPlacesAPI.SimulationEngine.db.DB.update(temp_db)

    def test_search_text_empty_query_raises(self):
        request = {"textQuery": ""}
        with self.assertRaises(ValueError):
            GoogleMapsPlacesAPI.Places.searchText(request)

    def test_search_text_basic(self):
        request = {"textQuery": "central park"}
        result = GoogleMapsPlacesAPI.Places.searchText(request)
        found_ids = [p["id"] for p in result["places"]]
        self.assertIn("place_central", found_ids)

    def test_search_text_strict_type_filtering(self):
        request = {
            "textQuery": "new york",
            "strictTypeFiltering": True,
            "includedType": "skyscraper",
        }
        result = GoogleMapsPlacesAPI.Places.searchText(request)
        self.assertEqual(len(result["places"]), 1)
        self.assertEqual(result["places"][0]["id"], "place_empire")

    def test_search_text_price_levels(self):
        request = {"textQuery": "new york", "priceLevels": ["PRICE_LEVEL_FREE"]}
        # "place_central" is PRICE_LEVEL_FREE, empire is PRICE_LEVEL_VERY_EXPENSIVE
        result = GoogleMapsPlacesAPI.Places.searchText(request)
        self.assertEqual(len(result["places"]), 1)
        self.assertEqual(result["places"][0]["id"], "place_central")

    def test_search_text_open_now(self):
        request = {"textQuery": "new york", "openNow": True}
        result = GoogleMapsPlacesAPI.Places.searchText(request)
        # Both are openNow from the sample data => expect 2
        self.assertIn("places", result)
        self.assertGreaterEqual(len(result["places"]), 2)

    def test_search_text_min_rating(self):
        request = {"textQuery": "new york", "minRating": 4.5}
        # empire=4.7, central=4.3 => only empire passes
        result = GoogleMapsPlacesAPI.Places.searchText(request)
        self.assertEqual(len(result["places"]), 1)
        self.assertEqual(result["places"][0]["id"], "place_empire")

    def test_search_text_exclude_pure_service_area_businesses(self):
        # Mark central as pure service area => exclude it
        GoogleMapsPlacesAPI.DB["place_central"]["pureServiceAreaBusiness"] = True

        request = {"textQuery": "central", "includePureServiceAreaBusinesses": False}
        result = GoogleMapsPlacesAPI.Places.searchText(request)
        self.assertEqual(len(result["places"]), 0)

    def test_search_text_location_restriction_no_location(self):
        # Remove empire's location to skip it
        GoogleMapsPlacesAPI.DB["place_empire"]["location"] = {}

        request = {
            "textQuery": "empire",
            "locationRestriction": {
                "circle": {
                    "center": {"latitude": 40.748817, "longitude": -73.985428},
                    "radius": 100,
                }
            },
        }
        result = GoogleMapsPlacesAPI.Places.searchText(request)
        self.assertEqual(len(result["places"]), 0)

    def test_search_text_language_code_mismatch(self):
        request = {"textQuery": "new york", "languageCode": "ja"}
        result = GoogleMapsPlacesAPI.Places.searchText(request)
        self.assertEqual(len(result["places"]), 0)

    def test_search_text_unsupported_params(self):
        # regionCode, rankPreference, searchAlongRouteParameters, evOptions, routingParameters
        request = {
            "textQuery": "empire",
            "regionCode": "US",
            "rankPreference": "DISTANCE",
            "searchAlongRouteParameters": {"route": "whatever"},
            "evOptions": {"isEvFriendly": True},
            "routingParameters": {"travelMode": "DRIVING"},
        }
        result = GoogleMapsPlacesAPI.Places.searchText(request)
        self.assertIn("places", result)


class TestPlacesPhotos(BaseTestCaseWithErrorHandler):
    """
    Tests for Photos.getMedia.
    """

    def setUp(self):
        GoogleMapsPlacesAPI.SimulationEngine.db.DB.clear()
        GoogleMapsPlacesAPI.SimulationEngine.db.DB.update(temp_db)

    def test_get_media_valid(self):
        media = GoogleMapsPlacesAPI.Places.Photos.getMedia(
            "places/place_empire/photos/photo_1/media", maxWidthPx=400
        )
        self.assertIsInstance(media, list)
        self.assertGreater(len(media), 0)
        self.assertIn("w400", media[0]["photoUri"])

    def test_get_media_invalid_pattern(self):
        with self.assertRaises(ValueError):
            GoogleMapsPlacesAPI.Places.Photos.getMedia(
                "invalid/resource/media", maxWidthPx=400
            )

    def test_get_media_no_dimensions(self):
        with self.assertRaises(ValueError):
            GoogleMapsPlacesAPI.Places.Photos.getMedia(
                "places/place_empire/photos/photo_1/media"
            )

    def test_get_media_too_few_parts(self):
        with self.assertRaises(ValueError):
            GoogleMapsPlacesAPI.Places.Photos.getMedia(
                "places/place_empire/photos/photo_1", maxWidthPx=400
            )

    def test_get_media_max_height(self):
        media = GoogleMapsPlacesAPI.Places.Photos.getMedia(
            "places/place_empire/photos/photo_1/media", maxHeightPx=600
        )
        self.assertIsInstance(media, list)
        self.assertGreater(len(media), 0)
        self.assertIn("h600", media[0]["photoUri"])

    def test_get_media_skip_http_redirect_true(self):
        media = GoogleMapsPlacesAPI.Places.Photos.getMedia(
            "places/place_empire/photos/photo_1/media",
            maxWidthPx=400,
            skipHttpRedirect=True,
        )
        self.assertTrue(len(media) > 0)
        # The skipHttpRedirect param doesn't change the result,
        # but now it's covered.
