import re
import unicodedata

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
            # DATOS DEL EMPLEO
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

            "Datos del cónyuge": {
                "modo": "TODO",
                "campos": []
            },

            "Ingresos netos del declarante, pareja y/o dependientes económicos": {
                "modo": "TODO",
                "campos": []
            },

            "Bienes inmuebles": {
                "modo": "TODO",
                "campos": []
            },

            "Vehículos": {
                "modo": "TODO",
                "campos": []
            },

            "Inversiones, cuentas bancarias y otro tipo de valores / activos": {
                "modo": "TODO",
                "campos": []
            },

            "Adeudos / pasivos / créditos / tarjetas de crédito o departamentales": {
                "modo": "TODO",
                "campos": []
            },
        }

    # =========================================================
    # NORMALIZAR
    # =========================================================

    def normalizar(self, texto):

        texto = unicodedata.normalize(
            "NFD",
            texto or ""
        )

        texto = "".join(
            caracter
            for caracter in texto
            if unicodedata.category(caracter) != "Mn"
        )

        return re.sub(
            r"\s+",
            " ",
            texto.upper()
        ).strip()

    # =========================================================
    # IDENTIFICAR SECCIÓN
    # =========================================================

    def identificar_seccion(
        self,
        descripcion,
        contenido=""
    ):

        texto_descripcion = self.normalizar(
            descripcion
        )

        texto_contenido = self.normalizar(
            contenido
        )

        textos = [
            texto_descripcion,
            texto_contenido,
            f"{texto_descripcion} {texto_contenido}".strip()
        ]

        # =====================================================
        # SECCIONES CONFIGURADAS
        # =====================================================

        for seccion in self.secciones:

            titulo = self.normalizar(
                seccion
            )

            for texto in textos:

                if not texto:
                    continue

                if (
                    texto == titulo
                    or texto.startswith(titulo)
                    
                ):
                    return seccion

        # =====================================================
        # CASOS ESPECIALES
        # =====================================================

        for texto in textos:

            if not texto:
                continue

            if "DATOS DEL CONYUGE" in texto:
                return "Datos del cónyuge"

            if "DATOS DE LA PAREJA" in texto:
                return "Datos de la pareja"

            if "DEPENDIENTE ECONOMICO" in texto:
                return "Datos del dependiente económico"

            if "BIENES INMUEBLES" in texto:
                return "Bienes inmuebles"

            if "VEHICULOS" in texto:
                return "Vehículos"

            if "INGRESOS NETOS" in texto:
                return (
                    "Ingresos netos del declarante, "
                    "pareja y/o dependientes económicos"
                )

            if (
                "INVERSIONES" in texto
                and (
                    "CUENTAS BANCARIAS" in texto
                    or "ACTIVOS" in texto
                )
            ):
                return (
                    "Inversiones, cuentas bancarias "
                    "y otro tipo de valores / activos"
                )

            if (
                "ADEUDOS" in texto
                or "PASIVOS" in texto
            ):
                return (
                    "Adeudos / pasivos / créditos / "
                    "tarjetas de crédito o departamentales"
                )

        return None

    # =========================================================
    # IDENTIFICAR CAMPO
    # =========================================================

    def identificar_campo(
        self,
        descripcion,
        contenido,
        campos
    ):

        descripcion_normalizada = self.normalizar(
            descripcion
        )

        contenido_normalizado = self.normalizar(
            contenido
        )

        textos = [
            descripcion_normalizada,
            contenido_normalizado,
            f"{descripcion_normalizada} "
            f"{contenido_normalizado}".strip()
        ]

        for campo in campos:

            campo_normalizado = self.normalizar(
                campo
            )

            for texto in textos:

                if not texto:
                    continue

                if texto == campo_normalizado:
                    return campo

                if texto.startswith(
                    campo_normalizado + " "
                ):
                    return campo

                if campo_normalizado in texto:
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
    # PIE DE PÁGINA
    # =========================================================

    def _es_pie_de_pagina(self, texto):

        texto = self.normalizar(
            texto
        )

        return texto.startswith(
            (
                "CV ",
                "CD ",
                "PAG. ",
                "PAG "
            )
        )

    # =========================================================
    # REGEX DE MONTO
    # =========================================================

    def _extraer_montos(self, texto):

        if not texto:
            return []

        patron = (
            r"\$\s*"
            r"\d{1,3}"
            r"(?:,\d{3})*"
            r"(?:\.\d{1,2})?"
        )

        return re.findall(
            patron,
            texto
        )

    # =========================================================
    # ¿TIENE CÓNYUGE?
    # =========================================================

    def _contiene_conyuge(
        self,
        descripcion,
        contenido
    ):

        texto = (
            self.normalizar(descripcion)
            + " "
            + self.normalizar(contenido)
        )

        return (
            "CONYUGE" in texto
            or "CÓNYUGE" in texto
        )

    # =========================================================
    # ¿ES ACLARACIÓN?
    # =========================================================

    def _es_aclaracion(
        self,
        descripcion
    ):

        texto = self.normalizar(
            descripcion
        )

        return (
            "ACLARACIONES" in texto
            or "OBSERVACIONES" in texto
        )

    # =========================================================
    # ¿ES SERVIDOR PÚBLICO?
    # =========================================================

    def _es_pregunta_servidor_publico(
        self,
        descripcion
    ):

        texto = self.normalizar(
            descripcion
        )

        return (
            "TE DESEMPENASTE COMO SERVIDOR PUBLICO"
            in texto
        )

    # =========================================================
    # ¿ES FILA SENSIBLE?
    # =========================================================

    def _es_campo_sensible(
        self,
        descripcion,
        contenido
    ):

        texto = self.normalizar(
            descripcion
        )

        # =====================================================
        # CÓNYUGE
        # =====================================================

        if self._contiene_conyuge(
            descripcion,
            contenido
        ):
            return True

        # =====================================================
        # ACLARACIONES / OBSERVACIONES
        # =====================================================

        if self._es_aclaracion(
            descripcion
        ):
            return True

        # =====================================================
        # ETIQUETAS SENSIBLES
        # =====================================================

        etiquetas = (

            "MONTO",
            "VALOR",
            "PRECIO",
            "SALDO INSOLUTO",

            "FOLIO",
            "DATOS DEL REGISTRO",

            "NUMERO DE SERIE",
            "NUMERO DE REGISTRO",

            "NOMBRE O RAZON SOCIAL",
            "NOMBRE, DENOMINACION O RAZON SOCIAL",
            "NOMBRE, INSTITUCION O RAZON SOCIAL",
            "INSTITUCION O RAZON SOCIAL",

            "RFC",
            "EXPEDIENTE",
        )

        if any(
            etiqueta in texto
            for etiqueta in etiquetas
        ):
            return True

        # =====================================================
        # MONTOS DENTRO DE DESCRIPCIÓN O CONTENIDO
        # =====================================================

        if self._extraer_montos(
            descripcion
        ):
            return True

        if self._extraer_montos(
            contenido
        ):
            return True

        return False

    # =========================================================
    # CREAR CAMPO
    # =========================================================

    def _crear_campo(
        self,
        fila,
        campo,
        valor=None,
        seccion=None,
        forzar_testado=False
    ):

        coordenadas = self.obtener_coordenadas(
            fila
        )

        if coordenadas is None:
            return None

        x, y, ancho, alto = coordenadas

        return {

            "seccion": (
                seccion
                or fila.get(
                    "seccion",
                    "Regla especial"
                )
            ),

            "campo": campo,

            "valor": (
                fila.get(
                    "contenido",
                    ""
                )
                if valor is None
                else valor
            ),

            "pagina": fila.get(
                "pagina"
            ),

            "x": x,
            "y": y,
            "ancho": ancho,
            "alto": alto,

            "accion": "IGNORAR",

            "forzar_testado": (
                forzar_testado
            ),
        }

    # =========================================================
    # CREAR CAMPO FORZADO
    # =========================================================

    def _crear_campo_forzado(
        self,
        fila,
        seccion="Regla patrimonial"
    ):

        descripcion = fila.get(
            "descripcion",
            ""
        ).strip()

        contenido = fila.get(
            "contenido",
            ""
        ).strip()

        if not descripcion:
            return None

        return self._crear_campo(
            fila,
            descripcion,
            contenido,
            seccion,
            True
        )

    # =========================================================
    # AGREGAR SI NO EXISTE
    # =========================================================

    def _agregar_si_no_existe(
        self,
        campos,
        nuevo
    ):

        if nuevo is None:
            return

        for campo in campos:

            misma_ubicacion = (

                campo.get(
                    "pagina"
                )
                == nuevo.get(
                    "pagina"
                )

                and

                abs(
                    campo.get(
                        "x",
                        -1
                    )
                    - nuevo.get(
                        "x",
                        -2
                    )
                ) < 0.1

                and

                abs(
                    campo.get(
                        "y",
                        -1
                    )
                    - nuevo.get(
                        "y",
                        -2
                    )
                ) < 0.1
            )

            if misma_ubicacion:

                campo[
                    "forzar_testado"
                ] = True

                return

        campos.append(
            nuevo
        )

    # =========================================================
    # AGREGAR MONTO
    # =========================================================

    def _agregar_montos_de_fila(
        self,
        fila,
        campos
    ):

        descripcion = fila.get(
            "descripcion",
            ""
        ).strip()

        contenido = fila.get(
            "contenido",
            ""
        ).strip()

        textos = [
            descripcion,
            contenido
        ]

        for texto in textos:

            montos = self._extraer_montos(
                texto
            )

            if not montos:
                continue

            for monto in montos:

                nuevo = self._crear_campo(
                    fila,
                    "Monto",
                    monto,
                    "Montos",
                    True
                )

                self._agregar_si_no_existe(
                    campos,
                    nuevo
                )

    # =========================================================
    # AGREGAR ACLARACIÓN
    # =========================================================

    def _agregar_aclaracion(
        self,
        fila,
        campos
    ):

        descripcion = fila.get(
            "descripcion",
            ""
        ).strip()

        contenido = fila.get(
            "contenido",
            ""
        ).strip()

        if not contenido:
            return

        if not self._es_aclaracion(
            descripcion
        ):
            return

        nuevo = self._crear_campo(
            fila,
            descripcion,
            contenido,
            "Aclaraciones",
            True
        )

        self._agregar_si_no_existe(
            campos,
            nuevo
        )

    # =========================================================
    # SERVIDOR PÚBLICO
    # =========================================================

    def _agregar_servidor_publico(
        self,
        filas,
        indice,
        campos
    ):

        fila = filas[indice]

        descripcion = self.normalizar(
            fila.get(
                "descripcion",
                ""
            )
        )

        if not self._es_pregunta_servidor_publico(
            descripcion
        ):
            return

        # -----------------------------------------------------
        # El PDF puede partir la pregunta en 2 filas:
        #
        # ¿Te desempeñaste ... inmediato
        # anterior?
        #
        # SI
        # -----------------------------------------------------

        for siguiente in filas[
            indice + 1:
            indice + 4
        ]:

            valor = (
                siguiente.get(
                    "contenido",
                    ""
                )
                or siguiente.get(
                    "descripcion",
                    ""
                )
            ).strip()

            valor_normalizado = self.normalizar(
                valor
            )

            if valor_normalizado in (
                "SI",
                "SÍ",
                "NO"
            ):

                nuevo = self._crear_campo(
                    siguiente,
                    "Servidor público",
                    valor,
                    "Datos Generales",
                    True
                )

                self._agregar_si_no_existe(
                    campos,
                    nuevo
                )

                return

    # =========================================================
    # ANALIZAR DOCUMENTO
    # =========================================================

    def analizar(self, filas):

        campos = []

        seccion_actual = None

        documento_final = False

        print()
        print("==============================")
        print("ANALISIS POR SECCIONES")
        print("==============================")

        for indice, fila in enumerate(
            filas
        ):

            descripcion = fila.get(
                "descripcion",
                ""
            ).strip()

            contenido = fila.get(
                "contenido",
                ""
            ).strip()

            descripcion_normalizada = self.normalizar(
                descripcion
            )

            contenido_normalizado = self.normalizar(
                contenido
            )

            # =================================================
            # BLOQUE FINAL
            # =================================================

            # IMPORTANTE:
            # La primera página también contiene "BAJO PROTESTA
            # DE DECIR VERDAD", pero NO es el cierre.
            #
            # El cierre real del documento es:
            # "BAJO PROTESTA DE DECIR VERDAD:"
            # =================================================

            if (
                descripcion_normalizada.strip()
                == "BAJO PROTESTA DE DECIR VERDAD:"
            ):

                documento_final = True
                continue

            if documento_final:
                continue

            # =================================================
            # PIE DE PÁGINA
            # =================================================

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

            # =================================================
            # FILA VACÍA
            # =================================================

            if (
                not descripcion
                and not contenido
            ):
                continue

            # =================================================
            # DETECTAR SECCIÓN
            # =================================================

            nueva_seccion = (
                self.identificar_seccion(
                    descripcion,
                    contenido
                )
            )

            if nueva_seccion:

                seccion_actual = nueva_seccion

                print()
                print(
                    f"SECCION: {seccion_actual}"
                )

                continue

            # =================================================
            # SERVIDOR PÚBLICO
            # =================================================

            self._agregar_servidor_publico(
                filas,
                indice,
                campos
            )

            # =================================================
            # SI NO HAY SECCIÓN
            # =================================================

            if not seccion_actual:
                continue

            # =================================================
            # ENCABEZADOS
            # =================================================

            if descripcion_normalizada in (
                "DESCRIPCION",
                "DESCRIPCIÓN",
                "CONTENIDO"
            ):
                continue

            # =================================================
            # CONFIGURACIÓN
            # =================================================

            configuracion = (
                self.secciones[
                    seccion_actual
                ]
            )

            modo = configuracion[
                "modo"
            ]

            # =================================================
            # IGNORAR SECCIÓN
            # =================================================

            if modo == "IGNORAR":
                continue

            # =================================================
            # LISTA
            # =================================================

            if modo == "LISTA":

                campo_identificado = (
                    self.identificar_campo(
                        descripcion,
                        contenido,
                        configuracion[
                            "campos"
                        ]
                    )
                )

                if not campo_identificado:
                    continue

            # =================================================
            # TODO
            # =================================================

            elif modo == "TODO":

                campo_identificado = (
                    descripcion
                    if descripcion
                    else "Campo"
                )

            else:

                continue

            # =================================================
            # COORDENADAS
            # =================================================

            coordenadas = (
                self.obtener_coordenadas(
                    fila
                )
            )

            if coordenadas is None:
                continue

            x, y, ancho, alto = coordenadas

            # =================================================
            # CREAR CAMPO PRINCIPAL
            # =================================================

            campo = {

                "seccion": seccion_actual,

                "campo": campo_identificado,

                "valor": contenido,

                "pagina": fila.get(
                    "pagina"
                ),

                "x": x,

                "y": y,

                "ancho": ancho,

                "alto": alto,

                "accion": "IGNORAR",

                "forzar_testado": False
            }

            # =================================================
            # REGLAS INMEDIATAS
            # =================================================

            if seccion_actual in (
                "Datos de la pareja",
                "Datos del dependiente económico",
                "Datos del cónyuge"
            ):

                campo[
                    "forzar_testado"
                ] = True

            if self._contiene_conyuge(
                descripcion,
                contenido
            ):

                campo[
                    "forzar_testado"
                ] = True

            if self._es_aclaracion(
                descripcion
            ):

                campo[
                    "forzar_testado"
                ] = True

            campos.append(
                campo
            )

            print(
                f"{seccion_actual} | "
                f"{campo_identificado} | "
                f"{contenido}"
            )

            # =================================================
            # MONTOS
            # =================================================

            self._agregar_montos_de_fila(
                fila,
                campos
            )

            # =================================================
            # ACLARACIONES
            # =================================================

            self._agregar_aclaracion(
                fila,
                campos
            )

    # =========================================================
    # CAMPOS ESPECIALES DESPUÉS DEL RECORRIDO
    # =========================================================

        # =====================================================
        # FOLIO DE BIENES INMUEBLES
        # =====================================================

        seccion_bienes = False

        esperar_folio = False

        for fila in filas:

            descripcion = fila.get(
                "descripcion",
                ""
            ).strip()

            contenido = fila.get(
                "contenido",
                ""
            ).strip()

            texto = self.normalizar(
                descripcion
            )

            if (
                texto.startswith(
                    "BIENES INMUEBLES"
                )
            ):

                seccion_bienes = True
                continue

            if not seccion_bienes:
                continue

            if (
                "DATOS DEL REGISTRO PUBLICO"
                in texto
            ):

                esperar_folio = True
                continue

            if esperar_folio:

                candidato = (
                    contenido
                    or descripcion
                ).strip()

                # Folio numérico típico
                if re.fullmatch(
                    r"\d{4,}",
                    candidato
                ):

                    nuevo = self._crear_campo(
                        fila,
                        "Folio del inmueble",
                        candidato,
                        "Bienes inmuebles",
                        True
                    )

                    self._agregar_si_no_existe(
                        campos,
                        nuevo
                    )

                    esperar_folio = False

            # Terminar cuando cambia de sección
            if (
                texto.startswith(
                    "VEHICULOS"
                )
                or texto.startswith(
                    "VEHÍCULOS"
                )
            ):

                break

        # =====================================================
        # NOMBRES DE TRANSMISORES EN BIENES
        # =====================================================

        for fila in filas:

            descripcion = fila.get(
                "descripcion",
                ""
            ).strip()

            contenido = fila.get(
                "contenido",
                ""
            ).strip()

            texto = self.normalizar(
                descripcion
            )

            if (
                "NOMBRE O RAZON SOCIAL DEL TRANSMISOR"
                in texto
                or
                "NOMBRE O RAZON SOCIAL DEL TRANSMISOR DE LA PROPIEDAD"
                in texto
            ):

                if contenido:

                    nuevo = self._crear_campo(
                        fila,
                        "Nombre del transmisor",
                        contenido,
                        "Bienes inmuebles",
                        True
                    )

                    self._agregar_si_no_existe(
                        campos,
                        nuevo
                    )

        # =====================================================
        # REVISAR TODOS LOS CAMPOS POR CÓNYUGE
        # =====================================================

        for campo in campos:

            if self._contiene_conyuge(
                campo.get(
                    "campo",
                    ""
                ),
                campo.get(
                    "valor",
                    ""
                )
            ):

                campo[
                    "forzar_testado"
                ] = True

        # =====================================================
        # REGISTROS DE CÓNYUGE
        # =====================================================

        inicio_registro = {}
        registro_conyuge = {}

        for indice, campo in enumerate(
            campos
        ):

            seccion = campo.get(
                "seccion",
                ""
            )

            nombre = self.normalizar(
                campo.get(
                    "campo",
                    ""
                )
            )

            valor = self.normalizar(
                campo.get(
                    "valor",
                    ""
                )
            )

            if nombre.startswith(
                "SELECCIONE EL TIPO DE OPERACI"
            ):

                inicio_registro[
                    seccion
                ] = indice

                registro_conyuge[
                    seccion
                ] = False

            if (
                "CONYUGE" in valor
                or "CÓNYUGE" in valor
            ):

                registro_conyuge[
                    seccion
                ] = True

                inicio = (
                    inicio_registro.get(
                        seccion,
                        indice
                    )
                )

                for previo in campos[
                    inicio:indice + 1
                ]:

                    if (
                        previo.get(
                            "seccion"
                        )
                        == seccion
                    ):

                        previo[
                            "forzar_testado"
                        ] = True

            if registro_conyuge.get(
                seccion,
                False
            ):

                campo[
                    "forzar_testado"
                ] = True

        # =====================================================
        # CAMPOS PATRIMONIALES ESPECIALES
        # =====================================================

        self._agregar_campos_especiales(
            filas,
            campos
        )

        # =====================================================
        # RESUMEN
        # =====================================================

        total_testar = sum(
            1
            for campo in campos
            if campo.get(
                "forzar_testado",
                False
            )
        )

        print()
        print("==============================")
        print(
            f"TOTAL CAMPOS: {len(campos)}"
        )
        print(
            f"TOTAL A TESTAR: {total_testar}"
        )
        print("==============================")

        return campos

    # =========================================================
    # CAMPOS PATRIMONIALES ESPECIALES
    # =========================================================

    def _agregar_campos_especiales(
        self,
        filas,
        campos
    ):

        registro = []

        pagina_anterior = None

        pagina_final = False

        # =====================================================
        # PROCESAR REGISTRO
        # =====================================================

        def procesar_registro():

            if not registro:
                return

            es_conyuge = any(

                self._contiene_conyuge(
                    fila.get(
                        "descripcion",
                        ""
                    ),
                    fila.get(
                        "contenido",
                        ""
                    )
                )

                for fila in registro
            )

            if not es_conyuge:
                return

            for fila_registro in registro:

                self._agregar_si_no_existe(

                    campos,

                    self._crear_campo_forzado(
                        fila_registro,
                        "Registro conyuge"
                    )
                )

        # =====================================================
        # RECORRER FILAS
        # =====================================================

        for fila in filas:

            descripcion = fila.get(
                "descripcion",
                ""
            ).strip()

            contenido = fila.get(
                "contenido",
                ""
            ).strip()

            descripcion_normalizada = (
                self.normalizar(
                    descripcion
                )
            )

            contenido_normalizado = (
                self.normalizar(
                    contenido
                )
            )

            pagina = fila.get(
                "pagina"
            )

            # =================================================
            # CIERRE DEL DOCUMENTO
            # =================================================

            if (
                descripcion_normalizada.strip()
                == "BAJO PROTESTA DE DECIR VERDAD:"
            ):

                procesar_registro()

                registro = []

                pagina_final = True

                continue

            if pagina_final:
                continue

            # =================================================
            # CAMBIO DE PÁGINA
            # =================================================

            if (
                pagina_anterior is not None
                and pagina != pagina_anterior
            ):

                procesar_registro()

                registro = []

            pagina_anterior = pagina

            # =================================================
            # NUEVO REGISTRO
            # =================================================

            if descripcion_normalizada.startswith(
                "SELECCIONE EL TIPO DE OPERACI"
            ):

                procesar_registro()

                registro = []

            # =================================================
            # AGREGAR FILA AL REGISTRO
            # =================================================

            if (
                descripcion
                and (
                    contenido
                    or descripcion
                )
                and not self._es_pie_de_pagina(
                    descripcion
                )
            ):

                registro.append(
                    fila
                )

            # =================================================
            # DETECCIÓN DE CÓNYUGE
            # =================================================

            if self._contiene_conyuge(
                descripcion,
                contenido
            ):

                nuevo = self._crear_campo(
                    fila,
                    descripcion,
                    contenido,
                    "Registro conyuge",
                    True
                )

                self._agregar_si_no_existe(
                    campos,
                    nuevo
                )

            # =================================================
            # MONTO
            # =================================================

            if self._extraer_montos(
                descripcion
            ) or self._extraer_montos(
                contenido
            ):

                self._agregar_montos_de_fila(
                    fila,
                    campos
                )

            # =================================================
            # ACLARACIONES
            # =================================================

            self._agregar_aclaracion(
                fila,
                campos
            )

        # =====================================================
        # PROCESAR ÚLTIMO REGISTRO
        # =====================================================

        procesar_registro()