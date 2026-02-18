# ============================================
# modulos/ui_principal.py
# Ventana principal con botones para abrir 4 ventanas
# ============================================

import tkinter as tk
from tkinter import ttk

from .ui_cursos import VentanaCursos
from .ui_alumnos import VentanaAlumnos
from .ui_evaluaciones import VentanaEvaluaciones
from .ui_notas import VentanaNotas


class AppPrincipal(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("SGA - Sistema de Gestión de Alumnos")
        self.geometry("520x320")
        self.resizable(False, False)

        # Título
        lbl = ttk.Label(self, text="SGA - Gestión Académica", font=("Segoe UI", 16, "bold"))
        lbl.pack(pady=18)

        # Botonera
        frm = ttk.Frame(self)
        frm.pack(pady=10)

        ttk.Button(frm, text="1) Cursos (Universidad/Carrera/Curso)", width=40, command=self.abrir_cursos).pack(pady=6)
        ttk.Button(frm, text="2) Alumnos", width=40, command=self.abrir_alumnos).pack(pady=6)
        ttk.Button(frm, text="3) Evaluaciones y Porcentajes", width=40, command=self.abrir_evaluaciones).pack(pady=6)
        ttk.Button(frm, text="4) Notas y Cálculo de Promedios", width=40, command=self.abrir_notas).pack(pady=6)

        # Nota inferior
        ttk.Label(self, text="SQLite local + Exportación Excel/PDF + PyInstaller", foreground="gray").pack(pady=10)

    def abrir_cursos(self):
        VentanaCursos(self)

    def abrir_alumnos(self):
        VentanaAlumnos(self)

    def abrir_evaluaciones(self):
        VentanaEvaluaciones(self)

    def abrir_notas(self):
        VentanaNotas(self)
