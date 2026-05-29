"""
Dashboard de analytics del agente LinkedIn.
Muestra qué posts funcionaron mejor, qué temas tienen más engagement,
y cuándo es mejor publicar.

Uso: python analytics.py config/ejemplo_cliente.json
"""
import json
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

sys.path.insert(0, ".")
from memory.memory import cargar_memoria

def mostrar_analytics(config_path: str):
    with open(config_path) as f:
        config = json.load(f)

    nombre = config.get("nombre", "usuario")
    memoria = cargar_memoria(nombre)
    posts = memoria.get("posts_publicados", [])

    if not posts:
        print("No hay posts registrados todavía.")
        return

    posts_con_datos = [p for p in posts if p["fecha"] != "importado"]

    print("\n" + "="*55)
    print(f"  ANALYTICS — {nombre.upper()}")
    print("="*55)

    # Total de posts
    print(f"\n📊 Posts publicados: {len(posts_con_datos)}")
    print(f"   Posts importados (historial): {len(posts) - len(posts_con_datos)}")

    if not posts_con_datos:
        print("\nAún no hay posts publicados con el agente.")
        print("Los analytics aparecerán después del primer post.\n")
        return

    # Engagement total
    total_likes = sum(p["engagement"]["likes"] for p in posts_con_datos)
    total_comentarios = sum(p["engagement"]["comentarios"] for p in posts_con_datos)
    avg_likes = total_likes / len(posts_con_datos) if posts_con_datos else 0
    avg_comentarios = total_comentarios / len(posts_con_datos) if posts_con_datos else 0

    print(f"\n❤️  Total likes: {total_likes} (promedio: {avg_likes:.1f} por post)")
    print(f"💬  Total comentarios: {total_comentarios} (promedio: {avg_comentarios:.1f} por post)")

    # Top 3 posts con más likes
    top_posts = sorted(posts_con_datos, key=lambda p: p["engagement"]["likes"], reverse=True)[:3]
    if any(p["engagement"]["likes"] > 0 for p in top_posts):
        print("\n🏆 Top posts por likes:")
        for i, post in enumerate(top_posts, 1):
            likes = post["engagement"]["likes"]
            comentarios = post["engagement"]["comentarios"]
            preview = post["post"][:70].replace("\n", " ")
            print(f"   {i}. [{likes}❤️  {comentarios}💬] {preview}...")

    # Temas exitosos
    temas = memoria.get("temas_exitosos", [])
    if temas:
        print(f"\n✅ Temas que funcionan ({len(temas)}):")
        for tema in temas[:5]:
            print(f"   • {tema[:60]}...")

    # Tendencia: ¿está mejorando?
    if len(posts_con_datos) >= 4:
        mitad = len(posts_con_datos) // 2
        primera_mitad = posts_con_datos[:mitad]
        segunda_mitad = posts_con_datos[mitad:]
        avg_primera = sum(p["engagement"]["likes"] for p in primera_mitad) / len(primera_mitad)
        avg_segunda = sum(p["engagement"]["likes"] for p in segunda_mitad) / len(segunda_mitad)

        print(f"\n📈 Tendencia de engagement:")
        if avg_segunda > avg_primera:
            mejora = ((avg_segunda - avg_primera) / max(avg_primera, 0.1)) * 100
            print(f"   ↑ Mejorando {mejora:.0f}% vs tus primeros posts")
        elif avg_segunda < avg_primera:
            print(f"   ↓ Bajando vs tus primeros posts — prueba variar el tema o formato")
        else:
            print(f"   → Estable")

    # Estilo aprendido
    estilo = memoria.get("estilo_aprendido", "")
    if estilo:
        print(f"\n🧠 Tu estilo detectado:")
        print(f"   {estilo[:150]}...")

    # Frases características
    frases = memoria.get("frases_caracteristicas", [])
    if frases:
        print(f"\n💬 Frases que usas:")
        for frase in frases[:4]:
            print(f"   \"{frase}\"")

    print("\n" + "="*55 + "\n")

if __name__ == "__main__":
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config/ejemplo_cliente.json"
    mostrar_analytics(config_path)
