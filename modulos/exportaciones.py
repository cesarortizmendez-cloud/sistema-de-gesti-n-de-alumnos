# ============================================
# modulos/exportaciones.py
# Exportación a Excel/PDF incluyendo TODAS las NOTAS
# ============================================

from typing import Any, Dict, List
from openpyxl import Workbook

from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors


def exportar_notas_curso_excel(
    ruta_xlsx: str,
    curso_info: dict,
    evaluaciones: List[Dict[str, Any]],
    filas: List[Dict[str, Any]],
) -> None:
    """
    Exporta a Excel TODAS las notas de un curso en formato "matriz":

    Columnas:
      RUT | Alumno | Email | Eval1(...) | Eval2(...) | ... | Promedio | Suma%
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "Notas"

    # Título superior
    titulo = f"Curso: {curso_info.get('curso_nombre','')} | Sem {curso_info.get('semestre','')} | " \
             f"{curso_info.get('carrera_nombre','')} | {curso_info.get('universidad_nombre','')}"
    ws.append([titulo])
    ws.append([])

    # Encabezados base
    headers = ["RUT", "Alumno", "Email"]

    # Encabezados por evaluación
    for e in evaluaciones:
        headers.append(f"{e['nombre']} ({float(e['porcentaje']):.0f}%)")

    # Columnas finales
    headers.extend(["Promedio", "Suma %"])
    ws.append(headers)

    # Filas de datos
    for f in filas:
        alumno = f"{f.get('apellidos','')} {f.get('nombres','')}".strip()
        row = [
            f.get("rut", ""),
            alumno,
            f.get("email", "") or "",
        ]

        # Notas por evaluación (en el mismo orden)
        notas = f.get("notas", {})
        for e in evaluaciones:
            row.append(float(notas.get(int(e["evaluacion_id"]), 0)))

        # Promedio y suma %
        row.append(float(f.get("promedio_ponderado") or 0))
        row.append(float(f.get("suma_porcentajes") or 0))

        ws.append(row)

    wb.save(ruta_xlsx)


def exportar_notas_curso_pdf(
    ruta_pdf: str,
    curso_info: dict,
    evaluaciones: List[Dict[str, Any]],
    filas: List[Dict[str, Any]],
) -> None:
    """
    Exporta a PDF TODAS las notas.
    Se usa A4 horizontal (landscape) para soportar más columnas.
    """
    doc = SimpleDocTemplate(ruta_pdf, pagesize=landscape(A4))
    styles = getSampleStyleSheet()

    elementos = []
    elementos.append(Paragraph("Reporte de Notas (Curso)", styles["Title"]))
    elementos.append(Spacer(1, 10))

    # Texto de curso
    curso_txt = f"Curso: {curso_info.get('curso_nombre','')} | Semestre: {curso_info.get('semestre','')}<br/>" \
                f"Carrera: {curso_info.get('carrera_nombre','')} | Universidad: {curso_info.get('universidad_nombre','')}"
    elementos.append(Paragraph(curso_txt, styles["Normal"]))
    elementos.append(Spacer(1, 12))

    # Encabezado tabla
    encabezado = ["RUT", "Alumno"]
    for e in evaluaciones:
        encabezado.append(f"{e['nombre']} ({float(e['porcentaje']):.0f}%)")
    encabezado.extend(["Prom", "Suma%"])

    data = [encabezado]

    # Filas
    for f in filas:
        alumno = f"{f.get('apellidos','')} {f.get('nombres','')}".strip()
        row = [str(f.get("rut", "")), alumno]

        notas = f.get("notas", {})
        for e in evaluaciones:
            row.append(f"{float(notas.get(int(e['evaluacion_id']), 0)):.2f}")

        row.append(f"{float(f.get('promedio_ponderado') or 0):.2f}")
        row.append(f"{float(f.get('suma_porcentajes') or 0):.2f}")

        data.append(row)

    tabla = Table(data, repeatRows=1)

    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))

    elementos.append(tabla)
    doc.build(elementos)
