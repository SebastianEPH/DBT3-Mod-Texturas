# DBT3 Mod Texturas

Herramientas para **mejorar las texturas** del port de PC de *Dragon Ball Z: Budokai Tenkaichi 3*
([Tenkaichi3Decomp](https://github.com/z3xox/Tenkaichi3Decomp)): sacarlas del juego, agrandarlas con
inteligencia artificial y devolverlas en alta resolución.

El juego no se modifica en ningún momento: las texturas de reemplazo viven en una carpeta aparte, y
quitarlas devuelve el juego a su estado original.

> **Este repositorio no contiene datos del juego.** Las imágenes salen de tu propia copia.

---

## No es un parche: el juego ya lo soporta

El port **ya trae de fábrica un sistema de texturas de reemplazo**, compatible con el del emulador PCSX2.
Lo dice su propio `textures/README.txt`:

> *Texture packs go here. Put a pack's replacement textures into this folder... The files have to be named
> the way the PCSX2 emulator names texture replacements for this game.*

Incluso tiene un interruptor propio en **F1 › Video** para encenderlo y apagarlo.

El problema es que ese sistema exige dos cosas incómodas, y es justo lo que automatizan estas herramientas:

1. **Conseguir las imágenes originales**, que dentro del juego están comprimidas y en el formato del chip
   gráfico de PS2.
2. **Saber el nombre que debe llevar cada reemplazo**: el juego no las identifica por su nombre, sino por un
   código calculado a partir de sus datos (`1dd4c761…-56e3d446…-00005e54.png`).

---

## Qué toca cada paso

```
                     escribe en                        lee de
1-extract-textures   extracted-images/                 el juego (mientras lo juegas)
2-upscale-images     selected-images/                  selected-images/
3-install-textures   <juego>/textures/   ←── el juego mira aquí al arrancar
```

**Solo el paso 3 escribe dentro del juego**, y únicamente en su carpeta `textures`, que es la que el port
reserva para esto. Nada más del juego se toca: ni sus datos, ni sus archivos, ni el ejecutable.

---

## Requisitos

- **El port ya instalado y funcionando** ([Tenkaichi3Decomp](https://github.com/z3xox/Tenkaichi3Decomp)).
- **[Python 3](https://www.python.org/downloads/)** — lo único que instalas tú.
  Al instalarlo marca *Add Python to PATH*.

| | Qué es | Cómo se consigue |
|---|---|---|
| **Pillow** | librería de imágenes | se instala sola con `pip` la primera vez |
| **Real-ESRGAN** | el agrandado con IA (~45 MB, portable) | lo descargas tú, solo si usas el paso 2 |

**Real-ESRGAN** se descarga de [su página](https://github.com/xinntao/Real-ESRGAN/releases) (la versión
*portable* para Windows, `realesrgan-ncnn-vulkan`) y se descomprime en una carpeta `realesrgan` dentro de
este proyecto. No instala nada en el sistema. Si no está, el paso 2 te lo dice y se detiene; **ningún script
descarga nada por su cuenta**.

Para ese paso necesitas una **tarjeta gráfica con Vulkan** (cualquiera de los últimos 10 años).
No hace falta CUDA ni drivers aparte.

> El paso 2 es **opcional**: si prefieres agrandar con Upscayl, chaiNNer, Photoshop o GIMP, hazlo por tu
> cuenta y guarda el resultado en `selected-images` con el mismo nombre. El paso 3 funciona igual.

---

## Dónde se instala

**Esta carpeta va dentro de la carpeta del juego**, al mismo nivel que `Tenkaichi3Decomp.exe`:

```
Tenkaichi3Decomp/                  ← la carpeta del juego
├── Tenkaichi3Decomp.exe
├── gamedata/
├── textures/                      ← del juego: aquí acaban las mejoradas (paso 3)
└── DBT3-Mod-Texturas/             ← ESTA carpeta, aquí dentro
    ├── 1-extract-textures.bat
    ├── 2-upscale-images.bat
    ├── 3-install-textures.bat
    ├── scripts/
    ├── extracted-images/
    └── selected-images/
```

Es importante que quede **ahí dentro**: los scripts buscan el juego en la carpeta de arriba. Dentro de ese
esquema todo son rutas relativas, así que puedes mover el juego de sitio sin romper nada.

---

## Uso

### 1 · Sacar las texturas

```
1-extract-textures.bat
```

Abre el juego guardando cada imagen que usa. **Ve a la pantalla que quieras cambiar y cierra el juego.**
Al cerrarlo las convierte a PNG y borra los archivos en crudo.

> No lo dejes abierto mucho rato: guarda un archivo por textura y ocupa rápido.

Resultado: `extracted-images/png/`

### 2 · Elegir y agrandar

Mira `extracted-images/png`, elige las que quieras mejorar y **cópialas a `selected-images`
sin cambiarles el nombre**. Luego:

```
2-upscale-images.bat        ← x4 (por defecto)
2-upscale-images.bat 8      ← x8
```

Los originales se guardan en `selected-images/originals`.

### 3 · Instalar

```
3-install-textures.bat
```

Copia tus imágenes a **`<juego>/textures/`** con el nombre en clave que el juego espera. Ese es el único
momento en que se escribe algo dentro del juego.

Abre el juego y míralas. Dentro, **F1 › Video** tiene el interruptor del pack de texturas, para comparar
el antes y el después sin cerrar.

---

## Cómo deshacerlo

Borra los archivos de la carpeta **`textures` del juego**.

**Deja dentro `README.txt` y `0-0-0.png`.** Ese PNG de un píxel no reemplaza nada: está para encender el
sistema de reemplazo del juego, que es lo que hace que el paso 1 pueda averiguar los códigos. Lo crea el
paso 1 si no existe.

Borrar esas imágenes devuelve el juego exactamente a como estaba. Tus originales siguen en
`selected-images/originals` por si quieres rehacerlas con otra escala u otro modelo.

---

## Carpetas

| Carpeta | Qué es |
|---|---|
| `extracted-images/png/` | catálogo de imágenes para elegir *(borrable al acabar)* |
| `selected-images/` | **tu carpeta**: las que quieres mejorar |
| `selected-images/originals/` | copia intacta de las que mejoraste |
| `scripts/` | los programas que hacen el trabajo |

Las dos primeras tienen su contenido en `.gitignore`: son imágenes del juego y no deben subirse a un repo.

---

## Cosas que conviene saber

**Los nombres llevan el código y no se tocan.** Son del tipo:

```
tex_00061_256x512__ecac4e5eedfb7c45-3ec0a55b6e2b1a37-00006613.png
                   └─── el código con el que el juego la reconoce ───┘
```

Si la renombras, el paso 3 no sabrá qué textura es y la dejará fuera, avisándote.

**Mantén la proporción al agrandar.** Si la original es 256×512, usa 1024×2048. Si cambias la forma, la
imagen saldrá estirada dentro del juego, porque las coordenadas son relativas.

**Empieza por imágenes simples** — un fondo, una pared, el suelo. Las hojas con muchos dibujos juntos, y
sobre todo las de letras, pueden salir raras: el juego recorta trozos por posición exacta.

**La transparencia se convierte sola.** El juego usa una escala propia donde *opaco* es 128 y no 255. Por
eso las imágenes ya instaladas se ven «a medias» en el explorador de Windows: es correcto, no es un error.

**Elige el modelo con criterio.** Por defecto se usa `realesrgan-x4plus-anime`, adecuado para el dibujo de
este juego. Evita los modelos fotorrealistas: inventan poros y grano sobre colores planos. Se puede cambiar
con `--model`.

**El juego avisará de que sus datos están modificados.** Es normal y no afecta: el port comprueba sus
archivos al arrancar. Las texturas de reemplazo no cuentan para ese aviso.

---

## Opciones

Los `.bat` cubren el uso normal. Para afinar, los scripts se pueden llamar a mano:

```bash
python scripts/texpack_dump.py    --game <juego> --work . [--keep-raw] [--ensure-marker]
python scripts/texpack_upscale.py --game <juego> --work . [--scale 4] [--model <nombre>] [--exe <ruta>]
python scripts/texpack_install.py --game <juego> --work . [--dry-run]
```

`--game` es la carpeta del juego y `--work` la de este proyecto. `--dry-run` dice qué haría sin escribir nada.

---

## Créditos

- [Tenkaichi3Decomp](https://github.com/z3xox/Tenkaichi3Decomp) — el port de PC, que incluye el sistema de
  texturas de reemplazo sobre el que se apoya todo esto.
- [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN) — el agrandado con IA.

## Licencia

MIT — ver [LICENSE](LICENSE).

Este proyecto no está afiliado con los creadores, editores ni propietarios de los derechos del juego.
No distribuye material del juego: necesitas tu propia copia.
