import anthropic
import sys
sys.path.insert(0, ".")
from memory.memory import obtener_contexto, cargar_memoria

client = anthropic.Anthropic()

def _construir_prompt(nombre, industria, tono, temas_str, idioma, contexto_contenido, seccion_memoria, variante="") -> str:
    instruccion_variante = ""
    if variante == "A":
        instruccion_variante = "VARIANTE A: Empieza con un dato o hecho concreto que sorprenda."
    elif variante == "B":
        instruccion_variante = "VARIANTE B: Empieza con una pregunta o situación personal."

    return f"""Eres el ghostwriter de LinkedIn de {nombre}.
{seccion_memoria}
Perfil base del cliente:
- Industria: {industria}
- Tono: {tono}
- Temas clave: {temas_str}
- Idioma: {idioma}

{contexto_contenido}
{instruccion_variante}

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

def _score_post(post: str, memoria: dict) -> float:
    score = 0.0
    temas_exitosos = memoria.get("temas_exitosos", [])
    frases = memoria.get("frases_caracteristicas", [])

    # Penalizar si es muy largo o muy corto
    palabras = len(post.split())
    if 80 <= palabras <= 180:
        score += 2.0
    elif palabras < 50 or palabras > 250:
        score -= 1.0

    # Premio si usa frases características del cliente
    for frase in frases:
        if any(palabra in post.lower() for palabra in frase.lower().split()[:3]):
            score += 1.0

    # Premio si toca temas exitosos
    for tema in temas_exitosos:
        palabras_tema = tema.lower().split()[:5]
        if any(p in post.lower() for p in palabras_tema):
            score += 1.5

    # Premio si termina con pregunta
    if "?" in post[-100:]:
        score += 1.0

    # Penalizar frases corporativas
    frases_malas = ["en el mundo actual", "es fundamental", "cabe destacar", "sin duda", "hoy en día"]
    for frase in frases_malas:
        if frase in post.lower():
            score -= 2.0

    return score

def generar_post(config: dict, tendencias: list[str], tema: str = None) -> str:
    nombre = config.get("nombre", "el usuario")
    industria = config.get("industria", "negocios")
    tono = config.get("tono", "casual y directo")
    temas_clave = config.get("temas_clave", [])
    idioma = config.get("idioma", "español")

    contexto_memoria = obtener_contexto(nombre)
    memoria = cargar_memoria(nombre)

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

    # A/B testing: generar 2 versiones y elegir la mejor
    tiene_historial = len(memoria.get("posts_publicados", [])) >= 3

    if tiene_historial:
        print("Generando 2 versiones del post (A/B test)...")

        prompts = [
            _construir_prompt(nombre, industria, tono, temas_str, idioma, contexto_contenido, seccion_memoria, "A"),
            _construir_prompt(nombre, industria, tono, temas_str, idioma, contexto_contenido, seccion_memoria, "B"),
        ]

        versiones = []
        for prompt in prompts:
            msg = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            versiones.append(msg.content[0].text)

        scores = [_score_post(v, memoria) for v in versiones]
        mejor_idx = scores.index(max(scores))
        ganadora = "A" if mejor_idx == 0 else "B"
        print(f"Versión {ganadora} seleccionada (score: {scores[mejor_idx]:.1f} vs {scores[1-mejor_idx]:.1f})")
        return versiones[mejor_idx]

    else:
        # Sin historial suficiente: generar una sola versión
        prompt = _construir_prompt(nombre, industria, tono, temas_str, idioma, contexto_contenido, seccion_memoria)
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
