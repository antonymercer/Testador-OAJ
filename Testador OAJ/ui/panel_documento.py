import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from tkinter import filedialog


class PanelDocumento(ttk.Labelframe):

    def __init__(self, master, app):

        super().__init__(
            master,
            text="Documento",
            padding=15
        )

        self.app = app

        self.ruta_pdf = ""

        self.lbl_archivo = ttk.Label(
            self,
            text="Ningún PDF seleccionado",
            font=("Segoe UI", 11),
            anchor="center"
        )

        self.lbl_archivo.pack(
            pady=20,
            fill=X
        )

        ttk.Button(
            self,
            text="Examinar",
            bootstyle="primary",
            command=self.abrir_pdf
        ).pack(fill=X)

    # =====================================================

    def abrir_pdf(self):

        ruta = filedialog.askopenfilename(
            filetypes=[
                ("PDF", "*.pdf")
            ]
        )

        if not ruta:
            return

        self.ruta_pdf = ruta

        self.lbl_archivo.configure(
            text=ruta.split("/")[-1]
        )

        self.app.panel_pdf.mostrar_pdf(ruta)

        self.app.panel_estado.reiniciar()

        self.app.panel_estado.actualizar(
            "documento"
        )