# ============================================  # Separador visual
# modulos/ui_principal.py                        # Ventana principal con NavBar superior
# - Barra superior con botones (Cursos/Alumnos/Evaluaciones/Notas)  # Navegación arriba
# - Área central para mostrar "páginas" (Frames)                   # Contenido dinámico
# - Barra de estado inferior                                        # Mensajes de estado
# ============================================  # Separador visual

import tkinter as tk                                                # Tkinter base
from tkinter import ttk                                              # Widgets ttk

from .ui_cursos import PaginaCursos                                  # Página Cursos
from .ui_alumnos import PaginaAlumnos                                # Página Alumnos
from .ui_evaluaciones import PaginaEvaluaciones                      # Página Evaluaciones
from .ui_notas import PaginaNotas                                    # ✅ Página Notas (ya NO es ventana)
from pathlib import Path
import os
import sys

class AppPrincipal(tk.Tk):                                           # Ventana principal
    def __init__(self):                                              # Constructor
        super().__init__()                                           # Inicializa tk.Tk

        self.title("SGA - Sistema de Gestión de Alumnos")            # Título
        self.geometry("1280x720")                                    # Tamaño inicial
        self.minsize(1100, 650)                                      # Tamaño mínimo

        self._pagina_actual = None                                   # Guarda nombre de página actual
        self._paginas = {}                                           # Diccionario nombre->Frame
        self._btns_nav = {}                                          # Diccionario nombre->Button

        self._configurar_estilos()                                   # Configura estilos ttk
        self._crear_layout()                                         # Crea layout principal
        self._crear_paginas()                                        # Crea páginas
        self.mostrar_pagina("Cursos")                                # Muestra Cursos por defecto
       # ... dentro del __init__ de AppPrincipal:
        try:
            self.iconbitmap(resource_path("assets/app.ico"))
        except Exception:
            pass

    def resource_path(ruta_relativa: str) -> str:
        if hasattr(sys, "_MEIPASS"):
            return os.path.join(sys._MEIPASS, ruta_relativa)
        return os.path.join(os.path.abspath("."), ruta_relativa)



    # =========================================================
    # Estilos
    # =========================================================
    def _configurar_estilos(self):                                   # Configura estilos
        style = ttk.Style(self)                                      # Control de estilos
        try:                                                         # Intento tema moderno
            style.theme_use("clam")                                  # Tema clam
        except Exception:                                            # Si falla
            pass                                                     # No rompe

        style.configure("Nav.TButton", padding=(12, 8))               # Botones nav
        style.configure("NavSel.TButton", padding=(12, 8), relief="sunken")  # Botón activo

    # =========================================================
    # Layout base: NavBar (arriba) + Contenido + Statusbar
    # =========================================================
    def _crear_layout(self):                                         # Crea estructura principal
        self.columnconfigure(0, weight=1)                            # Crece horizontal
        self.rowconfigure(1, weight=1)                               # ✅ Solo contenido central crece vertical

        # ---------------- NAVBAR SUPERIOR ----------------
        self.navbar = ttk.Frame(self)                                # Barra superior
        self.navbar.grid(row=0, column=0, sticky="ew")               # Arriba
        self.navbar.columnconfigure(0, weight=1)                     # Se expande

        nav_inner = ttk.Frame(self.navbar)                           # Contenedor interno
        nav_inner.grid(row=0, column=0, sticky="ew", padx=10, pady=8)  # Padding
        nav_inner.columnconfigure(10, weight=1)                      # Columna elástica

        # Marca
        lbl = ttk.Label(nav_inner, text="SGA", font=("Segoe UI", 12, "bold"))  # Texto marca
        lbl.grid(row=0, column=0, padx=(0, 12), sticky="w")          # Ubicación

        # Botones NavBar
        self._crear_boton_nav(nav_inner, "Cursos", 1)                # Botón Cursos
        self._crear_boton_nav(nav_inner, "Alumnos", 2)               # Botón Alumnos
        self._crear_boton_nav(nav_inner, "Evaluaciones", 3)          # Botón Evaluaciones
        self._crear_boton_nav(nav_inner, "Notas", 4)                 # ✅ Botón Notas (página)

        # Separador + salir
        ttk.Separator(nav_inner, orient="vertical").grid(row=0, column=9, sticky="ns", padx=10)  # Separador
        ttk.Button(nav_inner, text="Salir", command=self.destroy).grid(row=0, column=11, sticky="e")  # Cierra

        # ---------------- CONTENEDOR CENTRAL ----------------
        self.contenido = ttk.Frame(self)                             # Contenedor páginas
        self.contenido.grid(row=1, column=0, sticky="nsew")          # Centro
        self.contenido.columnconfigure(0, weight=1)                  # Crece ancho
        self.contenido.rowconfigure(0, weight=1)                     # Crece alto

        # ---------------- STATUSBAR ----------------
        self.statusbar = ttk.Label(self, text="Listo.", anchor="w")  # Barra estado
        self.statusbar.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 8))  # Abajo

    def _crear_boton_nav(self, parent, nombre: str, col: int):       # Crea botón en el NavBar
        btn = ttk.Button(                                            # Botón
            parent,                                                  # Padre
            text=nombre,                                             # Texto
            style="Nav.TButton",                                     # Estilo
            command=lambda n=nombre: self.mostrar_pagina(n),          # Acción
        )
        btn.grid(row=0, column=col, padx=4, sticky="w")               # Ubicación
        self._btns_nav[nombre] = btn                                 # Guarda referencia

    # =========================================================
    # Crear páginas (Frames)
    # =========================================================
    def _crear_paginas(self):                                        # Instancia páginas
        self._paginas["Cursos"] = PaginaCursos(self.contenido)       # Página Cursos
        self._paginas["Alumnos"] = PaginaAlumnos(self.contenido)     # Página Alumnos
        self._paginas["Evaluaciones"] = PaginaEvaluaciones(self.contenido)  # Página Evaluaciones
        self._paginas["Notas"] = PaginaNotas(self.contenido)         # ✅ Página Notas embebida

        # Posiciona todas en el mismo grid (se muestran/ocultan)
        for nombre, frame in self._paginas.items():                  # Recorre páginas
            frame.grid(row=0, column=0, sticky="nsew")               # Mismo lugar
            frame.grid_remove()                                      # Ocultas al inicio

    # =========================================================
    # Navegación: mostrar una página
    # =========================================================
    def mostrar_pagina(self, nombre: str):                           # Muestra página seleccionada
        # Oculta anterior
        if self._pagina_actual:                                      # Si había una anterior
            self._paginas[self._pagina_actual].grid_remove()         # Oculta

        # Muestra nueva
        frame = self._paginas.get(nombre)                            # Obtiene frame
        if frame is None:                                            # Si no existe
            self.set_status(f"Vista no disponible: {nombre}")        # Mensaje
            return                                                   # Sale

        frame.grid()                                                 # Muestra
        self._pagina_actual = nombre                                 # Guarda actual

        # Si la página tiene on_show(), se refresca
        if hasattr(frame, "on_show") and callable(getattr(frame, "on_show")):  # Si existe
            frame.on_show()                                          # Refresca

        self._marcar_nav(nombre)                                     # Marca botón activo
        self.set_status(f"Vista: {nombre}")                          # Estado

    def _marcar_nav(self, nombre: str):                              # Marca botón seleccionado
        for n, btn in self._btns_nav.items():                        # Recorre botones
            if n == nombre:                                          # Si activo
                btn.configure(style="NavSel.TButton")                # Estilo seleccionado
            else:                                                    # Si no
                btn.configure(style="Nav.TButton")                   # Estilo normal

    # =========================================================
    # Statusbar público
    # =========================================================
    def set_status(self, texto: str):                                # Permite enviar mensajes
        self.statusbar.config(text=texto)                            # Actualiza texto
