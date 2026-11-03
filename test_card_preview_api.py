import unittest
from card_preview_api import build_card_response


class CardApiContractTests(unittest.TestCase):
    def test_verified_free_user(self):
        result = build_card_response(
            authenticated_user_id="user-a", email_confirmed=True,
            server_billing_state={"active": False, "status": "none"})
        self.assertEqual(result["card"]["level"], "BASIC")

    def test_unverified_user_not_eligible(self):
        result = build_card_response(
            authenticated_user_id="user-a", email_confirmed=False,
            server_billing_state={"active": False})
        self.assertFalse(result["eligible"])
        self.assertIsNone(result["card"])

    def test_missing_identity_rejected(self):
        with self.assertRaises(ValueError):
            build_card_response(
                authenticated_user_id="", email_confirmed=True,
                server_billing_state={"active": False})

    def test_billing_outage_does_not_grant_pro(self):
        result = build_card_response(
            authenticated_user_id="user-a", email_confirmed=True,
            server_billing_state=None)
        self.assertEqual(result["card"]["level"], "BASIC")
        self.assertEqual(result["card"]["billing_status"], "verification_pending")


if __name__ == "__main__":
    unittest.main()
