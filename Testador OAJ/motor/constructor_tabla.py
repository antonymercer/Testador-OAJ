class ConstructorTabla:

    # ==========================================
    # CONSTRUIR FILAS
    # ==========================================

    def construir(self, palabras):

        filas = []

        if not palabras:
            return filas

        # ======================================
        # Si ya son filas construidas
        # ======================================

        if "descripcion" in palabras[0]:

            return palabras

        # ======================================
        # Ordenar palabras
        # ======================================

        palabras = sorted(
            palabras,
            key=lambda p: (
                p["pagina"],
                round(p["y0"], 1),
                p["x0"]
            )
        )

        fila_actual = []

        pagina_actual = palabras[0]["pagina"]

        y_actual = palabras[0]["y0"]

        tolerancia = 2

        # ======================================
        # CONSTRUIR RENGLONES
        # ======================================

        for palabra in palabras:

            misma_pagina = (
                palabra["pagina"]
                == pagina_actual
            )

            mismo_renglon = (
                abs(
                    palabra["y0"] - y_actual
                ) <= tolerancia
            )

            if misma_pagina and mismo_renglon:

                fila_actual.append(
                    palabra
                )

            else:

                if fila_actual:

                    filas.append(
                        self._crear_fila(
                            fila_actual
                        )
                    )

                fila_actual = [palabra]

                pagina_actual = (
                    palabra["pagina"]
                )

                y_actual = palabra["y0"]

        # ======================================
        # ÚLTIMA FILA
        # ======================================

        if fila_actual:

            filas.append(
                self._crear_fila(
                    fila_actual
                )
            )

        return filas

    # ==========================================
    # CREAR FILA
    # ==========================================

    def _crear_fila(self, palabras):

        palabras = sorted(
            palabras,
            key=lambda p: p["x0"]
        )

        # ======================================
        # UNA SOLA PALABRA
        # ======================================

        if len(palabras) == 1:

            palabra = palabras[0]

            return {

                "descripcion": palabra["texto"],

                "contenido": "",

                "pagina": palabra["pagina"],

                "descripcion_x0": palabra["x0"],
                "descripcion_y0": palabra["y0"],
                "descripcion_x1": palabra["x1"],
                "descripcion_y1": palabra["y1"],

                "palabras": palabras
            }

        # ======================================
        # BUSCAR SEPARACIÓN
        # ======================================

        mayor_espacio = 0

        posicion_corte = None

        for i in range(
            len(palabras) - 1
        ):

            actual = palabras[i]

            siguiente = palabras[i + 1]

            espacio = (
                siguiente["x0"]
                - actual["x1"]
            )

            if espacio > mayor_espacio:

                mayor_espacio = espacio

                posicion_corte = i

        # ======================================
        # DETERMINAR SI ES TABLA
        # ======================================

        if (
            posicion_corte is not None
            and mayor_espacio > 40
        ):

            izquierda = palabras[
                :posicion_corte + 1
            ]

            derecha = palabras[
                posicion_corte + 1:
            ]

        else:

            izquierda = palabras

            derecha = []

        # ======================================
        # TEXTOS
        # ======================================

        descripcion = " ".join(
            p["texto"]
            for p in izquierda
        ).strip()

        contenido = " ".join(
            p["texto"]
            for p in derecha
        ).strip()

        # ======================================
        # CREAR FILA
        # ======================================

        fila = {

            "descripcion": descripcion,

            "contenido": contenido,

            "pagina": palabras[0]["pagina"],

            "palabras": palabras
        }

        # ======================================
        # COORDENADAS DESCRIPCIÓN
        # ======================================

        if izquierda:

            fila["descripcion_x0"] = min(
                p["x0"]
                for p in izquierda
            )

            fila["descripcion_y0"] = min(
                p["y0"]
                for p in izquierda
            )

            fila["descripcion_x1"] = max(
                p["x1"]
                for p in izquierda
            )

            fila["descripcion_y1"] = max(
                p["y1"]
                for p in izquierda
            )

        # ======================================
        # COORDENADAS CONTENIDO
        # ======================================

        if derecha:

            fila["contenido_x0"] = min(
                p["x0"]
                for p in derecha
            )

            fila["contenido_y0"] = min(
                p["y0"]
                for p in derecha
            )

            fila["contenido_x1"] = max(
                p["x1"]
                for p in derecha
            )

            fila["contenido_y1"] = max(
                p["y1"]
                for p in derecha
            )

        return fila