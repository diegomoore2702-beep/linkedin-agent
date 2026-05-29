import anthropic
import sys
sys.path.insert(0, ".")

client = anthropic.Anthropic()

def _construir_prompt(nombre, industria, tono, temas_str, idioma, contexto_contenido, seccion_memoria, variante="") -> str:
    instruccion_variante = ""
    if variante == "A":
        instruccion_variante = "\nVARIANTE A: Empieza con un dato o hecho concreto que sorprenda."
    elif variante == "B":
        instruccion_variante = "\nVARIANTE B: Empieza con una situación personal o pregunta directa."

    return f"""Eres el ghostwriter de LinkedIn de {nombre}.
{seccion_memoria}
Perfil del cliente:
- Industria: {industria}
- Tono: {tono}
- Temas clave: {temas_str}
- Idioma: {idioma}

{contexto_contenido}{instruccion_variante}

El post debe sonar como alguien que comparte lo que está aprendiendo, no como un experto.

Reglas:
- Primera persona, natural — como contándole algo a un amigo
- Empieza con algo concreto, no con una declaración genérica
- Máximo 200 palabras, párrafos de 1-2 líneas
- Termina con una pregunta genuina
- Sin: "En el mundo actual", "Es fundamental", "cabe destacar", "sin duda"
- Sin lenguaje corporativo ni hashtags
- Si hay memoria, copia el ritmo y frases de {nombre}

Solo escribe el post, sin títulos ni explicaciones."""

def _score_post(post: str, memoria: dict) -> float:
    score = 0.0
    palabras = len(post.split())

    if 80 <= palabras <= 180:
        score += 2.0
    elif palabras < 50 or palabras > 250:
        score -= 1.0

    for frase in memoria.get("frases_caracteristicas", []):
        if any(p in post.lower() for p in frase.lower().split()[:3]):
            score += 1.0

    for tema in memoria.get("temas_exitosos", []):
        if any(p in post.lower() for p in tema.lower().split()[:5]):
            score += 1.5

    if "?" in post[-100:]:
        score += 1.0

    frases_malas = ["en el mundo actual", "es fundamental", "cabe destacar", "sin duda", "hoy en día"]
    for frase in frases_malas:
        if frase in post.lower():
            score -= 2.0

    return score

def generar_post(config: dict, tendencias: list, tema: str = None) -> str:
    nombre = config.get("nombre", "el usuario")
    industria = config.get("industria", "negocios")
    tono = config.get("tono", "casual y directo")
    temas_clave = config.get("temas_clave", [])
    idioma = config.get("idioma", "español")
    temas_str = ", ".join(temas_clave) if temas_clave else industria

    # Cargar contexto de memoria
    seccion_memoria = ""
    memoria = {}
    try:
        from memory.memory import obtener_contexto, cargar_memoria
        contexto = obtener_contexto(nombre)
        memoria = cargar_memoria(nombre)
        if contexto:
            seccion_memoria = f"\nMEMORIA DEL CLIENTE:\n{contexto}\n"
    except Exception:
        pass

    if tema:
        contexto_contenido = f"TEMA ELEGIDO:\n{tema}"
    elif tendencias:
        tendencias_str = "\n".join(f"- {t}" for t in tendencias)
        contexto_contenido = f"TENDENCIAS DEL DÍA (elige una):\n{tendencias_str}"
    else:
        contexto_contenido = f"Escribe sobre {industria} con perspectiva original."

    tiene_historial = len(memoria.get("posts_publicados", [])) >= 3

    if tiene_historial:
        # A/B testing: generar 2 versiones y elegir la mejor
        try:
            print("Generando versiones A/B...")
            versiones = []
            for variante in ["A", "B"]:
                prompt = _construir_prompt(nombre, industria, tono, temas_str, idioma, contexto_contenido, seccion_memoria, variante)
                msg = client.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=1024,
                    messages=[{"role": "user", "content": prompt}]
                )
                versiones.append(msg.content[0].text)

            scores = [_score_post(v, memoria) for v in versiones]
            mejor_idx = scores.index(max(scores))
            ganadora = "A" if mejor_idx == 0 else "B"
            print(f"Versión {ganadora} elegida (score: {scores[mejor_idx]:.1f} vs {scores[1-mejor_idx]:.1f})")
            return versiones[mejor_idx]
        except Exception as e:
            print(f"A/B test falló, generando versión única: {e}")

    # Sin historial o si A/B falló: versión única
    prompt = _construir_prompt(nombre, industria, tono, temas_str, idioma, contexto_contenido, seccion_memoria)
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text
