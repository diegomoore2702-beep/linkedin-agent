# Guía: Automatiza tus posts de LinkedIn con IA

**Tiempo estimado:** 20-30 minutos  
**Lo que necesitas:** VS Code instalado, $5 en créditos de Anthropic

Abre la terminal en VS Code con `Ctrl + J` (Windows) o `Cmd + J` (Mac) y sigue los pasos.

---

## Paso 1 — Instalar Python

**Mac:**
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
Cuando termine:
```bash
brew install python
```

**Windows (PowerShell como administrador):**
```powershell
winget install Python.Python.3.12
```

Verifica que quedó bien:
```bash
python --version
```
Debe mostrarte algo como `Python 3.12.x`.

---

## Paso 2 — Obtener tu API Key de Anthropic

1. Ve a [console.anthropic.com](https://console.anthropic.com) y crea una cuenta
2. Ve a **Plans & Billing** y carga $5
3. Ve a **API Keys** → **Create Key**
4. Copia la key — empieza con `sk-ant-...`

---

## Paso 3 — Descargar el agente

```bash
git clone https://github.com/diegomoore2702-beep/linkedin-agent.git
cd linkedin-agent
```

---

## Paso 4 — Guardar tu API Key

**Mac:**
```bash
echo 'export ANTHROPIC_API_KEY="sk-ant-PEGA-TU-KEY-AQUI"' >> ~/.zprofile
source ~/.zprofile
```

**Windows (PowerShell):**
```powershell
setx ANTHROPIC_API_KEY "sk-ant-PEGA-TU-KEY-AQUI"
```
Cierra y vuelve a abrir la terminal después de esto.

---

## Paso 5 — Instalar las dependencias

```bash
pip install anthropic feedparser apscheduler python-dotenv playwright
playwright install chromium
```

Esto puede tardar 2-3 minutos.

---

## Paso 6 — Configurar tu perfil

Abre el archivo de configuración:

**Mac:**
```bash
open config/ejemplo_cliente.json
```

**Windows:**
```powershell
notepad config\ejemplo_cliente.json
```

Edítalo con tu información:

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

Guarda con `Ctrl+S`.

---

## Paso 7 — Generar tu primer post

```bash
python main.py config/ejemplo_cliente.json --solo-generar
```

El agente va a:
1. Buscar tendencias del día en tu industria
2. Generar un post en tu tono
3. Guardarlo en la carpeta `posts/`

Si el post te gusta, cópialo y publícalo manualmente en LinkedIn.

---

## Paso 8 — Publicación automática (mientras duermes)

Agrega tus credenciales de LinkedIn en el JSON:

```json
"linkedin_email": "tu@email.com",
"linkedin_password": "tu_contraseña"
```

La hora de publicación ya está en el JSON — cámbiala si quieres:

```json
"hora_publicacion": "08:00"
```

Luego corre el scheduler:

```bash
python scheduler.py config/ejemplo_cliente.json
```

Verás algo así:
```
2026-05-28 — Scheduler activo — publicará cada día a las 08:00
2026-05-28 — Deja esta ventana abierta. Ctrl+C para detener.
```

**Deja la ventana de la terminal abierta y el computador encendido.** El agente publicará solo a la hora configurada todos los días.

Para detenerlo: `Ctrl + C`

---

## Errores comunes

**"python: command not found"**
```bash
brew install python
```

**"anthropic: module not found"**
```bash
pip install anthropic
```

**"AuthenticationError"**  
→ Tu API key está mal o no tiene créditos. Verifica en [console.anthropic.com](https://console.anthropic.com).

**"git: command not found"**

Mac:
```bash
xcode-select --install
```
Windows:
```powershell
winget install Git.Git
```

---

## ¿Qué sigue?

Una vez que el agente genera posts que te gustan, puedes programarlo para que corra solo cada mañana. Escríbele a Diego para ese paso.
