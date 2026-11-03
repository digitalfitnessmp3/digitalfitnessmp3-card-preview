import unittest
from card_preview_logic import card_view

class TestCard(unittest.TestCase):
    def test_email(self):
        self.assertIsNone(card_view(user_id="one", email_confirmed=False, billing_state={})["card"])

    def test_basic(self):
        self.assertEqual(card_view(user_id="one", email_confirmed=True, billing_state={"active": False}, now=100)["card"]["level"], "BASIC")

    def test_pro(self):
        state = {"active": True, "status": "active", "sandbox": False, "period_end": 200}
        self.assertEqual(card_view(user_id="one", email_confirmed=True, billing_state=state, now=100)["card"]["level"], "PRO")

    def test_expired(self):
        state = {"active": True, "status": "active", "sandbox": False, "period_end": 50}
        self.assertEqual(card_view(user_id="one", email_confirmed=True, billing_state=state, now=100)["card"]["level"], "BASIC")

    def test_sandbox(self):
        state = {"active": True, "status": "active", "sandbox": True, "period_end": 200}
        self.assertEqual(card_view(user_id="one", email_confirmed=True, billing_state=state, now=100)["card"]["level"], "BASIC")

    def test_missing_billing(self):
        self.assertEqual(card_view(user_id="one", email_confirmed=True, billing_state=None)["card"]["billing_status"], "verification_pending")

    def test_missing_identity(self):
        with self.assertRaises(ValueError):
            card_view(user_id="", email_confirmed=True, billing_state={})

if __name__ == "__main__":
    unittest.main()
