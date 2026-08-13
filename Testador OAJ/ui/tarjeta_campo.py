import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class TarjetaCampo(ttk.Frame):

    def __init__(self, master, campo):

        self.campo = campo

        accion = campo["accion"]

        if accion == "TESTAR":
            estilo = "danger"

        elif accion == "MOSTRAR":
            estilo = "success"

        else:
            estilo = "secondary"

        super().__init__(
            master,
            bootstyle=estilo,
            padding=8
        )

        # ==========================
        # Nombre del campo
        # ==========================

        ttk.Label(

            self,

            text=campo["campo"],

            font=("Segoe UI",10,"bold")

        ).pack(anchor=W)

        # ==========================
        # Valor
        # ==========================

        ttk.Label(

            self,

            text=campo["valor"],

            wraplength=220

        ).pack(anchor=W,pady=(2,5))

        # ==========================
        # Acción
        # ==========================

        ttk.Label(

            self,

            text=accion,

            font=("Segoe UI",8)

        ).pack(anchor=E)