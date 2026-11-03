"""Supabase Auth REST lookup for isolated preview, with public key only.

Configure SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY on the server.
Never use a service_role/secret key. Does not change any Supabase data.
"""
import os
import httpx


async def lookup_supabase_user(access_token: str):
    url = os.environ["SUPABASE_URL"].rstrip("/")
    key = os.environ["SUPABASE_PUBLISHABLE_KEY"]
    if not url.startswith("https://") or not key:
        raise ValueError("Invalid Supabase preview configuration")
    async with httpx.AsyncClient(timeout=5.0, follow_redirects=False) as client:
        response = await client.get(
            url + "/auth/v1/user",
            headers={"apikey": key, "Authorization": "Bearer " + access_token},
        )
        response.raise_for_status()
        data = response.json()
    if not isinstance(data, dict):
        raise ValueError("Invalid Supabase Auth response")
    return {"id": data.get("id"), "email_confirmed_at": data.get("email_confirmed_at")}
