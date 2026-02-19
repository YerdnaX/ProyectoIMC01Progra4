from datetime import date, datetime

def _parse_fecha(fecha_txt):
    if not fecha_txt:
        return None
    candidatos = ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y", "%m-%d-%Y"]
    for fmt in candidatos:
        try:
            return datetime.strptime(str(fecha_txt), fmt).date()
        except Exception:
            continue
    try:
        return datetime.fromisoformat(str(fecha_txt)).date()
    except Exception:
        return None


##Valida ID, por tipo
def validarID(id, tipo) -> str:
    if not id:
        return "El ID no puede estar vac\u00edo."
    elif tipo == "Nacional":
        if not id.isdigit() or len(id) != 9:
            return "El ID nacional debe ser un n\u00famero de 9 d\u00edgitos."
    elif tipo == "Residente":
        if not id.isdigit() or len(id) != 12:
            return "El ID de residente debe ser un n\u00famero de 12 caracteres."
    elif tipo == "Pasaporte":
        if not id.isalnum() or len(id) != 9:
            return "El ID de pasaporte debe ser un n\u00famero alfanum\u00e9rico de 9 caracteres."
    return None


##Valida nombre
def validarNombre(nombre) -> str:
    if not nombre:
        return "El nombre no puede estar vac\u00edo."
    elif not nombre.replace(" ", "").isalpha():
        return "El nombre solo puede contener letras y espacios."
    return None


##Valida fecha de nacimiento
def validarFechaNacimiento(fecha_txt) -> str:
    if not fecha_txt:
        return "La fecha de nacimiento no puede estar vac\u00eda."
    fecha = _parse_fecha(fecha_txt)
    if not fecha:
        return "La fecha de nacimiento no tiene un formato v\u00e1lido (AAAA-MM-DD o DD/MM/AAAA)."

    hoy = date.today()
    if fecha > hoy:
        return "La fecha de nacimiento no puede ser futura."
    edad = hoy.year - fecha.year - ((hoy.month, hoy.day) < (fecha.month, fecha.day))
    if edad < 0 or edad > 120:
        return "La edad calculada debe estar entre 0 y 120 a\u00f1os."
    return None


##Valida G\u00c9nero
def validarGenero(genero) -> str:
    if not genero:
        return "El g\u00e9nero no puede estar vac\u00edo."
    elif genero.lower() not in ["masculino", "femenino"]:
        return "El g\u00e9nero debe ser 'masculino' o 'femenino'."
    return None


##Valida Peso
def validarPeso(peso) -> str:
    if not peso:
        return "El peso no puede estar vac\u00edo."
    elif not peso.replace(".", "", 1).isdigit():
        return "El peso debe ser un n\u00famero."
    elif float(peso) <= 0 or float(peso) > 500:
        return "El peso debe ser un n\u00famero positivo y menor a 500."
    return None


##Valida Estatura
def validarEstaturaMetros(estatura) -> str:
    if not estatura:
        return "La estatura no puede estar vac\u00eda."
    elif not estatura.replace(".", "", 1).isdigit():
        return "La estatura debe ser un n\u00famero."
    elif float(estatura) <= 0 or float(estatura) > 3:
        return "La estatura debe ser un n\u00famero positivo y menor a 3 metros."
    return None
