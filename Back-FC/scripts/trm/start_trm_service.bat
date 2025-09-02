@echo off
echo =====================================================
echo         SERVICIO TRM AUTOMATICO - BOLIVAR
echo                    PRODUCCION
echo =====================================================
echo.
echo Iniciando servicio de actualizacion automatica de TRM...
echo El servicio se ejecutara diariamente a las 19:00 (7:00 PM)
echo Hora de Colombia - Para obtener TRM del dia siguiente
echo.
echo Para detener el servicio, presiona Ctrl+C
echo.

cd /d "%~dp0"
cd ..

:: Activar entorno virtual
call "..\..\.venv\Scripts\activate.bat"

:: Ejecutar scheduler de producción
python scripts/trm_scheduler_simple.py

pause
