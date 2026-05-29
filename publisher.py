import time
import json
import os
import urllib.parse
from pathlib import Path
from playwright.sync_api import sync_playwright

COOKIES_PATH = Path("config/linkedin_session.json")
MODO_SERVIDOR = os.getenv("RAILWAY_ENVIRONMENT") is not None

def guardar_sesion(context):
    cookies = context.cookies()
    COOKIES_PATH.write_text(json.dumps(cookies))
    if not MODO_SERVIDOR:
        print("Sesión guardada.")

def cargar_sesion(context) -> bool:
    if COOKIES_PATH.exists():
        cookies = json.loads(COOKIES_PATH.read_text())
        context.add_cookies(cookies)
        return True
    return False

def publicar_en_linkedin(email: str, password: str, texto: str, carrusel_path: str = None) -> bool:
    headless = MODO_SERVIDOR

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless, slow_mo=300 if not headless else 0)
        context = browser.new_context()
        page = context.new_page()

        try:
            sesion_cargada = cargar_sesion(context)

            if sesion_cargada:
                page.goto("https://www.linkedin.com/feed/")
                time.sleep(3)
                if "feed" not in page.url:
                    sesion_cargada = False

            if not sesion_cargada:
                page.goto("https://www.linkedin.com/login")
                time.sleep(2)
                try:
                    page.fill("#username", email, timeout=10000)
                    page.fill("#password", password)
                    page.click('[type="submit"]')
                    page.wait_for_url("**/feed**", timeout=30000)
                except Exception:
                    pass

                if not MODO_SERVIDOR:
                    input("\nPresiona Enter cuando estés en el feed de LinkedIn...")

                guardar_sesion(context)

            # Abrir modal con texto pre-cargado
            texto_encoded = urllib.parse.quote(texto)
            page.goto(f"https://www.linkedin.com/feed/?shareActive=true&text={texto_encoded}")
            time.sleep(4)

            if not MODO_SERVIDOR:
                # Abrir carrusel en Finder para arrastrar
                if carrusel_path and Path(carrusel_path).exists():
                    import subprocess
                    subprocess.run(["open", "-R", carrusel_path])
                    print(f"\nCarrusel abierto en Finder. Arrástralo al modal de LinkedIn.")

                input("\nRevisa el post, adjunta el carrusel y publica.\nPresiona Enter cuando hayas publicado...")
            else:
                # En servidor: intentar adjuntar y publicar automáticamente
                time.sleep(3)
                if carrusel_path and Path(carrusel_path).exists():
                    try:
                        file_input = page.locator('input[type="file"]').first
                        file_input.set_input_files(carrusel_path, timeout=10000)
                        time.sleep(3)
                    except Exception:
                        pass

                # Intentar publicar
                for selector in ['button:has-text("Publicar")', 'button:has-text("Post")', 'button[data-control-name="share.post"]']:
                    try:
                        page.click(selector, timeout=5000)
                        break
                    except Exception:
                        continue
                time.sleep(3)

            guardar_sesion(context)
            browser.close()
            print("Publicado en LinkedIn.")
            return True

        except Exception as e:
            print(f"Error al publicar: {e}")
            browser.close()
            return False
