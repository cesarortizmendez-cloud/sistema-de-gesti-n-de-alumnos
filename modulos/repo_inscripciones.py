# ============================================
# modulos/repo_inscripciones.py
# Inscribir alumnos a cursos + listar inscritos
# ============================================

from typing import Any, Dict, List, Optional
from .bd_sqlite import obtener_conexion
from .repo_logs import registrar_evento


def _fila_a_dict(fila) -> Dict[str, Any]:
    return dict(fila) if fila else {}


def inscribir_alumno(alumno_id: int, curso_id: int) -> int:
    """Crea inscripción alumno-curso y retorna inscripcion_id."""
    conn = obtener_conexion()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO inscripciones(alumno_id, curso_id) VALUES(?,?)",
            (int(alumno_id), int(curso_id)),
        )
        conn.commit()
        iid = int(cur.lastrowid)
        registrar_evento("inscripciones", "CREAR", f"inscripcion_id={iid} alumno_id={alumno_id} curso_id={curso_id}")
        return iid
    finally:
        conn.close()


def desinscribir(inscripcion_id: int) -> bool:
    """Elimina inscripción (borra notas por cascada)."""
    conn = obtener_conexion()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM inscripciones WHERE inscripcion_id=?", (int(inscripcion_id),))
        conn.commit()
        ok = cur.rowcount > 0
        if ok:
            registrar_evento("inscripciones", "ELIMINAR", f"inscripcion_id={inscripcion_id}")
        return ok
    finally:
        conn.close()


def listar_inscritos_por_curso(curso_id: int) -> List[Dict[str, Any]]:
    """
    Lista alumnos inscritos en un curso, incluyendo promedio ponderado (vista).
    """
    conn = obtener_conexion()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT
                i.inscripcion_id,
                a.alumno_id, a.rut, a.nombres, a.apellidos, a.email, a.semestre, a.estado,
                vp.promedio_ponderado, vp.suma_porcentajes
            FROM inscripciones i
            JOIN alumnos a ON a.alumno_id = i.alumno_id
            LEFT JOIN vw_promedios_ponderados vp ON vp.inscripcion_id = i.inscripcion_id
            WHERE i.curso_id=?
            ORDER BY a.apellidos, a.nombres
            """,
            (int(curso_id),),
        )
        return [_fila_a_dict(f) for f in cur.fetchall()]
    finally:
        conn.close()


def obtener_inscripcion(alumno_id: int, curso_id: int) -> Optional[Dict[str, Any]]:
    """Devuelve la inscripción si existe."""
    conn = obtener_conexion()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM inscripciones WHERE alumno_id=? AND curso_id=?",
            (int(alumno_id), int(curso_id)),
        )
        fila = cur.fetchone()
        return _fila_a_dict(fila) if fila else None
    finally:
        conn.close()
