# Scripts de Utilidades

Herramientas para análisis, diagnóstico y mantenimiento del proyecto frontend.

## 📁 **Archivos disponibles:**

### `analyze-bundle.js`
Analiza el bundle de producción para detectar oportunidades de optimización.

**Uso:**
```bash
node scripts/utils/analyze-bundle.js
```

**Características:**
- 📊 Tamaño de archivos JavaScript y CSS
- ⚠️  Detección de archivos grandes
- 💡 Recomendaciones de optimización
- 📈 Reporte del tamaño total del bundle

**Ejemplo de salida:**
```
📁 Archivos JavaScript:
  index-abc123.js: 245.8 KB
  vendor-def456.js: 1.2 MB ⚠️  (Archivo grande)

🎨 Archivos CSS:
  style-ghi789.css: 45.2 KB

📊 Tamaño total del bundle: 1.5 MB

💡 Recomendaciones:
  • Considera dividir el código en chunks más pequeños
  • Usa Gzip/Brotli en el servidor
```

### `check-project.js`
Verifica el estado general del proyecto y su configuración.

**Uso:**
```bash
node scripts/utils/check-project.js
```

**Verificaciones incluidas:**
- ✅ Archivos de configuración (package.json, tsconfig.json, etc.)
- ✅ Estructura de directorios
- ✅ Scripts npm disponibles
- ✅ Dependencias principales instaladas
- ✅ Configuración de .gitignore

**Ejemplo de salida:**
```
📋 Archivos de configuración:
✅ Package.json: package.json
✅ TypeScript config: tsconfig.json
✅ Vite config: vite.config.ts

📂 Estructura de directorios:
✅ Código fuente: src
✅ Componentes: src/components
```

## 🔧 **Uso recomendado:**

### Antes de construir para producción:
```bash
node scripts/utils/check-project.js
```

### Después de construir:
```bash
node scripts/utils/analyze-bundle.js
```

## 💡 **Consejos de optimización:**

1. **Archivos JS > 500KB:** Considera code splitting
2. **Archivos CSS > 100KB:** Revisa CSS no utilizado
3. **Bundle > 1MB:** Implementa lazy loading
4. **Muchas dependencias:** Audita y elimina las no necesarias

## 🔍 **Diagnóstico de problemas:**

Si `check-project.js` muestra errores:
- ❌ **package.json no encontrado:** Estás en el directorio correcto?
- ❌ **node_modules faltante:** Ejecuta `npm install`
- ❌ **Scripts faltantes:** Revisa la sección "scripts" en package.json
