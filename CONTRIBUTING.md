# Contribuyendo al Sistema de Flujo de Caja - Bolívar

¡Gracias por tu interés en contribuir! Este documento proporciona directrices y mejores prácticas para contribuir al proyecto.

## 📋 Tabla de Contenidos

- [Código de Conducta](#código-de-conducta)
- [¿Cómo Puedo Contribuir?](#cómo-puedo-contribuir)
- [Guía de Estilo](#guía-de-estilo)
- [Proceso de Pull Request](#proceso-de-pull-request)
- [Reportar Bugs](#reportar-bugs)
- [Sugerir Mejoras](#sugerir-mejoras)

## Código de Conducta

Este proyecto se adhiere a un Código de Conducta. Al participar, se espera que respetes este código. Por favor reporta comportamientos inaceptables al equipo del proyecto.

## ¿Cómo Puedo Contribuir?

### Reportar Bugs

Antes de crear un reporte de bug:
- Verifica que el bug no haya sido reportado previamente
- Determina en qué repositorio debería ser reportado (backend/frontend)
- Recopila información sobre el bug (pasos para reproducir, mensajes de error, etc.)

Cuando crees un reporte de bug, incluye:
- Título descriptivo
- Pasos detallados para reproducir el problema
- Comportamiento esperado vs comportamiento actual
- Capturas de pantalla si es aplicable
- Información del entorno (OS, versiones, etc.)

### Sugerir Mejoras

Las sugerencias de mejoras son bienvenidas. Incluye:
- Descripción clara de la mejora propuesta
- Justificación de por qué sería útil
- Ejemplos de uso si es aplicable

### Pull Requests

1. Fork el repositorio
2. Crea una rama desde `main`:
   ```bash
   git checkout -b feature/nombre-feature
   # o
   git checkout -b fix/nombre-fix
   ```
3. Realiza tus cambios
4. Asegúrate de que los tests pasen
5. Commit con mensajes descriptivos
6. Push a tu fork
7. Abre un Pull Request

## Guía de Estilo

### Commits

Usa mensajes de commit descriptivos siguiendo el formato:

```
tipo(ámbito): descripción corta

Descripción detallada si es necesario
```

Tipos:
- `feat`: Nueva funcionalidad
- `fix`: Corrección de bug
- `docs`: Cambios en documentación
- `style`: Cambios de formato (no afectan el código)
- `refactor`: Refactorización de código
- `test`: Agregar o modificar tests
- `chore`: Mantenimiento

Ejemplos:
```
feat(auth): agregar autenticación con JWT
fix(api): corregir error en endpoint de usuarios
docs(readme): actualizar instrucciones de instalación
```

### Python (Backend)

- Sigue PEP 8
- Usa type hints
- Documenta funciones con docstrings
- Máximo 120 caracteres por línea
- Nombra variables en snake_case
- Nombra clases en PascalCase

```python
def calcular_total(items: List[Item]) -> Decimal:
    """
    Calcula el total de una lista de items.
    
    Args:
        items: Lista de items a sumar
        
    Returns:
        Total como Decimal
    """
    return sum(item.precio for item in items)
```

### TypeScript/React (Frontend)

- Usa TypeScript estricto
- Componentes funcionales con hooks
- Props tipadas con interfaces
- Nombres de componentes en PascalCase
- Hooks y funciones en camelCase
- Máximo 100 caracteres por línea

```typescript
interface UserProps {
  name: string;
  email: string;
  onUpdate: (user: User) => void;
}

export const UserCard: React.FC<UserProps> = ({ name, email, onUpdate }) => {
  // Componente aquí
};
```

### Tests

- Escribe tests para nuevas funcionalidades
- Mantén tests existentes actualizados
- Usa nombres descriptivos
- Organiza tests en `describe` y `it`/`test`

#### Backend (pytest)
```python
def test_usuario_puede_iniciar_sesion():
    """Test que verifica login de usuario exitoso"""
    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
```

#### Frontend (Vitest)
```typescript
describe('AuthContext', () => {
  it('should login successfully', async () => {
    const { result } = renderHook(() => useAuth());
    await act(async () => {
      await result.current.login('test@example.com', 'password');
    });
    expect(result.current.user).toBeDefined();
  });
});
```

## Proceso de Pull Request

1. **Actualiza tu rama con main**
   ```bash
   git fetch origin
   git rebase origin/main
   ```

2. **Asegúrate de que los tests pasen**
   ```bash
   # Backend
   cd backend
   pytest

   # Frontend
   cd frontend
   npm test
   ```

3. **Verifica el linting**
   ```bash
   # Backend
   flake8 app/
   black app/ --check
   
   # Frontend
   npm run lint
   ```

4. **Actualiza documentación**
   - Si agregaste funcionalidad, documéntala
   - Actualiza README si es necesario
   - Agrega comentarios en código complejo

5. **Completa la plantilla de PR**
   - Describe qué hace el PR
   - Referencia issues relacionados
   - Agrega capturas de pantalla si aplica
   - Lista cambios importantes

6. **Espera revisión**
   - El equipo revisará tu PR
   - Responde a comentarios
   - Realiza cambios solicitados

## Configuración del Ambiente de Desarrollo

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Copiar y configurar .env
cp .env.example .env

# Ejecutar migraciones
alembic upgrade head

# Ejecutar servidor
python run.py
```

### Frontend

```bash
cd frontend
npm install

# Copiar y configurar .env
cp .env.example .env

# Ejecutar en desarrollo
npm run dev
```

## Estructura de Branches

- `main`: Rama principal (producción)
- `develop`: Rama de desarrollo
- `feature/*`: Nuevas funcionalidades
- `fix/*`: Correcciones de bugs
- `hotfix/*`: Correcciones urgentes para producción

## Versionado

Este proyecto sigue [Semantic Versioning](https://semver.org/):
- MAJOR: Cambios incompatibles con versiones anteriores
- MINOR: Nueva funcionalidad compatible
- PATCH: Correcciones de bugs compatibles

## Preguntas

Si tienes preguntas sobre cómo contribuir:
1. Revisa la documentación en `/docs`
2. Busca en issues existentes
3. Crea un nuevo issue con la etiqueta `question`

## Licencia

Al contribuir, aceptas que tus contribuciones sean licenciadas bajo la misma licencia del proyecto (MIT).

---

**¡Gracias por contribuir al Sistema de Flujo de Caja - Bolívar!** 🎉
