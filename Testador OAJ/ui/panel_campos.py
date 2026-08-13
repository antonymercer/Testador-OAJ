import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from ui.tarjeta_campo import TarjetaCampo


class PanelCampos(ttk.Labelframe):

    def __init__(self, master):

        super().__init__(
            master,
            text="Campos detectados",
            padding=10
        )

        self.contenedor = ttk.Frame(self)

        self.contenedor.pack(
            fill=BOTH,
            expand=True
        )

        ttk.Label(
            self.contenedor,
            text="Esperando análisis..."
        ).pack(
            anchor="center",
            pady=20
        )

    # ==========================================
    # Mostrar resultados
    # ==========================================

    def mostrar_campos(self, campos):

        # Limpiar panel

        self.limpiar()

        # No hubo resultados

        if not campos:

            ttk.Label(
                self.contenedor,
                text="No se encontraron campos."
            ).pack(
                anchor="center",
                pady=20
            )

            return

        # Crear una tarjeta por cada campo

        for campo in campos:

            tarjeta = TarjetaCampo(
                self.contenedor,
                campo
            )

            tarjeta.pack(
                fill=X,
                padx=4,
                pady=4
            )

    # ==========================================
    # Limpiar panel
    # ==========================================

    def limpiar(self):

        for widget in self.contenedor.winfo_children():

            widget.destroy()

        ttk.Label(
            self.contenedor,
            text="Esperando análisis..."
        ).pack(
            anchor="center",
            pady=20
        )