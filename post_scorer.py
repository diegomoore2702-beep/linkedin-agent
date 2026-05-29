"""
Evalúa un post de LinkedIn antes de publicar.
Si el score es bajo, regenera automáticamente.
"""
import anthropic
import json

client = anthropic.Anthropic()

def evaluar_post(post: str, config: dict) -> dict:
    nombre = config.get("nombre", "")
    industria = config.get("industria", "")

    try:
        respuesta = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=400,
            messages=[{
                "role": "user",
                "content": f"""Evalúa este post de LinkedIn para {nombre} ({industria}).

POST:
{post}

Evalúa del 1 al 10 estos criterios y responde en JSON:
{{
  "score_total": número del 1 al 10,
  "gancho": número del 1 al 10,
  "claridad": número del 1 al 10,
  "engagement": número del 1 al 10,
  "autenticidad": número del 1 al 10,
  "problema_principal": "el mayor problema del post en una línea, o vacío si es bueno",
  "publicar": true o false
}}

Reglas para publicar:
- score_total >= 7: publicar = true
- score_total < 7: publicar = false

Solo el JSON."""
            }]
        )

        texto = respuesta.content[0].text.strip()
        if texto.startswith("```"):
            texto = texto.split("```")[1]
            if texto.startswith("json"):
                texto = texto[4:]
        return json.loads(texto)

    except Exception as e:
        # Si falla la evaluación, dejamos pasar el post
        return {"score_total": 8, "publicar": True, "problema_principal": ""}


def generar_post_con_score(config: dict, tendencias: list, tema: str = None, intentos: int = 3) -> str:
    from writer import generar_post

    for intento in range(intentos):
        post = generar_post(config, tendencias, tema)
        evaluacion = evaluar_post(post, config)
        score = evaluacion.get("score_total", 8)
        problema = evaluacion.get("problema_principal", "")

        print(f"Score del post: {score}/10", end="")
        if problema:
            print(f" — {problema}")
        else:
            print(" — Listo para publicar")

        if evaluacion.get("publicar", True):
            return post

        if intento < intentos - 1:
            print(f"Generando mejor versión (intento {intento + 2}/{intentos})...")

    # Si ninguno superó el umbral, retornar el último generado
    print("Publicando mejor versión disponible.")
    return post
