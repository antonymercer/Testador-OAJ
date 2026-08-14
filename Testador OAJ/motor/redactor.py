import os
import re

import pymupdf


class Redactor:

    def __init__(self):

        # =====================================================
        # CONFIGURACIÓN
        # =====================================================

        self.x_contenido = 228.34

        self.ancho_testado = 250
        self.alto_testado = 10

        self.margen_x = 2
        self.margen_y = 1

        self.alto_aclaracion = 16

    # =====================================================
    # NORMALIZAR
    # =====================================================

    def normalizar(self, texto):

        texto = str(
            texto or ""
        ).upper()

        reemplazos = {
            "Á": "A",
            "É": "E",
            "Í": "I",
            "Ó": "O",
            "Ú": "U",
            "Ü": "U",
            "Ñ": "N",
        }

        for original, nuevo in reemplazos.items():

            texto = texto.replace(
                original,
                nuevo
            )

        return re.sub(
            r"\s+",
            " ",
            texto
        ).strip()

    # =====================================================
    # PALABRAS
    # =====================================================

    def palabras(
        self,
        pagina
    ):

        return pagina.get_text(
            "words"
        )

    # =====================================================
    # CONSTRUIR RENGLONES
    # =====================================================

    def obtener_renglones(
        self,
        pagina
    ):

        palabras = self.palabras(
            pagina
        )

        renglones = []

        for palabra in palabras:

            x0 = palabra[0]
            y0 = palabra[1]
            x1 = palabra[2]
            y1 = palabra[3]

            renglon = None

            for existente in renglones:

                if abs(
                    existente["y"] - y0
                ) <= 3:

                    renglon = existente
                    break

            if renglon is None:

                renglon = {
                    "y": y0,
                    "y1": y1,
                    "x0": x0,
                    "x1": x1,
                    "palabras": [],
                }

                renglones.append(
                    renglon
                )

            renglon[
                "palabras"
            ].append(
                palabra
            )

            renglon["y"] = min(
                renglon["y"],
                y0
            )

            renglon["y1"] = max(
                renglon["y1"],
                y1
            )

            renglon["x0"] = min(
                renglon["x0"],
                x0
            )

            renglon["x1"] = max(
                renglon["x1"],
                x1
            )

        renglones.sort(
            key=lambda r: r["y"]
        )

        # =================================================
        # DESCRIPCIÓN / CONTENIDO
        # =================================================

        for renglon in renglones:

            izquierda = []
            contenido = []

            for palabra in sorted(
                renglon["palabras"],
                key=lambda p: p[0]
            ):

                if palabra[0] < self.x_contenido:

                    izquierda.append(
                        palabra[4]
                    )

                else:

                    contenido.append(
                        palabra[4]
                    )

            renglon[
                "izquierda"
            ] = self.normalizar(
                " ".join(
                    izquierda
                )
            )

            renglon[
                "contenido"
            ] = self.normalizar(
                " ".join(
                    contenido
                )
            )

        return renglones

    # =====================================================
    # PIE DE PÁGINA
    # =====================================================

    def es_pie(
        self,
        pagina,
        y
    ):

        return (
            y >=
            pagina.rect.height - 65
        )

    # =====================================================
    # TÍTULOS REALES
    # =====================================================

    def es_titulo_seccion(
        self,
        renglon
    ):

        izquierda = self.normalizar(
            renglon["izquierda"]
        )

        contenido = self.normalizar(
            renglon["contenido"]
        )

        texto = self.normalizar(
            izquierda
            + " "
            + contenido
        )

        titulos = (
            "INGRESOS NETOS DEL DECLARANTE",
            "BIENES INMUEBLES (ENTRE",
            "BIENES MUEBLES (ENTRE",
            "VEHICULOS (ENTRE",
            "INVERSIONES, CUENTAS BANCARIAS",
            "ADEUDOS / PASIVOS / CREDITOS",
            "PRESTAMO O COMODATO",
        )

        if not any(
            texto.startswith(titulo)
            for titulo in titulos
        ):

            return False

        ancho = (
            renglon["x1"]
            - renglon["x0"]
        )

        return ancho >= 300

    # =====================================================
    # ENCABEZADO
    # =====================================================

    def es_encabezado(
        self,
        renglon
    ):

        izquierda = self.normalizar(
            renglon["izquierda"]
        )

        contenido = self.normalizar(
            renglon["contenido"]
        )

        if izquierda == "DESCRIPCION":
            return True

        if contenido == "CONTENIDO":
            return True

        return (
            "DESCRIPCION" in izquierda
            and
            "CONTENIDO" in contenido
        )

    # =====================================================
    # INICIO DE REGISTRO
    # =====================================================

    def es_inicio_registro(
        self,
        renglon
    ):

        izquierda = self.normalizar(
            renglon["izquierda"]
        )

        return (
            "SELECCIONE EL TIPO DE OPERACION"
            in izquierda
        )

    # =====================================================
    # BORDE DERECHO
    # =====================================================

    def borde_contenido(
        self,
        pagina,
        y
    ):

        candidatos = []

        try:

            dibujos = pagina.get_drawings()

            for dibujo in dibujos:

                rect = dibujo.get(
                    "rect"
                )

                if rect is None:
                    continue

                if rect.width > 1.5:
                    continue

                if not (
                    rect.y0 <= y <= rect.y1
                ):
                    continue

                x = rect.x0

                if (
                    x >
                    self.x_contenido + 20
                ):

                    candidatos.append(
                        x
                    )

        except Exception:

            candidatos = []

        if candidatos:

            return max(
                candidatos
            )

        return (
            self.x_contenido
            + self.ancho_testado
        )

    # =====================================================
    # RECTÁNGULO NORMAL
    # =====================================================

    def rect_fila(
        self,
        pagina,
        y,
        alto=None
    ):

        if alto is None:

            alto = self.alto_testado

        x_final = self.borde_contenido(
            pagina,
            y
        )

        return pymupdf.Rect(

            self.x_contenido,

            max(
                0,
                y - self.margen_y
            ),

            max(
                self.x_contenido + 20,
                x_final - self.margen_x
            ),

            min(
                pagina.rect.height,
                y
                + alto
                + self.margen_y
            )
        )

    # =====================================================
    # RECTÁNGULO ACLARACIÓN
    # =====================================================

    def rect_aclaracion(
        self,
        pagina,
        y,
        alto
    ):

        x_final = self.borde_contenido(
            pagina,
            y
        )

        return pymupdf.Rect(

            self.x_contenido,

            max(
                0,
                y - self.margen_y
            ),

            max(
                self.x_contenido + 20,
                x_final - self.margen_x
            ),

            min(
                pagina.rect.height,
                y + alto
            )
        )

    # =====================================================
    # AGREGAR REDACCIÓN
    # =====================================================

    def agregar_rect(
        self,
        pagina,
        rect
    ):

        if rect is None:
            return

        if (
            rect.x1 <= rect.x0
            or
            rect.y1 <= rect.y0
        ):

            return

        pagina.add_redact_annot(
            rect,
            fill=(0, 0, 0),
            cross_out=False
        )

    # =====================================================
    # TESTAR RENGLÓN
    # =====================================================

    def testar_renglon(
        self,
        pagina,
        renglon,
        alto=None
    ):

        if self.es_pie(
            pagina,
            renglon["y"]
        ):

            return

        if self.es_titulo_seccion(
            renglon
        ):

            return

        if self.es_encabezado(
            renglon
        ):

            return

        if not renglon[
            "contenido"
        ]:

            return

        self.agregar_rect(
            pagina,
            self.rect_fila(
                pagina,
                renglon["y"],
                alto
            )
        )

    # =====================================================
    # DATOS GENERALES
    # =====================================================

    def testar_datos_generales(
        self,
        pagina
    ):

        renglones = self.obtener_renglones(
            pagina
        )

        campos = (
            "CURP",
            "RFC",
            "HOMOCLAVE",
            "CORREO ELECTRONICO PERSONAL",
            "NUMERO CELULAR PERSONAL",
            "SITUACION PERSONAL",
            "PAIS DE NACIMIENTO",
            "NACIONALIDAD",
        )

        # =================================================
        # CAMPOS SENSIBLES
        # =================================================

        for renglon in renglones:

            etiqueta = self.normalizar(
                renglon["izquierda"]
            )

            etiqueta = etiqueta.lstrip(
                "* "
            )

            for campo in campos:

                if campo in etiqueta:

                    self.agregar_rect(
                        pagina,
                        self.rect_fila(
                            pagina,
                            renglon["y"]
                        )
                    )

                    break

        # =================================================
        # RÉGIMEN MATRIMONIAL
        # =================================================

        for renglon in renglones:

            etiqueta = self.normalizar(
                renglon["izquierda"]
            )

            contenido = self.normalizar(
                renglon["contenido"]
            )

            texto = self.normalizar(
                etiqueta
                + " "
                + contenido
            )

            if (
                "REGIMEN MATRIMONIAL"
                in texto
                or
                "REGIMEN PATRIMONIAL"
                in texto
            ):

                if (
                    "SOCIEDAD CONYUGAL"
                    in contenido
                    or
                    "SOCIEDAD MANCOMUNADA"
                    in contenido
                ):

                    self.agregar_rect(
                        pagina,
                        self.rect_fila(
                            pagina,
                            renglon["y"]
                        )
                    )

                    break

    # =====================================================
    # DOMICILIO
    # =====================================================

    def testar_domicilio(
        self,
        pagina
    ):

        renglones = self.obtener_renglones(
            pagina
        )

        activo = False

        for renglon in renglones:

            texto = (
                renglon["izquierda"]
                + " "
                + renglon["contenido"]
            )

            if (
                "DOMICILIO DEL DECLARANTE"
                in texto
            ):

                activo = True
                continue

            if (
                activo
                and
                "DATOS CURRICULARES"
                in texto
            ):

                break

            if not activo:
                continue

            self.testar_renglon(
                pagina,
                renglon
            )

    # =====================================================
    # SERVIDOR PÚBLICO
    #
    # DETECTA LA PREGUNTA CON Ñ NORMALIZADA
    # Y TESTA TODO EL RENGLÓN DE CONTENIDO
    # =====================================================

    def testar_servidor_publico(
        self,
        pagina
    ):

        palabras = pagina.get_text(
            "words"
        )

        # =================================================
        # AGRUPAR PALABRAS POR LÍNEA
        # =================================================

        grupos = []

        for palabra in palabras:

            y0 = palabra[1]
            y1 = palabra[3]

            grupo = None

            for existente in grupos:

                if abs(
                    existente["y"] - y0
                ) <= 4:

                    grupo = existente
                    break

            if grupo is None:

                grupo = {
                    "y": y0,
                    "y1": y1,
                    "palabras": [],
                }

                grupos.append(
                    grupo
                )

            grupo[
                "palabras"
            ].append(
                palabra
            )

            grupo["y"] = min(
                grupo["y"],
                y0
            )

            grupo["y1"] = max(
                grupo["y1"],
                y1
            )

        # =================================================
        # ENCONTRAR LA PREGUNTA
        # =================================================

        pregunta = None

        for grupo in grupos:

            ordenadas = sorted(
                grupo["palabras"],
                key=lambda p: p[0]
            )

            texto = self.normalizar(
                " ".join(
                    p[4]
                    for p in ordenadas
                )
            )

            if (
                "DESEMPENASTE"
                in texto
                and
                "SERVIDOR PUBLICO"
                in texto
            ):

                pregunta = grupo
                break

        if pregunta is None:
            return

        # =================================================
        # BUSCAR SI / NO
        # =================================================

        respuesta_y = None

        for palabra in palabras:

            x0 = palabra[0]
            y0 = palabra[1]

            valor = self.normalizar(
                palabra[4]
            )

            if valor not in (
                "SI",
                "NO",
            ):
                continue

            # Debe estar en la columna CONTENIDO
            if x0 < self.x_contenido:
                continue

            # Debe estar cerca verticalmente
            if y0 < pregunta["y"] - 5:
                continue

            if y0 > pregunta["y1"] + 30:
                continue

            respuesta_y = y0
            break

        if respuesta_y is None:
            return

        # =================================================
        # TESTAR TODO EL RENGLÓN
        # =================================================

        self.agregar_rect(
            pagina,
            self.rect_fila(
                pagina,
                respuesta_y
            )
        )

    # =====================================================
    # TESTAR SECCIÓN COMPLETA
    # =====================================================

    def testar_seccion(
        self,
        documento,
        titulo_inicio,
        titulos_fin
    ):

        activa = False

        for pagina in documento:

            renglones = self.obtener_renglones(
                pagina
            )

            for renglon in renglones:

                texto = (
                    renglon["izquierda"]
                    + " "
                    + renglon["contenido"]
                )

                if (
                    titulo_inicio
                    in texto
                ):

                    activa = True
                    continue

                if activa:

                    if any(
                        titulo in texto
                        for titulo in titulos_fin
                    ):

                        activa = False
                        break

                if not activa:
                    continue

                self.testar_renglon(
                    pagina,
                    renglon
                )

    # =====================================================
    # PAREJA
    # =====================================================

    def testar_pareja(
        self,
        documento
    ):

        self.testar_seccion(
            documento,

            "DATOS DE LA PAREJA",

            (
                "DATOS DEL DEPENDIENTE ECONOMICO",
                "INGRESOS NETOS DEL DECLARANTE",
            )
        )

    # =====================================================
    # DEPENDIENTES
    # =====================================================

    def testar_dependientes(
        self,
        documento
    ):

        self.testar_seccion(
            documento,

            "DATOS DEL DEPENDIENTE ECONOMICO",

            (
                "INGRESOS NETOS DEL DECLARANTE",
            )
        )

    # =====================================================
    # CÓNYUGE
    # =====================================================

    def testar_conyuge(
        self,
        pagina
    ):

        renglones = self.obtener_renglones(
            pagina
        )

        inicios = []

        for indice, renglon in enumerate(
            renglones
        ):

            if self.es_inicio_registro(
                renglon
            ):

                inicios.append(
                    indice
                )

        if not inicios:
            return

        for posicion, inicio in enumerate(
            inicios
        ):

            if (
                posicion + 1
                <
                len(inicios)
            ):

                fin = inicios[
                    posicion + 1
                ]

            else:

                fin = len(
                    renglones
                )

            bloque = renglones[
                inicio:fin
            ]

            tiene_conyuge = False

            for renglon in bloque:

                texto = self.normalizar(
                    renglon["izquierda"]
                    + " "
                    + renglon["contenido"]
                )

                if "CONYUGE" in texto:

                    tiene_conyuge = True
                    break

            if not tiene_conyuge:
                continue

            for renglon in bloque:

                self.testar_renglon(
                    pagina,
                    renglon
                )

    # =====================================================
    # MONTOS
    # =====================================================

    def testar_montos(
        self,
        pagina
    ):

        renglones = self.obtener_renglones(
            pagina
        )

        patron = (
            r"\$\s*"
            r"\d{1,3}"
            r"(?:,\d{3})*"
            r"(?:\.\d{1,2})?"
        )

        for renglon in renglones:

            texto = (
                renglon["izquierda"]
                + " "
                + renglon["contenido"]
            )

            if re.search(
                patron,
                texto
            ):

                self.testar_renglon(
                    pagina,
                    renglon
                )

    # =====================================================
    # CUENTAS
    # =====================================================

    def testar_cuentas(
        self,
        pagina
    ):

        renglones = self.obtener_renglones(
            pagina
        )

        for renglon in renglones:

            texto = self.normalizar(
                renglon["izquierda"]
            )

            if (
                "NUMERO DE CUENTA"
                in texto
                or
                "CUENTA, CONTRATO O POLIZA"
                in texto
            ):

                self.testar_renglon(
                    pagina,
                    renglon
                )

    # =====================================================
    # REGISTRO PÚBLICO
    # =====================================================

    def testar_registro_publico(
        self,
        pagina
    ):

        renglones = self.obtener_renglones(
            pagina
        )

        for indice, renglon in enumerate(
            renglones
        ):

            texto = (
                renglon["izquierda"]
                + " "
                + renglon["contenido"]
            )

            if (
                "DATOS DEL REGISTRO PUBLICO"
                not in texto
                and
                "FOLIO REAL"
                not in texto
            ):

                continue

            self.testar_renglon(
                pagina,
                renglon
            )

            if (
                indice + 1
                <
                len(renglones)
            ):

                siguiente = renglones[
                    indice + 1
                ]

                self.testar_renglon(
                    pagina,
                    siguiente
                )

            return

    # =====================================================
    # TRANSMISOR
    # =====================================================

    def testar_transmisor(
        self,
        pagina
    ):

        renglones = self.obtener_renglones(
            pagina
        )

        for renglon in renglones:

            texto = self.normalizar(
                renglon["izquierda"]
            )

            if (
                "NOMBRE O RAZON SOCIAL DEL TRANSMISOR"
                in texto
            ):

                self.testar_renglon(
                    pagina,
                    renglon
                )

    # =====================================================
    # VEHÍCULOS
    # =====================================================

    def testar_vehiculos(
        self,
        pagina
    ):

        renglones = self.obtener_renglones(
            pagina
        )

        for renglon in renglones:

            texto = self.normalizar(
                renglon["izquierda"]
            )

            if any(
                patron in texto
                for patron in (
                    "NUMERO DE SERIE",
                    "NUMERO DE SERIE O REGISTRO",
                    "SERIE O REGISTRO",
                    "PLACAS",
                    "PLACA",
                )
            ):

                self.testar_renglon(
                    pagina,
                    renglon
                )

    # =====================================================
    # VALORES / SALDOS
    # =====================================================

    def testar_valores(
        self,
        pagina
    ):

        renglones = self.obtener_renglones(
            pagina
        )

        patrones = (
            "VALOR DE ADQUISICION",
            "VALOR DE ADQUISICION DEL VEHICULO",
            "VALOR DE ADQUISICION DEL MUEBLE",
            "SALDO INSOLUTO",
            "SALDO AL 31 DE DICIEMBRE",
            "MONTO ORIGINAL DEL ADEUDO",
            "MONTO ANUAL PAGADO",
        )

        for renglon in renglones:

            texto = self.normalizar(
                renglon["izquierda"]
            )

            if any(
                patron in texto
                for patron in patrones
            ):

                self.testar_renglon(
                    pagina,
                    renglon
                )

    # =====================================================
    # ACLARACIONES
    # =====================================================

    def testar_aclaraciones(
        self,
        pagina
    ):

        renglones = self.obtener_renglones(
            pagina
        )

        for renglon in renglones:

            texto = self.normalizar(
                renglon["izquierda"]
            )

            if (
                "ACLARACIONES"
                not in texto
                and
                "OBSERVACIONES"
                not in texto
            ):

                continue

            if self.es_pie(
                pagina,
                renglon["y"]
            ):

                continue

            self.agregar_rect(
                pagina,
                self.rect_aclaracion(
                    pagina,
                    renglon["y"],
                    self.alto_aclaracion
                )
            )

    # =====================================================
    # APLICAR REGLAS
    # =====================================================

    def aplicar_reglas_directas(
        self,
        documento
    ):

        self.testar_pareja(
            documento
        )

        self.testar_dependientes(
            documento
        )

        for indice, pagina in enumerate(
            documento
        ):

            if indice == 0:

                self.testar_datos_generales(
                    pagina
                )

                self.testar_servidor_publico(
                    pagina
                )

                self.testar_domicilio(
                    pagina
                )

            self.testar_conyuge(
                pagina
            )

            self.testar_montos(
                pagina
            )

            self.testar_cuentas(
                pagina
            )

            self.testar_registro_publico(
                pagina
            )

            self.testar_vehiculos(
                pagina
            )

            self.testar_valores(
                pagina
            )

            self.testar_aclaraciones(
                pagina
            )

            self.testar_transmisor(
                pagina
            )

    # =====================================================
    # GENERAR PDF
    # =====================================================

    def generar_pdf(
        self,
        ruta_pdf,
        campos=None
    ):

        if not ruta_pdf:

            raise ValueError(
                "No se ha proporcionado un PDF."
            )

        if not os.path.exists(
            ruta_pdf
        ):

            raise FileNotFoundError(
                f"No existe el PDF:\n{ruta_pdf}"
            )

        documento = pymupdf.open(
            ruta_pdf
        )

        try:

            self.aplicar_reglas_directas(
                documento
            )

            total = 0

            for pagina in documento:

                anotacion = (
                    pagina.first_annot
                )

                while anotacion:

                    total += 1

                    anotacion = (
                        anotacion.next
                    )

                pagina.apply_redactions()

            print()
            print(
                "=============================="
            )

            print(
                f"REDACCIONES APLICADAS: {total}"
            )

            print(
                "=============================="
            )

            if total == 0:

                raise ValueError(
                    "No se generaron redacciones."
                )

            carpeta = os.path.dirname(
                os.path.abspath(
                    ruta_pdf
                )
            )

            nombre = os.path.basename(
                ruta_pdf
            )

            base = os.path.splitext(
                nombre
            )[0]

            ruta_salida = os.path.join(
                carpeta,
                f"{base}_TESTADO.pdf"
            )

            if os.path.exists(
                ruta_salida
            ):

                try:

                    os.remove(
                        ruta_salida
                    )

                except PermissionError:

                    raise PermissionError(
                        "No se puede reemplazar el PDF "
                        "porque está abierto en otro programa.\n\n"
                        f"{ruta_salida}"
                    )

            documento.save(
                ruta_salida,
                garbage=4,
                deflate=True
            )

            if not os.path.exists(
                ruta_salida
            ):

                raise RuntimeError(
                    "PyMuPDF no creó el archivo de salida."
                )

            tamano = os.path.getsize(
                ruta_salida
            )

            if tamano == 0:

                raise RuntimeError(
                    "El PDF generado tiene tamaño 0."
                )

            print(
                f"Tamaño PDF: {tamano} bytes"
            )

            print(
                "PDF creado correctamente."
            )

            return ruta_salida

        finally:

            documento.close()