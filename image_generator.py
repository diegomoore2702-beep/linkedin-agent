"""
Genera una imagen relevante para el post usando Pollinations AI (gratis, sin API key).
"""
import re
import requests
import anthropic
from pathlib import Path
from datetime import datetime

client = anthropic.Anthropic()

def generar_prompt_imagen(post: str, industria: str) -> str:
    respuesta = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=150,
        messages=[{
            "role": "user",
            "content": f"""Basándote en este post de LinkedIn sobre {industria}:

{post[:300]}

Escribe un prompt en inglés para generar una imagen profesional que lo acompañe.
- Estilo: professional, corporate, minimalist, LinkedIn-appropriate
- Sin texto en la imagen
- Sin personas específicas
- Máximo 20 palabras

Solo el prompt, sin explicaciones."""
        }]
    )
    return respuesta.content[0].text.strip()

def generar_imagen(post: str, nombre: str, industria: str) -> str | None:
    try:
        prompt = generar_prompt_imagen(post, industria)
        prompt_encoded = requests.utils.quote(f"{prompt}, professional LinkedIn post image, high quality")

        url = f"https://image.pollinations.ai/prompt/{prompt_encoded}?width=1200&height=627&nologo=true"

        print(f"Generando imagen: {prompt}")
        response = requests.get(url, timeout=30)

        if response.status_code == 200:
            carpeta = Path("posts/imagenes")
            carpeta.mkdir(parents=True, exist_ok=True)
            fecha = datetime.now().strftime("%Y-%m-%d")
            nombre_archivo = f"{nombre.replace(' ', '_')}_{fecha}.jpg"
            ruta = carpeta / nombre_archivo
            ruta.write_bytes(response.content)
            print(f"Imagen guardada en: {ruta}")
            return str(ruta)
        else:
            print("No se pudo generar la imagen.")
            return None

    except Exception as e:
        print(f"Error generando imagen: {e}")
        return None
