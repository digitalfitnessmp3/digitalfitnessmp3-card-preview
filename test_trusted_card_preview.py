"""Tests for trusted preview adapter; no external credentials or services."""
import unittest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from trusted_card_preview import mount_trusted_card_preview


class TrustedCardTests(unittest.TestCase):
    def make_client(self, identity, billing_state):
        calls = []
        app = FastAPI()

        async def resolve_identity():
            return identity

        async def read_billing(uid):
            calls.append(uid)
            return billing_state

        mount_trusted_card_preview(app, resolve_identity, read_billing)
        return TestClient(app), calls

    def test_valid_identity_is_bound_to_billing(self):
        client, calls = self.make_client(
            {"user_id": "account-A", "email_confirmed": True},
            {"active": False, "status": "none"},
        )
        with client:
            response = client.get(
                "/api/alphabeat/card/verified-preview?user_id=account-B"
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["card"]["level"], "BASIC")
        self.assertEqual(calls, ["account-A"])

    def test_unverified_identity_is_rejected_before_billing(self):
        client, calls = self.make_client(
            {"user_id": "account-A", "email_confirmed": False}, None
        )
        with client:
            response = client.get("/api/alphabeat/card/verified-preview")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(calls, [])

    def test_missing_identity_is_rejected_before_billing(self):
        client, calls = self.make_client(None, None)
        with client:
            response = client.get("/api/alphabeat/card/verified-preview")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(calls, [])

    def test_missing_billing_is_pending_not_pro(self):
        client, calls = self.make_client(
            {"user_id": "account-A", "email_confirmed": True}, None
        )
        with client:
            response = client.get("/api/alphabeat/card/verified-preview")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["card"]["billing_status"], "verification_pending")
        self.assertEqual(calls, ["account-A"])


if __name__ == "__main__":
    unittest.main()
