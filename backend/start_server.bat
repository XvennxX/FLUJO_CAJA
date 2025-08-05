@echo off
REM Script para iniciar el servidor de FastAPI con configuracion automatica
echo ================================
echo  FLUJO DE CAJA - BACKEND SERVER
echo ================================
echo.

cd /d "%~dp0"
echo Configurando variables de entorno...
set "PYTHONPATH=%cd%"

echo Iniciando servidor FastAPI en http://127.0.0.1:8000
echo Documentacion API: http://127.0.0.1:8000/docs
echo.
echo Presiona Ctrl+C para detener el servidor
echo.

python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000

pause
