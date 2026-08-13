import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class BarraInferior(ttk.Frame):

    def __init__(self, master, app):

        super().__init__(master)

        self.app = app

        ttk.Button(
            self,
            text="Analizar",
            bootstyle="success",
            command=self.app.analizar_documento
        ).pack(side=LEFT, padx=5)

        ttk.Button(
            self,
            text="Generar PDF",
            bootstyle="primary",
            command=self.app.generar_pdf
        ).pack(side=LEFT, padx=5)

        ttk.Button(
            self,
            text="Nuevo documento",
            bootstyle="secondary",
            command=self.app.nuevo_documento
        ).pack(side=LEFT, padx=5)