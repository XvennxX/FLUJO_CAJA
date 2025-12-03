# 🚀 Guía de Instalación Completa

Guía paso a paso para configurar el Sistema de Flujo de Caja de Bolívar desde cero.

## 📋 **Prerequisitos del Sistema**

### **Software Requerido**
- **Python** 3.8 o superior
- **Node.js** 18 o superior  
- **MySQL** 8.0 o superior
- **Git** para control de versiones
- **VS Code** (recomendado) o editor de código preferido

### **Verificación de Prerequisitos**
```bash
# Verificar versiones instaladas
python --version        # Debe ser 3.8+
node --version         # Debe ser 18+
npm --version          # Debe ser 9+
mysql --version        # Debe ser 8.0+
git --version          # Cualquier versión reciente
```

## 📁 **1. Configuración del Proyecto**

### **Clonar Repositorio**
```bash
# Clonar el proyecto
git clone <repository-url>
cd FLUJO_CAJA

# Verificar estructura
ls -la
# Debe mostrar: Back-FC/ Front-FC/ docs/ README.md
```

## 🐍 **2. Configuración del Backend**

### **2.1 Entorno Virtual Python**
```bash
# Navegar al backend
cd Back-FC

# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Verificar activación (debe mostrar (.venv) en el prompt)
```

### **2.2 Instalar Dependencias**
```bash
# Instalar todas las dependencias
pip install -r requirements.txt

# Verificar instalación
pip list | grep fastapi
pip list | grep sqlalchemy
pip list | grep pymysql
```

### **2.3 Configuración de Base de Datos**

#### **Crear Base de Datos MySQL**
```sql
-- Conectar a MySQL como administrador
mysql -u root -p

-- Crear base de datos
CREATE DATABASE flujo_caja CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Crear usuario específico (opcional pero recomendado)
CREATE USER 'flujo_user'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON flujo_caja.* TO 'flujo_user'@'localhost';
FLUSH PRIVILEGES;

-- Verificar creación
SHOW DATABASES;
USE flujo_caja;
```

#### **Configurar Variables de Entorno**
```bash
# Crear archivo .env en Back-FC/
cp .env.example .env  # Si existe
# O crear nuevo archivo .env con:
```

**Contenido del archivo `.env`:**
```properties
# Configuración de Base de Datos
DB_HOST=localhost
DB_PORT=3306
DB_USER=flujo_user
DB_PASSWORD=secure_password
DB_NAME=flujo_caja

# Configuración de Seguridad
SECRET_KEY=tu_clave_secreta_muy_larga_y_segura_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Configuración de CORS (para desarrollo)
CORS_ORIGINS=["http://localhost:5000", "http://127.0.0.1:5000"]

# Configuración TRM
TRM_UPDATE_TIME=19:00
TRM_TIMEZONE=America/Bogota
```

### **2.4 Inicializar Base de Datos**
```bash
# Crear datos iniciales (usuarios, bancos, conceptos)
python scripts/setup/create_initial_data.py

# Crear bancos de prueba
python scripts/setup/create_test_banks.py

# Verificar creación
python scripts/utils/listar_usuarios_api.py
```

### **2.5 Configurar TRM Automática**
```bash
# Crear tabla TRM si no existe
mysql -u flujo_user -p flujo_caja < scripts/migrations/create_trm_table.sql

# Probar obtención de TRM
python scripts/trm/test_trm.py

# Verificar scheduler
python scripts/trm/trm_scheduler_simple.py --test
```

### **2.6 Iniciar Backend**
```bash
# Iniciar servidor de desarrollo
python run_server.py

# Verificar en otra terminal:
curl http://localhost:8000/api/v1/health
# Debe responder: {"status": "healthy"}

# Acceder a documentación:
# http://localhost:8000/docs (Swagger UI)
# http://localhost:8000/redoc (ReDoc)
```

## ⚛️ **3. Configuración del Frontend**

### **3.1 Instalación de Dependencias**
```bash
# En nueva terminal, navegar al frontend
cd Front-FC

# Instalar dependencias Node.js
npm install

# Verificar instalación
npm list react
npm list typescript
npm list vite
```

### **3.2 Verificar Configuración**
```bash
# Ejecutar verificación del proyecto
npm run check

# Debe mostrar todos ✅ en verde
# Si hay errores ❌, revisar la instalación
```

### **3.3 Configurar Conexión con Backend**
Verificar que el archivo `src/contexts/AuthContext.tsx` tenga la URL correcta:

```typescript
// Línea ~20 en AuthContext.tsx
const API_BASE_URL = 'http://localhost:8000/api/v1';
```

### **3.4 Iniciar Frontend**
```bash
# Iniciar servidor de desarrollo
npm run dev

# Verificar que aparezca:
# ➜  Local:   http://localhost:5000/
# ➜  Network: use --host to expose
```

## 🔗 **4. Verificación de Integración**

### **4.1 Probar Conexión Frontend-Backend**
1. **Abrir Frontend:** http://localhost:5000
2. **Probar Login** con credenciales de prueba:
   - **Email:** mesadinero@bolivar.com
   - **Password:** mesa123
3. **Verificar Dashboard** se carga correctamente
4. **Comprobar TRM** se muestra en la interfaz

### **4.2 Verificar API Endpoints**
```bash
# Probar endpoints principales
curl http://localhost:8000/api/v1/trm/current
curl http://localhost:8000/api/v1/banks/
curl http://localhost:8000/docs
```

### **4.3 Verificar Base de Datos**
```sql
-- Conectar a MySQL y verificar datos
mysql -u flujo_user -p flujo_caja

-- Verificar tablas creadas
SHOW TABLES;

-- Verificar usuarios
SELECT id, name, email, role FROM usuarios;

-- Verificar TRM (debe tener al menos un registro)
SELECT * FROM trm ORDER BY fecha DESC LIMIT 5;
```

## ⚙️ **5. Configuración de Producción**

### **5.1 Backend para Producción**
```bash
# Instalar servidor ASGI para producción
pip install gunicorn

# Crear archivo de configuración gunicorn.conf.py:
bind = "0.0.0.0:8000"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
```

### **5.2 Frontend para Producción**
```bash
# Construir para producción
npm run build:prod

# Analizar bundle
npm run analyze

# Los archivos estáticos están en /dist
# Configurar servidor web (Nginx, Apache) para servir desde /dist
```

### **5.3 Base de Datos en Producción**
```sql
-- Configuraciones recomendadas para MySQL en producción
SET GLOBAL innodb_buffer_pool_size = 1073741824;  -- 1GB
SET GLOBAL max_connections = 200;
SET GLOBAL query_cache_size = 67108864;  -- 64MB
```

## 🔄 **6. Configuración del Servicio TRM**

### **6.1 Servicio Automático (Windows)**
```batch
REM Crear archivo start_trm_service.bat
@echo off
cd /d "C:\ruta\al\proyecto\Back-FC"
.venv\Scripts\activate
python scripts/trm/trm_scheduler_simple.py
```

### **6.2 Servicio Automático (Linux)**
```bash
# Crear servicio systemd /etc/systemd/system/trm-service.service
[Unit]
Description=TRM Scheduler Service
After=network.target

[Service]
Type=simple
User=tu_usuario
WorkingDirectory=/ruta/al/proyecto/Back-FC
Environment=PATH=/ruta/al/proyecto/Back-FC/.venv/bin
ExecStart=/ruta/al/proyecto/Back-FC/.venv/bin/python scripts/trm/trm_scheduler_simple.py
Restart=always

[Install]
WantedBy=multi-user.target

# Habilitar e iniciar servicio
sudo systemctl enable trm-service
sudo systemctl start trm-service
sudo systemctl status trm-service
```

## 🛠️ **7. Herramientas de Desarrollo**

### **7.1 VS Code Configuración**
Extensiones recomendadas:
- Python
- Pylance
- ES7+ React/Redux/React-Native snippets
- Tailwind CSS IntelliSense
- TypeScript Importer

### **7.2 Scripts de Utilidades**
```bash
# Backend - Verificar estado del sistema
python scripts/utils/verify_system_status.py

# Frontend - Verificar configuración
npm run check

# Frontend - Analizar performance
npm run analyze
```

## 🚨 **8. Resolución de Problemas**

### **Problemas Comunes del Backend**
```bash
# Error de conexión a MySQL
# Verificar que MySQL esté ejecutándose
sudo systemctl status mysql  # Linux
net start mysql             # Windows

# Error de permisos de base de datos
# Verificar usuario y contraseña en .env
mysql -u flujo_user -p

# Error de dependencias Python
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### **Problemas Comunes del Frontend**
```bash
# Error de módulos Node.js
rm -rf node_modules package-lock.json
npm install

# Error de TypeScript
npm run lint:fix

# Error de conexión con backend
# Verificar que backend esté ejecutándose en puerto 8000
curl http://localhost:8000/health
```

### **Problemas de TRM**
```bash
# TRM no se actualiza
# Verificar logs
python scripts/trm/test_trm.py

# Verificar scheduler
python scripts/trm/monitor_trm.py

# Verificar conectividad a fuentes
ping datos.gov.co
ping banrep.gov.co
```

## ✅ **9. Lista de Verificación Final**

### **Backend ✅**
- [ ] Python 3.8+ instalado
- [ ] Entorno virtual activado
- [ ] Dependencias instaladas
- [ ] MySQL configurado y ejecutándose
- [ ] Base de datos creada
- [ ] Variables .env configuradas
- [ ] Datos iniciales creados
- [ ] Servidor ejecutándose en puerto 8000
- [ ] API docs accesibles en /docs
- [ ] TRM configurada y funcionando

### **Frontend ✅**
- [ ] Node.js 18+ instalado
- [ ] Dependencias npm instaladas
- [ ] Verificación de proyecto exitosa
- [ ] Conexión con backend establecida
- [ ] Servidor ejecutándose en puerto 5000
- [ ] Login funcional con usuarios de prueba
- [ ] Dashboard cargando correctamente

### **Integración ✅**
- [ ] Frontend se conecta al backend
- [ ] Autenticación funciona
- [ ] TRM se muestra en la interfaz
- [ ] Base de datos responde correctamente
- [ ] Sistema de auditoría registra acciones

## 🎉 **¡Instalación Completada!**

El Sistema de Flujo de Caja de Bolívar está ahora completamente configurado y listo para usar.

**URLs del sistema:**
- **Frontend:** http://localhost:5000
- **Backend API:** http://localhost:8000
- **Documentación:** http://localhost:8000/docs

**Próximos pasos:**
1. Configurar usuarios adicionales según necesidades
2. Importar datos históricos si es necesario
3. Configurar backups automáticos
4. Monitorear logs del sistema TRM
5. Planificar despliegue a producción
