from .authentication_service import authorize_service_access, check_service_authorization, clear_all_service_authorizations, generate_secured_function_wrapper, retrieve_authorized_services, revoke_service_access

_function_map = {
    'authorize_service_access': 'authentication.mutations.m01.authentication_service.authorize_service_access',
    'check_service_authorization': 'authentication.mutations.m01.authentication_service.check_service_authorization',
    'clear_all_service_authorizations': 'authentication.mutations.m01.authentication_service.clear_all_service_authorizations',
    'generate_secured_function_wrapper': 'authentication.mutations.m01.authentication_service.generate_secured_function_wrapper',
    'retrieve_authorized_services': 'authentication.mutations.m01.authentication_service.retrieve_authorized_services',
    'revoke_service_access': 'authentication.mutations.m01.authentication_service.revoke_service_access',
}
