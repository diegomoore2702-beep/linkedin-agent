"""
Importa los posts existentes de LinkedIn para arrancar la memoria del cliente.
Uso: python importer.py config/ejemplo_cliente.json
"""
import sys
import time
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
sys.path.insert(0, ".")
from memory.memory import cargar_memoria, guardar_memoria, _analizar_estilo

def importar_posts(config_path: str):
    with open(config_path) as f:
        config = json.load(f)

    if not config.get("linkedin_email") or not config.get("linkedin_password"):
        print("Agrega linkedin_email y linkedin_password en el config para importar posts.")
        return

    print(f"Conectando a LinkedIn como {config['nombre']}...")
    print("\nSe va a abrir el navegador. Si LinkedIn pide verificación, complétala manualmente.")
    print("Cuando estés en el feed de LinkedIn, presiona Enter aquí para continuar...\n")
    posts = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()

        try:
            page.goto("https://www.linkedin.com/login")
            time.sleep(2)

            try:
                page.fill("#username", config["linkedin_email"], timeout=10000)
                page.fill("#password", config["linkedin_password"])
                page.click('[type="submit"]')
                page.wait_for_url("**/feed**", timeout=30000)
            except Exception:
                pass

            input("Presiona Enter cuando estés en el feed de LinkedIn...")
            print("Login exitoso.")

            # Ir al perfil
            page.goto("https://www.linkedin.com/in/me/recent-activity/shares/")
            time.sleep(3)

            # Scroll para cargar más posts
            for _ in range(5):
                page.keyboard.press("End")
                time.sleep(2)

            # Extraer texto de los posts
            elementos = page.query_selector_all(".feed-shared-update-v2__description-wrapper, .update-components-text")
            for el in elementos[:30]:
                texto = el.inner_text().strip()
                if len(texto) > 100:
                    posts.append(texto)

            print(f"Se encontraron {len(posts)} posts.")
            browser.close()

        except Exception as e:
            print(f"Error: {e}")
            browser.close()
            return

    if not posts:
        print("No se encontraron posts. Verifica que tu perfil tenga publicaciones.")
        return

    # Guardar posts en memoria
    memoria = cargar_memoria(config["nombre"])
    for post in posts:
        memoria["posts_publicados"].append({
            "fecha": "importado",
            "post": post,
            "engagement": {"likes": 0, "comentarios": 0, "reposts": 0}
        })
    memoria["total_posts"] = len(posts)

    print("Analizando tu estilo de escritura...")
    memoria = _analizar_estilo(memoria)
    guardar_memoria(memoria)

    print(f"\nListo. Memoria creada con {len(posts)} posts.")
    print(f"Estilo detectado: {memoria['estilo_aprendido'][:200]}...")
    print("\nDesde ahora el agente sonará exactamente como tú.")

if __name__ == "__main__":
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config/ejemplo_cliente.json"
    importar_posts(config_path)
