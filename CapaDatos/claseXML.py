from pathlib import Path
import xml.etree.ElementTree as ET


ArchivoConfiguracionSistema = Path(__file__).resolve().parent.parent / "configuracionSistema.xml"


def guardarRutaSistema(ruta: str):
    ArchivoConfiguracionSistema.parent.mkdir(parents=True, exist_ok=True)
    root = ET.Element("configuracion")
    ET.SubElement(root, "rutasistema").text = ruta
    tree = ET.ElementTree(root)
    tree.write(ArchivoConfiguracionSistema, encoding="utf-8", xml_declaration=True)


def cargarRutaSistema():
    if not ArchivoConfiguracionSistema.exists():
        return None
    try:
        tree = ET.parse(ArchivoConfiguracionSistema)
        root = tree.getroot()
        nodo = root.find("rutasistema")
        return nodo.text if nodo is not None else None
    except Exception:
        return None


def guardarListaPersonas(lista_personas, ruta_destino: str):
    """
    Guarda la lista de personas en un archivo XML en la ruta indicada.
    Archivo: respaldo_personas.xml
    """
    destino = Path(ruta_destino)
    destino.mkdir(parents=True, exist_ok=True)
    archivo = destino / "respaldo_personas.xml"

    root = ET.Element("personas")
    for persona in lista_personas:
        nodo = ET.SubElement(root, "persona")
        ET.SubElement(nodo, "id").text = str(persona.id)
        ET.SubElement(nodo, "nombre").text = str(persona.nombre)
        ET.SubElement(nodo, "edad").text = str(persona.edad)
        ET.SubElement(nodo, "genero").text = str(persona.genero)
        ET.SubElement(nodo, "peso").text = str(persona.peso)
        ET.SubElement(nodo, "estatura").text = str(persona.estatura)
        ET.SubElement(nodo, "imc").text = str(persona.imcCalculado)
        ET.SubElement(nodo, "estado").text = str(persona.estado)

    tree = ET.ElementTree(root)
    tree.write(archivo, encoding="utf-8", xml_declaration=True)
    return str(archivo)


def cargarListaPersonas(ruta_origen: str):
    """
    Lee respaldo_personas.xml en la ruta indicada y devuelve lista de diccionarios.
    """
    archivo = Path(ruta_origen) / "respaldo_personas.xml"
    if not archivo.exists():
        return None
    tree = ET.parse(archivo)
    root = tree.getroot()
    personas = []
    for nodo in root.findall("persona"):
        personas.append(
            {
                "id": nodo.findtext("id"),
                "nombre": nodo.findtext("nombre"),
                "edad": nodo.findtext("edad"),
                "genero": nodo.findtext("genero"),
                "peso": nodo.findtext("peso"),
                "estatura": nodo.findtext("estatura"),
                "imc": nodo.findtext("imc"),
                "estado": nodo.findtext("estado"),
            }
        )
    return personas
