#!/bin/bash

echo "🧹 Limpiando contenedores e imágenes Docker..."

# Detener todos los contenedores relacionados con SOA
echo "🛑 Deteniendo contenedores..."
docker-compose down

# Eliminar contenedores huérfanos
echo "🗑️ Eliminando contenedores huérfanos..."
docker container prune -f

# Eliminar imágenes no utilizadas
echo "🖼️ Eliminando imágenes no utilizadas..."
docker image prune -f

# Eliminar la imagen base problemática si existe
echo "🎯 Eliminando imagen base problemática..."
docker rmi soa-base:latest 2>/dev/null || echo "Imagen soa-base:latest no encontrada"

# Limpiar build cache
echo "🧽 Limpiando build cache..."
docker builder prune -f

echo ""
echo "✅ Limpieza completada!"
echo ""
echo "🚀 Ahora puedes ejecutar:"
echo "   docker-compose up --build" 