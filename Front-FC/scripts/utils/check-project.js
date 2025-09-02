import fs from 'fs';
import path from 'path';

/**
 * Script para verificar el estado del proyecto frontend
 * Revisa dependencias, configuración y archivos importantes
 */

const PROJECT_ROOT = process.cwd();

function checkFile(filePath, description) {
  const exists = fs.existsSync(filePath);
  const status = exists ? '✅' : '❌';
  console.log(`${status} ${description}: ${filePath}`);
  return exists;
}

function checkDirectory(dirPath, description) {
  const exists = fs.existsSync(dirPath) && fs.statSync(dirPath).isDirectory();
  const status = exists ? '✅' : '❌';
  console.log(`${status} ${description}: ${dirPath}`);
  return exists;
}

function checkPackageJson() {
  console.log('\n📦 Verificando package.json...');
  
  if (!fs.existsSync('package.json')) {
    console.log('❌ No se encontró package.json');
    return false;
  }

  const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));
  
  // Verificar scripts esenciales
  const requiredScripts = ['dev', 'build', 'lint'];
  console.log('\n🔧 Scripts disponibles:');
  requiredScripts.forEach(script => {
    const exists = packageJson.scripts && packageJson.scripts[script];
    const status = exists ? '✅' : '❌';
    console.log(`${status} ${script}: ${exists || 'No definido'}`);
  });

  // Verificar dependencias principales
  console.log('\n📚 Dependencias principales:');
  const mainDeps = ['react', 'react-dom'];
  mainDeps.forEach(dep => {
    const version = packageJson.dependencies && packageJson.dependencies[dep];
    const status = version ? '✅' : '❌';
    console.log(`${status} ${dep}: ${version || 'No instalado'}`);
  });

  return true;
}

function checkNodeModules() {
  console.log('\n📁 Verificando node_modules...');
  if (fs.existsSync('node_modules')) {
    const moduleCount = fs.readdirSync('node_modules').length;
    console.log(`✅ node_modules existe con ${moduleCount} paquetes`);
    return true;
  } else {
    console.log('❌ node_modules no existe. Ejecuta "npm install"');
    return false;
  }
}

function checkGitIgnore() {
  console.log('\n🚫 Verificando .gitignore...');
  if (!fs.existsSync('.gitignore')) {
    console.log('❌ No se encontró .gitignore');
    return false;
  }

  const gitignore = fs.readFileSync('.gitignore', 'utf8');
  const requiredEntries = ['node_modules', 'dist', '.env'];
  
  requiredEntries.forEach(entry => {
    const exists = gitignore.includes(entry);
    const status = exists ? '✅' : '⚠️ ';
    console.log(`${status} ${entry} ${exists ? 'ignorado' : 'debería estar en .gitignore'}`);
  });

  return true;
}

function main() {
  console.log('🔍 Verificando estado del proyecto Frontend...\n');

  // Verificar archivos de configuración
  console.log('📋 Archivos de configuración:');
  checkFile('package.json', 'Package.json');
  checkFile('tsconfig.json', 'TypeScript config');
  checkFile('vite.config.ts', 'Vite config');
  checkFile('tailwind.config.js', 'Tailwind config');
  checkFile('.gitignore', 'Git ignore');

  // Verificar estructura de directorios
  console.log('\n📂 Estructura de directorios:');
  checkDirectory('src', 'Código fuente');
  checkDirectory('src/components', 'Componentes');
  checkDirectory('src/contexts', 'Contextos');
  checkDirectory('src/hooks', 'Hooks personalizados');
  checkDirectory('src/types', 'Definiciones de tipos');
  checkDirectory('src/utils', 'Utilidades');

  // Verificaciones específicas
  checkPackageJson();
  checkNodeModules();
  checkGitIgnore();

  console.log('\n✨ Verificación completada!');
  console.log('\n💡 Si hay elementos marcados con ❌, corrige esos problemas antes de continuar.');
}

main();
