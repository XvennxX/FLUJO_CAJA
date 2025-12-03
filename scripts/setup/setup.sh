#!/bin/bash
# Setup Script para Linux/Mac
# Sistema de Flujo de Caja - Bolívar

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Iniciando setup del Sistema de Flujo de Caja${NC}"
echo ""

# Verificar requisitos
echo -e "${YELLOW}📋 Verificando requisitos previos...${NC}"

# Verificar Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✅ $PYTHON_VERSION instalado${NC}"
else
    echo -e "${RED}❌ Python 3.12+ no encontrado${NC}"
    exit 1
fi

# Verificar Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✅ Node.js $NODE_VERSION instalado${NC}"
else
    echo -e "${RED}❌ Node.js no encontrado. Instala Node.js 18+${NC}"
    exit 1
fi

# Verificar PostgreSQL
if command -v psql &> /dev/null; then
    echo -e "${GREEN}✅ PostgreSQL instalado${NC}"
else
    echo -e "${YELLOW}⚠️  PostgreSQL no encontrado. Asegúrate de tenerlo instalado${NC}"
fi

echo ""
echo -e "${YELLOW}📦 Configurando variables de entorno...${NC}"

# Copiar archivos .env.example
if [ ! -f "Back-FC/.env" ]; then
    cp Back-FC/.env.example Back-FC/.env
    echo -e "${GREEN}✅ Creado Back-FC/.env${NC}"
fi

if [ ! -f "Front-FC/.env" ]; then
    cp Front-FC/.env.example Front-FC/.env
    echo -e "${GREEN}✅ Creado Front-FC/.env${NC}"
fi

if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}✅ Creado .env${NC}"
fi

echo ""
echo -e "${YELLOW}📦 Instalando dependencias del backend...${NC}"
cd Back-FC

# Crear entorno virtual
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo -e "${GREEN}✅ Entorno virtual creado${NC}"
fi

# Activar entorno virtual e instalar dependencias
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
echo -e "${GREEN}✅ Dependencias del backend instaladas${NC}"

cd ..

echo ""
echo -e "${YELLOW}📦 Instalando dependencias del frontend...${NC}"
cd Front-FC
npm install
echo -e "${GREEN}✅ Dependencias del frontend instaladas${NC}"

cd ..

echo ""
echo -e "${GREEN}✅ Setup completado!${NC}"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANTE: Edita los archivos .env con tus credenciales antes de continuar${NC}"
echo ""
echo -e "${CYAN}📚 Próximos pasos:${NC}"
echo "  1. Edita Back-FC/.env con tus credenciales de base de datos"
echo "  2. Edita Front-FC/.env si es necesario"
echo "  3. Crea la base de datos PostgreSQL"
echo "  4. Ejecuta las migraciones: cd Back-FC && source .venv/bin/activate && alembic upgrade head"
echo "  5. Inicia el backend: cd Back-FC && python run_server.py"
echo "  6. Inicia el frontend: cd Front-FC && npm run dev"
echo ""
echo -e "${CYAN}📖 Lee docs/GETTING_STARTED.md para más información${NC}"
