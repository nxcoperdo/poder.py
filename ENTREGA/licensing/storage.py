import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

APP_NAME = "AsistenteCajaPro"
STATE_FILE_NAME = "license_state.json"


def get_data_dir() -> Path:
    # Permite sobrescribir la ruta durante pruebas o despliegues especiales.
    custom_dir = os.getenv("ASISTENTE_DATA_DIR")
    if custom_dir:
        return Path(custom_dir)

    # En Windows se prioriza APPDATA para mantener el estado por usuario.
    appdata = os.getenv("APPDATA")
    if appdata:
        return Path(appdata) / APP_NAME

    # Fallback multiplataforma en caso de no existir APPDATA.
    return Path.home() / f".{APP_NAME.lower()}"


def get_state_path() -> Path:
    # Ruta completa del archivo JSON de licencia local.
    return get_data_dir() / STATE_FILE_NAME


def load_state() -> Optional[Dict[str, Any]]:
    path = get_state_path()
    if not path.exists():
        return None

    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except Exception:
        # Si el archivo esta corrupto o ilegible se fuerza reactivacion.
        return None

    if isinstance(data, dict):
        return data
    return None


def save_state(state: Dict[str, Any]) -> None:
    data_dir = get_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)

    state_path = get_state_path()
    temp_path = state_path.with_suffix(".tmp")

    with temp_path.open("w", encoding="utf-8") as file:
        json.dump(state, file, ensure_ascii=True, indent=2)

    # Reemplazo atomico para evitar archivos truncados en cortes inesperados.
    temp_path.replace(state_path)

