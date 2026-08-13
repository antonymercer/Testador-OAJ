import os

import pymupdf


class Redactor:

    def __init__(self):

        # ==========================================
        # CONFIGURACIÓN ORIGINAL
        # ==========================================

        self.ancho_testado = 250
        self.alto_testado = 10

        self.margen_x = 2
        self.margen_y = 2

    # ==========================================
    # GENERAR PDF
    # ==========================================

    def generar_pdf(
        self,
        ruta_pdf,
        campos
    ):

        if not ruta_pdf:
            raise ValueError(
                "No se ha proporcionado un PDF."
            )

        if not os.path.exists(ruta_pdf):
            raise FileNotFoundError(
                f"No existe el archivo:\n{ruta_pdf}"
            )

        documento = pymupdf.open(
            ruta_pdf
        )

        try:

            redactados = 0

            # ==========================================
            # RECORRER CAMPOS
            # ==========================================

            for campo in campos:

                accion = campo.get(
                    "accion",
                    "IGNORAR"
                )

                forzar = campo.get(
                    "forzar_testado",
                    False
                )

                # --------------------------------------
                # SOLO TESTAR
                # --------------------------------------

                if (
                    accion != "TESTAR"
                    and not forzar
                ):
                    continue

                # --------------------------------------
                # PÁGINA
                # --------------------------------------

                pagina_numero = campo.get(
                    "pagina"
                )

                if pagina_numero is None:
                    continue

                indice_pagina = (
                    pagina_numero - 1
                )

                if not (
                    0 <= indice_pagina < len(documento)
                ):
                    continue

                pagina = documento[
                    indice_pagina
                ]

                # --------------------------------------
                # COORDENADAS
                # --------------------------------------

                x = campo.get("x")
                y = campo.get("y")
                ancho = campo.get("ancho")
                alto = campo.get("alto")

                if None in (
                    x,
                    y,
                    ancho,
                    alto
                ):
                    continue

                if (
                    ancho <= 0
                    or alto <= 0
                ):
                    continue

                # ======================================
                # RECTÁNGULO NORMAL
                # ======================================

                ancho_necesario = max(
                    self.ancho_testado,
                    ancho + (
                        2 * self.margen_x
                    )
                )

                alto_necesario = (
                    self.alto_testado
                )

                # ======================================
                # ACLARACIONES / OBSERVACIONES
                # ======================================

                nombre_campo = str(
                    campo.get(
                        "campo",
                        ""
                    )
                ).upper()

                if (
                    "ACLARACIONES" in nombre_campo
                    or "OBSERVACIONES" in nombre_campo
                ):

                    # Sólo estas filas serán
                    # ligeramente más altas.
                    alto_necesario = 20

                # ======================================
                # CREAR RECTÁNGULO
                # ======================================

                rectangulo = pymupdf.Rect(

                    max(
                        0,
                        x - self.margen_x
                    ),

                    max(
                        0,
                        y - self.margen_y
                    ),

                    min(
                        pagina.rect.width,
                        x
                        + ancho_necesario
                        + self.margen_x
                    ),

                    min(
                        pagina.rect.height,
                        y
                        + alto_necesario
                        + self.margen_y
                    )
                )

                # ======================================
                # AGREGAR REDACCIÓN
                # ======================================

                pagina.add_redact_annot(
                    rectangulo,
                    fill=(0, 0, 0),
                    cross_out=False
                )

                redactados += 1

            # ==========================================
            # APLICAR
            # ==========================================

            for pagina in documento:

                pagina.apply_redactions()

            # ==========================================
            # VALIDAR
            # ==========================================

            if redactados == 0:

                raise ValueError(
                    "No se encontraron campos marcados "
                    "para testar."
                )

            # ==========================================
            # ARCHIVO DE SALIDA
            # ==========================================

            carpeta = os.path.dirname(
                ruta_pdf
            )

            nombre = os.path.basename(
                ruta_pdf
            )

            nombre_sin_extension = (
                os.path.splitext(
                    nombre
                )[0]
            )

            ruta_salida = os.path.join(
                carpeta,
                f"{nombre_sin_extension}_TESTADO.pdf"
            )

            # ==========================================
            # ELIMINAR ANTERIOR
            # ==========================================

            if os.path.exists(
                ruta_salida
            ):
                os.remove(
                    ruta_salida
                )

            # ==========================================
            # GUARDAR
            # ==========================================

            documento.save(
                ruta_salida,
                garbage=4,
                deflate=True
            )

            print()
            print(
                "=============================="
            )
            print(
                f"REDACCIONES APLICADAS: {redactados}"
            )
            print(
                f"ARCHIVO: {ruta_salida}"
            )
            print(
                "=============================="
            )
            print()

            return ruta_salida

        finally:

            documento.close()