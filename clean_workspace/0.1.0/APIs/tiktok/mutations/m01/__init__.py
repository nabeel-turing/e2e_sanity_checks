from .Business.Get import retrieve_account_analytics
from .Business.Publish.Status import check_content_publication_status
from .Business.Video.Publish import upload_video_to_account

_function_map = {
    'check_content_publication_status': 'tiktok.mutations.m01.Business.Publish.Status.check_content_publication_status',
    'retrieve_account_analytics': 'tiktok.mutations.m01.Business.Get.retrieve_account_analytics',
    'upload_video_to_account': 'tiktok.mutations.m01.Business.Video.Publish.upload_video_to_account',
}
