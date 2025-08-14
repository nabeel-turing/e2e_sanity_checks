from datetime import datetime
import uuid 

from google_slides.SimulationEngine.utils import _ensure_user 
from google_slides.presentations import create_presentation
from google_slides.SimulationEngine.custom_errors import InvalidInputError
from common_utils.base_case import BaseTestCaseWithErrorHandler
from google_slides.SimulationEngine.db import DB

class TestCreatePresentation(BaseTestCaseWithErrorHandler):
    def setUp(self):
        self.DB = DB
        self.DB.clear()
        self.user_id = "me"
        
        # Initialize counters if tests depend on specific starting values for non-UUID counters
        # Ensure the user and their counters dictionary exist before trying to access specific counters
        if 'users' not in self.DB or self.user_id not in self.DB['users'] or 'counters' not in self.DB['users'][self.user_id]:
            _ensure_user(self.user_id)
        else: 
            if 'counters' not in self.DB['users'][self.user_id]:
                 # _ensure_user would have created this, but as a safeguard if user existed partially:
                self.DB['users'][self.user_id]['counters'] = {} 
            
            default_counters_for_test_logic = ['presentation', 'slide', 'pageElement', 'revision']
            for counter_name in default_counters_for_test_logic:
                 if counter_name not in self.DB['users'][self.user_id]['counters']:
                     self.DB['users'][self.user_id]['counters'][counter_name] = 0


    def _validate_uuid(self, id_string, id_name):
        try:
            uuid.UUID(str(id_string)) 
        except ValueError:
            self.fail(f"{id_name} '{id_string}' is not a valid UUID.")
    def _assert_successful_creation(self, response, expected_title):
        self.assertIsInstance(response, dict, "Response should be a dictionary.")

        # Validate presentationId
        self.assertIn("presentationId", response)
        self.assertIsInstance(response["presentationId"], str)
        self._validate_uuid(response["presentationId"], "presentationId")

        # Title should match expected_title
        self.assertIn("title", response)
        self.assertEqual(response["title"], expected_title, "Title does not match expected.")

        # Page size is expected to be None
        self.assertIn("pageSize", response)
        self.assertIsNone(response["pageSize"], "Page size should be None upon creation.")

        # Slides should be an empty list
        self.assertIn("slides", response)
        self.assertIsInstance(response["slides"], list)
        self.assertEqual(len(response["slides"]), 0, "Slides list should be empty.")

        # Masters should be present and empty
        self.assertIn("masters", response)
        self.assertIsInstance(response["masters"], list)
        self.assertEqual(response["masters"], [])

        # Layouts should be present and empty
        self.assertIn("layouts", response)
        self.assertIsInstance(response["layouts"], list)
        self.assertEqual(response["layouts"], [])

        # notesMaster should be None
        self.assertIn("notesMaster", response)
        self.assertIsNone(response["notesMaster"], "notesMaster should be None upon creation.")

        # locale should be None
        self.assertIn("locale", response)
        self.assertIsNone(response["locale"], "locale should be None upon creation.")

        # revisionId should be None
        self.assertIn("revisionId", response)
        self.assertIsInstance(response["revisionId"], str)
        self._validate_uuid(response["revisionId"], "revisionId")

        # Check DB structure
        presentation_id = response["presentationId"]
        self.assertIn(self.user_id, self.DB.get('users', {}), f"User '{self.user_id}' not found in DB.")
        user_data = self.DB['users'][self.user_id]
        self.assertIn('files', user_data, f"User '{self.user_id}' does not have 'files' entry in DB.")
        self.assertIn(presentation_id, user_data['files'], "Presentation not found in user's files in DB.")
        db_presentation_file = user_data['files'][presentation_id]

        self.assertEqual(db_presentation_file.get("id"), presentation_id)
        self.assertEqual(db_presentation_file.get("title"), expected_title)
        self.assertEqual(db_presentation_file.get("mimeType"), "application/vnd.google-apps.presentation")

        for time_field in ["createdTime", "modifiedTime"]:
            self.assertIn(time_field, db_presentation_file)
            self.assertIsInstance(db_presentation_file[time_field], str)
            try:
                datetime.fromisoformat(db_presentation_file[time_field].replace("Z", "+00:00"))
            except ValueError:
                self.fail(f"{time_field} '{db_presentation_file[time_field]}' is not a valid ISO 8601 Z-offset timestamp string.")

    def test_create_presentation_success(self):
        title = "My First Presentation"
        response = create_presentation(title=title)
        self._assert_successful_creation(response, title) 

    def test_create_presentation_with_special_chars_in_title(self):
        title = "Presentation: Test with !@#$%^&*()_+-=[]{};':\",./<>? and unicode "
        response = create_presentation(title=title)
        self._assert_successful_creation(response, title) 

    def test_create_presentation_with_long_valid_title(self):
        title = "a" * 255 
        response = create_presentation(title=title)
        self._assert_successful_creation(response, title) 

    def test_create_presentation_title_with_leading_trailing_spaces(self):
        title_with_spaces = "   My Presentation with Spaces   "
        response = create_presentation(title=title_with_spaces) 
        self._assert_successful_creation(response, title_with_spaces) 

    def test_create_multiple_presentations_success(self):
        title1 = "Presentation One"
        response1 = create_presentation(title=title1)
        self._assert_successful_creation(response1, title1) 

        presentation_id1 = response1["presentationId"]
        self.assertIn(presentation_id1, self.DB['users'][self.user_id]['files'])

        title2 = "Presentation Two"
        response2 = create_presentation(title=title2)
        self._assert_successful_creation(response2, title2)

        presentation_id2 = response2["presentationId"]
        self.assertNotEqual(presentation_id1, presentation_id2, "Presentation IDs should be unique.")
        self.assertIn(presentation_id2, self.DB['users'][self.user_id]['files'])
        self.assertEqual(self.DB['users'][self.user_id]['files'][presentation_id2]['name'], title2)

    def test_create_presentation_with_empty_title_raises_invalid_input(self):
        self.assert_error_behavior(
            func_to_call=create_presentation,
            expected_exception_type=InvalidInputError,
            expected_message="Presentation title cannot be empty or contain only whitespace.", 
            title=""
        )

    def test_create_presentation_with_whitespace_only_title_raises_invalid_input(self):
        self.assert_error_behavior(
            func_to_call=create_presentation,
            expected_exception_type=InvalidInputError,
            expected_message="Presentation title cannot be empty or contain only whitespace.", 
            title="   "
        )

    def test_create_presentation_with_none_title_raises_invalid_input(self):
        self.assert_error_behavior(
            func_to_call=create_presentation,
            expected_exception_type=InvalidInputError, 
            expected_message="Presentation title cannot be empty or contain only whitespace.", 
            title=None
        )