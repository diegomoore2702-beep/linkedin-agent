import json
import sys
from pathlib import Path
from trends import get_trends
from writer import generar_post
from publisher import publicar_en_linkedin
from carousel_generator import generar_carrusel

def correr_agente(config_path: str, solo_generar: bool = False, foto_override: str = None, tema: str = None, estilo: str = None):
    with open(config_path) as f:
        config = json.load(f)

    print(f"Agente iniciado para: {config['nombre']}")

    tendencias = []
    if not tema:
        print("Buscando tendencias...")
        tendencias = get_trends(config["industria"])
        print(f"Tendencias encontradas: {len(tendencias)}")
    else:
        print(f"Tema elegido: {tema}")

    print("Generando post...")
    post = generar_post(config, tendencias, tema)

    print("\n" + "="*50)
    print("POST GENERADO:")
    print("="*50)
    print(post)
    print("="*50 + "\n")

    # Generar carrusel
    print("Generando carrusel...")
    foto_path = foto_override or config.get("foto_path", "config/foto.jpg")
    estilo_carrusel = estilo or config.get("estilo_carrusel", "clasico")
    imagen_path = generar_carrusel(post, config, foto_path, estilo_carrusel)
    if imagen_path:
        print(f"Carrusel guardado en: {imagen_path}")

    # Guardar en archivo
    output = Path("posts") / f"{config['nombre'].replace(' ', '_')}_post.txt"
    output.parent.mkdir(exist_ok=True)
    output.write_text(post)
    print(f"Post guardado en: {output}")

    if solo_generar:
        print("Modo solo-generar: no se publicó.")
        return

    if config.get("linkedin_email") and config.get("linkedin_password"):
        confirmar = input("\n¿Publicar en LinkedIn ahora? (s/n): ")
        if confirmar.lower() == "s":
            publicar_en_linkedin(config["linkedin_email"], config["linkedin_password"], post, imagen_path)
    else:
        print("Sin credenciales de LinkedIn — post guardado para revisión manual.")

if __name__ == "__main__":
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config/ejemplo_cliente.json"
    solo_generar = "--solo-generar" in sys.argv

    # --foto /ruta/foto.jpg
    foto_override = None
    if "--foto" in sys.argv:
        idx = sys.argv.index("--foto")
        if idx + 1 < len(sys.argv):
            foto_override = sys.argv[idx + 1]

    # --tema "de qué quieres hablar hoy"
    tema = None
    if "--tema" in sys.argv:
        idx = sys.argv.index("--tema")
        if idx + 1 < len(sys.argv):
            tema = sys.argv[idx + 1]

    # --estilo clasico | minimalista | claro | foto-grande
    estilo = None
    if "--estilo" in sys.argv:
        idx = sys.argv.index("--estilo")
        if idx + 1 < len(sys.argv):
            estilo = sys.argv[idx + 1]

    correr_agente(config_path, solo_generar, foto_override, tema, estilo)
