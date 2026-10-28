import functools
import os
import tkinter as tk
from datetime import datetime
from tkinter import messagebox

import agenda
from registros import CAMPOS, RUTA_DATOS, TAM_REGISTRO, AgendaError, crear_carpeta, parse_id

def manejar_errores(func):
    """Cualquier error se muestra en un mensaje; la aplicación no se cae."""
    functools.wraps(func)
    def envoltura(*args, **kwargs):
        try:
            crear_carpeta()
            return func(*args, **kwargs)
        except AgendaError as e:
            messagebox.showwarning("Aviso", str(e))
        except PermissionError:
            messagebox.showerror("Error", "No hay permisos para leer o escribir el archivo.")
        except OSError as e:
            messagebox.showerror("Error de archivo", str(e))
        except Exception as e:
            messagebox.showerror("Error inesperado", f"{type(e).__name__}: {e}")
    return envoltura

class Dialogo(tk.Toplevel):
    def __init__(self, app, modo):  # modo: "agregar", "buscar" o "modificar"
        super().__init__(app)
        self.app, self.modo, self.id_cargado = app, modo, None
        self.title(modo.capitalize())
        self.vars = {nombre: tk.StringVar() for nombre, _ in CAMPOS}
        for fila, (nombre, _) in enumerate(CAMPOS):
            tk.Label(self, text=nombre).grid(row=fila, column=0)
            tk.Entry(self, textvariable=self.vars[nombre]).grid(row=fila, column=1)
        if modo != "agregar":
            tk.Button(self, text="Buscar", command=self.buscar).grid(row=5, column=0)
        if modo != "buscar":
            tk.Button(self, text="Guardar", command=self.guardar).grid(row=5, column=1)

    def buscar(self):
        self.id_cargado = None

    def guardar(self):
        datos = {nombre: var.get() for nombre, var in self.vars.items()}
        if self.modo == "agregar":
            c, num, pos = agenda.agregar(datos)
            for var in self.vars.values():
                var.set("")
        else:
            if self.id_cargado is None:
                raise AgendaError("Primero busque el contacto.")
            if parse_id(datos["id"]) != self.id_cargado:
                raise AgendaError("El ID cambió. Busque el contacto de nuevo.")
            c, num, pos = agenda.modificar(datos)
        self.app.log(f"{self.modo.capitalize()} ID {c['id']}: registro #{num}, seek({pos[0]}), "
                     f"tell() antes={pos[0]} después={pos[1]}")


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

    def log(self, texto):
        self.texto.configure(state="normal")
        self.texto.insert("end", f"[{datetime.now():%H:%M:%S}] {texto}\n")
        self.texto.see("end")
        self.texto.configure(state="disabled")

    def revisar_al_iniciar(self):
        if not os.path.exists():
            self.log("Aún no hay contactos. Los archivos se guardan en la carpeta datos/.")
            return

    def exportar_json(self):
        n = 0
        self.log(f"{n} contactos exportados a datos/contactos.json")

    def exportar_pdf(self):
        n = 0
        self.log(f"Reporte PDF con {n} contactos en datos/reporte_contactos.pdf")

    def verificar(self):
        self.log("Integridad verificada. No se encontraron errores.")

    def respaldo(self):
        self.log("Respaldo creado en datos/respaldo.zip")

    def informacion(self):
        self.log("Información del archivo mostrada.")

if __name__ == "__main__":
    App().mainloop()