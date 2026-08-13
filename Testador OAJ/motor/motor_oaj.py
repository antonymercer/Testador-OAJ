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
        # RESULTADOS DEL ANÁLISIS
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
        # REINICIAR ESTADO DEL DOCUMENTO
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
            f"Bloques/palabras: {len(self.bloques)}"
        )

        # ======================================
        # MOSTRAR PRIMERA PALABRA
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
            f"Total de filas: {len(self.filas)}"
        )

        print()
        print("==============================")
        print("PRIMERA FILA")
        print("==============================")
        print(
            self.filas[0]
        )

        # ======================================
        # DOCUMENTO CORRECTAMENTE CARGADO
        # ======================================

        self.documento_cargado = True

        return self.filas

    # ==========================================
    # ANALIZAR
    # ==========================================

    def analizar(self):

        # ======================================
        # VALIDAR DOCUMENTO
        # ======================================

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

        # ======================================
        # ASEGURAR QUE SIEMPRE SEA LISTA
        # ======================================

        if resultado is None:
            resultado = []

        self.campos = resultado

        # ======================================
        # MARCAR ANÁLISIS COMO REALIZADO
        # ======================================

        self.analisis_realizado = True

        # ======================================
        # LIMPIAR RESULTADOS ANTERIORES
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
            f"Campos detectados: {len(self.campos)}"
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

        # ======================================
        # VALIDAR ANÁLISIS
        # ======================================

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

        # ======================================
        # REINICIAR CAMPOS A TESTAR
        # ======================================

        self.campos_testar = []

        # ======================================
        # RECORRER CAMPOS
        # ======================================

        for campo in self.campos:

            nombre = campo.get(
                "campo",
                ""
            )

            seccion = campo.get(
                "seccion",
                ""
            )

            # ==================================
            # REGLA FORZADA
            # ==================================

            if campo.get(
                "forzar_testado",
                False
            ):

                accion = "TESTAR"

            else:

                accion = (
                    self.reglas.obtener_accion(
                        seccion,
                        nombre
                    )
                )

            # ==================================
            # GUARDAR ACCIÓN
            # ==================================

            campo["accion"] = accion

            # ==================================
            # AGREGAR A CAMPOS A TESTAR
            # ==================================

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
            if campo.get("accion") == "MOSTRAR"
        )

        ignorar = sum(
            1
            for campo in self.campos
            if campo.get("accion") == "IGNORAR"
        )

        testar = len(
            self.campos_testar
        )

        print()
        print("==============================")
        print("RESUMEN DE REGLAS")
        print("==============================")
        print(
            f"Campos detectados: {len(self.campos)}"
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

        # ======================================
        # VALIDAR PDF
        # ======================================

        if not self.documento_cargado:
            raise Exception(
                "No hay PDF cargado."
            )

        if not self.ruta_pdf:
            raise Exception(
                "No hay una ruta de PDF disponible."
            )

        # ======================================
        # VALIDAR ANÁLISIS
        # ======================================

        if not self.analisis_realizado:
            raise Exception(
                "Primero debe analizar el documento."
            )

        # ======================================
        # VALIDAR REGLAS
        # ======================================

        if not self.reglas_aplicadas:
            raise Exception(
                "Primero deben aplicarse las reglas."
            )

        # ======================================
        # CASO: ANÁLISIS SIN CAMPOS
        # ======================================

        if not self.campos:

            raise Exception(
                "El documento fue analizado, "
                "pero no se detectaron campos.\n\n"
                "Revise el formato del PDF y las "
                "secciones configuradas en el analizador."
            )

        # ======================================
        # CASO: NO HAY CAMPOS PARA TESTAR
        # ======================================

        if not self.campos_testar:

            raise Exception(
                "El documento fue analizado y las reglas "
                "fueron aplicadas, pero no hay campos "
                "marcados para testar."
            )

        # ======================================
        # GENERAR PDF
        # ======================================

        print()
        print("==============================")
        print("GENERANDO PDF")
        print("==============================")
        print(
            f"Campos a testar: "
            f"{len(self.campos_testar)}"
        )

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