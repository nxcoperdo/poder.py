import hashlib
import os
import platform
import subprocess
import uuid


def _safe_wmic_uuid() -> str:
    # Obtiene UUID de hardware en Windows; si falla, retorna vacio sin romper flujo.
    try:
        output = subprocess.check_output(
            ["wmic", "csproduct", "get", "uuid"],
            stderr=subprocess.DEVNULL,
            timeout=2,
        ).decode("utf-8", errors="ignore")
    except Exception:
        return ""

    lines = [line.strip() for line in output.splitlines() if line.strip()]
    if len(lines) < 2:
        return ""

    return lines[1]


def get_device_fingerprint() -> str:
    # Combina identificadores estables del equipo y los resume con SHA-256.
    parts = [
        os.getenv("COMPUTERNAME", ""),
        platform.system(),
        platform.release(),
        platform.machine(),
        str(uuid.getnode()),
        _safe_wmic_uuid(),
    ]

    raw = "|".join(parts).encode("utf-8", errors="ignore")
    return hashlib.sha256(raw).hexdigest()

