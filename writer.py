import anthropic
import sys
sys.path.insert(0, ".")
from memory.memory import obtener_contexto

client = anthropic.Anthropic()

def generar_post(config: dict, tendencias: list[str]) -> str:
    tendencias_str = "\n".join(f"- {t}" for t in tendencias)
    contexto_memoria = obtener_contexto(config["nombre"])

    seccion_memoria = ""
    if contexto_memoria:
        seccion_memoria = f"""
MEMORIA ACUMULADA DEL CLIENTE (usa esto para sonar exactamente como él/ella):
{contexto_memoria}

"""

    prompt = f"""Eres el ghostwriter de LinkedIn de {config['nombre']}.
{seccion_memoria}
Perfil base del cliente:
- Industria: {config['industria']}
- Tono: {config['tono']}
- Temas clave: {', '.join(config['temas_clave'])}
- Idioma: {config['idioma']}

Tendencias del día en su industria:
{tendencias_str}

Escribe UN post de LinkedIn que:
- Use una de las tendencias como gancho o contexto
- Aporte una perspectiva original desde el punto de vista de alguien que está aprendiendo, no de un experto
- Tenga entre 150-250 palabras
- Use saltos de línea cortos, fácil de leer en el cel
- Termine con una pregunta genuina que invite a comentar
- Suene como un estudiante inteligente y curioso, NO como consultor ni ejecutivo
- Nada de frases corporativas: sin "En el mundo actual", sin "Es fundamental", sin "cabe destacar"
- Lenguaje casual pero con criterio — como cuando le explicas algo a un amigo que sabe del tema
- NO use hashtags
- Si hay memoria acumulada, suene EXACTAMENTE como {config['nombre']} — mismas frases, mismo ritmo

Solo escribe el post, sin explicaciones ni títulos."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )

    return message.content[0].text
