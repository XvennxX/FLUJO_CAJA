# Sistema de Flujo de Caja Web 💰

Sistema web moderno que digitaliza y automatiza los cuadros de flujo de caja tradicionalmente manejados en Excel, manteniendo la lógica contable existente pero añadiendo funcionalidades avanzadas de control, reportes y visualización.

## 🎯 Objetivo
Transformar los archivos Excel de flujo de caja (CUADROFLUJOMAYO2025.xlsx, JUNIO2025.xlsx, etc.) en un sistema web completo que permita:
- Registro diario de transacciones por categorías
- Cálculo automático de saldos y flujos
- Control de acceso por roles (Tesorería, Pagaduría, Mesa de Dinero)
- Reportes y exportaciones automatizadas
- Visualización tipo calendario/tabla similar a Excel

## 🏗️ Arquitectura

### Backend (FastAPI)
- **API REST** con documentación automática
- **MySQL** como base de datos principal
- **SQLAlchemy** para ORM y migraciones
- **JWT** para autenticación y autorización
- **Pydantic** para validación de datos

### Frontend (React + TypeScript)
- **Vite** como bundler de desarrollo
- **TailwindCSS** para estilos
- **React Query** para manejo de estado del servidor
- **React Hook Form** para formularios
- **Chart.js/Recharts** para gráficos

### Base de Datos
```sql
-- Estructura principal
usuarios (id, nombre, email, rol, password_hash)
categorias (id, nombre, tipo, descripcion)
transacciones (id, fecha, monto, categoria_id, descripcion, usuario_id)
meses_flujo (id, mes, anio, saldo_inicial, saldo_final)
```

## 🚀 Inicio Rápido

### Prerrequisitos
- Python 3.11+
- Node.js 18+
- MySQL 8.0+
- Docker (opcional)

### Configuración Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
alembic upgrade head
uvicorn main:app --reload
```

### Configuración Frontend
```bash
cd frontend
npm install
npm run dev
```

### Con Docker
```bash
docker-compose up -d
```

## 📊 Funcionalidades Principales

### ✅ Equivalencia Excel → Web
| Excel | Sistema Web |
|-------|-------------|
| Hoja por mes | Vista mensual con calendario interactivo |
| Columnas por días | Tabla dinámica con días del mes |
| Filas por categorías | Sistema de categorías configurable |
| Fórmulas de suma | Cálculos automáticos en backend |
| Saldo acumulado | Tracking automático de saldos diarios |

### ✅ Nuevas Capacidades
- **Dashboard ejecutivo** con métricas clave
- **Importación de Excel** históricos
- **Exportación** a PDF y Excel
- **Proyecciones** de flujo futuro
- **Alertas** de saldos negativos
- **Auditoría** completa de cambios
- **Reportes personalizados** por período y categoría

## 👥 Roles y Permisos

### 🏦 Tesorería
- Acceso completo al sistema
- Puede ver y editar todas las transacciones
- Gestión de usuarios y configuraciones
- Cierre de períodos mensuales

### 💰 Pagaduría  
- Solo egresos relacionados con nómina y proveedores
- No puede ver ingresos o movimientos de tesorería
- Acceso limitado a reportes de su área

### 📊 Mesa de Dinero
- Solo lectura y consultas
- Generación de reportes
- Dashboard de análisis y proyecciones

## 🛠️ Desarrollo

### Estructura del Proyecto
```
FLUJO_CAJA2/
├── backend/
│   ├── app/
│   │   ├── models/      # Modelos SQLAlchemy
│   │   ├── schemas/     # Schemas Pydantic
│   │   ├── routers/     # Endpoints API
│   │   ├── services/    # Lógica de negocio
│   │   └── core/        # Configuración y utilidades
│   ├── alembic/         # Migraciones de BD
│   └── tests/           # Tests del backend
├── frontend/
│   ├── src/
│   │   ├── components/  # Componentes React
│   │   ├── pages/       # Páginas principales
│   │   ├── hooks/       # Custom hooks
│   │   ├── services/    # Llamadas API
│   │   └── types/       # Tipos TypeScript
│   └── public/          # Assets estáticos
├── database/
│   ├── init.sql         # Script inicial
│   └── seeds/           # Datos de prueba
└── docs/
    ├── api.md           # Documentación API
    └── deployment.md    # Guía de despliegue
```

### Scripts Disponibles
```bash
# Backend
npm run dev:backend    # Desarrollo con recarga automática
npm run test:backend   # Tests unitarios
npm run migrate        # Ejecutar migraciones

# Frontend  
npm run dev:frontend   # Servidor de desarrollo
npm run build         # Build de producción
npm run test:frontend # Tests con Vitest

# Full Stack
npm run dev           # Backend + Frontend simultáneo
npm run docker:up     # Levantar con Docker
```

## 📈 Roadmap

### Fase 1 - Core (4 semanas)
- [x] Estructura del proyecto
- [ ] Modelos de base de datos
- [ ] API básica CRUD
- [ ] Autenticación y autorización
- [ ] Frontend básico con formularios

### Fase 2 - Business Logic (3 semanas)
- [ ] Cálculos de flujo de caja
- [ ] Vista tipo Excel
- [ ] Importación de archivos históricos
- [ ] Sistema de roles completo

### Fase 3 - Advanced Features (3 semanas)
- [ ] Dashboard con gráficos
- [ ] Reportes avanzados
- [ ] Exportaciones automáticas
- [ ] Proyecciones y alertas

### Fase 4 - Production (2 semanas)
- [ ] Optimización de performance
- [ ] Tests completos
- [ ] Documentación
- [ ] Despliegue en producción

## 🤝 Contribución

1. Fork del repositorio
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Añadir nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 📞 Soporte

Para soporte técnico o preguntas sobre el sistema:
- 📧 Email: soporte@flujocaja.com
- 📱 WhatsApp: +57 xxx xxx xxxx
- 💬 Slack: #flujo-caja-soporte

---

**Desarrollado con ❤️ para modernizar la gestión financiera**
