class clasePersona:
    def __init__(self, id, nombre, edad, genero, peso, estatura, imcCalculado, estado):
        self.id = id
        self.nombre = nombre
        self.edad = edad
        self.genero = genero
        self.peso = peso
        self.estatura = estatura
        self.imcCalculado = imcCalculado
        self.estado = estado
        
    
    ## Gets and sets para cada atributo
    
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

    def __str__(self):
        return (
            f"ID: {self.id}, Nombre: {self.nombre}, Edad: {self.edad}, "
            f"Género: {self.genero}, Peso: {self.peso}, Estatura: {self.estatura}, "
            f"IMC calculado: {self.imcCalculado}, Estado: {self.estado}"
        )
    
    
