# ============================================
# modulos/modelos.py
# Modelos (POO) simples usando dataclasses
# ============================================

from dataclasses import dataclass
from typing import Optional


@dataclass
class Universidad:
    universidad_id: Optional[int]
    nombre: str


@dataclass
class Carrera:
    carrera_id: Optional[int]
    universidad_id: int
    nombre: str


@dataclass
class Curso:
    curso_id: Optional[int]
    carrera_id: int
    semestre: int
    nombre: str
    codigo: Optional[str] = None


@dataclass
class Alumno:
    alumno_id: Optional[int]
    tipo_alumno: str
    rut: str
    rut_normalizado: str
    nombres: str
    apellidos: str
    email: Optional[str]
    telefono: Optional[str]
    universidad_id: int
    carrera_id: int
    semestre: int
    estado: int
