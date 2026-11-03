# AlphaBeat World Card — Studio V04 preview integration gate

Read-only inspection of `digitalfitnessmp3/digitalfitnessmp3-studio`, branch `lab/free-unlimited-remix-access-20261029`, on 2026-11-03.

## Confirmed compatibility
- Studio's `app.py` creates the FastAPI `app` and exposes `authenticated_user(request)` with verified Supabase JWT signatures.
- The Card preview's `lookup_supabase_user` calls the Supabase Auth server to validate a token and read the authoritative `email_confirmed_at`.
- Studio's existing configuration uses `SUPABASE_URL` and `SUPABASE_ANON_KEY`; the card lookup now supports these.
- Studio's `stripe_billing.stored_state(uid)` is the server-only source for billing state.
- Render `digitalfitnessmp3-studio-v04-preview` has auto-deploy disabled.

## Blocking issue before mounting
- Studio's `requirements.txt` does **not** explicitly declare `httpx`, which the preview Auth HTTP adapter imports.
- On a dedicated integration branch, add a pinned/bounded `httpx` dependency and install the card's server-only Python modules in the Studio source tree.
- Do not add card modules to static GitHub Pages or leak Supabase keys, tokens or billing data to browser HTML.
- Verify `app.py` only mounts `/api/alphabeat/card/verified-preview` behind an explicit preview-only feature flag, default OFF.
- Run server startup, missing-token 401, unverified-email 403, Redis outage 503, and cross-account isolation tests in an isolated environment.

## Status
43 isolated CI tests passed in the card-preview repository, but this is not a real Supabase/Redis end-to-end integration.
No deploy or production changes authorized or performed.
