"""Pure, dependency-free AlphaBeat World Card projection; preview only.

Never use browser-provided subscription data for authorization. Caller must provide
verified server-side identity and billing state. This module does not create accounts.
"""
from datetime import datetime, timezone


def card_view(*, user_id, email_confirmed, billing_state, now=None):
    if not isinstance(user_id, str) or not user_id.strip():
        raise ValueError("Verified user identity required")
    if email_confirmed is not True:
        return {"eligible": False, "reason": "email_unverified", "card": None}
    if billing_state is None:
        return {"eligible": True, "reason": "billing_unavailable", "card": {
            "level": "BASIC", "billing_status": "verification_pending", "services": []}}
    if not isinstance(billing_state, dict):
        raise ValueError("Server billing state must be a mapping")
    if now is None:
        now = datetime.now(timezone.utc).timestamp()
    end = billing_state.get("period_end")
    paid = (billing_state.get("active") is True
            and billing_state.get("status") == "active"
            and billing_state.get("sandbox") is False
            and isinstance(end, (int, float)) and not isinstance(end, bool)
            and end > now)
    # Only active paid status can promote the display; real access still
    # belongs to the existing server-side entitlement checks.
    return {"eligible": True, "reason": "ok", "card": {
        "level": "PRO" if paid else "BASIC",
        "billing_status": "active" if paid else "free_or_inactive",
        "services": ["DigitalFitnessMP3"] if paid else []}}
