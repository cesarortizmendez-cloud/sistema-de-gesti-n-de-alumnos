# ============================================
# modulos/ui_alumnos.py
# Ventana 2: CRUD alumnos + búsqueda + combos universidad/carrera
# ============================================

import tkinter as tk
from tkinter import ttk, messagebox

from .repo_universidades import listar_universidades
from .repo_carreras import listar_carreras_por_universidad
from .repo_alumnos import listar_alumnos, buscar_alumnos, crear_alumno, actualizar_alumno, eliminar_alumno, obtener_alumno


class VentanaAlumnos(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)

        self.title("Alumnos - Gestión")
        self.geometry("1200x650")
        self.minsize(1100, 600)

        self.alumno_sel = None

        self._crear_ui()
        self._cargar_universidades()
        self._cargar_tabla(listar_alumnos())

    def _crear_ui(self):
        # Barra buscar
        barra = ttk.Frame(self)
        barra.pack(fill="x", padx=10, pady=8)

        ttk.Label(barra, text="Buscar (nombre / RUT / email):").pack(side="left")
        self.var_buscar = tk.StringVar()
        ent = ttk.Entry(barra, textvariable=self.var_buscar, width=40)
        ent.pack(side="left", padx=8)
        ent.bind("<Return>", lambda e: self.on_buscar())

        ttk.Button(barra, text="Buscar", command=self.on_buscar).pack(side="left", padx=4)
        ttk.Button(barra, text="Ver todo", command=self.on_ver_todo).pack(side="left", padx=4)

        # Contenedor
        cont = ttk.Frame(self)
        cont.pack(fill="both", expand=True, padx=10, pady=8)

        cont.columnconfigure(0, weight=1)
        cont.columnconfigure(1, weight=2)
        cont.rowconfigure(0, weight=1)

        # Formulario
        frm = ttk.LabelFrame(cont, text="Formulario Alumno")
        frm.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        frm.columnconfigure(1, weight=1)

        self.var_tipo = tk.StringVar(value="Pregrado")
        self.var_rut = tk.StringVar()
        self.var_nombres = tk.StringVar()
        self.var_apellidos = tk.StringVar()
        self.var_email = tk.StringVar()
        self.var_tel = tk.StringVar()
        self.var_sem = tk.StringVar(value="1")
        self.var_estado = tk.IntVar(value=1)

        self.var_uni = tk.StringVar()
        self.var_car = tk.StringVar()

        r = 0
        ttk.Label(frm, text="Tipo alumno:").grid(row=r, column=0, sticky="w", padx=8, pady=6)
        ttk.Combobox(frm, textvariable=self.var_tipo, values=["Pregrado", "Postgrado", "Intercambio"], state="readonly").grid(
            row=r, column=1, sticky="ew", padx=8, pady=6
        )

        r += 1
        ttk.Label(frm, text="RUT:").grid(row=r, column=0, sticky="w", padx=8, pady=6)
        ttk.Entry(frm, textvariable=self.var_rut).grid(row=r, column=1, sticky="ew", padx=8, pady=6)

        r += 1
        ttk.Label(frm, text="Nombres:").grid(row=r, column=0, sticky="w", padx=8, pady=6)
        ttk.Entry(frm, textvariable=self.var_nombres).grid(row=r, column=1, sticky="ew", padx=8, pady=6)

        r += 1
        ttk.Label(frm, text="Apellidos:").grid(row=r, column=0, sticky="w", padx=8, pady=6)
        ttk.Entry(frm, textvariable=self.var_apellidos).grid(row=r, column=1, sticky="ew", padx=8, pady=6)

        r += 1
        ttk.Label(frm, text="Email:").grid(row=r, column=0, sticky="w", padx=8, pady=6)
        ttk.Entry(frm, textvariable=self.var_email).grid(row=r, column=1, sticky="ew", padx=8, pady=6)

        r += 1
        ttk.Label(frm, text="Teléfono:").grid(row=r, column=0, sticky="w", padx=8, pady=6)
        ttk.Entry(frm, textvariable=self.var_tel).grid(row=r, column=1, sticky="ew", padx=8, pady=6)

        r += 1
        ttk.Label(frm, text="Universidad:").grid(row=r, column=0, sticky="w", padx=8, pady=6)
        self.cmb_uni = ttk.Combobox(frm, textvariable=self.var_uni, state="readonly")
        self.cmb_uni.grid(row=r, column=1, sticky="ew", padx=8, pady=6)
        self.cmb_uni.bind("<<ComboboxSelected>>", lambda e: self._cargar_carreras())

        r += 1
        ttk.Label(frm, text="Carrera:").grid(row=r, column=0, sticky="w", padx=8, pady=6)
        self.cmb_car = ttk.Combobox(frm, textvariable=self.var_car, state="readonly")
        self.cmb_car.grid(row=r, column=1, sticky="ew", padx=8, pady=6)

        r += 1
        ttk.Label(frm, text="Semestre:").grid(row=r, column=0, sticky="w", padx=8, pady=6)
        ttk.Entry(frm, textvariable=self.var_sem).grid(row=r, column=1, sticky="ew", padx=8, pady=6)

        r += 1
        ttk.Checkbutton(frm, text="Activo", variable=self.var_estado).grid(row=r, column=0, columnspan=2, sticky="w", padx=8, pady=6)

        # Botones
        r += 1
        btns = ttk.Frame(frm)
        btns.grid(row=r, column=0, columnspan=2, sticky="ew", padx=8, pady=10)

        ttk.Button(btns, text="Agregar", command=self.on_agregar).pack(side="left", padx=4)
        ttk.Button(btns, text="Actualizar", command=self.on_actualizar).pack(side="left", padx=4)
        ttk.Button(btns, text="Eliminar", command=self.on_eliminar).pack(side="left", padx=4)
        ttk.Button(btns, text="Limpiar", command=self.on_limpiar).pack(side="left", padx=4)

        # Tabla
        tabla = ttk.LabelFrame(cont, text="Listado de Alumnos")
        tabla.grid(row=0, column=1, sticky="nsew")
        tabla.rowconfigure(0, weight=1)
        tabla.columnconfigure(0, weight=1)

        cols = ("id", "rut", "nombre", "email", "uni", "car", "sem", "tipo", "estado")
        self.tree = ttk.Treeview(tabla, columns=cols, show="headings")
        for c, t in [
            ("id", "ID"),
            ("rut", "RUT"),
            ("nombre", "Alumno"),
            ("email", "Email"),
            ("uni", "Universidad"),
            ("car", "Carrera"),
            ("sem", "Sem"),
            ("tipo", "Tipo"),
            ("estado", "Activo"),
        ]:
            self.tree.heading(c, text=t)

        self.tree.column("id", width=60, anchor="center")
        self.tree.column("rut", width=120, anchor="w")
        self.tree.column("nombre", width=220, anchor="w")
        self.tree.column("email", width=180, anchor="w")
        self.tree.column("uni", width=180, anchor="w")
        self.tree.column("car", width=180, anchor="w")
        self.tree.column("sem", width=60, anchor="center")
        self.tree.column("tipo", width=110, anchor="center")
        self.tree.column("estado", width=70, anchor="center")

        sb = ttk.Scrollbar(tabla, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)

        self.tree.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        sb.grid(row=0, column=1, sticky="ns")

        self.tree.bind("<<TreeviewSelect>>", lambda e: self.on_select())

    # -----------------------
    # Combos
    # -----------------------
    def _cargar_universidades(self):
        self._unis = listar_universidades()
        nombres = [u["nombre"] for u in self._unis]
        self.cmb_uni["values"] = nombres
        if nombres:
            self.var_uni.set(nombres[0])
            self._cargar_carreras()

    def _cargar_carreras(self):
        uni_name = self.var_uni.get()
        uni_id = next((u["universidad_id"] for u in self._unis if u["nombre"] == uni_name), None)
        if uni_id is None:
            self.cmb_car["values"] = []
            self.var_car.set("")
            return

        self._cars = listar_carreras_por_universidad(uni_id)
        nombres = [c["nombre"] for c in self._cars]
        self.cmb_car["values"] = nombres
        self.var_car.set(nombres[0] if nombres else "")

    # -----------------------
    # Tabla
    # -----------------------
    def _cargar_tabla(self, registros):
        for i in self.tree.get_children():
            self.tree.delete(i)

        for a in registros:
            alumno = f"{a.get('apellidos','')} {a.get('nombres','')}".strip()
            self.tree.insert(
                "",
                "end",
                values=(
                    a.get("alumno_id", ""),
                    a.get("rut", ""),
                    alumno,
                    a.get("email", "") or "",
                    a.get("universidad_nombre", ""),
                    a.get("carrera_nombre", ""),
                    a.get("semestre", ""),
                    a.get("tipo_alumno", ""),
                    a.get("estado", ""),
                ),
            )

    # -----------------------
    # Eventos
    # -----------------------
    def on_buscar(self):
        self._cargar_tabla(buscar_alumnos(self.var_buscar.get()))

    def on_ver_todo(self):
        self.var_buscar.set("")
        self._cargar_tabla(listar_alumnos())

    def _leer_form(self):
        # Mapear nombres a IDs
        uni_name = self.var_uni.get()
        uni_id = next((u["universidad_id"] for u in self._unis if u["nombre"] == uni_name), None)

        car_name = self.var_car.get()
        car_id = next((c["carrera_id"] for c in getattr(self, "_cars", []) if c["nombre"] == car_name), None)

        if uni_id is None:
            raise ValueError("Debe seleccionar una universidad.")
        if car_id is None:
            raise ValueError("Debe seleccionar una carrera.")

        return {
            "tipo_alumno": self.var_tipo.get(),
            "rut": self.var_rut.get(),
            "nombres": self.var_nombres.get(),
            "apellidos": self.var_apellidos.get(),
            "email": self.var_email.get(),
            "telefono": self.var_tel.get(),
            "universidad_id": uni_id,
            "carrera_id": car_id,
            "semestre": self.var_sem.get(),
            "estado": self.var_estado.get(),
        }

    def on_agregar(self):
        try:
            crear_alumno(self._leer_form())
            messagebox.showinfo("OK", "Alumno agregado.")
            self._cargar_tabla(listar_alumnos())
            self.on_limpiar()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_actualizar(self):
        if self.alumno_sel is None:
            messagebox.showwarning("Atención", "Seleccione un alumno.")
            return
        try:
            ok = actualizar_alumno(self.alumno_sel, self._leer_form())
            if ok:
                messagebox.showinfo("OK", "Alumno actualizado.")
                self._cargar_tabla(listar_alumnos())
                self.on_limpiar()
            else:
                messagebox.showwarning("Atención", "No se pudo actualizar.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_eliminar(self):
        if self.alumno_sel is None:
            messagebox.showwarning("Atención", "Seleccione un alumno.")
            return
        if not messagebox.askyesno("Confirmar", "¿Eliminar alumno? (Borra sus inscripciones/notas)"):
            return
        try:
            eliminar_alumno(self.alumno_sel)
            messagebox.showinfo("OK", "Alumno eliminado.")
            self._cargar_tabla(listar_alumnos())
            self.on_limpiar()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_limpiar(self):
        self.alumno_sel = None
        self.var_tipo.set("Pregrado")
        self.var_rut.set("")
        self.var_nombres.set("")
        self.var_apellidos.set("")
        self.var_email.set("")
        self.var_tel.set("")
        self.var_sem.set("1")
        self.var_estado.set(1)

    def on_select(self):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0], "values")
        if not vals:
            return
        self.alumno_sel = int(vals[0])

        a = obtener_alumno(self.alumno_sel)
        if not a:
            return

        self.var_tipo.set(a.get("tipo_alumno", "Pregrado"))
        self.var_rut.set(a.get("rut", ""))
        self.var_nombres.set(a.get("nombres", ""))
        self.var_apellidos.set(a.get("apellidos", ""))
        self.var_email.set(a.get("email") or "")
        self.var_tel.set(a.get("telefono") or "")
        self.var_sem.set(str(a.get("semestre", 1)))
        self.var_estado.set(int(a.get("estado", 1)))

        # Set combos uni/carrera según IDs
        uni_id = a.get("universidad_id")
        car_id = a.get("carrera_id")

        # Cambiar universidad por nombre (dispara carga carreras)
        uni_name = next((u["nombre"] for u in self._unis if u["universidad_id"] == uni_id), "")
        self.var_uni.set(uni_name)
        self._cargar_carreras()

        car_name = next((c["nombre"] for c in getattr(self, "_cars", []) if c["carrera_id"] == car_id), "")
        self.var_car.set(car_name)
