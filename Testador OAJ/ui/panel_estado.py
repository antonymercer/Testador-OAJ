import ttkbootstrap as ttk


class PanelEstado(ttk.Labelframe):

    def __init__(self, master):

        super().__init__(
            master,
            text="Estado",
            padding=10
        )

        self.lbl_documento = ttk.Label(
            self,
            text="⚪ Esperando documento"
        )
        self.lbl_documento.pack(anchor="w")

        self.lbl_lectura = ttk.Label(
            self,
            text="⚪ Leyendo PDF"
        )
        self.lbl_lectura.pack(anchor="w")

        self.lbl_analisis = ttk.Label(
            self,
            text="⚪ Detectando campos"
        )
        self.lbl_analisis.pack(anchor="w")

        self.lbl_reglas = ttk.Label(
            self,
            text="⚪ Aplicando reglas"
        )
        self.lbl_reglas.pack(anchor="w")

        self.lbl_pdf = ttk.Label(
            self,
            text="⚪ Generando PDF"
        )
        self.lbl_pdf.pack(anchor="w")

    # ==========================================
    # Actualizar una etapa
    # ==========================================

    def actualizar(self, etapa):

        estados = {
            "documento": self.lbl_documento,
            "lectura": self.lbl_lectura,
            "analisis": self.lbl_analisis,
            "reglas": self.lbl_reglas,
            "pdf": self.lbl_pdf
        }

        if etapa in estados:

            texto = estados[etapa].cget("text")

            estados[etapa].configure(
                text=texto.replace("⚪", "🟢")
            )

    # ==========================================
    # Reiniciar
    # ==========================================

    def reiniciar(self):

        self.lbl_documento.configure(text="⚪ Esperando documento")
        self.lbl_lectura.configure(text="⚪ Leyendo PDF")
        self.lbl_analisis.configure(text="⚪ Detectando campos")
        self.lbl_reglas.configure(text="⚪ Aplicando reglas")
        self.lbl_pdf.configure(text="⚪ Generando PDF")