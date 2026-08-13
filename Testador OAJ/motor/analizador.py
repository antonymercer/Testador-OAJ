from motor.reglas import Reglas


class Analizador:

    def __init__(self):

        self.reglas = Reglas()

        # =====================================================
        # CONFIGURACIÓN DE SECCIONES
        # =====================================================

        self.secciones = {

            "Datos Generales": {
                "modo": "LISTA",
                "campos": [
                    "Nombre(s)",
                    "Primer apellido",
                    "Segundo apellido",
                    "CURP",
                    "RFC",
                    "Homoclave",
                    "Correo electrónico institucional",
                    "Correo electrónico personal / Alterno",
                    "Número celular personal",
                    "Situación personal / estado civil",
                    "** Régimen matrimonial",
                    "País de nacimiento",
                    "Nacionalidad (es)",
                    "¿Te desempeñaste como servidor público el año inmediato anterior?",
                ]
            },


            "Domicilio del declarante": {
                "modo": "LISTA",
                "campos": [
                    "Lugar en que reside actualmente",
                    "Calle",
                    "Número exterior",
                    "Número interior",
                    "Colonia / Localidad",
                    "Entidad federativa",
                    "Municipio / Alcaldía",
                    "Código postal",
                ]
            },


            # =================================================
            # NO TESTAR
            # =================================================

            "Datos curriculares del declarante": {
                "modo": "IGNORAR",
                "campos": []
            },


            # =================================================
            # SOLO UN CAMPO
            # =================================================

            "Datos del empleo, cargo o comisión actual": {
                "modo": "LISTA",
                "campos": [
                    "Número de expediente del declarante",
                ]
            },


            # =================================================
            # TODO
            # =================================================

            "Datos de la pareja": {
                "modo": "TODO",
                "campos": []
            },


            "Datos del dependiente económico": {
                "modo": "TODO",
                "campos": []
            },

        }


    # =========================================================
    # NORMALIZAR
    # =========================================================

    def normalizar(self, texto):

        if not texto:
            return ""

        return " ".join(
            texto.upper().split()
        )


    # =========================================================
    # IDENTIFICAR SECCIÓN
    # =========================================================

    def identificar_seccion(self, descripcion):

        texto = self.normalizar(
            descripcion
        )

        for seccion in self.secciones:

            titulo = self.normalizar(
                seccion
            )

            if texto == titulo:

                return seccion

        return None


    # =========================================================
    # IDENTIFICAR CAMPO
    # =========================================================

    def identificar_campo(
        self,
        descripcion,
        campos
    ):

        descripcion_normalizada = self.normalizar(
            descripcion
        )

        for campo in campos:

            campo_normalizado = self.normalizar(
                campo
            )

            # Coincidencia exacta
            if (
                descripcion_normalizada
                == campo_normalizado
            ):

                return campo


            # La descripción comienza con el campo
            if descripcion_normalizada.startswith(
                campo_normalizado + " "
            ):

                return campo


            # La descripción contiene el campo
            if campo_normalizado in descripcion_normalizada:

                return campo

        return None


    # =========================================================
    # COORDENADAS
    # =========================================================

    def obtener_coordenadas(self, fila):

        # -----------------------------------------
        # Preferir CONTENIDO
        # -----------------------------------------

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

            return x, y, ancho, alto


        # -----------------------------------------
        # Respaldo: DESCRIPCIÓN
        # -----------------------------------------

        if (
            "descripcion_x0" in fila
            and "descripcion_y0" in fila
            and "descripcion_x1" in fila
            and "descripcion_y1" in fila
        ):

            x = fila["descripcion_x0"]
            y = fila["descripcion_y0"]

            ancho = (
                fila["descripcion_x1"]
                - fila["descripcion_x0"]
            )

            alto = (
                fila["descripcion_y1"]
                - fila["descripcion_y0"]
            )

            return x, y, ancho, alto

        return None


    # =========================================================
    # ANALIZAR DOCUMENTO
    # =========================================================

    def analizar(self, filas):

        campos = []

        seccion_actual = None

        print()
        print("==============================")
        print("ANALISIS POR SECCIONES")
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

            # =================================================
            # IGNORAR PIE DE PÁGINA
            # =================================================

            descripcion_normalizada = self.normalizar(
                descripcion
            )

            contenido_normalizado = self.normalizar(
                contenido
            )
            

            # CV, CD y número de página NO son datos
            if (
                descripcion_normalizada.startswith("CV ")
                or descripcion_normalizada.startswith("CD ")
                or descripcion_normalizada.startswith("PÁG.")
                or descripcion_normalizada.startswith("PAG.")
                or "PÁG. " in descripcion_normalizada
                or "PAG. " in descripcion_normalizada
                or "DE 18" in descripcion_normalizada
            ):

                continue

            if (
                contenido_normalizado.startswith("CV ")
                or contenido_normalizado.startswith("CD ")
                or contenido_normalizado.startswith("PÁG.")
                or contenido_normalizado.startswith("PAG.")
            ):

                continue

            # -----------------------------------------
            # FILA VACÍA
            # -----------------------------------------

            if not descripcion and not contenido:
                continue


            # =================================================
            # DETECTAR NUEVA SECCIÓN
            # =================================================

            nueva_seccion = self.identificar_seccion(
                descripcion
            )

            if nueva_seccion:

                seccion_actual = nueva_seccion

                print()
                print(
                    f"SECCION: {seccion_actual}"
                )

                continue


            # =================================================
            # TODAVÍA NO HAY SECCIÓN
            # =================================================

            if not seccion_actual:
                continue


            # =================================================
            # IGNORAR ENCABEZADOS
            # =================================================

            descripcion_normalizada = self.normalizar(
                descripcion
            )

            if descripcion_normalizada in (
                "DESCRIPCIÓN",
                "CONTENIDO"
            ):

                continue


            # =================================================
            # OBTENER CONFIGURACIÓN DE LA SECCIÓN
            # =================================================

            configuracion = self.secciones[
                seccion_actual
            ]

            modo = configuracion["modo"]


            # =================================================
            # SECCIÓN IGNORADA
            # =================================================

            if modo == "IGNORAR":

                continue


            # =================================================
            # MODO LISTA
            # =================================================

            if modo == "LISTA":

                campo_identificado = (
                    self.identificar_campo(

                        descripcion,

                        configuracion["campos"]

                    )
                )


                if not campo_identificado:

                    continue


            # =================================================
            # MODO TODO
            # =================================================

            elif modo == "TODO":

                campo_identificado = descripcion


                # No crear campos sin descripción
                if not campo_identificado:

                    continue


            # =================================================
            # COORDENADAS
            # =================================================

            coordenadas = self.obtener_coordenadas(
                fila
            )

            if coordenadas is None:

                continue


            x, y, ancho, alto = coordenadas


            # =================================================
            # CREAR CAMPO
            # =================================================

            campo = {

                "seccion": seccion_actual,

                "campo": campo_identificado,

                "valor": contenido,

                "pagina": fila["pagina"],

                "x": x,

                "y": y,

                "ancho": ancho,

                "alto": alto,

                "accion": "IGNORAR"

            }


            campos.append(
                campo
            )


            print(
                f"{seccion_actual} | "
                f"{campo_identificado} | "
                f"{contenido}"
            )


        print()
        print("==============================")
        print(
            f"TOTAL CAMPOS: {len(campos)}"
        )
        print("==============================")


        return campos