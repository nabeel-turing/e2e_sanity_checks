# """
# A comprehensive, sequential test script to validate the combined functionality and rollback capabilities of all framework features.

# This script tests the following scenarios based on the default_framework_config.json:
# 1.  **Setup:** Applies the comprehensive configuration.
# 2.  **Test Applied State:**
#     - **Gmail (Mutation + Auth + error_dict):** Validates that a mutated, auth-required function returns an error dict, then succeeds after authentication.
#     - **GDrive (Error Sim + Auth + raise):** Validates that a pre-authenticated service raises a simulated error once, then succeeds.
#     - **Slack (Mutation without Auth):** Validates that a mutated function works without auth.
# 3.  **Rollback:** Reverts all applied configurations.
# 4.  **Test Rolled-Back State:**
#     - Verifies that mutations are gone.
#     - Verifies that authentication requirements have reverted.
#     - Verifies that error simulations are disabled.
# """
# import sys
# import os
# import json
# import pytest

# # Ensure the APIs directory is in the Python path
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# # Import necessary managers and service modules
# from common_utils import framework_feature_manager
# from authentication import authenticate_service, is_service_authenticated
# from APIs.authentication.authentication_service import AuthenticationError
# import gmail
# import gdrive
# import slack

# def test_framework_end_to_end_and_rollback():
#     """
#     Runs a full end-to-end test of the framework, including setup,
#     validation of the applied state, rollback, and verification of the clean state.
#     """
#     # --- Test Setup ---
#     print("\n--- Framework Test: Applying Configuration ---")
#     config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'default_framework_config.json'))
#     try:
#         with open(config_path) as f:
#             config = json.load(f)
#         framework_feature_manager.apply_config(config)
#         print(f"✅ Configuration from '{os.path.basename(config_path)}' applied successfully.")
#     except Exception as e:
#         pytest.fail(f"❌ SETUP FAILED: Could not apply framework config: {e}")

#     # --- Test Applied State ---
#     print("\n--- Framework Test: Verifying Applied State ---")

#     # 1. Gmail (Mutation + Auth + error_dict)
#     print("\n▶️ Testing Gmail (Mutation + Auth + error_dict)...")
#     # Call mutated function without auth, expect an error_dict
#     gmail_result_1 = gmail.search_mailbox_for_emails(user_account_to_search="me", search_query_string="test")
#     assert isinstance(gmail_result_1, dict) and "AuthenticationError" in gmail_result_1.get("exceptionType", ""), "Gmail should have returned an AuthenticationError dict."
#     print("✅ Gmail: Received AuthenticationError dict as expected.")
#     # Authenticate and call again
#     authenticate_service("gmail")
#     assert is_service_authenticated("gmail"), "Gmail should be authenticated."
#     gmail_result_2 = gmail.search_mailbox_for_emails(user_account_to_search="me", search_query_string="test")
#     assert isinstance(gmail_result_2, dict) and "message" in gmail_result_2, "Gmail call should succeed after auth."
#     print("✅ Gmail: Authenticated and executed mutated function successfully.")

#     # 2. GDrive (Error Sim + Auth + raise)
#     print("\n▶️ Testing GDrive (Error Sim + Auth + raise)...")
#     # GDrive is pre-authenticated in the config, so the first call should trigger the simulated error.
#     with pytest.raises(RuntimeError, match="Error 500: Internal server error"):
#         gdrive.get_drive_account_info()
#     print("✅ GDrive: Raised simulated RuntimeError as expected.")
#     # The error is exhausted, so the second call should succeed.
#     gdrive_result_2 = gdrive.get_drive_account_info()
#     assert isinstance(gdrive_result_2, dict) and "user" in gdrive_result_2, "GDrive call should succeed after simulated error."
#     print("✅ GDrive: Function executed successfully on the second attempt.")

#     # 3. Slack (Mutation without Auth)
#     print("\n▶️ Testing Slack (Mutation without Auth)...")
#     # Function is mutated from search_messages -> find_messages_by_query
#     # and argument 'query' -> 'message_search_expression'
#     # The mutated function is expected to return a list directly.
#     slack_result = slack.find_messages_by_query(message_search_expression="test")
#     assert isinstance(slack_result, list), "Mutated Slack function should return a list."
#     print("✅ Slack: Executed mutated function without auth successfully.")

#     # --- Rollback ---
#     print("\n--- Framework Test: Rolling Back Configuration ---")
#     try:
#         framework_feature_manager.rollback_config()
#         print("✅ Framework configurations reverted successfully.")
#     except Exception as e:
#         pytest.fail(f"❌ ROLLBACK FAILED: Could not revert framework configs: {e}")

#     # --- Verify Rolled-Back State ---
#     print("\n--- Framework Test: Verifying Rolled-Back State ---")

#     # 1. Verify Gmail State is Reverted
#     print("\n▶️ Verifying Gmail state...")
#     # Mutation: Mutated function should be gone
#     with pytest.raises(AttributeError):
#         gmail.search_mailbox_for_emails(user_account_to_search="me", search_query_string="test")
#     print("✅ Gmail: Mutated function no longer exists.")
#     # Auth: After rollback, auth should be disabled, and the call should succeed.
#     try:
#         profile_result = gmail.get_user_profile(userId="me")
#         assert isinstance(profile_result, dict) and "emailAddress" in profile_result
#         print("✅ Gmail: Standard function works without auth after rollback, as expected.")
#     except Exception as e:
#         pytest.fail(f"❌ Gmail: Standard function failed after rollback when it should have succeeded: {e}")

#     # 2. Verify GDrive State is Reverted
#     print("\n▶️ Verifying GDrive state...")

#     gdrive.get_drive_account_info()
#     print("✅ GDrive: No longer simulates RuntimeError ")

#     # 3. Verify Slack State is Reverted
#     print("\n▶️ Verifying Slack state...")
#     # Mutation: Mutated function should be gone
#     with pytest.raises(AttributeError):
#         slack.find_messages_by_query(message_search_expression="test")
#     print("✅ Slack: Mutated function 'find_messages_by_query' no longer exists.")
#     # Original function should now work. Slack's default state does not require auth.
#     try:
#         original_slack_result = slack.search_messages(query="test")
#         assert isinstance(original_slack_result, list)
#         print("✅ Slack: Original function is restored and works.")
#     except Exception as e:
#         pytest.fail(f"❌ Slack: Original function failed after rollback: {e}")

# if __name__ == "__main__":
#     pytest.main(['-s', __file__])