import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

import requests

from licensing.client import LicenseController


class FakeResponse:
    # Simula la parte minima de requests.Response usada por el controlador.
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload


class LicensingControllerTests(unittest.TestCase):
    def setUp(self):
        # Aisla archivos de estado en una carpeta temporal por test.
        self.temp_dir = tempfile.TemporaryDirectory()
        os.environ["ASISTENTE_DATA_DIR"] = self.temp_dir.name

    def tearDown(self):
        # Limpia el directorio temporal y restaura variable de entorno.
        self.temp_dir.cleanup()
        os.environ.pop("ASISTENTE_DATA_DIR", None)

    def test_activation_and_local_validation(self):
        # Caso feliz: activa una vez y luego valida desde estado local.
        now = datetime.now(timezone.utc)

        def fake_post(url, json, timeout):
            if url.endswith("/activate"):
                return FakeResponse(
                    200,
                    {
                        "status": "active",
                        "token": "abc",
                        "next_check_at": (now + timedelta(hours=24)).isoformat(),
                        "grace_until": (now + timedelta(hours=72)).isoformat(),
                    },
                )
            raise AssertionError("No deberia llamar heartbeat")

        controller = LicenseController(
            api_base_url="http://localhost:8008",
            http_post=fake_post,
        )

        ok, _ = controller.ensure_valid(lambda: "ACP-DEMO")
        self.assertTrue(ok)

        ok, _ = controller.revalidate_non_interactive()
        self.assertTrue(ok)

    def test_offline_grace_when_server_is_unreachable(self):
        # Caso offline: sin red, debe permitir uso dentro de ventana de gracia.
        past = datetime.now(timezone.utc) - timedelta(hours=1)
        grace = datetime.now(timezone.utc) + timedelta(hours=2)

        def fake_post(url, json, timeout):
            if url.endswith("/activate"):
                return FakeResponse(
                    200,
                    {
                        "status": "active",
                        "token": "abc",
                        "next_check_at": past.isoformat(),
                        "grace_until": grace.isoformat(),
                    },
                )
            raise requests.RequestException("Sin red")

        controller = LicenseController(
            api_base_url="http://localhost:8008",
            http_post=fake_post,
        )

        ok, _ = controller.ensure_valid(lambda: "ACP-DEMO")
        self.assertTrue(ok)

        ok, message = controller.revalidate_non_interactive()
        self.assertTrue(ok)
        self.assertIn("gracia", message.lower())


if __name__ == "__main__":
    unittest.main()

