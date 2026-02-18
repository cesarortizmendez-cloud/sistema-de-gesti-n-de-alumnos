# ============================================
# modulos/repo_universidades.py
# CRUD de universidades
# ============================================

from typing import Any, Dict, List, Optional
from .bd_sqlite import obtener_conexion
from .validaciones import normalizar_texto
from .repo_logs import registrar_evento


def _fila_a_dict(fila) -> Dict[str, Any]:
    """Convierte sqlite3.Row a dict."""
    return dict(fila) if fila else {}


def listar_universidades() -> List[Dict[str, Any]]:
    """Retorna universidades ordenadas por nombre."""
    conn = obtener_conexion()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM universidades ORDER BY nombre ASC")
        return [_fila_a_dict(f) for f in cur.fetchall()]
    finally:
        conn.close()


def obtener_universidad(universidad_id: int) -> Optional[Dict[str, Any]]:
    """Obtiene una universidad por ID."""
    conn = obtener_conexion()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM universidades WHERE universidad_id=?", (int(universidad_id),))
        fila = cur.fetchone()
        return _fila_a_dict(fila) if fila else None
    finally:
        conn.close()


def crear_universidad(nombre: str) -> int:
    """Crea una universidad y retorna su ID."""
    nombre = normalizar_texto(nombre)
    if not nombre:
        raise ValueError("El nombre de la universidad es obligatorio.")

    conn = obtener_conexion()
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO universidades(nombre) VALUES(?)", (nombre,))
        conn.commit()
        uid = int(cur.lastrowid)
        registrar_evento("universidades", "CREAR", f"universidad_id={uid} nombre='{nombre}'")
        return uid
    finally:
        conn.close()


def actualizar_universidad(universidad_id: int, nombre: str) -> bool:
    """Actualiza nombre de universidad."""
    nombre = normalizar_texto(nombre)
    if not nombre:
        raise ValueError("El nombre de la universidad es obligatorio.")

    conn = obtener_conexion()
    try:
        cur = conn.cursor()
        cur.execute(
            "UPDATE universidades SET nombre=? WHERE universidad_id=?",
            (nombre, int(universidad_id)),
        )
        conn.commit()
        ok = cur.rowcount > 0
        if ok:
            registrar_evento("universidades", "ACTUALIZAR", f"universidad_id={universidad_id} nombre='{nombre}'")
        return ok
    finally:
        conn.close()


def eliminar_universidad(universidad_id: int) -> bool:
    """Elimina universidad (si no tiene carreras asociadas)."""
    conn = obtener_conexion()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM universidades WHERE universidad_id=?", (int(universidad_id),))
        conn.commit()
        ok = cur.rowcount > 0
        if ok:
            registrar_evento("universidades", "ELIMINAR", f"universidad_id={universidad_id}")
        return ok
    finally:
        conn.close()
