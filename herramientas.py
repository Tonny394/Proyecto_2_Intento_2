import os
import zipfile
from datetime import datetime

from agenda import calcular_hash, leer_indice, guardar_indice, tam_datos
from registros import (CARPETA, RUTA_DATOS, RUTA_INDICE, RUTA_HASH, TAM_REGISTRO,
                       AgendaError, desempaquetar)

def info(): #Tamaño y hora de la ultima modificación del archivo
    try:
        st = os.stat(RUTA_DATOS)
    except FileNotFoundError:
        raise AgendaError("Todavía no existe el archivo de contactos.")
    return {
        "ruta": RUTA_DATOS,
        "tamaño": st.st_size,
        "registros": st.st_size // TAM_REGISTRO,
        "modificado": datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
        "lectura": os.access(RUTA_DATOS, os.R_OK),
        "escritura": os.access(RUTA_DATOS, os.W_OK),
    }

def respaldar():
    if not os.path.exists(RUTA_DATOS):
        raise AgendaError("Todavía no hay archivo de contactos para respaldar.")
    archivos = [RUTA_DATOS]
    if os.path.exists(RUTA_INDICE):
        archivos.append(RUTA_INDICE)
    ruta_zip = os.path.join(CARPETA, datetime.now().strftime("respaldo_%Y%m%d_%H%M%S.zip"))
    with zipfile.ZipFile(ruta_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for ruta in archivos:
            z.write(ruta, arcname=os.path.basename(ruta))
    original = sum(os.path.getsize(r) for r in archivos)
    return ruta_zip, original, os.path.getsize(ruta_zip)

def problema_hash():
    if not os.path.exists(RUTA_DATOS):
        return None
    try:
        with open(RUTA_HASH, "r", encoding="utf-8") as f:
            guardado = f.read().strip()
    except FileNotFoundError:
        return "No existe contactos.sha256: no se puede comprobar la integridad."
    except UnicodeDecodeError:
        guardado = ""
    if guardado != calcular_hash():
        return ("El hash SHA-256 no coincide: el archivo de contactos fue modificado "
                "fuera de la aplicación.")
    return None

def revisar():
    problemas, real = [], {}
    tam = tam_datos()
    if tam % TAM_REGISTRO:
        problemas.append(f"El tamaño del archivo ({tam} bytes) no es múltiplo de {TAM_REGISTRO}.")
    if tam:
        with open(RUTA_DATOS, "rb") as f:
            for num in range(tam // TAM_REGISTRO):
                try:
                    c = desempaquetar(f.read(TAM_REGISTRO))
                except AgendaError:
                    problemas.append(f"El registro #{num} está dañado.")
                    continue
                if c["id"] in real:
                    problemas.append(f"ID {c['id']} duplicado (registros #{real[c['id']]} y #{num}).")
                else:
                    real[c["id"]] = num
    try:
        indice = leer_indice()
    except AgendaError:
        indice = None
    if indice != real:
        problemas.append("El índice no existía, estaba dañado o no coincidía con el archivo: "
                         "fue reconstruido.")
        guardar_indice(real)
    texto_hash = problema_hash()
    if texto_hash:
        problemas.append(texto_hash)
    return problemas