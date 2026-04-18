from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Dict, Optional, Tuple

import requests

from .device_id import get_device_fingerprint
from .storage import load_state, save_state

# Valores por defecto para validacion remota y ventana offline.
DEFAULT_CHECK_HOURS = 24
DEFAULT_GRACE_HOURS = 72


class LicenseError(Exception):
    # Error de dominio para fallas de validacion de licencia.
    pass


class LicenseController:
    def __init__(
        self,
        api_base_url: str,
        check_hours: int = DEFAULT_CHECK_HOURS,
        grace_hours: int = DEFAULT_GRACE_HOURS,
        timeout_seconds: int = 8,
        http_post: Optional[Callable[..., requests.Response]] = None,
    ):
        # Se inyecta http_post para pruebas unitarias sin red real.
        self.api_base_url = api_base_url.rstrip("/")
        self.check_hours = check_hours
        self.grace_hours = grace_hours
        self.timeout_seconds = timeout_seconds
        self.http_post = http_post or requests.post

    def ensure_valid(self, ask_license_key: Callable[[], Optional[str]]) -> Tuple[bool, str]:
        # Primero intenta estado local; si no sirve, fuerza activacion interactiva.
        device_id = get_device_fingerprint()
        state = load_state()

        ok, message = self._validate_existing_state(state, device_id)
        if ok:
            return True, message

        license_key = ask_license_key()
        if not license_key:
            return False, "No se ingreso una licencia valida."

        try:
            payload = self._activate(license_key.strip(), device_id)
        except LicenseError as exc:
            return False, str(exc)

        self._persist_state(payload, license_key.strip(), device_id)
        return True, "Licencia activada correctamente."

    def revalidate_non_interactive(self) -> Tuple[bool, str]:
        # Revalida sin pedir clave, pensado para chequeos periodicos en segundo plano.
        device_id = get_device_fingerprint()
        state = load_state()
        ok, message = self._validate_existing_state(state, device_id)
        if ok:
            return True, message
        return False, "No se pudo revalidar la licencia."

    def _validate_existing_state(self, state: Optional[Dict[str, Any]], device_id: str) -> Tuple[bool, str]:
        # Valida integridad minima del estado local antes de llamar al servidor.
        if not state:
            return False, "No existe licencia local."

        if state.get("device_id") != device_id:
            return False, "La licencia local pertenece a otro equipo."

        token = state.get("token")
        if not token:
            return False, "Licencia local incompleta."

        now = _utc_now()
        next_check_at = _parse_dt(state.get("next_check_at"))
        grace_until = _parse_dt(state.get("grace_until"))

        if next_check_at and now < next_check_at:
            return True, "Licencia local valida."

        try:
            # Si toca chequeo remoto, refresca token y ventanas temporales.
            payload = self._heartbeat(token, device_id)
            self._persist_state(payload, state.get("license_key", ""), device_id)
            return True, "Licencia revalidada con el servidor."
        except requests.RequestException:
            # Sin red: permite continuar solo dentro de la ventana de gracia.
            if grace_until and now <= grace_until:
                return True, "Modo gracia offline activo."
            return False, "No hay conexion para verificar la licencia y vencio la gracia offline."
        except LicenseError as exc:
            return False, str(exc)

    def _activate(self, license_key: str, device_id: str) -> Dict[str, Any]:
        # Registro inicial del equipo contra la licencia comercial.
        payload = self._post_json(
            "/activate",
            {
                "license_key": license_key,
                "device_id": device_id,
                "app_version": "1.0.0",
            },
        )
        if payload.get("status") != "active":
            raise LicenseError(payload.get("message", "No se pudo activar la licencia."))
        return payload

    def _heartbeat(self, token: str, device_id: str) -> Dict[str, Any]:
        # Ping periodico para detectar revocaciones y renovar token.
        payload = self._post_json(
            "/heartbeat",
            {
                "token": token,
                "device_id": device_id,
            },
        )
        if payload.get("status") != "active":
            raise LicenseError(payload.get("message", "La licencia fue rechazada por el servidor."))
        return payload

    def _post_json(self, endpoint: str, body: Dict[str, Any]) -> Dict[str, Any]:
        # Wrapper comun para mapear respuestas HTTP a errores de licencia claros.
        response = self.http_post(
            f"{self.api_base_url}{endpoint}",
            json=body,
            timeout=self.timeout_seconds,
        )

        if response.status_code >= 500:
            raise LicenseError("Error interno del servidor de licencias.")

        if response.status_code >= 400:
            try:
                data = response.json()
            except Exception:
                raise LicenseError(f"Error {response.status_code} en servidor de licencias.")
            raise LicenseError(data.get("message", f"Error {response.status_code} en servidor de licencias."))

        data = response.json()
        if not isinstance(data, dict):
            raise LicenseError("Respuesta invalida del servidor de licencias.")
        return data

    def _persist_state(self, payload: Dict[str, Any], license_key: str, device_id: str) -> None:
        # Normaliza campos faltantes de tiempo para mantener el cliente funcional.
        now = _utc_now()

        next_check_at = payload.get("next_check_at")
        grace_until = payload.get("grace_until")

        if not next_check_at:
            next_check_at = (now + timedelta(hours=self.check_hours)).isoformat()

        if not grace_until:
            grace_until = (now + timedelta(hours=self.grace_hours)).isoformat()

        state = {
            "license_key": license_key,
            "device_id": device_id,
            "token": payload.get("token", ""),
            "next_check_at": next_check_at,
            "grace_until": grace_until,
            "updated_at": now.isoformat(),
        }
        # Guarda snapshot local que usa el arranque siguiente.
        save_state(state)


def _utc_now() -> datetime:
    # Centraliza reloj en UTC para evitar desfaces por zona horaria.
    return datetime.now(timezone.utc)


def _parse_dt(value: Any) -> Optional[datetime]:
    # Acepta ISO con o sin sufijo Z y devuelve datetime con zona UTC.
    if not value or not isinstance(value, str):
        return None

    normalized = value.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(normalized)
    except ValueError:
        return None

    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

