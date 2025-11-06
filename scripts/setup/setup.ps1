# Setup Script para Windows PowerShell
# Sistema de Flujo de Caja - Bolívar

Write-Host "🚀 Iniciando setup del Sistema de Flujo de Caja" -ForegroundColor Blue
Write-Host ""

# Verificar requisitos
Write-Host "📋 Verificando requisitos previos..." -ForegroundColor Yellow

# Verificar Python
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python 3\.1[2-9]") {
        Write-Host "✅ Python $pythonVersion instalado" -ForegroundColor Green
    } else {
        Write-Host "❌ Python 3.12+ requerido. Versión actual: $pythonVersion" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Python no encontrado. Instala Python 3.12+" -ForegroundColor Red
    exit 1
}

# Verificar Node.js
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✅ Node.js $nodeVersion instalado" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js no encontrado. Instala Node.js 18+" -ForegroundColor Red
    exit 1
}

# Verificar PostgreSQL
try {
    $pgVersion = psql --version 2>&1
    Write-Host "✅ PostgreSQL instalado" -ForegroundColor Green
} catch {
    Write-Host "⚠️  PostgreSQL no encontrado. Asegúrate de tenerlo instalado" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📦 Configurando variables de entorno..." -ForegroundColor Yellow

# Copiar archivos .env.example
if (-not (Test-Path "Back-FC\.env")) {
    Copy-Item "Back-FC\.env.example" "Back-FC\.env"
    Write-Host "✅ Creado Back-FC\.env" -ForegroundColor Green
}

if (-not (Test-Path "Front-FC\.env")) {
    Copy-Item "Front-FC\.env.example" "Front-FC\.env"
    Write-Host "✅ Creado Front-FC\.env" -ForegroundColor Green
}

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "✅ Creado .env" -ForegroundColor Green
}

Write-Host ""
Write-Host "📦 Instalando dependencias del backend..." -ForegroundColor Yellow
Set-Location Back-FC

# Crear entorno virtual
if (-not (Test-Path ".venv")) {
    python -m venv .venv
    Write-Host "✅ Entorno virtual creado" -ForegroundColor Green
}

# Activar entorno virtual e instalar dependencias
& .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -r requirements-dev.txt
Write-Host "✅ Dependencias del backend instaladas" -ForegroundColor Green

Set-Location ..

Write-Host ""
Write-Host "📦 Instalando dependencias del frontend..." -ForegroundColor Yellow
Set-Location Front-FC
npm install
Write-Host "✅ Dependencias del frontend instaladas" -ForegroundColor Green

Set-Location ..

Write-Host ""
Write-Host "✅ Setup completado!" -ForegroundColor Green
Write-Host ""
Write-Host "⚠️  IMPORTANTE: Edita los archivos .env con tus credenciales antes de continuar" -ForegroundColor Yellow
Write-Host ""
Write-Host "📚 Próximos pasos:" -ForegroundColor Cyan
Write-Host "  1. Edita Back-FC\.env con tus credenciales de base de datos"
Write-Host "  2. Edita Front-FC\.env si es necesario"
Write-Host "  3. Crea la base de datos PostgreSQL"
Write-Host "  4. Ejecuta las migraciones: cd Back-FC; alembic upgrade head"
Write-Host "  5. Inicia el backend: cd Back-FC; python run_server.py"
Write-Host "  6. Inicia el frontend: cd Front-FC; npm run dev"
Write-Host ""
Write-Host "📖 Lee docs\GETTING_STARTED.md para más información" -ForegroundColor Cyan
