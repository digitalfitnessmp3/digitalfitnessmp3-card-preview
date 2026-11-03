"""End-to-end mocked HTTP tests for the composed preview route."""
import unittest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from authenticated_card_preview import install_authenticated_card_preview


class ComposedPreviewTests(unittest.TestCase):
    def make_client(self, user, state):
        calls = []
        async def lookup_user(token):
            calls.append(("auth", token))
            if user == "invalid":
                raise ValueError("invalid token")
            return user
        async def read_billing(uid):
            calls.append(("billing", uid))
            return state
        app = FastAPI()
        install_authenticated_card_preview(app, lookup_user=lookup_user, read_billing=read_billing)
        return TestClient(app), calls

    def test_valid_account_uses_same_uid_for_billing(self):
        client, calls = self.make_client({"id": "A", "email_confirmed_at": "2026-01-01"}, None)
        with client:
            response = client.get("/api/alphabeat/card/verified-preview?user_id=B",
                                  headers={"Authorization": "Bearer valid"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["card"]["level"], "BASIC")
        self.assertEqual(calls, [("auth", "valid"), ("billing", "A")])

    def test_no_token_never_loads_billing(self):
        client, calls = self.make_client({"id": "A", "email_confirmed_at": "2026-01-01"}, None)
        with client:
            response = client.get("/api/alphabeat/card/verified-preview")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(calls, [])

    def test_unconfirmed_never_loads_billing(self):
        client, calls = self.make_client({"id": "A", "email_confirmed_at": None}, None)
        with client:
            response = client.get("/api/alphabeat/card/verified-preview",
                                  headers={"Authorization": "Bearer valid"})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(calls, [("auth", "valid")])

    def test_invalid_token_never_loads_billing(self):
        client, calls = self.make_client("invalid", None)
        with client:
            response = client.get("/api/alphabeat/card/verified-preview",
                                  headers={"Authorization": "Bearer invalid"})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(calls, [("auth", "invalid")])


if __name__ == "__main__":
    unittest.main()
