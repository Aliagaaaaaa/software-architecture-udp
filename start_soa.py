import subprocess
import time
import sys
import signal
import os
from typing import List

class SOALauncher:
    def __init__(self):
        self.processes: List[subprocess.Popen] = []

    def start_server(self):
        print("🚀 Iniciando servidor SOA principal...")
        try:
            # Iniciar en una ventana separada para que sea visible
            if os.name == 'nt':  # Windows
                process = subprocess.Popen([
                    'start', 'cmd', '/k', 
                    sys.executable, "soa_server.py"
                ], shell=True)
            else:  # Linux/Mac
                process = subprocess.Popen([
                    sys.executable, "soa_server.py"
                ])
            
            self.processes.append(process)
            print("⏳ Esperando que el servidor SOA se inicie...")
            time.sleep(5)  # Aumentar tiempo de espera
            print("✅ Servidor SOA iniciado")
            return True
        except Exception as e:
            print(f"❌ Error iniciando servidor SOA: {e}")
            return False
            
    def start_services(self):
        services = [
            ("auth_service.py", "🔐 Servicio de Autenticación JWT"),
            ("prof_service.py", "👤 Servicio de Gestión de Perfiles"),
            ("forum_service.py", "🗣️ Servicio de Gestión de Foros"),
            ("post_service.py", "💬 Servicio de Gestión de Posts"),
            ("comment_service.py", "💭 Servicio de Gestión de Comentarios"),
            ("event_service.py", "📅 Servicio de Gestión de Eventos"),
            ("message_service.py", "💌 Servicio de Gestión de Mensajes"),
            ("report_service.py", "📋 Servicio de Gestión de Reportes"),
            ("notification_service.py", "🔔 Servicio de Gestión de Notificaciones")
        ]
        
        for service_file, service_name in services:
            print(f"🔧 Iniciando {service_name}...")
            try:
                # Iniciar cada servicio en su propia ventana
                if os.name == 'nt':  # Windows
                    process = subprocess.Popen([
                        'start', 'cmd', '/k',
                        sys.executable, service_file
                    ], shell=True)
                else:  # Linux/Mac
                    process = subprocess.Popen([
                        sys.executable, service_file
                    ])
                
                self.processes.append(process)
                print(f"⏳ Esperando que {service_name} se registre...")
                time.sleep(3)  # Aumentar tiempo de espera
                print(f"✅ {service_name} iniciado")
            except Exception as e:
                print(f"❌ Error iniciando {service_name}: {e}")
                
    def start_auth_only(self):
        """Inicia solo el servicio de autenticación"""
        print("🔐 Iniciando solo el servicio de autenticación...")
        try:
            if not self.start_server():
                return False
                
            print(f"🔧 Iniciando Servicio de Autenticación JWT...")
            if os.name == 'nt':  # Windows
                process = subprocess.Popen([
                    'start', 'cmd', '/k',
                    sys.executable, "auth_service.py"
                ], shell=True)
            else:  # Linux/Mac
                process = subprocess.Popen([
                    sys.executable, "auth_service.py"
                ])
            
            self.processes.append(process)
            print("⏳ Esperando que el servicio se registre...")
            time.sleep(5)  # Tiempo suficiente para que se registre
            print(f"✅ Servicio de Autenticación JWT iniciado")
            
            print("\n📋 Información del servicio:")
            print("   - Nombre: auth")
            print("   - Base de datos: Cloudflare D1 (remota)")
            print("   - Usuario admin: admin@institucional.edu.co / admin123")
            print("\n🧪 Para probar el servicio:")
            print("   python soa_client.py")
            print("   > login admin@institucional.edu.co admin123")
            
            return True
        except Exception as e:
            print(f"❌ Error iniciando servicio de autenticación: {e}")
            return False
    
    def start_auth_and_profiles(self):
        """Inicia los servicios de autenticación y perfiles"""
        print("🔐👤 Iniciando servicios de autenticación y perfiles...")
        try:
            if not self.start_server():
                return False
                
            # Iniciar servicio de autenticación
            print(f"🔧 Iniciando Servicio de Autenticación JWT...")
            if os.name == 'nt':  # Windows
                auth_process = subprocess.Popen([
                    'start', 'cmd', '/k',
                    sys.executable, "auth_service.py"
                ], shell=True)
            else:  # Linux/Mac
                auth_process = subprocess.Popen([
                    sys.executable, "auth_service.py"
                ])
            
            self.processes.append(auth_process)
            print("⏳ Esperando que el servicio de auth se registre...")
            time.sleep(5)
            print(f"✅ Servicio de Autenticación JWT iniciado")
            
            # Iniciar servicio de perfiles
            print(f"🔧 Iniciando Servicio de Gestión de Perfiles...")
            if os.name == 'nt':  # Windows
                prof_process = subprocess.Popen([
                    'start', 'cmd', '/k',
                    sys.executable, "prof_service.py"
                ], shell=True)
            else:  # Linux/Mac
                prof_process = subprocess.Popen([
                    sys.executable, "prof_service.py"
                ])
            
            self.processes.append(prof_process)
            print("⏳ Esperando que el servicio de perfiles se registre...")
            time.sleep(5)
            print(f"✅ Servicio de Gestión de Perfiles iniciado")
            
            print("\n📋 Información de los servicios:")
            print("   🔐 auth - Base de datos: Cloudflare D1 (remota)")
            print("   👤 prof - Base de datos: Cloudflare D1 (remota)")
            print("   📧 Usuario admin: admin@institucional.edu.co / admin123")
            print("\n🧪 Para probar los servicios:")
            print("   python soa_client.py")
            print("   > login admin@institucional.edu.co admin123")
            print("   > call prof create_profile https://avatar.com/admin.jpg 'Admin profile'")
            print("   > call prof get_profile")
            
            return True
        except Exception as e:
            print(f"❌ Error iniciando servicios: {e}")
            return False
    
    def start_client(self, demo_mode: bool = False):
        print("\n🎯 Iniciando cliente SOA...")
        try:
            if demo_mode:
                process = subprocess.Popen([
                    sys.executable, "soa_client.py", "demo"
                ])
            else:
                process = subprocess.Popen([
                    sys.executable, "soa_client.py"
                ])
            process.wait()  
        except Exception as e:
            print(f"❌ Error iniciando cliente SOA: {e}")
    
    def stop_all(self):
        print("\n🛑 Deteniendo todos los servicios...")
        # En Windows, los procesos se abren en ventanas separadas,
        # así que no podemos terminarlos directamente
        if os.name == 'nt':
            print("💡 Por favor cierra manualmente las ventanas de los servicios")
            print("   o usa Ctrl+C en cada ventana de servicio")
        else:
            for process in self.processes:
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                except Exception:
                    pass
        print("✅ Instrucciones de cierre enviadas")
    
    def run_full_demo(self):
        print("="*60)
        print("🎬 DEMOSTRACIÓN COMPLETA SOA")
        print("="*60)
        print("Esta demostración:")
        print("1. Iniciará el servidor SOA")
        print("2. Registrará servicios de ejemplo (Auth + Perfiles + Foros)")
        print("3. Ejecutará pruebas automáticas")
        print("4. Mostrará el cliente interactivo")
        print("="*60)
        
        try:
            # Iniciar servidor
            if not self.start_server():
                return
            
            # Iniciar servicios
            self.start_services()
            
            # Esperar que todos se registren
            print("\n⏳ Esperando que todos los servicios se registren completamente...")
            time.sleep(8)
            
            # Ejecutar demostración
            print("\n🎬 Ejecutando demostración automática...")
            self.start_client(demo_mode=True)
            
            # Preguntar por modo interactivo
            print("\n" + "="*60)
            choice = input("¿Desea continuar con el modo interactivo? (y/n): ").lower()
            if choice in ['y', 'yes', 's', 'si']:
                self.start_client(demo_mode=False)
                
        except KeyboardInterrupt:
            print("\n👋 Demostración interrumpida por el usuario")
        finally:
            self.stop_all()
    
    def run_interactive(self):
        print("="*60)
        print("🎯 MODO INTERACTIVO SOA")
        print("="*60)
        
        try:
            # Iniciar servidor
            if not self.start_server():
                return
            
            # Iniciar servicios
            self.start_services()
            
            # Esperar que todos se registren
            print("\n⏳ Esperando que todos los servicios se registren completamente...")
            time.sleep(10)
            
            print("\n📋 SERVICIOS DISPONIBLES:")
            print("   🔐 auth - Servicio de Autenticación JWT")
            print("   👤 prof - Servicio de Gestión de Perfiles")
            print("   🗣️ forum - Servicio de Gestión de Foros")
            print("   💬 post - Servicio de Gestión de Posts")
            print("\n🌐 BASE DE DATOS:")
            print("   Cloudflare D1 (remota) - https://d1-database-proxy.maliagapacheco.workers.dev/query")
            print("\n🎯 USUARIO POR DEFECTO:")
            print("   admin@institucional.edu.co / admin123")
            
            # Iniciar cliente
            self.start_client(demo_mode=False)
                
        except KeyboardInterrupt:
            print("\n👋 Sesión interrumpida por el usuario")
        finally:
            self.stop_all()
    
    def run_auth_demo(self):
        """Demostración específica del servicio de autenticación"""
        print("="*60)
        print("🔐 DEMOSTRACIÓN DEL SERVICIO DE AUTENTICACIÓN")
        print("="*60)
        print("Esta demostración:")
        print("1. Iniciará el servidor SOA")
        print("2. Iniciará el servicio de autenticación")
        print("3. Mostrará el cliente para pruebas")
        print("="*60)
        
        try:
            # Iniciar servicio de auth
            if not self.start_auth_only():
                return
            
            # Esperar que se registre completamente
            print("\n⏳ Esperando que el servicio se registre completamente...")
            time.sleep(3)
            
            # Iniciar cliente
            print("\n🧪 Iniciando cliente para pruebas...")
            self.start_client(demo_mode=False)
                
        except KeyboardInterrupt:
            print("\n👋 Demostración interrumpida por el usuario")
        finally:
            self.stop_all()

    def start_full_services(self):
        """Inicia todos los servicios (auth, prof, forum, post)"""
        print("🔐👤🗣️💬 Iniciando servicios completos...")
        try:
            if not self.start_server():
                return False
                
            # Iniciar servicio de autenticación
            print(f"🔧 Iniciando Servicio de Autenticación JWT...")
            if os.name == 'nt':  # Windows
                auth_process = subprocess.Popen([
                    'start', 'cmd', '/k',
                    sys.executable, "auth_service.py"
                ], shell=True)
            else:  # Linux/Mac
                auth_process = subprocess.Popen([
                    sys.executable, "auth_service.py"
                ])
            
            self.processes.append(auth_process)
            print("⏳ Esperando que el servicio de auth se registre...")
            time.sleep(5)
            print(f"✅ Servicio de Autenticación JWT iniciado")
            
            # Iniciar servicio de perfiles
            print(f"🔧 Iniciando Servicio de Gestión de Perfiles...")
            if os.name == 'nt':  # Windows
                prof_process = subprocess.Popen([
                    'start', 'cmd', '/k',
                    sys.executable, "prof_service.py"
                ], shell=True)
            else:  # Linux/Mac
                prof_process = subprocess.Popen([
                    sys.executable, "prof_service.py"
                ])
            
            self.processes.append(prof_process)
            print("⏳ Esperando que el servicio de perfiles se registre...")
            time.sleep(5)
            print(f"✅ Servicio de Gestión de Perfiles iniciado")
            
            # Iniciar servicio de foros
            print(f"🔧 Iniciando Servicio de Gestión de Foros...")
            if os.name == 'nt':  # Windows
                forum_process = subprocess.Popen([
                    'start', 'cmd', '/k',
                    sys.executable, "forum_service.py"
                ], shell=True)
            else:  # Linux/Mac
                forum_process = subprocess.Popen([
                    sys.executable, "forum_service.py"
                ])
            
            self.processes.append(forum_process)
            print("⏳ Esperando que el servicio de foros se registre...")
            time.sleep(5)
            print(f"✅ Servicio de Gestión de Foros iniciado")
            
            # Iniciar servicio de posts
            print(f"🔧 Iniciando Servicio de Gestión de Posts...")
            if os.name == 'nt':  # Windows
                post_process = subprocess.Popen([
                    'start', 'cmd', '/k',
                    sys.executable, "post_service.py"
                ], shell=True)
            else:  # Linux/Mac
                post_process = subprocess.Popen([
                    sys.executable, "post_service.py"
                ])
            
            self.processes.append(post_process)
            print("⏳ Esperando que el servicio de posts se registre...")
            time.sleep(5)
            print(f"✅ Servicio de Gestión de Posts iniciado")
            
            # Iniciar servicio de comentarios
            print(f"🔧 Iniciando Servicio de Gestión de Comentarios...")
            if os.name == 'nt':  # Windows
                comment_process = subprocess.Popen([
                    'start', 'cmd', '/k',
                    sys.executable, "comment_service.py"
                ], shell=True)
            else:  # Linux/Mac
                comment_process = subprocess.Popen([
                    sys.executable, "comment_service.py"
                ])
            
            self.processes.append(comment_process)
            print("⏳ Esperando que el servicio de comentarios se registre...")
            time.sleep(5)
            print(f"✅ Servicio de Gestión de Comentarios iniciado")
            
            # Iniciar servicio de eventos
            print(f"🔧 Iniciando Servicio de Gestión de Eventos...")
            if os.name == 'nt':  # Windows
                event_process = subprocess.Popen([
                    'start', 'cmd', '/k',
                    sys.executable, "event_service.py"
                ], shell=True)
            else:  # Linux/Mac
                event_process = subprocess.Popen([
                    sys.executable, "event_service.py"
                ])
            
            self.processes.append(event_process)
            print("⏳ Esperando que el servicio de eventos se registre...")
            time.sleep(5)
            print(f"✅ Servicio de Gestión de Eventos iniciado")
            
            # Iniciar servicio de mensajes
            print(f"🔧 Iniciando Servicio de Gestión de Mensajes...")
            if os.name == 'nt':  # Windows
                message_process = subprocess.Popen([
                    'start', 'cmd', '/k',
                    sys.executable, "message_service.py"
                ], shell=True)
            else:  # Linux/Mac
                message_process = subprocess.Popen([
                    sys.executable, "message_service.py"
                ])
            
            self.processes.append(message_process)
            print("⏳ Esperando que el servicio de mensajes se registre...")
            time.sleep(5)
            print(f"✅ Servicio de Gestión de Mensajes iniciado")
            
            # Iniciar servicio de reportes
            print(f"🔧 Iniciando Servicio de Gestión de Reportes...")
            if os.name == 'nt':  # Windows
                report_process = subprocess.Popen([
                    'start', 'cmd', '/k',
                    sys.executable, "report_service.py"
                ], shell=True)
            else:  # Linux/Mac
                report_process = subprocess.Popen([
                    sys.executable, "report_service.py"
                ])
            
            self.processes.append(report_process)
            print("⏳ Esperando que el servicio de reportes se registre...")
            time.sleep(5)
            print(f"✅ Servicio de Gestión de Reportes iniciado")
            
            # Iniciar servicio de notificaciones
            print(f"🔧 Iniciando Servicio de Gestión de Notificaciones...")
            if os.name == 'nt':  # Windows
                notification_process = subprocess.Popen([
                    'start', 'cmd', '/k',
                    sys.executable, "notification_service.py"
                ], shell=True)
            else:  # Linux/Mac
                notification_process = subprocess.Popen([
                    sys.executable, "notification_service.py"
                ])
            
            self.processes.append(notification_process)
            print("⏳ Esperando que el servicio de notificaciones se registre...")
            time.sleep(5)
            print(f"✅ Servicio de Gestión de Notificaciones iniciado")
            
            print("\n📋 Información de los servicios:")
            print("   🔐 auth - Base de datos: Cloudflare D1 (remota)")
            print("   👤 prof - Base de datos: Cloudflare D1 (remota)")
            print("   🗣️ forum - Base de datos: Cloudflare D1 (remota)")
            print("   💬 post - Base de datos: Cloudflare D1 (remota)")
            print("   💭 comment - Base de datos: Cloudflare D1 (remota)")
            print("   📅 event - Base de datos: Cloudflare D1 (remota)")
            print("   💌 msg - Base de datos: Cloudflare D1 (remota)")
            print("   📋 reprt - Base de datos: Cloudflare D1 (remota)")
            print("   📧 Usuario admin: admin@institucional.edu.co / admin123")
            print("\n🧪 Para probar los servicios:")
            print("   python soa_client.py")
            print("   > login admin@institucional.edu.co admin123")
            print("   > call prof create_profile https://avatar.com/admin.jpg 'Admin profile'")
            print("   > call forum create_forum 'Bienvenida' 'General'")
            print("   > call forum list_forums")
            print("   > call post create_post 1 'Mi primer post en el foro'")
            print("   > call post list_posts 1")
            print("   > call comment create_comment 1 'Mi primer comentario'")
            print("   > call comment list_comments 1")
            print("   > call event create_event 'Mi primer evento' 'Descripción del evento' '2024-12-31'")
            print("   > call event list_events")
            print("   > call msg send_message admin@institucional.edu.co 'Hola, este es mi primer mensaje'")
            print("   > call msg list_received_messages")
            print("   > call msg list_sent_messages")
            print("   > call reprt create_report 1 post 'Contenido inapropiado'")
            print("   > call reprt list_my_reports")
            print("   > call reprt list_reports  # Solo moderadores")
            print("   > call reprt update_report_status 1 revisado  # Solo moderadores")
            print("   > call notif list_notifications")
            print("   > call notif get_unread_count")
            print("   > call notif mark_as_read 1")
            print("   > call notif mark_all_as_read")
            
            return True
        except Exception as e:
            print(f"❌ Error iniciando servicios: {e}")
            return False

def signal_handler(sig, frame):
    print("\n🛑 Recibida señal de interrupción...")
    sys.exit(0)

def main():
    # Registrar manejador de señales
    signal.signal(signal.SIGINT, signal_handler)
    
    launcher = SOALauncher()
    
    # Procesar argumentos de línea de comandos
    if len(sys.argv) > 1:
        if sys.argv[1] == '--demo':
            launcher.run_full_demo()
        elif sys.argv[1] == '--interactive':
            launcher.run_interactive()
        elif sys.argv[1] == '--auth':
            launcher.start_auth_only()
            input("\nPresiona Enter para detener el servicio...")
        elif sys.argv[1] == '--auth-demo':
            launcher.run_auth_demo()
        elif sys.argv[1] == '--profiles':
            launcher.start_auth_and_profiles()
            input("\nPresiona Enter para detener los servicios...")
        elif sys.argv[1] == '--full':
            launcher.start_full_services()
            input("\nPresiona Enter para detener los servicios...")
        elif sys.argv[1] == '--help':
            print("🚀 LAUNCHER SOA - Sistema de servicios distribuidos")
            print("="*55)
            print("Uso:")
            print("  python start_soa.py                    - Modo interactivo (por defecto)")
            print("  python start_soa.py --demo             - Demostración completa")
            print("  python start_soa.py --interactive      - Solo modo interactivo")
            print("  python start_soa.py --auth             - Solo servicio de autenticación")
            print("  python start_soa.py --auth-demo        - Demo específico de autenticación")
            print("  python start_soa.py --profiles         - Iniciar servicios de autenticación y perfiles")
            print("  python start_soa.py --full             - Iniciar todos los servicios (auth + prof + forum + post + comment + event)")
            print("  python start_soa.py --help             - Mostrar esta ayuda")
            print("\n🔐 SERVICIO DE AUTENTICACIÓN:")
            print("   - Base de datos: Cloudflare D1 (remota)")
            print("   - Usuario admin: admin@institucional.edu.co / admin123")
            print("   - Métodos: login, register, verify, refresh, users, delete_user")
            print("\n👤 SERVICIO DE PERFILES:")
            print("   - Base de datos: Cloudflare D1 (remota)")
            print("   - Requiere autenticación JWT del servicio auth")
            print("   - Métodos: create_profile, get_profile, update_profile, delete_profile")
            print("   - Métodos admin: list_profiles, admin_get_profile, admin_delete_profile")
            print("\n🗣️ SERVICIO DE FOROS:")
            print("   - Base de datos: Cloudflare D1 (remota)")
            print("   - Requiere autenticación JWT del servicio auth")
            print("   - Métodos: create_forum, get_forum, list_forums, list_my_forums, update_forum, delete_forum")
            print("   - Métodos admin: admin_delete_forum")
            print("\n💬 SERVICIO DE POSTS:")
            print("   - Base de datos: Cloudflare D1 (remota)")
            print("   - Requiere autenticación JWT del servicio auth")
            print("   - Dependencias: auth, forum")
            print("   - Métodos: create_post, get_post, list_posts, list_my_posts, update_post, delete_post")
            print("   - Métodos admin: admin_delete_post")
            print("\n💭 SERVICIO DE COMENTARIOS:")
            print("   - Base de datos: Cloudflare D1 (remota)")
            print("   - Requiere autenticación JWT del servicio auth")
            print("   - Dependencias: auth, post")
            print("   - Métodos: create_comment, get_comment, list_comments, list_my_comments, update_comment, delete_comment")
            print("   - Métodos admin: admin_delete_comment")
            print("\n📅 SERVICIO DE EVENTOS:")
            print("   - Base de datos: Cloudflare D1 (remota)")
            print("   - Requiere autenticación JWT del servicio auth")
            print("   - Dependencias: auth")
            print("   - Métodos: create_event, get_event, list_events, list_my_events, update_event, delete_event")
            print("   - Métodos admin: admin_delete_event")
            print("   - Formato fecha: YYYY-MM-DD")
            print("\n💌 SERVICIO DE MENSAJES:")
            print("   - Base de datos: Cloudflare D1 (remota)")
            print("   - Requiere autenticación JWT del servicio auth")
            print("   - Dependencias: auth")
            print("   - Métodos: send_message, get_message, list_sent_messages, list_received_messages, list_conversation, delete_message")
            print("   - Métodos admin: admin_delete_message")
            print("   - Límite contenido: 2000 caracteres")
            
            print("\n📋 SERVICIO DE REPORTES:")
            print("   - Base de datos: Cloudflare D1 (remota)")
            print("   - Requiere autenticación JWT del servicio auth")
            print("   - Dependencias: auth, post, comm")
            print("   - Métodos: create_report, list_my_reports, get_report, list_reports, update_report_status, delete_report")
            print("   - Métodos admin: admin_delete_report")
            print("   - Tipos de contenido: post, comentario")
            print("   - Estados: pendiente, revisado, resuelto, descartado")
            
            print("\n🔔 SERVICIO DE NOTIFICACIONES:")
            print("   - Base de datos: Cloudflare D1 (remota)")
            print("   - Requiere autenticación JWT del servicio auth")
            print("   - Dependencias: auth")
            print("   - Métodos: list_notifications, get_unread_count, mark_as_read, mark_all_as_read, get_notification, delete_notification, clear_all_notifications")
            print("   - Métodos admin: admin_list_all_notifications")
            print("   - Tipos de notificación: mensaje, reporte, foro, post, comentario, evento, sistema")
            print("   - Notificaciones automáticas: se crean cuando hay actividad en otros servicios")
            
            print("\n🧪 Para probar los servicios:")
            print("   python soa_client.py")
            print("   > login admin@institucional.edu.co admin123")
            print("   > call prof create_profile https://avatar.com/admin.jpg 'Mi biografía'")
            print("   > call forum create_forum 'Mi primer foro' 'General'")
            print("   > call forum list_forums")
            print("   > call post create_post 1 'Mi primer post en el foro'")
            print("   > call post list_posts 1")
            print("   > call comment create_comment 1 'Mi primer comentario'")
            print("   > call comment list_comments 1")
            print("   > call event create_event 'Mi primer evento' 'Descripción del evento' '2024-12-31'")
            print("   > call event list_events")
            print("   > call msg send_message admin@institucional.edu.co 'Hola, este es mi primer mensaje'")
            print("   > call msg list_received_messages")
            print("   > call msg list_sent_messages")
            print("   > call reprt create_report 1 post 'Contenido inapropiado'")
            print("   > call reprt list_my_reports")
            print("   > call reprt list_reports  # Solo moderadores")
            print("   > call reprt update_report_status 1 revisado  # Solo moderadores")
            print("   > call notif list_notifications")
            print("   > call notif get_unread_count")
            print("   > call notif mark_as_read 1")
            print("   > call notif mark_all_as_read")
        else:
            print(f"Argumento no reconocido: {sys.argv[1]}")
            print("Use --help para ver las opciones disponibles")
    else:
        # Modo por defecto: interactivo
        launcher.run_interactive()

if __name__ == "__main__":
    main() 