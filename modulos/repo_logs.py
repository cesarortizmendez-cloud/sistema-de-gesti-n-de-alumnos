# ============================================
# modulos/repo_logs.py
# Registro de eventos en la tabla logs_eventos
# ============================================

from .bd_sqlite import obtener_conexion


def registrar_evento(modulo: str, accion: str, detalle: str = "", nivel: str = "INFO") -> None:
    """
    Inserta un registro en logs_eventos.
    Se usa para auditoría básica del sistema.
    """
    conn = obtener_conexion()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO logs_eventos (modulo, accion, detalle, nivel)
            VALUES (?, ?, ?, ?)
            """,
            (modulo, accion, detalle, nivel),
        )
        conn.commit()
    finally:
        conn.close()
