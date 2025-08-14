from .Canva.Asset import check_media_upload_status, fetch_asset_metadata, modify_asset_details, permanently_remove_asset, start_media_upload_process
from .Canva.Autofill import fetch_autofill_task_status, initiate_design_autofill_task
from .Canva.BrandTemplate import fetch_brand_template_by_id, find_brand_templates, retrieve_brand_template_schema
from .Canva.Design.Comment import enumerate_thread_replies, fetch_discussion_thread, post_reply_to_thread, retrieve_specific_reply, start_new_discussion_thread
from .Canva.Design.DesignExport import initiate_design_export_process, query_design_export_status
from .Canva.Design.DesignImport import begin_design_import_from_file, check_file_import_progress, get_url_import_status, initiate_design_import_from_url
from .Canva.Design.__init__ import fetch_project_pages, generate_canva_artwork, retrieve_artwork_metadata, search_canva_creations
from .Canva.Folder import enumerate_directory_contents, make_new_directory, remove_directory_and_contents, rename_directory, retrieve_directory_details
from .Canva.Users import fetch_user_team_info, retrieve_user_profile_data

_function_map = {
    'begin_design_import_from_file': 'canva.mutations.m01.Canva.Design.DesignImport.begin_design_import_from_file',
    'check_file_import_progress': 'canva.mutations.m01.Canva.Design.DesignImport.check_file_import_progress',
    'check_media_upload_status': 'canva.mutations.m01.Canva.Asset.check_media_upload_status',
    'enumerate_directory_contents': 'canva.mutations.m01.Canva.Folder.enumerate_directory_contents',
    'enumerate_thread_replies': 'canva.mutations.m01.Canva.Design.Comment.enumerate_thread_replies',
    'fetch_asset_metadata': 'canva.mutations.m01.Canva.Asset.fetch_asset_metadata',
    'fetch_autofill_task_status': 'canva.mutations.m01.Canva.Autofill.fetch_autofill_task_status',
    'fetch_brand_template_by_id': 'canva.mutations.m01.Canva.BrandTemplate.fetch_brand_template_by_id',
    'fetch_discussion_thread': 'canva.mutations.m01.Canva.Design.Comment.fetch_discussion_thread',
    'fetch_project_pages': 'canva.mutations.m01.Canva.Design.__init__.fetch_project_pages',
    'fetch_user_team_info': 'canva.mutations.m01.Canva.Users.fetch_user_team_info',
    'find_brand_templates': 'canva.mutations.m01.Canva.BrandTemplate.find_brand_templates',
    'generate_canva_artwork': 'canva.mutations.m01.Canva.Design.__init__.generate_canva_artwork',
    'get_url_import_status': 'canva.mutations.m01.Canva.Design.DesignImport.get_url_import_status',
    'initiate_design_autofill_task': 'canva.mutations.m01.Canva.Autofill.initiate_design_autofill_task',
    'initiate_design_export_process': 'canva.mutations.m01.Canva.Design.DesignExport.initiate_design_export_process',
    'initiate_design_import_from_url': 'canva.mutations.m01.Canva.Design.DesignImport.initiate_design_import_from_url',
    'make_new_directory': 'canva.mutations.m01.Canva.Folder.make_new_directory',
    'modify_asset_details': 'canva.mutations.m01.Canva.Asset.modify_asset_details',
    'permanently_remove_asset': 'canva.mutations.m01.Canva.Asset.permanently_remove_asset',
    'post_reply_to_thread': 'canva.mutations.m01.Canva.Design.Comment.post_reply_to_thread',
    'query_design_export_status': 'canva.mutations.m01.Canva.Design.DesignExport.query_design_export_status',
    'remove_directory_and_contents': 'canva.mutations.m01.Canva.Folder.remove_directory_and_contents',
    'rename_directory': 'canva.mutations.m01.Canva.Folder.rename_directory',
    'retrieve_artwork_metadata': 'canva.mutations.m01.Canva.Design.__init__.retrieve_artwork_metadata',
    'retrieve_brand_template_schema': 'canva.mutations.m01.Canva.BrandTemplate.retrieve_brand_template_schema',
    'retrieve_directory_details': 'canva.mutations.m01.Canva.Folder.retrieve_directory_details',
    'retrieve_specific_reply': 'canva.mutations.m01.Canva.Design.Comment.retrieve_specific_reply',
    'retrieve_user_profile_data': 'canva.mutations.m01.Canva.Users.retrieve_user_profile_data',
    'search_canva_creations': 'canva.mutations.m01.Canva.Design.__init__.search_canva_creations',
    'start_media_upload_process': 'canva.mutations.m01.Canva.Asset.start_media_upload_process',
    'start_new_discussion_thread': 'canva.mutations.m01.Canva.Design.Comment.start_new_discussion_thread',
}
