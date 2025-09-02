@echo off
echo =====================================================
echo       ACTUALIZACION MANUAL TRM - BOLIVAR
echo =====================================================
echo.
echo Verificando y actualizando TRMs faltantes...
echo.

cd /d "%~dp0"
cd ..\..

:: Activar entorno virtual
call ".venv\Scripts\activate.bat"

:: Ejecutar script de actualizacion de TRMs faltantes
python scripts\trm\update_missing_trm.py

echo.
echo =====================================================
echo           ACTUALIZACION COMPLETADA
echo =====================================================
echo.

pause
