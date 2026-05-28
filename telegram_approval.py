"""
Envía el post por Telegram y espera aprobación antes de publicar.
Responde SI para publicar, NO para descartar, EDITAR [nuevo texto] para modificar.
"""
import time
import requests

def enviar_y_esperar_aprobacion(token: str, chat_id: str, post: str) -> str | None:
    """
    Envía el post por Telegram y espera respuesta.
    Retorna el post aprobado (original o editado), o None si fue rechazado.
    """
    base_url = f"https://api.telegram.org/bot{token}"

    mensaje = (
        f"📝 *Post de LinkedIn listo para publicar:*\n\n"
        f"{post}\n\n"
        f"---\n"
        f"Responde:\n"
        f"✅ *SI* — publicar\n"
        f"❌ *NO* — descartar\n"
        f"✏️ *EDITAR [tu versión]* — publicar con tu texto"
    )

    # Enviar mensaje
    requests.post(f"{base_url}/sendMessage", json={
        "chat_id": chat_id,
        "text": mensaje,
        "parse_mode": "Markdown"
    })

    print("Post enviado por Telegram. Esperando aprobación...")

    # Obtener el offset actual
    offset = None
    inicio = time.time()
    timeout = 3600  # esperar hasta 1 hora

    while time.time() - inicio < timeout:
        params = {"timeout": 30}
        if offset:
            params["offset"] = offset

        try:
            response = requests.get(f"{base_url}/getUpdates", params=params, timeout=35)
            updates = response.json().get("result", [])

            for update in updates:
                offset = update["update_id"] + 1
                mensaje_recibido = update.get("message", {})
                chat = mensaje_recibido.get("chat", {})

                if str(chat.get("id")) != str(chat_id):
                    continue

                texto = mensaje_recibido.get("text", "").strip()

                if texto.upper() == "SI":
                    requests.post(f"{base_url}/sendMessage", json={
                        "chat_id": chat_id,
                        "text": "✅ Publicando en LinkedIn..."
                    })
                    return post

                elif texto.upper() == "NO":
                    requests.post(f"{base_url}/sendMessage", json={
                        "chat_id": chat_id,
                        "text": "❌ Post descartado. Hasta mañana."
                    })
                    return None

                elif texto.upper().startswith("EDITAR "):
                    nuevo_post = texto[7:].strip()
                    requests.post(f"{base_url}/sendMessage", json={
                        "chat_id": chat_id,
                        "text": "✅ Publicando tu versión editada..."
                    })
                    return nuevo_post

        except requests.exceptions.Timeout:
            continue
        except Exception as e:
            print(f"Error Telegram: {e}")
            time.sleep(5)

    print("Timeout — no se recibió respuesta en 1 hora. Post descartado.")
    return None
