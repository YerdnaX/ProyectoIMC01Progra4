import json
from pathlib import Path


def guardarListaPersonas(listaPersonas, rutaDestino: str):
    destino = Path(rutaDestino)
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
        for persona in listaPersonas
    ]

    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return str(archivo)
