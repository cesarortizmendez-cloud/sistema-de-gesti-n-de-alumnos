# ============================================
# modulos/repo_notas.py
# Guardar notas (UPSERT) + obtener notas por inscripción
# ============================================

from typing import Any, Dict, List, Optional
from .bd_sqlite import obtener_conexion
from .validaciones import validar_nota
from .repo_logs import registrar_evento


def _fila_a_dict(fila) -> Dict[str, Any]:
    return dict(fila) if fila else {}


def obtener_notas_por_inscripcion(inscripcion_id: int) -> List[Dict[str, Any]]:
    """
    Retorna lista:
      - evaluacion_id
      - nombre evaluación
      - porcentaje
      - nota (si existe)
    Útil para mostrar pantalla de notas.
    """
    conn = obtener_conexion()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT
                e.evaluacion_id,
                e.nombre,
                e.porcentaje,
                COALESCE(n.nota, 0) AS nota
            FROM evaluaciones e
            LEFT JOIN notas n
                ON n.evaluacion_id = e.evaluacion_id
               AND n.inscripcion_id = ?
            WHERE e.curso_id = (SELECT curso_id FROM inscripciones WHERE inscripcion_id=?)
            ORDER BY e.nombre ASC
            """,
            (int(inscripcion_id), int(inscripcion_id)),
        )
        return [_fila_a_dict(f) for f in cur.fetchall()]
    finally:
        conn.close()


def guardar_nota(inscripcion_id: int, evaluacion_id: int, nota: float) -> None:
    """
    Guarda o actualiza nota (UPSERT).
    """
    nota = validar_nota(nota)

    conn = obtener_conexion()
    try:
        cur = conn.cursor()

        # Intentamos UPDATE; si no existe, INSERT
        cur.execute(
            """
            UPDATE notas
            SET nota=?
            WHERE inscripcion_id=? AND evaluacion_id=?
            """,
            (float(nota), int(inscripcion_id), int(evaluacion_id)),
        )

        if cur.rowcount == 0:
            cur.execute(
                """
                INSERT INTO notas(inscripcion_id, evaluacion_id, nota)
                VALUES(?,?,?)
                """,
                (int(inscripcion_id), int(evaluacion_id), float(nota)),
            )

        conn.commit()
        registrar_evento("notas", "GUARDAR", f"inscripcion_id={inscripcion_id} evaluacion_id={evaluacion_id} nota={nota}")
    finally:
        conn.close()


def obtener_promedio_inscripcion(inscripcion_id: int) -> Optional[Dict[str, Any]]:
    """Lee promedio ponderado desde la vista."""
    conn = obtener_conexion()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM vw_promedios_ponderados WHERE inscripcion_id=?",
            (int(inscripcion_id),),
        )
        fila = cur.fetchone()
        return _fila_a_dict(fila) if fila else None
    finally:
        conn.close()
