import json
import sys
import logging
from pathlib import Path
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from trends import get_trends
from writer import generar_post
from publisher import publicar_en_linkedin
from memory.memory import registrar_post

logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(message)s")

def publicar_automatico(config_path: str):
    with open(config_path) as f:
        config = json.load(f)

    logging.info(f"Iniciando agente para: {config['nombre']}")

    try:
        tendencias = get_trends(config["industria"])
        logging.info(f"Tendencias encontradas: {len(tendencias)}")

        post = generar_post(config, tendencias)

        output = Path("posts") / f"{config['nombre'].replace(' ', '_')}_{datetime.now().strftime('%Y-%m-%d')}.txt"
        output.parent.mkdir(exist_ok=True)
        output.write_text(post)
        logging.info(f"Post guardado en: {output}")

        print("\n" + "="*50)
        print(post)
        print("="*50 + "\n")

        if config.get("linkedin_email") and config.get("linkedin_password"):
            publicar_en_linkedin(config["linkedin_email"], config["linkedin_password"], post)
            logging.info("Post publicado en LinkedIn.")
        else:
            logging.warning("Sin credenciales — post guardado pero no publicado.")

        registrar_post(config["nombre"], post)
        logging.info("Post guardado en memoria del cliente.")

    except Exception as e:
        logging.error(f"Error: {e}")

if __name__ == "__main__":
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config/ejemplo_cliente.json"

    with open(config_path) as f:
        config = json.load(f)

    hora = config.get("hora_publicacion", "08:00")
    hora_h, hora_m = hora.split(":")

    scheduler = BlockingScheduler()
    scheduler.add_job(
        publicar_automatico,
        "cron",
        hour=int(hora_h),
        minute=int(hora_m),
        args=[config_path]
    )

    logging.info(f"Scheduler activo — publicará cada día a las {hora} para {config['nombre']}")
    logging.info("Deja esta ventana abierta. Ctrl+C para detener.")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logging.info("Scheduler detenido.")
