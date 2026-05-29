"""
Dashboard de analytics del agente LinkedIn.
Uso: python analytics.py config/ejemplo_cliente.json
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def mostrar_analytics(config_path: str):
    try:
        with open(config_path) as f:
            config = json.load(f)
    except Exception as e:
        print(f"Error leyendo config: {e}")
        return

    nombre = config.get("nombre", "usuario")

    try:
        from memory.memory import cargar_memoria
        memoria = cargar_memoria(nombre)
    except Exception as e:
        print(f"Error cargando memoria: {e}")
        return

    posts = memoria.get("posts_publicados", [])
    posts_agente = [p for p in posts if p.get("fecha", "") != "importado"]

    print("\n" + "="*55)
    print(f"  ANALYTICS — {nombre.upper()}")
    print("="*55)
    print(f"\nPosts publicados con el agente: {len(posts_agente)}")
    print(f"Posts en historial (importados): {len(posts) - len(posts_agente)}")

    if not posts_agente:
        print("\nAún no hay posts publicados. Los analytics aparecen después del primer post.")
        print("="*55 + "\n")
        return

    # Engagement
    likes_list = [p["engagement"].get("likes", 0) for p in posts_agente]
    comentarios_list = [p["engagement"].get("comentarios", 0) for p in posts_agente]
    total_likes = sum(likes_list)
    total_comentarios = sum(comentarios_list)
    avg_likes = total_likes / len(posts_agente)
    avg_comentarios = total_comentarios / len(posts_agente)

    print(f"\n❤️  Likes totales:       {total_likes} (avg: {avg_likes:.1f}/post)")
    print(f"💬  Comentarios totales: {total_comentarios} (avg: {avg_comentarios:.1f}/post)")

    # Top posts
    top = sorted(posts_agente, key=lambda p: p["engagement"].get("likes", 0), reverse=True)[:3]
    if any(p["engagement"].get("likes", 0) > 0 for p in top):
        print("\n🏆 Top 3 posts:")
        for i, p in enumerate(top, 1):
            l = p["engagement"].get("likes", 0)
            c = p["engagement"].get("comentarios", 0)
            preview = p["post"][:65].replace("\n", " ")
            print(f"   {i}. {l}❤️  {c}💬  — {preview}...")

    # Temas exitosos
    temas = memoria.get("temas_exitosos", [])
    if temas:
        print(f"\n✅ Temas que han funcionado:")
        for t in temas[:4]:
            print(f"   • {t[:65]}...")

    # Tendencia
    if len(posts_agente) >= 4:
        mitad = len(posts_agente) // 2
        avg_antes = sum(likes_list[:mitad]) / mitad
        avg_despues = sum(likes_list[mitad:]) / (len(posts_agente) - mitad)
        print(f"\n📈 Tendencia: ", end="")
        if avg_despues > avg_antes * 1.1:
            print(f"↑ Mejorando ({avg_antes:.1f} → {avg_despues:.1f} avg likes)")
        elif avg_despues < avg_antes * 0.9:
            print(f"↓ Bajando ({avg_antes:.1f} → {avg_despues:.1f} avg likes) — varía el tema o formato")
        else:
            print(f"→ Estable ({avg_likes:.1f} avg likes)")

    # Estilo detectado
    estilo = memoria.get("estilo_aprendido", "")
    if estilo:
        print(f"\n🧠 Estilo detectado: {estilo[:120]}...")

    # Frases características
    frases = memoria.get("frases_caracteristicas", [])
    if frases:
        print(f"\n💬 Frases que usas:")
        for f in frases[:3]:
            print(f"   \"{f}\"")

    print("\n" + "="*55 + "\n")

if __name__ == "__main__":
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config/ejemplo_cliente.json"
    mostrar_analytics(config_path)
