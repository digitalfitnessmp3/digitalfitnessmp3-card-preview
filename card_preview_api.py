"""Preview-only API adapter for AlphaBeat World Card.

Not mounted on the production app. The host application must inject its
existing verified Supabase authentication and server-side billing dependency.
"""
from card_preview_logic import card_view


def build_card_response(*, authenticated_user_id, email_confirmed, server_billing_state):
    """Return a safe card projection from trusted server-side inputs only.

    Never pass client-supplied user_id, email_confirmed, or billing state.
    Caller must verify Supabase user identity AND email confirmation server-side.
    """
    return card_view(
        user_id=authenticated_user_id,
        email_confirmed=email_confirmed,
        billing_state=server_billing_state,
    )


def install_preview_route(app, authenticated_identity, load_billing_state):
    """Install GET /api/alphabeat/card only in an isolated preview app.

    authenticated_identity must return trusted {'user_id': ..., 'email_confirmed': bool}.
    load_billing_state must fetch trusted billing data for that user ID.
    This function intentionally imports FastAPI lazily so pure tests work
    without FastAPI installed. It must not be mounted in production as-is.
    """
    from fastapi import Depends, HTTPException

    @app.get("/api/alphabeat/card")
    async def get_card(identity=Depends(authenticated_identity)):
        if not isinstance(identity, dict) or not identity.get("user_id"):
            raise HTTPException(status_code=401, detail="Authentication required")
        if identity.get("email_confirmed") is not True:
            raise HTTPException(status_code=403, detail="Verified email required")
        state = await load_billing_state(identity["user_id"])
        return build_card_response(
            authenticated_user_id=identity["user_id"],
            email_confirmed=True,
            server_billing_state=state,
        )
