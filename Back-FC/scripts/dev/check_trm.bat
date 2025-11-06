@echo off
title Verificar Estado TRM
echo.
echo ==========================================
echo   VERIFICACION DE ESTADO TRM
echo ==========================================
echo.

cd /d "c:\Users\1006509625\Desktop\PROYECTO\Back-FC"
python check_trm_status.py

echo.
echo ==========================================
echo Presione cualquier tecla para continuar...
pause