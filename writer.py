import anthropic
import sys
sys.path.insert(0, ".")
from memory.memory import obtener_contexto

client = anthropic.Anthropic()

def generar_post(config: dict, tendencias: list[str], tema: str = None) -> str:
    nombre = config.get("nombre", "el usuario")
    industria = config.get("industria", "negocios")
    tono = config.get("tono", "casual y directo")
    temas_clave = config.get("temas_clave", [])
    idioma = config.get("idioma", "español")

    contexto_memoria = obtener_contexto(nombre)

    seccion_memoria = ""
    if contexto_memoria:
        seccion_memoria = f"""
MEMORIA ACUMULADA DEL CLIENTE (usa esto para sonar exactamente como él/ella):
{contexto_memoria}

"""

    if tema:
        contexto_contenido = f"TEMA ELEGIDO POR EL USUARIO:\n{tema}"
    else:
        tendencias_str = "\n".join(f"- {t}" for t in tendencias)
        contexto_contenido = f"TENDENCIAS DEL DÍA (elige una como gancho):\n{tendencias_str}"

    temas_str = ", ".join(temas_clave) if temas_clave else industria

    prompt = f"""Eres el ghostwriter de LinkedIn de {nombre}.
{seccion_memoria}
Perfil base del cliente:
- Industria: {industria}
- Tono: {tono}
- Temas clave: {temas_str}
- Idioma: {idioma}

{contexto_contenido}

El post debe sonar como alguien que comparte lo que está aprendiendo, no como un experto dando cátedra.

Reglas estrictas:
- Habla en primera persona, de forma natural — como si le contaras algo a un amigo
- Empieza con algo concreto que llamó tu atención, no con una gran declaración
- Máximo 200 palabras, párrafos cortos de 1-2 líneas
- Termina con una pregunta genuina y simple
- NADA de: "En el mundo actual", "Es fundamental", "cabe destacar", "sin duda", "hoy en día"
- NADA de lenguaje de consultor o ejecutivo
- Sin hashtags
- Si hay memoria acumulada, copia exactamente el ritmo y frases de {nombre}

Ejemplo del tono correcto:
"Vi que [empresa X] está haciendo algo raro con sus números.
Sus ingresos subieron 20% pero su margen bajó. Eso normalmente no pasa.
Lo que encontré cuando lo revisé me pareció interesante: [insight].
¿A alguien más le ha pasado analizar algo así?"

Solo escribe el post, sin explicaciones ni títulos."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )

    return message.content[0].text
