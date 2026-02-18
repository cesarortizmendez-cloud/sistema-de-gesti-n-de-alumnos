# ============================================
# modulos/validaciones.py
# Validaciones y normalizaciones (RUT, rangos, textos)
# ============================================

import re


def normalizar_texto(valor) -> str:
    """
    Convierte cualquier valor a string limpio.
    - None => ""
    - Quita espacios al inicio y final
    """
    if valor is None:
        return ""
    return str(valor).strip()


def rut_a_normalizado(rut: str) -> str:
    """
    Normaliza un RUT chileno para guardarlo y compararlo:
    - "12.345.678-k" => "12345678K"
    """
    r = normalizar_texto(rut).upper()
    r = r.replace(".", "").replace("-", "")
    r = re.sub(r"[^0-9K]", "", r)
    return r


def nombre_busqueda(nombres: str, apellidos: str) -> str:
    """
    Texto para búsquedas rápidas (en minúsculas):
    "Juan Pérez" => "juan pérez"
    """
    base = f"{normalizar_texto(nombres)} {normalizar_texto(apellidos)}".strip()
    return base.casefold()


def validar_semestre(valor) -> int:
    """
    Valida semestre entre 1 y 20.
    """
    try:
        s = int(valor)
    except Exception:
        raise ValueError("Semestre debe ser un número entero.")
    if s < 1 or s > 20:
        raise ValueError("Semestre debe estar entre 1 y 20.")
    return s


def validar_porcentaje(valor) -> float:
    """
    Valida porcentaje entre 0 y 100 (excluye 0).
    """
    try:
        p = float(valor)
    except Exception:
        raise ValueError("Porcentaje debe ser numérico.")
    if p <= 0 or p > 100:
        raise ValueError("Porcentaje debe ser > 0 y <= 100.")
    return p


def validar_nota(valor) -> float:
    """
    Valida nota entre 0 y 7 (0 se usa como 'sin nota aún').
    """
    try:
        n = float(valor)
    except Exception:
        raise ValueError("Nota debe ser numérica.")
    if n < 0 or n > 7:
        raise ValueError("Nota debe estar entre 0 y 7.")
    return n
