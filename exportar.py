import json
from datetime import datetime

from agenda import listar
from registros import RUTA_JSON, RUTA_PDF, AgendaError

def exportar_json():
    contactos = listar()
    with open(RUTA_JSON, "w", encoding="utf-8") as f:
        json.dump(contactos, f, ensure_ascii=False, indent=2)
    return len(contactos)

def exportar_pdf():
    try:
        from fpdf import FPDF
    except ImportError:
        raise AgendaError("Falta la librería fpdf2. Instálela con:  pip install fpdf2")
    exportar_json()
    with open(RUTA_JSON, "r", encoding="utf-8") as f:
        contactos = json.load(f)
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    anchos = {"id": 12, "nombre": 48, "telefono": 26, "correo": 70, "ciudad": 34}

    def latin1(texto):  # la fuente base de PDF solo admite latin-1
        return str(texto).encode("latin-1", "replace").decode("latin-1")

    class Reporte(FPDF):
        def header(self):  # se repite en cada página
            self.set_font("Helvetica", "B", 14)
            self.cell(0, 8, "Agenda de contactos", new_x="LMARGIN", new_y="NEXT")
            self.set_font("Helvetica", "", 9)
            self.cell(0, 6, f"Generado: {fecha}", new_x="LMARGIN", new_y="NEXT")
            self.ln(2)
            self.set_font("Helvetica", "B", 9)
            for campo, ancho in anchos.items():
                self.cell(ancho, 7, campo.capitalize(), border=1)
            self.ln(7)

    pdf = Reporte(format="A4")
    pdf.add_page()
    pdf.set_font("Helvetica", "", 9)
    for c in contactos:
        for campo, ancho in anchos.items():
            pdf.cell(ancho, 7, latin1(c.get(campo, "")), border=1)
        pdf.ln(7)
    pdf.ln(3)
    pdf.cell(0, 6, f"Total de contactos: {len(contactos)}")
    pdf.output(RUTA_PDF)
    return len(contactos)