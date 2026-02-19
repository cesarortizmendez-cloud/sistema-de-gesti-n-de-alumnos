# ============================================  # Separador visual
# modulos/config.py                              # Nombre del módulo
# Configuración de rutas para la app:            # Descripción
# - Base de datos SQLite en carpeta del usuario  # Evita problemas de permisos al usar .exe
# - Carpeta de exportaciones (Excel/PDF)         # Lugar recomendado para guardar archivos
# ============================================  # Separador visual

import os                                       # Acceso a variables de entorno (APPDATA)          # noqa: E501
from pathlib import Path                        # Manejo de rutas de forma segura (Windows/Linux)  # noqa: E501


APP_NOMBRE = "SGA"                              # Nombre corto de la aplicación (para carpetas)    # noqa: E501
DB_NOMBRE = "sga.db"                            # Nombre del archivo SQLite                        # noqa: E501


def carpeta_app() -> Path:                      # Devuelve carpeta base donde la app guarda datos   # noqa: E501
    appdata = os.getenv("APPDATA")              # En Windows: ruta tipo C:\Users\X\AppData\Roaming  # noqa: E501
    if appdata:                                 # Si existe APPDATA (caso normal en Windows)        # noqa: E501
        base = Path(appdata)                    # Convierte a Path                                  # noqa: E501
    else:                                       # Si no existe (otro SO o caso raro)                # noqa: E501
        base = Path.home() / ".config"          # Alternativa estándar en Linux/Mac                 # noqa: E501

    ruta = base / APP_NOMBRE                    # Carpeta final: ...\APPDATA\SGA                    # noqa: E501
    ruta.mkdir(parents=True, exist_ok=True)     # Crea la carpeta si no existe                      # noqa: E501
    return ruta                                 # Retorna la ruta lista para usar                   # noqa: E501


def ruta_db() -> str:                           # Entrega la ruta completa del archivo .db          # noqa: E501
    return str(carpeta_app() / DB_NOMBRE)       # Ej: C:\Users\X\AppData\Roaming\SGA\sga.db         # noqa: E501


def carpeta_exports() -> str:                   # Entrega carpeta recomendada para exportaciones    # noqa: E501
    ruta = carpeta_app() / "exports"            # Carpeta exports dentro de AppData\SGA             # noqa: E501
    ruta.mkdir(parents=True, exist_ok=True)     # Crea si no existe                                 # noqa: E501
    return str(ruta)                            # Retorna como string (para usar en filedialog)     # noqa: E501
