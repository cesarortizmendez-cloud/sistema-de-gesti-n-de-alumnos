# ============================================
# modulos/ui_cursos.py
# Ventana 1: gestión de universidades, carreras y cursos
# ============================================

import tkinter as tk
from tkinter import ttk, messagebox

from .repo_universidades import listar_universidades, crear_universidad, actualizar_universidad, eliminar_universidad
from .repo_carreras import listar_carreras_por_universidad, crear_carrera, actualizar_carrera, eliminar_carrera
from .repo_cursos import listar_cursos_por_carrera, crear_curso, actualizar_curso, eliminar_curso


class VentanaCursos(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)

        self.title("Cursos - Universidades / Carreras / Cursos")
        self.geometry("1100x600")
        self.minsize(1050, 560)

        self.uni_sel = None
        self.car_sel = None
        self.curso_sel = None

        self._crear_ui()
        self._cargar_universidades()

    def _crear_ui(self):
        cont = ttk.Frame(self)
        cont.pack(fill="both", expand=True, padx=10, pady=10)

        cont.columnconfigure(0, weight=1)
        cont.columnconfigure(1, weight=1)
        cont.columnconfigure(2, weight=2)
        cont.rowconfigure(1, weight=1)

        # =======================
        # UNIVERSIDADES
        # =======================
        uni_box = ttk.LabelFrame(cont, text="Universidades")
        uni_box.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 8))

        self.var_uni_nombre = tk.StringVar()

        frm_uni = ttk.Frame(uni_box)
        frm_uni.pack(fill="x", padx=8, pady=8)

        ttk.Label(frm_uni, text="Nombre:").pack(side="left")
        ttk.Entry(frm_uni, textvariable=self.var_uni_nombre, width=24).pack(side="left", padx=6)

        ttk.Button(frm_uni, text="Agregar", command=self.on_uni_agregar).pack(side="left", padx=3)
        ttk.Button(frm_uni, text="Actualizar", command=self.on_uni_actualizar).pack(side="left", padx=3)
        ttk.Button(frm_uni, text="Eliminar", command=self.on_uni_eliminar).pack(side="left", padx=3)

        self.tree_uni = ttk.Treeview(uni_box, columns=("id", "nombre"), show="headings", height=18)
        self.tree_uni.heading("id", text="ID")
        self.tree_uni.heading("nombre", text="Universidad")
        self.tree_uni.column("id", width=60, anchor="center")
        self.tree_uni.column("nombre", width=260, anchor="w")
        self.tree_uni.pack(fill="both", expand=True, padx=8, pady=8)
        self.tree_uni.bind("<<TreeviewSelect>>", lambda e: self.on_uni_select())

        # =======================
        # CARRERAS
        # =======================
        car_box = ttk.LabelFrame(cont, text="Carreras (de la universidad seleccionada)")
        car_box.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=(0, 8))

        self.var_car_nombre = tk.StringVar()

        frm_car = ttk.Frame(car_box)
        frm_car.pack(fill="x", padx=8, pady=8)

        ttk.Label(frm_car, text="Nombre:").pack(side="left")
        ttk.Entry(frm_car, textvariable=self.var_car_nombre, width=24).pack(side="left", padx=6)

        ttk.Button(frm_car, text="Agregar", command=self.on_car_agregar).pack(side="left", padx=3)
        ttk.Button(frm_car, text="Actualizar", command=self.on_car_actualizar).pack(side="left", padx=3)
        ttk.Button(frm_car, text="Eliminar", command=self.on_car_eliminar).pack(side="left", padx=3)

        self.tree_car = ttk.Treeview(car_box, columns=("id", "nombre"), show="headings", height=18)
        self.tree_car.heading("id", text="ID")
        self.tree_car.heading("nombre", text="Carrera")
        self.tree_car.column("id", width=60, anchor="center")
        self.tree_car.column("nombre", width=260, anchor="w")
        self.tree_car.pack(fill="both", expand=True, padx=8, pady=8)
        self.tree_car.bind("<<TreeviewSelect>>", lambda e: self.on_car_select())

        # =======================
        # CURSOS
        # =======================
        curso_box = ttk.LabelFrame(cont, text="Cursos (de la carrera seleccionada)")
        curso_box.grid(row=0, column=2, rowspan=2, sticky="nsew")

        self.var_curso_sem = tk.StringVar()
        self.var_curso_nombre = tk.StringVar()
        self.var_curso_codigo = tk.StringVar()

        frm_c = ttk.Frame(curso_box)
        frm_c.pack(fill="x", padx=8, pady=8)

        ttk.Label(frm_c, text="Semestre:").grid(row=0, column=0, sticky="w")
        ttk.Entry(frm_c, textvariable=self.var_curso_sem, width=8).grid(row=0, column=1, sticky="w", padx=6)

        ttk.Label(frm_c, text="Nombre curso:").grid(row=0, column=2, sticky="w")
        ttk.Entry(frm_c, textvariable=self.var_curso_nombre, width=28).grid(row=0, column=3, sticky="w", padx=6)

        ttk.Label(frm_c, text="Código:").grid(row=0, column=4, sticky="w")
        ttk.Entry(frm_c, textvariable=self.var_curso_codigo, width=12).grid(row=0, column=5, sticky="w", padx=6)

        ttk.Button(frm_c, text="Agregar", command=self.on_curso_agregar).grid(row=1, column=1, pady=6)
        ttk.Button(frm_c, text="Actualizar", command=self.on_curso_actualizar).grid(row=1, column=2, pady=6)
        ttk.Button(frm_c, text="Eliminar", command=self.on_curso_eliminar).grid(row=1, column=3, pady=6)

        self.tree_curso = ttk.Treeview(
            curso_box,
            columns=("id", "sem", "nombre", "codigo"),
            show="headings",
            height=18,
        )
        self.tree_curso.heading("id", text="ID")
        self.tree_curso.heading("sem", text="Sem")
        self.tree_curso.heading("nombre", text="Curso")
        self.tree_curso.heading("codigo", text="Código")

        self.tree_curso.column("id", width=60, anchor="center")
        self.tree_curso.column("sem", width=60, anchor="center")
        self.tree_curso.column("nombre", width=360, anchor="w")
        self.tree_curso.column("codigo", width=100, anchor="w")

        self.tree_curso.pack(fill="both", expand=True, padx=8, pady=8)
        self.tree_curso.bind("<<TreeviewSelect>>", lambda e: self.on_curso_select())

    # -----------------------------
    # CARGAS
    # -----------------------------
    def _cargar_universidades(self):
        for i in self.tree_uni.get_children():
            self.tree_uni.delete(i)
        for u in listar_universidades():
            self.tree_uni.insert("", "end", values=(u["universidad_id"], u["nombre"]))

        # Limpieza dependientes
        self.uni_sel = None
        self.car_sel = None
        self.curso_sel = None
        self._limpiar_carreras()
        self._limpiar_cursos()

    def _cargar_carreras(self, universidad_id: int):
        for i in self.tree_car.get_children():
            self.tree_car.delete(i)
        for c in listar_carreras_por_universidad(universidad_id):
            self.tree_car.insert("", "end", values=(c["carrera_id"], c["nombre"]))

        self.car_sel = None
        self._limpiar_cursos()

    def _cargar_cursos(self, carrera_id: int):
        for i in self.tree_curso.get_children():
            self.tree_curso.delete(i)
        for cu in listar_cursos_por_carrera(carrera_id):
            self.tree_curso.insert("", "end", values=(cu["curso_id"], cu["semestre"], cu["nombre"], cu.get("codigo") or ""))

        self.curso_sel = None

    def _limpiar_carreras(self):
        for i in self.tree_car.get_children():
            self.tree_car.delete(i)

    def _limpiar_cursos(self):
        for i in self.tree_curso.get_children():
            self.tree_curso.delete(i)

    # -----------------------------
    # SELECTS
    # -----------------------------
    def on_uni_select(self):
        sel = self.tree_uni.selection()
        if not sel:
            return
        vals = self.tree_uni.item(sel[0], "values")
        self.uni_sel = int(vals[0])
        self.var_uni_nombre.set(vals[1])

        self._cargar_carreras(self.uni_sel)

    def on_car_select(self):
        sel = self.tree_car.selection()
        if not sel:
            return
        vals = self.tree_car.item(sel[0], "values")
        self.car_sel = int(vals[0])
        self.var_car_nombre.set(vals[1])

        self._cargar_cursos(self.car_sel)

    def on_curso_select(self):
        sel = self.tree_curso.selection()
        if not sel:
            return
        vals = self.tree_curso.item(sel[0], "values")
        self.curso_sel = int(vals[0])
        self.var_curso_sem.set(vals[1])
        self.var_curso_nombre.set(vals[2])
        self.var_curso_codigo.set(vals[3])

    # -----------------------------
    # CRUD UNIVERSIDAD
    # -----------------------------
    def on_uni_agregar(self):
        try:
            crear_universidad(self.var_uni_nombre.get())
            self.var_uni_nombre.set("")
            self._cargar_universidades()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_uni_actualizar(self):
        if self.uni_sel is None:
            messagebox.showwarning("Atención", "Seleccione una universidad.")
            return
        try:
            actualizar_universidad(self.uni_sel, self.var_uni_nombre.get())
            self._cargar_universidades()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_uni_eliminar(self):
        if self.uni_sel is None:
            messagebox.showwarning("Atención", "Seleccione una universidad.")
            return
        if not messagebox.askyesno("Confirmar", "¿Eliminar universidad? (Si tiene carreras asociadas, fallará)"):
            return
        try:
            eliminar_universidad(self.uni_sel)
            self.var_uni_nombre.set("")
            self._cargar_universidades()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # -----------------------------
    # CRUD CARRERA
    # -----------------------------
    def on_car_agregar(self):
        if self.uni_sel is None:
            messagebox.showwarning("Atención", "Seleccione una universidad primero.")
            return
        try:
            crear_carrera(self.uni_sel, self.var_car_nombre.get())
            self.var_car_nombre.set("")
            self._cargar_carreras(self.uni_sel)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_car_actualizar(self):
        if self.car_sel is None:
            messagebox.showwarning("Atención", "Seleccione una carrera.")
            return
        try:
            actualizar_carrera(self.car_sel, self.var_car_nombre.get())
            self._cargar_carreras(self.uni_sel)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_car_eliminar(self):
        if self.car_sel is None:
            messagebox.showwarning("Atención", "Seleccione una carrera.")
            return
        if not messagebox.askyesno("Confirmar", "¿Eliminar carrera? (Si tiene cursos/alumnos, fallará)"):
            return
        try:
            eliminar_carrera(self.car_sel)
            self.var_car_nombre.set("")
            self._cargar_carreras(self.uni_sel)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # -----------------------------
    # CRUD CURSO
    # -----------------------------
    def on_curso_agregar(self):
        if self.car_sel is None:
            messagebox.showwarning("Atención", "Seleccione una carrera primero.")
            return
        try:
            crear_curso(self.car_sel, self.var_curso_sem.get(), self.var_curso_nombre.get(), self.var_curso_codigo.get())
            self.var_curso_sem.set("")
            self.var_curso_nombre.set("")
            self.var_curso_codigo.set("")
            self._cargar_cursos(self.car_sel)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_curso_actualizar(self):
        if self.curso_sel is None:
            messagebox.showwarning("Atención", "Seleccione un curso.")
            return
        try:
            actualizar_curso(self.curso_sel, self.car_sel, self.var_curso_sem.get(), self.var_curso_nombre.get(), self.var_curso_codigo.get())
            self._cargar_cursos(self.car_sel)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_curso_eliminar(self):
        if self.curso_sel is None:
            messagebox.showwarning("Atención", "Seleccione un curso.")
            return
        if not messagebox.askyesno("Confirmar", "¿Eliminar curso? (Si tiene inscripciones/evaluaciones fallará)"):
            return
        try:
            eliminar_curso(self.curso_sel)
            self.var_curso_sem.set("")
            self.var_curso_nombre.set("")
            self.var_curso_codigo.set("")
            self._cargar_cursos(self.car_sel)
        except Exception as e:
            messagebox.showerror("Error", str(e))
