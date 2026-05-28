import json
import anthropic
from pathlib import Path
from datetime import datetime

client = anthropic.Anthropic()

def _ruta(nombre: str) -> Path:
    return Path(__file__).parent / "clientes" / f"{nombre.replace(' ', '_').lower()}.json"

def cargar_memoria(nombre: str) -> dict:
    ruta = _ruta(nombre)
    if ruta.exists():
        with open(ruta) as f:
            return json.load(f)
    return {
        "nombre": nombre,
        "posts_publicados": [],
        "frases_caracteristicas": [],
        "temas_exitosos": [],
        "temas_fallidos": [],
        "estilo_aprendido": "",
        "referencias_personales": [],
        "total_posts": 0
    }

def guardar_memoria(memoria: dict):
    ruta = _ruta(memoria["nombre"])
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with open(ruta, "w") as f:
        json.dump(memoria, f, ensure_ascii=False, indent=2)

def registrar_post(nombre: str, post: str, engagement: dict = None):
    memoria = cargar_memoria(nombre)
    entrada = {
        "fecha": datetime.now().strftime("%Y-%m-%d"),
        "post": post,
        "engagement": engagement or {"likes": 0, "comentarios": 0, "reposts": 0}
    }
    memoria["posts_publicados"].append(entrada)
    memoria["total_posts"] += 1

    # Cada 5 posts, analizar y actualizar el estilo aprendido
    if memoria["total_posts"] % 5 == 0:
        memoria = _analizar_estilo(memoria)

    guardar_memoria(memoria)

def _analizar_estilo(memoria: dict) -> dict:
    if len(memoria["posts_publicados"]) < 3:
        return memoria

    posts_texto = "\n\n---\n\n".join([p["post"] for p in memoria["posts_publicados"][-20:]])

    # Identificar posts exitosos
    posts_con_engagement = [
        p for p in memoria["posts_publicados"]
        if p["engagement"]["likes"] + p["engagement"]["comentarios"] > 0
    ]

    prompt = f"""Analiza estos posts de LinkedIn de {memoria['nombre']} y extrae:

POSTS:
{posts_texto}

Responde en JSON con exactamente esta estructura:
{{
  "estilo_aprendido": "descripción detallada de su voz, tono, estructura de posts, longitud típica, uso de emojis, etc.",
  "frases_caracteristicas": ["frase1", "frase2", "frase3"],
  "referencias_personales": ["referencia1", "referencia2"],
  "temas_exitosos": ["tema1", "tema2"],
  "patrones_de_apertura": ["como suele empezar sus posts"],
  "patrones_de_cierre": ["como suele cerrar o preguntar"]
}}

Solo el JSON, sin explicaciones."""

    respuesta = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )

    try:
        analisis = json.loads(respuesta.content[0].text)
        memoria["estilo_aprendido"] = analisis.get("estilo_aprendido", "")
        memoria["frases_caracteristicas"] = analisis.get("frases_caracteristicas", [])
        memoria["referencias_personales"] = analisis.get("referencias_personales", [])
        memoria["temas_exitosos"] = analisis.get("temas_exitosos", [])
        memoria["patrones_apertura"] = analisis.get("patrones_de_apertura", [])
        memoria["patrones_cierre"] = analisis.get("patrones_de_cierre", [])
    except json.JSONDecodeError:
        pass

    return memoria

def obtener_contexto(nombre: str) -> str:
    memoria = cargar_memoria(nombre)

    if not memoria["estilo_aprendido"] and not memoria["posts_publicados"]:
        return ""

    partes = []

    if memoria["estilo_aprendido"]:
        partes.append(f"ESTILO APRENDIDO DE {nombre.upper()}:\n{memoria['estilo_aprendido']}")

    if memoria["frases_caracteristicas"]:
        partes.append(f"FRASES QUE USA: {', '.join(memoria['frases_caracteristicas'])}")

    if memoria["referencias_personales"]:
        partes.append(f"REFERENCIAS PERSONALES: {', '.join(memoria['referencias_personales'])}")

    if memoria.get("patrones_apertura"):
        partes.append(f"CÓMO SUELE ABRIR: {', '.join(memoria['patrones_apertura'])}")

    if memoria["temas_exitosos"]:
        partes.append(f"TEMAS QUE LE HAN FUNCIONADO: {', '.join(memoria['temas_exitosos'])}")

    if memoria["posts_publicados"]:
        ultimo = memoria["posts_publicados"][-1]["post"]
        partes.append(f"ÚLTIMO POST (no repetir ideas):\n{ultimo[:300]}...")

    return "\n\n".join(partes)
