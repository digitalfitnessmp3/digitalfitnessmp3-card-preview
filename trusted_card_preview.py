"""Preview-only trusted dependency adapter.

The supplied resolve_identity must validate the bearer JWT and look up
email confirmation from the Auth server. It must never trust request fields.
The supplied read_billing must use the same authenticated user UUID.
"""
from fastapi import Depends, HTTPException
from card_preview_api import build_card_response


def mount_trusted_card_preview(app, resolve_identity, read_billing):
    @app.get("/api/alphabeat/card/verified-preview")
    async def verified_card(identity=Depends(resolve_identity)):
        if not isinstance(identity, dict):
            raise HTTPException(401, "Authentication required")
        uid = identity.get("user_id")
        if not isinstance(uid, str) or not uid.strip():
            raise HTTPException(401, "Authentication required")
        if identity.get("email_confirmed") is not True:
            raise HTTPException(403, "Verified email required")
        state = await read_billing(uid)
        return build_card_response(
            authenticated_user_id=uid,
            email_confirmed=True,
            server_billing_state=state,
        )
