# ============================================
# modulos/repo_evaluaciones.py
# CRUD de evaluaciones por curso (con validación de suma %)
# ============================================

from typing import Any, Dict, List, Optional
from .bd_sqlite import obtener_conexion
from .validaciones import normalizar_texto, validar_porcentaje
from .repo_logs import registrar_evento


def _fila_a_dict(fila) -> Dict[str, Any]:
    return dict(fila) if fila else {}


def listar_evaluaciones(curso_id: int) -> List[Dict[str, Any]]:
    """Lista evaluaciones de un curso."""
    conn = obtener_conexion()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM evaluaciones WHERE curso_id=? ORDER BY nombre ASC",
            (int(curso_id),),
        )
        return [_fila_a_dict(f) for f in cur.fetchall()]
    finally:
        conn.close()


def obtener_evaluacion(evaluacion_id: int) -> Optional[Dict[str, Any]]:
    conn = obtener_conexion()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM evaluaciones WHERE evaluacion_id=?", (int(evaluacion_id),))
        fila = cur.fetchone()
        return _fila_a_dict(fila) if fila else None
    finally:
        conn.close()


def suma_porcentajes(curso_id: int, excluir_evaluacion_id: int | None = None) -> float:
    """
    Calcula suma de porcentajes del curso.
    Permite excluir una evaluación (útil en update).
    """
    conn = obtener_conexion()
    try:
        cur = conn.cursor()
        if excluir_evaluacion_id is None:
            cur.execute("SELECT COALESCE(SUM(porcentaje),0) AS s FROM evaluaciones WHERE curso_id=?", (int(curso_id),))
        else:
            cur.execute(
                "SELECT COALESCE(SUM(porcentaje),0) AS s FROM evaluaciones WHERE curso_id=? AND evaluacion_id<>?",
                (int(curso_id), int(excluir_evaluacion_id)),
            )
        return float(cur.fetchone()["s"])
    finally:
        conn.close()


def crear_evaluacion(curso_id: int, nombre: str, porcentaje: float) -> int:
    """
    Crea evaluación validando:
    - nombre obligatorio
    - porcentaje (0, 100]
    - suma porcentajes no debe superar 100
    """
    nombre = normalizar_texto(nombre)
    if not nombre:
        raise ValueError("El nombre de la evaluación es obligatorio.")
    porcentaje = validar_porcentaje(porcentaje)

    s = suma_porcentajes(curso_id)
    if s + porcentaje > 100.00001:
        raise ValueError(f"La suma de porcentajes supera 100%. Actual: {s:.2f}%, intento agregar: {porcentaje:.2f}%.")

    conn = obtener_conexion()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO evaluaciones(curso_id, nombre, porcentaje) VALUES(?,?,?)",
            (int(curso_id), nombre, float(porcentaje)),
        )
        conn.commit()
        eid = int(cur.lastrowid)
        registrar_evento("evaluaciones", "CREAR", f"evaluacion_id={eid} curso_id={curso_id} {nombre} {porcentaje}%")
        return eid
    finally:
        conn.close()


def actualizar_evaluacion(evaluacion_id: int, curso_id: int, nombre: str, porcentaje: float) -> bool:
    """Actualiza evaluación con la misma validación de suma porcentajes."""
    nombre = normalizar_texto(nombre)
    if not nombre:
        raise ValueError("El nombre de la evaluación es obligatorio.")
    porcentaje = validar_porcentaje(porcentaje)

    s = suma_porcentajes(curso_id, excluir_evaluacion_id=evaluacion_id)
    if s + porcentaje > 100.00001:
        raise ValueError(f"La suma de porcentajes supera 100%. Actual(sin esta): {s:.2f}%, nuevo: {porcentaje:.2f}%.")

    conn = obtener_conexion()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE evaluaciones
            SET curso_id=?, nombre=?, porcentaje=?
            WHERE evaluacion_id=?
            """,
            (int(curso_id), nombre, float(porcentaje), int(evaluacion_id)),
        )
        conn.commit()
        ok = cur.rowcount > 0
        if ok:
            registrar_evento("evaluaciones", "ACTUALIZAR", f"evaluacion_id={evaluacion_id} {nombre} {porcentaje}%")
        return ok
    finally:
        conn.close()


def eliminar_evaluacion(evaluacion_id: int) -> bool:
    """Elimina evaluación (borra notas asociadas por cascada)."""
    conn = obtener_conexion()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM evaluaciones WHERE evaluacion_id=?", (int(evaluacion_id),))
        conn.commit()
        ok = cur.rowcount > 0
        if ok:
            registrar_evento("evaluaciones", "ELIMINAR", f"evaluacion_id={evaluacion_id}")
        return ok
    finally:
        conn.close()
