from motor.lector_pdf import LectorPDF
from motor.analizador import Analizador
from motor.reglas import Reglas
from motor.redactor import Redactor
from motor.constructor_tabla import ConstructorTabla


class MotorOAJ:

    def __init__(self):

        # ==========================================
        # COMPONENTES DEL MOTOR
        # ==========================================

        self.lector = LectorPDF()
        self.analizador = Analizador()
        self.reglas = Reglas()
        self.redactor = Redactor()
        self.constructor = ConstructorTabla()

        # ==========================================
        # ESTADO DEL DOCUMENTO
        # ==========================================

        self.ruta_pdf = ""

        self.bloques = []
        self.filas = []

        # ==========================================
        # RESULTADOS
        # ==========================================

        self.campos = []
        self.campos_testar = []

        # ==========================================
        # ESTADOS
        # ==========================================

        self.documento_cargado = False
        self.analisis_realizado = False
        self.reglas_aplicadas = False

    # ==========================================
    # CARGAR PDF
    # ==========================================

    def cargar_pdf(self, ruta_pdf):

        if not ruta_pdf:
            raise Exception(
                "No se proporcionó una ruta de PDF."
            )

        # ======================================
        # REINICIAR ESTADO
        # ======================================

        self.ruta_pdf = ruta_pdf

        self.bloques = []
        self.filas = []

        self.campos = []
        self.campos_testar = []

        self.documento_cargado = False
        self.analisis_realizado = False
        self.reglas_aplicadas = False

        # ======================================
        # LEER PDF
        # ======================================

        self.bloques = self.lector.leer_pdf(
            ruta_pdf
        )

        if not self.bloques:

            raise Exception(
                "No se encontraron palabras en el PDF."
            )

        print()
        print("==============================")
        print("PDF CARGADO")
        print("==============================")

        print(
            f"Archivo: {ruta_pdf}"
        )

        print(
            f"Bloques/palabras: "
            f"{len(self.bloques)}"
        )

        # ======================================
        # PRIMERA PALABRA
        # ======================================

        print()
        print("==============================")
        print("PRIMERA PALABRA")
        print("==============================")

        print(
            self.bloques[0]
        )

        # ======================================
        # CONSTRUIR FILAS
        # ======================================

        self.filas = self.constructor.construir(
            self.bloques
        )

        if not self.filas:

            raise Exception(
                "No se pudieron construir las filas."
            )

        print()
        print("==============================")
        print("FILAS CONSTRUIDAS")
        print("==============================")

        print(
            f"Total de filas: "
            f"{len(self.filas)}"
        )

        # ======================================
        # PRIMERA FILA
        # ======================================

        print()
        print("==============================")
        print("PRIMERA FILA")
        print("==============================")

        print(
            self.filas[0]
        )

        # ======================================
        # DOCUMENTO CARGADO
        # ======================================

        self.documento_cargado = True

        return self.filas

    # ==========================================
    # ANALIZAR
    # ==========================================

    def analizar(self):

        if not self.documento_cargado:

            raise Exception(
                "Primero debe cargar un PDF."
            )

        if not self.filas:

            raise Exception(
                "El PDF no contiene filas para analizar."
            )

        print()
        print("==============================")
        print("INICIANDO ANÁLISIS")
        print("==============================")

        # ======================================
        # EJECUTAR ANALIZADOR
        # ======================================

        resultado = self.analizador.analizar(
            self.filas
        )

        if resultado is None:
            resultado = []

        self.campos = resultado

        # ======================================
        # MARCAR ANÁLISIS
        # ======================================

        self.analisis_realizado = True

        # ======================================
        # LIMPIAR REGLAS ANTERIORES
        # ======================================

        self.campos_testar = []
        self.reglas_aplicadas = False

        # ======================================
        # RESUMEN
        # ======================================

        print()
        print("==============================")
        print("RESULTADO DEL ANÁLISIS")
        print("==============================")

        print(
            f"Campos detectados: "
            f"{len(self.campos)}"
        )

        if not self.campos:

            print(
                "ADVERTENCIA: "
                "El análisis terminó sin detectar campos."
            )

        print("==============================")
        print()

        return self.campos

    # ==========================================
    # APLICAR REGLAS
    # ==========================================

    def aplicar_reglas(self):

        if not self.documento_cargado:

            raise Exception(
                "Primero debe cargar un PDF."
            )

        if not self.analisis_realizado:

            raise Exception(
                "Primero debe analizar el documento."
            )

        print()
        print("==============================")
        print("APLICANDO REGLAS")
        print("==============================")

        self.campos_testar = []

        # ======================================
        # SECCIONES QUE NO SE TESTAN
        # ======================================

        secciones_ignorar = {
            "Datos Generales",
            "Domicilio del declarante",
            "Datos curriculares del declarante",
            "Datos del empleo, cargo o comisión actual",
        }

        # ======================================
        # SECCIONES QUE SE TESTAN COMPLETAS
        # ======================================

        secciones_todo = {
            "Datos de la pareja",
            "Datos del dependiente económico",
            "Datos del cónyuge",
        }

        # ======================================
        # SECCIONES SENSIBLES
        # ======================================

        secciones_sensibles = {
            "Ingresos netos del declarante, pareja y/o dependientes económicos",
            "Bienes inmuebles",
            "Bienes muebles",
            "Vehículos",
            "Inversiones, cuentas bancarias y otro tipo de valores / activos",
            "Adeudos / pasivos / créditos / tarjetas de crédito o departamentales",
        }

        # ======================================
        # RECORRER CAMPOS
        # ======================================

        for campo in self.campos:

            nombre = str(
                campo.get(
                    "campo",
                    ""
                )
            )

            valor = str(
                campo.get(
                    "valor",
                    ""
                )
            )

            seccion = str(
                campo.get(
                    "seccion",
                    ""
                )
            )

            nombre_u = nombre.upper()
            valor_u = valor.upper()

            accion = "IGNORAR"

            # ==================================
            # DATOS GENERALES
            # ==================================

            if seccion == "Datos Generales":

                if (
                    "SERVIDOR PÚBLICO"
                    in nombre_u
                    or
                    "SERVIDOR PUBLICO"
                    in nombre_u
                ):

                    accion = "TESTAR"

            # ==================================
            # SECCIONES IGNORADAS
            # ==================================

            elif seccion in secciones_ignorar:

                accion = "IGNORAR"

            # ==================================
            # PAREJA / DEPENDIENTE / CÓNYUGE
            # ==================================

            elif seccion in secciones_todo:

                accion = "TESTAR"

            # ==================================
            # SECCIONES SENSIBLES
            # ==================================

            elif seccion in secciones_sensibles:

                # --------------------------------
                # CÓNYUGE
                # --------------------------------

                if (
                    "CÓNYUGE" in nombre_u
                    or
                    "CONYUGE" in nombre_u
                    or
                    "CÓNYUGE" in valor_u
                    or
                    "CONYUGE" in valor_u
                ):

                    accion = "TESTAR"

                # --------------------------------
                # ACLARACIONES
                # --------------------------------

                elif (
                    "ACLARACIONES" in nombre_u
                    or
                    "OBSERVACIONES" in nombre_u
                ):

                    accion = "TESTAR"

                # --------------------------------
                # FOLIO
                # --------------------------------

                elif (
                    "FOLIO" in nombre_u
                    or
                    "DATOS DEL REGISTRO" in nombre_u
                ):

                    accion = "TESTAR"

                # --------------------------------
                # NOMBRE TRANSMISOR
                # --------------------------------

                elif (
                    seccion == "Bienes inmuebles"
                    and (
                        "NOMBRE O RAZON SOCIAL DEL TRANSMISOR"
                        in nombre_u
                        or
                        "NOMBRE O RAZÓN SOCIAL DEL TRANSMISOR"
                        in nombre_u
                    )
                ):

                    accion = "TESTAR"

                # --------------------------------
                # MONTOS
                # --------------------------------

                elif (
                    "$" in nombre_u
                    or
                    "$" in valor_u
                    or
                    "MONTO" in nombre_u
                    or
                    "SALDO INSOLUTO" in nombre_u
                    or
                    "VALOR DE ADQUISICION" in nombre_u
                    or
                    "VALOR DE ADQUISICIÓN" in nombre_u
                ):

                    accion = "TESTAR"

            # ==================================
            # GUARDAR ACCIÓN
            # ==================================

            campo["accion"] = accion

            if accion == "TESTAR":

                self.campos_testar.append(
                    campo
                )

            # ==================================
            # DEPURACIÓN
            # ==================================

            print(
                f"{seccion} | "
                f"{nombre} -> {accion}"
            )

            print(
                f"    página={campo.get('pagina')} "
                f"x={campo.get('x')} "
                f"y={campo.get('y')} "
                f"ancho={campo.get('ancho')} "
                f"alto={campo.get('alto')}"
            )

        # ======================================
        # ESTADO
        # ======================================

        self.reglas_aplicadas = True

        # ======================================
        # RESUMEN
        # ======================================

        mostrar = sum(
            1
            for campo in self.campos
            if campo.get(
                "accion"
            ) == "MOSTRAR"
        )

        ignorar = sum(
            1
            for campo in self.campos
            if campo.get(
                "accion"
            ) == "IGNORAR"
        )

        testar = len(
            self.campos_testar
        )

        print()
        print("==============================")
        print("RESUMEN DE REGLAS")
        print("==============================")

        print(
            f"Campos detectados: "
            f"{len(self.campos)}"
        )

        print(
            f"TESTAR: {testar}"
        )

        print(
            f"MOSTRAR: {mostrar}"
        )

        print(
            f"IGNORAR: {ignorar}"
        )

        print("==============================")
        print()

        return self.campos

    # ==========================================
    # GENERAR PDF
    # ==========================================

    def generar_pdf(self):

        if not self.documento_cargado:

            raise Exception(
                "No hay PDF cargado."
            )

        if not self.ruta_pdf:

            raise Exception(
                "No hay una ruta de PDF disponible."
            )

        if not self.analisis_realizado:

            raise Exception(
                "Primero debe analizar el documento."
            )

        if not self.reglas_aplicadas:

            raise Exception(
                "Primero deben aplicarse las reglas."
            )

        # ======================================
        # SIN CAMPOS
        # ======================================

        if not self.campos:

            raise Exception(
                "El documento fue analizado, "
                "pero no se detectaron campos."
            )

        # ======================================
        # SIN CAMPOS A TESTAR
        # ======================================

        if not self.campos_testar:

            raise Exception(
                "El documento fue analizado y las reglas "
                "fueron aplicadas, pero no hay campos "
                "marcados para testar."
            )

        print()
        print("==============================")
        print("GENERANDO PDF")
        print("==============================")

        print(
            f"Campos a testar: "
            f"{len(self.campos_testar)}"
        )

        # ======================================
        # REDACTOR
        # ======================================

        ruta = self.redactor.generar_pdf(
            self.ruta_pdf,
            self.campos
        )

        print(
            f"PDF generado: {ruta}"
        )

        print("==============================")
        print()

        return ruta

    # ==========================================
    # REINICIAR MOTOR
    # ==========================================

    def reiniciar(self):

        self.ruta_pdf = ""

        self.bloques = []
        self.filas = []

        self.campos = []
        self.campos_testar = []

        self.documento_cargado = False
        self.analisis_realizado = False
        self.reglas_aplicadas = False