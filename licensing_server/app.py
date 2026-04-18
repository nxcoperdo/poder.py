from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

# Configuracion base del servicio y politicas de tiempos.
APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "licenses.db"
LICENSE_SECRET = os.getenv("LICENSE_SECRET", "change-this-license-secret")
ADMIN_KEY = os.getenv("LICENSE_ADMIN_KEY", "change-this-admin-key")
CHECK_HOURS = int(os.getenv("LICENSE_CHECK_HOURS", "24"))
GRACE_HOURS = int(os.getenv("LICENSE_GRACE_HOURS", "72"))
TOKEN_HOURS = int(os.getenv("LICENSE_TOKEN_HOURS", "168"))

app = FastAPI(title="AsistenteCajaPro License Server", version="1.0.0")


class ActivateRequest(BaseModel):
    # Payload usado por el cliente al activar un equipo por primera vez.
    license_key: str = Field(min_length=6)
    device_id: str = Field(min_length=32)
    app_version: str = "1.0.0"


class HeartbeatRequest(BaseModel):
    # Payload para revalidaciones periodicas de una activacion ya existente.
    token: str
    device_id: str = Field(min_length=32)


class CreateLicenseRequest(BaseModel):
    # Payload administrativo para emitir licencias comerciales.
    customer_name: str = Field(min_length=2)
    max_devices: int = Field(default=1, ge=1, le=20)
    expires_days: Optional[int] = Field(default=None, ge=1, le=3650)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()


def _parse_iso(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    normalized = value.replace("Z", "+00:00")
    dt = datetime.fromisoformat(normalized)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _b64_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def _sign(payload: Dict[str, Any]) -> str:
    # Firma HMAC simple tipo token compacto: payload_base64.firma_base64.
    raw_payload = json.dumps(payload, ensure_ascii=True, separators=(",", ":")).encode("utf-8")
    encoded_payload = _b64(raw_payload)
    signature = hmac.new(LICENSE_SECRET.encode("utf-8"), encoded_payload.encode("utf-8"), hashlib.sha256).digest()
    return f"{encoded_payload}.{_b64(signature)}"


def _verify(token: str) -> Dict[str, Any]:
    # Verifica estructura, firma e expiracion del token emitido por este servidor.
    if "." not in token:
        raise HTTPException(status_code=401, detail="Token invalido")

    encoded_payload, encoded_sig = token.split(".", 1)
    expected_sig = hmac.new(LICENSE_SECRET.encode("utf-8"), encoded_payload.encode("utf-8"), hashlib.sha256).digest()
    provided_sig = _b64_decode(encoded_sig)

    if not hmac.compare_digest(expected_sig, provided_sig):
        raise HTTPException(status_code=401, detail="Firma de token invalida")

    payload = json.loads(_b64_decode(encoded_payload).decode("utf-8"))
    exp = _parse_iso(payload.get("exp"))
    if not exp or _utc_now() > exp:
        raise HTTPException(status_code=401, detail="Token expirado")
    return payload


def _connect() -> sqlite3.Connection:
    # Conexion SQLite por request; suficiente para MVP local.
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _init_db() -> None:
    # Crea tablas base si no existen para permitir arranque idempotente.
    conn = _connect()
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS licenses (
                license_key TEXT PRIMARY KEY,
                customer_name TEXT NOT NULL,
                max_devices INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'active',
                expires_at TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS activations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                license_key TEXT NOT NULL,
                device_id TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'active',
                first_seen TEXT NOT NULL,
                last_seen TEXT NOT NULL,
                UNIQUE(license_key, device_id)
            );
            """
        )
        conn.commit()
    finally:
        conn.close()


@app.on_event("startup")
def startup() -> None:
    # Inicializa esquema al levantar el servicio.
    _init_db()


@app.get("/health")
def health() -> Dict[str, str]:
    # Endpoint de salud para monitoreo y pruebas automatizadas.
    return {"status": "ok"}


@app.post("/admin/create_license")
def create_license(payload: CreateLicenseRequest, x_admin_key: str = Header(default="")) -> Dict[str, Any]:
    # Solo administradores autorizados pueden emitir nuevas licencias.
    if x_admin_key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Admin key invalida")

    now = _utc_now()
    expires_at = None
    if payload.expires_days:
        expires_at = _iso(now + timedelta(days=payload.expires_days))

    key = f"ACP-{secrets.token_hex(8).upper()}"

    conn = _connect()
    try:
        conn.execute(
            """
            INSERT INTO licenses (license_key, customer_name, max_devices, status, expires_at, created_at, updated_at)
            VALUES (?, ?, ?, 'active', ?, ?, ?)
            """,
            (key, payload.customer_name, payload.max_devices, expires_at, _iso(now), _iso(now)),
        )
        conn.commit()
    finally:
        conn.close()

    return {
        "status": "active",
        "license_key": key,
        "customer_name": payload.customer_name,
        "max_devices": payload.max_devices,
        "expires_at": expires_at,
    }


@app.post("/admin/revoke/license/{license_key}")
def revoke_license(license_key: str, x_admin_key: str = Header(default="")) -> Dict[str, str]:
    # Revoca licencia completa y todas sus activaciones asociadas.
    if x_admin_key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Admin key invalida")

    conn = _connect()
    try:
        cur = conn.execute("UPDATE licenses SET status='revoked', updated_at=? WHERE license_key=?", (_iso(_utc_now()), license_key))
        conn.execute("UPDATE activations SET status='revoked' WHERE license_key=?", (license_key,))
        conn.commit()
    finally:
        conn.close()

    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Licencia no encontrada")

    return {"status": "revoked", "license_key": license_key}


@app.post("/admin/revoke/device/{license_key}/{device_id}")
def revoke_device(license_key: str, device_id: str, x_admin_key: str = Header(default="")) -> Dict[str, str]:
    # Revocacion puntual de un equipo sin afectar el resto de la licencia.
    if x_admin_key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Admin key invalida")

    conn = _connect()
    try:
        cur = conn.execute(
            "UPDATE activations SET status='revoked' WHERE license_key=? AND device_id=?",
            (license_key, device_id),
        )
        conn.commit()
    finally:
        conn.close()

    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Activacion no encontrada")

    return {"status": "revoked", "license_key": license_key, "device_id": device_id}


@app.post("/activate")
def activate(payload: ActivateRequest) -> Dict[str, Any]:
    # Flujo de alta de equipo: valida licencia y respeta limite de dispositivos.
    now = _utc_now()

    conn = _connect()
    try:
        license_row = conn.execute("SELECT * FROM licenses WHERE license_key=?", (payload.license_key,)).fetchone()
        if not license_row:
            raise HTTPException(status_code=404, detail="Licencia inexistente")

        if license_row["status"] != "active":
            raise HTTPException(status_code=403, detail="Licencia revocada")

        expires_at = _parse_iso(license_row["expires_at"])
        if expires_at and now > expires_at:
            raise HTTPException(status_code=403, detail="Licencia expirada")

        activation = conn.execute(
            "SELECT * FROM activations WHERE license_key=? AND device_id=?",
            (payload.license_key, payload.device_id),
        ).fetchone()

        if activation and activation["status"] == "revoked":
            raise HTTPException(status_code=403, detail="Este equipo fue revocado")

        if not activation:
            count_active = conn.execute(
                "SELECT COUNT(*) AS total FROM activations WHERE license_key=? AND status='active'",
                (payload.license_key,),
            ).fetchone()["total"]

            if count_active >= int(license_row["max_devices"]):
                raise HTTPException(status_code=403, detail="Se alcanzo el limite de dispositivos")

            conn.execute(
                """
                INSERT INTO activations (license_key, device_id, status, first_seen, last_seen)
                VALUES (?, ?, 'active', ?, ?)
                """,
                (payload.license_key, payload.device_id, _iso(now), _iso(now)),
            )
        else:
            conn.execute(
                "UPDATE activations SET status='active', last_seen=? WHERE license_key=? AND device_id=?",
                (_iso(now), payload.license_key, payload.device_id),
            )

        conn.execute(
            "UPDATE licenses SET updated_at=? WHERE license_key=?",
            (_iso(now), payload.license_key),
        )
        conn.commit()
    finally:
        conn.close()

    token_payload = {
        "license_key": payload.license_key,
        "device_id": payload.device_id,
        "exp": _iso(now + timedelta(hours=TOKEN_HOURS)),
    }

    return {
        "status": "active",
        "message": "Licencia activa",
        "token": _sign(token_payload),
        "next_check_at": _iso(now + timedelta(hours=CHECK_HOURS)),
        "grace_until": _iso(now + timedelta(hours=GRACE_HOURS)),
    }


@app.post("/heartbeat")
def heartbeat(payload: HeartbeatRequest) -> Dict[str, Any]:
    # Revalida token y estado de activacion para habilitar uso continuo.
    token_payload = _verify(payload.token)

    if token_payload.get("device_id") != payload.device_id:
        raise HTTPException(status_code=401, detail="Token no corresponde al equipo")

    license_key = token_payload.get("license_key")
    now = _utc_now()

    conn = _connect()
    try:
        license_row = conn.execute("SELECT * FROM licenses WHERE license_key=?", (license_key,)).fetchone()
        if not license_row:
            raise HTTPException(status_code=404, detail="Licencia inexistente")

        if license_row["status"] != "active":
            raise HTTPException(status_code=403, detail="Licencia revocada")

        expires_at = _parse_iso(license_row["expires_at"])
        if expires_at and now > expires_at:
            raise HTTPException(status_code=403, detail="Licencia expirada")

        activation = conn.execute(
            "SELECT * FROM activations WHERE license_key=? AND device_id=?",
            (license_key, payload.device_id),
        ).fetchone()

        if not activation or activation["status"] != "active":
            raise HTTPException(status_code=403, detail="Activacion revocada o inexistente")

        conn.execute(
            "UPDATE activations SET last_seen=? WHERE license_key=? AND device_id=?",
            (_iso(now), license_key, payload.device_id),
        )
        conn.execute(
            "UPDATE licenses SET updated_at=? WHERE license_key=?",
            (_iso(now), license_key),
        )
        conn.commit()
    finally:
        conn.close()

    refreshed_payload = {
        "license_key": license_key,
        "device_id": payload.device_id,
        "exp": _iso(now + timedelta(hours=TOKEN_HOURS)),
    }

    return {
        "status": "active",
        "message": "Licencia valida",
        "token": _sign(refreshed_payload),
        "next_check_at": _iso(now + timedelta(hours=CHECK_HOURS)),
        "grace_until": _iso(now + timedelta(hours=GRACE_HOURS)),
    }

