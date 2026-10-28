import hashlib
import json
import os

from registros import (RUTA_DATOS, RUTA_INDICE, RUTA_HASH, TAM_REGISTRO, AgendaError,
                       validar_contacto, empaquetar, desempaquetar, parse_id)

def tam_datos():
    return os.path.getsize(RUTA_DATOS) if os.path.exists(RUTA_DATOS) else 0

def total_registros():
    return tam_datos() // TAM_REGISTRO

# --- índice primario (id -> número de registro) ---
def leer_indice():
    try:
        with open(RUTA_INDICE, "r", encoding="utf-8") as f:
            return {int(k): int(v) for k, v in json.load(f).items()}
    except FileNotFoundError:
        if tam_datos():
            raise AgendaError("No se encontró indice.json. Use Herramientas > "
                              "Verificar integridad para reconstruirlo.")
        return {}
    except (ValueError, AttributeError, TypeError):  # JSON corrupto o con otra forma
        raise AgendaError("El índice está dañado. Use Herramientas > "
                          "Verificar integridad para reconstruirlo.")

def guardar_indice(indice):
    with open(RUTA_INDICE, "w", encoding="utf-8") as f:
        json.dump({str(k): v for k, v in sorted(indice.items())}, f, indent=2)

# --- hash de integridad ---
def calcular_hash():
    h = hashlib.sha256()
    with open(RUTA_DATOS, "rb") as f:
        for bloque in iter(lambda: f.read(65536), b""):
            h.update(bloque)
    return h.hexdigest()

def guardar_hash():
    with open(RUTA_HASH, "w", encoding="utf-8") as f:
        f.write(calcular_hash())

# --- lectura y escritura de un registro ---
def leer_registro(num):
    try:
        f = open(RUTA_DATOS, "rb")
    except FileNotFoundError:
        raise AgendaError("No existe el archivo de contactos.")
    with f:
        f.seek(num * TAM_REGISTRO)
        ini = f.tell()
        datos = f.read(TAM_REGISTRO)
        fin = f.tell()
    return desempaquetar(datos), (ini, fin)

def escribir_registro(num, c):
    modo = "r+b" if os.path.exists(RUTA_DATOS) else "w+b"
    with open(RUTA_DATOS, modo) as f:
        f.seek(num * TAM_REGISTRO)
        ini = f.tell()
        f.write(empaquetar(c))
        fin = f.tell()
    return ini, fin

def agregar(datos):
    c = validar_contacto(datos)
    indice = leer_indice()
    if c["id"] in indice:
        raise AgendaError(f"Ya existe un contacto con ID {c['id']}.")
    tam = tam_datos()
    if tam % TAM_REGISTRO:
        raise AgendaError("El archivo de contactos está dañado (tamaño inválido).")
    num = tam // TAM_REGISTRO
    pos = escribir_registro(num, c)
    indice[c["id"]] = num
    guardar_indice(indice)
    guardar_hash()
    return c, num, pos

def buscar(id_):
    pass

def modificar(datos):
    pass

def listar():
    pass