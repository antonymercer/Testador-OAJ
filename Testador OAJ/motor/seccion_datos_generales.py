"""
SECCIÓN DATOS GENERALES
"""

from motor.seccion import Seccion


class SeccionDatosGenerales(Seccion):

    TITULO = "Datos Generales"

    FIN = "Domicilio del declarante"

    def __init__(self):

        self.campos = [

            "Nombre(s)",
            "Primer apellido",
            "Segundo apellido",
            "CURP",
            "RFC",
            "Homoclave",
            "Correo electrónico institucional",
            "Correo electrónico personal",
            "Número celular"

        ]

    # =====================================================
    # ANALIZAR SECCIÓN
    # =====================================================

    def analizar(self, filas):

        encontrados = []

        # ---------------------------------------------
        # Obtener únicamente filas de Datos Generales
        # ---------------------------------------------

        filas = self.obtener_bloques(filas)

        print("\n==============================")
        print("ANALIZANDO DATOS GENERALES")
        print("==============================")

        for fila in filas:

            descripcion = fila.get(
                "descripcion",
                ""
            ).strip()

            contenido = fila.get(
                "contenido",
                ""
            ).strip()

            print(
                f"DESCRIPCION: {descripcion}"
            )

            print(
                f"CONTENIDO: {contenido}"
            )

            # -----------------------------------------
            # Buscar campo
            # -----------------------------------------

            for campo in self.campos:

                if self.coincide_etiqueta(
                    descripcion,
                    campo
                ):

                    print(
                        f"ENCONTRADO: {campo}"
                    )

                    # ---------------------------------
                    # Coordenadas del CONTENIDO
                    # ---------------------------------

                    if (
                        "contenido_x0" in fila
                        and "contenido_y0" in fila
                        and "contenido_x1" in fila
                        and "contenido_y1" in fila
                    ):

                        x = fila["contenido_x0"]

                        y = fila["contenido_y0"]

                        ancho = (
                            fila["contenido_x1"]
                            - fila["contenido_x0"]
                        )

                        alto = (
                            fila["contenido_y1"]
                            - fila["contenido_y0"]
                        )

                    # ---------------------------------
                    # Si no existe contenido
                    # ---------------------------------

                    else:

                        x = fila.get(
                            "descripcion_x0",
                            0
                        )

                        y = fila.get(
                            "descripcion_y0",
                            0
                        )

                        ancho = (
                            fila.get(
                                "descripcion_x1",
                                x
                            )
                            - x
                        )

                        alto = (
                            fila.get(
                                "descripcion_y1",
                                y
                            )
                            - y
                        )

                    # ---------------------------------
                    # Guardar campo
                    # ---------------------------------

                    encontrados.append({

                       "seccion": self.TITULO,

                       "campo": campo,

                       "valor": contenido,

                       "pagina": fila["pagina"],

                       "x": x,
                       "y": y,
                       "ancho": ancho,
                       "alto": alto


                    })

                    # ---------------------------------
                    # Ya encontró el campo
                    # ---------------------------------

                    break

        print(
            f"\nTOTAL CAMPOS ENCONTRADOS: "
            f"{len(encontrados)}"
        )

        return encontrados