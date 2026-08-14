import re
import unicodedata


class Analizador:

    def __init__(self):

        # =====================================================
        # CONFIGURACIÓN
        # =====================================================

        self.secciones = {

            # NO TESTAR
            "Datos Generales":
                "IGNORAR",

            "Domicilio del declarante":
                "IGNORAR",

            "Datos curriculares del declarante":
                "IGNORAR",

            "Datos del empleo, cargo o comisión actual":
                "IGNORAR",

            # TODO TESTAR
            "Datos de la pareja":
                "TODO",

            "Datos del dependiente económico":
                "TODO",

            "Datos del cónyuge":
                "TODO",

            # TESTAR SOLO DATOS SENSIBLES
            "Ingresos netos del declarante, pareja y/o dependientes económicos":
                "SENSIBLES",

            "Bienes inmuebles":
                "SENSIBLES",

            "Vehículos":
                "SENSIBLES",

            "Inversiones, cuentas bancarias y otro tipo de valores / activos":
                "SENSIBLES",

            "Adeudos / pasivos / créditos / tarjetas de crédito o departamentales":
                "SENSIBLES",
        }

    # =====================================================
    # NORMALIZAR
    # =====================================================

    def normalizar(self, texto):

        texto = unicodedata.normalize(
            "NFD",
            texto or ""
        )

        texto = "".join(
            c
            for c in texto
            if unicodedata.category(c) != "Mn"
        )

        return re.sub(
            r"\s+",
            " ",
            texto.upper()
        ).strip()

    # =====================================================
    # IDENTIFICAR SECCIÓN
    # =====================================================

    def identificar_seccion(self, texto):

        texto = self.normalizar(
            texto
        )

        # ---------------------------------------------
        # TÍTULOS EXACTOS
        # ---------------------------------------------

        for seccion in self.secciones:

            titulo = self.normalizar(
                seccion
            )

            if (
                texto == titulo
                or texto.startswith(
                    titulo
                )
            ):
                return seccion

        # ---------------------------------------------
        # CASOS ESPECIALES
        # ---------------------------------------------

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

    # =====================================================
    # PIE DE PÁGINA
    # =====================================================

    def es_pie(self, texto):

        texto = self.normalizar(
            texto
        )

        return texto.startswith(
            (
                "CV ",
                "CD ",
                "PAG ",
                "PÁG "
            )
        )

    # =====================================================
    # DETECTAR MONTOS
    # =====================================================

    def extraer_montos(self, texto):

        if not texto:
            return []

        return re.findall(
            r"\$\s*\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?",
            texto
        )

    # =====================================================
    # DETECTAR CÓNYUGE
    # =====================================================

    def contiene_conyuge(
        self,
        descripcion,
        contenido
    ):

        texto = (
            self.normalizar(
                descripcion
            )
            + " "
            + self.normalizar(
                contenido
            )
        )

        return "CONYUGE" in texto

    # =====================================================
    # DETECTAR ACLARACIONES
    # =====================================================

    def es_aclaracion(
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

    # =====================================================
    # COORDENADAS DEL CONTENIDO
    # =====================================================

    def obtener_coordenadas(
        self,
        fila
    ):

        claves = (
            "contenido_x0",
            "contenido_y0",
            "contenido_x1",
            "contenido_y1",
        )

        if not all(
            clave in fila
            for clave in claves
        ):
            return None

        x = fila[
            "contenido_x0"
        ]

        y = fila[
            "contenido_y0"
        ]

        ancho = (
            fila["contenido_x1"]
            - fila["contenido_x0"]
        )

        alto = (
            fila["contenido_y1"]
            - fila["contenido_y0"]
        )

        return (
            x,
            y,
            ancho,
            alto
        )

    # =====================================================
    # CREAR CAMPO
    # =====================================================

    def crear_campo(
        self,
        fila,
        nombre,
        valor,
        seccion
    ):

        coordenadas = (
            self.obtener_coordenadas(
                fila
            )
        )

        if coordenadas is None:
            return None

        x, y, ancho, alto = coordenadas

        return {

            "seccion": seccion,

            "campo": nombre,

            "valor": valor,

            "pagina": fila.get(
                "pagina"
            ),

            "x": x,

            "y": y,

            "ancho": ancho,

            "alto": alto,

            "accion": "IGNORAR",

            "forzar_testado": True,
        }

    # =====================================================
    # AGREGAR SIN DUPLICAR
    # =====================================================

    def agregar(
        self,
        campos,
        campo
    ):

        if campo is None:
            return

        for existente in campos:

            misma_ubicacion = (

                existente.get(
                    "pagina"
                )
                == campo.get(
                    "pagina"
                )

                and

                abs(
                    existente.get(
                        "x",
                        -1
                    )
                    -
                    campo.get(
                        "x",
                        -2
                    )
                ) < 0.1

                and

                abs(
                    existente.get(
                        "y",
                        -1
                    )
                    -
                    campo.get(
                        "y",
                        -2
                    )
                ) < 0.1
            )

            if misma_ubicacion:

                existente[
                    "forzar_testado"
                ] = True

                return

        campos.append(
            campo
        )

    # =====================================================
    # SERVIDOR PÚBLICO
    # =====================================================

    def detectar_servidor_publico(
        self,
        filas,
        indice,
        campos
    ):

        descripcion = self.normalizar(
            filas[indice].get(
                "descripcion",
                ""
            )
        )

        if (
            "TE DESEMPENASTE COMO SERVIDOR PUBLICO"
            not in descripcion
        ):
            return

        # La respuesta puede estar en las
        # siguientes filas.
        for fila in filas[
            indice + 1:
            indice + 4
        ]:

            valor = (
                fila.get(
                    "contenido",
                    ""
                )
                or
                fila.get(
                    "descripcion",
                    ""
                )
            ).strip()

            if self.normalizar(
                valor
            ) in (
                "SI",
                "SÍ",
                "NO"
            ):

                campo = self.crear_campo(
                    fila,
                    "Servidor público",
                    valor,
                    "Datos Generales"
                )

                self.agregar(
                    campos,
                    campo
                )

                return

    # =====================================================
    # ANALIZAR
    # =====================================================

    def analizar(
        self,
        filas
    ):

        campos = []

        seccion_actual = None

        documento_final = False

        print()
        print(
            "=============================="
        )
        print(
            "ANALISIS POR SECCIONES"
        )
        print(
            "=============================="
        )

        # =================================================
        # RECORRER FILAS
        # =================================================

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

            desc = self.normalizar(
                descripcion
            )

            # =============================================
            # CIERRE REAL DEL DOCUMENTO
            # =============================================

            if (
                desc
                == "BAJO PROTESTA DE DECIR VERDAD:"
            ):

                documento_final = True

                continue

            if documento_final:
                continue

            # =============================================
            # PIE
            # =============================================

            if self.es_pie(
                descripcion
            ):
                continue

            # =============================================
            # VACÍA
            # =============================================

            if (
                not descripcion
                and not contenido
            ):
                continue

            # =============================================
            # NUEVA SECCIÓN
            # =============================================

            nueva_seccion = (
                self.identificar_seccion(
                    descripcion
                )
            )

            if nueva_seccion:

                seccion_actual = (
                    nueva_seccion
                )

                print(
                    f"SECCION: "
                    f"{seccion_actual}"
                )

                continue

            # =============================================
            # SERVIDOR PÚBLICO
            # =============================================

            self.detectar_servidor_publico(
                filas,
                indice,
                campos
            )

            # =============================================
            # SIN SECCIÓN
            # =============================================

            if not seccion_actual:
                continue

            # =============================================
            # ENCABEZADOS
            # =============================================

            if desc in (
                "DESCRIPCION",
                "DESCRIPCIÓN",
                "CONTENIDO"
            ):
                continue

            modo = self.secciones.get(
                seccion_actual
            )

            # =================================================
            # IGNORAR
            # =================================================

            if modo == "IGNORAR":

                continue

            # =================================================
            # TODO
            # =================================================

            if modo == "TODO":

                if not contenido:
                    continue

                campo = self.crear_campo(
                    fila,
                    descripcion,
                    contenido,
                    seccion_actual
                )

                self.agregar(
                    campos,
                    campo
                )

                print(
                    f"{seccion_actual} | "
                    f"{descripcion} | "
                    f"TESTAR"
                )

                continue

            # =================================================
            # SENSIBLES
            # =================================================

            if modo != "SENSIBLES":
                continue

            # =================================================
            # CÓNYUGE
            # =================================================

            if self.contiene_conyuge(
                descripcion,
                contenido
            ):

                campo = self.crear_campo(
                    fila,
                    descripcion,
                    contenido,
                    seccion_actual
                )

                self.agregar(
                    campos,
                    campo
                )

            # =================================================
            # ACLARACIONES
            # =================================================

            if (
                self.es_aclaracion(
                    descripcion
                )
                and contenido
            ):

                campo = self.crear_campo(
                    fila,
                    descripcion,
                    contenido,
                    seccion_actual
                )

                self.agregar(
                    campos,
                    campo
                )

            # =================================================
            # MONTOS
            # =================================================

            montos = (
                self.extraer_montos(
                    descripcion
                )
                +
                self.extraer_montos(
                    contenido
                )
            )

            for monto in montos:

                campo = self.crear_campo(
                    fila,
                    "Monto",
                    monto,
                    seccion_actual
                )

                self.agregar(
                    campos,
                    campo
                )

            # =================================================
            # FOLIO DE INMUEBLE
            # =================================================

            if (
                seccion_actual
                == "Bienes inmuebles"
                and re.fullmatch(
                    r"\d{4,}",
                    contenido
                )
            ):

                campo = self.crear_campo(
                    fila,
                    "Folio del inmueble",
                    contenido,
                    seccion_actual
                )

                self.agregar(
                    campos,
                    campo
                )

            # =================================================
            # NOMBRE DEL TRANSMISOR
            # =================================================

            if (
                seccion_actual
                == "Bienes inmuebles"
                and
                "NOMBRE O RAZON SOCIAL DEL TRANSMISOR"
                in desc
                and contenido
            ):

                campo = self.crear_campo(
                    fila,
                    "Nombre del transmisor",
                    contenido,
                    seccion_actual
                )

                self.agregar(
                    campos,
                    campo
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
        print(
            "=============================="
        )

        print(
            f"TOTAL CAMPOS: "
            f"{len(campos)}"
        )

        print(
            f"TOTAL A TESTAR: "
            f"{total_testar}"
        )

        print(
            "=============================="
        )

        return campos