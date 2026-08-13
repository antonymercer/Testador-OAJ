import pymupdf
import os


class Redactor:

    def __init__(self):

        # =====================================================
        # CONFIGURACIÓN DEL TESTADO
        # =====================================================

        # Altura uniforme de todos los testados
        self.alto_testado = 8

        # Márgenes pequeños
        self.margen_x = 1
        self.margen_y = 1


    # =====================================================
    # GENERAR PDF TESTADO
    # =====================================================

    def generar_pdf(self, ruta_pdf, campos):

        if not ruta_pdf:
            raise ValueError(
                "No se ha proporcionado un PDF."
            )

        if not os.path.exists(ruta_pdf):
            raise FileNotFoundError(
                f"No existe el archivo: {ruta_pdf}"
            )


        documento = pymupdf.open(ruta_pdf)


        try:

            # =================================================
            # 1. OBTENER CAMPOS QUE SE TESTAN
            # =================================================

            campos_testar = []

            for campo in campos:

                accion = campo.get(
                    "accion",
                    "REVISAR"
                )

                if accion != "TESTAR":
                    continue


                ancho = campo.get(
                    "ancho"
                )

                if ancho is None:
                    continue

                if ancho <= 0:
                    continue


                campos_testar.append(
                    campo
                )


            # =================================================
            # 2. SI NO HAY CAMPOS
            # =================================================

            if not campos_testar:

                print(
                    "No hay campos para testar."
                )

                return None


            # =================================================
            # 3. ANCHO UNIFORME POR SECCIÓN
            # =================================================

            anchos_por_seccion = {}


            for campo in campos_testar:

                seccion = campo.get(
                    "seccion",
                    "SIN SECCION"
                )

                ancho = campo["ancho"]


                if seccion not in anchos_por_seccion:

                    anchos_por_seccion[
                        seccion
                    ] = ancho

                else:

                    if ancho > anchos_por_seccion[
                        seccion
                    ]:

                        anchos_por_seccion[
                            seccion
                        ] = ancho


            # =================================================
            # MOSTRAR CONFIGURACIÓN
            # =================================================

            print()
            print(
                "=============================="
            )

            print(
                "ANCHOS UNIFORMES POR SECCIÓN"
            )

            print(
                "=============================="
            )


            for seccion, ancho in (
                anchos_por_seccion.items()
            ):

                print(
                    f"{seccion} -> "
                    f"{ancho}"
                )


            print(
                "=============================="
            )


            # =================================================
            # 4. RECORRER CAMPOS
            # =================================================

            for campo in campos_testar:

                pagina_num = campo.get(
                    "pagina"
                )

                x = campo.get(
                    "x"
                )

                y = campo.get(
                    "y"
                )


                if pagina_num is None:
                    continue

                if x is None or y is None:
                    continue


                # =============================================
                # PÁGINA
                # =============================================

                indice_pagina = (
                    pagina_num - 1
                )


                if (
                    indice_pagina < 0
                    or indice_pagina >= len(documento)
                ):

                    continue


                pagina = documento[
                    indice_pagina
                ]


                # =============================================
                # ANCHO DE LA SECCIÓN
                # =============================================

                seccion = campo.get(
                    "seccion",
                    "SIN SECCION"
                )


                ancho_uniforme = (
                    anchos_por_seccion[
                        seccion
                    ]
                )


                # =============================================
                # RECTÁNGULO
                # =============================================

                x0 = max(
                    0,
                    x - self.margen_x
                )


                y0 = max(
                    0,
                    y - self.margen_y
                )


                x1 = min(
                    pagina.rect.width,
                    x
                    + ancho_uniforme
                    + self.margen_x
                )


                y1 = min(
                    pagina.rect.height,
                    y
                    + self.alto_testado
                    + self.margen_y
                )


                # =============================================
                # VALIDAR RECTÁNGULO
                # =============================================

                if x1 <= x0:
                    continue

                if y1 <= y0:
                    continue


                rect = pymupdf.Rect(
                    x0,
                    y0,
                    x1,
                    y1
                )


                # =============================================
                # DIBUJAR TESTADO
                # =============================================

                pagina.draw_rect(

                    rect,

                    color=(0, 0, 0),

                    fill=(0, 0, 0),

                    overlay=True

                )


                print(
                    f"{seccion} | "
                    f"{campo.get('campo', '')} | "
                    f"TESTADO"
                )


            # =================================================
            # 5. NOMBRE DEL ARCHIVO
            # =================================================

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

                nombre_sin_extension
                + "_TESTADO.pdf"

            )


            # =================================================
            # 6. GUARDAR
            # =================================================

            documento.save(

                ruta_salida,

                garbage=4,

                deflate=True

            )


            print()
            print(
                f"PDF generado: {ruta_salida}"
            )


            return ruta_salida


        finally:

            documento.close() 