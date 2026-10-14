@echo off
rem ============ PASO 2 de 3 ============
rem Mejora con IA (tu tarjeta grafica) las imagenes de la carpeta "selected-images".
rem   selected-images\originals\ -> se guardan los originals intactos
rem   selected-images\            -> quedan las mejoradas, listas para el paso 4
rem
rem Por defecto x4. Para x8 abre una consola aqui y escribe:  2-upscale-images.bat 8
cd /d "%~dp0"
set ESCALA=%1
if "%ESCALA%"=="" set ESCALA=4
python "%~dp0scripts\texpack_upscale.py" --game "%~dp0.." --work "%~dp0." --scale %ESCALA%
echo.
echo Ahora ejecuta 3-install-textures.bat
pause
