# 🔧 Solución: Error "Could not validate credentials" con indicador verde

## 📋 Resumen del Problema

**Síntoma:** El usuario veía el indicador de sesión verde (activo) pero recibía el error "Could not validate credentials" al intentar editar datos en el dashboard.

**Causa Raíz:** Desacople entre el tiempo de expiración del token JWT en el backend (30 minutos) y el tiempo de sesión del frontend (60 minutos).

### Flujo del Error:
```
Tiempo 0min:  ✅ Login exitoso - Token válido - Indicador verde
Tiempo 30min: 🔴 Token expira en backend (ACCESS_TOKEN_EXPIRE_MINUTES = 30)
Tiempo 30min: 🟢 Frontend aún muestra indicador verde (cree que tiene 30min más)
Tiempo 30min: ❌ Usuario intenta editar → Error "Could not validate credentials"
```

---

## 🎯 Solución Implementada

### 1. **Sincronización de Tiempos**

#### Backend - config.py
```python
# ANTES:
access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# DESPUÉS:
access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))  # 2 horas
```

#### Frontend - AuthContext.tsx
```typescript
const TOKEN_CONFIG = {
  EXPIRE_TIME: 120 * 60 * 1000, // 2 horas (sincronizado con backend)
  REFRESH_BEFORE: 10 * 60 * 1000, // Renovar 10 minutos antes
};
```

#### Frontend - SessionContext.tsx
```typescript
const SESSION_CONFIG = {
  INACTIVITY_TIMEOUT: 60 * 60 * 1000, // 1 hora de inactividad
  TOKEN_LIFETIME: 120 * 60 * 1000, // 2 horas de vida del token
  // ...
};
```

---

### 2. **Sistema de Renovación Automática del Token**

#### Nuevo Endpoint Backend - auth.py
```python
@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Renovar token de acceso usando el token actual"""
    # Verificar que el usuario siga activo
    if not current_user.estado:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Su cuenta ha sido desactivada.",
        )
    
    # Crear nuevo token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": current_user.email}, 
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60,
        "user": UserResponse.model_validate(current_user)
    }
```

#### Frontend - AuthContext.tsx
```typescript
const refreshToken = async (): Promise<boolean> => {
  const currentToken = localStorage.getItem('access_token');
  if (!currentToken) return false;

  try {
    const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${currentToken}`,
        'Content-Type': 'application/json'
      }
    });

    if (response.ok) {
      const data = await response.json();
      localStorage.setItem('access_token', data.access_token);
      setToken(data.access_token);
      
      // Programar próxima renovación
      const expireTime = Date.now() + TOKEN_CONFIG.EXPIRE_TIME;
      setTokenExpireTime(expireTime);
      scheduleTokenRefresh(expireTime);
      
      return true;
    } else {
      logout();
      return false;
    }
  } catch (error) {
    logout();
    return false;
  }
};

const scheduleTokenRefresh = (expireTime: number) => {
  if (refreshTimerRef.current) {
    clearTimeout(refreshTimerRef.current);
  }

  // Renovar 10 minutos antes de expirar
  const refreshTime = expireTime - TOKEN_CONFIG.REFRESH_BEFORE - Date.now();
  
  if (refreshTime > 0) {
    console.log(`⏰ Token se renovará en ${Math.round(refreshTime / 60000)} minutos`);
    refreshTimerRef.current = setTimeout(() => {
      refreshToken();
    }, refreshTime);
  }
};
```

---

### 3. **Interceptor Global de Errores 401**

#### Nuevo Archivo - apiInterceptor.ts
```typescript
// Interceptor de fetch global para capturar errores 401
const originalFetch = window.fetch;

window.fetch = async (...args) => {
  const response = await originalFetch(...args);

  // Si recibimos un 401, el token ha expirado o es inválido
  if (response.status === 401) {
    console.error('🚫 Error 401: Token expirado, cerrando sesión...');
    
    // Mostrar notificación
    showSessionExpiredNotification();
    
    // Ejecutar logout automáticamente
    if (logoutCallback) {
      setTimeout(() => logoutCallback?.(), 1500);
    }
  }

  return response;
};

// Notificación visual al usuario
const showSessionExpiredNotification = () => {
  const notification = document.createElement('div');
  notification.innerHTML = `
    <div style="...">
      ⚠️ Sesión Expirada
      Tu sesión ha caducado. Redirigiendo al login...
    </div>
  `;
  document.body.appendChild(notification);
  // ... animación y auto-remover
};
```

#### Integración - main.tsx
```typescript
import './utils/apiInterceptor'; // Inicializa el interceptor global
```

#### Registro de Callback - AuthContext.tsx
```typescript
useEffect(() => {
  registerLogoutCallback(logout);
  console.log('✅ Callback de logout registrado');
}, []);
```

---

## 📊 Flujo de Funcionamiento

### Flujo Normal (Con Renovación Automática)
```
Tiempo 0min:     ✅ Login → Token válido (2h)
Tiempo 110min:   🔄 Auto-renovación → Nuevo token (2h más)
Tiempo 220min:   🔄 Auto-renovación → Nuevo token (2h más)
...continúa indefinidamente mientras haya actividad
```

### Flujo con Inactividad (Cierre por Sesión)
```
Tiempo 0min:     ✅ Login → Token válido (2h)
Tiempo 60min:    ⚠️ Sin actividad → SessionContext detecta inactividad
Tiempo 60min:    🚪 Auto-logout por inactividad (antes de que expire el token)
```

### Flujo con Token Expirado (Error 401)
```
Tiempo 0min:     ✅ Login → Token válido
Tiempo 120min:   🔴 Token expira (no se renovó porque no hubo actividad)
Tiempo 120min:   🚫 Usuario intenta acción → Error 401
Tiempo 120min:   📢 Interceptor detecta 401 → Muestra notificación
Tiempo 121.5min: 🚪 Auto-logout → Redirige a login
```

---

## 🔑 Componentes Clave

### Archivo Modificado/Creado | Propósito
| Archivo | Cambios | Propósito |
|---------|---------|-----------|
| `Back-FC/app/core/config.py` | Token expira en 120min | Sincronizar con frontend |
| `Back-FC/app/api/auth.py` | Nuevo endpoint `/refresh` | Renovar tokens antes de expirar |
| `Front-FC/src/contexts/AuthContext.tsx` | Sistema de renovación automática | Mantener sesión activa indefinidamente |
| `Front-FC/src/utils/apiInterceptor.ts` | ✨ NUEVO - Interceptor global | Detectar 401 y cerrar sesión |
| `Front-FC/src/main.tsx` | Import del interceptor | Activar protección global |
| `Front-FC/src/contexts/SessionContext.tsx` | Config TOKEN_LIFETIME | Documentar tiempo de token |

---

## ✅ Beneficios de la Solución

1. **🔐 Sincronización Perfecta**
   - Backend y frontend usan el mismo tiempo (2 horas)
   - Eliminado el desacople que causaba el error

2. **🔄 Renovación Automática**
   - Token se renueva cada 110 minutos (10 min antes de expirar)
   - Sesión activa puede durar indefinidamente con actividad

3. **⚠️ Detección Proactiva**
   - Interceptor captura errores 401 inmediatamente
   - Usuario es notificado visualmente antes del logout

4. **🚪 Logout Inteligente**
   - Por inactividad: 60 minutos sin actividad
   - Por token expirado: 120 minutos sin renovación
   - Por error 401: Inmediato con notificación

5. **👥 Mejor UX**
   - Indicador verde = sesión realmente activa
   - No más errores inesperados
   - Notificaciones claras de cierre de sesión

---

## 🧪 Testing Recomendado

### Test 1: Renovación Automática
```
1. Login
2. Esperar 110 minutos (con actividad ocasional)
3. Verificar en console: "✅ Token renovado exitosamente"
4. Comprobar que el indicador sigue verde
```

### Test 2: Inactividad
```
1. Login
2. No interactuar por 60 minutos
3. Verificar advertencias a los 50min y 58min
4. Comprobar logout automático a los 60min
```

### Test 3: Token Expirado (Simulado)
```
1. Login
2. En localStorage, eliminar 'access_token'
3. Intentar editar dashboard
4. Verificar notificación "Sesión Expirada"
5. Comprobar logout automático
```

### Test 4: Error 401 Real
```
1. Login
2. Cambiar TOKEN_EXPIRE a 2 minutos (para testing)
3. Esperar 2 minutos sin actividad
4. Intentar editar dashboard
5. Verificar interceptor captura 401 y cierra sesión
```

---

## 📝 Notas Importantes

### ⚠️ Para Producción
- Considerar usar refresh tokens por seguridad
- Implementar límite de renovaciones consecutivas
- Agregar telemetría de sesiones expiradas

### 🔧 Configuración Flexible
Todos los tiempos son configurables:

```typescript
// Frontend
const TOKEN_CONFIG = {
  EXPIRE_TIME: 120 * 60 * 1000,      // Ajustable
  REFRESH_BEFORE: 10 * 60 * 1000,    // Ajustable
};

// Backend (.env)
ACCESS_TOKEN_EXPIRE_MINUTES=120  # Ajustable
```

### 🐛 Debugging
Para verificar el sistema funciona:
```typescript
// En console del navegador:
localStorage.getItem('access_token')  // Ver token actual
localStorage.getItem('last_user_activity')  // Ver última actividad
```

---

## 🎉 Resultado Final

**ANTES:**
- ❌ Error "Could not validate credentials" después de 30 minutos
- ❌ Indicador verde confuso (mostraba activo cuando el token estaba expirado)
- ❌ Usuario frustrado por errores inesperados

**DESPUÉS:**
- ✅ Token se renueva automáticamente cada 110 minutos
- ✅ Indicador verde siempre sincronizado con estado real
- ✅ Errores 401 capturados con notificación amigable
- ✅ Usuario puede trabajar indefinidamente con actividad
- ✅ Logout automático solo por inactividad real (60 min)

---

## 📚 Referencias

- JWT Best Practices: https://datatracker.ietf.org/doc/html/rfc8725
- OAuth 2.0 Token Refresh: https://oauth.net/2/refresh-tokens/
- FastAPI Security: https://fastapi.tiangolo.com/tutorial/security/
