@echo off
title Servicio TRM Automatico - Sistema de Flujo de Caja
echo.
echo ==========================================
echo   SERVICIO TRM AUTOMATICO
echo   Sistema de Flujo de Caja
echo ==========================================
echo.
echo Iniciando servicio de actualizacion automatica de TRM...
echo.
echo IMPORTANTE:
echo - El servicio se ejecuta de 8:00 AM a 6:00 PM
echo - Actualiza TRMs cada 30 minutos
echo - Para detener presione Ctrl+C
echo.
echo ==========================================
echo.

cd /d "c:\Users\1006509625\Desktop\PROYECTO\Back-FC"
python trm_service.py

pause