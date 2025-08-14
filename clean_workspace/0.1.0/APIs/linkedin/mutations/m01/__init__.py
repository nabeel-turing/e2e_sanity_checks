from .Me import create_authenticated_user_profile, erase_own_profile, get_own_profile_details, revise_own_profile_information
from .OrganizationAcls import establish_new_organization_role, fetch_organization_permissions_for_member, rescind_organization_access_right, revise_organization_access_control
from .Organizations import discard_organization_by_alias, establish_new_organization, find_organizations_by_public_name, purge_organization_record, revise_organization_details
from .Posts import compose_new_share, get_single_post_by_identifier, retract_post_by_identifier, retrieve_posts_by_author_urn, revise_published_post

_function_map = {
    'compose_new_share': 'linkedin.mutations.m01.Posts.compose_new_share',
    'create_authenticated_user_profile': 'linkedin.mutations.m01.Me.create_authenticated_user_profile',
    'discard_organization_by_alias': 'linkedin.mutations.m01.Organizations.discard_organization_by_alias',
    'erase_own_profile': 'linkedin.mutations.m01.Me.erase_own_profile',
    'establish_new_organization': 'linkedin.mutations.m01.Organizations.establish_new_organization',
    'establish_new_organization_role': 'linkedin.mutations.m01.OrganizationAcls.establish_new_organization_role',
    'fetch_organization_permissions_for_member': 'linkedin.mutations.m01.OrganizationAcls.fetch_organization_permissions_for_member',
    'find_organizations_by_public_name': 'linkedin.mutations.m01.Organizations.find_organizations_by_public_name',
    'get_own_profile_details': 'linkedin.mutations.m01.Me.get_own_profile_details',
    'get_single_post_by_identifier': 'linkedin.mutations.m01.Posts.get_single_post_by_identifier',
    'purge_organization_record': 'linkedin.mutations.m01.Organizations.purge_organization_record',
    'rescind_organization_access_right': 'linkedin.mutations.m01.OrganizationAcls.rescind_organization_access_right',
    'retract_post_by_identifier': 'linkedin.mutations.m01.Posts.retract_post_by_identifier',
    'retrieve_posts_by_author_urn': 'linkedin.mutations.m01.Posts.retrieve_posts_by_author_urn',
    'revise_organization_access_control': 'linkedin.mutations.m01.OrganizationAcls.revise_organization_access_control',
    'revise_organization_details': 'linkedin.mutations.m01.Organizations.revise_organization_details',
    'revise_own_profile_information': 'linkedin.mutations.m01.Me.revise_own_profile_information',
    'revise_published_post': 'linkedin.mutations.m01.Posts.revise_published_post',
}
