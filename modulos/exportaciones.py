# ============================================
# modulos/exportaciones.py
# Exportación a Excel/PDF (reporte de promedios por curso)
# ============================================

from typing import Any, Dict, List
from openpyxl import Workbook

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors


def exportar_promedios_curso_excel(ruta_xlsx: str, curso_info: dict, filas: List[Dict[str, Any]]) -> None:
    """
    Exporta un reporte simple:
      - Alumno (RUT, Nombre)
      - Promedio ponderado
      - Suma porcentajes
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "Promedios"

    titulo = f"Curso: {curso_info.get('curso_nombre','')} (Sem {curso_info.get('semestre','')})"
    ws.append([titulo])
    ws.append([])

    headers = ["RUT", "Alumno", "Email", "Promedio ponderado", "Suma %"]
    ws.append(headers)

    for f in filas:
        alumno = f"{f.get('apellidos','')} {f.get('nombres','')}".strip()
        ws.append([
            f.get("rut", ""),
            alumno,
            f.get("email", "") or "",
            float(f.get("promedio_ponderado") or 0),
            float(f.get("suma_porcentajes") or 0),
        ])

    wb.save(ruta_xlsx)


def exportar_promedios_curso_pdf(ruta_pdf: str, curso_info: dict, filas: List[Dict[str, Any]]) -> None:
    """
    Exporta PDF en tabla.
    """
    doc = SimpleDocTemplate(ruta_pdf, pagesize=A4)
    styles = getSampleStyleSheet()

    elementos = []
    elementos.append(Paragraph("Reporte de Promedios Ponderados", styles["Title"]))
    elementos.append(Spacer(1, 10))

    curso_txt = f"Curso: {curso_info.get('curso_nombre','')} | Semestre: {curso_info.get('semestre','')}<br/>" \
                f"Carrera: {curso_info.get('carrera_nombre','')} | Universidad: {curso_info.get('universidad_nombre','')}"
    elementos.append(Paragraph(curso_txt, styles["Normal"]))
    elementos.append(Spacer(1, 12))

    data = [["RUT", "Alumno", "Promedio", "Suma %"]]
    for f in filas:
        alumno = f"{f.get('apellidos','')} {f.get('nombres','')}".strip()
        data.append([
            str(f.get("rut", "")),
            alumno,
            f"{float(f.get('promedio_ponderado') or 0):.2f}",
            f"{float(f.get('suma_porcentajes') or 0):.2f}",
        ])

    tabla = Table(data, repeatRows=1)
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))

    elementos.append(tabla)
    doc.build(elementos)
