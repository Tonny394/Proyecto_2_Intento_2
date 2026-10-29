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
    pass