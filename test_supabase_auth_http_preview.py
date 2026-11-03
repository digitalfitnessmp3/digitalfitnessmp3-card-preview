"""Mocked HTTP tests for the Supabase Auth preview lookup."""
import os
import unittest
from unittest.mock import patch
import httpx
from supabase_auth_http_preview import lookup_supabase_user


class AuthHTTPPreviewTests(unittest.IsolatedAsyncioTestCase):
    async def test_valid_response_uses_auth_fields_only(self):
        def handler(request):
            self.assertEqual(str(request.url), "https://project.supabase.co/auth/v1/user")
            self.assertEqual(request.headers["authorization"], "Bearer valid")
            return httpx.Response(200, json={
                "id": "account-A", "email_confirmed_at": "2026-01-01",
                "user_metadata": {"role": "admin"},
            })
        transport = httpx.MockTransport(handler)
        original = httpx.AsyncClient
        def mock_client(*args, **kwargs):
            return original(*args, transport=transport, **kwargs)
        with patch.dict(os.environ, {
            "SUPABASE_URL": "https://project.supabase.co",
            "SUPABASE_PUBLISHABLE_KEY": "public-key",
        }), patch("supabase_auth_http_preview.httpx.AsyncClient", side_effect=mock_client):
            result = await lookup_supabase_user("valid")
        self.assertEqual(result, {"id": "account-A", "email_confirmed_at": "2026-01-01"})

    async def test_auth_401_fails_closed(self):
        transport = httpx.MockTransport(lambda req: httpx.Response(401))
        original = httpx.AsyncClient
        with patch.dict(os.environ, {
            "SUPABASE_URL": "https://project.supabase.co",
            "SUPABASE_PUBLISHABLE_KEY": "public-key",
        }), patch("supabase_auth_http_preview.httpx.AsyncClient",
                  side_effect=lambda *a, **k: original(*a, transport=transport, **k)):
            with self.assertRaises(httpx.HTTPStatusError):
                await lookup_supabase_user("invalid")

    async def test_insecure_url_rejected(self):
        with patch.dict(os.environ, {
            "SUPABASE_URL": "http://project.supabase.co",
            "SUPABASE_PUBLISHABLE_KEY": "public-key",
        }):
            with self.assertRaises(ValueError):
                await lookup_supabase_user("token")


if __name__ == "__main__":
    unittest.main()
