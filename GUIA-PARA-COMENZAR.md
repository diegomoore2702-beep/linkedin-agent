# Guía: Automatiza tus posts de LinkedIn con IA

**Tiempo estimado:** 20-30 minutos  
**Lo que necesitas:** VS Code, Python, $5 en créditos de Anthropic

---

## Paso 1 — Instalar Python

Ve a [python.org/downloads](https://www.python.org/downloads) y descarga la versión más reciente.

Durante la instalación, **marca la casilla "Add Python to PATH"** — es importante.

Para verificar que quedó bien, abre la terminal en VS Code (`Ctrl + J` o `Cmd + J`) y escribe:
```
python --version
```
Debe mostrarte algo como `Python 3.12.x`.

---

## Paso 2 — Obtener tu API Key de Anthropic

1. Ve a [console.anthropic.com](https://console.anthropic.com)
2. Crea una cuenta (o entra si ya tienes)
3. Ve a **Plans & Billing** y carga $5
4. Ve a **API Keys** → **Create Key**
5. Copia la key — empieza con `sk-ant-...`

---

## Paso 3 — Descargar el agente

Descarga o clona esta carpeta en tu computador. Si no sabes cómo clonar, descarga el ZIP desde GitHub y descomprímelo.

En VS Code, abre la carpeta del proyecto: **File → Open Folder**.

---

## Paso 4 — Guardar tu API Key

En la terminal de VS Code, escribe según tu sistema:

**Mac:**
```bash
echo 'export ANTHROPIC_API_KEY="sk-ant-PEGA-TU-KEY-AQUI"' >> ~/.zprofile
source ~/.zprofile
```

**Windows (PowerShell):**
```powershell
setx ANTHROPIC_API_KEY "sk-ant-PEGA-TU-KEY-AQUI"
```
Cierra y vuelve a abrir VS Code después de esto.

---

## Paso 5 — Instalar las dependencias

En la terminal de VS Code:

```bash
pip install anthropic feedparser apscheduler python-dotenv playwright
playwright install chromium
```

Esto puede tardar 2-3 minutos.

---

## Paso 6 — Configurar tu perfil

Abre el archivo `config/ejemplo_cliente.json` y edítalo con tu información:

```json
{
  "nombre": "Tu Nombre",
  "industria": "tu industria (ej: marketing, finanzas, tecnología)",
  "tono": "cómo quieres sonar (ej: profesional pero cercano, directo, con humor)",
  "temas_clave": ["tema1", "tema2", "tema3"],
  "idioma": "español",
  "hora_publicacion": "08:00",
  "posts_por_semana": 5,
  "linkedin_email": "",
  "linkedin_password": ""
}
```

Guarda el archivo con `Ctrl+S`.

---

## Paso 7 — Generar tu primer post

En la terminal:

```bash
python main.py config/ejemplo_cliente.json --solo-generar
```

El agente va a:
1. Buscar tendencias del día en tu industria
2. Generar un post en tu tono
3. Guardarlo en la carpeta `posts/`

Si el post te gusta, ya puedes copiarlo y publicarlo manualmente en LinkedIn.

---

## Paso 8 — Publicación automática (opcional)

Si quieres que el agente publique solo, agrega tus credenciales de LinkedIn en el JSON:

```json
"linkedin_email": "tu@email.com",
"linkedin_password": "tu_contraseña"
```

Luego corre sin `--solo-generar`:

```bash
python main.py config/ejemplo_cliente.json
```

Te va a preguntar si confirmas antes de publicar.

---

## Errores comunes

**"python: command not found"**  
→ Python no está en el PATH. Reinstala marcando "Add Python to PATH".

**"anthropic: module not found"**  
→ Corre `pip install anthropic` en la terminal.

**"AuthenticationError"**  
→ Tu API key está mal o no tiene créditos. Verifica en console.anthropic.com.

---

## ¿Qué sigue?

Una vez que el agente genera posts que te gustan, puedes programarlo para que corra solo cada mañana. Escríbele a Diego para ese paso.
