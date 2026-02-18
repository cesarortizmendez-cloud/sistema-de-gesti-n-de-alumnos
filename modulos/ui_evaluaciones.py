# ============================================
# modulos/ui_evaluaciones.py
# Ventana 3: evaluaciones + porcentajes por curso
# ============================================

import tkinter as tk
from tkinter import ttk, messagebox

from .repo_cursos import listar_cursos_detallados
from .repo_evaluaciones import listar_evaluaciones, crear_evaluacion, actualizar_evaluacion, eliminar_evaluacion, suma_porcentajes


class VentanaEvaluaciones(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)

        self.title("Evaluaciones - Porcentajes por Curso")
        self.geometry("900x600")
        self.minsize(860, 560)

        self.curso_sel = None
        self.eval_sel = None

        self._crear_ui()
        self._cargar_cursos()

    def _crear_ui(self):
        top = ttk.Frame(self)
        top.pack(fill="x", padx=10, pady=10)

        ttk.Label(top, text="Curso:").pack(side="left")
        self.var_curso = tk.StringVar()
        self.cmb_curso = ttk.Combobox(top, textvariable=self.var_curso, state="readonly", width=70)
        self.cmb_curso.pack(side="left", padx=8)
        self.cmb_curso.bind("<<ComboboxSelected>>", lambda e: self.on_curso_change())

        self.lbl_suma = ttk.Label(top, text="Suma %: 0.00")
        self.lbl_suma.pack(side="left", padx=10)

        cont = ttk.Frame(self)
        cont.pack(fill="both", expand=True, padx=10, pady=10)
        cont.columnconfigure(0, weight=1)
        cont.rowconfigure(1, weight=1)

        frm = ttk.LabelFrame(cont, text="Nueva / Editar Evaluación")
        frm.grid(row=0, column=0, sticky="ew")
        frm.columnconfigure(1, weight=1)

        self.var_nombre = tk.StringVar()
        self.var_porcentaje = tk.StringVar()

        ttk.Label(frm, text="Nombre:").grid(row=0, column=0, sticky="w", padx=8, pady=6)
        ttk.Entry(frm, textvariable=self.var_nombre).grid(row=0, column=1, sticky="ew", padx=8, pady=6)

        ttk.Label(frm, text="%:").grid(row=0, column=2, sticky="w", padx=8, pady=6)
        ttk.Entry(frm, textvariable=self.var_porcentaje, width=10).grid(row=0, column=3, sticky="w", padx=8, pady=6)

        btns = ttk.Frame(frm)
        btns.grid(row=1, column=0, columnspan=4, sticky="w", padx=8, pady=8)
        ttk.Button(btns, text="Agregar", command=self.on_agregar).pack(side="left", padx=4)
        ttk.Button(btns, text="Actualizar", command=self.on_actualizar).pack(side="left", padx=4)
        ttk.Button(btns, text="Eliminar", command=self.on_eliminar).pack(side="left", padx=4)
        ttk.Button(btns, text="Limpiar", command=self.on_limpiar).pack(side="left", padx=4)

        tabla = ttk.LabelFrame(cont, text="Evaluaciones del curso")
        tabla.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        tabla.rowconfigure(0, weight=1)
        tabla.columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(tabla, columns=("id", "nombre", "porcentaje"), show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("nombre", text="Evaluación")
        self.tree.heading("porcentaje", text="%")

        self.tree.column("id", width=70, anchor="center")
        self.tree.column("nombre", width=520, anchor="w")
        self.tree.column("porcentaje", width=120, anchor="center")

        sb = ttk.Scrollbar(tabla, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)

        self.tree.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        sb.grid(row=0, column=1, sticky="ns")

        self.tree.bind("<<TreeviewSelect>>", lambda e: self.on_select())

    def _cargar_cursos(self):
        self._cursos = listar_cursos_detallados()
        # Display amigable
        display = []
        for c in self._cursos:
            txt = f"{c['universidad_nombre']} | {c['carrera_nombre']} | Sem {c['semestre']} | {c['curso_nombre']}"
            if c.get("codigo"):
                txt += f" ({c['codigo']})"
            display.append(txt)

        self.cmb_curso["values"] = display
        if display:
            self.var_curso.set(display[0])
            self.on_curso_change()

    def _curso_id_seleccionado(self):
        txt = self.var_curso.get()
        if not txt:
            return None
        idx = self.cmb_curso["values"].index(txt)
        return int(self._cursos[idx]["curso_id"])

    def on_curso_change(self):
        self.curso_sel = self._curso_id_seleccionado()
        self.eval_sel = None
        self.on_limpiar()
        self._refrescar_tabla()

    def _refrescar_tabla(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        if self.curso_sel is None:
            return

        evs = listar_evaluaciones(self.curso_sel)
        for e in evs:
            self.tree.insert("", "end", values=(e["evaluacion_id"], e["nombre"], f"{float(e['porcentaje']):.2f}"))

        s = suma_porcentajes(self.curso_sel)
        self.lbl_suma.config(text=f"Suma %: {s:.2f}")
        if abs(s - 100.0) < 0.001:
            self.lbl_suma.config(foreground="green")
        else:
            self.lbl_suma.config(foreground="red")

    def on_select(self):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0], "values")
        self.eval_sel = int(vals[0])
        self.var_nombre.set(vals[1])
        self.var_porcentaje.set(vals[2])

    def on_agregar(self):
        if self.curso_sel is None:
            messagebox.showwarning("Atención", "Seleccione un curso.")
            return
        try:
            crear_evaluacion(self.curso_sel, self.var_nombre.get(), self.var_porcentaje.get())
            self.on_limpiar()
            self._refrescar_tabla()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_actualizar(self):
        if self.curso_sel is None or self.eval_sel is None:
            messagebox.showwarning("Atención", "Seleccione una evaluación.")
            return
        try:
            actualizar_evaluacion(self.eval_sel, self.curso_sel, self.var_nombre.get(), self.var_porcentaje.get())
            self.on_limpiar()
            self._refrescar_tabla()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_eliminar(self):
        if self.eval_sel is None:
            messagebox.showwarning("Atención", "Seleccione una evaluación.")
            return
        if not messagebox.askyesno("Confirmar", "¿Eliminar evaluación? (Borra notas asociadas)"):
            return
        try:
            eliminar_evaluacion(self.eval_sel)
            self.on_limpiar()
            self._refrescar_tabla()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_limpiar(self):
        self.eval_sel = None
        self.var_nombre.set("")
        self.var_porcentaje.set("")
