# ============================================
# modulos/repo_notas.py
# Repositorio de NOTAS (solo lógica de BD, SIN Tkinter)
#
# Funciones:
# - obtener_notas_por_inscripcion(inscripcion_id)
# - guardar_nota(inscripcion_id, evaluacion_id, nota)
# - obtener_promedio_inscripcion(inscripcion_id)
# - obtener_reporte_notas_por_curso(curso_id)
# ============================================

from typing import Any, Dict, List, Optional
from .bd_sqlite import obtener_conexion
from .validaciones import validar_nota
from .repo_logs import registrar_evento


def _fila_a_dict(fila) -> Dict[str, Any]:
    return dict(fila) if fila else {}


def obtener_notas_por_inscripcion(inscripcion_id: int) -> List[Dict[str, Any]]:
    """
    Devuelve:
      - evaluacion_id, nombre, porcentaje, nota
    Para TODAS las evaluaciones del curso asociado a la inscripción.
    Si no existe nota, devuelve 0.
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
            WHERE e.curso_id = (
                SELECT curso_id
                FROM inscripciones
                WHERE inscripcion_id = ?
            )
            ORDER BY e.nombre ASC
            """,
            (int(inscripcion_id), int(inscripcion_id)),
        )
        return [_fila_a_dict(f) for f in cur.fetchall()]
    finally:
        conn.close()


def guardar_nota(inscripcion_id: int, evaluacion_id: int, nota: float) -> None:
    """
    Guarda o actualiza una nota (UPSERT manual):
    - intenta UPDATE
    - si no actualiza nada, INSERT
    """
    nota = validar_nota(nota)

    conn = obtener_conexion()
    try:
        cur = conn.cursor()

        cur.execute(
            """
            UPDATE notas
            SET nota = ?
            WHERE inscripcion_id = ? AND evaluacion_id = ?
            """,
            (float(nota), int(inscripcion_id), int(evaluacion_id)),
        )

        if cur.rowcount == 0:
            cur.execute(
                """
                INSERT INTO notas(inscripcion_id, evaluacion_id, nota)
                VALUES (?,?,?)
                """,
                (int(inscripcion_id), int(evaluacion_id), float(nota)),
            )

        conn.commit()

        registrar_evento(
            "notas",
            "GUARDAR",
            f"inscripcion_id={inscripcion_id} evaluacion_id={evaluacion_id} nota={nota}",
        )
    finally:
        conn.close()


def obtener_promedio_inscripcion(inscripcion_id: int) -> Optional[Dict[str, Any]]:
    """
    Lee promedio ponderado desde la vista vw_promedios_ponderados.
    """
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


def obtener_reporte_notas_por_curso(curso_id: int) -> Dict[str, Any]:
    """
    Reporte completo (alumnos x evaluaciones) para exportar Excel/PDF.
    Retorna:
      { "evaluaciones": [...], "filas": [...] }
    """
    conn = obtener_conexion()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT
                i.inscripcion_id,
                a.alumno_id,
                a.rut,
                a.nombres,
                a.apellidos,
                a.email,

                e.evaluacion_id,
                e.nombre AS evaluacion_nombre,
                e.porcentaje,

                COALESCE(n.nota, 0) AS nota,

                COALESCE(vp.promedio_ponderado, 0) AS promedio_ponderado,
                COALESCE(vp.suma_porcentajes, 0) AS suma_porcentajes
            FROM inscripciones i
            JOIN alumnos a ON a.alumno_id = i.alumno_id
            JOIN evaluaciones e ON e.curso_id = i.curso_id
            LEFT JOIN notas n
                ON n.inscripcion_id = i.inscripcion_id
               AND n.evaluacion_id = e.evaluacion_id
            LEFT JOIN vw_promedios_ponderados vp
                ON vp.inscripcion_id = i.inscripcion_id
            WHERE i.curso_id = ?
            ORDER BY a.apellidos, a.nombres, e.nombre
            """,
            (int(curso_id),),
        )

        rows = cur.fetchall()

        evaluaciones: List[Dict[str, Any]] = []
        eval_seen = set()
        filas_dict: Dict[int, Dict[str, Any]] = {}

        for r in rows:
            insc_id = int(r["inscripcion_id"])
            eval_id = int(r["evaluacion_id"])

            if eval_id not in eval_seen:
                eval_seen.add(eval_id)
                evaluaciones.append(
                    {
                        "evaluacion_id": eval_id,
                        "nombre": r["evaluacion_nombre"],
                        "porcentaje": float(r["porcentaje"]),
                    }
                )

            if insc_id not in filas_dict:
                filas_dict[insc_id] = {
                    "inscripcion_id": insc_id,
                    "alumno_id": int(r["alumno_id"]),
                    "rut": r["rut"],
                    "nombres": r["nombres"],
                    "apellidos": r["apellidos"],
                    "email": r["email"],
                    "promedio_ponderado": float(r["promedio_ponderado"] or 0),
                    "suma_porcentajes": float(r["suma_porcentajes"] or 0),
                    "notas": {},
                }

            filas_dict[insc_id]["notas"][eval_id] = float(r["nota"] or 0)

        filas = list(filas_dict.values())
        return {"evaluaciones": evaluaciones, "filas": filas}

    finally:
        conn.close()
