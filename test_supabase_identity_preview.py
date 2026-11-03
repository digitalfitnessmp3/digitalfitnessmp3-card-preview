"""HTTP tests for the server-side Supabase identity boundary (mocked Auth)."""
import unittest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from supabase_identity_preview import make_verified_identity_dependency


class SupabaseIdentityPreviewTests(unittest.TestCase):
    def client(self, lookup):
        app = FastAPI()
        dependency = make_verified_identity_dependency(lookup)
        @app.get("/identity")
        async def identity(user=Depends(dependency)):
            return user
        return TestClient(app)

    def test_missing_token_rejected_without_lookup(self):
        calls = []
        async def lookup(token):
            calls.append(token)
            return {"id": "A", "email_confirmed_at": "2026-01-01"}
        with self.client(lookup) as client:
            response = client.get("/identity")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(calls, [])

    def test_invalid_token_rejected(self):
        async def lookup(token):
            raise ValueError("invalid")
        with self.client(lookup) as client:
            response = client.get("/identity", headers={"Authorization": "Bearer invalid"})
        self.assertEqual(response.status_code, 401)

    def test_confirmed_user_uses_auth_record(self):
        async def lookup(token):
            self.assertEqual(token, "valid")
            return {"id": "account-A", "email_confirmed_at": "2026-01-01"}
        with self.client(lookup) as client:
            response = client.get("/identity?user_id=account-B", headers={"Authorization": "Bearer valid"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"user_id": "account-A", "email_confirmed": True})

    def test_unconfirmed_user_not_marked_confirmed(self):
        async def lookup(token):
            return {"id": "account-A", "email_confirmed_at": None,
                    "user_metadata": {"email_confirmed_at": "fake"}}
        with self.client(lookup) as client:
            response = client.get("/identity", headers={"Authorization": "Bearer valid"})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["email_confirmed"])

    def test_missing_auth_user_id_rejected(self):
        async def lookup(token):
            return {"email_confirmed_at": "2026-01-01"}
        with self.client(lookup) as client:
            response = client.get("/identity", headers={"Authorization": "Bearer valid"})
        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
