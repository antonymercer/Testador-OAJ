import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from ui.canvas_pdf import CanvasPDF


class VisorPDF(ttk.Labelframe):

    def __init__(self, master):

        super().__init__(

            master,

            text="Vista previa",

            padding=5

        )

        # ======================================
        # Barra superior
        # ======================================

        barra = ttk.Frame(self)

        barra.pack(
            fill=X,
            pady=(0,5)
        )

        ttk.Button(

            barra,

            text="-",

            width=3,

            command=self.zoom_menos

        ).pack(side=LEFT)

        self.lbl_zoom = ttk.Label(

            barra,

            text="150%",

            width=8,

            anchor="center"

        )

        self.lbl_zoom.pack(side=LEFT)

        ttk.Button(

            barra,

            text="+",

            width=3,

            command=self.zoom_mas

        ).pack(side=LEFT)

        # ======================================

        self.canvas_pdf = CanvasPDF(self)

        self.canvas_pdf.pack(

            fill=BOTH,

            expand=True

        )

    # ======================================

    def mostrar_pdf(self, ruta_pdf):

        self.canvas_pdf.cargar_pdf(ruta_pdf)

        self.actualizar_zoom()

    # ======================================

    def zoom_mas(self):

        self.canvas_pdf.zoom_mas()

    def zoom_menos(self):

        self.canvas_pdf.zoom_menos()

    # ======================================

    def actualizar_zoom(self):

        self.lbl_zoom.configure(

            text=f"{int(self.canvas_pdf.zoom*100)}%"

        )