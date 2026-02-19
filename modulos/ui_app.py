import tkinter as tk                                   # Importa Tkinter (base de la GUI)                                      # noqa: E501
from tkinter import ttk                                # Importa ttk (widgets con mejor estilo)                                # noqa: E501

from .ui_cursos import PaginaCursos                    # Importa la “página” de Cursos (Frame embebido)                        # noqa: E501
from .ui_alumnos import PaginaAlumnos                  # Importa la “página” de Alumnos (Frame embebido)                       # noqa: E501
from .ui_evaluaciones import PaginaEvaluaciones        # Importa la “página” de Evaluaciones (Frame embebido)                  # noqa: E501
from .ui_notas import PaginaNotas                      # Importa la “página” de Notas (Frame embebido)                         # noqa: E501


class App(tk.Tk):                                      # Clase principal: una sola ventana (NO Toplevel por módulo)            # noqa: E501
    def __init__(self):                                # Constructor de la ventana principal                                   # noqa: E501
        super().__init__()                             # Inicializa internamente tk.Tk                                          # noqa: E501

        self.title("SGA - Sistema de Gestión de Alumnos")  # Título de la ventana                                               # noqa: E501
        self.geometry("1320x760")                      # Tamaño inicial                                                        # noqa: E501
        self.minsize(1180, 680)                        # Tamaño mínimo para evitar que la UI “colapse”                          # noqa: E501

        style = ttk.Style(self)                        # Crea/obtiene el “estilo” de ttk                                        # noqa: E501
        try:                                           # Intenta aplicar un tema moderno                                        # noqa: E501
            style.theme_use("clam")                    # Tema “clam” suele ser limpio y estable                                 # noqa: E501
        except Exception:                              # Si el tema no existe en el sistema                                     # noqa: E501
            pass                                       # No se hace nada (Tkinter usará el tema por defecto)                     # noqa: E501

        self.sidebar_expanded = True                   # Estado del menú lateral (True = expandido / False = colapsado)          # noqa: E501

        self.columnconfigure(1, weight=1)              # Columna 1 (contenido) se estira con la ventana                          # noqa: E501
        self.rowconfigure(0, weight=1)                 # Fila 0 (zona principal) se estira                                      # noqa: E501

        self._crear_sidebar()                          # Construye el menú lateral                                              # noqa: E501
        self._crear_contenido()                        # Construye el área central de páginas                                   # noqa: E501
        self._crear_statusbar()                        # Construye una barra inferior de estado                                 # noqa: E501

        self.show("cursos")                            # Página inicial (puedes cambiarla si quieres)                            # noqa: E501

    # =========================================================
    # Sidebar (menú lateral)
    # =========================================================
    def _crear_sidebar(self):                          # Construye el panel lateral                                             # noqa: E501
        self.sidebar = ttk.Frame(self)                 # Frame lateral                                                          # noqa: E501
        self.sidebar.grid(row=0, column=0, sticky="ns")  # Se pega arriba/abajo (norte/sur)                                      # noqa: E501
        self.sidebar.configure(width=260)              # Ancho inicial expandido                                                # noqa: E501
        self.sidebar.grid_propagate(False)             # Evita que el contenido cambie el ancho del sidebar                      # noqa: E501

        top = ttk.Frame(self.sidebar)                  # Contenedor superior del sidebar                                         # noqa: E501
        top.pack(fill="x", padx=10, pady=(10, 8))      # Se expande horizontalmente                                              # noqa: E501

        self.btn_toggle = ttk.Button(top, text="≡", command=self.toggle_sidebar)  # Botón hamburguesa                 # noqa: E501
        self.btn_toggle.pack(side="left")              # Lo ubica a la izquierda                                                 # noqa: E501

        self.lbl_app = ttk.Label(top, text="SGA", font=("Segoe UI", 12, "bold"))  # Nombre de la app                # noqa: E501
        self.lbl_app.pack(side="left", padx=10)        # Texto al lado del botón                                                # noqa: E501

        ttk.Separator(self.sidebar).pack(fill="x", padx=10, pady=8)  # Línea separadora                          # noqa: E501

        self.btns_frame = ttk.Frame(self.sidebar)      # Frame contenedor de botones                                             # noqa: E501
        self.btns_frame.pack(fill="x", padx=10, pady=6)  # Se ajusta al ancho del sidebar                                        # noqa: E501

        self.btn_cursos = ttk.Button(self.btns_frame, text="📚  Cursos", command=lambda: self.show("cursos"))            # noqa: E501
        self.btn_alumnos = ttk.Button(self.btns_frame, text="👤  Alumnos", command=lambda: self.show("alumnos"))         # noqa: E501
        self.btn_eval = ttk.Button(self.btns_frame, text="🧾  Evaluaciones", command=lambda: self.show("evaluaciones"))  # noqa: E501
        self.btn_notas = ttk.Button(self.btns_frame, text="✅  Notas", command=lambda: self.show("notas"))               # noqa: E501

        for b in (self.btn_cursos, self.btn_alumnos, self.btn_eval, self.btn_notas):  # Recorre los botones             # noqa: E501
            b.pack(fill="x", pady=6)                 # Cada botón ocupa el ancho disponible                                   # noqa: E501

        ttk.Separator(self.sidebar).pack(fill="x", padx=10, pady=10)  # Separador inferior                          # noqa: E501

        self.lbl_info = ttk.Label(self.sidebar, text="Tkinter + SQLite + Excel/PDF", anchor="center")  # Footer info     # noqa: E501
        self.lbl_info.pack(fill="x", padx=10, pady=(0, 10))  # Se centra en el ancho                               # noqa: E501

    def toggle_sidebar(self):                          # Alterna expandir/colapsar el sidebar                                   # noqa: E501
        self.sidebar_expanded = not self.sidebar_expanded  # Invierte el estado                                                   # noqa: E501
        self._aplicar_sidebar_state()                  # Aplica cambios visuales                                                # noqa: E501

    def _aplicar_sidebar_state(self):                  # Cambia ancho y textos de botones según el estado                       # noqa: E501
        if self.sidebar_expanded:                      # Si está expandido                                                      # noqa: E501
            self.sidebar.configure(width=260)          # Ancho grande                                                           # noqa: E501
            self.lbl_app.configure(text="SGA")         # Muestra nombre completo en el encabezado                                # noqa: E501
            self.btn_cursos.configure(text="📚  Cursos")       # Botones con texto                                                   # noqa: E501
            self.btn_alumnos.configure(text="👤  Alumnos")     # Botones con texto                                                   # noqa: E501
            self.btn_eval.configure(text="🧾  Evaluaciones")   # Botones con texto                                                   # noqa: E501
            self.btn_notas.configure(text="✅  Notas")         # Botones con texto                                                   # noqa: E501
            self.lbl_info.configure(text="Tkinter + SQLite + Excel/PDF")  # Footer detallado                         # noqa: E501
        else:                                         # Si está colapsado                                                      # noqa: E501
            self.sidebar.configure(width=70)           # Ancho pequeño                                                          # noqa: E501
            self.lbl_app.configure(text="")            # Oculta texto del encabezado para ahorrar espacio                        # noqa: E501
            self.btn_cursos.configure(text="📚")       # Botones sólo ícono                                                     # noqa: E501
            self.btn_alumnos.configure(text="👤")      # Botones sólo ícono                                                     # noqa: E501
            self.btn_eval.configure(text="🧾")         # Botones sólo ícono                                                     # noqa: E501
            self.btn_notas.configure(text="✅")        # Botones sólo ícono                                                     # noqa: E501
            self.lbl_info.configure(text="SGA")        # Footer corto                                                           # noqa: E501

        self.sidebar.grid_propagate(False)             # Mantiene el ancho fijo aunque cambie el contenido                        # noqa: E501

    # =========================================================
    # Contenido (páginas dentro de la misma ventana)
    # =========================================================
    def _crear_contenido(self):                        # Construye el área central                                               # noqa: E501
        self.contenido = ttk.Frame(self)               # Frame principal de contenido                                            # noqa: E501
        self.contenido.grid(row=0, column=1, sticky="nsew")  # Se estira en todas direcciones                                     # noqa: E501
        self.contenido.rowconfigure(1, weight=1)       # La fila 1 crecerá (zona de páginas)                                     # noqa: E501
        self.contenido.columnconfigure(0, weight=1)    # Columna única crecerá                                                   # noqa: E501

        # Barra superior interna (título de sección / breadcrumb)                                                          # noqa: E501
        self.topbar = ttk.Frame(self.contenido)        # Frame de barra superior                                                 # noqa: E501
        self.topbar.grid(row=0, column=0, sticky="ew") # Ocupa el ancho                                                          # noqa: E501
        self.topbar.columnconfigure(0, weight=1)       # Permite que el título se expanda                                        # noqa: E501

        self.lbl_titulo = ttk.Label(self.topbar, text="Cursos", font=("Segoe UI", 14, "bold"))  # Título sección          # noqa: E501
        self.lbl_titulo.grid(row=0, column=0, sticky="w", padx=14, pady=12)  # Ubicación del título                      # noqa: E501

        ttk.Separator(self.contenido).grid(row=2, column=0, sticky="ew")  # Separador horizontal                          # noqa: E501

        # Contenedor donde viven las páginas (Frames apilados)                                                             # noqa: E501
        self.pages_container = ttk.Frame(self.contenido)  # Frame contenedor de páginas                                           # noqa: E501
        self.pages_container.grid(row=1, column=0, sticky="nsew")  # Zona central                                            # noqa: E501
        self.pages_container.rowconfigure(0, weight=1)    # Se estira verticalmente                                               # noqa: E501
        self.pages_container.columnconfigure(0, weight=1) # Se estira horizontalmente                                             # noqa: E501

        self.pages = {}                                 # Diccionario para guardar las páginas por clave                          # noqa: E501

        self.pages["cursos"] = PaginaCursos(self.pages_container)          # Crea página Cursos                            # noqa: E501
        self.pages["alumnos"] = PaginaAlumnos(self.pages_container)        # Crea página Alumnos                           # noqa: E501
        self.pages["evaluaciones"] = PaginaEvaluaciones(self.pages_container)  # Crea página Evaluaciones                    # noqa: E501
        self.pages["notas"] = PaginaNotas(self.pages_container)            # Crea página Notas                              # noqa: E501

        for p in self.pages.values():                    # Recorre todas las páginas                                               # noqa: E501
            p.grid(row=0, column=0, sticky="nsew")       # Las apila en el mismo lugar; se usa tkraise() para mostrar una           # noqa: E501

    def show(self, key: str):                            # Muestra la página indicada por la clave                                 # noqa: E501
        page = self.pages.get(key)                       # Busca la página en el diccionario                                       # noqa: E501
        if not page:                                     # Si no existe esa clave                                                  # noqa: E501
            return                                       # Sale sin hacer nada                                                      # noqa: E501

        titulo = {                                       # Diccionario de títulos para la barra superior                            # noqa: E501
            "cursos": "Cursos",                          # Texto para cursos                                                        # noqa: E501
            "alumnos": "Alumnos",                        # Texto para alumnos                                                       # noqa: E501
            "evaluaciones": "Evaluaciones",              # Texto para evaluaciones                                                  # noqa: E501
            "notas": "Notas",                            # Texto para notas                                                         # noqa: E501
        }.get(key, "SGA")                                # Si no se encuentra, usa “SGA”                                           # noqa: E501

        self.lbl_titulo.configure(text=titulo)           # Actualiza el título de la sección                                       # noqa: E501
        page.tkraise()                                   # Trae la página al frente (sin abrir nuevas ventanas)                      # noqa: E501

        on_show = getattr(page, "on_show", None)         # Busca si la página tiene método on_show()                                # noqa: E501
        if callable(on_show):                            # Si existe y es una función                                               # noqa: E501
            on_show()                                    # Ejecuta refresco de datos al mostrarse                                   # noqa: E501

        self.set_status(f"Sección activa: {titulo}")     # Muestra mensaje en barra inferior                                        # noqa: E501

    # =========================================================
    # Barra de estado (mensajes)
    # =========================================================
    def _crear_statusbar(self):                          # Construye barra inferior                                                 # noqa: E501
        self.statusbar = ttk.Frame(self)                 # Frame para la barra inferior                                             # noqa: E501
        self.statusbar.grid(row=1, column=0, columnspan=2, sticky="ew")  # Ocupa todo el ancho                             # noqa: E501
        self.statusbar.columnconfigure(0, weight=1)      # Permite que el texto crezca                                              # noqa: E501

        self.var_status = tk.StringVar(value="Listo.")   # Variable ligada al texto de estado                                       # noqa: E501
        self.lbl_status = ttk.Label(self.statusbar, textvariable=self.var_status, anchor="w")  # Label status             # noqa: E501
        self.lbl_status.grid(row=0, column=0, sticky="ew", padx=10, pady=6)  # Ubicación y padding                          # noqa: E501

    def set_status(self, texto: str):                    # Permite a cualquier página mostrar mensajes al usuario                   # noqa: E501
        self.var_status.set(texto)                       # Actualiza el texto de la barra inferior                                  # noqa: E501
