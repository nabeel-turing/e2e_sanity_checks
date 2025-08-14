from .annotation_operations import add_or_update_annotation, retrieve_design_annotations
from .document_context import fetch_document_styles, fetch_file_defined_components
from .file_management import export_node_images_locally, fetch_figma_file_details, switch_active_document
from .layout_operations import configure_frame_autolayout
from .node_creation import add_new_rectangle, add_new_text_element, construct_new_frame, duplicate_figma_element
from .node_editing import adjust_element_dimensions, apply_fill_color_to_node, apply_stroke_style, bulk_remove_figma_elements, remove_figma_element, reposition_figma_element, update_text_node_value
from .node_reading import fetch_detailed_node_properties, find_descendant_nodes_by_type, retrieve_current_selection_info

_function_map = {
    'add_new_rectangle': 'figma.mutations.m01.node_creation.add_new_rectangle',
    'add_new_text_element': 'figma.mutations.m01.node_creation.add_new_text_element',
    'add_or_update_annotation': 'figma.mutations.m01.annotation_operations.add_or_update_annotation',
    'adjust_element_dimensions': 'figma.mutations.m01.node_editing.adjust_element_dimensions',
    'apply_fill_color_to_node': 'figma.mutations.m01.node_editing.apply_fill_color_to_node',
    'apply_stroke_style': 'figma.mutations.m01.node_editing.apply_stroke_style',
    'bulk_remove_figma_elements': 'figma.mutations.m01.node_editing.bulk_remove_figma_elements',
    'configure_frame_autolayout': 'figma.mutations.m01.layout_operations.configure_frame_autolayout',
    'construct_new_frame': 'figma.mutations.m01.node_creation.construct_new_frame',
    'duplicate_figma_element': 'figma.mutations.m01.node_creation.duplicate_figma_element',
    'export_node_images_locally': 'figma.mutations.m01.file_management.export_node_images_locally',
    'fetch_detailed_node_properties': 'figma.mutations.m01.node_reading.fetch_detailed_node_properties',
    'fetch_document_styles': 'figma.mutations.m01.document_context.fetch_document_styles',
    'fetch_figma_file_details': 'figma.mutations.m01.file_management.fetch_figma_file_details',
    'fetch_file_defined_components': 'figma.mutations.m01.document_context.fetch_file_defined_components',
    'find_descendant_nodes_by_type': 'figma.mutations.m01.node_reading.find_descendant_nodes_by_type',
    'remove_figma_element': 'figma.mutations.m01.node_editing.remove_figma_element',
    'reposition_figma_element': 'figma.mutations.m01.node_editing.reposition_figma_element',
    'retrieve_current_selection_info': 'figma.mutations.m01.node_reading.retrieve_current_selection_info',
    'retrieve_design_annotations': 'figma.mutations.m01.annotation_operations.retrieve_design_annotations',
    'switch_active_document': 'figma.mutations.m01.file_management.switch_active_document',
    'update_text_node_value': 'figma.mutations.m01.node_editing.update_text_node_value',
}
