# ============================================
# modulos/bd_sqlite.py
# SQLite: conexión + creación de tablas + migración (semestre -> periodo)
# ============================================

import sqlite3  # Librería estándar para SQLite
from datetime import datetime  # Para obtener el año actual (para periodo por defecto)

from .config import ruta_db  # Ruta segura donde se guarda la BD (AppData)


def obtener_conexion() -> sqlite3.Connection:
    """
    Abre una conexión a la BD SQLite.
    - row_factory permite acceder a columnas por nombre (fila["columna"])
    - foreign_keys activa claves foráneas en SQLite
    """
    conn = sqlite3.connect(ruta_db())  # Abre/crea el archivo .db si no existe
    conn.row_factory = sqlite3.Row  # Filas tipo diccionario por nombre de columna
    conn.execute("PRAGMA foreign_keys = ON;")  # Activa integridad referencial
    return conn


def _tabla_existe(conn: sqlite3.Connection, nombre_tabla: str) -> bool:
    """Devuelve True si la tabla existe en SQLite."""
    cur = conn.cursor()
    cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (nombre_tabla,),
    )
    return cur.fetchone() is not None


def _columna_existe(conn: sqlite3.Connection, nombre_tabla: str, nombre_columna: str) -> bool:
    """Devuelve True si la columna existe dentro de la tabla."""
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({nombre_tabla})")  # Lista columnas de la tabla
    cols = [r["name"] for r in cur.fetchall()]  # Extraemos nombres de columnas
    return nombre_columna in cols


def _crear_tablas_si_no_existen(conn: sqlite3.Connection) -> None:
    """
    Crea tablas base si NO existen.
    IMPORTANTE:
    - Si ya existen, SQLite NO las modifica (por eso necesitamos migración aparte).
    """
    cur = conn.cursor()

    # Universidades
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS universidades (
            universidad_id  INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre          TEXT NOT NULL UNIQUE
        )
        """
    )

    # Carreras
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS carreras (
            carrera_id       INTEGER PRIMARY KEY AUTOINCREMENT,
            universidad_id   INTEGER NOT NULL,
            nombre           TEXT NOT NULL,
            UNIQUE(universidad_id, nombre),
            FOREIGN KEY (universidad_id) REFERENCES universidades(universidad_id) ON DELETE CASCADE
        )
        """
    )

    # Cursos (nuevo: periodo)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS cursos (
            curso_id     INTEGER PRIMARY KEY AUTOINCREMENT,
            carrera_id   INTEGER NOT NULL,
            periodo      TEXT NOT NULL CHECK (periodo GLOB '[0-9][0-9][0-9][0-9]-[12]'),
            nombre       TEXT NOT NULL,
            codigo       TEXT,
            UNIQUE(carrera_id, periodo, nombre),
            FOREIGN KEY (carrera_id) REFERENCES carreras(carrera_id) ON DELETE CASCADE
        )
        """
    )

    # Alumnos (nuevo: periodo)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS alumnos (
            alumno_id        INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_alumno      TEXT NOT NULL CHECK (tipo_alumno IN ('Pregrado','Postgrado','Intercambio')),
            rut              TEXT NOT NULL,
            rut_normalizado  TEXT NOT NULL UNIQUE,
            nombres          TEXT NOT NULL,
            apellidos        TEXT NOT NULL,
            email            TEXT,
            telefono         TEXT,
            universidad_id   INTEGER NOT NULL,
            carrera_id       INTEGER NOT NULL,
            periodo          TEXT NOT NULL CHECK (periodo GLOB '[0-9][0-9][0-9][0-9]-[12]'),
            estado           INTEGER NOT NULL DEFAULT 1 CHECK (estado IN (0,1)),
            nombre_busqueda  TEXT NOT NULL,
            fecha_registro   TEXT NOT NULL DEFAULT (datetime('now')),
            fecha_actualiza  TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (universidad_id) REFERENCES universidades(universidad_id) ON DELETE RESTRICT,
            FOREIGN KEY (carrera_id) REFERENCES carreras(carrera_id) ON DELETE RESTRICT
        )
        """
    )

    # Inscripciones
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS inscripciones (
            inscripcion_id INTEGER PRIMARY KEY AUTOINCREMENT,
            alumno_id      INTEGER NOT NULL,
            curso_id       INTEGER NOT NULL,
            UNIQUE(alumno_id, curso_id),
            FOREIGN KEY (alumno_id) REFERENCES alumnos(alumno_id) ON DELETE CASCADE,
            FOREIGN KEY (curso_id) REFERENCES cursos(curso_id) ON DELETE CASCADE
        )
        """
    )

    # Evaluaciones
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS evaluaciones (
            evaluacion_id INTEGER PRIMARY KEY AUTOINCREMENT,
            curso_id      INTEGER NOT NULL,
            nombre        TEXT NOT NULL,
            porcentaje    REAL NOT NULL CHECK (porcentaje > 0 AND porcentaje <= 100),
            UNIQUE(curso_id, nombre),
            FOREIGN KEY (curso_id) REFERENCES cursos(curso_id) ON DELETE CASCADE
        )
        """
    )

    # Notas
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS notas (
            nota_id        INTEGER PRIMARY KEY AUTOINCREMENT,
            inscripcion_id INTEGER NOT NULL,
            evaluacion_id  INTEGER NOT NULL,
            nota           REAL NOT NULL CHECK (nota >= 0 AND nota <= 7),
            UNIQUE(inscripcion_id, evaluacion_id),
            FOREIGN KEY (inscripcion_id) REFERENCES inscripciones(inscripcion_id) ON DELETE CASCADE,
            FOREIGN KEY (evaluacion_id) REFERENCES evaluaciones(evaluacion_id) ON DELETE CASCADE
        )
        """
    )

    # Logs
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS logs_eventos (
            log_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_hora  TEXT NOT NULL DEFAULT (datetime('now')),
            modulo      TEXT NOT NULL,
            accion      TEXT NOT NULL,
            detalle     TEXT,
            nivel       TEXT NOT NULL DEFAULT 'INFO' CHECK (nivel IN ('INFO','WARN','ERROR'))
        )
        """
    )


def _migrar_semestre_a_periodo(conn: sqlite3.Connection) -> None:
    """
    Migración suave:
    - Si la BD era antigua (tenía semestre y no periodo), agregamos la columna periodo.
    - No se puede inferir año real desde 'semestre' antiguo, así que asignamos un valor por defecto.
    """
    cur = conn.cursor()

    # Periodo por defecto (puedes cambiarlo si quieres)
    periodo_default = f"{datetime.now().year}-1"  # Ej: 2026-1

    # ---- Cursos: agregar columna periodo si falta ----
    if _tabla_existe(conn, "cursos") and not _columna_existe(conn, "cursos", "periodo"):
        cur.execute("ALTER TABLE cursos ADD COLUMN periodo TEXT")  # Agrega columna a tabla existente
        # Rellenamos valores vacíos con el periodo por defecto
        cur.execute(
            "UPDATE cursos SET periodo=? WHERE periodo IS NULL OR TRIM(periodo)=''",
            (periodo_default,),
        )

    # ---- Alumnos: agregar columna periodo si falta ----
    if _tabla_existe(conn, "alumnos") and not _columna_existe(conn, "alumnos", "periodo"):
        cur.execute("ALTER TABLE alumnos ADD COLUMN periodo TEXT")
        cur.execute(
            "UPDATE alumnos SET periodo=? WHERE periodo IS NULL OR TRIM(periodo)=''",
            (periodo_default,),
        )


def _crear_indices_triggers_vistas(conn: sqlite3.Connection) -> None:
    """
    Crea índices, trigger y vista.
    IMPORTANTE:
    - Esto se ejecuta después de migrar, para asegurar que 'periodo' exista.
    """
    cur = conn.cursor()

    # Índices
    cur.execute("CREATE INDEX IF NOT EXISTS idx_carreras_universidad ON carreras(universidad_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_cursos_carrera ON cursos(carrera_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_cursos_periodo ON cursos(periodo)")

    cur.execute("CREATE INDEX IF NOT EXISTS idx_alumnos_nombre ON alumnos(nombre_busqueda)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_alumnos_carrera ON alumnos(carrera_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_alumnos_universidad ON alumnos(universidad_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_alumnos_periodo ON alumnos(periodo)")

    cur.execute("CREATE INDEX IF NOT EXISTS idx_insc_alumno ON inscripciones(alumno_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_insc_curso ON inscripciones(curso_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_eval_curso ON evaluaciones(curso_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_notas_insc ON notas(inscripcion_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_notas_eval ON notas(evaluacion_id)")

    # Trigger: actualiza fecha_actualiza al modificar alumno
    cur.execute(
        """
        CREATE TRIGGER IF NOT EXISTS trg_alumnos_fecha
        AFTER UPDATE ON alumnos
        FOR EACH ROW
        BEGIN
            UPDATE alumnos
            SET fecha_actualiza = datetime('now')
            WHERE alumno_id = OLD.alumno_id;
        END;
        """
    )

    # Vista: promedios ponderados por inscripción
    cur.execute(
        """
        CREATE VIEW IF NOT EXISTS vw_promedios_ponderados AS
        SELECT
            i.inscripcion_id,
            i.alumno_id,
            i.curso_id,
            SUM(COALESCE(n.nota,0) * e.porcentaje) / 100.0 AS promedio_ponderado,
            SUM(e.porcentaje) AS suma_porcentajes
        FROM inscripciones i
        JOIN evaluaciones e ON e.curso_id = i.curso_id
        LEFT JOIN notas n ON n.inscripcion_id = i.inscripcion_id AND n.evaluacion_id = e.evaluacion_id
        GROUP BY i.inscripcion_id, i.alumno_id, i.curso_id;
        """
    )


def inicializar_bd() -> None:
    """
    Inicialización completa:
    1) Crear tablas si no existen
    2) Migrar BD antigua agregando columna 'periodo' si falta
    3) Crear índices / triggers / vistas
    """
    conn = obtener_conexion()
    try:
        _crear_tablas_si_no_existen(conn)
        _migrar_semestre_a_periodo(conn)
        _crear_indices_triggers_vistas(conn)
        conn.commit()
    finally:
        conn.close()
