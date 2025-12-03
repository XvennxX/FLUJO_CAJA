# Sistema de Gestión de Roles y Permisos (RBAC)

## 📋 Resumen

Se ha implementado un **sistema completo de Control de Acceso Basado en Roles (RBAC)** que permite:

✅ Gestionar roles y permisos de forma granular  
✅ Asignar permisos específicos a cada rol  
✅ Controlar accesos a funcionalidades del sistema  
✅ Auditar permisos de usuarios  
✅ Migración automática desde el sistema antiguo  

---

## 🗂️ Estructura Implementada

### 1. **Modelos de Base de Datos**

#### `Rol` (`roles`)
- `id`: ID único
- `nombre`: Nombre descriptivo del rol
- `codigo`: Código único (ej: ADMIN, TESORERIA)
- `descripcion`: Descripción del rol
- `activo`: Si el rol está activo
- `es_sistema`: Roles protegidos que no se pueden eliminar
- `permisos`: Relación Many-to-Many con permisos

#### `Permiso` (`permisos`)
- `id`: ID único
- `nombre`: Nombre descriptivo
- `codigo`: Código único (ej: transacciones.crear)
- `descripcion`: Descripción del permiso
- `modulo`: Módulo al que pertenece
- `activo`: Si el permiso está activo

#### `Usuario` (actualizado)
- Se agregó campo `rol_id` para relación con tabla `roles`
- Se mantiene campo `rol` antiguo por compatibilidad
- Nuevos métodos:
  - `tiene_permiso(codigo)`: Verifica un permiso específico
  - `tiene_cualquier_permiso(codigos)`: Verifica múltiples permisos
  - `obtener_permisos()`: Lista todos los permisos del usuario

---

## 🔌 API Endpoints

### **Roles**

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/v1/rbac/roles` | Listar todos los roles |
| GET | `/api/v1/rbac/roles/{id}` | Obtener rol específico con sus permisos |
| POST | `/api/v1/rbac/roles` | Crear nuevo rol |
| PUT | `/api/v1/rbac/roles/{id}` | Actualizar rol |
| DELETE | `/api/v1/rbac/roles/{id}` | Eliminar rol (si no es de sistema) |
| POST | `/api/v1/rbac/roles/{id}/permisos` | Asignar permisos a un rol |
| DELETE | `/api/v1/rbac/roles/{id}/permisos` | Remover permisos de un rol |

### **Permisos**

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/v1/rbac/permisos` | Listar todos los permisos |
| GET | `/api/v1/rbac/permisos/por-modulo` | Permisos agrupados por módulo |
| GET | `/api/v1/rbac/permisos/{id}` | Obtener permiso específico |
| POST | `/api/v1/rbac/permisos` | Crear nuevo permiso |
| PUT | `/api/v1/rbac/permisos/{id}` | Actualizar permiso |
| DELETE | `/api/v1/rbac/permisos/{id}` | Eliminar permiso |

---

## 🎯 Roles Predefinidos

### 1. **ADMIN - Administrador**
- **Permisos**: TODOS
- **Descripción**: Acceso total al sistema
- **Protegido**: SÍ (no se puede eliminar)

### 2. **TESORERIA - Tesorería**
- **Permisos**:
  - Transacciones: ver, crear, editar, aprobar
  - Conceptos: ver, crear, editar
  - Cuentas: ver, crear, editar
  - Reportes: ver, exportar, consolidado
  - Conciliación: ver, crear, aprobar
  - TRM: ver
- **Protegido**: SÍ

### 3. **PAGADURIA - Pagaduría**
- **Permisos**:
  - Transacciones: ver, crear, editar
  - Conceptos: ver
  - Cuentas: ver
  - Reportes: ver, exportar
  - TRM: ver
- **Protegido**: SÍ

### 4. **MESA_DINERO - Mesa de Dinero**
- **Permisos**:
  - Transacciones: ver, crear, editar
  - Conceptos: ver
  - Cuentas: ver
  - Reportes: ver, exportar
  - TRM: ver, editar
  - Conciliación: ver
- **Protegido**: SÍ

### 5. **CONSULTA - Solo Consulta**
- **Permisos**: Solo lectura (ver)
- **Protegido**: NO (se puede personalizar)

---

## 📦 Módulos y Permisos

### **Usuarios** (usuarios.*)
- `usuarios.ver` - Ver lista de usuarios
- `usuarios.crear` - Crear usuarios
- `usuarios.editar` - Editar usuarios
- `usuarios.eliminar` - Eliminar usuarios
- `usuarios.cambiar_estado` - Activar/desactivar usuarios

### **Roles** (roles.*)
- `roles.ver` - Ver roles y permisos
- `roles.crear` - Crear roles
- `roles.editar` - Editar roles
- `roles.eliminar` - Eliminar roles

### **Transacciones** (transacciones.*)
- `transacciones.ver`
- `transacciones.crear`
- `transacciones.editar`
- `transacciones.eliminar`
- `transacciones.aprobar`

### **Conceptos** (conceptos.*)
- `conceptos.ver`
- `conceptos.crear`
- `conceptos.editar`
- `conceptos.eliminar`

### **Cuentas Bancarias** (cuentas.*)
- `cuentas.ver`
- `cuentas.crear`
- `cuentas.editar`
- `cuentas.eliminar`

### **Reportes** (reportes.*)
- `reportes.ver`
- `reportes.exportar`
- `reportes.consolidado`

### **TRM** (trm.*)
- `trm.ver`
- `trm.editar`

### **Conciliación** (conciliacion.*)
- `conciliacion.ver`
- `conciliacion.crear`
- `conciliacion.aprobar`

### **Auditoría** (auditoria.*)
- `auditoria.ver`

### **Configuración** (configuracion.*)
- `configuracion.ver`
- `configuracion.editar`

---

## 🚀 Cómo Inicializar

### 1. **Crear las tablas en la base de datos**

Ejecuta las migraciones de SQLAlchemy o usa el script de inicialización.

### 2. **Ejecutar script de seed**

```bash
cd Back-FC
python -m scripts.setup.init_roles_permisos
```

Este script:
- ✅ Crea todos los permisos del sistema
- ✅ Crea los 5 roles predefinidos
- ✅ Migra usuarios existentes al nuevo sistema

### 3. **Verificar en la API**

Accede a la documentación interactiva:
```
http://localhost:8000/docs
```

Busca la sección **"Roles y Permisos"** para probar los endpoints.

---

## 💻 Uso en el Código

### Verificar permisos de un usuario

```python
from app.models.usuarios import Usuario

# Obtener usuario
usuario = db.query(Usuario).filter(Usuario.id == user_id).first()

# Verificar permiso específico
if usuario.tiene_permiso('transacciones.crear'):
    # Permitir crear transacción
    pass

# Verificar múltiples permisos (OR)
if usuario.tiene_cualquier_permiso(['transacciones.editar', 'transacciones.aprobar']):
    # Usuario puede editar O aprobar
    pass

# Obtener todos los permisos
permisos = usuario.obtener_permisos()
# Retorna: ['transacciones.ver', 'transacciones.crear', ...]
```

### Decorador para proteger endpoints (próximo paso)

```python
from app.core.permissions import require_permission

@router.post("/transacciones")
@require_permission("transacciones.crear")
def crear_transaccion(...):
    # Solo usuarios con el permiso pueden acceder
    pass
```

---

## 📋 Próximos Pasos

1. **Frontend - Interfaz de Gestión**
   - Página de administración de roles
   - Matriz de permisos interactiva
   - Asignación visual de permisos a roles
   - Gestión de usuarios con roles

2. **Middleware de Autorización**
   - Decorador `@require_permission()`
   - Decorador `@require_any_permission()`
   - Protección automática de endpoints

3. **Integración con Usuarios**
   - Actualizar formulario de creación/edición de usuarios
   - Selector de rol con descripción de permisos
   - Vista de permisos del usuario actual

4. **Auditoría Avanzada**
   - Registrar cambios en roles y permisos
   - Log de intentos de acceso denegados

---

## ⚠️ Notas Importantes

1. **Compatibilidad**: El sistema mantiene el campo `rol` antiguo por compatibilidad. Los usuarios migrados tendrán ambos campos poblados.

2. **Roles de Sistema**: Los roles marcados con `es_sistema=True` no se pueden eliminar, solo editar sus permisos.

3. **Cascada**: Al eliminar un rol, los usuarios asignados **NO** se eliminan, simplemente quedarán sin rol asignado (`rol_id=NULL`).

4. **Permisos Activos**: Solo los permisos con `activo=True` son evaluados en las verificaciones.

---

## 📞 Soporte

Para dudas o problemas con el sistema de roles:
1. Revisar la documentación de la API en `/docs`
2. Verificar logs del servidor
3. Ejecutar script de inicialización si hay inconsistencias

---

**Última actualización**: 11 de noviembre de 2025
