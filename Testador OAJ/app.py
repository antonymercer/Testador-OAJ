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

        self.panel_documento = PanelDocumento(
            contenido,
            self
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

        # ======================================
        # VALIDAR PDF
        # ======================================

        if not self.panel_documento.ruta_pdf:

            messagebox.showwarning(
                "TESTADOR OAJ",
                "Seleccione un documento PDF."
            )

            return

        try:

            # ==================================
            # LECTURA
            # ==================================

            self.panel_estado.actualizar(
                "lectura"
            )

            self.motor.cargar_pdf(
                self.panel_documento.ruta_pdf
            )

            # ==================================
            # ANÁLISIS
            # ==================================

            self.panel_estado.actualizar(
                "analisis"
            )

            campos = self.motor.analizar()

            # ==================================
            # VALIDAR RESULTADO
            # ==================================

            if campos is None:
                campos = []

            # ==================================
            # REGLAS
            # ==================================

            self.panel_estado.actualizar(
                "reglas"
            )

            campos = self.motor.aplicar_reglas()

            # ==================================
            # MOSTRAR CAMPOS
            # ==================================

            self.panel_campos.mostrar_campos(
                campos
            )

            # ==================================
            # FINAL
            # ==================================

            print()
            print("==============================")
            print("ANÁLISIS COMPLETADO")
            print("==============================")
            print(
                f"Campos detectados: {len(campos)}"
            )
            print("==============================")
            print()

        except Exception as e:

            messagebox.showerror(
                "TESTADOR OAJ",
                str(e)
            )

    # ==========================================
    # GENERAR PDF
    # ==========================================

    def generar_pdf(self):

        # ======================================
        # VALIDAR ANÁLISIS
        # ======================================

        if not getattr(
            self.motor,
            "analisis_realizado",
            False
        ):

            messagebox.showwarning(
                "TESTADOR OAJ",
                "Primero analiza el documento."
            )

            return

        # ======================================
        # VALIDAR REGLAS
        # ======================================

        if not getattr(
            self.motor,
            "reglas_aplicadas",
            False
        ):

            messagebox.showwarning(
                "TESTADOR OAJ",
                "Primero aplica las reglas al documento."
            )

            return

        try:

            # ==================================
            # GENERACIÓN
            # ==================================

            self.panel_estado.actualizar(
                "pdf"
            )

            ruta = self.motor.generar_pdf()

            if not ruta:
                return

            messagebox.showinfo(
                "TESTADOR OAJ",
                "PDF generado correctamente."
            )

            os.startfile(
                ruta
            )

        except Exception as e:

            messagebox.showerror(
                "TESTADOR OAJ",
                str(e)
            )

    # ==========================================
    # NUEVO DOCUMENTO
    # ==========================================

    def nuevo_documento(self):

        # ======================================
        # LIMPIAR DOCUMENTO
        # ======================================

        self.panel_documento.ruta_pdf = ""

        self.panel_documento.lbl_archivo.configure(
            text="Ningún PDF seleccionado"
        )

        # ======================================
        # LIMPIAR CAMPOS
        # ======================================

        self.panel_campos.limpiar()

        # ======================================
        # REINICIAR ESTADO
        # ======================================

        self.panel_estado.reiniciar()

        # ======================================
        # REINICIAR MOTOR
        # ======================================

        if hasattr(
            self.motor,
            "reiniciar"
        ):

            self.motor.reiniciar()

        else:

            self.motor.ruta_pdf = ""
            self.motor.bloques = []
            self.motor.filas = []
            self.motor.campos = []

            if hasattr(
                self.motor,
                "campos_testar"
            ):
                self.motor.campos_testar = []

            if hasattr(
                self.motor,
                "documento_cargado"
            ):
                self.motor.documento_cargado = False

            if hasattr(
                self.motor,
                "analisis_realizado"
            ):
                self.motor.analisis_realizado = False

            if hasattr(
                self.motor,
                "reglas_aplicadas"
            ):
                self.motor.reglas_aplicadas = False

        # ======================================
        # LIMPIAR VISOR PDF
        # ======================================

        self.panel_pdf.canvas_pdf.canvas.delete(
            "all"
        )

        self.panel_pdf.canvas_pdf.documento = None

        self.panel_pdf.canvas_pdf.imagenes.clear()


if __name__ == "__main__":

    app = TestadorOAJ()

    app.mainloop()