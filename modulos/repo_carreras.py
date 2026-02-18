# ============================================
# modulos/repo_carreras.py
# CRUD de carreras (por universidad)
# ============================================

from typing import Any, Dict, List, Optional
from .bd_sqlite import obtener_conexion
from .validaciones import normalizar_texto
from .repo_logs import registrar_evento


def _fila_a_dict(fila) -> Dict[str, Any]:
    return dict(fila) if fila else {}


def listar_carreras_por_universidad(universidad_id: int) -> List[Dict[str, Any]]:
    """Lista carreras de una universidad."""
    conn = obtener_conexion()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM carreras WHERE universidad_id=? ORDER BY nombre ASC",
            (int(universidad_id),),
        )
        return [_fila_a_dict(f) for f in cur.fetchall()]
    finally:
        conn.close()


def obtener_carrera(carrera_id: int) -> Optional[Dict[str, Any]]:
    conn = obtener_conexion()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM carreras WHERE carrera_id=?", (int(carrera_id),))
        fila = cur.fetchone()
        return _fila_a_dict(fila) if fila else None
    finally:
        conn.close()


def crear_carrera(universidad_id: int, nombre: str) -> int:
    """Crea carrera y retorna carrera_id."""
    nombre = normalizar_texto(nombre)
    if not nombre:
        raise ValueError("El nombre de la carrera es obligatorio.")

    conn = obtener_conexion()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO carreras(universidad_id, nombre) VALUES(?,?)",
            (int(universidad_id), nombre),
        )
        conn.commit()
        cid = int(cur.lastrowid)
        registrar_evento("carreras", "CREAR", f"carrera_id={cid} universidad_id={universidad_id} nombre='{nombre}'")
        return cid
    finally:
        conn.close()


def actualizar_carrera(carrera_id: int, nombre: str) -> bool:
    """Actualiza nombre de carrera."""
    nombre = normalizar_texto(nombre)
    if not nombre:
        raise ValueError("El nombre de la carrera es obligatorio.")

    conn = obtener_conexion()
    try:
        cur = conn.cursor()
        cur.execute(
            "UPDATE carreras SET nombre=? WHERE carrera_id=?",
            (nombre, int(carrera_id)),
        )
        conn.commit()
        ok = cur.rowcount > 0
        if ok:
            registrar_evento("carreras", "ACTUALIZAR", f"carrera_id={carrera_id} nombre='{nombre}'")
        return ok
    finally:
        conn.close()


def eliminar_carrera(carrera_id: int) -> bool:
    """Elimina carrera (si no tiene cursos/alumnos)."""
    conn = obtener_conexion()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM carreras WHERE carrera_id=?", (int(carrera_id),))
        conn.commit()
        ok = cur.rowcount > 0
        if ok:
            registrar_evento("carreras", "ELIMINAR", f"carrera_id={carrera_id}")
        return ok
    finally:
        conn.close()
