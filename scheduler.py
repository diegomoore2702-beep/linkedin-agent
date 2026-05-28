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
from image_generator import generar_imagen
from engagement_tracker import actualizar_engagement

logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(message)s")

def publicar_automatico(config_path: str):
    with open(config_path) as f:
        config = json.load(f)

    logging.info(f"Iniciando agente para: {config['nombre']}")

    try:
        # 1. Actualizar engagement de posts anteriores
        logging.info("Actualizando engagement de posts anteriores...")
        actualizar_engagement(config_path)

        # 2. Generar post
        tendencias = get_trends(config["industria"])
        logging.info(f"Tendencias encontradas: {len(tendencias)}")
        post = generar_post(config, tendencias)

        # 3. Generar imagen
        imagen_path = None
        logging.info("Generando imagen...")
        imagen_path = generar_imagen(post, config["nombre"], config["industria"])

        # 4. Aprobación por Telegram
        if config.get("telegram_token") and config.get("telegram_chat_id"):
            from telegram_approval import enviar_y_esperar_aprobacion
            post = enviar_y_esperar_aprobacion(
                config["telegram_token"],
                config["telegram_chat_id"],
                post
            )
            if not post:
                logging.info("Post descartado por el usuario.")
                return

        # 5. Guardar post
        output = Path("posts") / f"{config['nombre'].replace(' ', '_')}_{datetime.now().strftime('%Y-%m-%d')}.txt"
        output.parent.mkdir(exist_ok=True)
        output.write_text(post)
        logging.info(f"Post guardado en: {output}")

        print("\n" + "="*50)
        print(post)
        print("="*50 + "\n")

        # 6. Publicar en LinkedIn
        if config.get("linkedin_email") and config.get("linkedin_password"):
            publicar_en_linkedin(config["linkedin_email"], config["linkedin_password"], post)
            logging.info("Publicado en LinkedIn.")

        # 7. Publicar en Instagram si está configurado
        if config.get("instagram_username") and config.get("instagram_password"):
            from instagram_publisher import publicar_en_instagram
            if imagen_path:
                publicar_en_instagram(
                    config["instagram_username"],
                    config["instagram_password"],
                    post,
                    imagen_path
                )
                logging.info("Publicado en Instagram.")
            else:
                logging.warning("Sin imagen — no se publicó en Instagram.")

        # 8. Guardar en memoria
        registrar_post(config["nombre"], post)
        logging.info("Post guardado en memoria.")

    except Exception as e:
        logging.error(f"Error: {e}")

if __name__ == "__main__":
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config/ejemplo_cliente.json"

    with open(config_path) as f:
        config = json.load(f)

    hora = config.get("hora_publicacion", "08:00")
    hora_h, hora_m = hora.split(":")

    scheduler = BlockingScheduler()

    # Publicar post todos los días
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
