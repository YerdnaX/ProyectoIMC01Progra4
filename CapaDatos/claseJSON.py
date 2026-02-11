import json
from pathlib import Path


def guardarListaPersonas(lista_personas, ruta_destino: str):
    destino = Path(ruta_destino)
    destino.mkdir(parents=True, exist_ok=True)
    archivo = destino / "respaldoPrincipalSistema.json"

    data = [
        {
            "id": persona.id,
            "nombre": persona.nombre,
            "edad": persona.edad,
            "genero": persona.genero,
            "peso": persona.peso,
            "estatura": persona.estatura,
            "imc": persona.imcCalculado,
            "estado": persona.estado,
        }
        for persona in lista_personas
    ]

    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return str(archivo)
