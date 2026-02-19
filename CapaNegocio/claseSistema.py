from datetime import date, datetime
import pandas as pandas
from Entidades.clasePersona import clasePersona
from CapaDatos import claseXML, claseJSON

listaPersonas = []
# Ruta donde se guardan respaldos/archivos del sistema
rutaSistema = claseXML.cargarRutaSistema()


def _parse_fecha(fecha_nac):
    """Convierte fecha en str o date a date, aceptando varios formatos habituales."""
    if isinstance(fecha_nac, date):
        return fecha_nac
    if not fecha_nac:
        return None
    candidatos = ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y", "%m-%d-%Y"]
    for fmt in candidatos:
        try:
            return datetime.strptime(str(fecha_nac), fmt).date()
        except Exception:
            continue
    try:
        # fallback a fromisoformat por si viene con tiempo
        return datetime.fromisoformat(str(fecha_nac)).date()
    except Exception:
        return None


def calcularEdadDesdeFecha(fecha_nac):
    """Calcula la edad desde string o date; retorna None si no se pudo calcular."""
    fecha = _parse_fecha(fecha_nac)
    if not fecha:
        return None
    hoy = date.today()
    return hoy.year - fecha.year - ((hoy.month, hoy.day) < (fecha.month, fecha.day))


def _persona_desde_dict(dato: dict):
    fecha_nacimiento = dato.get("fecha_nacimiento")
    edad = calcularEdadDesdeFecha(fecha_nacimiento)
    if edad is None:
        try:
            edad = int(dato.get("edad") or 0)
        except Exception:
            edad = 0
    try:
        peso = float(dato.get("peso") or 0)
        estatura = float(dato.get("estatura") or 1)
    except Exception:
        return None
    try:
        imc = float(dato.get("imc") or calcularIMC(peso, estatura))
    except Exception:
        imc = calcularIMC(peso, estatura)

    try:
        return clasePersona(
            dato.get("id"),
            dato.get("nombre"),
            edad,
            dato.get("genero"),
            peso,
            estatura,
            imc,
            dato.get("estado"),
            fecha_nacimiento=fecha_nacimiento,
        )
    except Exception:
        return None


def cargaAlAbrirDesdeJSON():
    if not rutaSistema:
        return
    datos = claseJSON.cargarListaPersonas(rutaSistema)
    if not datos:
        return
    personas = []
    for dato in datos:
        persona = _persona_desde_dict(dato)
        if persona:
            personas.append(persona)
    if personas:
        global listaPersonas
        listaPersonas = personas


cargaAlAbrirDesdeJSON()


##Agrega Persona a la lista, ya la info viene validada :D
def agregarPersona(id, nombre, genero, peso, estatura, fecha_nacimiento):
    edad = calcularEdadDesdeFecha(fecha_nacimiento) or 0
    imc = calcularIMC(peso, estatura)
    estadoAsignado = estadoIMC(genero, edad, estatura, peso, genero, imc)
    personaNueva = clasePersona(
        id, nombre, edad, genero, peso, estatura, imc, estadoAsignado, fecha_nacimiento=fecha_nacimiento
    )
    listaPersonas.append(personaNueva)
    
##Elimina persona de la lista
def eliminarPersona(id):
    global listaPersonas
    listaPersonas = [p for p in listaPersonas if p.id != id]

##Funcion q se llama desde para guardar ruta sistema, usa variable global para tenerla siempre en memoria :D
def establecerRutaSistema(ruta: str):
    global rutaSistema
    claseXML.guardarRutaSistema(ruta)
    rutaSistema = ruta
    return ruta

##Retorna la ruta seleccionada del sistema, si no retorna none
def obtenerRutaSistema():
    return claseXML.cargarRutaSistema()

##De objeto persona a diccionario
def personaToDict(persona: clasePersona):
    return {
        "id": persona.id,
        "nombre": persona.nombre,
        "edad": persona.edad,
        "fecha_nacimiento": persona.fecha_nacimiento,
        "genero": persona.genero,
        "peso": persona.peso,
        "estatura": persona.estatura,
        "imc": persona.imcCalculado,
        "estado": persona.estado,
    }

## Funcion para guardar JSON-XML
def guardarInformacionArchivos():
    ruta = obtenerRutaSistema()
    if not ruta:
        raise ValueError("No hay ruta del sistema configurada. Configure una carpeta antes de guardar.")
    archivo_json = claseJSON.guardarListaPersonas(listaPersonas, ruta)
    archivo_xml = claseXML.guardarListaPersonas(listaPersonas, ruta)
    return archivo_json, archivo_xml

##Carga desde respaldo XML, retorna la cantidad de objetos cargados a memoria
def cargarDesdeRespaldo():
    ruta = obtenerRutaSistema()
    if not ruta:
        raise ValueError("No hay ruta del sistema configurada. Configure una carpeta antes de cargar.")
    datos = claseXML.cargarListaPersonas(ruta)
    if datos is None:
        raise FileNotFoundError("No se encontró respaldo_personas.xml en la ruta configurada.")

    personas = []
    for dato in datos:
        persona = _persona_desde_dict(dato)
        if persona:
            personas.append(persona)

    global listaPersonas
    listaPersonas = personas
    return len(personas)
    
##Retorna el IMC de una persona
def calcularIMC(peso, estatura) -> float:
    imc = peso / (estatura ** 2)
    return imc

##Retorna el estado del IMC
def estadoIMC(sexo, edad, estatura, peso, genero, imc) -> str:
    generoAsignado = genero.lower()
    imc = calcularIMC(peso, estatura)
    if edad < 12:
        return estadoIMCnino(imc, generoAsignado)
    elif edad >= 12 and edad < 18:
        return estadoIMCadolecente(imc, generoAsignado)
    else:
        return estadoIMCadulto(imc, generoAsignado)

##Retorna estadoIMC para niños   
def estadoIMCnino(imc, genero)-> str:
    if genero == "masculino":
        if imc < 14.5:
            return "Bajo peso"
        elif imc >= 14.5 and imc < 18.5:
            return "Peso normal"
        elif imc >= 18.5 and imc < 25:
            return "Sobrepeso"
        else:
            return "Obesidad"
    elif genero == "femenino":
        if imc < 14:
            return "Bajo peso"
        elif imc >= 14 and imc < 18:
            return "Peso normal"
        elif imc >= 18 and imc < 24:
            return "Sobrepeso"
        else:
            return "Obesidad"

##Retorna estadoIMC para adolescentes
def estadoIMCadolecente(imc, genero) -> str:
    if genero == "masculino":
        if imc < 17.5:
            return "Bajo peso"
        elif imc >= 17.5 and imc < 22.5:
            return "Peso normal"
        elif imc >= 22.5 and imc < 27.5:
            return "Sobrepeso"
        else:
            return "Obesidad"
    elif genero == "femenino":
        if imc < 16.5:
            return "Bajo peso"
        elif imc >= 16.5 and imc < 21.5:
            return "Peso normal"
        elif imc >= 21.5 and imc < 26.5:
            return "Sobrepeso"
        else:
            return "Obesidad"

##Retorna estadoIMC para adultos  
def estadoIMCadulto(imc, genero) -> str:
    if genero == "masculino":
        if imc < 18.5:
            return "Bajo peso"
        elif imc >= 18.5 and imc < 25:
            return "Peso normal"
        elif imc >= 25 and imc < 30:
            return "Sobrepeso"
        else:
            return "Obesidad"
    elif genero == "femenino":
        if imc < 18.5:
            return "Bajo peso"
        elif imc >= 18.5 and imc < 25:
            return "Peso normal"
        elif imc >= 25 and imc < 30:
            return "Sobrepeso"
        else:
            return "Obesidad"


#  Reportes

##Genera el dataframe a partir de la lista de personas pa reportes 
def dataframePersonas():
    if not listaPersonas:
        return pandas.DataFrame(columns=["id", "nombre", "edad", "genero", "peso", "estatura", "imc", "estado"])
    return pandas.DataFrame(
        [
            {
                "id": p.id,
                "nombre": p.nombre,
                "edad": p.edad,
                "genero": p.genero,
                "peso": p.peso,
                "estatura": p.estatura,
                "imc": p.imcCalculado,
                "estado": p.estado,
            }
            for p in listaPersonas
        ]
    )

##Genera el reporte de cantidad y promedio de IMC por estado
def reporteCategoriaIMC():
    df = dataframePersonas()
    if df.empty:
        return pandas.DataFrame({"estado": [], "cantidad": [], "imc_promedio": []})
    resumen = (
        df.groupby("estado")
        .agg(cantidad=("id", "count"), imc_promedio=("imc", "mean"))
        .reset_index()
        .sort_values(by="estado")
    )
    resumen.loc[len(resumen)] = ["TOTAL", resumen["cantidad"].sum(), resumen["imc_promedio"].mean()]
    return resumen

##Genera el reporte de cantidad y promedio de IMC por grupo de edad
def reporteGrupoEdad():
    df = dataframePersonas()
    if df.empty:
        return pandas.DataFrame({"grupo_edad": [], "cantidad": [], "imc_promedio": []})

    def bucket(edad):
        if edad < 12:
            return "Ninez (<12)"
        elif edad < 18:
            return "Adolescencia (12-17)"
        elif edad < 60:
            return "Adulto (18-59)"
        else:
            return "Adulto mayor (60+)"

    df["grupo_edad"] = df["edad"].apply(bucket)
    resumen = (
        df.groupby("grupo_edad")
        .agg(cantidad=("id", "count"), imc_promedio=("imc", "mean"))
        .reset_index()
        .sort_values(by="grupo_edad")
    )
    resumen.loc[len(resumen)] = ["TOTAL", resumen["cantidad"].sum(), resumen["imc_promedio"].mean()]
    return resumen


##Genera el reporte de cantidad y promedio de IMC por genero
def reporte_por_genero():
    df = dataframePersonas()
    if df.empty:
        return pandas.DataFrame({"genero": [], "cantidad": [], "imc_promedio": []})
    resumen = (
        df.groupby("genero")
        .agg(cantidad=("id", "count"), imc_promedio=("imc", "mean"))
        .reset_index()
        .sort_values(by="genero")
    )
    resumen.loc[len(resumen)] = ["TOTAL", resumen["cantidad"].sum(), resumen["imc_promedio"].mean()]
    return resumen
