Write-Host "🐳 Configurando el entorno Docker para SOA System..." -ForegroundColor Blue

# Crear directorios si no existen
Write-Host "📁 Creando directorios de servicios..." -ForegroundColor Yellow
$directories = @(
    "soa_bus", "notification_service", "auth_service", "message_service",
    "forum_service", "post_service", "comment_service", "event_service",
    "report_service", "prof_service", "client"
)

foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  ✅ Creado: $dir" -ForegroundColor Green
    } else {
        Write-Host "  ℹ️  Ya existe: $dir" -ForegroundColor Cyan
    }
}

Write-Host ""
Write-Host "📋 Estructura de directorios:" -ForegroundColor Yellow
Get-ChildItem | Where-Object { $_.Name -match "service|soa_bus|client" } | Format-Table Name, LastWriteTime

Write-Host ""
Write-Host "🚀 Para iniciar todos los servicios, ejecuta:" -ForegroundColor Green
Write-Host "   docker-compose up --build" -ForegroundColor White

Write-Host ""
Write-Host "🔧 Para iniciar un servicio específico:" -ForegroundColor Green
Write-Host "   docker-compose up --build <nombre-servicio>" -ForegroundColor White

Write-Host ""
Write-Host "📊 Para ver el estado de los contenedores:" -ForegroundColor Green
Write-Host "   docker-compose ps" -ForegroundColor White

Write-Host ""
Write-Host "📝 Para ver logs de un servicio:" -ForegroundColor Green
Write-Host "   docker-compose logs <nombre-servicio>" -ForegroundColor White

Write-Host ""
Write-Host "✅ Setup completado!" -ForegroundColor Green 