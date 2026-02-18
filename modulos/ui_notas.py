# ============================================
# modulos/ui_notas.py
# Ventana 4 (refactor):
# - Notas se ingresan y ven en UNA SOLA TABLA (Treeview)
# - Doble click sobre "Nota" para editar dentro de la tabla
# - Exporta TODAS las notas a Excel/PDF
# ============================================

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from .repo_cursos import listar_cursos_detallados
from .repo_inscripciones import (
    listar_inscritos_por_curso,
    inscribir_alumno,
    obtener_inscripcion,
    desinscribir,
)
from .repo_alumnos import listar_alumnos
from .repo_notas import (
    obtener_notas_por_inscripcion,
    guardar_nota,
    obtener_promedio_inscripcion,
    obtener_reporte_notas_por_curso,
)
from .repo_evaluaciones import suma_porcentajes
from .exportaciones import exportar_notas_curso_excel, exportar_notas_curso_pdf


class VentanaNotas(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)

        self.title("Notas - Tabla única / Promedio / Exportación completa")
        self.geometry("1280x700")
        self.minsize(1200, 640)

        # IDs seleccionados
        self.curso_sel = None
        self.inscripcion_sel = None

        # Para edición “in-place” en Treeview
        self._editor_entry = None
        self._editor_item = None
        self._editor_col = None

        self._crear_ui()
        self._cargar_cursos()

    # ---------------------------------------------------------
    # UI
    # ---------------------------------------------------------
    def _crear_ui(self):
        # Barra superior: curso + acciones
        top = ttk.Frame(self)
        top.pack(fill="x", padx=10, pady=10)

        ttk.Label(top, text="Curso:").pack(side="left")
        self.var_curso = tk.StringVar()
        self.cmb_curso = ttk.Combobox(top, textvariable=self.var_curso, state="readonly", width=80)
        self.cmb_curso.pack(side="left", padx=8)
        self.cmb_curso.bind("<<ComboboxSelected>>", lambda e: self.on_curso_change())

        self.lbl_suma = ttk.Label(top, text="Suma %: 0.00")
        self.lbl_suma.pack(side="left", padx=12)

        ttk.Button(top, text="Inscribir alumno", command=self.on_inscribir).pack(side="left", padx=6)
        ttk.Button(top, text="Quitar inscripción", command=self.on_desinscribir).pack(side="left", padx=6)

        ttk.Separator(top, orient="vertical").pack(side="left", fill="y", padx=10)

        ttk.Button(top, text="Exportar Excel (todas las notas)", command=self.on_exportar_excel).pack(side="left", padx=6)
        ttk.Button(top, text="Exportar PDF (todas las notas)", command=self.on_exportar_pdf).pack(side="left", padx=6)

        # Contenedor principal
        cont = ttk.Frame(self)
        cont.pack(fill="both", expand=True, padx=10, pady=10)
        cont.columnconfigure(0, weight=2)
        cont.columnconfigure(1, weight=3)
        cont.rowconfigure(0, weight=1)

        # Izquierda: alumnos inscritos
        izq = ttk.LabelFrame(cont, text="Alumnos inscritos")
        izq.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        izq.rowconfigure(0, weight=1)
        izq.columnconfigure(0, weight=1)

        self.tree_insc = ttk.Treeview(
            izq,
            columns=("insc", "rut", "alumno", "email", "prom", "sum"),
            show="headings",
            selectmode="browse",
        )
        for c, t in [
            ("insc", "InscID"),
            ("rut", "RUT"),
            ("alumno", "Alumno"),
            ("email", "Email"),
            ("prom", "Promedio"),
            ("sum", "Suma %"),
        ]:
            self.tree_insc.heading(c, text=t)

        self.tree_insc.column("insc", width=70, anchor="center")
        self.tree_insc.column("rut", width=120, anchor="w")
        self.tree_insc.column("alumno", width=230, anchor="w")
        self.tree_insc.column("email", width=170, anchor="w")
        self.tree_insc.column("prom", width=90, anchor="center")
        self.tree_insc.column("sum", width=80, anchor="center")

        sb1 = ttk.Scrollbar(izq, orient="vertical", command=self.tree_insc.yview)
        self.tree_insc.configure(yscrollcommand=sb1.set)

        self.tree_insc.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        sb1.grid(row=0, column=1, sticky="ns")

        self.tree_insc.bind("<<TreeviewSelect>>", lambda e: self.on_select_inscrito())

        # Derecha: tabla única de notas
        der = ttk.LabelFrame(cont, text="Tabla de notas del alumno seleccionado")
        der.grid(row=0, column=1, sticky="nsew")
        der.rowconfigure(1, weight=1)
        der.columnconfigure(0, weight=1)

        self.lbl_alumno = ttk.Label(der, text="Seleccione un alumno inscrito.", font=("Segoe UI", 11, "bold"))
        self.lbl_alumno.grid(row=0, column=0, sticky="w", padx=10, pady=10)

        self.tree_notas = ttk.Treeview(
            der,
            columns=("eval_id", "evaluacion", "porcentaje", "nota"),
            show="headings",
            selectmode="browse",
        )
        self.tree_notas.heading("eval_id", text="EvalID")
        self.tree_notas.heading("evaluacion", text="Evaluación")
        self.tree_notas.heading("porcentaje", text="%")
        self.tree_notas.heading("nota", text="Nota")

        # Ocultamos eval_id (solo interno)
        self.tree_notas.column("eval_id", width=0, stretch=False)
        self.tree_notas.column("evaluacion", width=420, anchor="w")
        self.tree_notas.column("porcentaje", width=80, anchor="center")
        self.tree_notas.column("nota", width=80, anchor="center")

        sb2 = ttk.Scrollbar(der, orient="vertical", command=self.tree_notas.yview)
        self.tree_notas.configure(yscrollcommand=sb2.set)

        self.tree_notas.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        sb2.grid(row=1, column=1, sticky="ns", pady=10)

        # Doble click para editar la celda Nota
        self.tree_notas.bind("<Double-1>", self.on_doble_click_nota)

        # Botones y promedio
        botones = ttk.Frame(der)
        botones.grid(row=2, column=0, sticky="w", padx=10, pady=10)

        ttk.Button(botones, text="Guardar todo (leer tabla)", command=self.on_guardar_todo).pack(side="left", padx=5)
        ttk.Button(botones, text="Recalcular promedio", command=self.on_recalcular).pack(side="left", padx=5)

        self.lbl_prom = ttk.Label(der, text="Promedio ponderado: -", font=("Segoe UI", 11))
        self.lbl_prom.grid(row=3, column=0, sticky="w", padx=10, pady=10)

    # ---------------------------------------------------------
    # Cursos
    # ---------------------------------------------------------
    def _cargar_cursos(self):
        self._cursos = listar_cursos_detallados()

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

    def _curso_info(self):
        txt = self.var_curso.get()
        if not txt:
            return None
        idx = self.cmb_curso["values"].index(txt)
        return self._cursos[idx]

    def on_curso_change(self):
        info = self._curso_info()
        if not info:
            return

        self.curso_sel = int(info["curso_id"])
        self.inscripcion_sel = None

        # Mostrar suma % para advertir si no llega a 100
        s = suma_porcentajes(self.curso_sel)
        self.lbl_suma.config(text=f"Suma %: {s:.2f}", foreground=("green" if abs(s - 100) < 0.001 else "red"))

        self._refrescar_inscritos()
        self._limpiar_notas()

    # ---------------------------------------------------------
    # Inscritos (lista izquierda)
    # ---------------------------------------------------------
    def _refrescar_inscritos(self):
        for i in self.tree_insc.get_children():
            self.tree_insc.delete(i)

        if self.curso_sel is None:
            return

        ins = listar_inscritos_por_curso(self.curso_sel)

        for r in ins:
            alumno = f"{r.get('apellidos','')} {r.get('nombres','')}".strip()
            prom = float(r.get("promedio_ponderado") or 0)
            s = float(r.get("suma_porcentajes") or 0)

            self.tree_insc.insert(
                "",
                "end",
                values=(
                    r.get("inscripcion_id", ""),
                    r.get("rut", ""),
                    alumno,
                    r.get("email", "") or "",
                    f"{prom:.2f}",
                    f"{s:.2f}",
                ),
            )

    def on_select_inscrito(self):
        sel = self.tree_insc.selection()
        if not sel:
            return
        vals = self.tree_insc.item(sel[0], "values")
        if not vals:
            return

        self.inscripcion_sel = int(vals[0])
        self.lbl_alumno.config(text=f"{vals[2]} (RUT: {vals[1]})")

        self._cargar_notas_en_tabla()
        self.on_recalcular()

    # ---------------------------------------------------------
    # Tabla única de notas (derecha)
    # ---------------------------------------------------------
    def _limpiar_notas(self):
        for i in self.tree_notas.get_children():
            self.tree_notas.delete(i)
        self.lbl_alumno.config(text="Seleccione un alumno inscrito.")
        self.lbl_prom.config(text="Promedio ponderado: -")

    def _cargar_notas_en_tabla(self):
        self._limpiar_notas()

        if self.inscripcion_sel is None:
            return

        filas = obtener_notas_por_inscripcion(self.inscripcion_sel)

        for f in filas:
            self.tree_notas.insert(
                "",
                "end",
                values=(
                    int(f["evaluacion_id"]),
                    f["nombre"],
                    f"{float(f['porcentaje']):.2f}",
                    f"{float(f.get('nota') or 0):.2f}",
                ),
            )

    # ---------------------------------------------------------
    # Edición in-place: doble click sobre columna "Nota"
    # ---------------------------------------------------------
    def on_doble_click_nota(self, event):
        # Si no hay inscripción seleccionada, no se edita
        if self.inscripcion_sel is None:
            return

        # Identificar fila y columna clickeada
        row_id = self.tree_notas.identify_row(event.y)
        col = self.tree_notas.identify_column(event.x)

        # Columnas:
        # #1 eval_id (oculta)
        # #2 evaluacion
        # #3 porcentaje
        # #4 nota  <-- queremos editar esta
        if col != "#4" or not row_id:
            return

        # Obtenemos la caja (bbox) de esa celda para posicionar el Entry encima
        bbox = self.tree_notas.bbox(row_id, col)
        if not bbox:
            return
        x, y, w, h = bbox

        # Si existe un editor anterior, lo destruimos
        if self._editor_entry is not None:
            self._editor_entry.destroy()

        # Valor actual de la celda Nota
        valor_actual = self.tree_notas.set(row_id, "nota")

        # Creamos un Entry encima de la celda
        self._editor_entry = ttk.Entry(self.tree_notas)
        self._editor_entry.place(x=x, y=y, width=w, height=h)
        self._editor_entry.insert(0, valor_actual)
        self._editor_entry.focus()

        # Guardamos referencias para saber qué editar
        self._editor_item = row_id
        self._editor_col = "nota"

        # Confirmar con Enter o al perder foco
        self._editor_entry.bind("<Return>", lambda e: self._commit_edicion())
        self._editor_entry.bind("<FocusOut>", lambda e: self._commit_edicion())

    def _commit_edicion(self):
        """Confirma la edición del Entry y guarda la nota en BD."""
        if self._editor_entry is None or self._editor_item is None:
            return

        nuevo_valor = self._editor_entry.get().strip()
        if nuevo_valor == "":
            nuevo_valor = "0"

        # Validación + guardado
        try:
            nota = float(nuevo_valor)

            # evaluacion_id está en la fila
            eval_id = int(self.tree_notas.set(self._editor_item, "eval_id"))

            # Guardar en BD
            guardar_nota(self.inscripcion_sel, eval_id, nota)

            # Reflejar en tabla con formato 2 decimales
            self.tree_notas.set(self._editor_item, "nota", f"{nota:.2f}")

            # Actualizar promedio y lista izquierda
            self._refrescar_inscritos()
            self.on_recalcular()

        except Exception as e:
            messagebox.showerror("Error", str(e))

        # Destruir el editor
        self._editor_entry.destroy()
        self._editor_entry = None
        self._editor_item = None
        self._editor_col = None

    # ---------------------------------------------------------
    # Guardar todo (lee todas las filas de la tabla y persiste)
    # ---------------------------------------------------------
    def on_guardar_todo(self):
        if self.inscripcion_sel is None:
            messagebox.showwarning("Atención", "Seleccione un alumno inscrito.")
            return

        try:
            for item in self.tree_notas.get_children():
                eval_id = int(self.tree_notas.set(item, "eval_id"))
                nota_str = self.tree_notas.set(item, "nota").strip()
                if nota_str == "":
                    nota_str = "0"
                guardar_nota(self.inscripcion_sel, eval_id, float(nota_str))

            messagebox.showinfo("OK", "Notas guardadas (tabla completa).")
            self._refrescar_inscritos()
            self.on_recalcular()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---------------------------------------------------------
    # Promedio
    # ---------------------------------------------------------
    def on_recalcular(self):
        if self.inscripcion_sel is None:
            return

        p = obtener_promedio_inscripcion(self.inscripcion_sel)
        if not p:
            self.lbl_prom.config(text="Promedio ponderado: -")
            return

        prom = float(p.get("promedio_ponderado") or 0)
        suma = float(p.get("suma_porcentajes") or 0)

        if abs(suma - 100.0) > 0.001:
            self.lbl_prom.config(text=f"Promedio (⚠ suma %={suma:.2f}): {prom:.2f}")
        else:
            self.lbl_prom.config(text=f"Promedio ponderado: {prom:.2f}")

    # ---------------------------------------------------------
    # Inscribir / desinscribir
    # ---------------------------------------------------------
    def on_inscribir(self):
        if self.curso_sel is None:
            messagebox.showwarning("Atención", "Seleccione un curso.")
            return

        win = tk.Toplevel(self)
        win.title("Inscribir alumno")
        win.geometry("600x420")
        win.transient(self)
        win.grab_set()

        ttk.Label(win, text="Seleccione un alumno y presione 'Inscribir':", font=("Segoe UI", 10, "bold")).pack(pady=10)

        alumnos = listar_alumnos()

        tree = ttk.Treeview(win, columns=("id", "rut", "nombre", "email"), show="headings")
        tree.heading("id", text="ID")
        tree.heading("rut", text="RUT")
        tree.heading("nombre", text="Alumno")
        tree.heading("email", text="Email")

        tree.column("id", width=60, anchor="center")
        tree.column("rut", width=120, anchor="w")
        tree.column("nombre", width=250, anchor="w")
        tree.column("email", width=160, anchor="w")

        for a in alumnos:
            nombre = f"{a.get('apellidos','')} {a.get('nombres','')}".strip()
            tree.insert("", "end", values=(a["alumno_id"], a.get("rut", ""), nombre, a.get("email", "") or ""))

        tree.pack(fill="both", expand=True, padx=10, pady=10)

        def inscribir_sel():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Atención", "Seleccione un alumno.")
                return

            vals = tree.item(sel[0], "values")
            alumno_id = int(vals[0])

            # Evitar duplicado
            if obtener_inscripcion(alumno_id, self.curso_sel):
                messagebox.showwarning("Atención", "El alumno ya está inscrito en este curso.")
                return

            try:
                inscribir_alumno(alumno_id, self.curso_sel)
                messagebox.showinfo("OK", "Alumno inscrito.")
                win.destroy()
                self._refrescar_inscritos()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(win, text="Inscribir", command=inscribir_sel).pack(pady=10)

    def on_desinscribir(self):
        if self.inscripcion_sel is None:
            messagebox.showwarning("Atención", "Seleccione un alumno inscrito.")
            return

        if not messagebox.askyesno("Confirmar", "¿Quitar inscripción? (Borra notas por cascada)"):
            return

        try:
            desinscribir(self.inscripcion_sel)
            self.inscripcion_sel = None
            self._refrescar_inscritos()
            self._limpiar_notas()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---------------------------------------------------------
    # Exportación completa (TODAS las notas)
    # ---------------------------------------------------------
    def on_exportar_excel(self):
        if self.curso_sel is None:
            messagebox.showwarning("Atención", "Seleccione un curso.")
            return

        try:
            # Reporte completo (evaluaciones + notas de todos)
            rep = obtener_reporte_notas_por_curso(self.curso_sel)
            evaluaciones = rep["evaluaciones"]
            filas = rep["filas"]

            curso_info = self._curso_info()

            ruta = filedialog.asksaveasfilename(
                title="Guardar Excel",
                defaultextension=".xlsx",
                filetypes=[("Excel", "*.xlsx")],
                initialdir="exports",
            )
            if not ruta:
                return

            exportar_notas_curso_excel(ruta, curso_info, evaluaciones, filas)
            messagebox.showinfo("OK", "Excel exportado con todas las notas.")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_exportar_pdf(self):
        if self.curso_sel is None:
            messagebox.showwarning("Atención", "Seleccione un curso.")
            return

        try:
            rep = obtener_reporte_notas_por_curso(self.curso_sel)
            evaluaciones = rep["evaluaciones"]
            filas = rep["filas"]

            curso_info = self._curso_info()

            ruta = filedialog.asksaveasfilename(
                title="Guardar PDF",
                defaultextension=".pdf",
                filetypes=[("PDF", "*.pdf")],
                initialdir="exports",
            )
            if not ruta:
                return

            exportar_notas_curso_pdf(ruta, curso_info, evaluaciones, filas)
            messagebox.showinfo("OK", "PDF exportado con todas las notas.")

        except Exception as e:
            messagebox.showerror("Error", str(e))
