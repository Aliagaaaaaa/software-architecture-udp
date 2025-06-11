#!/bin/bash

echo "🐳 Configurando el entorno Docker para SOA System..."

# Crear directorios si no existen
echo "📁 Creando directorios de servicios..."
mkdir -p soa_bus notification_service auth_service message_service 
mkdir -p forum_service post_service comment_service event_service 
mkdir -p report_service prof_service

echo "📋 Estructura de directorios creada:"
ls -la | grep "service\|soa_bus"

echo ""
echo "🚀 Para iniciar todos los servicios, ejecuta:"
echo "   docker-compose up --build"
echo ""
echo "🔧 Para iniciar un servicio específico:"
echo "   docker-compose up --build <nombre-servicio>"
echo ""
echo "📊 Para ver el estado de los contenedores:"
echo "   docker-compose ps"
echo ""
echo "📝 Para ver logs de un servicio:"
echo "   docker-compose logs <nombre-servicio>"
echo ""
echo "✅ Setup completado!" 