import os

from tkinter import messagebox

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from motor.motor_oaj import MotorOAJ

from ui.panel_documento import PanelDocumento
from ui.visor_pdf import VisorPDF
from ui.panel_campos import PanelCampos
from ui.panel_estado import PanelEstado
from ui.barra_inferior import BarraInferior


class TestadorOAJ(ttk.Window):

    def __init__(self):

        super().__init__(
            themename="flatly"
        )

        # ======================================
        # MOTOR
        # ======================================

        self.motor = MotorOAJ()

        # ======================================
        # VENTANA
        # ======================================

        self.title(
            "TESTADOR OAJ"
        )

        self.geometry(
            "1450x850"
        )

        self.minsize(
            1200,
            700
        )

        self.crear_interfaz()

    # ==========================================
    # INTERFAZ
    # ==========================================

    def crear_interfaz(self):

        self.grid_rowconfigure(
            1,
            weight=1
        )

        self.grid_columnconfigure(
            0,
            weight=1
        )

        titulo = ttk.Label(

            self,

            text="TESTADOR OAJ",

            font=(
                "Segoe UI",
                18,
                "bold"
            )

        )

        titulo.grid(

            row=0,

            column=0,

            pady=10

        )

        contenido = ttk.Frame(
            self
        )

        contenido.grid(

            row=1,

            column=0,

            sticky="nsew",

            padx=10,

            pady=5

        )

        contenido.grid_columnconfigure(
            0,
            weight=1
        )

        contenido.grid_columnconfigure(
            1,
            weight=3
        )

        contenido.grid_columnconfigure(
            2,
            weight=1
        )

        contenido.grid_rowconfigure(
            0,
            weight=1
        )

        # ======================================
        # DOCUMENTO
        # ======================================

        self.panel_documento = (
            PanelDocumento(
                contenido,
                self
            )
        )

        self.panel_documento.grid(

            row=0,

            column=0,

            sticky="nsew",

            padx=5

        )

        # ======================================
        # PDF
        # ======================================

        self.panel_pdf = VisorPDF(
            contenido
        )

        self.panel_pdf.grid(

            row=0,

            column=1,

            sticky="nsew",

            padx=5

        )

        # ======================================
        # CAMPOS
        # ======================================

        self.panel_campos = PanelCampos(
            contenido
        )

        self.panel_campos.grid(

            row=0,

            column=2,

            sticky="nsew",

            padx=5

        )

        # ======================================
        # ESTADO
        # ======================================

        self.panel_estado = PanelEstado(
            self
        )

        self.panel_estado.grid(

            row=2,

            column=0,

            sticky="ew",

            padx=10,

            pady=5

        )

        # ======================================
        # BARRA
        # ======================================

        self.barra = BarraInferior(

            self,

            self

        )

        self.barra.grid(

            row=3,

            column=0,

            sticky="ew",

            padx=10,

            pady=10

        )

    # ==========================================
    # ANALIZAR
    # ==========================================

    def analizar_documento(self):

        if not self.panel_documento.ruta_pdf:

            messagebox.showwarning(

                "TESTADOR OAJ",

                "Seleccione un documento PDF."

            )

            return

        try:

            self.panel_estado.actualizar(
                "lectura"
            )

            self.motor.cargar_pdf(

                self.panel_documento.ruta_pdf

            )

            self.panel_estado.actualizar(
                "analisis"
            )

            self.motor.analizar()

            self.panel_estado.actualizar(
                "reglas"
            )

            campos = (
                self.motor.aplicar_reglas()
            )

            self.panel_campos.mostrar_campos(
                campos
            )

            self.panel_estado.actualizar(
                "Documento analizado correctamente."
            )

        except Exception as e:

            messagebox.showerror(

                "TESTADOR OAJ",

                str(e)

            )

    # ==========================================
    # GENERAR PDF
    # ==========================================

    def generar_pdf(self):

        if not self.motor.campos:

            messagebox.showwarning(

                "TESTADOR OAJ",

                "Primero analiza el documento."

            )

            return

        try:

            self.panel_estado.actualizar(
                "pdf"
            )

            ruta = (
                self.motor.generar_pdf()
            )

            if not ruta:

                return

            messagebox.showinfo(

                "TESTADOR OAJ",

                "PDF generado correctamente."

            )

            os.startfile(ruta)

        except Exception as e:

            messagebox.showerror(

                "TESTADOR OAJ",

                str(e)

            )

        # ==========================================================
    # NUEVO DOCUMENTO
    # ==========================================================

    def nuevo_documento(self):

        # Limpiar documento seleccionado
        self.panel_documento.ruta_pdf = ""

        self.panel_documento.lbl_archivo.configure(
            text="Ningún PDF seleccionado"
        )

        # Limpiar campos detectados
        self.panel_campos.limpiar()

        # Reiniciar estado
        self.panel_estado.reiniciar()

        # Limpiar motor
        self.motor.ruta_pdf = ""
        self.motor.bloques = []
        self.motor.filas = []
        self.motor.campos = []

        # Limpiar visor
        self.panel_pdf.canvas_pdf.canvas.delete("all")

        self.panel_pdf.canvas_pdf.documento = None

        self.panel_pdf.canvas_pdf.imagenes.clear()


if __name__ == "__main__":

    app = TestadorOAJ()

    app.mainloop()