import functools
import os
import tkinter as tk
from datetime import datetime
from tkinter import messagebox


class Dialogo(tk.Toplevel):
    def __init__(self, app, modo):  # modo: "agregar", "buscar" o "modificar"
        super().__init__(app)
        self.app, self.modo, self.id_cargado = app, modo, None


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Agenda")
        self.geometry("560x220")
        self.texto = tk.Text(self, state="disabled")
        self.texto.pack(fill="both", expand=True)
        menus = {
            "Contactos": [("Agregar", lambda: Dialogo(self, "agregar")),
                          ("Buscar por ID", lambda: Dialogo(self, "buscar")),
                          ("Modificar", lambda: Dialogo(self, "modificar")),
                          ("Salir", self.destroy)],
            "Exportar": [("A JSON", self.exportar_json), ("Reporte PDF", self.exportar_pdf)],
            "Herramientas": [("Verificar integridad", self.verificar),
                             ("Respaldo ZIP", self.respaldo),
                             ("Información del archivo", self.informacion)],
            "Ayuda": [("Acerca de", lambda: messagebox.showinfo("Ayuda", "Opción simulada."))],
        }
        barra = tk.Menu(self)
        for titulo, opciones in menus.items():
            menu = tk.Menu(barra, tearoff=0)
            for etiqueta, comando in opciones:
                menu.add_command(label=etiqueta, command=comando)
            barra.add_cascade(label=titulo, menu=menu)
        self.config(menu=barra)
        self.after(100, self.revisar_al_iniciar)

    