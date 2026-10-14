@echo off
rem ============ PASO 1 de 3 ============
rem Abre el juego guardando cada textura que usa, y al cerrarlo las deja ya en PNG.
rem
rem Entra, llega a la pantalla que quieras cambiar, y CIERRA el juego.
rem No lo dejes abierto: guarda un archivo por textura y ocupa rapido.
rem
rem Al terminar tendras:  extracted-images\png\  con las imagenes listas para elegir

cd /d "%~dp0"
if not exist "%~dp0extracted-images" mkdir "%~dp0extracted-images"

rem El juego solo apunta los codigos de las texturas mientras su sistema de reemplazo esta
rem encendido, y eso exige que haya al menos un archivo en su carpeta textures. Este PNG de
rem 1 pixel lo enciende sin reemplazar nada.
python "%~dp0scripts\texpack_dump.py" --game "%~dp0.." --ensure-marker

cd /d "%~dp0.."
set BT3_TEX_DUMP=%~dp0extracted-images
set BT3_TEX_LOG=1

echo PASO 1: abriendo el juego y guardando sus texturas...
echo Cierra el juego cuando hayas visto la pantalla que te interesa.
echo.

rem Las dos salidas al mismo archivo: el juego reengancha su salida de errores a la consola
rem (plat_crash.c), asi que con "2>" solo, el archivo queda vacio.
Tenkaichi3Decomp.exe > "%~dp0extracted-images\texturas.log" 2>&1

echo.
echo Convirtiendo a PNG...
cd /d "%~dp0"
python "%~dp0scripts\texpack_dump.py" --game "%~dp0.." --work "%~dp0."

echo.
echo Listo. Mira extracted-images\png, copia las que quieras a selected-images
echo y ejecuta 2-upscale-images.bat
pause
