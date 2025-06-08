Write-Host "🧹 Limpiando contenedores e imágenes Docker..." -ForegroundColor Blue

# Detener todos los contenedores relacionados con SOA
Write-Host "🛑 Deteniendo contenedores..." -ForegroundColor Yellow
docker-compose down

# Eliminar contenedores huérfanos
Write-Host "🗑️ Eliminando contenedores huérfanos..." -ForegroundColor Yellow
docker container prune -f

# Eliminar imágenes no utilizadas
Write-Host "🖼️ Eliminando imágenes no utilizadas..." -ForegroundColor Yellow
docker image prune -f

# Eliminar la imagen base problemática si existe
Write-Host "🎯 Eliminando imagen base problemática..." -ForegroundColor Yellow
try {
    docker rmi soa-base:latest
} catch {
    Write-Host "Imagen soa-base:latest no encontrada" -ForegroundColor Cyan
}

# Limpiar build cache
Write-Host "🧽 Limpiando build cache..." -ForegroundColor Yellow
docker builder prune -f

Write-Host ""
Write-Host "✅ Limpieza completada!" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 Ahora puedes ejecutar:" -ForegroundColor Green
Write-Host "   docker-compose up --build" -ForegroundColor White 