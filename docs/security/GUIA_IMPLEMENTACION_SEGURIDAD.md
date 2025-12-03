# 🚀 Guía de Implementación - Correcciones de Seguridad

## ✅ Correcciones Ya Aplicadas

### 1. ✅ Console.log con Contraseña - CORREGIDO

**Archivo modificado:** `Front-FC/src/components/Pages/Login.tsx`

**Cambio aplicado:**
```typescript
// ❌ ANTES (VULNERABILIDAD)
console.log('🔍 Login attempt:', { email, password });

// ✅ AHORA (SEGURO)
if (import.meta.env.DEV) {
  console.log('🔍 Login attempt:', { email, password: '***' });
}
```

**Estado:** ✅ **COMPLETADO**

---

### 2. ✅ Sistema de Configuración Centralizado - CREADO

**Archivos creados:**
- ✅ `Front-FC/src/config/api.config.ts` - Configuración centralizada
- ✅ `Front-FC/.env.example` - Plantilla de variables
- ✅ `Front-FC/.env.development` - Configuración de desarrollo
- ✅ `Front-FC/.env.production` - Configuración de producción

**Estado:** ✅ **COMPLETADO**

---

## 📝 Pasos Pendientes para Completar la Migración

### Paso 1: Copiar archivo de configuración

```powershell
# En la terminal, dentro de Front-FC/
cp .env.development .env
```

### Paso 2: Actualizar imports en archivos

Necesitas actualizar los siguientes archivos para usar la nueva configuración:

#### Archivos a Modificar (19 archivos):

1. **`src/contexts/AuthContext.tsx`**
```typescript
// ❌ Reemplazar
const API_BASE_URL = 'http://localhost:8000/api/v1';

// ✅ Por
import { API_ENDPOINTS } from '../config/api.config';
// Usar: API_ENDPOINTS.auth.login, etc.
```

2. **`src/components/Pages/Users.tsx`**
```typescript
// ❌ Reemplazar
const response = await fetch('http://localhost:8000/api/v1/users/', {

// ✅ Por
import { API_ENDPOINTS, getAuthHeaders } from '../../config/api.config';
const response = await fetch(API_ENDPOINTS.users.list, {
  headers: getAuthHeaders()
});
```

3. **`src/components/Pages/EditUserModal.tsx`**
```typescript
// ❌ Reemplazar
const response = await fetch(`http://localhost:8000/api/v1/users/${user.id}`, {

// ✅ Por
import { API_ENDPOINTS, getAuthHeaders } from '../../config/api.config';
const response = await fetch(API_ENDPOINTS.users.update(user.id), {
  headers: getAuthHeaders()
});
```

4. **`src/hooks/useCompanies.ts`**
```typescript
// ❌ Reemplazar
fetch('http://localhost:8000/api/v1/companies/test', {

// ✅ Por
import { API_ENDPOINTS, getAuthHeaders } from '../config/api.config';
fetch(API_ENDPOINTS.companies.list, {
  headers: getAuthHeaders()
});
```

5. **`src/hooks/useBankAccounts.ts`**
```typescript
// ❌ Reemplazar
fetch(`http://localhost:8000/api/v1/bank-accounts/test/companies/${companyId}`, {

// ✅ Por
import { API_ENDPOINTS, getAuthHeaders } from '../config/api.config';
fetch(API_ENDPOINTS.bankAccounts.byCompany(companyId), {
  headers: getAuthHeaders()
});
```

6. **`src/hooks/useTransaccionesFlujoCaja.ts`**
```typescript
// ❌ Reemplazar
fetch(`http://localhost:8000/api/v1/api/transacciones-flujo-caja/fecha/${fecha}?area=${area}`, {

// ✅ Por
import { API_ENDPOINTS, getAuthHeaders } from '../config/api.config';
fetch(API_ENDPOINTS.transactions.byDate(fecha, area), {
  headers: getAuthHeaders()
});
```

7. **`src/hooks/useTRMByDate.ts`**
```typescript
// ❌ Reemplazar
fetch(`http://localhost:8000/api/v1/trm/by-date/${targetDate}`, {

// ✅ Por
import { API_ENDPOINTS, getAuthHeaders } from '../config/api.config';
fetch(API_ENDPOINTS.trm.byDate(targetDate), {
  headers: getAuthHeaders()
});
```

8. **`src/hooks/useDiferenciaSaldos.ts`**
```typescript
// ❌ Reemplazar
fetch('http://localhost:8000/api/v1/diferencia-saldos/calcular-diferencia-saldos', {

// ✅ Por
import { API_ENDPOINTS, getAuthHeaders } from '../config/api.config';
fetch(API_ENDPOINTS.diferenciaSaldos.calcular, {
  headers: getAuthHeaders()
});
```

9. **`src/services/apiService.ts`**
```typescript
// ❌ Reemplazar
this.baseUrl = 'http://localhost:8000';

// ✅ Por
import config from '../config/api.config';
this.baseUrl = config.apiBaseUrl;
```

10. **`src/services/saldoInicialService.ts`**
```typescript
// ❌ Reemplazar
const API_BASE_URL = 'http://localhost:8000/api/v1';

// ✅ Por
import { API_BASE_URL } from '../config/api.config';
```

11. **`src/utils/diasHabiles.ts`**
```typescript
// ❌ Reemplazar
constructor(baseUrl: string = 'http://localhost:8000/api/v1/dias-habiles') {

// ✅ Por
import { API_ENDPOINTS } from '../config/api.config';
constructor(baseUrl: string = API_ENDPOINTS.diasHabiles) {
```

---

## 🔄 Script de Migración Automática (Opcional)

Si quieres automatizar el proceso, puedes usar este script de PowerShell:

```powershell
# migrate-api-urls.ps1

$files = @(
    "src/contexts/AuthContext.tsx",
    "src/components/Pages/Users.tsx",
    "src/components/Pages/EditUserModal.tsx",
    "src/hooks/useCompanies.ts",
    "src/hooks/useBankAccounts.ts",
    "src/hooks/useTransaccionesFlujoCaja.ts",
    "src/hooks/useTRMByDate.ts",
    "src/hooks/useDiferenciaSaldos.ts",
    "src/services/apiService.ts",
    "src/services/saldoInicialService.ts",
    "src/utils/diasHabiles.ts"
)

foreach ($file in $files) {
    Write-Host "🔄 Procesando: $file"
    # Aquí irían las expresiones regulares para reemplazar
    # (Por seguridad, es mejor hacerlo manualmente)
}
```

**⚠️ Recomendación:** Hacer los cambios manualmente para asegurar que todo funcione correctamente.

---

## 🧪 Testing Después de Cambios

### 1. Verificar que el archivo .env se cargó:

```typescript
// En cualquier componente, temporalmente:
console.log('API URL:', import.meta.env.VITE_API_BASE_URL);
console.log('Environment:', import.meta.env.VITE_ENVIRONMENT);
```

### 2. Probar login:
- Abrir aplicación
- Intentar login
- Verificar que funcione correctamente

### 3. Probar endpoints principales:
- Listar usuarios
- Editar usuario
- Crear transacciones
- Ver reportes

### 4. Verificar consola:
- No debe haber errores de conexión
- Los logs solo deben aparecer en desarrollo

---

## 📋 Checklist de Verificación

### Configuración:
- [ ] Archivo `.env` creado y configurado
- [ ] Variables de entorno correctas
- [ ] `.env` en `.gitignore` (ya está ✅)

### Código:
- [ ] Todos los `fetch` usan la nueva configuración
- [ ] No hay URLs hardcodeadas
- [ ] Console.logs solo en desarrollo
- [ ] Headers de autenticación centralizados

### Testing:
- [ ] Login funciona
- [ ] Endpoints de usuarios funcionan
- [ ] Endpoints de transacciones funcionan
- [ ] Endpoints de reportes funcionan
- [ ] No hay errores en consola

### Producción:
- [ ] `.env.production` con URLs correctas
- [ ] Build de producción sin errores
- [ ] URLs de producción verificadas
- [ ] HTTPS configurado

---

## 🚀 Comandos para Deploy

### Desarrollo:
```bash
npm run dev
```

### Build para Producción:
```bash
npm run build
```

### Preview de Producción:
```bash
npm run preview
```

---

## 🆘 Solución de Problemas

### Problema 1: Variables de entorno no se cargan

**Solución:**
1. Reiniciar el servidor de desarrollo
2. Verificar que el nombre empiece con `VITE_`
3. Verificar que el archivo `.env` esté en la raíz de `Front-FC/`

### Problema 2: Error de CORS

**Solución:**
Verificar configuración de CORS en el backend:
```python
# Back-FC/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://tu-dominio.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Problema 3: 404 en endpoints

**Solución:**
Verificar que:
1. Backend está corriendo
2. URL en `.env` es correcta
3. Endpoints en `api.config.ts` son correctos

---

## 📚 Recursos Adicionales

- [Vite Environment Variables](https://vitejs.dev/guide/env-and-mode.html)
- [TypeScript Module Resolution](https://www.typescriptlang.org/docs/handbook/module-resolution.html)
- [Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)

---

## ✅ Estado Final Esperado

Después de completar estos pasos:

```
✅ Sin URLs hardcodeadas
✅ Sin console.logs con información sensible
✅ Variables de entorno configuradas
✅ Configuración centralizada
✅ Fácil cambio entre ambientes
✅ Listo para producción
```

---

**Tiempo Estimado:** 2-4 horas  
**Dificultad:** Media  
**Prioridad:** 🔴 Crítica

**Nota:** Estos cambios son **necesarios antes de desplegar a producción**.
