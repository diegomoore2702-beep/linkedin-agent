# Guía completa — Agente de LinkedIn con IA

Hola 👋 Esta guía te lleva desde cero hasta tener el agente funcionando.
No necesitas saber programar. Solo sigue los pasos en orden.

**Tiempo estimado:** 40 minutos la primera vez.

---

## ¿Qué va a hacer este agente?

Cada día, a la hora que tú elijas, el agente va a:
- Buscar tendencias del día en tu industria
- Escribir un post que suena como tú (no como IA)
- Crear un carrusel PDF con tu foto y tus colores
- Publicarlo en LinkedIn
- Dejar el primer comentario solo para aumentar el alcance

Tú no tienes que hacer nada — solo la configuración inicial una vez.

---

## PARTE 1 — Instalar lo que necesitas

### 1.1 — Abrir la terminal

La terminal es una ventana donde escribes comandos.

- **Mac:** Presiona `Cmd + Espacio`, escribe `Terminal` y abre la app
- **Windows:** Presiona la tecla Windows, escribe `PowerShell`, click derecho → *Ejecutar como administrador*

Deja esa ventana abierta durante toda la instalación.

---

### 1.2 — Instalar Python

Python es el lenguaje en el que está hecho el agente.

**Mac — copia y pega este comando en la terminal:**
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
Cuando termine (puede tardar 5 minutos), escribe:
```bash
brew install python
```

**Windows — copia y pega en PowerShell:**
```powershell
winget install Python.Python.3.12
```

**Verifica que quedó bien** — escribe esto y presiona Enter:
```bash
python --version
```
Debe aparecer algo como `Python 3.12.3`. Si aparece eso, está perfecto.

---

### 1.3 — Crear cuenta en Anthropic y obtener tu API Key

El agente usa la IA de Anthropic para escribir los posts. Necesitas cargarle $5 una sola vez.

1. Ve a **console.anthropic.com** y crea una cuenta
2. Entra a **Plans & Billing** → carga $5 con tu tarjeta
3. Ve a **API Keys** → click en **Create Key**
4. Copia el código que aparece — empieza con `sk-ant-...`
   ⚠️ *Guárdalo en un bloc de notas, solo aparece una vez*

---

### 1.4 — Guardar la API Key

Esto hace que el agente pueda usar la IA de Anthropic.

**Mac — reemplaza el texto y pega en la terminal:**
```bash
echo 'export ANTHROPIC_API_KEY="sk-ant-PEGA-TU-KEY-AQUI"' >> ~/.zprofile
source ~/.zprofile
```

**Windows — reemplaza el texto y pega en PowerShell:**
```powershell
setx ANTHROPIC_API_KEY "sk-ant-PEGA-TU-KEY-AQUI"
```
Después de esto, cierra la terminal y ábrela de nuevo.

---

### 1.5 — Descargar el agente

Esto descarga todos los archivos del agente a tu computador.

```bash
git clone https://github.com/diegomoore2702-beep/linkedin-agent.git
cd linkedin-agent
```

Si te dice que `git` no está instalado:

- **Mac:** `xcode-select --install`
- **Windows:** `winget install Git.Git` (luego cierra y abre la terminal de nuevo)

---

### 1.6 — Instalar las dependencias

Las dependencias son las herramientas que el agente necesita para funcionar.

```bash
pip install -r requirements.txt
playwright install chromium
```

Esto puede tardar 3-5 minutos. Es normal que aparezca mucho texto.

---

## PARTE 2 — Configurar el agente

### 2.1 — Agregar tu foto

El agente pone tu foto en los carruseles. Necesitas copiar una foto tuya (preferiblemente la del perfil de LinkedIn) a la carpeta del agente.

**Mac:**
```bash
open config/
```
Se abre una carpeta en el Finder. Arrastra tu foto ahí adentro y renómbrala exactamente así: `foto.jpg`

**Windows:**
```powershell
explorer config\
```
Arrastra tu foto a esa carpeta y renómbrala `foto.jpg`.

---

### 2.2 — Llenar tu perfil

Aquí le dices al agente quién eres y cómo hablas.

**Mac:**
```bash
open config/ejemplo_cliente.json
```

**Windows:**
```powershell
notepad config\ejemplo_cliente.json
```

Se abre un archivo de texto. Reemplaza cada campo con tu información:

```json
{
  "nombre": "Tu Nombre Completo",
  "industria": "tu industria (ej: marketing, moda, tecnología, finanzas)",
  "tono": "cómo hablas tú (ej: casual y cercana, directa, con humor, profesional)",
  "temas_clave": ["tema 1", "tema 2", "tema 3"],
  "idioma": "español",
  "hora_publicacion": "08:00",
  "linkedin_email": "tu email de LinkedIn",
  "linkedin_password": "tu contraseña de LinkedIn",
  "instagram_username": "",
  "instagram_password": "",
  "estilo_carrusel": "clasico",
  "card_fondo": "#0D0D0D",
  "card_acento": "#C9A02C",
  "card_texto": "#FFFFFF"
}
```

**Ejemplos de tono:**
- `"cercana, curiosa, sin tecnicismos"`
- `"directa y sin rodeos, con humor ocasional"`
- `"profesional pero humana, cuento historias"`

**Colores del carrusel** — cambia `card_acento` por el que quieras:
- Dorado: `#C9A02C`
- Rojo: `#E94560`
- Azul: `#00B4D8`
- Morado: `#7B2FBE`
- Verde: `#10B981`
- Rosa: `#EC4899`

Guarda el archivo con `Ctrl+S` (o `Cmd+S` en Mac).

---

### 2.3 — Aprender tu estilo (muy recomendado)

Si ya tienes posts en LinkedIn, el agente los lee y aprende exactamente cómo escribes. Desde el primer día sonará como tú.

```bash
python importer.py config/ejemplo_cliente.json
```

Se va a abrir el navegador con LinkedIn. Si te pide verificación o captcha, complétala tú manualmente. Cuando estés en el feed (la pantalla principal de LinkedIn), vuelve a la terminal y presiona **Enter**.

---

## PARTE 3 — Probar que funciona

### 3.1 — Generar tu primer post sin publicar

Este comando genera el post y el carrusel pero **no publica nada**. Úsalo para ver cómo quedan antes de publicar de verdad.

```bash
python main.py config/ejemplo_cliente.json --solo-generar
```

El agente va a:
1. Buscar tendencias del día
2. Elegir el mejor formato para el post
3. Generar 2 versiones y elegir la mejor
4. Puntuar el post — si es menor a 7/10 genera otro automáticamente
5. Crear el carrusel con tu foto

Cuando termine, revisa:
- El post: aparece en la terminal
- El carrusel: está en la carpeta `posts/carruseles/` — ábrelo para verlo

Si el post no suena como tú, ajusta el campo `tono` en el config y vuelve a intentarlo.

---

### 3.2 — Publicar en LinkedIn por primera vez

Cuando estés lista para publicar de verdad:

```bash
python main.py config/ejemplo_cliente.json
```

Lo que va a pasar:
1. Genera el post y el carrusel
2. Se abre LinkedIn en el navegador con el texto ya escrito en el modal
3. Se abre el Finder con el PDF del carrusel — arrástralo al modal de LinkedIn
4. Tú revisas el post, le das **Publicar** en LinkedIn
5. Vuelves a la terminal y presionas **Enter**
6. El agente espera 3 minutos y deja el primer comentario automáticamente

**La primera vez** te va a pedir que te loguees en LinkedIn. Hazlo normalmente. Después guarda la sesión y ya no te lo pide por ~30 días.

---

## PARTE 4 — Publicación automática diaria

Cuando todo está funcionando bien, activa el modo automático:

```bash
python scheduler.py config/ejemplo_cliente.json
```

**Deja esa ventana de la terminal abierta y el computador encendido.** El agente va a publicar solo todos los días a la hora que configuraste.

Para detenerlo en cualquier momento: `Ctrl + C`

---

## PARTE 5 — Ver qué está funcionando

Después de publicar varios posts, puedes ver tus estadísticas:

```bash
python analytics.py config/ejemplo_cliente.json
```

Muestra tus likes totales, los posts que más engancharon, los temas que funcionan, y si tu engagement está mejorando o no.

---

## Comandos de referencia rápida

| Para qué | Comando |
|---|---|
| Primera configuración — aprender tu estilo | `python importer.py config/ejemplo_cliente.json` |
| Probar sin publicar | `python main.py config/ejemplo_cliente.json --solo-generar` |
| Publicar con tema específico | `python main.py config/ejemplo_cliente.json --tema "de qué quieres hablar"` |
| Cambiar estilo del carrusel | `python main.py config/ejemplo_cliente.json --estilo minimalista` |
| Usar otra foto | `python main.py config/ejemplo_cliente.json --foto config/otra_foto.jpg` |
| Publicar normalmente | `python main.py config/ejemplo_cliente.json` |
| Ver estadísticas | `python analytics.py config/ejemplo_cliente.json` |
| Activar publicación automática diaria | `python scheduler.py config/ejemplo_cliente.json` |

---

## Errores comunes

**"python: command not found"**  
→ Python no está instalado. Ve al Paso 1.2.

**"No module named X"**  
→ Falta instalar dependencias:
```bash
pip install -r requirements.txt
```

**"AuthenticationError"**  
→ Tu API key está mal escrita o sin créditos. Revisa en console.anthropic.com.

**"git: command not found"**  
Mac: `xcode-select --install`  
Windows: `winget install Git.Git`

**LinkedIn pide verificación en el navegador**  
→ Es normal la primera vez. Complétala manualmente y presiona Enter en la terminal. Después ya no vuelve a pedirla.

**El carrusel no tiene mi foto**  
→ Verifica que la foto esté en `config/foto.jpg` con ese nombre exacto.

---

## ¿Necesitas ayuda?

Escríbele a Diego — él configuró todo esto y puede ayudarte en cualquier paso.
