"""
Publica el primer comentario en el post justo después de publicar.
Esto aumenta el alcance ~30-50% porque LinkedIn muestra el post a más gente
cuando hay actividad temprana.
"""
import time
import json
import os
import anthropic
from pathlib import Path
from playwright.sync_api import sync_playwright

client = anthropic.Anthropic()
COOKIES_PATH = Path("config/linkedin_session.json")
MODO_SERVIDOR = os.getenv("RAILWAY_ENVIRONMENT") is not None

def generar_primer_comentario(post: str, nombre: str) -> str:
    respuesta = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        messages=[{
            "role": "user",
            "content": f"""Este post de LinkedIn acaba de publicarse:

{post}

Escribe el primer comentario que dejará {nombre} en su propio post.
El comentario debe:
- Tener 3 puntos clave del post en formato de lista simple (sin bullets formales)
- Terminar invitando a guardar el post o a etiquetar a alguien
- Sonar natural, no corporativo
- Máximo 80 palabras

Solo el comentario, sin explicaciones."""
        }]
    )
    return respuesta.content[0].text.strip()

def publicar_primer_comentario(email: str, password: str, post: str, nombre: str) -> bool:
    comentario = generar_primer_comentario(post, nombre)
    print(f"\nPrimer comentario generado:\n{comentario}")

    # Esperar 3 minutos para que LinkedIn indexe el post
    print("Esperando 3 minutos antes de comentar...")
    time.sleep(180)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=MODO_SERVIDOR, slow_mo=300 if not MODO_SERVIDOR else 0)
        context = browser.new_context()
        page = context.new_page()

        try:
            # Cargar sesión guardada
            if COOKIES_PATH.exists():
                cookies = json.loads(COOKIES_PATH.read_text())
                context.add_cookies(cookies)

            # Ir al perfil y encontrar el último post
            page.goto("https://www.linkedin.com/in/me/recent-activity/shares/")
            time.sleep(4)

            # Click en el primer post
            primer_post = page.query_selector(".feed-shared-update-v2")
            if not primer_post:
                print("No se encontró el post para comentar.")
                browser.close()
                return False

            # Buscar el botón de comentar
            for selector in [
                'button[aria-label*="Comment"]',
                'button[aria-label*="Comentar"]',
                'button:has-text("Comentar")',
                'button:has-text("Comment")',
            ]:
                try:
                    primer_post.query_selector(selector).click()
                    break
                except Exception:
                    continue

            time.sleep(2)

            # Escribir el comentario
            editor = page.locator('[role="textbox"]').first
            editor.click()
            editor.type(comentario, delay=15)
            time.sleep(1)

            # Publicar comentario
            for selector in ['button:has-text("Publicar")', 'button:has-text("Post")', 'button[type="submit"]']:
                try:
                    page.click(selector, timeout=5000)
                    break
                except Exception:
                    continue

            time.sleep(2)
            print("Primer comentario publicado.")
            browser.close()
            return True

        except Exception as e:
            print(f"Error publicando comentario: {e}")
            browser.close()
            return False
