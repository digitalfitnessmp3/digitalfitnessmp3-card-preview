"""HTTP tests for the isolated card route, with injected mock identities.
Run with: python -m unittest test_card_http.py -v
Requires fastapi and httpx in the test environment. No live credentials.
"""
import unittest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from card_preview_api import install_preview_route


def make_client(identity, billing=None):
    app = FastAPI()
    async def auth():
        if identity is None:
            raise HTTPException(401, "Authentication required")
        return identity
    async def state(user_id):
        return billing
    install_preview_route(app, auth, state)
    return TestClient(app)


class CardHttpTests(unittest.TestCase):
    def test_no_login_401(self):
        with make_client(None) as client:
            self.assertEqual(client.get("/api/alphabeat/card").status_code, 401)

    def test_unverified_email_403(self):
        with make_client({"user_id": "u1", "email_confirmed": False}) as client:
            self.assertEqual(client.get("/api/alphabeat/card").status_code, 403)

    def test_verified_basic_200(self):
        with make_client({"user_id": "u1", "email_confirmed": True}, {"active": False}) as client:
            r = client.get("/api/alphabeat/card")
            self.assertEqual(r.status_code, 200)
            self.assertEqual(r.json()["card"]["level"], "BASIC")

    def test_billing_unavailable_is_not_pro(self):
        with make_client({"user_id": "u1", "email_confirmed": True}, None) as client:
            r = client.get("/api/alphabeat/card")
            self.assertEqual(r.status_code, 200)
            self.assertEqual(r.json()["card"]["billing_status"], "verification_pending")


if __name__ == "__main__":
    unittest.main()
