import os 

BASE = os.path.dirname(os.path.abspath(__file__))
CARPETA = os.path.join(BASE, "datos")
RUTA_DATOS = os.path.join(CARPETA, "contactos.dat")
RUTA_INDICE = os.path.join(CARPETA, "indice.json")
RUTA_HASH = os.path.join(CARPETA, "contactos.sha256")
RUTA_JSON = os.path.join(CARPETA, "contactos.json")
RUTA_PDF = os.path.join(CARPETA, "reporte_contactos.pdf")

CAMPOS = [("id", 6), ("nombre", 25), ("telefono", 15), ("correo", 35), ("ciudad", 18)]
TAM_REGISTRO = sum(largo for _, largo in CAMPOS) + 1  # +1 por el "\n" final = 100, que no se te olvide baboso 

class AgendaError(Exception):
    """Error con un mensaje listo"""

def crear_carpeta():
    os.makedirs(CARPETA, exist_ok=True)

def parse_id(texto):
    texto = str(texto).strip()
    if not (texto.isascii() and texto.isdigit()) or not 1 <= int(texto) <= 999999:
        raise AgendaError("El ID debe ser un número entero entre 1 y 999999.")
    return int(texto)

def validar_contacto(datos):
    c = {"id": parse_id(datos.get("id", ""))}
    for nombre, largo in CAMPOS[1:]:
        valor = " ".join(str(datos.get(nombre, "")).split())  # sin saltos ni espacios dobles
        if len(valor.encode("utf-8")) > largo:
            raise AgendaError(f"'{nombre}' excede el máximo de {largo} bytes.")
        c[nombre] = valor
    if not c["nombre"]:
        raise AgendaError("El nombre es obligatorio.")
    if c["correo"] and "" not in c["correo"]:
        raise AgendaError("El correo no es válido.")
    return c

def empaquetar(c):
    partes = []
    for nombre, largo in CAMPOS:
        dato = str(c[nombre]).encode("utf-8")
        partes.append(dato + b" " * (largo - len(dato)))
    return b"".join(partes) + b"\n"

def desempaquetar(datos):
    # bytes de un registro -> contacto (dict)
    if len(datos) != TAM_REGISTRO or not datos.endswith(b"\n"):
        raise AgendaError("Registro dañado: tamaño o formato incorrecto.")
    c, pos = {}, 0
    try:
        for nombre, largo in CAMPOS:
            c[nombre] = datos[pos:pos + largo].decode("utf-8").rstrip()
            pos += largo
        c["id"] = int(c["id"])
    except ValueError:  # incluye UnicodeDecodeError
        raise AgendaError("Registro dañado: contenido ilegible.")
    return c