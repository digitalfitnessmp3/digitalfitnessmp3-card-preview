"""Tests for read-only Studio billing adapter."""
import unittest
from fastapi import HTTPException
from studio_billing_preview import make_studio_billing_reader


class StudioBillingPreviewTests(unittest.IsolatedAsyncioTestCase):
    async def test_only_safe_fields_are_returned(self):
        calls = []
        async def stored_state(uid):
            calls.append(uid)
            return {"active": True, "status": "active", "sandbox": False,
                    "period_end": 9999999999, "period": "monthly",
                    "subscription_id": "sub_secret", "customer_id": "cus_secret"}
        result = await make_studio_billing_reader(stored_state)("account-A")
        self.assertEqual(calls, ["account-A"])
        self.assertNotIn("subscription_id", result)
        self.assertNotIn("customer_id", result)
        self.assertTrue(result["active"])

    async def test_missing_identity_is_rejected(self):
        calls = []
        async def stored_state(uid):
            calls.append(uid)
            return {}
        with self.assertRaises(HTTPException) as error:
            await make_studio_billing_reader(stored_state)("")
        self.assertEqual(error.exception.status_code, 401)
        self.assertEqual(calls, [])

    async def test_redis_outage_returns_503(self):
        async def stored_state(uid):
            raise RuntimeError("private redis error")
        with self.assertRaises(HTTPException) as error:
            await make_studio_billing_reader(stored_state)("account-A")
        self.assertEqual(error.exception.status_code, 503)
        self.assertNotIn("private redis error", error.exception.detail)

    async def test_unexpected_state_returns_503(self):
        async def stored_state(uid):
            return None
        with self.assertRaises(HTTPException) as error:
            await make_studio_billing_reader(stored_state)("account-A")
        self.assertEqual(error.exception.status_code, 503)


if __name__ == "__main__":
    unittest.main()
