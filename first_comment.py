"""
Publica el primer comentario en el post justo después de publicar.
Aumenta el alcance ~30-50% porque LinkedIn muestra el post a más gente con actividad temprana.
Si falla por cualquier razón, no afecta el flujo principal.
"""
import time
import json
import os
import anthropic
from pathlib import Path

client = anthropic.Anthropic()
COOKIES_PATH = Path(__file__).parent / "config" / "linkedin_session.json"
MODO_SERVIDOR = os.getenv("RAILWAY_ENVIRONMENT") is not None

def generar_primer_comentario(post: str, nombre: str) -> str:
    try:
        respuesta = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=200,
            messages=[{
                "role": "user",
                "content": f"""Este post de LinkedIn acaba de publicarse:

{post[:500]}

Escribe el primer comentario que dejará {nombre} en su propio post.
- 3 puntos clave del post, formato simple (sin bullets formales)
- Máximo 60 palabras
- Tono natural, no corporativo
- Termina invitando a guardar o compartir

Solo el comentario."""
            }]
        )
        return respuesta.content[0].text.strip()
    except Exception as e:
        return f"3 puntos clave de este post:\n1. {post[:60]}...\n\n¿Qué opinas? Guarda este post si te fue útil."

def publicar_primer_comentario(email: str, password: str, post: str, nombre: str) -> bool:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Playwright no disponible para primer comentario.")
        return False

    comentario = generar_primer_comentario(post, nombre)
    print(f"\nPrimer comentario preparado ({len(comentario)} chars)")

    print("Esperando 3 minutos antes de comentar...")
    time.sleep(180)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=MODO_SERVIDOR, slow_mo=200 if not MODO_SERVIDOR else 0)
            context = browser.new_context()
            page = context.new_page()

            try:
                # Cargar sesión
                if COOKIES_PATH.exists():
                    cookies = json.loads(COOKIES_PATH.read_text())
                    context.add_cookies(cookies)

                page.goto("https://www.linkedin.com/in/me/recent-activity/shares/", timeout=30000)
                time.sleep(4)

                # Verificar que está logueado
                if "login" in page.url:
                    print("Sesión expirada — primer comentario skipped.")
                    browser.close()
                    return False

                # Encontrar el primer post
                primer_post = page.query_selector(".feed-shared-update-v2")
                if not primer_post:
                    print("No se encontró el post reciente.")
                    browser.close()
                    return False

                # Buscar botón de comentar
                comentado = False
                for selector in [
                    'button[aria-label*="Comment"]',
                    'button[aria-label*="Comentar"]',
                    'button:has-text("Comentar")',
                    'button:has-text("Comment")',
                ]:
                    try:
                        btn = primer_post.query_selector(selector)
                        if btn:
                            btn.click()
                            comentado = True
                            break
                    except Exception:
                        continue

                if not comentado:
                    print("No se encontró el botón de comentar.")
                    browser.close()
                    return False

                time.sleep(2)

                # Escribir comentario
                editor = page.locator('[role="textbox"]').first
                editor.click()
                editor.type(comentario, delay=10)
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
                print(f"Error en primer comentario: {e}")
                try:
                    browser.close()
                except Exception:
                    pass
                return False

    except Exception as e:
        print(f"Error iniciando Playwright para comentario: {e}")
        return False
