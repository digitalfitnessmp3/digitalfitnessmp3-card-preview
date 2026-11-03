# AlphaBeat World Card V1 — integration contract (preview only)

Status: design prototype; no production integration, no Stripe writes.

## Identity
- One card per authenticated account, keyed server-side by verified user ID.
- Never accept user ID, tier, or paid status supplied by the browser.
- BASIC is free for every registered user and requires no checkout.
- Show the user's display name only from a verified account profile (with a safe fallback).

## Billing
- Read authenticated GET /api/billing/status with the existing access token.
- Only `active === true` AND a recognized `period` qualifies for a paid card.
- Recognized periods: monthly, quarterly, halfyear, yearly.
- When inactive or expired, show BASIC without deleting or duplicating the card.
- On network or auth failure, show a loading/error state, NOT a false paid entitlement.
- Never expose Stripe secrets, customer IDs, or payment details on the card.
- Preserve existing checkout, webhook and customer portal behavior.

## Presentation
- BASIC: approved fluorescent pink/fuchsia/orange gradient.
- Paid tiers: use the exact already-approved plan colors from the live subscription UI, after inspecting its CSS.
- Shared AlphaBeat World Card identity, with DigitalFitnessMP3 service branding where appropriate.
- Responsive mobile design; accessible contrast; no sensitive details in a public URL.

## Verification before integration
1. Locate actual deployed auth provider and account profile page, not merely a similarly named preview.
2. Verify authenticated /api/billing/status response for free, active, canceled-at-period-end and expired users.
3. Confirm existing account sessions remain valid after navigation and refresh.
4. Test that users cannot request another user's card or forge a paid tier.
5. Preview only. Do not merge or deploy without explicit authorization.
