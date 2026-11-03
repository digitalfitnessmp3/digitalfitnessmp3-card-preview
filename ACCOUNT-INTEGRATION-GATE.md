# AlphaBeat World Card — secure backend integration gate

Status: **design only**. No live login, no Stripe change, no production deployment.

## Existing verified backend interfaces

- Studio FastAPI authenticates bearer JWT through its `authenticated_user` dependency, validating issuer, audience, signature and subject. This returns the authenticated Supabase UUID.
- Studio billing router already exposes authenticated `/status` and derives a server-side subscription snapshot from Redis, keyed by authenticated UUID.
- `stripe_billing.stored_state(uid)` includes `active`, `status`, `period_end` and `sandbox`. The card display must use these values only on the server.
- The existing JWT dependency does **not** itself establish that the email is confirmed. Resolve this independently using a trusted Auth user record (or a documented, verified server-side claim). Do not trust client-provided `email_confirmed` or `user_metadata`.

## Proposed isolated preview wiring

1. Reuse the existing authenticated UUID dependency, with no request parameter selecting a user.
2. Resolve the authenticated user's email-confirmation state on the server. If absent or unknown, fail closed (403 or temporary error; never issue PRO).
3. Load billing state by that same UUID through the existing server-side billing module, not through a browser-provided subscription object.
4. Call `build_card_response(authenticated_user_id=uid, email_confirmed=confirmed, server_billing_state=state)`.
5. Return only safe card display fields. Keep Stripe customer IDs, Redis keys, raw user metadata and private user information out of the response.
6. Mount the endpoint **only** in a protected Studio preview after reviewing CORS and token handling. The public GitHub Pages mock must remain credential-free.
7. Keep actual subscription entitlements enforced by the existing billing middleware; card appearance grants no access.

## Required acceptance gates

- No token => 401; malformed or expired token => 401.
- Verified account A cannot read account B's state via query string, body, path or forged headers.
- Unconfirmed email => 403; billing lookup not invoked.
- Missing billing data => BASIC with verification_pending; never fabricated PRO.
- Sandbox subscription and expired subscription => no production PRO display.
- Active, paid, live subscription => correct tier and expiry based on existing authoritative plan mapping (currently PRO is a placeholder, not a complete plan taxonomy).
- Cancellation scheduled at period end retains correct paid status until actual expiry.
- Auth or billing backend outage fails safely and does not expose tracebacks, tokens or private state.
- No account migration, no new public table, no Stripe write, no cross-domain SSO claim without explicit design and testing.

## Deployment decision

Do not deploy or alter live authentication, Redis, Stripe, or database schema without separate authorization and passing integration tests.
