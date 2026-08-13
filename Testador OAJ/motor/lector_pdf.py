import pymupdf


class LectorPDF:

    def leer_pdf(self, ruta_pdf):

        documento = pymupdf.open(
            ruta_pdf
        )

        palabras = []

        # ==========================================
        # RECORRER PÁGINAS
        # ==========================================

        for numero_pagina in range(
            len(documento)
        ):

            pagina = documento.load_page(
                numero_pagina
            )

            # ======================================
            # OBTENER PALABRAS INDIVIDUALES
            # ======================================

            datos = pagina.get_text(
                "words"
            )

            for palabra in datos:

                palabras.append({

                    "texto": palabra[4].strip(),

                    "pagina":
                        numero_pagina + 1,

                    "x0": palabra[0],

                    "y0": palabra[1],

                    "x1": palabra[2],

                    "y1": palabra[3],

                    "ancho":
                        palabra[2] - palabra[0],

                    "alto":
                        palabra[3] - palabra[1]

                })

        documento.close()

        return palabras