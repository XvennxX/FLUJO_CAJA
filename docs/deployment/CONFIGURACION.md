# ⚙️ Configuración del Sistema

Guía completa de configuración para el Sistema de Flujo de Caja de Bolívar.

## 🔧 **Configuración del Backend**

### **Variables de Entorno (.env)**

**Ubicación:** `Back-FC/.env`

```properties
# ========================================
# CONFIGURACIÓN DE BASE DE DATOS
# ========================================
DB_HOST=localhost
DB_PORT=3306
DB_USER=flujo_user
DB_PASSWORD=tu_password_segura
DB_NAME=flujo_caja

# URL completa de conexión (alternativa)
DATABASE_URL=mysql+pymysql://flujo_user:tu_password_segura@localhost:3306/flujo_caja

# ========================================
# CONFIGURACIÓN DE SEGURIDAD
# ========================================
# Clave secreta para JWT (generar una nueva para producción)
SECRET_KEY=tu_clave_secreta_muy_larga_y_aleatoria_para_jwt_tokens
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ========================================
# CONFIGURACIÓN DE CORS
# ========================================
# URLs permitidas para CORS (separadas por comas)
CORS_ORIGINS=["http://localhost:5000", "http://127.0.0.1:5000", "http://localhost:3000"]

# ========================================
# CONFIGURACIÓN TRM
# ========================================
# Hora de actualización diaria (formato 24h)
TRM_UPDATE_TIME=19:00
TRM_TIMEZONE=America/Bogota

# URLs de fuentes TRM (backup)
TRM_SOURCE_PRIMARY=https://www.datos.gov.co/resource/32sa-8pi3.json
TRM_SOURCE_SECONDARY=https://totoro.banrep.gov.co/estadisticas-economicas/rest/consultaDatosService/consultaMercadoCambiario

# ========================================
# CONFIGURACIÓN DE LOGS
# ========================================
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
LOG_MAX_SIZE=10485760  # 10MB
LOG_BACKUP_COUNT=5

# ========================================
# CONFIGURACIÓN DE DESARROLLO
# ========================================
DEBUG=True
RELOAD=True
```

### **Configuración de Base de Datos**

#### **MySQL Optimizada para Producción**
```sql
-- Configuraciones recomendadas en my.cnf o my.ini

[mysqld]
# Configuración de memoria
innodb_buffer_pool_size = 1G
innodb_log_file_size = 256M
innodb_flush_log_at_trx_commit = 2

# Configuración de conexiones
max_connections = 200
max_user_connections = 190
thread_cache_size = 16

# Configuración de consultas
query_cache_type = 1
query_cache_size = 64M
query_cache_limit = 2M

# Configuración de charset
character_set_server = utf8mb4
collation_server = utf8mb4_unicode_ci

# Configuración de zona horaria
default_time_zone = '-05:00'  # Colombia UTC-5

# Configuración de logs
general_log = 0
slow_query_log = 1
long_query_time = 2
slow_query_log_file = /var/log/mysql/slow.log
```

#### **Índices Optimizados**
```sql
-- Índices para mejor performance

-- Tabla usuarios
CREATE INDEX idx_usuarios_email ON usuarios(email);
CREATE INDEX idx_usuarios_role ON usuarios(role);
CREATE INDEX idx_usuarios_activo ON usuarios(activo);

-- Tabla transacciones_flujo_caja
CREATE INDEX idx_transacciones_fecha ON transacciones_flujo_caja(fecha);
CREATE INDEX idx_transacciones_compania ON transacciones_flujo_caja(compania_id);
CREATE INDEX idx_transacciones_cuenta ON transacciones_flujo_caja(cuenta_bancaria_id);
CREATE INDEX idx_transacciones_concepto ON transacciones_flujo_caja(concepto_id);

-- Tabla TRM
CREATE INDEX idx_trm_fecha ON trm(fecha);
CREATE UNIQUE INDEX idx_trm_fecha_unique ON trm(fecha);

-- Tabla auditoria (si existe)
CREATE INDEX idx_auditoria_fecha ON auditoria(timestamp);
CREATE INDEX idx_auditoria_usuario ON auditoria(usuario_id);
CREATE INDEX idx_auditoria_modulo ON auditoria(modulo);
```

### **Configuración de Uvicorn/Gunicorn**

**Archivo:** `Back-FC/gunicorn.conf.py`
```python
# Configuración para producción
import multiprocessing

# Servidor
bind = "0.0.0.0:8000"
backlog = 2048

# Workers
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000

# Timeouts
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100

# Logging
accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Security
limit_request_line = 8192
limit_request_fields = 100
limit_request_field_size = 8190

# Process naming
proc_name = "flujo_caja_api"

# Server mechanics
preload_app = True
daemon = False
pidfile = "/var/run/flujo_caja.pid"
tmp_upload_dir = None

# SSL (para HTTPS en producción)
# keyfile = "/path/to/private.key"
# certfile = "/path/to/certificate.crt"
```

## ⚛️ **Configuración del Frontend**

### **Variables de Entorno**

**Archivo:** `Front-FC/.env` (opcional)
```properties
# URL del backend
VITE_API_BASE_URL=http://localhost:8000/api/v1

# Configuración de desarrollo
VITE_NODE_ENV=development

# Configuración de analytics (si se implementa)
VITE_GA_TRACKING_ID=

# Configuración de mapas (si se implementa)
VITE_MAPS_API_KEY=
```

### **Configuración de Vite**

**Archivo:** `Front-FC/vite.config.ts`
```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig({
  plugins: [react()],
  
  // Configuración del servidor de desarrollo
  server: {
    port: 5000,
    host: true,
    cors: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      }
    }
  },
  
  // Configuración de build
  build: {
    outDir: 'dist',
    sourcemap: false,
    minify: 'terser',
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          charts: ['recharts'],
          utils: ['date-fns', 'lucide-react']
        }
      }
    },
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
      },
    },
  },
  
  // Optimización de dependencias
  optimizeDeps: {
    exclude: ['lucide-react'],
    include: ['react', 'react-dom', 'recharts', 'date-fns']
  },
  
  // Configuración de alias
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@components': resolve(__dirname, 'src/components'),
      '@hooks': resolve(__dirname, 'src/hooks'),
      '@utils': resolve(__dirname, 'src/utils'),
      '@types': resolve(__dirname, 'src/types'),
    }
  },
  
  // Variables de entorno
  define: {
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version),
  }
});
```

### **Configuración de Tailwind CSS**

**Archivo:** `Front-FC/tailwind.config.js`
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        bolivar: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',  // Color principal Bolívar
          600: '#1e40af',
          700: '#1e3a8a',
          800: '#1e3a8a',
          900: '#1e3a8a',
        },
        gray: {
          50: '#f9fafb',
          100: '#f3f4f6',
          200: '#e5e7eb',
          300: '#d1d5db',
          400: '#9ca3af',
          500: '#6b7280',
          600: '#4b5563',
          700: '#374151',
          800: '#1f2937',
          900: '#111827',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-in': 'slideIn 0.3s ease-out',
        'bounce-subtle': 'bounceSubtle 2s infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideIn: {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(0)' },
        },
        bounceSubtle: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-5px)' },
        }
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}
```

### **Configuración de TypeScript**

**Archivo:** `Front-FC/tsconfig.json`
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "allowJs": false,
    
    /* Bundler mode */
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "isolatedModules": true,
    "moduleDetection": "force",
    "noEmit": true,
    "jsx": "react-jsx",
    
    /* Linting */
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    
    /* Path mapping */
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "@/components/*": ["src/components/*"],
      "@/hooks/*": ["src/hooks/*"],
      "@/utils/*": ["src/utils/*"],
      "@/types/*": ["src/types/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

## 🔒 **Configuración de Seguridad**

### **Configuración HTTPS (Producción)**

#### **Nginx Configuration**
```nginx
server {
    listen 80;
    server_name tu-dominio.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name tu-dominio.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    # Configuración SSL moderna
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # Headers de seguridad
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=63072000" always;
    
    # Frontend (archivos estáticos)
    location / {
        root /var/www/flujo_caja/dist;
        try_files $uri $uri/ /index.html;
        
        # Cache para assets estáticos
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### **Variables de Entorno de Producción**

**Archivo:** `Back-FC/.env.production`
```properties
# ========================================
# CONFIGURACIÓN DE PRODUCCIÓN
# ========================================
DEBUG=False
RELOAD=False
LOG_LEVEL=WARNING

# Base de datos con SSL
DATABASE_URL=mysql+pymysql://user:password@db-server:3306/flujo_caja?ssl_disabled=false

# CORS más restrictivo
CORS_ORIGINS=["https://tu-dominio.com"]

# JWT con mayor seguridad
ACCESS_TOKEN_EXPIRE_MINUTES=15
SECRET_KEY=clave_super_secreta_y_aleatoria_para_produccion

# Configuración TRM para producción
TRM_UPDATE_TIME=19:00
TRM_TIMEZONE=America/Bogota
```

## 📊 **Configuración de Monitoreo**

### **Logs Estructurados**

**Archivo:** `Back-FC/app/core/logging.py`
```python
import logging
import logging.handlers
from datetime import datetime
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'module': record.name,
            'message': record.getMessage(),
            'function': record.funcName,
            'line': record.lineno,
        }
        
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
            
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
            
        return json.dumps(log_entry)

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Handler para archivo con rotación
    file_handler = logging.handlers.RotatingFileHandler(
        'logs/app.log',
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(JSONFormatter())
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
```

### **Health Checks**

**Endpoint:** `/api/v1/health`
```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db

router = APIRouter()

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        # Verificar conexión a base de datos
        db.execute("SELECT 1")
        
        # Verificar servicio TRM
        from app.services.trm_service import get_current_trm
        trm = await get_current_trm()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "connected",
            "trm_service": "operational" if trm else "degraded",
            "version": "1.0.0"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
```

## 🔄 **Configuración de Backup**

### **Script de Backup MySQL**
```bash
#!/bin/bash
# Archivo: scripts/backup/mysql_backup.sh

DB_NAME="flujo_caja"
DB_USER="flujo_user"
DB_PASSWORD="tu_password"
BACKUP_DIR="/var/backups/mysql"
DATE=$(date +%Y%m%d_%H%M%S)

# Crear directorio si no existe
mkdir -p $BACKUP_DIR

# Realizar backup
mysqldump -u$DB_USER -p$DB_PASSWORD \
    --single-transaction \
    --routines \
    --triggers \
    $DB_NAME > $BACKUP_DIR/flujo_caja_$DATE.sql

# Comprimir backup
gzip $BACKUP_DIR/flujo_caja_$DATE.sql

# Eliminar backups antiguos (mantener 30 días)
find $BACKUP_DIR -name "flujo_caja_*.sql.gz" -mtime +30 -delete

echo "Backup completado: flujo_caja_$DATE.sql.gz"
```

### **Crontab para Backups Automáticos**
```bash
# Editar crontab
crontab -e

# Agregar línea para backup diario a las 2 AM
0 2 * * * /path/to/scripts/backup/mysql_backup.sh

# Backup del código fuente semanal (domingos 3 AM)
0 3 * * 0 tar -czf /var/backups/code/flujo_caja_$(date +\%Y\%m\%d).tar.gz /path/to/FLUJO_CAJA
```

## 📈 **Configuración de Performance**

### **Redis para Cache (Opcional)**
```python
# requirements.txt
redis==4.5.4
fastapi-cache2==0.2.1

# Configuración Redis
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=300  # 5 minutos
```

### **Configuración de Cache**
```python
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
import redis

# En app/main.py
@app.on_event("startup")
async def startup():
    redis_client = redis.from_url("redis://localhost:6379")
    FastAPICache.init(RedisBackend(redis_client), prefix="flujo-caja")
```

Esta configuración proporciona una base sólida para el sistema en desarrollo y producción, con opciones de seguridad, monitoreo y performance optimizadas.
