"""Preview-only billing adapter for the existing Studio Stripe/Redis backend.

Inject stripe_billing.stored_state from the HOST application's server process.
Do not import Studio billing in the public GitHub Pages site. Never accept a
user ID or billing snapshot from request parameters. This is read-only.
"""
from fastapi import HTTPException


def make_studio_billing_reader(stored_state):
    async def read_billing(authenticated_uid):
        if not isinstance(authenticated_uid, str) or not authenticated_uid.strip():
            raise HTTPException(401, "Authentication required")
        try:
            state = await stored_state(authenticated_uid)
        except Exception:
            # Do not silently downgrade a paid member or expose Redis errors.
            raise HTTPException(503, "Billing temporarily unavailable") from None
        if not isinstance(state, dict):
            raise HTTPException(503, "Billing temporarily unavailable")
        # Allow-list: never return Stripe customer/subscription IDs or internal keys.
        return {k: state.get(k) for k in (
            "active", "status", "sandbox", "period_end",
            "period", "cancel_at_period_end"
        )}
    return read_billing
