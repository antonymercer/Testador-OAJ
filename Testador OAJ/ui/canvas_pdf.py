import ttkbootstrap as ttk
from ttkbootstrap.constants import *

import pymupdf
from PIL import Image
from PIL import ImageTk


class CanvasPDF(ttk.Frame):

    def __init__(self, master):

        super().__init__(master)

        self.documento = None
        self.zoom = 1.50
        self.imagenes = []

        # ===============================
        # Canvas
        # ===============================

        self.canvas = ttk.Canvas(
            self,
            background="white",
            highlightthickness=0
        )

        self.scroll_y = ttk.Scrollbar(
            self,
            orient=VERTICAL,
            command=self.canvas.yview
        )

        self.canvas.configure(
            yscrollcommand=self.scroll_y.set
        )

        self.canvas.pack(
            side=LEFT,
            fill=BOTH,
            expand=True
        )

        self.scroll_y.pack(
            side=RIGHT,
            fill=Y
        )

        # ===============================
        # Eventos
        # ===============================

        self.canvas.bind("<MouseWheel>", self.mousewheel_windows)

        self.canvas.bind("<Button-4>", self.mousewheel_linux)

        self.canvas.bind("<Button-5>", self.mousewheel_linux)

    # ==========================================
    # Cargar PDF
    # ==========================================

    def cargar_pdf(self, ruta_pdf):

        self.documento = pymupdf.open(ruta_pdf)

        self.redibujar()

    # ==========================================
    # Dibujar
    # ==========================================

    def redibujar(self):

        if self.documento is None:
            return

        self.canvas.delete("all")

        self.imagenes.clear()

        y = 20

        for pagina in self.documento:

            pix = pagina.get_pixmap(
                matrix=pymupdf.Matrix(
                    self.zoom,
                    self.zoom
                )
            )

            modo = "RGBA" if pix.alpha else "RGB"

            imagen = Image.frombytes(
                modo,
                (pix.width, pix.height),
                pix.samples
            )

            foto = ImageTk.PhotoImage(imagen)

            self.imagenes.append(foto)

            self.canvas.create_image(
                20,
                y,
                image=foto,
                anchor="nw"
            )

            y += pix.height + 30

        self.canvas.update_idletasks()

        self.canvas.configure(
            scrollregion=self.canvas.bbox("all")
        )

    # ==========================================
    # Mouse
    # ==========================================

    def mousewheel_windows(self, event):

        # CTRL = Zoom

        if event.state & 0x0004:

            if event.delta > 0:
                self.zoom_mas()
            else:
                self.zoom_menos()

            return

        # Scroll

        self.canvas.yview_scroll(
            int(-event.delta / 120),
            "units"
        )

    def mousewheel_linux(self, event):

        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")

        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")

    # ==========================================
    # Zoom
    # ==========================================

    def zoom_mas(self):

        if self.zoom >= 3:
            return

        self.zoom += 0.15

        self.redibujar()

        self.master.actualizar_zoom()

    def zoom_menos(self):

        if self.zoom <= 0.50:
            return

        self.zoom -= 0.15

        self.redibujar()

        self.master.actualizar_zoom()