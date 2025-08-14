import unittest
import copy
import uuid

# Assuming these are the correct import paths for your project structure
from ..SimulationEngine.db import DB
from ..node_creation import create_frame
from common_utils.base_case import BaseTestCaseWithErrorHandler
from ..SimulationEngine import custom_errors
import unittest
import copy
import uuid
from unittest.mock import patch, MagicMock
from ..SimulationEngine import utils

# --- Test Data ---
DEFAULT_FILL_COLOR_INPUT_EXAMPLE = {'type': 'SOLID', 'color': {'r': 0.5, 'g': 0.5, 'b': 0.5, 'a': 1.0}}
EXPECTED_DEFAULT_FILL_COLOR_OUTPUT = {
    'type': 'SOLID',
    'color': {'r': 0.5, 'g': 0.5, 'b': 0.5, 'a': 1.0},
    'visible': True,
    'opacity': 1.0
}

DEFAULT_STROKE_COLOR_INPUT_EXAMPLE = {'type': 'SOLID', 'color': {'r': 0.0, 'g': 0.0, 'b': 0.0, 'a': 1.0}}
EXPECTED_DEFAULT_STROKE_COLOR_OUTPUT = {
    'type': 'SOLID',
    'color': {'r': 0.0, 'g': 0.0, 'b': 0.0, 'a': 1.0},
    'visible': True,
    'opacity': 1.0
}

# --- Updated Test Suite ---

class TestCreateFrame(BaseTestCaseWithErrorHandler):

    def setUp(self):
        """Set up a realistic, nested DB structure for each test."""
        self._original_DB_state = copy.deepcopy(DB)
        DB.clear()

        self.current_file_key = "1SORSDcBJjENuSp0rTi9dQ"
        self.page_default_id = "1516:368"
        self.valid_parent_frame_id = "1516:9022"
        self.non_container_node_id = "1516:9023" # A TEXT node

        # A minimal, valid DB structure based on the new schema
        test_db_structure = {
            "files": [
                {
                    "fileKey": self.current_file_key,
                    "name": "Purity UI Dashboard",
                    "document": {
                        "id": "0:0",
                        "name": "Document",
                        "currentPageId": self.page_default_id,
                        "children": [
                            {
                                "id": self.page_default_id,
                                "name": "👋 Introduction Page",
                                "type": "CANVAS",
                                "children": [
                                    {
                                        "id": self.valid_parent_frame_id,
                                        "name": "Main Dashboard Screen",
                                        "type": "FRAME",
                                        "children": [
                                            {
                                                "id": self.non_container_node_id,
                                                "name": "Page Title",
                                                "type": "TEXT",
                                            }
                                        ]
                                    },
                                    # Another frame to test sibling count for naming
                                    {"id": "existing-frame-1", "type": "FRAME", "name": "Existing Frame"}
                                ]
                            }
                        ]
                    }
                }
            ],
            "current_file_key": self.current_file_key,
        }
        DB.update(copy.deepcopy(test_db_structure))
        
        # Mocking utils.find_node_by_id to work with the setUp DB structure
        # This is necessary because the real function is not provided.
        # This mock simulates finding the parent node inside the test DB.
        # self.mock_find_node = patch('figma.SimulationEngine.utils.find_node_by_id', side_effect=lambda node_id: self._find_node(DB.get('files', []), node_id)).start()
        self.mock_uuid = patch('uuid.uuid4').start()

    def _find_node(self, nodes_list, node_id):
        """Helper to find nodes in the test DB for the mock."""
        for node in nodes_list:
            if node.get('id') == node_id:
                return node
            found = self._find_node(node.get('children', []), node_id)
            if found:
                return found
        return None

    def tearDown(self):
        """Restore the original DB state."""
        DB.clear()
        DB.update(self._original_DB_state)
        patch.stopall()

    # --- Success Test Cases ---
    
    def test_create_frame_minimal_args_and_correct_dynamic_naming(self):
        """Test creating a frame with minimal args and check for correct, stateful naming."""
        args = {'x': 10.0, 'y': 20.0, 'width': 100.0, 'height': 50.0}
        
        # There's one existing frame on the default page, so the first created should be "Frame 2".
        self.mock_uuid.return_value.hex = "new_frame_id_1"
        result1 = create_frame(**args)
        self.assertEqual(result1['name'], "Frame 3")
        self.assertEqual(result1['parent_id'], self.page_default_id)
        
        # Verify DB state: The new frame should be in the parent's children list.
        parent_node = utils.find_node_by_id(DB['files'][0]['document']['children'],self.page_default_id)
        self.assertEqual(parent_node['children'][-1]['id'], "new_frame_id_1")
        self.assertEqual(len(parent_node['children']), 3) # 2 existing + 1 new

        # Second call should create "Frame 3".
        self.mock_uuid.return_value.hex = "new_frame_id_2"
        result2 = create_frame(**args)
        self.assertEqual(result2['name'], "Frame 4")
        self.assertEqual(len(parent_node['children']), 4) # 2 existing + 2 new
        self.assertEqual(parent_node['children'][-1]['id'], "new_frame_id_2")

    def test_create_frame_with_name_and_specific_parent(self):
        """Test creating a frame with a custom name inside a specified parent frame."""
        self.mock_uuid.return_value.hex = "named_frame_id"
        custom_name = "MyNamedFrame"
        args = {
            'x': 5.0, 'y': 15.0, 'width': 120.0, 'height': 60.0,
            'name': custom_name, 'parent_id': self.valid_parent_frame_id
        }
        result = create_frame(**args)
        
        self.assertEqual(result['name'], custom_name)
        self.assertEqual(result['parent_id'], self.valid_parent_frame_id)

        # Verify it was added to the correct parent's children list.
        parent_frame = utils.find_node_by_id(DB['files'][0]['document']['children'],self.valid_parent_frame_id)
        self.assertEqual(parent_frame['children'][-1]['id'], "named_frame_id")

    def test_create_frame_with_fill_and_stroke(self):
        """Test that fill and stroke properties are correctly applied."""
        self.mock_uuid.return_value.hex = "style_frame_id"
        args = {
            'x': 0, 'y': 0, 'width': 10, 'height': 10, 
            'fill_color': DEFAULT_FILL_COLOR_INPUT_EXAMPLE,
            'stroke_color': DEFAULT_STROKE_COLOR_INPUT_EXAMPLE,
            'stroke_weight': 2.0
        }
        result = create_frame(**args)
        
        self.assertEqual(len(result['fills']), 1)
        self.assertDictEqual(result['fills'][0], EXPECTED_DEFAULT_FILL_COLOR_OUTPUT)
        self.assertEqual(len(result['strokes']), 1)
        self.assertDictEqual(result['strokes'][0], EXPECTED_DEFAULT_STROKE_COLOR_OUTPUT)
        self.assertEqual(result['stroke_weight'], 2.0)

    def test_create_frame_with_full_auto_layout(self):
        """Test that all auto-layout properties are correctly set."""
        self.mock_uuid.return_value.hex = "autolayout_frame_id"
        args = {
            'x': 0, 'y': 0, 'width': 200, 'height': 100, 'name': "AutoLayoutH",
            'layout_mode': "HORIZONTAL", 'layout_wrap': "WRAP",
            'padding_top': 5.0, 'padding_right': 10.0, 'padding_bottom': 5.0, 'padding_left': 10.0,
            'primary_axis_align_items': "SPACE_BETWEEN",
            'counter_axis_align_items': "CENTER",
            'item_spacing': 8.0
        }
        result = create_frame(**args)

        self.assertEqual(result['layout_mode'], "HORIZONTAL")
        self.assertEqual(result['layout_wrap'], "WRAP")
        self.assertEqual(result['padding_top'], 5.0)
        self.assertEqual(result['primary_axis_align_items'], "SPACE_BETWEEN")
        self.assertEqual(result['item_spacing'], 8.0)

    # --- Error and Edge Case Test Cases ---

    def _run_validation_error_test(self, mod_args, expected_msg_detail):
        base_args = {'x': 10.0, 'y': 20.0, 'width': 100.0, 'height': 50.0}
        test_args = {**base_args, **mod_args}
        self.assert_error_behavior(
            func_to_call=create_frame, expected_exception_type=custom_errors.ValidationError,
            expected_message=expected_msg_detail, **test_args
        )

    def test_create_frame_negative_width_raises_validationerror(self):
        self._run_validation_error_test({'width': -100.0}, "width must be non-negative")

    def test_create_frame_invalid_layout_mode_enum_raises_validationerror(self):
        self._run_validation_error_test({'layout_mode': "UNKNOWN_MODE"}, "Invalid value for layout_mode")

    def test_create_frame_non_existent_parent_id_raises_parentnotfounderror(self):
        args = {'x': 0, 'y': 0, 'width': 10, 'height': 10, 'parent_id': "id_does_not_exist"}
        self.assert_error_behavior(
            func_to_call=create_frame, expected_exception_type=custom_errors.ParentNotFoundError,
            expected_message="Parent node with ID 'id_does_not_exist' not found or is not a valid container.",
            **args
        )

    def test_create_frame_parent_is_not_valid_container_raises_parentnotfounderror(self):
        args = {'x': 0, 'y': 0, 'width': 10, 'height': 10, 'parent_id': self.non_container_node_id}
        self.assert_error_behavior(
            func_to_call=create_frame, expected_exception_type=custom_errors.ParentNotFoundError,
            expected_message=f"Parent node with ID '{self.non_container_node_id}' not found or is not a valid container.",
            **args
        )

    def test_create_frame_padding_with_layout_mode_none_raises_invalidinputerror(self):
        self.assert_error_behavior(
            func_to_call=create_frame, expected_exception_type=custom_errors.InvalidInputError,
            expected_message="Padding properties require layout_mode to be HORIZONTAL or VERTICAL.",
            x=10, y=10, width=10, height=10, padding_top=5.0
        )

    def test_create_frame_db_missing_current_file_raises_figmaoperationerror(self):
        """Test for a missing file object for the current_file_key."""
        DB['files'] = [] # Keep key, but remove the file list
        self.assert_error_behavior(
            func_to_call=create_frame, expected_exception_type=custom_errors.FigmaOperationError,
            expected_message=f"Current file not found.",
            x=0, y=0, width=10, height=10
        )

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)