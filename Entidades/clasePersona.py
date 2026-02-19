from datetime import date, datetime


class clasePersona:
    def __init__(self, id, nombre, edad, genero, peso, estatura, imcCalculado, estado, fecha_nacimiento=None):
        self.id = id
        self.nombre = nombre
        self.fecha_nacimiento = fecha_nacimiento
        # Mantiene compatibilidad: si viene la edad se usa; si no, se calcula desde la fecha
        self.edad = edad if edad is not None else self._edad_desde_fecha(fecha_nacimiento)
        self.genero = genero
        self.peso = peso
        self.estatura = estatura
        self.imcCalculado = imcCalculado
        self.estado = estado

    # Gets and sets para cada atributo
    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, nuevoId):
        self._id = nuevoId

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, nuevoNombre):
        self._nombre = nuevoNombre

    @property
    def fecha_nacimiento(self):
        return self._fecha_nacimiento

    @fecha_nacimiento.setter
    def fecha_nacimiento(self, fecha):
        self._fecha_nacimiento = fecha

    @property
    def edad(self):
        return self._edad

    @edad.setter
    def edad(self, nuevaEdad):
        self._edad = nuevaEdad

    @property
    def genero(self):
        return self._genero

    @genero.setter
    def genero(self, nuevoGenero):
        self._genero = nuevoGenero

    @property
    def peso(self):
        return self._peso

    @peso.setter
    def peso(self, nuevoPeso):
        self._peso = nuevoPeso

    @property
    def estatura(self):
        return self._estatura

    @estatura.setter
    def estatura(self, nuevaEstatura):
        self._estatura = nuevaEstatura

    @property
    def imcCalculado(self):
        return self._imcCalculado

    @imcCalculado.setter
    def imcCalculado(self, nuevoImcCalculado):
        self._imcCalculado = nuevoImcCalculado

    @property
    def estado(self):
        return self._estado

    @estado.setter
    def estado(self, nuevoEstado):
        self._estado = nuevoEstado

    @staticmethod
    def _edad_desde_fecha(fecha_nacimiento):
        if not fecha_nacimiento:
            return None
        try:
            if isinstance(fecha_nacimiento, str):
                fecha = datetime.fromisoformat(fecha_nacimiento).date()
            elif isinstance(fecha_nacimiento, date):
                fecha = fecha_nacimiento
            else:
                return None
            hoy = date.today()
            return hoy.year - fecha.year - ((hoy.month, hoy.day) < (fecha.month, fecha.day))
        except Exception:
            return None

    def __str__(self):
        return (
            f"ID: {self.id}, Nombre: {self.nombre}, Edad: {self.edad}, "
            f"Genero: {self.genero}, Peso: {self.peso}, Estatura: {self.estatura}, "
            f"IMC calculado: {self.imcCalculado}, Estado: {self.estado}, "
            f"Fecha nacimiento: {self.fecha_nacimiento}"
        )
