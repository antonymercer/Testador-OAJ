from motor.lector_pdf import LectorPDF
from motor.analizador import Analizador
from motor.reglas import Reglas
from motor.redactor import Redactor
from motor.constructor_tabla import ConstructorTabla


class MotorOAJ:

    def __init__(self):

        self.lector = LectorPDF()

        self.analizador = Analizador()

        self.reglas = Reglas()

        self.redactor = Redactor()

        self.constructor = ConstructorTabla()

        self.ruta_pdf = ""

        self.bloques = []

        self.filas = []

        self.campos = []

    # ==========================================
    # CARGAR PDF
    # ==========================================

    def cargar_pdf(self, ruta_pdf):

        self.ruta_pdf = ruta_pdf

        self.bloques = self.lector.leer_pdf(
            ruta_pdf
        )

        if not self.bloques:

            raise Exception(
                "No se encontraron palabras en el PDF."
            )

        print()
        print("==============================")
        print("PRIMERA PALABRA")
        print("==============================")
        print(self.bloques[0])

        self.filas = self.constructor.construir(
            self.bloques
        )

        if not self.filas:

            raise Exception(
                "No se pudieron construir las filas."
            )

        print()
        print("==============================")
        print("PRIMERA FILA")
        print("==============================")
        print(self.filas[0])

        return self.filas

    # ==========================================
    # ANALIZAR
    # ==========================================

    def analizar(self):

        if not self.filas:

            raise Exception(
                "Primero debe cargar un PDF."
            )

        self.campos = (
            self.analizador.analizar(
                self.filas
            )
        )

        return self.campos

    # ==========================================
    # APLICAR REGLAS
    # ==========================================

    def aplicar_reglas(self):

        print()
        print("==============================")
        print("REGLAS APLICADAS")
        print("==============================")

        for campo in self.campos:

            nombre = campo["campo"]

            seccion = campo["seccion"]

            accion = self.reglas.obtener_accion(
                seccion,
                nombre
            )

            campo["accion"] = accion

            print(
                f"{seccion} | "
                f"{nombre} -> {accion}"
            )
            
            print(
                f"    x={campo.get('x')} "
                f"y={campo.get('y')} "
                f"ancho={campo.get('ancho')} "
                f"alto={campo.get('alto')}"
            )

        print("==============================")
        print()

        return self.campos

    # ==========================================
    # GENERAR PDF
    # ==========================================

    def generar_pdf(self):

        if not self.ruta_pdf:

            raise Exception(
                "No hay PDF cargado."
            )

        if not self.campos:

            raise Exception(
                "Primero analiza el documento."
            )

        return self.redactor.generar_pdf(

            self.ruta_pdf,

            self.campos

        )