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
    pass

def problema_hash():
    pass

def revisar():
    pass