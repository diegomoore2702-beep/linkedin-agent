import json
import sys
from pathlib import Path
from trends import get_trends
from writer import generar_post
from publisher import publicar_en_linkedin

def correr_agente(config_path: str, solo_generar: bool = False):
    with open(config_path) as f:
        config = json.load(f)

    print(f"Agente iniciado para: {config['nombre']}")

    print("Buscando tendencias...")
    tendencias = get_trends(config["industria"])
    print(f"Tendencias encontradas: {len(tendencias)}")

    print("Generando post...")
    post = generar_post(config, tendencias)

    print("\n" + "="*50)
    print("POST GENERADO:")
    print("="*50)
    print(post)
    print("="*50 + "\n")

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
            publicar_en_linkedin(config["linkedin_email"], config["linkedin_password"], post)
    else:
        print("Sin credenciales de LinkedIn — post guardado para revisión manual.")

if __name__ == "__main__":
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config/ejemplo_cliente.json"
    solo_generar = "--solo-generar" in sys.argv
    correr_agente(config_path, solo_generar)
