"""Regression tests for Studio's existing Supabase anon-key configuration."""
import os
import unittest
from unittest.mock import patch
import httpx
from supabase_auth_http_preview import lookup_supabase_user


class StudioKeyCompatibilityTests(unittest.IsolatedAsyncioTestCase):
    async def test_existing_studio_anon_key_is_accepted(self):
        def handler(request):
            self.assertEqual(request.headers["apikey"], "studio-anon-public")
            self.assertEqual(request.headers["authorization"], "Bearer session-token")
            return httpx.Response(200, json={
                "id": "verified-account",
                "email_confirmed_at": "2026-11-01T12:00:00Z",
                "user_metadata": {"display_name": "Untrusted browser profile"},
            })
        original = httpx.AsyncClient
        transport = httpx.MockTransport(handler)
        env = {"SUPABASE_URL": "https://project.supabase.co",
               "SUPABASE_ANON_KEY": "studio-anon-public"}
        with patch.dict(os.environ, env, clear=True), patch(
            "supabase_auth_http_preview.httpx.AsyncClient",
            side_effect=lambda *a, **kw: original(*a, transport=transport, **kw)
        ):
            user = await lookup_supabase_user("session-token")
        self.assertEqual(user, {
            "id": "verified-account",
            "email_confirmed_at": "2026-11-01T12:00:00Z"
        })

    async def test_missing_public_key_fails_before_http(self):
        with patch.dict(os.environ, {"SUPABASE_URL": "https://project.supabase.co"}, clear=True):
            with self.assertRaises(ValueError):
                await lookup_supabase_user("session-token")

    async def test_secret_key_is_rejected(self):
        with patch.dict(os.environ, {
            "SUPABASE_URL": "https://project.supabase.co",
            "SUPABASE_ANON_KEY": "sb_secret_should-never-be-used",
        }, clear=True):
            with self.assertRaises(ValueError):
                await lookup_supabase_user("session-token")


if __name__ == "__main__":
    unittest.main()
