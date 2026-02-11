##Valida ID, por tipo
def validarID(id, tipo)-> str:
    if not id:
        return "El ID no puede estar vacío."
    elif tipo == "Nacional":
        if not id.isdigit() or len(id) != 9:
            return "El ID nacional debe ser un número de 9 dígitos."
    elif tipo == "Residente":
        if not id.isdigit() or len(id) != 12:
            return "El ID de residente debe ser un número de 12 caracteres."
    elif tipo == "Pasaporte":
        if not id.isalnum() or len(id) != 9:
            return "El ID de pasaporte debe ser un número alfanumérico de 9 caracteres."
    return None

##Valida nombre
def validarNombre(nombre)-> str:
    if not nombre:
        return "El nombre no puede estar vacío."
    elif not nombre.replace(" ", "").isalpha():
        return "El nombre solo puede contener letras y espacios."
    return None

##Valida Edad
def validarEdad(edad) -> str:
    if not edad:
        return "La edad no puede estar vacía."
    elif not edad.isdigit():
        return "La edad debe ser un número entero."
    elif int(edad) < 0 or int(edad) > 120:
        return "La edad debe estar entre 0 y 120 años."
    return None

##Valida GEnero
def validarGenero(genero) -> str:
    if not genero:
        return "El género no puede estar vacío."
    elif genero.lower() not in ["masculino", "femenino"]:
        return "El género debe ser 'masculino' o 'femenino'."
    return None

##Valida Peso
def validarPeso(peso) -> str:
    if not peso:
        return "El peso no puede estar vacío."
    elif not peso.replace(".", "", 1).isdigit():
        return "El peso debe ser un número."
    elif float(peso) <= 0 or float(peso) > 500:
        return "El peso debe ser un número positivo y menor a 500."
    return None

##Valida Estatura
def validarEstaturaMetros(estatura) -> str:
    if not estatura:
        return "La estatura no puede estar vacía."
    elif not estatura.replace(".", "", 1).isdigit():
        return "La estatura debe ser un número."
    elif float(estatura) <= 0 or float(estatura) > 3:
        return "La estatura debe ser un número positivo y menor a 3 metros."
    return None
