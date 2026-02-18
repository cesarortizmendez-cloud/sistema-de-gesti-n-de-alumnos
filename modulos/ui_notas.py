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

        self.title("Notas - Ingreso y Promedio")
        self.geometry("1280x720")
        self.minsize(1200, 660)

        self.curso_sel = None
        self.inscripcion_sel = None

        # Editor in-place (doble click)
        self._editor_entry = None
        self._editor_item = None

        # Panel casillas
        self.var_eval_nombre = tk.StringVar()
        self.var_eval_porcentaje = tk.StringVar()
        self.var_nota = tk.StringVar()

        self._crear_ui()
        self._cargar_cursos()

    # ---------------------------------------------------------
    # Ajuste columnas: 1/3 - 1/3 - 1/3
    # ---------------------------------------------------------
    def _ajustar_columnas_notas(self):
        """
        Ajusta las 3 columnas del Treeview a partes iguales (1/3 cada una).
        Se ejecuta al dibujar y cuando la tabla cambia de tamaño.
        """
        total = self.tree_notas.winfo_width()
        if total <= 1:
            return  # Aún no está dibujado

        w = total // 3
        w_eval = w
        w_por = w
        w_not = total - (w_eval + w_por)  # el resto para cuadrar exacto

        self.tree_notas.column("evaluacion", width=w_eval, stretch=True)
        self.tree_notas.column("porcentaje", width=w_por, stretch=True)
        self.tree_notas.column("nota", width=w_not, stretch=True)

    # ---------------------------------------------------------
    # UI
    # ---------------------------------------------------------
    def _crear_ui(self):
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

        ttk.Button(top, text="Exportar Excel", command=self.on_exportar_excel).pack(side="left", padx=6)
        ttk.Button(top, text="Exportar PDF", command=self.on_exportar_pdf).pack(side="left", padx=6)

        cont = ttk.Frame(self)
        cont.pack(fill="both", expand=True, padx=10, pady=10)
        cont.columnconfigure(0, weight=2)
        cont.columnconfigure(1, weight=3)
        cont.rowconfigure(0, weight=1)

        # ---------------- IZQUIERDA: INSCRITOS ----------------
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
        self.tree_insc.column("alumno", width=240, anchor="w")
        self.tree_insc.column("email", width=170, anchor="w")
        self.tree_insc.column("prom", width=90, anchor="center")
        self.tree_insc.column("sum", width=80, anchor="center")

        sb1 = ttk.Scrollbar(izq, orient="vertical", command=self.tree_insc.yview)
        self.tree_insc.configure(yscrollcommand=sb1.set)
        self.tree_insc.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        sb1.grid(row=0, column=1, sticky="ns")

        self.tree_insc.bind("<<TreeviewSelect>>", lambda e: self.on_select_inscrito())

        # ---------------- DERECHA: NOTAS ----------------
        der = ttk.LabelFrame(cont, text="Tabla de notas del alumno seleccionado")
        der.grid(row=0, column=1, sticky="nsew")
        der.columnconfigure(0, weight=1)
        der.rowconfigure(1, weight=1)

        self.lbl_alumno = ttk.Label(der, text="Seleccione un alumno inscrito.", font=("Segoe UI", 11, "bold"))
        self.lbl_alumno.grid(row=0, column=0, sticky="w", padx=10, pady=10)

        # Treeview con 3 columnas visibles (Evaluación / % / Nota)
        # El evaluacion_id se guarda como IID del item (no se muestra como columna)
        self.tree_notas = ttk.Treeview(
            der,
            columns=("evaluacion", "porcentaje", "nota"),
            show="headings",
            selectmode="browse",
        )
        self.tree_notas.heading("evaluacion", text="Evaluación")
        self.tree_notas.heading("porcentaje", text="%")
        self.tree_notas.heading("nota", text="Nota")

        # Nota: aquí los widths iniciales son “provisorios”, luego se auto-ajustan a 1/3
        self.tree_notas.column("evaluacion", width=200, anchor="w")
        self.tree_notas.column("porcentaje", width=100, anchor="center")
        self.tree_notas.column("nota", width=100, anchor="center")

        sb2 = ttk.Scrollbar(der, orient="vertical", command=self.tree_notas.yview)
        self.tree_notas.configure(yscrollcommand=sb2.set)
        self.tree_notas.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        sb2.grid(row=1, column=1, sticky="ns", pady=(0, 10))

        # ✅ Ajuste automático: 1/3 - 1/3 - 1/3 (al iniciar y al redimensionar)
        self.tree_notas.bind("<Configure>", lambda e: self._ajustar_columnas_notas())
        self.after(120, self._ajustar_columnas_notas)

        # Doble click para editar la columna Nota
        self.tree_notas.bind("<Double-1>", self.on_doble_click_nota)

        # Selección para cargar panel
        self.tree_notas.bind("<<TreeviewSelect>>", lambda e: self.on_select_evaluacion())

        # Panel casillas
        panel = ttk.LabelFrame(der, text="Ingreso de nota (casillas)")
        panel.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        panel.columnconfigure(1, weight=1)

        ttk.Label(panel, text="Evaluación:").grid(row=0, column=0, sticky="w", padx=8, pady=6)
        ttk.Entry(panel, textvariable=self.var_eval_nombre, state="readonly").grid(row=0, column=1, sticky="ew", padx=8, pady=6)

        ttk.Label(panel, text="%:").grid(row=0, column=2, sticky="w", padx=8, pady=6)
        ttk.Entry(panel, textvariable=self.var_eval_porcentaje, width=10, state="readonly").grid(row=0, column=3, sticky="w", padx=8, pady=6)

        ttk.Label(panel, text="Nota:").grid(row=1, column=0, sticky="w", padx=8, pady=6)
        ttk.Entry(panel, textvariable=self.var_nota, width=15).grid(row=1, column=1, sticky="w", padx=8, pady=6)

        btns_panel = ttk.Frame(panel)
        btns_panel.grid(row=1, column=2, columnspan=2, sticky="e", padx=8, pady=6)
        ttk.Button(btns_panel, text="Guardar nota", command=self.on_guardar_nota_panel).pack(side="left", padx=5)
        ttk.Button(btns_panel, text="Limpiar", command=self.on_limpiar_panel).pack(side="left", padx=5)

        botones = ttk.Frame(der)
        botones.grid(row=3, column=0, sticky="w", padx=10, pady=6)
        ttk.Button(botones, text="Guardar todo (leer tabla)", command=self.on_guardar_todo).pack(side="left", padx=5)
        ttk.Button(botones, text="Recalcular promedio", command=self.on_recalcular).pack(side="left", padx=5)

        self.lbl_prom = ttk.Label(der, text="Promedio ponderado: 0.00", font=("Segoe UI", 11))
        self.lbl_prom.grid(row=4, column=0, sticky="w", padx=10, pady=10)

    # ---------------------------------------------------------
    # Helpers: evaluacion_id desde el iid
    # ---------------------------------------------------------
    def _eval_id_seleccionado(self):
        sel = self.tree_notas.selection()
        if not sel:
            return None
        try:
            return int(sel[0])  # iid = evaluacion_id
        except Exception:
            return None

    def _seleccionar_eval_por_id(self, evaluacion_id: int):
        iid = str(int(evaluacion_id))
        if iid in self.tree_notas.get_children():
            self.tree_notas.selection_set(iid)
            self.tree_notas.focus(iid)
            self.tree_notas.see(iid)
            self.on_select_evaluacion()

    def _seleccionar_primera_eval(self):
        items = self.tree_notas.get_children()
        if items:
            self.tree_notas.selection_set(items[0])
            self.tree_notas.focus(items[0])
            self.tree_notas.see(items[0])
            self.on_select_evaluacion()

    # ---------------------------------------------------------
    # Cursos
    # ---------------------------------------------------------
    def _cargar_cursos(self):
        self._cursos = listar_cursos_detallados()
        display = []
        for c in self._cursos:
            txt = f"{c['universidad_nombre']} | {c['carrera_nombre']} | Periodo {c['periodo']} | {c['curso_nombre']}"
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

        s = suma_porcentajes(self.curso_sel)
        self.lbl_suma.config(text=f"Suma %: {s:.2f}")

        self._refrescar_inscritos()
        self._limpiar_notas()

    # ---------------------------------------------------------
    # Inscritos
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
                values=(r["inscripcion_id"], r["rut"], alumno, r.get("email") or "", f"{prom:.2f}", f"{s:.2f}"),
            )

    def on_select_inscrito(self):
        sel = self.tree_insc.selection()
        if not sel:
            return
        vals = self.tree_insc.item(sel[0], "values")

        self.inscripcion_sel = int(vals[0])
        self.lbl_alumno.config(text=f"{vals[2]} (RUT: {vals[1]})")

        self._cargar_notas_en_tabla()
        self._seleccionar_primera_eval()
        self.on_recalcular()

    # ---------------------------------------------------------
    # Notas
    # ---------------------------------------------------------
    def _limpiar_notas(self):
        for i in self.tree_notas.get_children():
            self.tree_notas.delete(i)

        self.lbl_alumno.config(text="Seleccione un alumno inscrito.")
        self.lbl_prom.config(text="Promedio ponderado: 0.00")
        self.on_limpiar_panel()

    def _cargar_notas_en_tabla(self):
        if self.inscripcion_sel is None:
            self._limpiar_notas()
            return

        eval_sel = self._eval_id_seleccionado()

        for i in self.tree_notas.get_children():
            self.tree_notas.delete(i)

        filas = obtener_notas_por_inscripcion(self.inscripcion_sel)

        for f in filas:
            eval_id = int(f["evaluacion_id"])
            nombre = f["nombre"]
            porcentaje = float(f["porcentaje"])
            nota = float(f.get("nota") or 0)

            self.tree_notas.insert(
                "",
                "end",
                iid=str(eval_id),
                values=(nombre, f"{porcentaje:.2f}", f"{nota:.2f}"),
            )

        if eval_sel is not None:
            self._seleccionar_eval_por_id(eval_sel)

        # Re-ajustar columnas (por si el tree todavía no se ajustó)
        self.after(1, self._ajustar_columnas_notas)

    def on_select_evaluacion(self):
        sel = self.tree_notas.selection()
        if not sel:
            return

        iid = sel[0]
        vals = self.tree_notas.item(iid, "values")
        self.var_eval_nombre.set(vals[0] if len(vals) > 0 else "")
        self.var_eval_porcentaje.set(vals[1] if len(vals) > 1 else "")
        self.var_nota.set(vals[2] if len(vals) > 2 else "")

    def on_guardar_nota_panel(self):
        if self.inscripcion_sel is None:
            messagebox.showwarning("Atención", "Seleccione un alumno inscrito.")
            return

        eval_id = self._eval_id_seleccionado()
        if eval_id is None:
            messagebox.showwarning("Atención", "Seleccione una evaluación.")
            return

        try:
            nota = float(self.var_nota.get().strip() or "0")
            guardar_nota(self.inscripcion_sel, eval_id, nota)

            self._cargar_notas_en_tabla()
            self._seleccionar_eval_por_id(eval_id)

            self._refrescar_inscritos()
            self.on_recalcular()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_limpiar_panel(self):
        self.var_eval_nombre.set("")
        self.var_eval_porcentaje.set("")
        self.var_nota.set("")

    # ---------------------------------------------------------
    # Doble click para editar "Nota" en la tabla
    # ---------------------------------------------------------
    def on_doble_click_nota(self, event):
        if self.inscripcion_sel is None:
            return

        row_id = self.tree_notas.identify_row(event.y)
        col = self.tree_notas.identify_column(event.x)

        # En este Treeview hay 3 columnas visibles:
        # #1 evaluacion, #2 porcentaje, #3 nota
        if col != "#3" or not row_id:
            return

        bbox = self.tree_notas.bbox(row_id, col)
        if not bbox:
            return

        x, y, w, h = bbox

        if self._editor_entry is not None:
            self._editor_entry.destroy()

        valor_actual = self.tree_notas.set(row_id, "nota")

        self._editor_entry = ttk.Entry(self.tree_notas)
        self._editor_entry.place(x=x, y=y, width=w, height=h)
        self._editor_entry.insert(0, valor_actual)
        self._editor_entry.focus()

        self._editor_item = row_id

        self._editor_entry.bind("<Return>", lambda e: self._commit_edicion())
        self._editor_entry.bind("<FocusOut>", lambda e: self._commit_edicion())

    def _commit_edicion(self):
        if self._editor_entry is None or self._editor_item is None:
            return

        try:
            eval_id = int(self._editor_item)
            nota = float(self._editor_entry.get().strip() or "0")

            guardar_nota(self.inscripcion_sel, eval_id, nota)

            self._cargar_notas_en_tabla()
            self._seleccionar_eval_por_id(eval_id)

            self._refrescar_inscritos()
            self.on_recalcular()

        except Exception as e:
            messagebox.showerror("Error", str(e))

        self._editor_entry.destroy()
        self._editor_entry = None
        self._editor_item = None

    # ---------------------------------------------------------
    # Guardar todo
    # ---------------------------------------------------------
    def on_guardar_todo(self):
        if self.inscripcion_sel is None:
            messagebox.showwarning("Atención", "Seleccione un alumno inscrito.")
            return

        try:
            for iid in self.tree_notas.get_children():
                eval_id = int(iid)
                nota_str = self.tree_notas.set(iid, "nota").strip() or "0"
                guardar_nota(self.inscripcion_sel, eval_id, float(nota_str))

            self._cargar_notas_en_tabla()
            self._seleccionar_primera_eval()

            messagebox.showinfo("OK", "Notas guardadas.")
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
        prom = float((p or {}).get("promedio_ponderado") or 0)
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
    # Exportación
    # ---------------------------------------------------------
    def on_exportar_excel(self):
        if self.curso_sel is None:
            messagebox.showwarning("Atención", "Seleccione un curso.")
            return
        try:
            rep = obtener_reporte_notas_por_curso(self.curso_sel)
            ruta = filedialog.asksaveasfilename(
                title="Guardar Excel",
                defaultextension=".xlsx",
                filetypes=[("Excel", "*.xlsx")],
                initialdir="exports",
            )
            if not ruta:
                return
            exportar_notas_curso_excel(ruta, self._curso_info(), rep["evaluaciones"], rep["filas"])
            messagebox.showinfo("OK", "Excel exportado.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_exportar_pdf(self):
        if self.curso_sel is None:
            messagebox.showwarning("Atención", "Seleccione un curso.")
            return
        try:
            rep = obtener_reporte_notas_por_curso(self.curso_sel)
            ruta = filedialog.asksaveasfilename(
                title="Guardar PDF",
                defaultextension=".pdf",
                filetypes=[("PDF", "*.pdf")],
                initialdir="exports",
            )
            if not ruta:
                return
            exportar_notas_curso_pdf(ruta, self._curso_info(), rep["evaluaciones"], rep["filas"])
            messagebox.showinfo("OK", "PDF exportado.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
