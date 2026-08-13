"""
SECCIÓN BASE
"""


class Seccion:

    TITULO = ""
    FIN = ""

    def __init__(self):

        pass

    # ==========================================
    # OBTENER FILAS DE LA SECCIÓN
    # ==========================================

    def obtener_bloques(self, filas):

        dentro = False

        resultado = []

        for fila in filas:

            # ----------------------------------
            # Construir texto de la fila
            # ----------------------------------

            descripcion = fila.get(
                "descripcion",
                ""
            )

            contenido = fila.get(
                "contenido",
                ""
            )

            texto = (
                descripcion
                + " "
                + contenido
            ).strip()

            # ----------------------------------
            # Inicio de la sección
            # ----------------------------------

            if self.TITULO:

                if self.TITULO.lower() in texto.lower():

                    dentro = True

                    continue

            # ----------------------------------
            # Fin de la sección
            # ----------------------------------

            if dentro and self.FIN:

                if self.FIN.lower() in texto.lower():

                    break

            # ----------------------------------
            # Guardar fila
            # ----------------------------------

            if dentro:

                resultado.append(fila)

        return resultado

    # ==========================================
    # NORMALIZAR TEXTO
    # ==========================================

    def normalizar(self, texto):

        return " ".join(
            texto.upper().split()
        )

    # ==========================================
    # COMPARAR ETIQUETA
    # ==========================================

    def coincide_etiqueta(
        self,
        texto,
        etiqueta
    ):

        texto = self.normalizar(texto)

        etiqueta = self.normalizar(etiqueta)

        return (
            texto == etiqueta
            or texto.startswith(
                etiqueta + " "
            )
            or texto.startswith(
                etiqueta
            )
        )