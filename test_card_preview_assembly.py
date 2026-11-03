"""Assembly smoke tests: no network, Redis, or production changes."""
import unittest
from unittest.mock import patch
from fastapi import FastAPI
from card_preview_assembly import mount_card_on_preview


class CardAssemblyTests(unittest.TestCase):
    def test_mounts_only_preview_route(self):
        app = FastAPI()
        async def stored_state(uid):
            return {"active": False, "status": "none"}
        mount_card_on_preview(app, stored_state)
        routes = [route.path for route in app.routes]
        self.assertIn("/api/alphabeat/card/verified-preview", routes)
        self.assertNotIn("/api/alphabeat/card", routes)

    def test_reader_uses_injected_server_callback(self):
        async def stored_state(uid):
            return {"active": False}
        with patch("card_preview_assembly.make_studio_billing_reader") as reader:
            with patch("card_preview_assembly.install_authenticated_card_preview") as installer:
                app = FastAPI()
                mount_card_on_preview(app, stored_state)
                reader.assert_called_once_with(stored_state)
                installer.assert_called_once()
                self.assertIs(installer.call_args.kwargs["app"], app) if "app" in installer.call_args.kwargs else self.assertIs(installer.call_args.args[0], app)


if __name__ == "__main__":
    unittest.main()
