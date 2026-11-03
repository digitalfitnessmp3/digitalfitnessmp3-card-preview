"""Server-only Supabase identity resolver for isolated preview.

The lookup_user callback MUST validate the supplied access token against
Supabase Auth (e.g. auth.get_user(token)); never decode an unsigned JWT or
trust browser-supplied user/email-confirmation fields.
"""
from fastapi import HTTPException, Request


def make_verified_identity_dependency(lookup_user):
    async def verified_identity(request: Request):
        authorization = request.headers.get("authorization", "")
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer" or not token.strip():
            raise HTTPException(401, "Authentication required")
        try:
            user = await lookup_user(token.strip())
        except Exception:
            raise HTTPException(401, "Invalid session") from None
        if not isinstance(user, dict):
            raise HTTPException(401, "Invalid session")
        uid = user.get("id")
        if not isinstance(uid, str) or not uid.strip():
            raise HTTPException(401, "Invalid session")
        # Supabase Auth user record, never user_metadata or request parameters.
        return {
            "user_id": uid,
            "email_confirmed": bool(user.get("email_confirmed_at")),
        }
    return verified_identity
