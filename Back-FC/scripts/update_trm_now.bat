@echo off
echo =====================================================
echo       ACTUALIZACION MANUAL TRM - BOLIVAR
echo =====================================================
echo.
echo Actualizando TRM manualmente...
echo.

cd /d "%~dp0"
cd ..

:: Activar entorno virtual
call "..\..\.venv\Scripts\activate.bat"

:: Ejecutar scraper una vez
python scripts/trm_scraper.py

echo.
echo =====================================================
echo           ACTUALIZACION COMPLETADA
echo =====================================================
echo.

pause
