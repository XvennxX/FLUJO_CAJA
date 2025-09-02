@echo off
REM Script de verificación completa del proyecto FLUJO_CAJA (Windows)

echo 🔍 Verificando estructura completa del proyecto FLUJO_CAJA...
echo ==================================================

echo.
echo 📁 Verificando estructura principal...
if exist "README.md" (echo ✅ README principal del proyecto) else (echo ❌ README principal del proyecto)
if exist "CHANGELOG.md" (echo ✅ Registro de cambios) else (echo ❌ Registro de cambios)
if exist "LICENSE" (echo ✅ Archivo de licencia) else (echo ❌ Archivo de licencia)
if exist ".gitignore" (echo ✅ Configuración de Git) else (echo ❌ Configuración de Git)
if exist "docs\" (echo ✅ Directorio de documentación global) else (echo ❌ Directorio de documentación global)
if exist "Back-FC\" (echo ✅ Directorio del backend) else (echo ❌ Directorio del backend)
if exist "Front-FC\" (echo ✅ Directorio del frontend) else (echo ❌ Directorio del frontend)

echo.
echo 📚 Verificando documentación global...
if exist "docs\INSTALACION.md" (echo ✅ Guía de instalación completa) else (echo ❌ Guía de instalación completa)
if exist "docs\CONFIGURACION.md" (echo ✅ Documentación de configuración) else (echo ❌ Documentación de configuración)
if exist "docs\API.md" (echo ✅ Documentación de API) else (echo ❌ Documentación de API)

echo.
echo 🐍 Verificando backend...
if exist "Back-FC\app\" (echo ✅ Código principal del backend) else (echo ❌ Código principal del backend)
if exist "Back-FC\scripts\" (echo ✅ Scripts organizados del backend) else (echo ❌ Scripts organizados del backend)
if exist "Back-FC\docs\" (echo ✅ Documentación del backend) else (echo ❌ Documentación del backend)
if exist "Back-FC\README.md" (echo ✅ README del backend) else (echo ❌ README del backend)
if exist "Back-FC\requirements.txt" (echo ✅ Dependencias Python) else (echo ❌ Dependencias Python)
if exist "Back-FC\.gitignore" (echo ✅ Git ignore del backend) else (echo ❌ Git ignore del backend)

echo.
echo 📦 Verificando scripts del backend...
if exist "Back-FC\scripts\trm\" (echo ✅ Scripts de TRM) else (echo ❌ Scripts de TRM)
if exist "Back-FC\scripts\setup\" (echo ✅ Scripts de configuración inicial) else (echo ❌ Scripts de configuración inicial)
if exist "Back-FC\scripts\migrations\" (echo ✅ Scripts de migraciones) else (echo ❌ Scripts de migraciones)
if exist "Back-FC\scripts\utils\" (echo ✅ Scripts de utilidades) else (echo ❌ Scripts de utilidades)

echo.
echo ⚛️ Verificando frontend...
if exist "Front-FC\src\" (echo ✅ Código fuente React) else (echo ❌ Código fuente React)
if exist "Front-FC\scripts\" (echo ✅ Scripts organizados del frontend) else (echo ❌ Scripts organizados del frontend)
if exist "Front-FC\docs\" (echo ✅ Documentación del frontend) else (echo ❌ Documentación del frontend)
if exist "Front-FC\README.md" (echo ✅ README del frontend) else (echo ❌ README del frontend)
if exist "Front-FC\package.json" (echo ✅ Dependencias Node.js) else (echo ❌ Dependencias Node.js)
if exist "Front-FC\.gitignore" (echo ✅ Git ignore del frontend) else (echo ❌ Git ignore del frontend)
if exist "Front-FC\vite.config.ts" (echo ✅ Configuración de Vite) else (echo ❌ Configuración de Vite)
if exist "Front-FC\tailwind.config.js" (echo ✅ Configuración de Tailwind) else (echo ❌ Configuración de Tailwind)

echo.
echo 🔧 Verificando scripts del frontend...
if exist "Front-FC\scripts\build\" (echo ✅ Scripts de construcción) else (echo ❌ Scripts de construcción)
if exist "Front-FC\scripts\deploy\" (echo ✅ Scripts de despliegue) else (echo ❌ Scripts de despliegue)
if exist "Front-FC\scripts\utils\" (echo ✅ Scripts de utilidades) else (echo ❌ Scripts de utilidades)

echo.
echo 🔍 Verificando archivos de configuración...

REM Verificar entorno virtual
if exist ".venv\" (
    echo ✅ Entorno virtual Python ^(.venv^)
) else (
    echo ⚠️  Entorno virtual no encontrado - crear con: python -m venv .venv
)

REM Verificar node_modules
if exist "Front-FC\node_modules\" (
    echo ✅ Dependencias Node.js instaladas
) else (
    echo ⚠️  Dependencias Node.js no instaladas - ejecutar: cd Front-FC ^&^& npm install
)

REM Verificar .env
if exist "Back-FC\.env" (
    echo ✅ Archivo .env del backend configurado
) else (
    echo ⚠️  Archivo .env del backend no encontrado - crear según documentación
)

echo.
echo 📊 Resumen del proyecto...

REM Verificar Git
if exist ".git\" (
    echo ✅ Repositorio Git inicializado
) else (
    echo ⚠️  No es un repositorio Git
)

echo.
echo 🚀 Comandos de inicio rápido...
echo Backend:
echo   cd Back-FC
echo   .venv\Scripts\activate
echo   python run_server.py
echo.
echo Frontend:
echo   cd Front-FC
echo   npm install ^(si es necesario^)
echo   npm run dev
echo.

echo 📚 URLs importantes...
echo Frontend: http://localhost:5000
echo Backend API: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.

echo ==================================================
echo ✨ Verificación completada!

pause
