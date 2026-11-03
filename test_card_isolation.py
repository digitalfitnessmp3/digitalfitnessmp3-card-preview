"""Isolated tenant-boundary tests for the AlphaBeat card preview.

These use injected identities, not production Supabase or Stripe credentials.
Run: python -m unittest test_card_isolation.py -v
Requires FastAPI and httpx.
"""
import unittest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from card_preview_api import install_preview_route


class IsolationTests(unittest.TestCase):
    def test_billing_lookup_uses_authenticated_identity_only(self):
        observed = []
        app = FastAPI()
        async def identity():
            return {"user_id": "account-A", "email_confirmed": True}
        async def billing(uid):
            observed.append(uid)
            return {"active": False, "status": "none"}
        install_preview_route(app, identity, billing)
        with TestClient(app) as client:
            response = client.get("/api/alphabeat/card?user_id=account-B")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(observed, ["account-A"])

    def test_unverified_user_never_loads_billing(self):
        observed = []
        app = FastAPI()
        async def identity():
            return {"user_id": "account-A", "email_confirmed": False}
        async def billing(uid):
            observed.append(uid)
            return {}
        install_preview_route(app, identity, billing)
        with TestClient(app) as client:
            response = client.get("/api/alphabeat/card")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(observed, [])

    def test_missing_identity_never_loads_billing(self):
        observed = []
        app = FastAPI()
        async def identity():
            raise HTTPException(status_code=401, detail="Login required")
        async def billing(uid):
            observed.append(uid)
            return {}
        install_preview_route(app, identity, billing)
        with TestClient(app) as client:
            response = client.get("/api/alphabeat/card")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(observed, [])


if __name__ == "__main__":
    unittest.main()
