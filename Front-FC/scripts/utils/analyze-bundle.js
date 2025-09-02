import fs from 'fs';
import path from 'path';

/**
 * Script para analizar el bundle de la aplicación
 * Detecta archivos grandes, dependencias pesadas y oportunidades de optimización
 */

const BUILD_DIR = 'dist';
const ASSETS_DIR = path.join(BUILD_DIR, 'assets');

function formatBytes(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function analyzeBundle() {
  console.log('📊 Analizando bundle de la aplicación...\n');

  if (!fs.existsSync(BUILD_DIR)) {
    console.log('❌ No se encuentra el directorio de construcción. Ejecuta "npm run build" primero.');
    return;
  }

  // Analizar archivos JavaScript
  const jsFiles = fs.readdirSync(ASSETS_DIR)
    .filter(file => file.endsWith('.js'))
    .map(file => {
      const filePath = path.join(ASSETS_DIR, file);
      const stats = fs.statSync(filePath);
      return {
        name: file,
        size: stats.size,
        formattedSize: formatBytes(stats.size)
      };
    })
    .sort((a, b) => b.size - a.size);

  // Analizar archivos CSS
  const cssFiles = fs.readdirSync(ASSETS_DIR)
    .filter(file => file.endsWith('.css'))
    .map(file => {
      const filePath = path.join(ASSETS_DIR, file);
      const stats = fs.statSync(filePath);
      return {
        name: file,
        size: stats.size,
        formattedSize: formatBytes(stats.size)
      };
    })
    .sort((a, b) => b.size - a.size);

  // Mostrar resultados
  console.log('📁 Archivos JavaScript:');
  jsFiles.forEach(file => {
    const warning = file.size > 500000 ? ' ⚠️  (Archivo grande)' : '';
    console.log(`  ${file.name}: ${file.formattedSize}${warning}`);
  });

  console.log('\n🎨 Archivos CSS:');
  cssFiles.forEach(file => {
    const warning = file.size > 100000 ? ' ⚠️  (Archivo grande)' : '';
    console.log(`  ${file.name}: ${file.formattedSize}${warning}`);
  });

  // Calcular tamaño total
  const totalSize = [...jsFiles, ...cssFiles].reduce((sum, file) => sum + file.size, 0);
  console.log(`\n📊 Tamaño total del bundle: ${formatBytes(totalSize)}`);

  // Recomendaciones
  console.log('\n💡 Recomendaciones:');
  if (jsFiles.some(file => file.size > 500000)) {
    console.log('  • Considera dividir el código en chunks más pequeños');
  }
  if (cssFiles.some(file => file.size > 100000)) {
    console.log('  • Revisa si hay CSS no utilizado que se pueda eliminar');
  }
  if (totalSize > 1000000) {
    console.log('  • El bundle es considerable, evalúa lazy loading para componentes');
  }
  console.log('  • Usa Gzip/Brotli en el servidor para reducir el tamaño de transferencia');
}

analyzeBundle();
