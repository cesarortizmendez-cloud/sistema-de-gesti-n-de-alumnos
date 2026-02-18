from typing import Any, Dict, List, Optional
from .bd_sqlite import obtener_conexion
from .validaciones import normalizar_texto, rut_a_normalizado, nombre_busqueda, validar_periodo
from .repo_logs import registrar_evento

def _fila_a_dict(fila) -> Dict[str, Any]:
    return dict(fila) if fila else {}

def listar_alumnos() -> List[Dict[str, Any]]:
    conn = obtener_conexion()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT a.*,
                   u.nombre AS universidad_nombre,
                   c.nombre AS carrera_nombre
            FROM alumnos a
            JOIN universidades u ON u.universidad_id = a.universidad_id
            JOIN carreras c ON c.carrera_id = a.carrera_id
            ORDER BY a.fecha_registro DESC
            """
        )
        return [_fila_a_dict(f) for f in cur.fetchall()]
    finally:
        conn.close()

def buscar_alumnos(texto: str) -> List[Dict[str, Any]]:
    q = normalizar_texto(texto).casefold()
    if not q:
        return listar_alumnos()

    rut_like = rut_a_normalizado(q)

    conn = obtener_conexion()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT a.*,
                   u.nombre AS universidad_nombre,
                   c.nombre AS carrera_nombre
            FROM alumnos a
            JOIN universidades u ON u.universidad_id = a.universidad_id
            JOIN carreras c ON c.carrera_id = a.carrera_id
            WHERE a.nombre_busqueda LIKE ?
               OR a.rut_normalizado LIKE ?
               OR COALESCE(a.email,'') LIKE ?
            ORDER BY a.fecha_registro DESC
            """,
            (f"%{q}%", f"%{rut_like}%", f"%{q}%"),
        )
        return [_fila_a_dict(f) for f in cur.fetchall()]
    finally:
        conn.close()

def obtener_alumno(alumno_id: int) -> Optional[Dict[str, Any]]:
    conn = obtener_conexion()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM alumnos WHERE alumno_id=?", (int(alumno_id),))
        fila = cur.fetchone()
        return _fila_a_dict(fila) if fila else None
    finally:
        conn.close()

def crear_alumno(datos: Dict[str, Any]) -> int:
    tipo = normalizar_texto(datos.get("tipo_alumno"))
    if tipo not in ("Pregrado", "Postgrado", "Intercambio"):
        raise ValueError("tipo_alumno debe ser Pregrado, Postgrado o Intercambio.")

    rut = normalizar_texto(datos.get("rut"))
    rut_norm = rut_a_normalizado(rut)
    if not rut_norm:
        raise ValueError("RUT es obligatorio.")

    nombres = normalizar_texto(datos.get("nombres"))
    apellidos = normalizar_texto(datos.get("apellidos"))
    if not nombres or not apellidos:
        raise ValueError("Nombres y apellidos son obligatorios.")

    email = normalizar_texto(datos.get("email"))
    telefono = normalizar_texto(datos.get("telefono"))

    universidad_id = int(datos.get("universidad_id"))
    carrera_id = int(datos.get("carrera_id"))

    periodo = validar_periodo(datos.get("periodo"))

    estado = 1 if int(datos.get("estado", 1)) == 1 else 0
    nb = nombre_busqueda(nombres, apellidos)

    conn = obtener_conexion()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO alumnos(
                tipo_alumno, rut, rut_normalizado,
                nombres, apellidos,
                email, telefono,
                universidad_id, carrera_id, periodo,
                estado, nombre_busqueda
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                tipo, rut, rut_norm,
                nombres, apellidos,
                (email if email else None),
                (telefono if telefono else None),
                universidad_id, carrera_id, periodo,
                estado, nb,
            ),
        )
        conn.commit()
        aid = int(cur.lastrowid)
        registrar_evento("alumnos", "CREAR", f"alumno_id={aid} rut='{rut}' periodo={periodo}")
        return aid
    finally:
        conn.close()

def actualizar_alumno(alumno_id: int, datos: Dict[str, Any]) -> bool:
    tipo = normalizar_texto(datos.get("tipo_alumno"))
    if tipo not in ("Pregrado", "Postgrado", "Intercambio"):
        raise ValueError("tipo_alumno debe ser Pregrado, Postgrado o Intercambio.")

    rut = normalizar_texto(datos.get("rut"))
    rut_norm = rut_a_normalizado(rut)
    if not rut_norm:
        raise ValueError("RUT es obligatorio.")

    nombres = normalizar_texto(datos.get("nombres"))
    apellidos = normalizar_texto(datos.get("apellidos"))
    if not nombres or not apellidos:
        raise ValueError("Nombres y apellidos son obligatorios.")

    email = normalizar_texto(datos.get("email"))
    telefono = normalizar_texto(datos.get("telefono"))

    universidad_id = int(datos.get("universidad_id"))
    carrera_id = int(datos.get("carrera_id"))

    periodo = validar_periodo(datos.get("periodo"))

    estado = 1 if int(datos.get("estado", 1)) == 1 else 0
    nb = nombre_busqueda(nombres, apellidos)

    conn = obtener_conexion()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE alumnos
            SET tipo_alumno=?,
                rut=?, rut_normalizado=?,
                nombres=?, apellidos=?,
                email=?, telefono=?,
                universidad_id=?, carrera_id=?, periodo=?,
                estado=?, nombre_busqueda=?
            WHERE alumno_id=?
            """,
            (
                tipo,
                rut, rut_norm,
                nombres, apellidos,
                (email if email else None),
                (telefono if telefono else None),
                universidad_id, carrera_id, periodo,
                estado, nb,
                int(alumno_id),
            ),
        )
        conn.commit()
        ok = cur.rowcount > 0
        if ok:
            registrar_evento("alumnos", "ACTUALIZAR", f"alumno_id={alumno_id} periodo={periodo}")
        return ok
    finally:
        conn.close()

def eliminar_alumno(alumno_id: int) -> bool:
    conn = obtener_conexion()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM alumnos WHERE alumno_id=?", (int(alumno_id),))
        conn.commit()
        ok = cur.rowcount > 0
        if ok:
            registrar_evento("alumnos", "ELIMINAR", f"alumno_id={alumno_id}")
        return ok
    finally:
        conn.close()
