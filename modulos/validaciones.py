import re

def normalizar_texto(valor) -> str:
    if valor is None:
        return ""
    return str(valor).strip()

def rut_a_normalizado(rut: str) -> str:
    r = normalizar_texto(rut).upper()
    r = r.replace(".", "").replace("-", "")
    r = re.sub(r"[^0-9K]", "", r)
    return r

def nombre_busqueda(nombres: str, apellidos: str) -> str:
    base = f"{normalizar_texto(nombres)} {normalizar_texto(apellidos)}".strip()
    return base.casefold()

def validar_periodo(valor) -> str:
    """
    Valida formato AAAA-1 o AAAA-2.
    Ej: 2026-1 = primer semestre 2026
    """
    txt = normalizar_texto(valor)
    if not re.fullmatch(r"\d{4}-[12]", txt):
        raise ValueError("Periodo debe tener formato AAAA-1 o AAAA-2 (ej: 2026-1).")
    return txt

def validar_porcentaje(valor) -> float:
    try:
        p = float(valor)
    except Exception:
        raise ValueError("Porcentaje debe ser numérico.")
    if p <= 0 or p > 100:
        raise ValueError("Porcentaje debe ser > 0 y <= 100.")
    return p

def validar_nota(valor) -> float:
    try:
        n = float(valor)
    except Exception:
        raise ValueError("Nota debe ser numérica.")
    if n < 0 or n > 7:
        raise ValueError("Nota debe estar entre 0 y 7.")
    return n
