from typing import Any, Dict, List, Optional
from .bd_sqlite import obtener_conexion
from .validaciones import normalizar_texto, validar_periodo
from .repo_logs import registrar_evento

def _fila_a_dict(fila) -> Dict[str, Any]:
    return dict(fila) if fila else {}

def listar_cursos_por_carrera(carrera_id: int) -> List[Dict[str, Any]]:
    conn = obtener_conexion()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM cursos WHERE carrera_id=? ORDER BY periodo ASC, nombre ASC",
            (int(carrera_id),),
        )
        return [_fila_a_dict(f) for f in cur.fetchall()]
    finally:
        conn.close()

def listar_cursos_detallados() -> List[Dict[str, Any]]:
    conn = obtener_conexion()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT
                cu.curso_id, cu.nombre AS curso_nombre, cu.codigo, cu.periodo,
                ca.carrera_id, ca.nombre AS carrera_nombre,
                u.universidad_id, u.nombre AS universidad_nombre
            FROM cursos cu
            JOIN carreras ca ON ca.carrera_id = cu.carrera_id
            JOIN universidades u ON u.universidad_id = ca.universidad_id
            ORDER BY u.nombre, ca.nombre, cu.periodo, cu.nombre
            """
        )
        return [_fila_a_dict(f) for f in cur.fetchall()]
    finally:
        conn.close()

def obtener_curso(curso_id: int) -> Optional[Dict[str, Any]]:
    conn = obtener_conexion()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM cursos WHERE curso_id=?", (int(curso_id),))
        fila = cur.fetchone()
        return _fila_a_dict(fila) if fila else None
    finally:
        conn.close()

def crear_curso(carrera_id: int, periodo: str, nombre: str, codigo: str = "") -> int:
    periodo = validar_periodo(periodo)
    nombre = normalizar_texto(nombre)
    codigo = normalizar_texto(codigo)

    if not nombre:
        raise ValueError("El nombre del curso es obligatorio.")

    conn = obtener_conexion()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO cursos(carrera_id, periodo, nombre, codigo)
            VALUES (?,?,?,?)
            """,
            (int(carrera_id), periodo, nombre, (codigo if codigo else None)),
        )
        conn.commit()
        cid = int(cur.lastrowid)
        registrar_evento("cursos", "CREAR", f"curso_id={cid} carrera_id={carrera_id} periodo={periodo} nombre='{nombre}'")
        return cid
    finally:
        conn.close()

def actualizar_curso(curso_id: int, carrera_id: int, periodo: str, nombre: str, codigo: str = "") -> bool:
    periodo = validar_periodo(periodo)
    nombre = normalizar_texto(nombre)
    codigo = normalizar_texto(codigo)

    if not nombre:
        raise ValueError("El nombre del curso es obligatorio.")

    conn = obtener_conexion()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE cursos
            SET carrera_id=?, periodo=?, nombre=?, codigo=?
            WHERE curso_id=?
            """,
            (int(carrera_id), periodo, nombre, (codigo if codigo else None), int(curso_id)),
        )
        conn.commit()
        ok = cur.rowcount > 0
        if ok:
            registrar_evento("cursos", "ACTUALIZAR", f"curso_id={curso_id} periodo={periodo} nombre='{nombre}'")
        return ok
    finally:
        conn.close()

def eliminar_curso(curso_id: int) -> bool:
    conn = obtener_conexion()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM cursos WHERE curso_id=?", (int(curso_id),))
        conn.commit()
        ok = cur.rowcount > 0
        if ok:
            registrar_evento("cursos", "ELIMINAR", f"curso_id={curso_id}")
        return ok
    finally:
        conn.close()
