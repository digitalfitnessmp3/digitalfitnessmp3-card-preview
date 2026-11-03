"""Compose the isolated preview card route with verified Auth identity.

Host must inject:
- lookup_user(access_token): async validated Supabase Auth get_user result
  normalized to {id, email_confirmed_at}; MUST NOT accept client metadata.
- read_billing(uid): async authoritative Redis-backed billing snapshot for uid.
This does not connect external services or mount on production.
"""
from supabase_identity_preview import make_verified_identity_dependency
from trusted_card_preview import mount_trusted_card_preview


def install_authenticated_card_preview(app, *, lookup_user, read_billing):
    verified_identity = make_verified_identity_dependency(lookup_user)
    mount_trusted_card_preview(app, verified_identity, read_billing)
