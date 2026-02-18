# ============================================
# modulos/bd_sqlite.py
# Conexión SQLite + creación de tablas (init)
# ============================================

import sqlite3

from .config import ruta_db


SQL_INIT = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS universidades (
    universidad_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre          TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS carreras (
    carrera_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    universidad_id   INTEGER NOT NULL,
    nombre           TEXT NOT NULL,
    UNIQUE(universidad_id, nombre),
    FOREIGN KEY (universidad_id) REFERENCES universidades(universidad_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_carreras_universidad ON carreras(universidad_id);

CREATE TABLE IF NOT EXISTS cursos (
    curso_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    carrera_id   INTEGER NOT NULL,
    semestre     INTEGER NOT NULL CHECK (semestre >= 1 AND semestre <= 20),
    nombre       TEXT NOT NULL,
    codigo       TEXT,
    UNIQUE(carrera_id, semestre, nombre),
    FOREIGN KEY (carrera_id) REFERENCES carreras(carrera_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_cursos_carrera ON cursos(carrera_id);
CREATE INDEX IF NOT EXISTS idx_cursos_semestre ON cursos(semestre);

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
    semestre         INTEGER NOT NULL CHECK (semestre >= 1 AND semestre <= 20),
    estado           INTEGER NOT NULL DEFAULT 1 CHECK (estado IN (0,1)),
    nombre_busqueda  TEXT NOT NULL,
    fecha_registro   TEXT NOT NULL DEFAULT (datetime('now')),
    fecha_actualiza  TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (universidad_id) REFERENCES universidades(universidad_id) ON DELETE RESTRICT,
    FOREIGN KEY (carrera_id) REFERENCES carreras(carrera_id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_alumnos_nombre ON alumnos(nombre_busqueda);
CREATE INDEX IF NOT EXISTS idx_alumnos_carrera ON alumnos(carrera_id);
CREATE INDEX IF NOT EXISTS idx_alumnos_universidad ON alumnos(universidad_id);

CREATE TRIGGER IF NOT EXISTS trg_alumnos_fecha
AFTER UPDATE ON alumnos
FOR EACH ROW
BEGIN
    UPDATE alumnos
    SET fecha_actualiza = datetime('now')
    WHERE alumno_id = OLD.alumno_id;
END;

CREATE TABLE IF NOT EXISTS inscripciones (
    inscripcion_id INTEGER PRIMARY KEY AUTOINCREMENT,
    alumno_id      INTEGER NOT NULL,
    curso_id       INTEGER NOT NULL,
    UNIQUE(alumno_id, curso_id),
    FOREIGN KEY (alumno_id) REFERENCES alumnos(alumno_id) ON DELETE CASCADE,
    FOREIGN KEY (curso_id) REFERENCES cursos(curso_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_insc_alumno ON inscripciones(alumno_id);
CREATE INDEX IF NOT EXISTS idx_insc_curso ON inscripciones(curso_id);

CREATE TABLE IF NOT EXISTS evaluaciones (
    evaluacion_id INTEGER PRIMARY KEY AUTOINCREMENT,
    curso_id      INTEGER NOT NULL,
    nombre        TEXT NOT NULL,
    porcentaje    REAL NOT NULL CHECK (porcentaje > 0 AND porcentaje <= 100),
    UNIQUE(curso_id, nombre),
    FOREIGN KEY (curso_id) REFERENCES cursos(curso_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_eval_curso ON evaluaciones(curso_id);

CREATE TABLE IF NOT EXISTS notas (
    nota_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    inscripcion_id INTEGER NOT NULL,
    evaluacion_id  INTEGER NOT NULL,
    nota           REAL NOT NULL CHECK (nota >= 0 AND nota <= 7),
    UNIQUE(inscripcion_id, evaluacion_id),
    FOREIGN KEY (inscripcion_id) REFERENCES inscripciones(inscripcion_id) ON DELETE CASCADE,
    FOREIGN KEY (evaluacion_id) REFERENCES evaluaciones(evaluacion_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_notas_insc ON notas(inscripcion_id);
CREATE INDEX IF NOT EXISTS idx_notas_eval ON notas(evaluacion_id);

CREATE TABLE IF NOT EXISTS logs_eventos (
    log_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha_hora  TEXT NOT NULL DEFAULT (datetime('now')),
    modulo      TEXT NOT NULL,
    accion      TEXT NOT NULL,
    detalle     TEXT,
    nivel       TEXT NOT NULL DEFAULT 'INFO' CHECK (nivel IN ('INFO','WARN','ERROR'))
);

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


def obtener_conexion() -> sqlite3.Connection:
    """
    Abre una conexión a SQLite.
    - row_factory = sqlite3.Row permite acceder por nombre de columna.
    """
    conn = sqlite3.connect(ruta_db())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def inicializar_bd() -> None:
    """
    Crea tablas/vistas si no existen.
    """
    conn = obtener_conexion()
    try:
        conn.executescript(SQL_INIT)
        conn.commit()
    finally:
        conn.close()
