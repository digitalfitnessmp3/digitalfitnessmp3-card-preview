"""Optional assembly of existing preview components. No automatic deployment."""
from authenticated_card_preview import install_authenticated_card_preview
from studio_billing_preview import make_studio_billing_reader
from supabase_auth_http_preview import lookup_supabase_user


def mount_card_on_preview(app, stored_state):
    reader = make_studio_billing_reader(stored_state)
    install_authenticated_card_preview(
        app, lookup_user=lookup_supabase_user, read_billing=reader
    )
