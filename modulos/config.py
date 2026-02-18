# ============================================
# modulos/config.py
# Manejo de rutas para guardar BD en un lugar seguro (AppData)
# ============================================

import os
import sys


def ruta_base_appdata() -> str:
    """
    Retorna una carpeta segura para escritura.
    - En Windows: %APPDATA%\SGA
    - Si no existe APPDATA (raro), usa carpeta del usuario.
    """
    base = os.environ.get("APPDATA") or os.path.expanduser("~")
    carpeta = os.path.join(base, "SGA")
    os.makedirs(carpeta, exist_ok=True)
    return carpeta


def ruta_data() -> str:
    """
    Carpeta 'data' dentro de AppData para guardar la BD.
    """
    carpeta = os.path.join(ruta_base_appdata(), "data")
    os.makedirs(carpeta, exist_ok=True)
    return carpeta


def ruta_db() -> str:
    """
    Ruta completa del archivo SQLite.
    """
    return os.path.join(ruta_data(), "sga.db")


def ruta_recurso(rel_path: str) -> str:
    """
    Ayuda para PyInstaller:
    - Si está empaquetado (onefile), usa sys._MEIPASS
    - Si no, usa ruta normal del proyecto
    """
    base = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base, rel_path)
