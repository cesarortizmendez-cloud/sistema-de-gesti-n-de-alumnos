# ============================================  # Separador visual
# modulos/bd_sqlite.py                           # Archivo de base de datos SQLite
# - Crea tablas si no existen                     # Inicialización base
# - Migra versiones antiguas (semestre -> periodo)# Migración suave
# - Crea índices, triggers y vistas               # Optimización y utilidades
# ============================================  # Separador visual

import sqlite3                                   # Librería estándar para SQLite                                   # noqa: E501
from datetime import datetime                     # Para usar año actual en migraciones                              # noqa: E501

from .config import ruta_db                       # Ruta segura del archivo .db (AppData)                            # noqa: E501


def obtener_conexion() -> sqlite3.Connection:     # Abre conexión configurada a la BD                                # noqa: E501
    conn = sqlite3.connect(ruta_db())             # Abre (o crea) el archivo sga.db                                  # noqa: E501
    conn.row_factory = sqlite3.Row                # Permite acceder por nombre: fila["columna"]                      # noqa: E501
    conn.execute("PRAGMA foreign_keys = ON;")     # Activa claves foráneas en SQLite                                  # noqa: E501
    return conn                                   # Retorna la conexión lista                                         # noqa: E501


def _tabla_existe(conn: sqlite3.Connection, nombre_tabla: str) -> bool:  # Verifica si existe una tabla                           # noqa: E501
    cur = conn.cursor()                        # Cursor para ejecutar SQL                                           # noqa: E501
    cur.execute(                               # Consulta en sqlite_master                                          # noqa: E501
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",  # SQL                                              # noqa: E501
        (nombre_tabla,),                       # Parámetro seguro                                                   # noqa: E501
    )
    return cur.fetchone() is not None          # True si encontró tabla, False si no                                # noqa: E501


def _columna_existe(conn: sqlite3.Connection, nombre_tabla: str, nombre_columna: str) -> bool:  # Verifica columna         # noqa: E501
    cur = conn.cursor()                        # Cursor                                                             # noqa: E501
    cur.execute(f"PRAGMA table_info({nombre_tabla})")  # Lista columnas de la tabla                                # noqa: E501
    cols = [r["name"] for r in cur.fetchall()] # Extrae nombres de columnas                                          # noqa: E501
    return nombre_columna in cols              # True si existe, False si no                                         # noqa: E501


def _crear_tablas_si_no_existen(conn: sqlite3.Connection) -> None:  # Crea tablas base si no existen                              # noqa: E501
    cur = conn.cursor()                      # Cursor para crear tablas                                             # noqa: E501

    # ---------- UNIVERSIDADES ----------      # Tabla universidades                                                 # noqa: E501
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS universidades (
            universidad_id  INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre          TEXT NOT NULL UNIQUE
        );
        """
    )

    # ---------- CARRERAS ----------           # Tabla carreras (depende de universidad)                             # noqa: E501
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS carreras (
            carrera_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            universidad_id  INTEGER NOT NULL,
            nombre          TEXT NOT NULL,
            UNIQUE(universidad_id, nombre),
            FOREIGN KEY (universidad_id) REFERENCES universidades(universidad_id) ON DELETE CASCADE
        );
        """
    )

    # ---------- CURSOS ----------             # Tabla cursos (depende de carrera) + periodo AAAA-1 o AAAA-2          # noqa: E501
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
        );
        """
    )

    # ---------- ALUMNOS ----------            # Tabla alumnos (rut UNIQUE para import Excel)                         # noqa: E501
    # Nota: dejamos campos extra opcionales (NULL) para no romper UI si aún no los captura.                           # noqa: E501
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS alumnos (
            alumno_id        INTEGER PRIMARY KEY AUTOINCREMENT,
            rut              TEXT NOT NULL,
            nombres          TEXT NOT NULL,
            apellidos        TEXT NOT NULL,
            email            TEXT,
            telefono         TEXT,

            -- Opcionales (para extender sin romper UI)
            tipo_alumno      TEXT DEFAULT 'Pregrado' CHECK (tipo_alumno IN ('Pregrado','Postgrado','Intercambio')),
            universidad_id   INTEGER,
            carrera_id       INTEGER,
            periodo          TEXT CHECK (periodo IS NULL OR periodo GLOB '[0-9][0-9][0-9][0-9]-[12]'),
            estado           INTEGER NOT NULL DEFAULT 1 CHECK (estado IN (0,1)),

            -- Campos de apoyo (búsqueda/fechas)
            nombre_busqueda  TEXT,
            fecha_registro   TEXT NOT NULL DEFAULT (datetime('now')),
            fecha_actualiza  TEXT NOT NULL DEFAULT (datetime('now')),

            FOREIGN KEY (universidad_id) REFERENCES universidades(universidad_id) ON DELETE RESTRICT,
            FOREIGN KEY (carrera_id)      REFERENCES carreras(carrera_id)       ON DELETE RESTRICT
        );
        """
    )

    # Importante: el UNIQUE del rut se crea con índice para migraciones suaves (si tabla ya existía).                  # noqa: E501

    # ---------- INSCRIPCIONES ----------       # Relación alumno <-> curso (muchos a muchos)                          # noqa: E501
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS inscripciones (
            inscripcion_id INTEGER PRIMARY KEY AUTOINCREMENT,
            alumno_id      INTEGER NOT NULL,
            curso_id       INTEGER NOT NULL,
            UNIQUE(alumno_id, curso_id),
            FOREIGN KEY (alumno_id) REFERENCES alumnos(alumno_id) ON DELETE CASCADE,
            FOREIGN KEY (curso_id)  REFERENCES cursos(curso_id)   ON DELETE CASCADE
        );
        """
    )

    # ---------- EVALUACIONES ----------        # Evaluaciones de un curso                                             # noqa: E501
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS evaluaciones (
            evaluacion_id INTEGER PRIMARY KEY AUTOINCREMENT,
            curso_id      INTEGER NOT NULL,
            nombre        TEXT NOT NULL,
            porcentaje    REAL NOT NULL CHECK (porcentaje > 0 AND porcentaje <= 100),
            UNIQUE(curso_id, nombre),
            FOREIGN KEY (curso_id) REFERENCES cursos(curso_id) ON DELETE CASCADE
        );
        """
    )

    # ---------- NOTAS ----------               # Nota por (inscripción, evaluación)                                   # noqa: E501
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS notas (
            nota_id        INTEGER PRIMARY KEY AUTOINCREMENT,
            inscripcion_id INTEGER NOT NULL,
            evaluacion_id  INTEGER NOT NULL,
            nota           REAL NOT NULL CHECK (nota >= 0 AND nota <= 7),
            UNIQUE(inscripcion_id, evaluacion_id),
            FOREIGN KEY (inscripcion_id) REFERENCES inscripciones(inscripcion_id) ON DELETE CASCADE,
            FOREIGN KEY (evaluacion_id)  REFERENCES evaluaciones(evaluacion_id)   ON DELETE CASCADE
        );
        """
    )

    # ---------- LOGS (opcional) ----------     # Registro de eventos de la app                                        # noqa: E501
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS logs_eventos (
            log_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_hora  TEXT NOT NULL DEFAULT (datetime('now')),
            modulo      TEXT NOT NULL,
            accion      TEXT NOT NULL,
            detalle     TEXT,
            nivel       TEXT NOT NULL DEFAULT 'INFO' CHECK (nivel IN ('INFO','WARN','ERROR'))
        );
        """
    )


def _migraciones(conn: sqlite3.Connection) -> None:  # Migraciones suaves para BD antiguas                             # noqa: E501
    cur = conn.cursor()                               # Cursor                                                          # noqa: E501
    periodo_default = f"{datetime.now().year}-1"       # Periodo por defecto (ej: 2026-1)                               # noqa: E501

    # --------- MIGRACIÓN: cursos.semestre -> cursos.periodo ---------
    if _tabla_existe(conn, "cursos"):                  # Si existe tabla cursos                                         # noqa: E501
        if not _columna_existe(conn, "cursos", "periodo"):  # Si NO existe columna periodo                            # noqa: E501
            cur.execute("ALTER TABLE cursos ADD COLUMN periodo TEXT")  # Agrega columna periodo                           # noqa: E501
            cur.execute(                               # Rellena periodo vacío con default                              # noqa: E501
                "UPDATE cursos SET periodo=? WHERE periodo IS NULL OR TRIM(periodo)=''",
                (periodo_default,),
            )

        # Si la BD antigua usaba 'semestre', intentamos copiarlo a periodo si sirve (solo si es 1 o 2)                  # noqa: E501
        if _columna_existe(conn, "cursos", "semestre"):  # Si existe columna semestre                                 # noqa: E501
            # No conocemos el año anterior real, pero si semestre era 1 o 2, al menos dejamos coherente el sufijo.      # noqa: E501
            cur.execute(                               # Ajusta solo el sufijo del periodo cuando semestre es válido   # noqa: E501
                """
                UPDATE cursos
                   SET periodo = substr(?,1,4) || '-' || CAST(semestre AS TEXT)
                 WHERE (periodo IS NULL OR TRIM(periodo)='' OR periodo NOT GLOB '[0-9][0-9][0-9][0-9]-[12]')
                   AND (semestre IN (1,2));
                """,
                (periodo_default,),
            )

    # --------- MIGRACIÓN: alumnos.periodo (si falta) ---------
    if _tabla_existe(conn, "alumnos"):                 # Si existe tabla alumnos                                        # noqa: E501
        if not _columna_existe(conn, "alumnos", "periodo"):  # Si falta periodo                                        # noqa: E501
            cur.execute("ALTER TABLE alumnos ADD COLUMN periodo TEXT")  # Agrega periodo                                 # noqa: E501
            cur.execute(                               # Rellena con default                                            # noqa: E501
                "UPDATE alumnos SET periodo=? WHERE periodo IS NULL OR TRIM(periodo)=''",
                (periodo_default,),
            )

        # Si existe rut_normalizado en BD anterior, no lo necesitamos, pero lo dejamos sin romper nada.                 # noqa: E501

    # --------- Asegurar índice UNIQUE en alumnos.rut (para ON CONFLICT(rut)) ---------
    # Esto es clave para el import Excel de ui_alumnos.py, que usa UPSERT por rut.                                       # noqa: E501
    try:                                              # Intento crear índice UNIQUE                                    # noqa: E501
        cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS ux_alumnos_rut ON alumnos(rut)")  # UNIQUE rut              # noqa: E501
    except sqlite3.IntegrityError:                     # Si hay rut duplicados antiguos                                # noqa: E501
        # No detenemos la app (pero en esa BD vieja el UPSERT por rut no funcionará correctamente).                      # noqa: E501
        pass                                           # Continúa sin cortar ejecución                                 # noqa: E501


def _crear_indices_triggers_vistas(conn: sqlite3.Connection) -> None:  # Índices, triggers y vista                                   # noqa: E501
    cur = conn.cursor()                           # Cursor                                                           # noqa: E501

    # ---------------- ÍNDICES (mejoran velocidad) ----------------
    cur.execute("CREATE INDEX IF NOT EXISTS idx_carreras_universidad ON carreras(universidad_id)")  # idx carrera->uni      # noqa: E501
    cur.execute("CREATE INDEX IF NOT EXISTS idx_cursos_carrera ON cursos(carrera_id)")              # idx cursos por carrera # noqa: E501
    cur.execute("CREATE INDEX IF NOT EXISTS idx_cursos_periodo ON cursos(periodo)")                 # idx cursos por periodo # noqa: E501

    cur.execute("CREATE INDEX IF NOT EXISTS idx_alumnos_rut ON alumnos(rut)")                        # idx alumnos por rut    # noqa: E501
    cur.execute("CREATE INDEX IF NOT EXISTS idx_alumnos_nombre ON alumnos(nombre_busqueda)")         # idx para búsqueda       # noqa: E501
    cur.execute("CREATE INDEX IF NOT EXISTS idx_insc_curso ON inscripciones(curso_id)")              # idx insc por curso      # noqa: E501
    cur.execute("CREATE INDEX IF NOT EXISTS idx_insc_alumno ON inscripciones(alumno_id)")            # idx insc por alumno     # noqa: E501
    cur.execute("CREATE INDEX IF NOT EXISTS idx_eval_curso ON evaluaciones(curso_id)")               # idx eval por curso      # noqa: E501
    cur.execute("CREATE INDEX IF NOT EXISTS idx_notas_insc ON notas(inscripcion_id)")                # idx notas por insc      # noqa: E501
    cur.execute("CREATE INDEX IF NOT EXISTS idx_notas_eval ON notas(evaluacion_id)")                 # idx notas por eval      # noqa: E501

    # ---------------- TRIGGERS: fecha_actualiza + nombre_busqueda ----------------
    # AFTER INSERT: genera nombre_busqueda y asegura consistencia
    cur.execute(
        """
        CREATE TRIGGER IF NOT EXISTS trg_alumnos_ai_busqueda
        AFTER INSERT ON alumnos
        FOR EACH ROW
        BEGIN
            UPDATE alumnos
               SET nombre_busqueda = lower(trim(COALESCE(NEW.apellidos,'') || ' ' || COALESCE(NEW.nombres,'') || ' ' || COALESCE(NEW.rut,''))),
                   fecha_actualiza = datetime('now')
             WHERE alumno_id = NEW.alumno_id;
        END;
        """
    )

    # AFTER UPDATE: actualiza fecha_actualiza y recalcula nombre_busqueda
    cur.execute(
        """
        CREATE TRIGGER IF NOT EXISTS trg_alumnos_au_busqueda
        AFTER UPDATE ON alumnos
        FOR EACH ROW
        BEGIN
            UPDATE alumnos
               SET nombre_busqueda = lower(trim(COALESCE(NEW.apellidos,'') || ' ' || COALESCE(NEW.nombres,'') || ' ' || COALESCE(NEW.rut,''))),
                   fecha_actualiza = datetime('now')
             WHERE alumno_id = NEW.alumno_id;
        END;
        """
    )

    # ---------------- VISTA: promedios ponderados por inscripción ----------------
    # Nota: calcula siempre contra evaluaciones del curso; si no hay nota usa 0.
    cur.execute(
        """
        CREATE VIEW IF NOT EXISTS vw_promedios_ponderados AS
        SELECT
            i.inscripcion_id,
            i.alumno_id,
            i.curso_id,
            CASE
                WHEN COALESCE(SUM(e.porcentaje),0) = 0 THEN 0
                ELSE SUM(COALESCE(n.nota,0) * e.porcentaje) / SUM(e.porcentaje)
            END AS promedio_ponderado,
            SUM(e.porcentaje) AS suma_porcentajes
        FROM inscripciones i
        JOIN evaluaciones e
          ON e.curso_id = i.curso_id
        LEFT JOIN notas n
          ON n.inscripcion_id = i.inscripcion_id
         AND n.evaluacion_id  = e.evaluacion_id
        GROUP BY i.inscripcion_id, i.alumno_id, i.curso_id;
        """
    )


def inicializar_bd() -> None:                      # Inicializa la base de datos completa                             # noqa: E501
    conn = obtener_conexion()                      # Abre conexión                                                     # noqa: E501
    try:                                           # Bloque protegido                                                  # noqa: E501
        _crear_tablas_si_no_existen(conn)          # 1) Crea tablas si no existen                                      # noqa: E501
        _migraciones(conn)                         # 2) Aplica migraciones suaves                                      # noqa: E501
        _crear_indices_triggers_vistas(conn)       # 3) Crea índices, triggers y vista                                  # noqa: E501
        conn.commit()                              # Confirma cambios                                                   # noqa: E501
    finally:                                       # Siempre                                                            # noqa: E501
        conn.close()                               # Cierra conexión                                                    # noqa: E501
