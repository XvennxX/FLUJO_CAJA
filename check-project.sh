#!/bin/bash
# Script de verificación completa del proyecto FLUJO_CAJA

echo "🔍 Verificando estructura completa del proyecto FLUJO_CAJA..."
echo "=================================================="

PROJECT_ROOT=$(pwd)

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para verificar archivos
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✅${NC} $2"
        return 0
    else
        echo -e "${RED}❌${NC} $2"
        return 1
    fi
}

# Función para verificar directorios
check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✅${NC} $2"
        return 0
    else
        echo -e "${RED}❌${NC} $2"
        return 1
    fi
}

echo -e "${BLUE}📁 Verificando estructura principal...${NC}"
check_file "README.md" "README principal del proyecto"
check_file "CHANGELOG.md" "Registro de cambios"
check_file "LICENSE" "Archivo de licencia"
check_file ".gitignore" "Configuración de Git"
check_dir "docs" "Directorio de documentación global"
check_dir "Back-FC" "Directorio del backend"
check_dir "Front-FC" "Directorio del frontend"

echo ""
echo -e "${BLUE}📚 Verificando documentación global...${NC}"
check_file "docs/INSTALACION.md" "Guía de instalación completa"
check_file "docs/CONFIGURACION.md" "Documentación de configuración"
check_file "docs/API.md" "Documentación de API"

echo ""
echo -e "${BLUE}🐍 Verificando backend...${NC}"
check_dir "Back-FC/app" "Código principal del backend"
check_dir "Back-FC/scripts" "Scripts organizados del backend"
check_dir "Back-FC/docs" "Documentación del backend"
check_file "Back-FC/README.md" "README del backend"
check_file "Back-FC/requirements.txt" "Dependencias Python"
check_file "Back-FC/.gitignore" "Git ignore del backend"

echo ""
echo -e "${BLUE}📦 Verificando scripts del backend...${NC}"
check_dir "Back-FC/scripts/trm" "Scripts de TRM"
check_dir "Back-FC/scripts/setup" "Scripts de configuración inicial"
check_dir "Back-FC/scripts/migrations" "Scripts de migraciones"
check_dir "Back-FC/scripts/utils" "Scripts de utilidades"

echo ""
echo -e "${BLUE}⚛️ Verificando frontend...${NC}"
check_dir "Front-FC/src" "Código fuente React"
check_dir "Front-FC/scripts" "Scripts organizados del frontend"
check_dir "Front-FC/docs" "Documentación del frontend"
check_file "Front-FC/README.md" "README del frontend"
check_file "Front-FC/package.json" "Dependencias Node.js"
check_file "Front-FC/.gitignore" "Git ignore del frontend"
check_file "Front-FC/vite.config.ts" "Configuración de Vite"
check_file "Front-FC/tailwind.config.js" "Configuración de Tailwind"

echo ""
echo -e "${BLUE}🔧 Verificando scripts del frontend...${NC}"
check_dir "Front-FC/scripts/build" "Scripts de construcción"
check_dir "Front-FC/scripts/deploy" "Scripts de despliegue"
check_dir "Front-FC/scripts/utils" "Scripts de utilidades"

echo ""
echo -e "${BLUE}🔍 Verificando archivos de configuración...${NC}"

# Verificar si existe entorno virtual
if [ -d ".venv" ]; then
    echo -e "${GREEN}✅${NC} Entorno virtual Python (.venv)"
else
    echo -e "${YELLOW}⚠️${NC}  Entorno virtual no encontrado - crear con: python -m venv .venv"
fi

# Verificar node_modules en frontend
if [ -d "Front-FC/node_modules" ]; then
    echo -e "${GREEN}✅${NC} Dependencias Node.js instaladas"
else
    echo -e "${YELLOW}⚠️${NC}  Dependencias Node.js no instaladas - ejecutar: cd Front-FC && npm install"
fi

# Verificar archivos .env
if [ -f "Back-FC/.env" ]; then
    echo -e "${GREEN}✅${NC} Archivo .env del backend configurado"
else
    echo -e "${YELLOW}⚠️${NC}  Archivo .env del backend no encontrado - crear según documentación"
fi

echo ""
echo -e "${BLUE}📊 Resumen del proyecto...${NC}"

# Contar archivos de documentación
doc_count=$(find . -name "*.md" | wc -l)
echo "📄 Archivos de documentación: $doc_count"

# Verificar si es un repositorio Git
if [ -d ".git" ]; then
    echo -e "${GREEN}✅${NC} Repositorio Git inicializado"
    
    # Mostrar rama actual si Git está disponible
    if command -v git &> /dev/null; then
        current_branch=$(git branch --show-current 2>/dev/null)
        if [ ! -z "$current_branch" ]; then
            echo "🌿 Rama actual: $current_branch"
        fi
    fi
else
    echo -e "${YELLOW}⚠️${NC}  No es un repositorio Git"
fi

echo ""
echo -e "${BLUE}🚀 Comandos de inicio rápido...${NC}"
echo "Backend:"
echo "  cd Back-FC"
echo "  source .venv/bin/activate  # Linux/Mac"
echo "  .venv\\Scripts\\activate     # Windows"
echo "  python run_server.py"
echo ""
echo "Frontend:"
echo "  cd Front-FC"
echo "  npm install (si es necesario)"
echo "  npm run dev"
echo ""

echo -e "${BLUE}📚 URLs importantes...${NC}"
echo "Frontend: http://localhost:5000"
echo "Backend API: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""

echo "=================================================="
echo -e "${GREEN}✨ Verificación completada!${NC}"

# Verificar si ambos servidores pueden iniciarse (opcional)
if [ "$1" = "--test-servers" ]; then
    echo ""
    echo -e "${BLUE}🧪 Probando conectividad de servidores...${NC}"
    
    # Probar backend
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅${NC} Backend ejecutándose en puerto 8000"
    else
        echo -e "${YELLOW}⚠️${NC}  Backend no detectado en puerto 8000"
    fi
    
    # Probar frontend
    if curl -s http://localhost:5000 > /dev/null 2>&1; then
        echo -e "${GREEN}✅${NC} Frontend ejecutándose en puerto 5000"
    else
        echo -e "${YELLOW}⚠️${NC}  Frontend no detectado en puerto 5000"
    fi
fi
