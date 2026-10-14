@echo off
rem ============ PASO 3 de 3 ============
rem Mete en el juego las imagenes mejoradas de "selected-images".
rem Les pone el nombre en clave que el juego exige (lo saca de extracted-images\texturas.log)
rem y las deja en la carpeta "textures" DEL JUEGO, que es donde el juego las busca.
rem
rem Para quitarlas: borra lo que haya en ..\textures (menos 0-0-0.png y README.txt)
cd /d "%~dp0"
python "%~dp0scripts\texpack_install.py" --game "%~dp0.." --work "%~dp0."
echo.
echo Si todo fue bien, abre el juego normal y mira el resultado.
pause
