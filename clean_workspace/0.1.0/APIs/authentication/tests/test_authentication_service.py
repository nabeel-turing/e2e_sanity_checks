import os
import unittest

from common_utils.base_case import BaseTestCaseWithErrorHandler
from common_utils.authentication_manager import AuthenticationManager, get_auth_manager
from authentication.authentication_service import (
    authenticate_service,
    deauthenticate_service,
    is_service_authenticated,
    list_authenticated_services,
    reset_all_authentication,
    create_authenticated_function,
)
from authentication.SimulationEngine.custom_errors import (
    ValidationError,
    AuthenticationError,
)


class TestAuthenticationService(BaseTestCaseWithErrorHandler):
    """Class-based tests for authentication service runtime functions."""

    def setUp(self):
        # Ensure auth enforcement is disabled for predictable tests
        self._prev_auth_env = os.environ.get("AUTH_ENFORCEMENT")
        os.environ["AUTH_ENFORCEMENT"] = "FALSE"
        # Reset manager to defaults between tests
        AuthenticationManager.rollback_config()
        # Start from a clean service config map in each test
        get_auth_manager().service_configs = {}

    def tearDown(self):
        # Restore env and reset manager
        if self._prev_auth_env is None:
            os.environ.pop("AUTH_ENFORCEMENT", None)
        else:
            os.environ["AUTH_ENFORCEMENT"] = self._prev_auth_env
        AuthenticationManager.rollback_config()

    # --- authenticate_service ---

    def test_authenticate_service_success(self):
        auth_manager = get_auth_manager()
        # Configure an existing service from DB
        auth_manager.service_configs["airline"] = {
            "authentication_enabled": True,
            "excluded_functions": [],
            "is_authenticated": False,
        }

        result = authenticate_service("airline")

        self.assertEqual(result["service"], "airline")
        self.assertTrue(result["authenticated"]) 
        self.assertIn("authenticated successfully", result["message"]) 
        self.assertTrue(auth_manager.is_service_authenticated("airline"))

    def test_authenticate_service_invalid_name(self):
        with self.assertRaises(ValidationError) as ctx:
            authenticate_service("")
        self.assertEqual(str(ctx.exception), "Service name must be a non-empty string")

    def test_authenticate_service_service_not_found(self):
        # Ensure the service is not present in DB
        with self.assertRaises(AuthenticationError) as ctx:
            authenticate_service("nonexistent_service")
        self.assertIn("not found", str(ctx.exception))

    # --- deauthenticate_service ---

    def test_deauthenticate_service_success(self):
        auth_manager = get_auth_manager()
        auth_manager.service_configs["airline"] = {
            "authentication_enabled": True,
            "excluded_functions": [],
            "is_authenticated": True,
        }

        result = deauthenticate_service("airline")

        self.assertEqual(result["service"], "airline")
        self.assertFalse(result["authenticated"]) 
        self.assertIn("deauthenticated successfully", result["message"]) 
        self.assertFalse(auth_manager.is_service_authenticated("airline"))

    def test_deauthenticate_service_invalid_name(self):
        with self.assertRaises(ValidationError) as ctx:
            deauthenticate_service("")
        self.assertEqual(str(ctx.exception), "Service name must be a non-empty string")

    # --- is_service_authenticated ---

    def test_is_service_authenticated_service_not_in_db(self):
        self.assertFalse(is_service_authenticated("totally_unknown_service"))

    def test_is_service_authenticated_when_auth_disabled(self):
        auth_manager = get_auth_manager()
        # Existing service with auth disabled should always return True
        auth_manager.service_configs["airline"] = {
            "authentication_enabled": False,
            "excluded_functions": [],
            "is_authenticated": False,
        }
        self.assertTrue(is_service_authenticated("airline"))

    def test_is_service_authenticated_when_auth_enabled_and_not_authenticated(self):
        auth_manager = get_auth_manager()
        auth_manager.service_configs["airline"] = {
            "authentication_enabled": True,
            "excluded_functions": [],
            "is_authenticated": False,
        }
        self.assertFalse(is_service_authenticated("airline"))

    def test_is_service_authenticated_when_auth_enabled_and_authenticated(self):
        auth_manager = get_auth_manager()
        auth_manager.service_configs["airline"] = {
            "authentication_enabled": True,
            "excluded_functions": [],
            "is_authenticated": True,
        }
        self.assertTrue(is_service_authenticated("airline"))

    # --- list_authenticated_services ---

    def test_list_authenticated_services(self):
        auth_manager = get_auth_manager()
        auth_manager.service_configs.update(
            {
                "airline": {
                    "authentication_enabled": True,
                    "excluded_functions": [],
                    "is_authenticated": True,
                },
                "gmail": {
                    "authentication_enabled": True,
                    "excluded_functions": [],
                    "is_authenticated": True,
                },
                "slack": {
                    "authentication_enabled": True,
                    "excluded_functions": [],
                    "is_authenticated": False,
                },
            }
        )

        result = list_authenticated_services()
        services = set(result.get("authenticated_services", []))

        self.assertIn("airline", services)
        self.assertIn("gmail", services)
        self.assertNotIn("slack", services)
        self.assertEqual(result.get("count"), 2)

    # --- reset_all_authentication ---

    def test_reset_all_authentication(self):
        auth_manager = get_auth_manager()
        auth_manager.service_configs.update(
            {
                "airline": {
                    "authentication_enabled": True,
                    "excluded_functions": [],
                    "is_authenticated": True,
                },
                "gmail": {
                    "authentication_enabled": True,
                    "excluded_functions": [],
                    "is_authenticated": True,
                },
            }
        )

        result = reset_all_authentication()

        self.assertTrue(result.get("success"))
        self.assertIn("deauthenticated", result.get("message", ""))
        self.assertFalse(auth_manager.is_service_authenticated("airline"))
        self.assertFalse(auth_manager.is_service_authenticated("gmail"))

    # --- create_authenticated_function ---

    def test_create_authenticated_function_enforces_auth(self):
        auth_manager = get_auth_manager()
        auth_manager.service_configs["airline"] = {
            "authentication_enabled": True,
            "excluded_functions": [],
            "is_authenticated": False,
        }

        def sample_func(x: int, y: int) -> int:
            return x + y

        wrapped = create_authenticated_function(sample_func, "airline")

        with self.assertRaises(AuthenticationError):
            wrapped(1, 2)

        # Authenticate and call again
        authenticate_service("airline")
        self.assertEqual(wrapped(3, 4), 7)

        # Deauthenticate and ensure it fails again
        deauthenticate_service("airline")
        with self.assertRaises(AuthenticationError):
            wrapped(5, 6)


if __name__ == "__main__":
    unittest.main()
