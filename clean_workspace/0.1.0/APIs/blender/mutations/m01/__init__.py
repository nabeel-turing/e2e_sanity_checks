from .execution import execute_blender_python_code
from .hyper3d import check_hyper3d_generation_progress, check_hyper3d_integration_status, create_3d_asset_from_images, create_3d_asset_from_text, load_completed_hyper3d_model
from .object import apply_polyhaven_texture_to_object, retrieve_object_details
from .polyhaven import fetch_and_import_polyhaven_asset, find_polyhaven_resources, list_polyhaven_asset_categories, verify_polyhaven_addon_enabled
from .scene import retrieve_current_scene_details

_function_map = {
    'apply_polyhaven_texture_to_object': 'blender.mutations.m01.object.apply_polyhaven_texture_to_object',
    'check_hyper3d_generation_progress': 'blender.mutations.m01.hyper3d.check_hyper3d_generation_progress',
    'check_hyper3d_integration_status': 'blender.mutations.m01.hyper3d.check_hyper3d_integration_status',
    'create_3d_asset_from_images': 'blender.mutations.m01.hyper3d.create_3d_asset_from_images',
    'create_3d_asset_from_text': 'blender.mutations.m01.hyper3d.create_3d_asset_from_text',
    'execute_blender_python_code': 'blender.mutations.m01.execution.execute_blender_python_code',
    'fetch_and_import_polyhaven_asset': 'blender.mutations.m01.polyhaven.fetch_and_import_polyhaven_asset',
    'find_polyhaven_resources': 'blender.mutations.m01.polyhaven.find_polyhaven_resources',
    'list_polyhaven_asset_categories': 'blender.mutations.m01.polyhaven.list_polyhaven_asset_categories',
    'load_completed_hyper3d_model': 'blender.mutations.m01.hyper3d.load_completed_hyper3d_model',
    'retrieve_current_scene_details': 'blender.mutations.m01.scene.retrieve_current_scene_details',
    'retrieve_object_details': 'blender.mutations.m01.object.retrieve_object_details',
    'verify_polyhaven_addon_enabled': 'blender.mutations.m01.polyhaven.verify_polyhaven_addon_enabled',
}
