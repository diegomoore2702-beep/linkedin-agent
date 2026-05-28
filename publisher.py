import time
import json
import urllib.parse
from pathlib import Path
from playwright.sync_api import sync_playwright

COOKIES_PATH = Path("config/linkedin_session.json")

def guardar_sesion(context):
    cookies = context.cookies()
    COOKIES_PATH.write_text(json.dumps(cookies))
    print("Sesión guardada. No necesitarás loguearte por ~30 días.")

def cargar_sesion(context) -> bool:
    if COOKIES_PATH.exists():
        cookies = json.loads(COOKIES_PATH.read_text())
        context.add_cookies(cookies)
        return True
    return False

def publicar_en_linkedin(email: str, password: str, texto: str, imagen_path: str = None) -> bool:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=300)
        context = browser.new_context()
        page = context.new_page()

        try:
            sesion_cargada = cargar_sesion(context)

            if sesion_cargada:
                # Verificar que la sesión sigue activa
                page.goto("https://www.linkedin.com/feed/")
                time.sleep(3)
                if "feed" not in page.url:
                    sesion_cargada = False
                    print("Sesión expirada. Logueándote de nuevo...")

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
                input("\nSi LinkedIn pidió verificación, complétala.\nPresiona Enter cuando estés en el feed...")
                guardar_sesion(context)

            # Abrir modal con texto pre-cargado
            texto_encoded = urllib.parse.quote(texto)
            page.goto(f"https://www.linkedin.com/feed/?shareActive=true&text={texto_encoded}")
            time.sleep(4)

            # Abrir imagen en Finder para arrastrar al modal
            if imagen_path and Path(imagen_path).exists():
                import subprocess
                subprocess.run(["open", "-R", imagen_path])
                print(f"\nImagen abierta en Finder: {imagen_path}")
                print("Arrástrala al modal de LinkedIn para adjuntarla.")

            input("\nPost listo en LinkedIn. Adjunta la imagen, revisa y publica.\nPresiona Enter cuando hayas publicado...")

            # Actualizar sesión
            guardar_sesion(context)
            browser.close()
            print("Publicado en LinkedIn.")
            return True

        except Exception as e:
            print(f"Error al publicar: {e}")
            browser.close()
            return False
