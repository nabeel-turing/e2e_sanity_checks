import unittest
import copy
from datetime import datetime, timezone # Ensure timezone is imported for datetime objects
import uuid # Import uuid for generating actual UUIDs if needed in setup/tests

# Assuming these are correctly located relative to your test execution path
from google_slides.presentations import batch_update_presentation 
from google_slides.SimulationEngine import utils # For _ensure_user if needed
from google_slides.SimulationEngine import custom_errors
from common_utils.base_case import BaseTestCaseWithErrorHandler
from google_slides.SimulationEngine.db import DB
from google_slides.SimulationEngine import models # For Pydantic models if used in setup
from google_slides.SimulationEngine.db import DB
from google_slides.SimulationEngine.models import *
from google_slides.SimulationEngine.custom_errors import *

# class TestBatchUpdatePresentation(BaseTestCaseWithErrorHandler):
#     def setUp(self):
#         self._original_DB_state = copy.deepcopy(DB)
#         DB.clear()

#         self.user_id = "me"
#         self.presentation_id = "pres_1_uuid" # Using a more UUID-like string, or generate actual UUID
#         self.initial_revision_id = "rev_initial_pres_1" # Initial revision ID for the presentation
#         self.default_layout_id = "layout_blank_canonical_id"
#         self.default_master_id = "master_default_canonical_id"

#         # Ensure user structure, including counters, is initialized
#         utils._ensure_user(self.user_id) # This will set up DB['users']['me'] with counters etc.

#         # Define the detailed presentation data (slides_data)
#         slides_data_content = {
#             "presentationId": self.presentation_id,
#             "title": "Test Presentation 1",
#             "slides": [
#                 {
#                     "objectId": "slide_1_1_uuid", # Make IDs more UUID like for consistency if validating
#                     "pageType": "SLIDE",
#                     "slideProperties": {"layoutObjectId": self.default_layout_id, "masterObjectId": self.default_master_id, "isSkipped": False},
#                     "notesPage": {
#                         "objectId": "notes_page_s1_1_uuid",
#                         "pageType": "NOTES_PAGE",
#                         "notesPageProperties": {"speakerNotesObjectId": "speaker_notes_s1_1_uuid"},
#                         "pageElements": [{
#                             "objectId": "speaker_notes_s1_1_uuid",
#                             "shape": {"shapeType": "TEXT_BOX", 
#                                       "text": {"textElements": [
#                                           models.TextElement(startIndex=0, endIndex=20, textRun=models.TextRun(content="Initial speaker notes.", style=models.TextStyle())).model_dump()
#                                           # Adding paragraph marker for completeness if text exists
#                                           ,models.TextElement(startIndex=20, endIndex=21, paragraphMarker=models.TextElement(style={})).model_dump()

#                                       ]}},
#                             "size": models.Size(width=models.Dimension(magnitude=400, unit="PT"), height=models.Dimension(magnitude=100, unit="PT")).model_dump(),
#                             "transform": models.AffineTransform(translateX=0, translateY=0, scaleX=1, scaleY=1, unit="PT").model_dump()
#                         }],
#                         "revisionId": "rev_notes_s1_1" 
#                     },
#                     "pageElements": [
#                         {
#                             "objectId": "shape_1_1_1_uuid",
#                             "shape": {
#                                 "shapeType": "TEXT_BOX",
#                                 "text": {"textElements": [
#                                     models.TextElement(startIndex=0, endIndex=11, textRun=models.TextRun(content="Hello World", style=models.TextStyle())).model_dump(),
#                                     models.TextElement(startIndex=11, endIndex=12, paragraphMarker=models.TextElement(style={})).model_dump()
#                                 ]}
#                             },
#                             "size": models.Size(width=models.Dimension(magnitude=100, unit="PT"), height=models.Dimension(magnitude=50, unit="PT")).model_dump(),
#                             "transform": models.AffineTransform(translateX=10, translateY=10, scaleX=1, scaleY=1, unit="PT").model_dump(),
#                             "altText": {"title": "", "description": ""}
#                         },
#                         {
#                             "objectId": "shape_1_1_2_uuid",
#                             "shape": {"shapeType": "RECTANGLE"},
#                             "size": models.Size(width=models.Dimension(magnitude=70, unit="PT"), height=models.Dimension(magnitude=70, unit="PT")).model_dump(),
#                             "transform": models.AffineTransform(translateX=150, translateY=10, scaleX=1, scaleY=1, unit="PT").model_dump(),
#                             "altText": {"title": "", "description": ""}
#                         }
#                     ],
#                     "revisionId": "rev_slide_1_1_initial"
#                 },
#                 {
#                     "objectId": "slide_1_2_uuid",
#                     "pageType": "SLIDE",
#                     "slideProperties": {"layoutObjectId": self.default_layout_id, "masterObjectId": self.default_master_id, "isSkipped": False},
#                     "pageElements": [],
#                     "revisionId": "rev_slide_1_2_initial"
#                 }
#             ],
#             "pageSize": models.Size(width=models.Dimension(magnitude=9144000, unit="EMU"), height=models.Dimension(magnitude=5143500, unit="EMU")).model_dump(),
#             "masters": [models.Master(objectId=self.default_master_id, displayName="Default Master", revisionId="rev_master_default").model_dump()],
#             "layouts": [models.Layout(objectId=self.default_layout_id, displayName="Blank Layout", revisionId="rev_layout_blank").model_dump()],
#             "revisionId": self.initial_revision_id,
#             "createTime": "2023-01-01T00:00:00Z",
#             "updateTime": "2023-01-01T00:00:00Z"
#         }

#         # Create the GDrive file entry for the presentation
#         DB['users'][self.user_id]['files'][self.presentation_id] = {
#             "id": self.presentation_id,
#             "name": slides_data_content["title"],
#             "mimeType": "application/vnd.google-apps.presentation",
#             "createdTime": slides_data_content["createTime"],
#             "modifiedTime": slides_data_content["updateTime"],
#             "version": slides_data_content["revisionId"], # GDrive version can be Slides revisionId
#             "slides_data": slides_data_content # Embed the detailed presentation model here
#         }
        
#         # Remove the separate DB['presentations'] if it exists, to avoid confusion
#         if 'presentations' in DB:
#             DB.pop('presentations', None)

#         # Update self attributes to point to correct IDs from the setup
#         self.slide_1_id = slides_data_content['slides'][0]['objectId']
#         self.shape_1_id = slides_data_content['slides'][0]['pageElements'][0]['objectId']
#         self.shape_2_id = slides_data_content['slides'][0]['pageElements'][1]['objectId']
#         self.layout_blank_id = slides_data_content['layouts'][0]['objectId']


#     def tearDown(self):
#         DB.clear()
#         DB.update(self._original_DB_state) # Restore original DB state if needed

#     def test_invalid_presentation_id_type(self):
#         self.assert_error_behavior(
#             batch_update_presentation, 
#             custom_errors.InvalidInputError,
#             expected_message="Presentation ID must be a string.",
#             presentationId=123, 
#             requests=[]
#         )

#     def test_presentation_not_found(self):
#         self.assert_error_behavior(
#             batch_update_presentation, 
#             custom_errors.NotFoundError,
#             expected_message="Presentation with ID 'non_existent_pres' not found or is not a presentation.",
#             presentationId="non_existent_pres", 
#             requests=[]
#         )

#     def test_invalid_requests_type_not_list(self):
#         self.assert_error_behavior(
#             batch_update_presentation, 
#             custom_errors.InvalidInputError, # Actual function raises this
#             expected_message="Requests payload must be a list.",
#             presentationId=self.presentation_id, 
#             requests="not_a_list" # type: ignore
#         )

#     def test_requests_item_not_dict(self):
#         self.assert_error_behavior(
#             batch_update_presentation, 
#             custom_errors.InvalidInputError,
#             expected_message="Request at index 0 is malformed: must be a dictionary with a single key.",
#             presentationId=self.presentation_id, 
#             requests=["not_a_dict"]
#         )

#     def test_requests_item_empty_dict(self):
#         self.assert_error_behavior(
#             batch_update_presentation, 
#             custom_errors.InvalidInputError,
#             expected_message="Request at index 0 is malformed: must be a dictionary with a single key.",
#             presentationId=self.presentation_id, 
#             requests=[{}]
#         )

#     def test_requests_item_multiple_keys(self):
#         self.assert_error_behavior(
#             batch_update_presentation, 
#             custom_errors.InvalidInputError,
#             expected_message="Request at index 0 is malformed: must be a dictionary with a single key.",
#             presentationId=self.presentation_id, 
#             requests=[{"createSlide": {}, "createShape": {}}]
#         )

#     def test_requests_item_unknown_request_type(self):
#         self.assert_error_behavior(
#             batch_update_presentation, 
#             custom_errors.InvalidInputError,
#             expected_message="Unsupported request type: 'unknownRequest' at index 0.",
#             presentationId=self.presentation_id, 
#             requests=[{"unknownRequest": {}}]
#         )

#     def test_empty_requests_list_is_noop(self):
#         response = batch_update_presentation(presentationId=self.presentation_id, requests=[])
#         self.assertEqual(response['presentationId'], self.presentation_id)
#         self.assertEqual(response['replies'], [])
#         self.assertNotEqual(response['writeControl']['requiredRevisionId'], self.initial_revision_id)
#         # Access slides_data within the file entry
#         self.assertEqual(DB['users'][self.user_id]['files'][self.presentation_id]['slides_data']['revisionId'], response['writeControl']['requiredRevisionId'])

#     def test_invalid_write_control_type(self):
#          # Pydantic model WriteControlRequest expects a dict. Passing string.
#         self.assert_error_behavior(
#             batch_update_presentation, 
#             custom_errors.InvalidInputError, # Wrapped by main func
#             # The exact Pydantic message might vary, check for a part of it.
#             # expected_message="Input should be a valid dictionary", # Example
#             presentationId=self.presentation_id, 
#             requests=[], 
#             writeControl="not_a_dict" # type: ignore
#         )
    
#     # This test might need adjustment based on how Pydantic handles unknown keys
#     # It might not raise an error if WriteControlRequest allows extra fields.
#     # If it should error, the Pydantic model needs `model_config = ConfigDict(extra='forbid')`
#     # For now, assuming it might pass through if not strictly forbidden by Pydantic model.
#     # The current InvalidInputError in batch_update_presentation for writeControl is generic.
#     # def test_invalid_write_control_content_bad_key(self):
#     #     self.assert_error_behavior(
#     #         batch_update_presentation, custom_errors.InvalidInputError,
#     #         presentationId=self.presentation_id, requests=[], writeControl={"badKey": "value"}
#     #     )

#     def test_concurrency_error_required_revision_id_mismatch(self):
#         self.assert_error_behavior(
#             batch_update_presentation, 
#             custom_errors.ConcurrencyError,
#             expected_message=f"Required revision ID 'wrong_revision_id' does not match current revision ID '{self.initial_revision_id}'.",
#             presentationId=self.presentation_id, 
#             requests=[],
#             writeControl={"requiredRevisionId": "wrong_revision_id"}
#         )

#     def test_success_with_matching_required_revision_id(self):
#         response = batch_update_presentation(
#             presentationId=self.presentation_id, 
#             requests=[], # Empty requests list, but writeControl is valid
#             writeControl={"requiredRevisionId": self.initial_revision_id}
#         )
#         self.assertEqual(response['presentationId'], self.presentation_id)
#         self.assertNotEqual(response['writeControl']['requiredRevisionId'], self.initial_revision_id)

#     # --- CreateSlideRequest Tests ---
#     def test_create_slide_minimal_success(self):
#         requests = [{"createSlide": {}}]
#         response = batch_update_presentation(self.presentation_id, requests)
#         self.assertEqual(len(response['replies']), 1)
#         self.assertIn('createSlide', response['replies'][0])
#         new_slide_id = response['replies'][0]['createSlide']['objectId']
#         presentation_data = DB['users'][self.user_id]['files'][self.presentation_id]['slides_data']
#         self.assertEqual(len(presentation_data['slides']), 3) # Was 2, now 3
#         self.assertTrue(any(s['objectId'] == new_slide_id for s in presentation_data['slides']))

#     def test_create_slide_with_object_id_success(self):
#         custom_slide_id = str(uuid.uuid4()) # Use a UUID
#         requests = [{"createSlide": {"objectId": custom_slide_id}}]
#         response = batch_update_presentation(self.presentation_id, requests)
#         self.assertEqual(response['replies'][0]['createSlide']['objectId'], custom_slide_id)

#     def test_create_slide_with_insertion_index_success(self):
#         requests = [{"createSlide": {"insertionIndex": 0}}]
#         response = batch_update_presentation(self.presentation_id, requests)
#         new_slide_id = response['replies'][0]['createSlide']['objectId']
#         self.assertEqual(DB['users'][self.user_id]['files'][self.presentation_id]['slides_data']['slides'][0]['objectId'], new_slide_id)

#     def test_create_slide_with_layout_id_success(self):
#         requests = [{"createSlide": {"slideLayoutReference": {"layoutId": self.layout_blank_id}}}]
#         response = batch_update_presentation(self.presentation_id, requests)
#         new_slide_id = response['replies'][0]['createSlide']['objectId']
#         new_slide = next(s for s in DB['users'][self.user_id]['files'][self.presentation_id]['slides_data']['slides'] if s['objectId'] == new_slide_id)
#         self.assertEqual(new_slide['slideProperties']['layoutObjectId'], self.layout_blank_id)
    
#     # --- CreateShapeRequest Tests ---
#     def test_create_shape_minimal_text_box_success(self):
#         requests = [{"createShape": {"shapeType": "TEXT_BOX", "elementProperties": {"pageObjectId": self.slide_1_id}}}]
#         response = batch_update_presentation(self.presentation_id, requests)
#         self.assertIn('createShape', response['replies'][0])
#         new_shape_id = response['replies'][0]['createShape']['objectId']
#         slide = next(s for s in DB['users'][self.user_id]['files'][self.presentation_id]['slides_data']['slides'] if s['objectId'] == self.slide_1_id)
#         self.assertTrue(any(el['objectId'] == new_shape_id for el in slide['pageElements']))

#     def test_create_shape_on_non_existent_slide(self):
#         self.assert_error_behavior(
#             batch_update_presentation, 
#             custom_errors.NotFoundError, # Handler raises NotFoundError if page not found
#             expected_message="Page with ID 'non_existent_slide_id' not found for creating shape.",
#             presentationId=self.presentation_id,
#             requests=[{"createShape": {"shapeType": "RECTANGLE", "elementProperties": {"pageObjectId": "non_existent_slide_id"}}}]
#         )

#     # --- InsertTextRequest Tests ---
#     def test_insert_text_success(self):
#         requests = [{"insertText": {"objectId": self.shape_1_id, "text": " New Text", "insertionIndex": 5}}]
#         batch_update_presentation(self.presentation_id, requests)
#         slide_data = DB['users'][self.user_id]['files'][self.presentation_id]['slides_data']['slides'][0]
#         shape = next(el for el in slide_data['pageElements'] if el['objectId'] == self.shape_1_id)
#         self.assertEqual(shape['shape']['text']['textElements'][0]['textRun']['content'], "Hello New Text")

#     def test_insert_text_to_non_existent_object_id(self):
#         self.assert_error_behavior(
#             batch_update_presentation, 
#             custom_errors.NotFoundError, # Handler raises NotFoundError
#             expected_message="Object with ID 'non_existent_shape' not found for InsertTextRequest.",
#             presentationId=self.presentation_id,
#             requests=[{"insertText": {"objectId": "non_existent_shape", "text": "t"}}]
#         )

#     # --- ReplaceAllTextRequest Tests ---
#     def test_replace_all_text_success(self):
#         requests = [{"replaceAllText": {"containsText": {"text": "Hello"}, "replaceText": "Greetings"}}]
#         response = batch_update_presentation(self.presentation_id, requests)
#         self.assertIn('replaceAllText', response['replies'][0])
#         self.assertGreaterEqual(response['replies'][0]['replaceAllText'].get('occurrencesChanged', 0), 1)
#         slide_data = DB['users'][self.user_id]['files'][self.presentation_id]['slides_data']['slides'][0]
#         shape1 = next(el for el in slide_data['pageElements'] if el['objectId'] == self.shape_1_id)
#         self.assertEqual(shape1['shape']['text']['textElements'][0]['textRun']['content'], "Greetings World")

#     # --- DeleteObjectRequest Tests ---
#     def test_delete_object_shape_success(self):
#         slide_data = DB['users'][self.user_id]['files'][self.presentation_id]['slides_data']['slides'][0]
#         initial_count = len(slide_data['pageElements'])
#         requests = [{"deleteObject": {"objectId": self.shape_1_id}}]
#         batch_update_presentation(self.presentation_id, requests)
#         # Re-fetch slide_data as it might have been modified
#         updated_slide_data = DB['users'][self.user_id]['files'][self.presentation_id]['slides_data']['slides'][0]
#         self.assertEqual(len(updated_slide_data['pageElements']), initial_count - 1)

#     def test_delete_object_slide_success(self):
#         initial_count = len(DB['users'][self.user_id]['files'][self.presentation_id]['slides_data']['slides'])
#         requests = [{"deleteObject": {"objectId": self.slide_1_id}}]
#         batch_update_presentation(self.presentation_id, requests)
#         self.assertEqual(len(DB['users'][self.user_id]['files'][self.presentation_id]['slides_data']['slides']), initial_count - 1)

#     # --- DeleteTextRequest Tests ---
#     def test_delete_text_fixed_range_success(self):
#         # Initial text in shape_1_id is "Hello World"
#         requests = [{"deleteText": {"objectId": self.shape_1_id, "textRange": {"type": "FIXED_RANGE", "startIndex": 0, "endIndex": 6}}}] # Deletes "Hello "
#         batch_update_presentation(self.presentation_id, requests)
#         slide_data = DB['users'][self.user_id]['files'][self.presentation_id]['slides_data']['slides'][0]
#         shape = next(el for el in slide_data['pageElements'] if el['objectId'] == self.shape_1_id)
#         self.assertEqual(shape['shape']['text']['textElements'][0]['textRun']['content'], "World")

#     # --- DuplicateObjectRequest Tests ---
#     def test_duplicate_object_shape_success(self):
#         slide_data = DB['users'][self.user_id]['files'][self.presentation_id]['slides_data']['slides'][0]
#         initial_count = len(slide_data['pageElements'])
#         requests = [{"duplicateObject": {"objectId": self.shape_1_id}}]
#         response = batch_update_presentation(self.presentation_id, requests)
#         self.assertIn('duplicateObject', response['replies'][0])
#         self.assertIn('objectId', response['replies'][0]['duplicateObject'])
#         # Re-fetch slide_data
#         updated_slide_data = DB['users'][self.user_id]['files'][self.presentation_id]['slides_data']['slides'][0]
#         self.assertEqual(len(updated_slide_data['pageElements']), initial_count + 1)

#     # --- UpdateTextStyleRequest Tests ---
#     def test_update_text_style_bold_success(self):
#         requests = [{"updateTextStyle": {"objectId": self.shape_1_id, 
#                                          "style": {"bold": True}, 
#                                          "textRange": {"type": "ALL"}, 
#                                          "fields": "bold"}}]
#         batch_update_presentation(self.presentation_id, requests)
#         slide_data = DB['users'][self.user_id]['files'][self.presentation_id]['slides_data']['slides'][0]
#         shape = next(el for el in slide_data['pageElements'] if el['objectId'] == self.shape_1_id)
#         style = shape['shape']['text']['textElements'][0]['textRun']['style']
#         self.assertTrue(style['bold'])

#     def test_update_text_style_star_fields_success(self):
#         requests = [{"updateTextStyle": {"objectId": self.shape_1_id, 
#                                          "style": {"italic": True, "underline": True}, 
#                                          "textRange": {"type": "ALL"}, 
#                                          "fields": "*"}}]
#         batch_update_presentation(self.presentation_id, requests) # This was the failing test
#         slide_data = DB['users'][self.user_id]['files'][self.presentation_id]['slides_data']['slides'][0]
#         shape = next(el for el in slide_data['pageElements'] if el['objectId'] == self.shape_1_id)
#         style = shape['shape']['text']['textElements'][0]['textRun']['style']
#         self.assertTrue(style['italic'])
#         self.assertTrue(style['underline'])

#     # --- GroupObjectsRequest Tests ---
#     def test_group_objects_success(self):
#         children_ids = [self.shape_1_id, self.shape_2_id]
#         custom_group_id = "myGroupObj_uuid" # Use a UUID like string or generate one
#         requests = [{"groupObjects": {"childrenObjectIds": children_ids, "groupObjectId": custom_group_id}}]
#         response = batch_update_presentation(self.presentation_id, requests)
#         self.assertIn('groupObjects', response['replies'][0])
#         self.assertEqual(response['replies'][0]['groupObjects']['objectId'], custom_group_id)
#         slide_data = DB['users'][self.user_id]['files'][self.presentation_id]['slides_data']['slides'][0]
#         self.assertTrue(any(el['objectId'] == custom_group_id and 'group' in el for el in slide_data['pageElements']))
#         self.assertFalse(any(el['objectId'] == self.shape_1_id for el in slide_data['pageElements'])) # Original shapes removed from page list

#     def test_group_objects_too_few_children(self):
#          # Assuming the Pydantic model GroupObjectsRequestParams enforces min_length=2 for childrenObjectIds
#         self.assert_error_behavior(
#             batch_update_presentation, 
#             custom_errors.InvalidInputError, # Wrapper should catch Pydantic validation
#             presentationId=self.presentation_id,
#             requests=[{"groupObjects": {"childrenObjectIds": [self.shape_1_id]}}] 
#         )

#     # --- UngroupObjectsRequest Tests ---
#     def test_ungroup_objects_success(self):
#         group_id = "groupToUngroup_uuid"
#         slide_data = DB['users'][self.user_id]['files'][self.presentation_id]['slides_data']['slides'][0]
        
#         # Create a group for testing ungroup
#         original_children = [
#             next(el for el in slide_data['pageElements'] if el['objectId'] == self.shape_1_id),
#             next(el for el in slide_data['pageElements'] if el['objectId'] == self.shape_2_id)
#         ]
#         slide_data['pageElements'] = [el for el in slide_data['pageElements'] if el['objectId'] not in [self.shape_1_id, self.shape_2_id]]
#         slide_data['pageElements'].append({"objectId": group_id, "group": {"children": copy.deepcopy(original_children)}})
        
#         requests = [{"ungroupObjects": {"objectIds": [group_id]}}]
#         batch_update_presentation(self.presentation_id, requests)
        
#         updated_slide_data = DB['users'][self.user_id]['files'][self.presentation_id]['slides_data']['slides'][0]
#         self.assertFalse(any(el['objectId'] == group_id for el in updated_slide_data['pageElements']))
#         self.assertTrue(any(el['objectId'] == self.shape_1_id for el in updated_slide_data['pageElements']))
#         self.assertTrue(any(el['objectId'] == self.shape_2_id for el in updated_slide_data['pageElements']))

#     # --- UpdatePageElementAltTextRequest Tests ---
#     def test_update_page_element_alt_text_success(self):
#         requests = [{"updatePageElementAltText": {"objectId": self.shape_1_id, "title": "New Alt Title"}}]
#         batch_update_presentation(self.presentation_id, requests)
#         slide_data = DB['users'][self.user_id]['files'][self.presentation_id]['slides_data']['slides'][0]
#         shape = next(el for el in slide_data['pageElements'] if el['objectId'] == self.shape_1_id)
#         self.assertEqual(shape['altText']['title'], "New Alt Title")

#     # --- UpdateSlidePropertiesRequest Tests ---
#     def test_update_slide_properties_is_skipped_success(self):
#         requests = [{"updateSlideProperties": {"objectId": self.slide_1_id, 
#                                              "slideProperties": {"isSkipped": True}, 
#                                              "fields": "isSkipped"}}] # Corrected field path for Pydantic
#         batch_update_presentation(self.presentation_id, requests)
#         slide_data = DB['users'][self.user_id]['files'][self.presentation_id]['slides_data']['slides'][0]
#         self.assertTrue(slide_data['slideProperties']['isSkipped'])

#     def test_update_slide_properties_notes_page_speaker_notes_object_id_success(self):
#         new_speaker_notes_obj_id = "new_speaker_notes_obj_id_test_uuid" # speaker_notes_s1_1_uuid
#         existing_notes_page_data = DB['users'][self.user_id]['files'][self.presentation_id]['slides_data']['slides'][0].get('notesPage', {})
        
#         notes_page_payload_for_update = {
#             "objectId": existing_notes_page_data.get("objectId", "notes_page_s1_1_uuid_fallback"), # ID of the notes page
#             "pageType": "NOTES",
#             "pageElements": existing_notes_page_data.get("pageElements", []), # Preserve existing elements or send empty
#             "revisionId": existing_notes_page_data.get("revisionId", "rev_notes_s1_1_fallback"), # Current revision of notes page
#             "pageProperties": existing_notes_page_data.get("pageProperties", {"pageBackgroundFill": {}}), # Preserve or default
#             "notesProperties": { # This is where speakerNotesObjectId lives in the Page model when pageType is NOTES
#                 "speakerNotesObjectId": new_speaker_notes_obj_id
#             }
#         }

#         requests = [{"updateSlideProperties": {
#             "objectId": self.slide_1_id, # ID of the slide whose properties are being updated
#             "slideProperties": { # This is SlidePropertiesUpdatePayload
#                 "notesPage": notes_page_payload_for_update # Provide the valid Page structure for notesPage
#             },
#             "fields": "notesPage.notesProperties.speakerNotesObjectId" # Corrected field mask path
#         }}]

#         batch_update_presentation(self.presentation_id, requests)
        
#         # Verify the change in the canonical location
#         slide_data = DB['users'][self.user_id]['files'][self.presentation_id]['slides_data']['slides'][0]
#         self.assertIsNotNone(slide_data.get("notesPage"), "Slide should have a notesPage.")
#         self.assertIsNotNone(slide_data["notesPage"].get("notesPageProperties"), "notesPage should have notesPageProperties.")
#         self.assertEqual(slide_data['notesPage']['notesPageProperties']['speakerNotesObjectId'], new_speaker_notes_obj_id)

#     # --- Multiple Requests & Atomicity ---
#     def test_multiple_requests_success_and_order(self):
#         new_slide_id = "batch_slide_001_uuid"
#         new_shape_id = "batch_shape_001_uuid"
#         requests = [
#             {"createSlide": {"objectId": new_slide_id, "insertionIndex": 0}},
#             {"createShape": {"objectId": new_shape_id, "shapeType": "ELLIPSE", "elementProperties": {"pageObjectId": new_slide_id}}},
#             {"insertText": {"objectId": new_shape_id, "text": "Batch Text"}}
#         ]
#         response = batch_update_presentation(self.presentation_id, requests)
#         self.assertEqual(len(response['replies']), 3)
#         self.assertEqual(response['replies'][0]['createSlide']['objectId'], new_slide_id)
#         self.assertEqual(response['replies'][1]['createShape']['objectId'], new_shape_id)
#         # Assuming insertText returns empty reply or specific one per API
#         self.assertIn('insertText', response['replies'][2]) # Or check for specific reply structure
        
#         presentation_slides_data = DB['users'][self.user_id]['files'][self.presentation_id]['slides_data']
#         self.assertEqual(presentation_slides_data['slides'][0]['objectId'], new_slide_id)
#         new_shape_data = presentation_slides_data['slides'][0]['pageElements'][0]
#         self.assertEqual(new_shape_data['objectId'], new_shape_id)
#         self.assertEqual(new_shape_data['shape']['text']['textElements'][0]['textRun']['content'], "Batch Text")

#     def test_batch_with_one_failing_request_rolls_back(self):
#         # Ensure the presentation exists from setUp
#         self.assertIn(self.presentation_id, DB['users'][self.user_id]['files'])
#         self.assertIn('slides_data', DB['users'][self.user_id]['files'][self.presentation_id])

#         # Capture the state of 'slides_data' *before* the batch_update call
#         expected_slides_data_after_rollback = copy.deepcopy(
#             DB['users'][self.user_id]['files'][self.presentation_id]['slides_data']
#         )
#         # Also capture the initial number of slides for a more specific check
#         initial_slide_count_in_slides_data = len(expected_slides_data_after_rollback.get('slides', []))

#         requests = [
#             {"createSlide": {"objectId": "batch_slide_ok_atomic_uuid"}}, # This should be rolled back
#             {"insertText": {"objectId": "non_existent_shape_atomic", "text": "fail"}} # This request will fail
#         ]

#         self.assert_error_behavior(
#             batch_update_presentation, 
#             custom_errors.NotFoundError, 
#             expected_message="Object with ID 'non_existent_shape_atomic' not found for InsertTextRequest.",
#             presentationId=self.presentation_id, 
#             requests=requests
#         )
        
#         # Verify atomicity: presentation state should be rolled back
#         # Re-fetch the current state from DB after the call
#         current_presentation_file_entry = DB['users'][self.user_id]['files'].get(self.presentation_id)
#         self.assertIsNotNone(current_presentation_file_entry, "Presentation file entry should still exist.")
        
#         current_slides_data = current_presentation_file_entry.get('slides_data')
#         self.assertIsNotNone(current_slides_data, "'slides_data' should still exist in the presentation entry.")
        
#         # 1. Check if the number of slides reverted (if createSlide was processed before error)
#         self.assertEqual(len(current_slides_data.get('slides', [])), initial_slide_count_in_slides_data, 
#                          "Number of slides should be rolled back to the count before this batch_update call.")
        
#         # 2. Check that the slide intended to be created is not there
#         self.assertFalse(
#             any(s.get('objectId') == "batch_slide_ok_atomic_uuid" for s in current_slides_data.get('slides', [])),
#             "Atomic slide creation (batch_slide_ok_atomic_uuid) should be rolled back and not present."
#         )
        
#         # 3. Compare the entire slides_data object to its state before the failing call
#         self.assertEqual(current_slides_data, expected_slides_data_after_rollback, 
#                          "Entire presentation slides_data should be rolled back to its state immediately before this batch_update call.")
        


class TestBatchUpdatePresentation(BaseTestCaseWithErrorHandler):
    def setUp(self):
        self.maxDiff = None
        text_style = TextElement(textRun=TextRun(content="Hello World", style=TextStyle(fontFamily="abc", fontSize=Dimension(magnitude=12.0, unit="PT"), bold=True))).model_dump(mode="json" )
        DB.clear()
        DB.update({
            "users": {
            "me": {
                "about": {
                "kind": "drive#about",
                "storageQuota": {
                    "limit": "0",
                    "usageInDrive": "0",
                    "usageInDriveTrash": "0",
                    "usage": "0"
                },
                "driveThemes": False,
                "canCreateDrives": False,
                "importFormats": {},
                "exportFormats": {},
                "appInstalled": False,
                "user": {
                    "displayName": "",
                    "kind": "drive#user",
                    "me": True,
                    "permissionId": "",
                    "emailAddress": ""
                },
                "folderColorPalette": "",
                "maxImportSizes": {},
                "maxUploadSize": "0"
                },
                "files": {
                "pres1": {
                    "id": "pres1",
                    "driveId": "My-Drive-ID",
                    "name": "Test Presentation 1",
                    "mimeType": "application/vnd.google-apps.presentation",
                    "createdTime": "2025-03-01T10:00:00Z",
                    "modifiedTime": "2025-03-10T10:00:00Z",
                    "trashed": False,
                    "starred": False,
                    "parents": [
                    "drive-1"
                    ],
                    "owners": [
                    "john.doe@gmail.com"
                    ],
                    "size": "102400",
                    "permissions": [
                    {
                        "id": "permission-1",
                        "role": "owner",
                        "type": "user",
                        "emailAddress": "john.doe@gmail.com"
                    }
                    ],
                    "presentationId": "pres1",
                    "title": "Test Presentation 1",
                    "slides": [
                    {
                        "objectId": "slide1_page1",
                        "pageType": "SLIDE",
                        "pageProperties": {
                        "backgroundColor": {
                            "opaqueColor": {
                            "rgbColor": {
                                "red": 1.0,
                                "green": 0.0,
                                "blue": 0.0
                            },
                            "themeColor": None
                            }
                        }
                        },
                        "slideProperties": {
                        "masterObjectId": "master1",
                        "layoutObjectId": "layout_for_slide1"
                        },
                        "pageElements": [
                        {
                            "objectId": "element1_slide1",
                            "title": "Element 1",
                            "description": "Element 1 description",
                            "size": {
                            "width": {
                                "magnitude": 200,
                                "unit": "PT"
                            },
                            "height": {
                                "magnitude": 100,
                                "unit": "PT"
                            }
                            },
                            "transform": {
                            "scaleX": 1.0,
                            "translateY": 50.0
                            },
                            "shape": {
                            "shapeType": "RECTANGLE",
                            "text": {'textElements' : [text_style]}
                            }
                        },
                        {
                            "objectId": "element2_slide1_text",
                            "size": {
                            "width": {
                                "magnitude": 300,
                                "unit": "PT"
                            },
                            "height": {
                                "magnitude": 150,
                                "unit": "PT"
                            }
                            },
                            "transform": {
                            "scaleX": 1.0,
                            "translateY": 200.0
                            },
                            "shape": {
                            "shapeType": "TEXT_BOX",
                            "text": {
                                "textElements": [
                                {
                                    "textRun": {
                                    "content": "Hello ",
                                    "style": {
                                        "fontFamily": "Calibri",
                                        "fontSize": {
                                        "magnitude": 12,
                                        "unit": "PT"
                                        }
                                    }
                                    }
                                },
                                {
                                    "textRun": {
                                    "content": "World!",
                                    "style": {
                                        "fontFamily": "Times New Roman",
                                        "fontSize": {
                                        "magnitude": 14,
                                        "unit": "PT"
                                        }
                                    }
                                    }
                                }
                                ]
                            }
                            }
                        }
                        ],
                        "revisionId": "rev_slide1"
                    },
                    ],
                    "masters": [
                    {
                        "objectId": "master_new1",
                        "pageType": "MASTER",
                        "pageProperties": {
                        "backgroundColor": {
                            "opaqueColor": {
                            "rgbColor": {
                                "red": 0.95,
                                "green": 0.95,
                                "blue": 0.95
                            }
                            }
                        }
                        },
                        "masterProperties": {
                        "displayName": "Master Title Placeholder"
                        },
                        "pageElements": [
                        {
                            "objectId": "master_textbox1",
                            "size": {
                            "width": {
                                "magnitude": 400,
                                "unit": "PT"
                            },
                            "height": {
                                "magnitude": 100,
                                "unit": "PT"
                            }
                            },
                            "transform": {
                            "scaleX": 1.0,
                            "scaleY": 1.0,
                            "translateX": 50.0,
                            "translateY": 50.0,
                            "unit": "PT"
                            },
                            "shape": {
                            "shapeType": "TEXT_BOX",
                            "text": {
                                "textElements": [
                                {
                                    "textRun": {
                                    "content": "Master Title Placeholder",
                                    "style": {
                                        "fontFamily": "Arial",
                                        "fontSize": {
                                        "magnitude": 24,
                                        "unit": "PT"
                                        },
                                        "bold": True
                                    }
                                    }
                                }
                                ]
                            }
                            }
                        }
                        ],
                        "revisionId": "rev_master_new1"
                    }
                    ],
                    "layouts": [
                    {
                        "objectId": "layout_basic_title_content",
                        "pageType": "LAYOUT",
                        "layoutProperties": {"displayName": "Basic Title and Content"},
                        "pageProperties": {
                        "backgroundColor": {
                            "opaqueColor": {
                            "rgbColor": {
                                "red": 1.0,
                                "green": 1.0,
                                "blue": 1.0
                            }
                            }
                        }
                        },
                        "pageElements": [
                        {
                            "objectId": "title_placeholder_layout",
                            "size": {
                            "width": {
                                "magnitude": 500,
                                "unit": "PT"
                            },
                            "height": {
                                "magnitude": 60,
                                "unit": "PT"
                            }
                            },
                            "transform": {
                            "scaleX": 1.0,
                            "scaleY": 1.0,
                            "translateX": 40.0,
                            "translateY": 40.0,
                            "unit": "PT"
                            },
                            "shape": {
                            "shapeType": "TEXT_BOX"
                            }
                        },
                        {
                            "objectId": "body_placeholder_layout",
                            "size": {
                            "width": {
                                "magnitude": 500,
                                "unit": "PT"
                            },
                            "height": {
                                "magnitude": 300,
                                "unit": "PT"
                            }
                            },
                            "transform": {
                            "scaleX": 1.0,
                            "scaleY": 1.0,
                            "translateX": 40.0,
                            "translateY": 120.0,
                            "unit": "PT"
                            },
                            "shape": {
                            "shapeType": "TEXT_BOX"
                            }
                        }
                        ],
                        "revisionId": "rev_layout_basic"
                    }
                    ],
                    "pageSize": {
                    "width": {
                        "magnitude": 9144000,
                        "unit": "EMU"
                    },
                    "height": {
                        "magnitude": 5143500,
                        "unit": "EMU"
                    }
                    },
                    "locale": "",
                    "notesMaster": [
                    {
                        "objectId": "notes_master1",
                        "pageType": "NOTES_MASTER",
                        "pageProperties": {
                        "backgroundColor": {
                            "opaqueColor": {
                            "rgbColor": {
                                "red": 0.98,
                                "green": 0.98,
                                "blue": 0.98
                            }
                            }
                        }
                        },
                        "pageElements": [
                        {
                            "objectId": "slide_image_placeholder",
                            "size": {
                            "width": {
                                "magnitude": 400,
                                "unit": "PT"
                            },
                            "height": {
                                "magnitude": 300,
                                "unit": "PT"
                            }
                            },
                            "transform": {
                            "scaleX": 1.0,
                            "scaleY": 1.0,
                            "translateX": 50.0,
                            "translateY": 50.0,
                            "unit": "PT"
                            },
                            "shape": {
                            "shapeType": "RECTANGLE"
                            },
                            "placeholder": {
                            "type": "SLIDE_IMAGE",
                            "index": 0
                            }
                        },
                        {
                            "objectId": "body_placeholder_notes",
                            "size": {
                            "width": {
                                "magnitude": 500,
                                "unit": "PT"
                            },
                            "height": {
                                "magnitude": 150,
                                "unit": "PT"
                            }
                            },
                            "transform": {
                            "scaleX": 1.0,
                            "scaleY": 1.0,
                            "translateX": 50.0,
                            "translateY": 400.0,
                            "unit": "PT"
                            },
                            "shape": {
                            "shapeType": "TEXT_BOX"
                            },
                            "placeholder": {
                            "type": "BODY",
                            "index": 0
                            }
                        }
                        ],
                        "revisionId": "rev_notes_master1"
                    }
                    ],
                    "revisionId": "rev_pres1",
                    "notesMaster": {
                        "objectId": "notes_master1",
                        "pageType": "NOTES_MASTER",
                        "pageProperties": {
                        "backgroundColor": {
                            "opaqueColor": {
                            "rgbColor": {
                                "red": 0.98,
                                "green": 0.98,
                                "blue": 0.98
                            }
                            }
                        }
                        },
                        "pageElements": [],
                        "revisionId": "rev_notes_master1"
                        
                    }

                }
                }
            },
            "drives": {},
            "comments": {},
            "replies": {},
            "labels": {},
            "accessproposals": {},
            "counters": {
                "file": 0,
                "drive": 0,
                "comment": 0,
                "reply": 0,
                "label": 0,
                "accessproposal": 0,
                "revision": 0
            }
            }
        })

    def test_create_slide(self):
        request = CreateSlideRequestModel(
        createSlide=CreateSlideRequestParams(
            objectId="slide1_page3",
            insertionIndex=0
            )
        ).model_dump(mode='json')


        batch_update_presentation(
            presentationId="pres1",
            requests=[
                request
                ]
        )

        assert DB['users']['me']['files']['pres1']['slides'][0]['objectId'] == 'slide1_page3'

    
    def test_group_objects(self):
        batch_update_presentation(
            presentationId="pres1",
            requests=[
                GroupObjectsRequestModel(
                    groupObjects=GroupObjectsRequestParams(
                        groupObjectId="grouped_elements_slide",
                        childrenObjectIds=["element2_slide1_text", "element1_slide1"]
                    )
                ).model_dump(mode="json")

                ]
            )

        assert any(element['objectId'] == 'grouped_elements_slide' for element in DB['users']['me']['files']['pres1']['slides'][0]['pageElements'])
        for element in DB['users']['me']['files']['pres1']['slides'][0]['pageElements']:
            if element['objectId'] == 'grouped_elements_slide':
                for child in element['elementGroup']['children']:
                    assert child['objectId'] in ['element2_slide1_text', 'element1_slide1']

    def test_ungroup_objects(self):
        batch_update_presentation(
            presentationId="pres1",
            requests=[
                GroupObjectsRequestModel(
                    groupObjects=GroupObjectsRequestParams(
                        groupObjectId="grouped_elements_slide",
                        childrenObjectIds=["element2_slide1_text", "element1_slide1"]
                    )
                ).model_dump(mode="json")

                ]
            )
        
        batch_update_presentation(
            presentationId="pres1",
            requests=[
                UngroupObjectsRequestModel(
                    ungroupObjects=UngroupObjectsRequestParams(
                        objectIds=["element1_slide1"]
                    )
                ).model_dump(mode="json")
                ]
            )

        assert any(element['objectId'] == 'element1_slide1' for element in DB['users']['me']['files']['pres1']['slides'][0]['pageElements'])

    def test_create_shape(self):
        request = CreateShapeRequestModel(
                        createShape=CreateShapeRequestParams(
                            objectId="element2_slide1_page1",
                            shapeType="TEXT_BOX",
                            elementProperties=PageElementProperties(
                                pageObjectId="slide1_page1",
                                size=Size(
                                    width=Dimension(
                                        magnitude=1000,
                                        unit="PT"
                                    ),
                                transform=AffineTransform(
                                    scaleX=1.0,
                                    scaleY=1.0,
                                    translateX=0.0,
                                    translateY=0.0,
                                    unit="PT"
                                )
                            )
                        )
                        )
                    ).model_dump(mode="json")

        batch_update_presentation(
            presentationId="pres1",
            requests=[request]
        )

        assert any(element['objectId'] == 'element2_slide1_page1' for element in DB['users']['me']['files']['pres1']['slides'][0]['pageElements'])
        for element in DB['users']['me']['files']['pres1']['slides'][0]['pageElements']:
            if element['objectId'] == 'element2_slide1_page1':
                assert element['shape']['shapeType'] == 'TEXT_BOX'

    def test_insert_text(self):
        request_shape = CreateShapeRequestModel(
                        createShape=CreateShapeRequestParams(
                            objectId="element2_slide1_page1",
                            shapeType="TEXT_BOX",
                            elementProperties=PageElementProperties(
                                pageObjectId="slide1_page1",
                                size=Size(
                                    width=Dimension(
                                        magnitude=1000,
                                        unit="PT"
                                    ),
                                transform=AffineTransform(
                                    scaleX=1.0,
                                    scaleY=1.0,
                                    translateX=0.0,
                                    translateY=0.0,
                                    unit="PT"
                                )
                            )
                        )
                        )
                    ).model_dump(mode="json")
        request_text = InsertTextRequestModel(
            insertText=InsertTextRequestParams(
                objectId="element2_slide1_page1",
                text="Hello",
            )
            ).model_dump(mode="json")

        batch_update_presentation(
            presentationId="pres1",
            requests=[request_shape, request_text]
        )

        for element in DB['users']['me']['files']['pres1']['slides'][0]['pageElements']:
            if element['objectId'] == 'element2_slide1_page1':
                assert element['shape']['text']['textElements'][0]['textRun']['content'] == 'Hello'

    def test_replace_all_text(self):
        request = ReplaceAllTextRequestModel(
                replaceAllText=ReplaceAllTextRequestParams(
                    pageObjectIds=["slide1_page1"],
                    replaceText="abc",
                    containsText=SubstringMatchCriteria(
                        text="Hello",
                        matchCase=True,
                        matchWholeString=True
                    )
                )
            ).model_dump(mode="json")

        batch_update_presentation(
                presentationId="pres1",
                requests=[request]
            )
        
        hello_count = 0
        for element in DB['users']['me']['files']['pres1']['slides'][0]['pageElements']:
            for text_element in element['shape']['text']['textElements']:
                if 'Hello' in text_element['textRun']['content']:
                    hello_count += 1

        assert hello_count == 0

    def test_delete_text(self):
        request_shape = CreateShapeRequestModel(
                createShape=CreateShapeRequestParams(
                    objectId="element2_slide1_page1",
                    shapeType="TEXT_BOX",
                    elementProperties=PageElementProperties(
                        pageObjectId="slide1_page1",
                        size=Size(
                            width=Dimension(
                                magnitude=1000,
                                unit="PT"
                            ),
                        transform=AffineTransform(
                            scaleX=1.0,
                            scaleY=1.0,
                            translateX=0.0,
                            translateY=0.0,
                            unit="PT"
                        )
                    )
                )
                )
            ).model_dump(mode="json")
        
        request_insert_text = InsertTextRequestModel(
            insertText=InsertTextRequestParams(
                objectId="element2_slide1_page1",
                text="Hello",
            )
            ).model_dump(mode="json")

        request_delete_text = DeleteTextRequestModel(
            deleteText=DeleteTextRequestParams(
                objectId="element2_slide1_page1",
                textRange=Range(
                    startIndex=0,
                    endIndex=5,
                    type="FIXED_RANGE"
                )
            )
        ).model_dump(mode="json")

        batch_update_presentation(
            presentationId="pres1",
            requests=[request_shape, request_insert_text, request_delete_text]
        )

        # for element in DB['users']['me']['files']['pres1']['slides'][0]['pageElements']:
        #     if element['objectId'] == 'element2_slide1_page1':
        #         assert element['text']['textElements'][0]['textRun']['content'] == ''

    def test_delete_object(self):

        request_create_shape = CreateShapeRequestModel(
                        createShape=CreateShapeRequestParams(
                            objectId="element2_slide1_page1",
                            shapeType="TEXT_BOX",
                            elementProperties=PageElementProperties(
                                pageObjectId="slide1_page1",
                                size=Size(
                                    width=Dimension(
                                        magnitude=1000,
                                        unit="PT"
                                    ),
                                transform=AffineTransform(
                                    scaleX=1.0,
                                    scaleY=1.0,
                                    translateX=0.0,
                                    translateY=0.0,
                                    unit="PT"
                                )
                            )
                        )
                        )
                    ).model_dump(mode="json")

        request_delete = DeleteObjectRequestModel(
            deleteObject=DeleteObjectRequestParams(
                objectId="element2_slide1_page1"
            )
        ).model_dump(mode="json")

        batch_update_presentation(
            presentationId="pres1",
            requests=[request_create_shape, request_delete]
        )

        assert not any(element['objectId'] == 'element2_slide1_page1' for element in DB['users']['me']['files']['pres1']['slides'][0]['pageElements'])

    def test_update_alt_text(self):

        request = UpdatePageElementAltTextRequestModel(
            updatePageElementAltText=UpdatePageElementAltTextRequestParams(
                objectId="element1_slide1",
                title="Hello",
                description="Hello description"
            )       
        ).model_dump(mode="json")

        batch_update_presentation(
            presentationId="pres1",
            requests=[request]
        )

        assert DB['users']['me']['files']['pres1']['slides'][0]['pageElements'][0]['title'] == 'Hello'
        assert DB['users']['me']['files']['pres1']['slides'][0]['pageElements'][0]['description'] == 'Hello description'

    def test_update_slide_properties(self):
        rgb_color = RgbColor(red=0.98, green=0.98, blue=0.98)
        opaque_color = OpaqueColor(rgbColor=rgb_color, themeColor=None)
        background_color = BackgroundColor(opaqueColor=opaque_color)
        page_properties = PageProperties(backgroundColor=background_color)
        notes_properties = NotesProperties(speakerNotesObjectId="notes_page1")
        notes_page = PageModel(objectId="notes_page1", pageType="NOTES", revisionId="rev_notes_page1", notesProperties=notes_properties, pageProperties=page_properties)
        slide_properties = SlideProperties(layoutObjectId="Layout_new_test", notesPage=notes_page, isSkipped=True)
        request = UpdateSlidePropertiesRequestModel(
                    updateSlideProperties=UpdateSlidePropertiesRequestParams(
                        objectId="slide1_page1",
                        slideProperties=slide_properties,
                        
                        
                        
                        
                    fields="layoutObjectId,isSkippedLayout,notesPage"
                )
        ).model_dump(mode="json")

        batch_update_presentation(
            presentationId="pres1",
            requests=[
                request
            ]
        )
        assert DB['users']['me']['files']['pres1']['slides'][0]['slideProperties']["layoutObjectId"] == "Layout_new_test"
 
    def test_update_text_style(self):

        batch_update_presentation(
            presentationId="pres1",
            requests=[
                UpdateTextStyleRequestModel(
                    updateTextStyle=UpdateTextStyleRequestParams(
                        objectId="element1_slide1",  # Must be a valid shape ID on the slide
                        style=TextStyle(
                            fontFamily="Arial",
                            fontSize=Dimension(magnitude=18.0, unit="PT"),
                            bold=True,
                            italic=True,
                            underline=False
                        ),
                        textRange=Range(
                            startIndex=0,
                            endIndex=10,
                            type="FIXED_RANGE"
                        ),
                        fields="fontFamily,fontSize,bold,italic,underline"
                    )
                ).model_dump(mode="json")
            ]
        )

        for element in DB['users']['me']['files']['pres1']['slides'][0]['pageElements'][0]['shape']['text']['textElements']:
            assert element['textRun']['style']['fontFamily'] == 'Arial'
            assert element['textRun']['style']['fontSize']['magnitude'] == 18.0
            assert element['textRun']['style']['bold'] == True
            assert element['textRun']['style']['italic'] == True
            assert element['textRun']['style']['underline'] == False

    def test_invalid_presentation_id_type(self):
        """Test that passing a non-string presentation ID raises InvalidInputError."""
        self.assert_error_behavior(
            batch_update_presentation,
            InvalidInputError,
            "Presentation ID must be a string.",
            presentationId=123,
            requests=[]
        )

    def test_empty_presentation_id(self):
        """Test that passing an empty presentation ID raises InvalidInputError."""
        self.assert_error_behavior(
            batch_update_presentation,
            InvalidInputError,
            "Presentation ID cannot be empty.",
            presentationId="",
            requests=[]
        )

    def test_presentation_not_found(self):
        """Test that requesting a non-existent presentation raises NotFoundError."""
        self.assert_error_behavior(
            batch_update_presentation,
            NotFoundError,
            "Presentation with ID 'nonexistent' not found or is not a presentation.",
            presentationId="nonexistent",
            requests=[]
        )

    def test_write_control_validation(self):
        """Test write control validation with invalid revision ID."""
        DB['users']['me']['files']['pres1']['revisionId'] = 'current_rev'
        
        self.assert_error_behavior(
            batch_update_presentation,
            ConcurrencyError,
            "Required revision ID 'different_rev' does not match current revision ID 'current_rev'.",
            presentationId="pres1",
            requests=[],
            writeControl={"requiredRevisionId": "different_rev"}
        )

    def test_invalid_requests_type(self):
        """Test that passing non-list requests raises InvalidInputError."""
        self.assert_error_behavior(
            batch_update_presentation,
            InvalidInputError,
            "Requests payload must be a list.",
            presentationId="pres1",
            requests="not_a_list"
        )

    def test_malformed_request_item(self):
        """Test that a malformed request item raises InvalidInputError."""
        self.assert_error_behavior(
            batch_update_presentation,
            InvalidInputError,
            "Request at index 0 is malformed: must be a dictionary with a single key.",
            presentationId="pres1",
            requests=[{"key1": "value1", "key2": "value2"}]
        )

    def test_invalid_request_params(self):
        """Test that invalid request parameters raise InvalidInputError."""
        self.assert_error_behavior(
            batch_update_presentation,
            InvalidInputError,
            "Parameters for request 'createShape' at index 0 must be a dictionary.",
            presentationId="pres1",
            requests=[{"createShape": "not_a_dict"}]
        )

    def test_unsupported_request_type(self):
        """Test that an unsupported request type raises InvalidInputError."""
        self.assert_error_behavior(
            batch_update_presentation,
            InvalidInputError,
            "Unsupported request type: 'unsupportedType' at index 0.",
            presentationId="pres1",
            requests=[{"unsupportedType": {}}]
        )

    def test_handler_error_propagation(self):
        """Test that errors from request handlers are properly propagated."""
        bad_request = {
            "createShape": {
                "objectId": "invalid_id",
                "shapeType": "INVALID_SHAPE_TYPE",  # This will cause a validation error
                "elementProperties": {}
            }
        }
        
        self.assert_error_behavior(
            batch_update_presentation,
            InvalidInputError,
            "Invalid parameters for createShape request: 1 validation error for CreateShapeRequestParams\nshapeType\n  Input should be 'TYPE_UNSPECIFIED', 'TEXT_BOX', 'RECTANGLE', 'ROUND_RECTANGLE', 'ELLIPSE', 'ARC', 'BENT_ARROW', 'BENT_UP_ARROW', 'BEVEL', 'BLOCK_ARC', 'BRACE_PAIR', 'BRACKET_PAIR', 'CAN', 'CHEVRON', 'CHORD', 'CLOUD', 'CORNER', 'CUBE', 'CURVED_DOWN_ARROW', 'CURVED_LEFT_ARROW', 'CURVED_RIGHT_ARROW', 'CURVED_UP_ARROW', 'DECAGON', 'DIAGONAL_STRIPE', 'DIAMOND', 'DODECAGON', 'DONUT', 'DOUBLE_WAVE', 'DOWN_ARROW', 'DOWN_ARROW_CALLOUT', 'FOLDED_CORNER', 'FRAME', 'HALF_FRAME', 'HEART', 'HEPTAGON', 'HEXAGON', 'HOME_PLATE', 'HORIZONTAL_SCROLL', 'IRREGULAR_SEAL_1', 'IRREGULAR_SEAL_2', 'LEFT_ARROW', 'LEFT_ARROW_CALLOUT', 'LEFT_BRACE', 'LEFT_BRACKET', 'LEFT_RIGHT_ARROW', 'LEFT_RIGHT_ARROW_CALLOUT', 'LEFT_RIGHT_UP_ARROW', 'LEFT_UP_ARROW', 'LIGHTNING_BOLT', 'MATH_DIVIDE', 'MATH_EQUAL', 'MATH_MINUS', 'MATH_MULTIPLY', 'MATH_NOT_EQUAL', 'MATH_PLUS', 'MOON', 'NO_SMOKING', 'NOTCHED_RIGHT_ARROW', 'OCTAGON', 'PARALLELOGRAM', 'PENTAGON', 'PIE', 'PLAQUE', 'PLUS', 'QUAD_ARROW', 'QUAD_ARROW_CALLOUT', 'RIBBON', 'RIBBON_2', 'RIGHT_ARROW', 'RIGHT_ARROW_CALLOUT', 'RIGHT_BRACE', 'RIGHT_BRACKET', 'ROUND_1_RECTANGLE', 'ROUND_2_DIAGONAL_RECTANGLE', 'ROUND_2_SAME_RECTANGLE', 'RIGHT_TRIANGLE', 'SMILEY_FACE', 'SNIP_1_RECTANGLE', 'SNIP_2_DIAGONAL_RECTANGLE', 'SNIP_2_SAME_RECTANGLE', 'SNIP_ROUND_RECTANGLE', 'STAR_10', 'STAR_12', 'STAR_16', 'STAR_24', 'STAR_32', 'STAR_4', 'STAR_5', 'STAR_6', 'STAR_7', 'STAR_8', 'STRIPED_RIGHT_ARROW', 'SUN', 'TRAPEZOID', 'TRIANGLE', 'UP_ARROW', 'UP_ARROW_CALLOUT', 'UP_DOWN_ARROW', 'UTURN_ARROW', 'VERTICAL_SCROLL', 'WAVE', 'WEDGE_ELLIPSE_CALLOUT', 'WEDGE_RECTANGLE_CALLOUT', 'WEDGE_ROUND_RECTANGLE_CALLOUT', 'FLOW_CHART_ALTERNATE_PROCESS', 'FLOW_CHART_COLLATE', 'FLOW_CHART_CONNECTOR', 'FLOW_CHART_DECISION', 'FLOW_CHART_DELAY', 'FLOW_CHART_DISPLAY', 'FLOW_CHART_DOCUMENT', 'FLOW_CHART_EXTRACT', 'FLOW_CHART_INPUT_OUTPUT', 'FLOW_CHART_INTERNAL_STORAGE', 'FLOW_CHART_MAGNETIC_DISK', 'FLOW_CHART_MAGNETIC_DRUM', 'FLOW_CHART_MAGNETIC_TAPE', 'FLOW_CHART_MANUAL_INPUT', 'FLOW_CHART_MANUAL_OPERATION', 'FLOW_CHART_MERGE', 'FLOW_CHART_MULTIDOCUMENT', 'FLOW_CHART_OFFLINE_STORAGE', 'FLOW_CHART_OFFPAGE_CONNECTOR', 'FLOW_CHART_ONLINE_STORAGE', 'FLOW_CHART_OR', 'FLOW_CHART_PREDEFINED_PROCESS', 'FLOW_CHART_PREPARATION', 'FLOW_CHART_PROCESS', 'FLOW_CHART_PUNCHED_CARD', 'FLOW_CHART_PUNCHED_TAPE', 'FLOW_CHART_SORT', 'FLOW_CHART_SUMMING_JUNCTION', 'FLOW_CHART_TERMINATOR', 'ARROW_EAST', 'ARROW_NORTH_EAST', 'ARROW_NORTH', 'SPEECH', 'STARBURST', 'TEARDROP', 'ELLIPSE_RIBBON', 'ELLIPSE_RIBBON_2', 'CLOUD_CALLOUT' or 'CUSTOM' [type=literal_error, input_value='INVALID_SHAPE_TYPE', input_type=str]\n    For further information visit https://errors.pydantic.dev/2.11/v/literal_error",
            presentationId="pres1",
            requests=[bad_request]
        )
