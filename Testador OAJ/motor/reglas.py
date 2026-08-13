class Reglas:

    def obtener_accion(self, seccion, nombre):

        # =====================================================
        # DATOS GENERALES
        # =====================================================

        if seccion == "Datos Generales":

            reglas = {

                "Nombre(s)": "IGNORAR",
                "Primer apellido": "IGNORAR",
                "Segundo apellido": "IGNORAR",

                "CURP": "TESTAR",
                "RFC": "TESTAR",
                "Homoclave": "TESTAR",

                "Correo electrónico institucional": "MOSTRAR",

                "Correo electrónico personal / Alterno": "TESTAR",

                "Número celular personal": "TESTAR",

                "Situación personal / estado civil": "TESTAR",

                "** Régimen matrimonial": "TESTAR",

                "País de nacimiento": "TESTAR",

                "Nacionalidad (es)": "TESTAR",

                "¿Te desempeñaste como servidor público el año inmediato anterior?":
                    "TESTAR",

            }

            return reglas.get(
                nombre,
                "IGNORAR"
            )


        # =====================================================
        # DOMICILIO
        # =====================================================

        if seccion == "Domicilio del declarante":

            return "TESTAR"


        # =====================================================
        # DATOS CURRICULARES
        # =====================================================

        if seccion == "Datos curriculares del declarante":

            return "IGNORAR"


        # =====================================================
        # EMPLEO ACTUAL
        # =====================================================

        if seccion == "Datos del empleo, cargo o comisión actual":

            if nombre == "Número de expediente del declarante":

                return "TESTAR"

            return "IGNORAR"


        # =====================================================
        # DATOS DE LA PAREJA
        # =====================================================

        if seccion == "Datos de la pareja":

            return "TESTAR"


        # =====================================================
        # DEPENDIENTE ECONÓMICO
        # =====================================================

        if seccion == "Datos del dependiente económico":

            return "TESTAR"


        # =====================================================
        # CUALQUIER OTRA SECCIÓN
        # =====================================================

        return "IGNORAR"