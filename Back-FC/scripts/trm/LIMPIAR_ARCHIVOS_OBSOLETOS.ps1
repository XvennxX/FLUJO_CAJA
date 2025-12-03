# Script para limpiar archivos TRM obsoletos
# El sistema ahora está integrado en main.py del servidor

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "    LIMPIEZA DE ARCHIVOS TRM OBSOLETOS" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📋 ARCHIVOS QUE SE MANTENDRÁN:" -ForegroundColor Green
Write-Host "   ✅ trm_scraper.py - Obtiene TRM del Banco República" -ForegroundColor Gray
Write-Host "   ✅ update_missing_trm.py - Recuperación manual" -ForegroundColor Gray
Write-Host "   ✅ README.md - Documentación" -ForegroundColor Gray
Write-Host "   ✅ INSTRUCCIONES_USO.md - Guía de uso" -ForegroundColor Gray
Write-Host ""

Write-Host "🗑️  ARCHIVOS OBSOLETOS (se eliminarán):" -ForegroundColor Yellow
Write-Host "   ❌ trm_scheduler_production.py - Ya no se usa (integrado en main.py)" -ForegroundColor Gray
Write-Host "   ❌ trm_scheduler_simple.py - Obsoleto" -ForegroundColor Gray
Write-Host "   ❌ trm_scheduler.py - Obsoleto" -ForegroundColor Gray
Write-Host "   ❌ start_trm_scheduler.ps1 - Ya no se necesita" -ForegroundColor Gray
Write-Host "   ❌ start_trm_service.bat - Ya no se necesita" -ForegroundColor Gray
Write-Host "   ❌ test_trm.py - Prueba duplicada" -ForegroundColor Gray
Write-Host "   ❌ monitor_trm.py - No está en uso" -ForegroundColor Gray
Write-Host "   ❌ update_trm_now.bat - Ya no se necesita" -ForegroundColor Gray
Write-Host "   ❌ migrate_trm.py - Solo era para migración inicial" -ForegroundColor Gray
Write-Host ""

Write-Host "ℹ️  OPCIONAL:" -ForegroundColor Cyan
Write-Host "   📝 test_trm_system.py - Script de pruebas (puedes mantenerlo)" -ForegroundColor Gray
Write-Host ""

$confirmacion = Read-Host "¿Deseas eliminar los archivos obsoletos? (S/N)"

if ($confirmacion -eq "S" -or $confirmacion -eq "s") {
    Write-Host ""
    Write-Host "🗑️  Eliminando archivos obsoletos..." -ForegroundColor Yellow
    
    $archivos_obsoletos = @(
        "trm_scheduler_production.py",
        "trm_scheduler_simple.py",
        "trm_scheduler.py",
        "start_trm_scheduler.ps1",
        "start_trm_service.bat",
        "test_trm.py",
        "monitor_trm.py",
        "update_trm_now.bat",
        "migrate_trm.py"
    )
    
    foreach ($archivo in $archivos_obsoletos) {
        if (Test-Path $archivo) {
            Remove-Item $archivo -Force
            Write-Host "   ✅ Eliminado: $archivo" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️  No encontrado: $archivo" -ForegroundColor Yellow
        }
    }
    
    Write-Host ""
    Write-Host "✅ LIMPIEZA COMPLETADA" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 ARCHIVOS RESTANTES:" -ForegroundColor Cyan
    Get-ChildItem -File | Select-Object Name | Format-Table -AutoSize
    
} else {
    Write-Host ""
    Write-Host "❌ Operación cancelada" -ForegroundColor Red
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "ℹ️  RECORDATORIO: El sistema TRM ahora está integrado en:" -ForegroundColor Cyan
Write-Host "   📁 app/main.py (verificación automática al iniciar)" -ForegroundColor Gray
Write-Host "   📁 app/services/trm_service.py (lógica de negocio)" -ForegroundColor Gray
Write-Host "   📁 scripts/trm/trm_scraper.py (obtención de datos)" -ForegroundColor Gray
Write-Host ""
Write-Host "🚀 Para usar el sistema, solo ejecuta:" -ForegroundColor Cyan
Write-Host "   python run_server.py" -ForegroundColor White
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

Read-Host "Presiona Enter para salir"
