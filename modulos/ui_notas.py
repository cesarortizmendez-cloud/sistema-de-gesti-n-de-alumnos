# ============================================
# modulos/ui_notas.py
# Ventana 4: inscribir alumnos, registrar notas y calcular promedio ponderado
# + Exportar reporte del curso (Excel/PDF)
# ============================================

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from .repo_cursos import listar_cursos_detallados
from .repo_inscripciones import listar_inscritos_por_curso, inscribir_alumno, obtener_inscripcion, desinscribir
from .repo_alumnos import listar_alumnos
from .repo_notas import obtener_notas_por_inscripcion, guardar_nota, obtener_promedio_inscripcion
from .repo_evaluaciones import suma_porcentajes
from .exportaciones import exportar_promedios_curso_excel, exportar_promedios_curso_pdf


class VentanaNotas(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)

        self.title("Notas - Inscripción / Registro / Promedio Ponderado")
        self.geometry("1200x680")
        self.minsize(1120, 620)

        self.curso_sel = None
        self.inscripcion_sel = None

        # Entradas dinámicas de notas (evaluacion_id -> Entry)
        self._entries_notas = {}

        self._crear_ui()
        self._cargar_cursos()

    def _crear_ui(self):
        # Selector de curso
        top = ttk.Frame(self)
        top.pack(fill="x", padx=10, pady=10)

        ttk.Label(top, text="Curso:").pack(side="left")
        self.var_curso = tk.StringVar()
        self.cmb_curso = ttk.Combobox(top, textvariable=self.var_curso, state="readonly", width=75)
        self.cmb_curso.pack(side="left", padx=8)
        self.cmb_curso.bind("<<ComboboxSelected>>", lambda e: self.on_curso_change())

        self.lbl_suma = ttk.Label(top, text="Suma %: 0.00")
        self.lbl_suma.pack(side="left", padx=10)

        ttk.Button(top, text="Inscribir alumno", command=self.on_inscribir).pack(side="left", padx=6)
        ttk.Button(top, text="Quitar inscripción", command=self.on_desinscribir).pack(side="left", padx=6)

        ttk.Separator(top, orient="vertical").pack(side="left", fill="y", padx=10)

        ttk.Button(top, text="Exportar Excel", command=self.on_exportar_excel).pack(side="left", padx=6)
        ttk.Button(top, text="Exportar PDF", command=self.on_exportar_pdf).pack(side="left", padx=6)

        # Contenedor principal
        cont = ttk.Frame(self)
        cont.pack(fill="both", expand=True, padx=10, pady=10)
        cont.columnconfigure(0, weight=2)
        cont.columnconfigure(1, weight=3)
        cont.rowconfigure(0, weight=1)

        # Izquierda: lista inscritos
        izq = ttk.LabelFrame(cont, text="Alumnos inscritos en el curso")
        izq.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        izq.rowconfigure(0, weight=1)
        izq.columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(
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
            self.tree.heading(c, text=t)

        self.tree.column("insc", width=70, anchor="center")
        self.tree.column("rut", width=120, anchor="w")
        self.tree.column("alumno", width=220, anchor="w")
        self.tree.column("email", width=180, anchor="w")
        self.tree.column("prom", width=90, anchor="center")
        self.tree.column("sum", width=80, anchor="center")

        sb = ttk.Scrollbar(izq, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)

        self.tree.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        sb.grid(row=0, column=1, sticky="ns")

        self.tree.bind("<<TreeviewSelect>>", lambda e: self.on_select_inscrito())

        # Derecha: notas del alumno
        der = ttk.LabelFrame(cont, text="Notas del alumno seleccionado")
        der.grid(row=0, column=1, sticky="nsew")
        der.columnconfigure(0, weight=1)
        der.rowconfigure(1, weight=1)

        self.lbl_alumno = ttk.Label(der, text="Seleccione un alumno inscrito.", font=("Segoe UI", 11, "bold"))
        self.lbl_alumno.grid(row=0, column=0, sticky="w", padx=10, pady=10)

        self.frm_notas = ttk.Frame(der)
        self.frm_notas.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.frm_notas.columnconfigure(1, weight=1)

        botones = ttk.Frame(der)
        botones.grid(row=2, column=0, sticky="w", padx=10, pady=10)

        ttk.Button(botones, text="Guardar notas", command=self.on_guardar_notas).pack(side="left", padx=5)
        ttk.Button(botones, text="Recalcular promedio", command=self.on_recalcular).pack(side="left", padx=5)

        self.lbl_prom = ttk.Label(der, text="Promedio ponderado: -", font=("Segoe UI", 11))
        self.lbl_prom.grid(row=3, column=0, sticky="w", padx=10, pady=10)

    # -----------------------
    # Cursos
    # -----------------------
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

        # Suma porcentajes (color)
        s = suma_porcentajes(self.curso_sel)
        self.lbl_suma.config(text=f"Suma %: {s:.2f}", foreground=("green" if abs(s - 100) < 0.001 else "red"))

        self._refrescar_inscritos()
        self._limpiar_panel_notas()

    # -----------------------
    # Inscritos
    # -----------------------
    def _refrescar_inscritos(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        if self.curso_sel is None:
            return

        ins = listar_inscritos_por_curso(self.curso_sel)
        for r in ins:
            alumno = f"{r.get('apellidos','')} {r.get('nombres','')}".strip()
            prom = float(r.get("promedio_ponderado") or 0)
            s = float(r.get("suma_porcentajes") or 0)
            self.tree.insert(
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
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0], "values")
        if not vals:
            return

        self.inscripcion_sel = int(vals[0])
        alumno_txt = f"{vals[2]} (RUT: {vals[1]})"
        self.lbl_alumno.config(text=alumno_txt)

        self._cargar_panel_notas()

    # -----------------------
    # Panel dinámico de notas
    # -----------------------
    def _limpiar_panel_notas(self):
        for w in self.frm_notas.winfo_children():
            w.destroy()
        self._entries_notas = {}
        self.lbl_alumno.config(text="Seleccione un alumno inscrito.")
        self.lbl_prom.config(text="Promedio ponderado: -")

    def _cargar_panel_notas(self):
        self._limpiar_panel_notas()

        if self.inscripcion_sel is None:
            return

        filas = obtener_notas_por_inscripcion(self.inscripcion_sel)

        # Header
        ttk.Label(self.frm_notas, text="Evaluación", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w", pady=4)
        ttk.Label(self.frm_notas, text="Nota (0 a 7)", font=("Segoe UI", 10, "bold")).grid(row=0, column=1, sticky="w", pady=4)

        # Creamos una fila por evaluación
        r = 1
        for f in filas:
            txt = f"{f['nombre']} ({float(f['porcentaje']):.2f}%)"
            ttk.Label(self.frm_notas, text=txt).grid(row=r, column=0, sticky="w", pady=3)

            e = ttk.Entry(self.frm_notas)
            e.grid(row=r, column=1, sticky="ew", pady=3)
            e.insert(0, str(float(f.get("nota") or 0)))
            self._entries_notas[int(f["evaluacion_id"])] = e
            r += 1

        self.on_recalcular()

    # -----------------------
    # Guardar notas / promedio
    # -----------------------
    def on_guardar_notas(self):
        if self.inscripcion_sel is None:
            messagebox.showwarning("Atención", "Seleccione un alumno inscrito.")
            return

        try:
            for evaluacion_id, entry in self._entries_notas.items():
                valor = entry.get().strip()
                if valor == "":
                    valor = "0"
                guardar_nota(self.inscripcion_sel, evaluacion_id, float(valor))

            messagebox.showinfo("OK", "Notas guardadas.")
            self._refrescar_inscritos()
            self.on_recalcular()

        except Exception as e:
            messagebox.showerror("Error", str(e))

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

    # -----------------------
    # Inscribir / desinscribir
    # -----------------------
    def on_inscribir(self):
        if self.curso_sel is None:
            messagebox.showwarning("Atención", "Seleccione un curso.")
            return

        # Ventana simple de selección
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
            tree.insert("", "end", values=(a["alumno_id"], a.get("rut",""), nombre, a.get("email","") or ""))

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
        if not messagebox.askyesno("Confirmar", "¿Quitar inscripción? (Borra notas del curso por cascada)"):
            return
        try:
            desinscribir(self.inscripcion_sel)
            self.inscripcion_sel = None
            self._refrescar_inscritos()
            self._limpiar_panel_notas()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # -----------------------
    # Exportación reporte curso
    # -----------------------
    def _datos_reporte_curso(self):
        if self.curso_sel is None:
            raise ValueError("Seleccione un curso.")
        curso_info = self._curso_info()
        inscritos = listar_inscritos_por_curso(self.curso_sel)
        return curso_info, inscritos

    def on_exportar_excel(self):
        try:
            curso_info, inscritos = self._datos_reporte_curso()
            ruta = filedialog.asksaveasfilename(
                title="Guardar Excel",
                defaultextension=".xlsx",
                filetypes=[("Excel", "*.xlsx")],
                initialdir="exports",
            )
            if not ruta:
                return
            exportar_promedios_curso_excel(ruta, curso_info, inscritos)
            messagebox.showinfo("OK", "Excel exportado.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_exportar_pdf(self):
        try:
            curso_info, inscritos = self._datos_reporte_curso()
            ruta = filedialog.asksaveasfilename(
                title="Guardar PDF",
                defaultextension=".pdf",
                filetypes=[("PDF", "*.pdf")],
                initialdir="exports",
            )
            if not ruta:
                return
            exportar_promedios_curso_pdf(ruta, curso_info, inscritos)
            messagebox.showinfo("OK", "PDF exportado.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
