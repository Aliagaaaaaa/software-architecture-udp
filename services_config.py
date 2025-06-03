#!/usr/bin/env python3
"""
Configuración de servicios SOA
"""

import json
import os
from typing import Dict, List, Any

class ServicesConfig:
    """Gestiona la configuración de todos los servicios SOA"""
    
    def __init__(self, config_file: str = 'services.json'):
        self.config_file = config_file
        self.services = self._load_default_config()
        self.load_config()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Configuración por defecto de los servicios"""
        return {
            "soa_server": {
                "name": "SOA Server",
                "description": "Servidor principal de registro y descubrimiento",
                "file": "soa_server.py",
                "port": 8000,
                "host": "localhost",
                "icon": "🏢",
                "enabled": True,
                "dependencies": []
            },
            "auth": {
                "name": "Authentication Service",
                "description": "Servicio de autenticación JWT con SQLite",
                "file": "auth_service.py",
                "port": 8002,
                "host": "localhost",
                "icon": "🔐",
                "enabled": True,
                "dependencies": ["soa_server"],
                "database": "auth_service.db",
                "methods": ["login", "register", "verify", "refresh", "users", "delete_user", "info"],
                "default_user": {
                    "username": "admin",
                    "password": "admin123",
                    "role": "admin"
                },
                "module": "auth_service",
                "class": "AuthService"
            },
            "prof": {
                "name": "Profile Service",
                "description": "Servicio de gestión de perfiles de usuario",
                "file": "prof_service.py",
                "port": 8004,
                "host": "localhost",
                "icon": "👤",
                "enabled": True,
                "dependencies": ["soa_server", "auth"],
                "database": "Cloudflare D1 (remota)",
                "methods": ["create_profile", "get_profile", "update_profile", "delete_profile", "list_profiles", "admin_get_profile", "admin_delete_profile", "info"],
                "module": "prof_service",
                "class": "ProfileService"
            },
            "forum": {
                "name": "Forum Service",
                "description": "Servicio de gestión de foros de discusión",
                "file": "forum_service.py",
                "port": 8003,
                "host": "localhost",
                "icon": "🗣️",
                "enabled": True,
                "dependencies": ["soa_server", "auth"],
                "database": "Cloudflare D1 (remota)",
                "methods": ["create_forum", "get_forum", "list_forums", "list_my_forums", "update_forum", "delete_forum", "admin_delete_forum", "info"],
                "module": "forum_service",
                "class": "ForumService"
            },
            "post": {
                "name": "Post Service",
                "description": "Servicio de gestión de posts en foros de discusión",
                "file": "post_service.py",
                "port": 8005,
                "host": "localhost",
                "icon": "💬",
                "enabled": True,
                "dependencies": ["soa_server", "auth", "forum"],
                "database": "Cloudflare D1 (remota)",
                "methods": ["create_post", "get_post", "list_posts", "list_my_posts", "update_post", "delete_post", "admin_delete_post", "info"],
                "module": "post_service",
                "class": "PostService"
            },
            "comm": {
                "name": "Comment Service",
                "description": "Servicio de gestión de comentarios en posts",
                "file": "comment_service.py",
                "port": 8006,
                "host": "localhost",
                "icon": "💭",
                "enabled": True,
                "dependencies": ["soa_server", "auth", "post"],
                "database": "Cloudflare D1 (remota)",
                "methods": ["create_comment", "get_comment", "list_comments", "list_my_comments", "update_comment", "delete_comment", "admin_delete_comment", "info"],
                "module": "comment_service",
                "class": "CommentService"
            },
            "event": {
                "name": "Event Service",
                "description": "Servicio de gestión de eventos",
                "file": "event_service.py",
                "port": 8007,
                "host": "localhost",
                "icon": "📅",
                "enabled": True,
                "dependencies": ["soa_server", "auth"],
                "database": "Cloudflare D1 (remota)",
                "methods": ["create_event", "get_event", "list_events", "list_my_events", "update_event", "delete_event", "admin_delete_event", "info"],
                "module": "event_service",
                "class": "EventService"
            },
            "msg": {
                "name": "Message Service",
                "description": "Servicio de gestión de mensajes privados entre usuarios",
                "file": "message_service.py",
                "port": 8008,
                "host": "localhost",
                "icon": "💌",
                "enabled": True,
                "dependencies": ["soa_server", "auth"],
                "database": "Cloudflare D1 (remota)",
                "methods": ["send_message", "get_message", "list_sent_messages", "list_received_messages", "list_conversation", "delete_message", "admin_delete_message", "info"],
                "module": "message_service",
                "class": "MessageService"
            },
            "reprt": {
                "name": "Report Service",
                "description": "Servicio de gestión de reportes de contenido inapropiado",
                "file": "report_service.py",
                "port": 8009,
                "host": "localhost",
                "icon": "📋",
                "enabled": True,
                "dependencies": ["soa_server", "auth", "post", "comm"],
                "database": "Cloudflare D1 (remota)",
                "methods": ["create_report", "get_report", "list_reports", "list_my_reports", "update_report_status", "delete_report", "admin_delete_report", "info"],
                "module": "report_service",
                "class": "ReportService"
            },
            "notif": {
                "name": "Notification Service",
                "description": "Servicio de gestión de notificaciones del sistema",
                "file": "notification_service.py",
                "port": 8010,
                "host": "localhost",
                "icon": "🔔",
                "enabled": True,
                "dependencies": ["soa_server", "auth"],
                "database": "Cloudflare D1 (remota)",
                "methods": ["list_notifications", "get_unread_count", "mark_as_read", "mark_all_as_read", "get_notification", "delete_notification", "clear_all_notifications", "admin_list_all_notifications", "info"],
                "module": "notification_service",
                "class": "NotificationService"
            }
        }
    
    def load_config(self):
        """Carga la configuración desde archivo JSON"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    self.services.update(loaded_config)
            except Exception as e:
                print(f"⚠️  Error cargando configuración: {e}")
                print("   Usando configuración por defecto")
    
    def save_config(self):
        """Guarda la configuración actual a archivo JSON"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.services, f, indent=2, ensure_ascii=False)
            print(f"✅ Configuración guardada en {self.config_file}")
        except Exception as e:
            print(f"❌ Error guardando configuración: {e}")
    
    def get_service(self, service_id: str) -> Dict[str, Any]:
        """Obtiene configuración de un servicio específico"""
        return self.services.get(service_id, {})
    
    def get_enabled_services(self) -> List[str]:
        """Obtiene lista de servicios habilitados"""
        return [sid for sid, config in self.services.items() 
                if config.get('enabled', False) and sid != 'soa_server']
    
    def get_service_dependencies(self, service_id: str) -> List[str]:
        """Obtiene dependencias de un servicio"""
        return self.services.get(service_id, {}).get('dependencies', [])
    
    def enable_service(self, service_id: str):
        """Habilita un servicio"""
        if service_id in self.services:
            self.services[service_id]['enabled'] = True
            print(f"✅ Servicio {service_id} habilitado")
        else:
            print(f"❌ Servicio {service_id} no encontrado")
    
    def disable_service(self, service_id: str):
        """Deshabilita un servicio"""
        if service_id in self.services:
            self.services[service_id]['enabled'] = False
            print(f"⏸️  Servicio {service_id} deshabilitado")
        else:
            print(f"❌ Servicio {service_id} no encontrado")
    
    def add_service(self, service_id: str, config: Dict[str, Any]):
        """Añade un nuevo servicio"""
        self.services[service_id] = config
        print(f"✅ Servicio {service_id} añadido")
    
    def remove_service(self, service_id: str):
        """Elimina un servicio"""
        if service_id in self.services:
            del self.services[service_id]
            print(f"🗑️  Servicio {service_id} eliminado")
        else:
            print(f"❌ Servicio {service_id} no encontrado")
    
    def list_services(self):
        """Lista todos los servicios"""
        print("\n📋 SERVICIOS CONFIGURADOS:")
        print("="*60)
        
        for service_id, config in self.services.items():
            status = "🟢 Habilitado" if config.get('enabled', False) else "🔴 Deshabilitado"
            icon = config.get('icon', '🔧')
            name = config.get('name', service_id)
            port = config.get('port', 'N/A')
            
            print(f"\n{icon} {service_id.upper()}: {name}")
            print(f"   Estado: {status}")
            print(f"   Puerto: {port}")
            print(f"   Archivo: {config.get('file', 'N/A')}")
            print(f"   Descripción: {config.get('description', 'Sin descripción')}")
            
            if config.get('methods'):
                methods = ', '.join(config['methods'])
                print(f"   Métodos: {methods}")
            
            if config.get('dependencies'):
                deps = ', '.join(config['dependencies'])
                print(f"   Dependencias: {deps}")
    
    def get_startup_order(self) -> List[str]:
        """Calcula el orden de inicio basado en dependencias"""
        order = []
        remaining = list(self.services.keys())
        
        # Primero el servidor SOA
        if 'soa_server' in remaining:
            order.append('soa_server')
            remaining.remove('soa_server')
        
        # Luego los servicios por dependencias
        while remaining:
            added_in_iteration = False
            
            for service_id in remaining[:]:
                deps = self.get_service_dependencies(service_id)
                if all(dep in order for dep in deps):
                    if self.services[service_id].get('enabled', False):
                        order.append(service_id)
                    remaining.remove(service_id)
                    added_in_iteration = True
            
            if not added_in_iteration and remaining:
                # Añadir servicios sin dependencias resueltas
                for service_id in remaining[:]:
                    if self.services[service_id].get('enabled', False):
                        order.append(service_id)
                    remaining.remove(service_id)
                break
        
        return order
    
    def export_service_info(self, output_file: str = 'services_info.json'):
        """Exporta información de servicios a JSON"""
        try:
            info = {}
            for service_id, config in self.services.items():
                info[service_id] = {
                    'name': config.get('name'),
                    'description': config.get('description'),
                    'port': config.get('port'),
                    'methods': config.get('methods', []),
                    'enabled': config.get('enabled', False)
                }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(info, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Información de servicios exportada a {output_file}")
        except Exception as e:
            print(f"❌ Error exportando información: {e}")

def main():
    """Función principal para gestionar configuración"""
    
    config = ServicesConfig()
    
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'list':
            config.list_services()
        
        elif command == 'save':
            config.save_config()
        
        elif command == 'export':
            output = sys.argv[2] if len(sys.argv) > 2 else 'services_info.json'
            config.export_service_info(output)
        
        elif command == 'order':
            order = config.get_startup_order()
            print("📋 Orden de inicio de servicios:")
            for i, service_id in enumerate(order, 1):
                service = config.get_service(service_id)
                icon = service.get('icon', '🔧')
                name = service.get('name', service_id)
                print(f"  {i}. {icon} {service_id} - {name}")
        
        elif command == 'enable' and len(sys.argv) > 2:
            config.enable_service(sys.argv[2])
            config.save_config()
        
        elif command == 'disable' and len(sys.argv) > 2:
            config.disable_service(sys.argv[2])
            config.save_config()
        
        elif command == 'help':
            print("🔧 GESTOR DE CONFIGURACIÓN DE SERVICIOS SOA")
            print("="*50)
            print("Uso:")
            print("  python services_config.py list      - Listar servicios")
            print("  python services_config.py save      - Guardar configuración")
            print("  python services_config.py export    - Exportar info de servicios")
            print("  python services_config.py order     - Mostrar orden de inicio")
            print("  python services_config.py enable <service>  - Habilitar servicio")
            print("  python services_config.py disable <service> - Deshabilitar servicio")
            print("  python services_config.py help      - Mostrar ayuda")
        
        else:
            print(f"Comando no reconocido: {command}")
            print("Use 'help' para ver comandos disponibles")
    
    else:
        config.list_services()

if __name__ == "__main__":
    main() 