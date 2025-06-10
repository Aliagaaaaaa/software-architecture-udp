import socket
import logging
import json
from typing import Dict, Any
from soa_protocol import SOAProtocol

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('SOA_Client')

class SOAClient:
    def __init__(self, soa_server_host: str = 'localhost', soa_server_port: int = 8000):
        self.soa_server_host = soa_server_host
        self.soa_server_port = soa_server_port
        # Token JWT en memoria
        self.current_token = None
        self.current_user = None  # Info del usuario logueado
        self.logger = logger
    
    def _send_request(self, message: str) -> Dict[str, Any]:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.soa_server_host, self.soa_server_port))
            
            self.logger.info(f"Enviando: {message}")
            sock.send(message.encode('utf-8'))
            
            response_data = sock.recv(4096)
            response_str = response_data.decode('utf-8')
            self.logger.info(f"Recibido: {response_str}")
            
            response = SOAProtocol.parse_response(response_str)
            
            sock.close()
            return response
            
        except Exception as e:
            self.logger.error(f"Error enviando petición: {e}")
            return {
                "status": "error",
                "message": f"Connection error: {str(e)}"
            }
    
    def call_service(self, service_name: str, method: str, params_str: str = "") -> Dict[str, Any]:
        # Lista de servicios que requieren autenticación
        auth_required_services = ["PROFS", "FORUM", "POSTS", "COMMS", "EVNTS", "MSGES", "REPOR", "NOTIF"]
        
        # Lista de métodos de auth que NO necesitan token automático (porque son para obtener el token)
        auth_methods_no_token = ["login", "register", "info"]
                
        # Si es un servicio que requiere autenticación y tenemos token
        if (service_name in auth_required_services or
            (service_name == "AUTH_" and method not in auth_methods_no_token)):
            
            if self.current_token:
                # Anteponer el token a los parámetros automáticamente
                if params_str.strip():
                    params_str = f"{self.current_token} {params_str}"
                else:
                    params_str = self.current_token
                    
                self.logger.info(f"🔑 Token automáticamente agregado para {service_name}.{method}")
            else:
                # Si no hay token, advertir al usuario
                self.logger.warning(f"⚠️  {service_name}.{method} requiere autenticación pero no hay token disponible")
        
        message = SOAProtocol.create_request(service_name, method, params_str)
        return self._send_request(message)
    
    def list_services(self) -> None:
        print("\n" + "="*60)
        print("SERVICIOS SOA DISPONIBLES")
        print("="*60)
        print("Descubrimiento de servicios deshabilitado.")
        print("Servicios conocidos:")
        print("  🔐 auth - Servicio de autenticación JWT con SQLite")
        print("     Métodos: login, register, verify, refresh, users, delete_user, info")
        print("     Usuario por defecto: admin@institucional.edu.co / admin123")
        print("     Roles: estudiante, moderador")
        print("  👤 prof - Servicio de gestión de perfiles de usuario")
        print("     Métodos: create_profile, get_profile, update_profile, delete_profile, list_profiles, admin_get_profile, admin_delete_profile, info")
        print("     Tabla: PERFIL (avatar, biografía, id_usuario)")
        print("     🔐 REQUIERE AUTENTICACIÓN: Todos los métodos necesitan token JWT")
        print("     🎯 PERMISOS: Los usuarios solo pueden gestionar su propio perfil | Moderadores tienen métodos admin_*")
        print("     ✨ TOKEN AUTOMÁTICO: Si estás logueado, el token se envía automáticamente")
        print("  🗣️ forum - Servicio de gestión de foros de discusión")
        print("     Métodos: create_forum, get_forum, list_forums, list_my_forums, update_forum, delete_forum, admin_delete_forum, info")
        print("     Tabla: FORO (título, categoría, creador_id)")
        print("     🔐 REQUIERE AUTENTICACIÓN: Todos los métodos necesitan token JWT")
        print("     🎯 PERMISOS: Los usuarios pueden gestionar sus foros | Moderadores pueden eliminar cualquier foro")
        print("     ✨ TOKEN AUTOMÁTICO: Si estás logueado, el token se envía automáticamente")
        print("  💬 post - Servicio de gestión de posts en foros de discusión")
        print("     Métodos: create_post, get_post, list_posts, list_my_posts, update_post, delete_post, admin_delete_post, info")
        print("     Tabla: POST (contenido, fecha, id_foro, autor_id)")
        print("     🔐 REQUIERE AUTENTICACIÓN: Todos los métodos necesitan token JWT")
        print("     🎯 PERMISOS: Los usuarios pueden gestionar sus posts | Moderadores tienen métodos admin_*")
        print("     ✨ TOKEN AUTOMÁTICO: Si estás logueado, el token se envía automáticamente")
        print("     📊 DEPENDENCIAS: Requiere servicios auth y forum activos")
        print("  💭 comm - Servicio de gestión de comentarios en posts")
        print("     Métodos: create_comment, get_comment, list_comments, list_my_comments, update_comment, delete_comment, admin_delete_comment, info")
        print("     Tabla: COMENTARIO (contenido, fecha, id_post, autor_id)")
        print("     🔐 REQUIERE AUTENTICACIÓN: Todos los métodos necesitan token JWT")
        print("     🎯 PERMISOS: Los usuarios pueden gestionar sus comentarios | Moderadores tienen métodos admin_*")
        print("     ✨ TOKEN AUTOMÁTICO: Si estás logueado, el token se envía automáticamente")
        print("     📊 DEPENDENCIAS: Requiere servicios auth y post activos")
        print("  📅 event - Servicio de gestión de eventos")
        print("     Métodos: create_event, get_event, list_events, list_my_events, update_event, delete_event, admin_delete_event, info")
        print("     Tabla: EVENTO (nombre, descripcion, fecha, creador_id)")
        print("     🔐 REQUIERE AUTENTICACIÓN: Todos los métodos necesitan token JWT")
        print("     🎯 PERMISOS: Los usuarios pueden gestionar sus eventos | Moderadores tienen métodos admin_*")
        print("     ✨ TOKEN AUTOMÁTICO: Si estás logueado, el token se envía automáticamente")
        print("     📊 DEPENDENCIAS: Requiere servicio auth activo")
        print("  💌 msg - Servicio de gestión de mensajes privados")
        print("     Métodos: send_message, get_message, list_sent_messages, list_received_messages, list_conversation, delete_message, admin_delete_message, info")
        print("     Tabla: MENSAJE (contenido, fecha, emisor_id, receptor_id)")
        print("     🔐 REQUIERE AUTENTICACIÓN: Todos los métodos necesitan token JWT")
        print("     🎯 PERMISOS: Los usuarios pueden gestionar sus mensajes | Moderadores tienen métodos admin_*")
        print("     ✨ TOKEN AUTOMÁTICO: Si estás logueado, el token se envía automáticamente")
        print("     📊 DEPENDENCIAS: Requiere servicio auth activo")
        print("     💬 FUNCIONALIDAD: Mensajes privados entre usuarios, conversaciones, límite 2000 caracteres")
        print("  📋 reprt - Servicio de gestión de reportes de contenido")
        print("     Métodos: create_report, get_report, list_reports, list_my_reports, update_report_status, delete_report, admin_delete_report, info")
        print("     Tabla: REPORTE (contenido_id, tipo_contenido, razon, fecha, reportado_por, estado)")
        print("     🔐 REQUIERE AUTENTICACIÓN: Todos los métodos necesitan token JWT")
        print("     🎯 PERMISOS: Los usuarios pueden crear y gestionar sus reportes | Moderadores tienen métodos admin_*")
        print("     ✨ TOKEN AUTOMÁTICO: Si estás logueado, el token se envía automáticamente")
        print("     📊 DEPENDENCIAS: Requiere servicios auth, post y comm activos")
        print("     📋 FUNCIONALIDAD: Reportar posts/comentarios inapropiados, gestión de moderación, límite 100 caracteres")
        print("  🔔 notif - Servicio de gestión de notificaciones del sistema")
        print("     Métodos: list_notifications, get_unread_count, mark_as_read, mark_all_as_read, get_notification, delete_notification, clear_all_notifications, admin_list_all_notifications, info")
        print("     Tabla: NOTIFICACION (usuario_id, titulo, mensaje, tipo, referencia_id, leido, fecha)")
        print("     🔐 REQUIERE AUTENTICACIÓN: Todos los métodos necesitan token JWT")
        print("     🎯 PERMISOS: Los usuarios pueden gestionar sus notificaciones | Moderadores pueden ver todas las notificaciones")
        print("     ✨ TOKEN AUTOMÁTICO: Si estás logueado, el token se envía automáticamente")
        print("     📊 DEPENDENCIAS: Requiere servicio auth activo")
        print("     🔔 FUNCIONALIDAD: Notificaciones automáticas de actividad, marcar como leído, gestión completa")
    
    def get_service_methods(self, service_name: str) -> None:
        print(f"\n" + "="*60)
        print(f"MÉTODOS DEL SERVICIO: {service_name.upper()}")
        print("="*60)
        
        # Intentar obtener métodos llamando al método 'info' si existe
        methods_response = self.call_service(service_name, 'info', '')
        
        if methods_response.get('status') == 'success':
            result_str = methods_response.get('result', '')
            print(f"\n📋 Información del servicio:")
            print(f"   {result_str}")
        else:
            print(f"No se pudo obtener información de métodos: {methods_response.get('message', 'Unknown error')}")
    
    def auth_login(self, email: str, password: str) -> Dict[str, Any]:
        """Autentica un usuario en el servicio de autenticación"""
        params = f"{email} {password}"
        response = self.call_service("AUTH_", "login", params)
        
        if response.get('status') == 'success':
            try:
                result = json.loads(response.get('result', '{}'))
                # Si el login es exitoso, guardar token y usuario en memoria
                if result.get('success') and result.get('token'):
                    self.current_token = result.get('token')
                    self.current_user = result.get('user', {})
                    print(f"🔑 Token guardado en memoria para {self.current_user.get('email')}")
                return result
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing auth response"}
        else:
            return {"success": False, "message": response.get('message', 'Auth service error')}
    
    def auth_register(self, email: str, password: str, rol: str = "estudiante") -> Dict[str, Any]:
        """Registra un nuevo usuario en el servicio de autenticación"""
        params = f"{email} {password} {rol}"
        response = self.call_service("auth", "register", params)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing auth response"}
        else:
            return {"success": False, "message": response.get('message', 'Auth service error')}
    
    def auth_verify_token(self, token: str) -> Dict[str, Any]:
        """Verifica un token JWT"""
        response = self.call_service("auth", "verify", token)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing auth response"}
        else:
            return {"success": False, "message": response.get('message', 'Auth service error')}
    
    def auth_refresh_token(self, token: str) -> Dict[str, Any]:
        """Renueva un token JWT"""
        response = self.call_service("auth", "refresh", token)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing auth response"}
        else:
            return {"success": False, "message": response.get('message', 'Auth service error')}
    
    def auth_list_users(self) -> Dict[str, Any]:
        """Lista todos los usuarios registrados"""
        response = self.call_service("auth", "users", "")
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing auth response"}
        else:
            return {"success": False, "message": response.get('message', 'Auth service error')}
    
    def auth_delete_user(self, email: str) -> Dict[str, Any]:
        """Elimina un usuario"""
        response = self.call_service("auth", "delete_user", email)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing auth response"}
        else:
            return {"success": False, "message": response.get('message', 'Auth service error')}
    
    def logout(self):
        """Limpia el token y usuario de la memoria"""
        if self.current_user:
            print(f"👋 Cerrando sesión de {self.current_user.get('email')}")
        else:
            print("👋 No había sesión activa")
        self.current_token = None
        self.current_user = None
    
    def whoami(self):
        """Muestra información del usuario actualmente logueado"""
        if self.current_user and self.current_token:
            print(f"👤 Usuario logueado: {self.current_user.get('email')} ({self.current_user.get('rol')})")
            print(f"🔑 Token: {self.current_token[:50]}...")
            
            # Verificar si el token sigue siendo válido
            verify_result = self.auth_verify_token(self.current_token)
            if verify_result.get('success'):
                print(f"✅ Token válido")
            else:
                print(f"❌ Token inválido o expirado: {verify_result.get('message')}")
                self.current_token = None
                self.current_user = None
        else:
            print("❌ No hay sesión activa. Usa 'login' para autenticarte.")
    
    def get_current_token(self) -> str:
        """Obtiene el token actual, solicitándolo si no existe"""
        if self.current_token:
            return self.current_token
        else:
            print("❌ No hay sesión activa. Usa 'login' para autenticarte.")
            return None
    
    def prof_create_profile(self, token: str = None, avatar: str = "", biografia: str = "") -> Dict[str, Any]:
        """Crea un perfil para el usuario autenticado (requiere token)"""
        if token is None:
            token = self.get_current_token()
            if not token:
                return {"success": False, "message": "No hay token disponible"}
        
        params = f"{token} {avatar} {biografia}".strip()
        response = self.call_service("prof", "create_profile", params)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing profile response"}
        else:
            return {"success": False, "message": response.get('message', 'Profile service error')}
    
    def prof_get_profile(self, token: str = None) -> Dict[str, Any]:
        """Obtiene el perfil del usuario autenticado (requiere token)"""
        if token is None:
            token = self.get_current_token()
            if not token:
                return {"success": False, "message": "No hay token disponible"}
        
        response = self.call_service("prof", "get_profile", token)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing profile response"}
        else:
            return {"success": False, "message": response.get('message', 'Profile service error')}
    
    def prof_update_profile(self, token: str = None, avatar: str = "", biografia: str = "") -> Dict[str, Any]:
        """Actualiza el perfil del usuario autenticado (requiere token)"""
        if token is None:
            token = self.get_current_token()
            if not token:
                return {"success": False, "message": "No hay token disponible"}
        
        params = f"{token} {avatar} {biografia}".strip()
        response = self.call_service("prof", "update_profile", params)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing profile response"}
        else:
            return {"success": False, "message": response.get('message', 'Profile service error')}
    
    def prof_delete_profile(self, token: str = None) -> Dict[str, Any]:
        """Elimina el perfil del usuario autenticado (requiere token)"""
        if token is None:
            token = self.get_current_token()
            if not token:
                return {"success": False, "message": "No hay token disponible"}
        
        response = self.call_service("prof", "delete_profile", token)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing profile response"}
        else:
            return {"success": False, "message": response.get('message', 'Profile service error')}
    
    def prof_list_profiles(self, token: str = None) -> Dict[str, Any]:
        """Lista todos los perfiles (requiere token, solo moderadores)"""
        if token is None:
            token = self.get_current_token()
            if not token:
                return {"success": False, "message": "No hay token disponible"}
        
        response = self.call_service("prof", "list_profiles", token)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing profile response"}
        else:
            return {"success": False, "message": response.get('message', 'Profile service error')}
    
    def prof_admin_get_profile(self, email: str, token: str = None) -> Dict[str, Any]:
        """Obtiene el perfil de cualquier usuario (solo moderadores)"""
        if token is None:
            token = self.get_current_token()
            if not token:
                return {"success": False, "message": "No hay token disponible"}
        
        params = f"{token} {email}"
        response = self.call_service("prof", "admin_get_profile", params)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing profile response"}
        else:
            return {"success": False, "message": response.get('message', 'Profile service error')}
    
    def prof_admin_delete_profile(self, email: str, token: str = None) -> Dict[str, Any]:
        """Elimina el perfil de cualquier usuario (solo moderadores)"""
        if token is None:
            token = self.get_current_token()
            if not token:
                return {"success": False, "message": "No hay token disponible"}
        
        params = f"{token} {email}"
        response = self.call_service("prof", "admin_delete_profile", params)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing profile response"}
        else:
            return {"success": False, "message": response.get('message', 'Profile service error')}
    
    # Métodos helper para el servicio de foros
    def forum_create_forum(self, titulo: str, categoria: str, token: str = None) -> Dict[str, Any]:
        """Crea un nuevo foro (requiere autenticación)"""
        if token is None:
            token = self.get_current_token()
            if not token:
                return {"success": False, "message": "No hay token disponible"}
        
        params = f"{token} {titulo} {categoria}"
        response = self.call_service("forum", "create_forum", params)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing forum response"}
        else:
            return {"success": False, "message": response.get('message', 'Forum service error')}
    
    def forum_get_forum(self, id_foro: str, token: str = None) -> Dict[str, Any]:
        """Obtiene un foro específico por ID (requiere autenticación)"""
        if token is None:
            token = self.get_current_token()
            if not token:
                return {"success": False, "message": "No hay token disponible"}
        
        params = f"{token} {id_foro}"
        response = self.call_service("forum", "get_forum", params)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing forum response"}
        else:
            return {"success": False, "message": response.get('message', 'Forum service error')}
    
    def forum_list_forums(self, token: str = None) -> Dict[str, Any]:
        """Lista todos los foros disponibles (requiere autenticación)"""
        if token is None:
            token = self.get_current_token()
            if not token:
                return {"success": False, "message": "No hay token disponible"}
        
        response = self.call_service("forum", "list_forums", token)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing forum response"}
        else:
            return {"success": False, "message": response.get('message', 'Forum service error')}
    
    def forum_list_my_forums(self, token: str = None) -> Dict[str, Any]:
        """Lista los foros creados por el usuario autenticado"""
        if token is None:
            token = self.get_current_token()
            if not token:
                return {"success": False, "message": "No hay token disponible"}
        
        response = self.call_service("forum", "list_my_forums", token)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing forum response"}
        else:
            return {"success": False, "message": response.get('message', 'Forum service error')}
    
    def forum_update_forum(self, id_foro: str, titulo: str, categoria: str, token: str = None) -> Dict[str, Any]:
        """Actualiza un foro (solo el creador o moderador)"""
        if token is None:
            token = self.get_current_token()
            if not token:
                return {"success": False, "message": "No hay token disponible"}
        
        params = f"{token} {id_foro} {titulo} {categoria}"
        response = self.call_service("forum", "update_forum", params)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing forum response"}
        else:
            return {"success": False, "message": response.get('message', 'Forum service error')}
    
    def forum_delete_forum(self, id_foro: str, token: str = None) -> Dict[str, Any]:
        """Elimina un foro (solo el creador o moderador)"""
        if token is None:
            token = self.get_current_token()
            if not token:
                return {"success": False, "message": "No hay token disponible"}
        
        params = f"{token} {id_foro}"
        response = self.call_service("forum", "delete_forum", params)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing forum response"}
        else:
            return {"success": False, "message": response.get('message', 'Forum service error')}
    
    def forum_admin_delete_forum(self, id_foro: str, token: str = None) -> Dict[str, Any]:
        """Elimina cualquier foro (solo moderadores)"""
        if token is None:
            token = self.get_current_token()
            if not token:
                return {"success": False, "message": "No hay token disponible"}
        
        params = f"{token} {id_foro}"
        response = self.call_service("forum", "admin_delete_forum", params)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing forum response"}
        else:
            return {"success": False, "message": response.get('message', 'Forum service error')}
    
    # Métodos helper para el servicio de posts
    def post_create_post(self, id_foro: str, contenido: str, token: str = None) -> Dict[str, Any]:
        """Crea un nuevo post en un foro (requiere autenticación)"""
        if token is None:
            token = self.get_current_token()
            if not token:
                return {"success": False, "message": "No hay token disponible"}
        
        params = f"{token} {id_foro} {contenido}"
        response = self.call_service("post", "create_post", params)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing post response"}
        else:
            return {"success": False, "message": response.get('message', 'Post service error')}
    
    def post_get_post(self, id_post: str, token: str = None) -> Dict[str, Any]:
        """Obtiene un post específico por ID (requiere autenticación)"""
        if token is None:
            token = self.get_current_token()
            if not token:
                return {"success": False, "message": "No hay token disponible"}
        
        params = f"{token} {id_post}"
        response = self.call_service("post", "get_post", params)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing post response"}
        else:
            return {"success": False, "message": response.get('message', 'Post service error')}
    
    def post_list_posts(self, id_foro: str, token: str = None) -> Dict[str, Any]:
        """Lista todos los posts de un foro específico (requiere autenticación)"""
        if token is None:
            token = self.get_current_token()
            if not token:
                return {"success": False, "message": "No hay token disponible"}
        
        params = f"{token} {id_foro}"
        response = self.call_service("post", "list_posts", params)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing post response"}
        else:
            return {"success": False, "message": response.get('message', 'Post service error')}
    
    def post_list_my_posts(self, token: str = None) -> Dict[str, Any]:
        """Lista los posts creados por el usuario autenticado"""
        if token is None:
            token = self.get_current_token()
            if not token:
                return {"success": False, "message": "No hay token disponible"}
        
        response = self.call_service("post", "list_my_posts", token)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing post response"}
        else:
            return {"success": False, "message": response.get('message', 'Post service error')}
    
    def post_update_post(self, id_post: str, contenido: str, token: str = None) -> Dict[str, Any]:
        """Actualiza un post (solo el autor o moderador)"""
        if token is None:
            token = self.get_current_token()
            if not token:
                return {"success": False, "message": "No hay token disponible"}
        
        params = f"{token} {id_post} {contenido}"
        response = self.call_service("post", "update_post", params)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing post response"}
        else:
            return {"success": False, "message": response.get('message', 'Post service error')}
    
    def post_delete_post(self, id_post: str, token: str = None) -> Dict[str, Any]:
        """Elimina un post (solo el autor o moderador)"""
        if token is None:
            token = self.get_current_token()
            if not token:
                return {"success": False, "message": "No hay token disponible"}
        
        params = f"{token} {id_post}"
        response = self.call_service("post", "delete_post", params)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing post response"}
        else:
            return {"success": False, "message": response.get('message', 'Post service error')}
    
    def post_admin_delete_post(self, id_post: str, token: str = None) -> Dict[str, Any]:
        """Elimina cualquier post (solo moderadores)"""
        if token is None:
            token = self.get_current_token()
            if not token:
                return {"success": False, "message": "No hay token disponible"}
        
        params = f"{token} {id_post}"
        response = self.call_service("post", "admin_delete_post", params)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing post response"}
        else:
            return {"success": False, "message": response.get('message', 'Post service error')}
    
    # Métodos helper para el servicio de comentarios
    def comment_create_comment(self, id_post: str, contenido: str, token: str = None) -> Dict[str, Any]:
        """Crea un nuevo comentario en un post (requiere autenticación)"""
        if token is None:
            token = self.get_current_token()
            if not token:
                return {"success": False, "message": "No hay token disponible"}
        
        params = f"{token} {id_post} {contenido}"
        response = self.call_service("comm", "create_comment", params)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing comment response"}
        else:
            return {"success": False, "message": response.get('message', 'Comment service error')}
    
    def comment_get_comment(self, id_comentario: str, token: str = None) -> Dict[str, Any]:
        """Obtiene un comentario específico por ID (requiere autenticación)"""
        if token is None:
            token = self.get_current_token()
            if not token:
                return {"success": False, "message": "No hay token disponible"}
        
        params = f"{token} {id_comentario}"
        response = self.call_service("comm", "get_comment", params)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing comment response"}
        else:
            return {"success": False, "message": response.get('message', 'Comment service error')}
    
    def comment_list_comments(self, id_post: str, token: str = None) -> Dict[str, Any]:
        """Lista todos los comentarios de un post específico (requiere autenticación)"""
        if token is None:
            token = self.get_current_token()
            if not token:
                return {"success": False, "message": "No hay token disponible"}
        
        params = f"{token} {id_post}"
        response = self.call_service("comm", "list_comments", params)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing comment response"}
        else:
            return {"success": False, "message": response.get('message', 'Comment service error')}
    
    def comment_list_my_comments(self, token: str = None) -> Dict[str, Any]:
        """Lista los comentarios creados por el usuario autenticado"""
        if token is None:
            token = self.get_current_token()
            if not token:
                return {"success": False, "message": "No hay token disponible"}
        
        response = self.call_service("comm", "list_my_comments", token)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing comment response"}
        else:
            return {"success": False, "message": response.get('message', 'Comment service error')}
    
    def comment_update_comment(self, id_comentario: str, contenido: str, token: str = None) -> Dict[str, Any]:
        """Actualiza un comentario (solo el autor o moderador)"""
        if token is None:
            token = self.get_current_token()
            if not token:
                return {"success": False, "message": "No hay token disponible"}
        
        params = f"{token} {id_comentario} {contenido}"
        response = self.call_service("comm", "update_comment", params)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing comment response"}
        else:
            return {"success": False, "message": response.get('message', 'Comment service error')}
    
    def comment_delete_comment(self, id_comentario: str, token: str = None) -> Dict[str, Any]:
        """Elimina un comentario (solo el autor o moderador)"""
        if token is None:
            token = self.get_current_token()
            if not token:
                return {"success": False, "message": "No hay token disponible"}
        
        params = f"{token} {id_comentario}"
        response = self.call_service("comm", "delete_comment", params)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing comment response"}
        else:
            return {"success": False, "message": response.get('message', 'Comment service error')}
    
    def comment_admin_delete_comment(self, id_comentario: str, token: str = None) -> Dict[str, Any]:
        """Elimina cualquier comentario (solo moderadores)"""
        if token is None:
            token = self.get_current_token()
            if not token:
                return {"success": False, "message": "No hay token disponible"}
        
        params = f"{token} {id_comentario}"
        response = self.call_service("comm", "admin_delete_comment", params)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing comment response"}
        else:
            return {"success": False, "message": response.get('message', 'Comment service error')}
    
    # Métodos helper para el servicio de eventos
    def event_create_event(self, nombre: str, descripcion: str, fecha: str, token: str = None) -> Dict[str, Any]:
        """Crea un nuevo evento (requiere autenticación)"""
        if token is None:
            token = self.get_current_token()
            if not token:
                return {"success": False, "message": "No hay token disponible"}
        
        params = f"{token} '{nombre}' '{descripcion}' {fecha}"
        response = self.call_service("event", "create_event", params)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing event response"}
        else:
            return {"success": False, "message": response.get('message', 'Event service error')}
    
    def event_get_event(self, id_evento: str, token: str = None) -> Dict[str, Any]:
        """Obtiene un evento específico por ID (requiere autenticación)"""
        if token is None:
            token = self.get_current_token()
            if not token:
                return {"success": False, "message": "No hay token disponible"}
        
        params = f"{token} {id_evento}"
        response = self.call_service("event", "get_event", params)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing event response"}
        else:
            return {"success": False, "message": response.get('message', 'Event service error')}
    
    def event_list_events(self, token: str = None) -> Dict[str, Any]:
        """Lista todos los eventos disponibles (requiere autenticación)"""
        if token is None:
            token = self.get_current_token()
            if not token:
                return {"success": False, "message": "No hay token disponible"}
        
        response = self.call_service("event", "list_events", token)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing event response"}
        else:
            return {"success": False, "message": response.get('message', 'Event service error')}
    
    def event_list_my_events(self, token: str = None) -> Dict[str, Any]:
        """Lista los eventos creados por el usuario autenticado"""
        if token is None:
            token = self.get_current_token()
            if not token:
                return {"success": False, "message": "No hay token disponible"}
        
        response = self.call_service("event", "list_my_events", token)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing event response"}
        else:
            return {"success": False, "message": response.get('message', 'Event service error')}
    
    def event_update_event(self, id_evento: str, nombre: str, descripcion: str, fecha: str, token: str = None) -> Dict[str, Any]:
        """Actualiza un evento (solo el creador o moderador)"""
        if token is None:
            token = self.get_current_token()
            if not token:
                return {"success": False, "message": "No hay token disponible"}
        
        params = f"{token} {id_evento} '{nombre}' '{descripcion}' {fecha}"
        response = self.call_service("event", "update_event", params)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing event response"}
        else:
            return {"success": False, "message": response.get('message', 'Event service error')}
    
    def event_delete_event(self, id_evento: str, token: str = None) -> Dict[str, Any]:
        """Elimina un evento (solo el creador o moderador)"""
        if token is None:
            token = self.get_current_token()
            if not token:
                return {"success": False, "message": "No hay token disponible"}
        
        params = f"{token} {id_evento}"
        response = self.call_service("event", "delete_event", params)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing event response"}
        else:
            return {"success": False, "message": response.get('message', 'Event service error')}
    
    def event_admin_delete_event(self, id_evento: str, token: str = None) -> Dict[str, Any]:
        """Elimina cualquier evento (solo moderadores)"""
        if token is None:
            token = self.get_current_token()
            if not token:
                return {"success": False, "message": "No hay token disponible"}
        
        params = f"{token} {id_evento}"
        response = self.call_service("event", "admin_delete_event", params)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing event response"}
        else:
            return {"success": False, "message": response.get('message', 'Event service error')}
    
    # Métodos helper para el servicio de mensajes
    def message_send_message(self, email_receptor: str, contenido: str, token: str = None) -> Dict[str, Any]:
        """Envía un mensaje a otro usuario (requiere autenticación)"""
        if token is None:
            token = self.get_current_token()
            if not token:
                return {"success": False, "message": "No hay token disponible"}
        
        params = f"{token} {email_receptor} '{contenido}'"
        response = self.call_service("msg", "send_message", params)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing message response"}
        else:
            return {"success": False, "message": response.get('message', 'Message service error')}
    
    def message_get_message(self, id_mensaje: str, token: str = None) -> Dict[str, Any]:
        """Obtiene un mensaje específico por ID (requiere autenticación)"""
        if token is None:
            token = self.get_current_token()
            if not token:
                return {"success": False, "message": "No hay token disponible"}
        
        params = f"{token} {id_mensaje}"
        response = self.call_service("msg", "get_message", params)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing message response"}
        else:
            return {"success": False, "message": response.get('message', 'Message service error')}
    
    def message_list_sent_messages(self, token: str = None) -> Dict[str, Any]:
        """Lista los mensajes enviados por el usuario autenticado"""
        if token is None:
            token = self.get_current_token()
            if not token:
                return {"success": False, "message": "No hay token disponible"}
        
        response = self.call_service("msg", "list_sent_messages", token)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing message response"}
        else:
            return {"success": False, "message": response.get('message', 'Message service error')}
    
    def message_list_received_messages(self, token: str = None) -> Dict[str, Any]:
        """Lista los mensajes recibidos por el usuario autenticado"""
        if token is None:
            token = self.get_current_token()
            if not token:
                return {"success": False, "message": "No hay token disponible"}
        
        response = self.call_service("msg", "list_received_messages", token)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing message response"}
        else:
            return {"success": False, "message": response.get('message', 'Message service error')}
    
    def message_list_conversation(self, email_otro_usuario: str, token: str = None) -> Dict[str, Any]:
        """Lista la conversación entre el usuario autenticado y otro usuario"""
        if token is None:
            token = self.get_current_token()
            if not token:
                return {"success": False, "message": "No hay token disponible"}
        
        params = f"{token} {email_otro_usuario}"
        response = self.call_service("msg", "list_conversation", params)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing message response"}
        else:
            return {"success": False, "message": response.get('message', 'Message service error')}
    
    def message_delete_message(self, id_mensaje: str, token: str = None) -> Dict[str, Any]:
        """Elimina un mensaje (solo el emisor o moderador)"""
        if token is None:
            token = self.get_current_token()
            if not token:
                return {"success": False, "message": "No hay token disponible"}
        
        params = f"{token} {id_mensaje}"
        response = self.call_service("msg", "delete_message", params)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing message response"}
        else:
            return {"success": False, "message": response.get('message', 'Message service error')}
    
    def message_admin_delete_message(self, id_mensaje: str, token: str = None) -> Dict[str, Any]:
        """Elimina cualquier mensaje (solo moderadores)"""
        if token is None:
            token = self.get_current_token()
            if not token:
                return {"success": False, "message": "No hay token disponible"}
        
        params = f"{token} {id_mensaje}"
        response = self.call_service("msg", "admin_delete_message", params)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing message response"}
        else:
            return {"success": False, "message": response.get('message', 'Message service error')}
    
    # Métodos helper para el servicio de reportes
    def report_create_report(self, contenido_id: str, tipo_contenido: str, razon: str, token: str = None) -> Dict[str, Any]:
        """Crea un reporte de contenido inapropiado (requiere autenticación)"""
        if token is None:
            token = self.get_current_token()
            if not token:
                return {"success": False, "message": "No hay token disponible"}
        
        params = f"{token} {contenido_id} {tipo_contenido} '{razon}'"
        response = self.call_service("reprt", "create_report", params)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing report response"}
        else:
            return {"success": False, "message": response.get('message', 'Report service error')}
    
    def report_get_report(self, id_reporte: str, token: str = None) -> Dict[str, Any]:
        """Obtiene un reporte específico por ID (solo moderadores)"""
        if token is None:
            token = self.get_current_token()
            if not token:
                return {"success": False, "message": "No hay token disponible"}
        
        params = f"{token} {id_reporte}"
        response = self.call_service("reprt", "get_report", params)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing report response"}
        else:
            return {"success": False, "message": response.get('message', 'Report service error')}
    
    def report_list_reports(self, token: str = None) -> Dict[str, Any]:
        """Lista todos los reportes (solo moderadores)"""
        if token is None:
            token = self.get_current_token()
            if not token:
                return {"success": False, "message": "No hay token disponible"}
        
        response = self.call_service("reprt", "list_reports", token)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing report response"}
        else:
            return {"success": False, "message": response.get('message', 'Report service error')}
    
    def report_list_my_reports(self, token: str = None) -> Dict[str, Any]:
        """Lista los reportes creados por el usuario autenticado"""
        if token is None:
            token = self.get_current_token()
            if not token:
                return {"success": False, "message": "No hay token disponible"}
        
        response = self.call_service("reprt", "list_my_reports", token)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing report response"}
        else:
            return {"success": False, "message": response.get('message', 'Report service error')}
    
    def report_update_report_status(self, id_reporte: str, estado: str, token: str = None) -> Dict[str, Any]:
        """Actualiza el estado de un reporte (solo moderadores)"""
        if token is None:
            token = self.get_current_token()
            if not token:
                return {"success": False, "message": "No hay token disponible"}
        
        params = f"{token} {id_reporte} {estado}"
        response = self.call_service("reprt", "update_report_status", params)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing report response"}
        else:
            return {"success": False, "message": response.get('message', 'Report service error')}
    
    def report_delete_report(self, id_reporte: str, token: str = None) -> Dict[str, Any]:
        """Elimina un reporte (solo el creador o moderador)"""
        if token is None:
            token = self.get_current_token()
            if not token:
                return {"success": False, "message": "No hay token disponible"}
        
        params = f"{token} {id_reporte}"
        response = self.call_service("reprt", "delete_report", params)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing report response"}
        else:
            return {"success": False, "message": response.get('message', 'Report service error')}
    
    def report_admin_delete_report(self, id_reporte: str, token: str = None) -> Dict[str, Any]:
        """Elimina cualquier reporte (solo moderadores)"""
        if token is None:
            token = self.get_current_token()
            if not token:
                return {"success": False, "message": "No hay token disponible"}
        
        params = f"{token} {id_reporte}"
        response = self.call_service("reprt", "admin_delete_report", params)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing report response"}
        else:
            return {"success": False, "message": response.get('message', 'Report service error')}
    
    # Métodos helper para el servicio de notificaciones
    def notification_list_notifications(self, limit: int = 50, token: str = None) -> Dict[str, Any]:
        """Lista las notificaciones del usuario autenticado"""
        if token is None:
            token = self.get_current_token()
            if not token:
                return {"success": False, "message": "No hay token disponible"}
        
        params = f"{token} {limit}"
        response = self.call_service("notif", "list_notifications", params)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing notification response"}
        else:
            return {"success": False, "message": response.get('message', 'Notification service error')}
    
    def notification_get_unread_count(self, token: str = None) -> Dict[str, Any]:
        """Obtiene el número de notificaciones no leídas del usuario"""
        if token is None:
            token = self.get_current_token()
            if not token:
                return {"success": False, "message": "No hay token disponible"}
        
        response = self.call_service("notif", "get_unread_count", token)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing notification response"}
        else:
            return {"success": False, "message": response.get('message', 'Notification service error')}
    
    def notification_mark_as_read(self, id_notificacion: str, token: str = None) -> Dict[str, Any]:
        """Marca una notificación específica como leída"""
        if token is None:
            token = self.get_current_token()
            if not token:
                return {"success": False, "message": "No hay token disponible"}
        
        params = f"{token} {id_notificacion}"
        response = self.call_service("notif", "mark_as_read", params)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing notification response"}
        else:
            return {"success": False, "message": response.get('message', 'Notification service error')}
    
    def notification_mark_all_as_read(self, token: str = None) -> Dict[str, Any]:
        """Marca todas las notificaciones del usuario como leídas"""
        if token is None:
            token = self.get_current_token()
            if not token:
                return {"success": False, "message": "No hay token disponible"}
        
        response = self.call_service("notif", "mark_all_as_read", token)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing notification response"}
        else:
            return {"success": False, "message": response.get('message', 'Notification service error')}
    
    def notification_get_notification(self, id_notificacion: str, token: str = None) -> Dict[str, Any]:
        """Obtiene una notificación específica por ID"""
        if token is None:
            token = self.get_current_token()
            if not token:
                return {"success": False, "message": "No hay token disponible"}
        
        params = f"{token} {id_notificacion}"
        response = self.call_service("notif", "get_notification", params)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing notification response"}
        else:
            return {"success": False, "message": response.get('message', 'Notification service error')}
    
    def notification_delete_notification(self, id_notificacion: str, token: str = None) -> Dict[str, Any]:
        """Elimina una notificación específica"""
        if token is None:
            token = self.get_current_token()
            if not token:
                return {"success": False, "message": "No hay token disponible"}
        
        params = f"{token} {id_notificacion}"
        response = self.call_service("notif", "delete_notification", params)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing notification response"}
        else:
            return {"success": False, "message": response.get('message', 'Notification service error')}
    
    def notification_clear_all_notifications(self, token: str = None) -> Dict[str, Any]:
        """Elimina todas las notificaciones del usuario"""
        if token is None:
            token = self.get_current_token()
            if not token:
                return {"success": False, "message": "No hay token disponible"}
        
        response = self.call_service("notif", "clear_all_notifications", token)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing notification response"}
        else:
            return {"success": False, "message": response.get('message', 'Notification service error')}
    
    def notification_admin_list_all_notifications(self, limit: int = 100, token: str = None) -> Dict[str, Any]:
        """Lista todas las notificaciones del sistema (solo moderadores)"""
        if token is None:
            token = self.get_current_token()
            if not token:
                return {"success": False, "message": "No hay token disponible"}
        
        params = f"{token} {limit}"
        response = self.call_service("notif", "admin_list_all_notifications", params)
        
        if response.get('status') == 'success':
            try:
                return json.loads(response.get('result', '{}'))
            except json.JSONDecodeError:
                return {"success": False, "message": "Error parsing notification response"}
        else:
            return {"success": False, "message": response.get('message', 'Notification service error')}
    
    def interactive_mode(self):
        print("\n" + "="*60)
        print("🚀 CLIENTE SOA INTERACTIVO")
        print("="*60)
        print("Usando protocolo NNNNNSSSSSDATOS (SIN JSON)")
        print("="*60)
        print("Comandos disponibles:")
        print("  list - Lista servicios conocidos")
        print("  methods <servicio> - Métodos de un servicio")
        print("  call <servicio> <método> [parámetros] - Llama a un método")
        print("  login <email> <password> - Autenticarse y guardar token")
        print("  logout - Cerrar sesión actual")
        print("  whoami - Ver usuario logueado")
        print("  auth - Para ver comandos específicos de auth")
        print("  prof - Para ver comandos específicos de prof")
        print("  forum - Para ver comandos específicos de forum")
        print("  post - Para ver comandos específicos de post")
        print("  comm - Para ver comandos específicos de comm")
        print("  event - Para ver comandos específicos de event")
        print("  msg - Para ver comandos específicos de msg")
        print("  reprt - Para ver comandos específicos de reprt")
        print("  notif - Para ver comandos específicos de notif")
        print("  quit - Salir")
        print("="*60)
        print("Ejemplos:")
        print("  login admin@institucional.edu.co admin123")
        print("  whoami")
        print("  # Con sesión activa (token automático):")
        print("  call prof create_profile https://avatar.com/juan.jpg 'Estudiante de ingeniería'")
        print("  call prof get_profile")
        print("  call prof update_profile https://new-avatar.com/juan.jpg 'Nueva biografía'")
        print("  call prof list_profiles  # Solo moderadores")
        print("  call forum create_forum 'Programación en Python' 'Tecnología'")
        print("  call forum list_forums")
        print("  call forum get_forum 1")
        print("  call forum list_my_forums")
        print("  call post create_post 1 'Mi primer post en este foro'")
        print("  call post list_posts 1")
        print("  call post get_post 1")
        print("  call msg send_message admin@institucional.edu.co 'Hola, este es mi primer mensaje'")
        print("  call msg list_received_messages")
        print("  call msg list_sent_messages")
        print("  call msg list_conversation admin@institucional.edu.co")
        print("  logout")
        print("  # También puedes usar métodos específicos de auth:")
        print("  call auth register juan@estudiante.edu.co pass123 estudiante")
        print("  call auth users")
        print("  auth - Para ver comandos específicos de auth")
        print("  prof - Para ver comandos específicos de prof")
        print("  forum - Para ver comandos específicos de forum")
        print("  post - Para ver comandos específicos de post")
        print("  comm - Para ver comandos específicos de comm")
        print("  event - Para ver comandos específicos de event")
        print("  msg - Para ver comandos específicos de msg")
        print("  reprt - Para ver comandos específicos de reprt")
        print("  notif - Para ver comandos específicos de notif")
        print("="*60)
        print("✨ NUEVO: Si estás logueado, el token se envía automáticamente para servicios que lo requieren")
        print("="*60)
        
        while True:
            try:
                # Crear prompt dinámico con información del usuario
                if self.current_user:
                    user_info = f"{self.current_user.get('email')} ({self.current_user.get('rol')})"
                    prompt = f"\n🎯 SOA[{user_info}]> "
                else:
                    prompt = f"\n🎯 SOA> "
                
                command = input(prompt).strip()
                
                if not command:
                    continue
                
                parts = command.split()
                cmd = parts[0].lower()
                
                if cmd == 'quit' or cmd == 'exit':
                    print("👋 ¡Hasta luego!")
                    break
                
                elif cmd == 'list':
                    self.list_services()
                
                elif cmd == 'methods' and len(parts) >= 2:
                    service_name = parts[1]
                    self.get_service_methods(service_name)
                
                elif cmd == 'auth':
                    self._show_auth_commands()
                
                elif cmd == 'prof':
                    self._show_prof_commands()
                
                elif cmd == 'forum':
                    self._show_forum_commands()
                
                elif cmd == 'post':
                    self._show_post_commands()
                
                elif cmd == 'comm':
                    self._show_comment_commands()
                
                elif cmd == 'event':
                    self._show_event_commands()
                
                elif cmd == 'msg':
                    self._show_message_commands()
                
                elif cmd == 'reprt':
                    self._show_report_commands()
                
                elif cmd == 'notif':
                    self._show_notification_commands()
                
                elif cmd == 'call' and len(parts) >= 3:
                    service_name = parts[1]
                    method_name = parts[2]
                    
                    # Parámetros como string simple
                    params_str = ' '.join(parts[3:]) if len(parts) > 3 else ""
                    
                    print(f"\n🔄 Llamando {service_name}.{method_name}({params_str})...")
                    response = self.call_service(service_name, method_name, params_str)
                    
                    if response.get('status') == 'success':
                        result = response.get('result', '')
                        
                        # Si es una respuesta del servicio auth, intentar formatear el JSON
                        if service_name == 'auth':
                            try:
                                auth_result = json.loads(result)
                                if auth_result.get('success'):
                                    print(f"✅ {auth_result.get('message', 'Operación exitosa')}")
                                    
                                    # Mostrar información adicional según el método
                                    if method_name == 'login' and auth_result.get('token'):
                                        user_info = auth_result.get('user', {})
                                        print(f"👤 Usuario: {user_info.get('email')} ({user_info.get('rol')})")
                                        print(f"🔑 Token JWT: {auth_result.get('token')[:50]}...")
                                    elif method_name == 'register' and auth_result.get('token'):
                                        user_info = auth_result.get('user', {})
                                        print(f"👤 Usuario creado: {user_info.get('email')} ({user_info.get('rol')})")
                                    elif method_name == 'users' and auth_result.get('users'):
                                        users = auth_result.get('users', [])
                                        print(f"📋 Total de usuarios: {len(users)}")
                                        for user in users:
                                            print(f"   👤 {user.get('email')} ({user.get('rol')})")
                                    elif method_name == 'verify' and auth_result.get('payload'):
                                        payload = auth_result.get('payload')
                                        print(f"👤 Usuario: {payload.get('email')} ({payload.get('rol')})")
                                        print(f"📅 Expedido: {payload.get('iat')} | Expira: {payload.get('exp')}")
                                else:
                                    print(f"❌ Error: {auth_result.get('message', 'Unknown error')}")
                            except json.JSONDecodeError:
                                print(f"✅ Resultado: {result}")
                        elif service_name == 'prof':
                            try:
                                prof_result = json.loads(result)
                                if prof_result.get('success'):
                                    print(f"✅ {prof_result.get('message', 'Operación exitosa')}")
                                    
                                    # Mostrar información adicional según el método
                                    if method_name in ['create_profile', 'get_profile', 'update_profile'] and prof_result.get('profile'):
                                        profile = prof_result.get('profile', {})
                                        print(f"👤 Email: {profile.get('email')}")
                                        print(f"🆔 ID Perfil: {profile.get('id_perfil')}")
                                        if profile.get('avatar'):
                                            print(f"🖼️  Avatar: {profile.get('avatar')}")
                                        if profile.get('biografia'):
                                            print(f"📝 Biografía: {profile.get('biografia')}")
                                        if profile.get('created_at'):
                                            print(f"📅 Creado: {profile.get('created_at')}")
                                        if profile.get('updated_at'):
                                            print(f"🔄 Actualizado: {profile.get('updated_at')}")
                                    elif method_name == 'list_profiles' and prof_result.get('profiles'):
                                        profiles = prof_result.get('profiles', [])
                                        print(f"📋 Total de perfiles: {len(profiles)}")
                                        for profile in profiles:
                                            print(f"   👤 {profile.get('email')} (ID: {profile.get('id_perfil')})")
                                            if profile.get('biografia'):
                                                bio_preview = profile.get('biografia')[:50] + ('...' if len(profile.get('biografia', '')) > 50 else '')
                                                print(f"      📝 {bio_preview}")
                                else:
                                    print(f"❌ Error: {prof_result.get('message', 'Unknown error')}")
                            except json.JSONDecodeError:
                                print(f"✅ Resultado: {result}")
                        elif service_name == 'forum':
                            try:
                                forum_result = json.loads(result)
                                if forum_result.get('success'):
                                    print(f"✅ {forum_result.get('message', 'Operación exitosa')}")
                                    
                                    # Mostrar información adicional según el método
                                    if method_name in ['create_forum', 'get_forum', 'update_forum'] and forum_result.get('forum'):
                                        forum = forum_result.get('forum', {})
                                        print(f"🆔 ID Foro: {forum.get('id_foro')}")
                                        print(f"📰 Título: {forum.get('titulo')}")
                                        print(f"📂 Categoría: {forum.get('categoria')}")
                                        print(f"👤 Creador: {forum.get('creador_email')}")
                                        if forum.get('created_at'):
                                            print(f"📅 Creado: {forum.get('created_at')}")
                                        if forum.get('updated_at'):
                                            print(f"🔄 Actualizado: {forum.get('updated_at')}")
                                    elif method_name in ['list_forums', 'list_my_forums'] and forum_result.get('forums'):
                                        forums = forum_result.get('forums', [])
                                        print(f"📋 Total de foros: {len(forums)}")
                                        for forum in forums:
                                            print(f"   🆔 {forum.get('id_foro')} - 📰 {forum.get('titulo')}")
                                            print(f"      📂 {forum.get('categoria')} | 👤 {forum.get('creador_email')}")
                                            if forum.get('created_at'):
                                                print(f"      📅 {forum.get('created_at')}")
                                else:
                                    print(f"❌ Error: {forum_result.get('message', 'Unknown error')}")
                            except json.JSONDecodeError:
                                print(f"✅ Resultado: {result}")
                        elif service_name == 'post':
                            try:
                                post_result = json.loads(result)
                                if post_result.get('success'):
                                    print(f"✅ {post_result.get('message', 'Operación exitosa')}")
                                    
                                    # Mostrar información adicional según el método
                                    if method_name in ['create_post', 'get_post'] and post_result.get('post'):
                                        post = post_result.get('post', {})
                                        print(f"🆔 ID Post: {post.get('id_post')}")
                                        print(f"📝 Contenido: {post.get('contenido')}")
                                    elif method_name in ['list_posts', 'list_my_posts'] and post_result.get('posts'):
                                        posts = post_result.get('posts', [])
                                        print(f"📋 Total de posts: {len(posts)}")
                                        for post in posts[-2:]:  # Mostrar solo los últimos 2
                                            print(f"     💬 {post.get('contenido')[:40]}... por {post.get('autor_email')}")
                                else:
                                    print(f"❌ Error: {post_result.get('message', 'Unknown error')}")
                            except json.JSONDecodeError:
                                print(f"✅ Resultado: {result}")
                        elif service_name == 'comm':
                            try:
                                comment_result = json.loads(result)
                                if comment_result.get('success'):
                                    print(f"✅ {comment_result.get('message', 'Operación exitosa')}")
                                    
                                    # Mostrar información adicional según el método
                                    if method_name in ['create_comment', 'get_comment'] and comment_result.get('comment'):
                                        comment = comment_result.get('comment', {})
                                        print(f"🆔 ID Comentario: {comment.get('id_comentario')}")
                                        print(f"💬 Contenido: {comment.get('contenido')}")
                                        if comment.get('autor_email'):
                                            print(f"👤 Autor: {comment.get('autor_email')}")
                                        if comment.get('id_post'):
                                            print(f"📝 En Post: {comment.get('id_post')}")
                                        if comment.get('fecha'):
                                            print(f"📅 Fecha: {comment.get('fecha')}")
                                    elif method_name in ['list_comments', 'list_my_comments'] and comment_result.get('comments'):
                                        comments = comment_result.get('comments', [])
                                        print(f"📋 Total de comentarios: {len(comments)}")
                                        for comment in comments[-5:]:  # Mostrar solo los últimos 5
                                            content_preview = comment.get('contenido', '')[:50] + ('...' if len(comment.get('contenido', '')) > 50 else '')
                                            print(f"   🆔 {comment.get('id_comentario')} - 💬 {content_preview}")
                                            print(f"      👤 {comment.get('autor_email')} | 📅 {comment.get('fecha')}")
                                            if comment.get('post_preview'):
                                                print(f"      📝 Post: {comment.get('post_preview')}")
                                else:
                                    print(f"❌ Error: {comment_result.get('message', 'Unknown error')}")
                            except json.JSONDecodeError:
                                print(f"✅ Resultado: {result}")
                        elif service_name == 'event':
                            try:
                                event_result = json.loads(result)
                                if event_result.get('success'):
                                    print(f"✅ {event_result.get('message', 'Operación exitosa')}")
                                    
                                    # Mostrar información adicional según el método
                                    if method_name in ['create_event', 'get_event'] and event_result.get('event'):
                                        event = event_result.get('event', {})
                                        print(f"🆔 ID Evento: {event.get('id_evento')}")
                                        print(f"📅 Nombre: {event.get('nombre')}")
                                        print(f"📝 Descripción: {event.get('descripcion')}")
                                        print(f"📅 Fecha: {event.get('fecha')}")
                                        print(f"👤 Creador: {event.get('creador_email')}")
                                    elif method_name == 'list_events' and event_result.get('events'):
                                        events = event_result.get('events', [])
                                        print(f"📋 Total de eventos: {len(events)}")
                                        for event in events[-2:]:  # Mostrar solo los últimos 2
                                            print(f"     📅 {event.get('nombre')} ({event.get('fecha')}) por {event.get('creador_email')}")
                                    elif method_name == 'list_my_events' and event_result.get('events'):
                                        events = event_result.get('events', [])
                                        print(f"📋 Mis eventos: {len(events)}")
                                        for event in events[-2:]:  # Mostrar solo los últimos 2
                                            print(f"     📅 {event.get('nombre')} - {event.get('fecha')}")
                                    elif method_name == 'update_event' and event_result.get('event'):
                                        event = event_result.get('event', {})
                                        print(f"📅 Evento actualizado: {event.get('nombre')}")
                                        print(f"📝 Descripción: {event.get('descripcion')}")
                                        print(f"📅 Fecha: {event.get('fecha')}")
                                        print(f"👤 Creador: {event.get('creador_email')}")
                                    elif method_name in ['delete_event', 'admin_delete_event']:
                                        print(f"✅ Evento eliminado exitosamente")
                                else:
                                    print(f"❌ Error: {event_result.get('message', 'Unknown error')}")
                            except json.JSONDecodeError:
                                print(f"✅ Resultado: {result}")
                        elif service_name == 'msg':
                            try:
                                message_result = json.loads(result)
                                if message_result.get('success'):
                                    print(f"✅ {message_result.get('message', 'Operación exitosa')}")
                                    
                                    # Mostrar información adicional según el método
                                    if method_name in ['send_message', 'get_message'] and message_result.get('message_data'):
                                        message = message_result.get('message_data', {})
                                        print(f"🆔 ID Mensaje: {message.get('id_mensaje')}")
                                        print(f"💬 Contenido: {message.get('contenido')}")
                                        if message.get('emisor_email'):
                                            print(f"👤 Emisor: {message.get('emisor_email')}")
                                        if message.get('receptor_email'):
                                            print(f"👤 Receptor: {message.get('receptor_email')}")
                                        if message.get('fecha'):
                                            print(f"📅 Fecha: {message.get('fecha')}")
                                    elif method_name in ['list_sent_messages', 'list_received_messages'] and message_result.get('messages'):
                                        messages = message_result.get('messages', [])
                                        print(f"📋 Total de mensajes: {len(messages)}")
                                        for message in messages[-5:]:  # Mostrar solo los últimos 5
                                            content_preview = message.get('contenido', '')[:50] + ('...' if len(message.get('contenido', '')) > 50 else '')
                                            print(f"   🆔 {message.get('id_mensaje')} - 💬 {content_preview}")
                                            print(f"      👤 De: {message.get('emisor_email')} → Para: {message.get('receptor_email')}")
                                            print(f"      📅 {message.get('fecha')}")
                                    elif method_name == 'list_conversation' and message_result.get('messages'):
                                        messages = message_result.get('messages', [])
                                        other_user = message_result.get('other_user', 'Usuario')
                                        print(f"👥 Conversación con {other_user} ({len(messages)} mensajes):")
                                        for message in messages[-10:]:  # Mostrar solo los últimos 10
                                            content_preview = message.get('contenido', '')[:60] + ('...' if len(message.get('contenido', '')) > 60 else '')
                                            is_sent = message.get('is_sent', False)
                                            direction = "→" if is_sent else "←"
                                            print(f"   {direction} {content_preview}")
                                            print(f"      👤 {message.get('emisor_email')} | 📅 {message.get('fecha')}")
                                    elif method_name in ['delete_message', 'admin_delete_message']:
                                        print(f"✅ Mensaje eliminado exitosamente")
                                else:
                                    print(f"❌ Error: {message_result.get('message', 'Unknown error')}")
                            except json.JSONDecodeError:
                                print(f"✅ Resultado: {result}")
                        elif service_name == 'reprt':
                            try:
                                report_result = json.loads(result)
                                if report_result.get('success'):
                                    print(f"✅ {report_result.get('message', 'Operación exitosa')}")
                                    
                                    # Mostrar información adicional según el método
                                    if method_name in ['create_report', 'get_report'] and report_result.get('report'):
                                        report = report_result.get('report', {})
                                        print(f"🆔 ID Reporte: {report.get('id_reporte')}")
                                        print(f"📝 Contenido: {report.get('contenido')}")
                                        print(f"🎯 Tipo: {report.get('tipo_contenido')}")
                                        print(f"📅 Fecha: {report.get('fecha')}")
                                        print(f"👤 Reportado por: {report.get('reportado_por')}")
                                        print(f"🏷️ Estado: {report.get('estado')}")
                                else:
                                    print(f"❌ Error: {report_result.get('message', 'Unknown error')}")
                            except json.JSONDecodeError:
                                print(f"✅ Resultado: {result}")
                        elif service_name == 'notif':
                            try:
                                notification_result = json.loads(result)
                                if notification_result.get('success'):
                                    print(f"✅ {notification_result.get('message', 'Operación exitosa')}")
                                    
                                    # Mostrar información adicional según el método
                                    if method_name in ['list_notifications', 'get_unread_count', 'mark_as_read', 'mark_all_as_read', 'get_notification', 'delete_notification', 'clear_all_notifications', 'admin_list_all_notifications']:
                                        if method_name == 'list_notifications':
                                            notifications = notification_result.get('notifications', [])
                                            print(f"📋 Notificaciones: {len(notifications)}")
                                            for notification in notifications:
                                                print(f"   🆔 {notification.get('id_notificacion')} - 📋 {notification.get('titulo')}")
                                        elif method_name == 'get_unread_count':
                                            unread_count = notification_result.get('unread_count', 0)
                                            print(f"📋 Total de notificaciones no leídas: {unread_count}")
                                        elif method_name == 'mark_as_read':
                                            print(f"✅ Notificación marcada como leída")
                                        elif method_name == 'mark_all_as_read':
                                            print(f"✅ Todas las notificaciones marcadas como leídas")
                                        elif method_name == 'get_notification':
                                            notification = notification_result.get('notification', {})
                                            print(f"🆔 ID Notificación: {notification.get('id_notificacion')}")
                                            print(f"📋 {notification.get('titulo')}")
                                            print(f"💬 Contenido: {notification.get('contenido')}")
                                            print(f"🎯 Tipo: {notification.get('tipo')}")
                                            print(f"📅 Fecha: {notification.get('fecha')}")
                                        elif method_name == 'delete_notification':
                                            print(f"✅ Notificación eliminada")
                                        elif method_name == 'clear_all_notifications':
                                            print(f"✅ Todas las notificaciones eliminadas")
                                        elif method_name == 'admin_list_all_notifications':
                                            notifications = notification_result.get('notifications', [])
                                            print(f"📋 Notificaciones del sistema: {len(notifications)}")
                                            for notification in notifications:
                                                print(f"   🆔 {notification.get('id_notificacion')} - 📋 {notification.get('titulo')}")
                                else:
                                    print(f"❌ Error: {notification_result.get('message', 'Unknown error')}")
                            except json.JSONDecodeError:
                                print(f"✅ Resultado: {result}")
                    else:
                        print(f"❌ Error: {response.get('message', 'Unknown error')}")
                
                elif cmd == 'login' and len(parts) >= 3:
                    email = parts[1]
                    password = parts[2]
                    self.auth_login(email, password)
                
                elif cmd == 'logout':
                    self.logout()
                
                elif cmd == 'whoami':
                    self.whoami()
                
                else:
                    print("❌ Comando no reconocido. Use 'list', 'methods <servicio>', 'call <servicio> <método> [params]', 'login <email> <password>', 'logout', 'whoami', 'auth', 'prof', 'forum', 'post', 'comm', 'event', 'msg', 'reprt', 'notif', o 'quit'")
            
            except KeyboardInterrupt:
                print("\n👋 ¡Hasta luego!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

    def _show_auth_commands(self):
        """Muestra los comandos específicos del servicio de autenticación"""
        print("\n" + "="*60)
        print("🔐 COMANDOS DEL SERVICIO DE AUTENTICACIÓN")
        print("="*60)
        print("Uso: call auth <método> [parámetros]")
        print("")
        print("Métodos disponibles:")
        print("  login <email> <contraseña>")
        print("    Ejemplo: call auth login admin@institucional.edu.co admin123")
        print("")
        print("  register <email> <contraseña> <rol>")
        print("    Ejemplo: call auth register juan@estudiante.edu.co pass123 estudiante")
        print("")
        print("  verify <token>")
        print("    Ejemplo: call auth verify eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...")
        print("")
        print("  refresh <token>")
        print("    Ejemplo: call auth refresh eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...")
        print("")
        print("  users")
        print("    Ejemplo: call auth users")
        print("")
        print("  delete_user <email>")
        print("    Ejemplo: call auth delete_user test@estudiante.edu.co")
        print("")
        print("  info")
        print("    Ejemplo: call auth info")
        print("="*60)
        print("💡 Usuario por defecto: admin@institucional.edu.co / admin123")
        print("🎯 Roles disponibles: estudiante, moderador")

    def _show_prof_commands(self):
        """Muestra los comandos específicos del servicio de perfiles"""
        print("\n" + "="*60)
        print("👤 COMANDOS DEL SERVICIO DE PERFILES")
        print("="*60)
        print("Uso: call prof <método> [parámetros]")
        print("✨ NUEVO: Si estás logueado, NO necesitas pasar el token manualmente")
        print("")
        print("Métodos para usuarios (gestión de tu propio perfil):")
        print("  create_profile <avatar> <biografía>")
        print("    Ejemplo: call prof create_profile https://avatar.com/mi-foto.jpg 'Mi biografía'")
        print("")
        print("  get_profile")
        print("    Ejemplo: call prof get_profile")
        print("")
        print("  update_profile <avatar> <biografía>")
        print("    Ejemplo: call prof update_profile https://new-avatar.com/foto.jpg 'Nueva biografía'")
        print("")
        print("  delete_profile")
        print("    Ejemplo: call prof delete_profile")
        print("")
        print("Métodos para moderadores:")
        print("  list_profiles")
        print("    Ejemplo: call prof list_profiles")
        print("")
        print("  admin_get_profile <email_usuario>")
        print("    Ejemplo: call prof admin_get_profile juan@estudiante.edu.co")
        print("")
        print("  admin_delete_profile <email_usuario>")
        print("    Ejemplo: call prof admin_delete_profile test@estudiante.edu.co")
        print("")
        print("General:")
        print("  info")
        print("    Ejemplo: call prof info")
        print("="*60)
        print("💡 Para loguearte: login tu@email.com tu_password")
        print("💡 Para ver tu sesión: whoami")
        print("🎯 Los usuarios solo pueden gestionar su propio perfil")
        print("🎯 Los moderadores pueden usar métodos admin_* para gestionar cualquier perfil")
        print("✨ AUTOMÁTICO: El token se envía automáticamente si estás logueado")

    def _show_forum_commands(self):
        """Muestra los comandos específicos del servicio de foros"""
        print("\n" + "="*60)
        print("🗣️ COMANDOS DEL SERVICIO DE FOROS")
        print("="*60)
        print("Uso: call forum <método> [parámetros]")
        print("✨ NUEVO: Si estás logueado, NO necesitas pasar el token manualmente")
        print("")
        print("Métodos para usuarios (gestión de foros):")
        print("  create_forum <titulo> <categoria>")
        print("    Ejemplo: call forum create_forum 'Programación Python' 'Tecnología'")
        print("")
        print("  get_forum <id_foro>")
        print("    Ejemplo: call forum get_forum 1")
        print("")
        print("  list_forums")
        print("    Ejemplo: call forum list_forums")
        print("")
        print("  list_my_forums")
        print("    Ejemplo: call forum list_my_forums")
        print("")
        print("  update_forum <id_foro> <titulo> <categoria>")
        print("    Ejemplo: call forum update_forum 1 'Python Avanzado' 'Programación'")
        print("    📝 Solo el creador o moderadores pueden actualizar")
        print("")
        print("  delete_forum <id_foro>")
        print("    Ejemplo: call forum delete_forum 1")
        print("    🗑️ Solo el creador o moderadores pueden eliminar")
        print("")
        print("Métodos para moderadores:")
        print("  admin_delete_forum <id_foro>")
        print("    Ejemplo: call forum admin_delete_forum 5")
        print("    🛡️ Solo moderadores pueden eliminar cualquier foro")
        print("")
        print("General:")
        print("  info")
        print("    Ejemplo: call forum info")
        print("="*60)
        print("💡 Para loguearte: login tu@email.com tu_password")
        print("💡 Para ver tu sesión: whoami")
        print("🎯 Los usuarios pueden crear y gestionar sus propios foros")
        print("🎯 Los moderadores pueden eliminar cualquier foro con admin_delete_forum")
        print("✨ AUTOMÁTICO: El token se envía automáticamente si estás logueado")
        print("📊 ESTRUCTURA: FORO(id_foro, titulo, categoria, creador_id, created_at, updated_at)")

    def _show_post_commands(self):
        """Muestra los comandos específicos del servicio de posts"""
        print("\n" + "="*60)
        print("💬 COMANDOS DEL SERVICIO DE POSTS")
        print("="*60)
        print("Uso: call post <método> [parámetros]")
        print("✨ NUEVO: Si estás logueado, NO necesitas pasar el token manualmente")
        print("")
        print("Métodos para usuarios (gestión de posts):")
        print("  create_post <id_foro> <contenido>")
        print("    Ejemplo: call post 1 'Este es un nuevo post'")
        print("")
        print("  get_post <id_post>")
        print("    Ejemplo: call post 1")
        print("")
        print("  list_posts <id_foro>")
        print("    Ejemplo: call post 1")
        print("")
        print("  list_my_posts")
        print("    Ejemplo: call post list_my_posts")
        print("")
        print("  update_post <id_post> <contenido>")
        print("    Ejemplo: call post 1 'Este es un post actualizado'")
        print("")
        print("  delete_post <id_post>")
        print("    Ejemplo: call post 1")
        print("")
        print("General:")
        print("  info")
        print("    Ejemplo: call post info")
        print("="*60)
        print("💡 Para loguearte: login tu@email.com tu_password")
        print("💡 Para ver tu sesión: whoami")
        print("🎯 Los usuarios pueden crear y gestionar sus propios posts")
        print("🎯 Los moderadores pueden eliminar cualquier post con admin_delete_post")
        print("✨ AUTOMÁTICO: El token se envía automáticamente si estás logueado")
        print("📊 ESTRUCTURA: POST(id_post, contenido, fecha, id_foro, autor_id)")

    def _show_comment_commands(self):
        """Muestra los comandos específicos del servicio de comentarios"""
        print("\n" + "="*60)
        print("💬 COMANDOS DEL SERVICIO DE COMENTARIOS")
        print("="*60)
        print("Uso: call comm <método> [parámetros]")
        print("✨ NUEVO: Si estás logueado, NO necesitas pasar el token manualmente")
        print("")
        print("Métodos para usuarios (gestión de comentarios):")
        print("  create_comment <id_post> <contenido>")
        print("    Ejemplo: call comm create_comment 1 'Este es un nuevo comentario'")
        print("")
        print("  get_comment <id_comentario>")
        print("    Ejemplo: call comm get_comment 1")
        print("")
        print("  list_comments <id_post>")
        print("    Ejemplo: call comm list_comments 1")
        print("")
        print("  list_my_comments")
        print("    Ejemplo: call comm list_my_comments")
        print("")
        print("  update_comment <id_comentario> <contenido>")
        print("    Ejemplo: call comm update_comment 1 'Este es un comentario actualizado'")
        print("")
        print("  delete_comment <id_comentario>")
        print("    Ejemplo: call comm delete_comment 1")
        print("")
        print("General:")
        print("  info")
        print("    Ejemplo: call comm info")
        print("="*60)
        print("💡 Para loguearte: login tu@email.com tu_password")
        print("💡 Para ver tu sesión: whoami")
        print("🎯 Los usuarios pueden crear y gestionar sus propios comentarios")
        print("🎯 Los moderadores pueden eliminar cualquier comentario con admin_delete_comment")
        print("✨ AUTOMÁTICO: El token se envía automáticamente si estás logueado")
        print("📊 ESTRUCTURA: COMENTARIO(id_comentario, contenido, fecha, id_post, autor_id)")

    def _show_event_commands(self):
        """Muestra los comandos específicos del servicio de eventos"""
        print("\n" + "="*60)
        print("📅 COMANDOS DEL SERVICIO DE EVENTOS")
        print("="*60)
        print("Uso: call event <método> [parámetros]")
        print("")
        print("Métodos disponibles:")
        print("  create_event <nombre> <descripcion> <fecha>")
        print("    Ejemplo: call event 'Evento de prueba' 'Descripción del evento' '2023-04-01'")
        print("")
        print("  get_event <id_evento>")
        print("    Ejemplo: call event 1")
        print("")
        print("  list_events")
        print("    Ejemplo: call event list_events")
        print("")
        print("  list_my_events")
        print("    Ejemplo: call event list_my_events")
        print("")
        print("  update_event <id_evento> <nombre> <descripcion> <fecha>")
        print("    Ejemplo: call event 1 'Evento actualizado' 'Descripción actualizada' '2023-04-02'")
        print("    📝 Solo el creador o moderadores pueden actualizar")
        print("")
        print("  delete_event <id_evento>")
        print("    Ejemplo: call event 1")
        print("    🗑️ Solo el creador o moderadores pueden eliminar")
        print("")
        print("Métodos para moderadores:")
        print("  admin_delete_event <id_evento>")
        print("    Ejemplo: call event admin_delete_event 5")
        print("    🛡️ Solo moderadores pueden eliminar cualquier evento")
        print("")
        print("General:")
        print("  info")
        print("    Ejemplo: call event info")
        print("="*60)
        print("💡 Para loguearte: login tu@email.com tu_password")
        print("💡 Para ver tu sesión: whoami")
        print("🎯 Los usuarios pueden crear y gestionar sus propios eventos")
        print("🎯 Los moderadores pueden eliminar cualquier evento con admin_delete_event")
        print("✨ AUTOMÁTICO: El token se envía automáticamente si estás logueado")
        print("📊 ESTRUCTURA: EVENTO(id_evento, nombre, descripcion, fecha, creador_id, created_at, updated_at)")

    def _show_message_commands(self):
        """Muestra los comandos específicos del servicio de mensajes"""
        print("\n" + "="*60)
        print("💌 COMANDOS DEL SERVICIO DE MENSAJES")
        print("="*60)
        print("Uso: call msg <método> [parámetros]")
        print("")
        print("Métodos disponibles:")
        print("  send_message <email_receptor> <contenido>")
        print("    Ejemplo: call msg send_message admin@institucional.edu.co 'Hola, este es mi primer mensaje'")
        print("")
        print("  get_message <id_mensaje>")
        print("    Ejemplo: call msg get_message 1")
        print("")
        print("  list_sent_messages")
        print("    Ejemplo: call msg list_sent_messages")
        print("")
        print("  list_received_messages")
        print("    Ejemplo: call msg list_received_messages")
        print("")
        print("  list_conversation <email_otro_usuario>")
        print("    Ejemplo: call msg list_conversation admin@institucional.edu.co")
        print("")
        print("  delete_message <id_mensaje>")
        print("    Ejemplo: call msg delete_message 1")
        print("")
        print("  admin_delete_message <id_mensaje>")
        print("    Ejemplo: call msg admin_delete_message 1")
        print("")
        print("General:")
        print("  info")
        print("    Ejemplo: call msg info")
        print("="*60)
        print("💡 Para loguearte: login tu@email.com tu_password")
        print("💡 Para ver tu sesión: whoami")
        print("🎯 Los usuarios pueden enviar y recibir mensajes")
        print("🎯 Los moderadores pueden eliminar cualquier mensaje")
        print("✨ AUTOMÁTICO: El token se envía automáticamente")
        print("📊 ESTRUCTURA: MENSAJE(id_mensaje, contenido, fecha, emisor_id, receptor_id)")

    def _show_report_commands(self):
        """Muestra los comandos específicos del servicio de reportes"""
        print("\n" + "="*60)
        print("📋 COMANDOS DEL SERVICIO DE REPORTES")
        print("="*60)
        print("Uso: call reprt <método> [parámetros]")
        print("")
        print("Métodos disponibles:")
        print("  create_report <contenido_id> <tipo_contenido> <razon>")
        print("    Ejemplo: call reprt create_report 1 'post' 'Contenido inapropiado'")
        print("")
        print("  get_report <id_reporte>")
        print("    Ejemplo: call reprt get_report 1")
        print("")
        print("  list_reports")
        print("    Ejemplo: call reprt list_reports")
        print("")
        print("  list_my_reports")
        print("    Ejemplo: call reprt list_my_reports")
        print("")
        print("  update_report_status <id_reporte> <estado>")
        print("    Ejemplo: call reprt update_report_status 1 'pendiente'")
        print("")
        print("  delete_report <id_reporte>")
        print("    Ejemplo: call reprt delete_report 1")
        print("    🗑️ Solo el creador o moderadores pueden eliminar")
        print("")
        print("Métodos para moderadores:")
        print("  admin_delete_report <id_reporte>")
        print("    Ejemplo: call reprt admin_delete_report 5")
        print("    🛡️ Solo moderadores pueden eliminar cualquier reporte")
        print("")
        print("General:")
        print("  info")
        print("    Ejemplo: call reprt info")
        print("="*60)
        print("💡 Para loguearte: login tu@email.com tu_password")
        print("💡 Para ver tu sesión: whoami")
        print("🎯 Los usuarios pueden crear y gestionar sus propios reportes")
        print("🎯 Los moderadores pueden eliminar cualquier reporte con admin_delete_report")
        print("✨ AUTOMÁTICO: El token se envía automáticamente si estás logueado")
        print("📊 ESTRUCTURA: REPORTE(id_reporte, contenido_id, tipo_contenido, razon, fecha, reportado_por, estado, created_at, updated_at)")

    def _show_notification_commands(self):
        """Muestra los comandos específicos del servicio de notificaciones"""
        print("\n" + "="*60)
        print("📋 COMANDOS DEL SERVICIO DE NOTIFICACIONES")
        print("="*60)
        print("Uso: call notif <método> [parámetros]")
        print("")
        print("Métodos disponibles:")
        print("  list_notifications <limit>")
        print("    Ejemplo: call notif list_notifications 50")
        print("")
        print("  get_unread_count")
        print("    Ejemplo: call notif get_unread_count")
        print("")
        print("  mark_as_read <id_notificacion>")
        print("    Ejemplo: call notif mark_as_read 1")
        print("")
        print("  mark_all_as_read")
        print("    Ejemplo: call notif mark_all_as_read")
        print("")
        print("  get_notification <id_notificacion>")
        print("    Ejemplo: call notif get_notification 1")
        print("")
        print("  delete_notification <id_notificacion>")
        print("    Ejemplo: call notif delete_notification 1")
        print("")
        print("  clear_all_notifications")
        print("    Ejemplo: call notif clear_all_notifications")
        print("")
        print("  admin_list_all_notifications <limit>")
        print("    Ejemplo: call notif admin_list_all_notifications 100")
        print("="*60)
        print("💡 Para ver tus notificaciones: whoami")
        print("🎯 Los usuarios pueden gestionar sus notificaciones")
        print("🎯 Los moderadores pueden ver todas las notificaciones")
        print("✨ AUTOMÁTICO: El token se envía automáticamente")

def run_demo():
    client = SOAClient()
    
    print("\n" + "="*60)
    print("🚀 DEMOSTRACIÓN CLIENTE SOA")
    print("="*60)
    print("Usando protocolo NNNNNSSSSSDATOS (SIN JSON)")
    print("="*60)
    
    # Listar servicios conocidos
    print("\n1. 📋 Servicios conocidos...")
    client.list_services()
    
    # Probar servicio de autenticación
    print("\n2. 🔐 Probando servicio de autenticación...")
    
    # Login con usuario admin y guardar token automáticamente
    print("   📋 Autenticándose con usuario admin...")
    login_result = client.auth_login("admin@institucional.edu.co", "admin123")
    if login_result.get('success'):
        print(f"   ✅ Login exitoso: {login_result.get('user', {}).get('email')}")
        
        # Mostrar información del usuario logueado
        print("   📋 Información del usuario logueado:")
        client.whoami()
            
        # Verificar el token guardado
        print("   📋 Verificando token guardado...")
        verify_result = client.auth_verify_token(client.current_token)
        if verify_result.get('success'):
           payload = verify_result.get('payload', {})
           print(f"   ✅ Token válido para: {payload.get('email')} ({payload.get('rol')})")
        else:
            print(f"   ❌ Error verificando token: {verify_result.get('message')}")
    else:
        print(f"   ❌ Error en login: {login_result.get('message')}")
    
    # Registrar un usuario de prueba
    print("   📋 Registrando usuario de prueba...")
    import time
    test_email = f"demo_{int(time.time())}@demo.com"
    register_result = client.auth_register(test_email, "demo123", "estudiante")
    if register_result.get('success'):
        print(f"   ✅ Usuario registrado: {register_result.get('user', {}).get('email')}")
    else:
        print(f"   ❌ Error registrando usuario: {register_result.get('message')}")
    
    # Listar usuarios
    print("   📋 Listando usuarios...")
    users_result = client.auth_list_users()
    if users_result.get('success'):
        users = users_result.get('users', [])
        print(f"   ✅ Total de usuarios: {len(users)}")
        for user in users[-3:]:  # Mostrar solo los últimos 3
            print(f"     👤 {user.get('email')} ({user.get('rol')})")
    else:
        print(f"   ❌ Error listando usuarios: {users_result.get('message')}")
    
    # Probar servicio de perfiles
    print("\n3. 👤 Probando servicio de perfiles (con token automático)...")
    
    # Verificar que tenemos un token válido
    if not client.current_token:
        print("   ❌ No hay token válido, saltando pruebas de perfiles y foros")
        return
    
    # Crear perfil para el usuario admin (usando token automático)
    print("   📋 Creando perfil para admin (token automático)...")
    admin_profile_result = client.prof_create_profile(
        avatar="https://avatars.example.com/admin.jpg", 
        biografia="Administrador del sistema educativo"
    )
    if admin_profile_result.get('success'):
        profile = admin_profile_result.get('profile', {})
        print(f"   ✅ Perfil creado para admin (ID: {profile.get('id_perfil')})")
    else:
        print(f"   ❌ Error creando perfil admin: {admin_profile_result.get('message')}")
    
    # Obtener el perfil usando el token automático
    print("   📋 Obteniendo mi perfil...")
    get_profile_result = client.prof_get_profile()
    if get_profile_result.get('success'):
        profile = get_profile_result.get('profile', {})
        print(f"   ✅ Perfil obtenido: {profile.get('email')}")
        print(f"     🖼️  Avatar: {profile.get('avatar')}")
        print(f"     📝 Biografía: {profile.get('biografia')}")
    else:
        print(f"   ❌ Error obteniendo perfil: {get_profile_result.get('message')}")
    
    # Actualizar el perfil
    print("   📋 Actualizando mi perfil...")
    update_profile_result = client.prof_update_profile(
        avatar="https://avatars.example.com/admin_updated.jpg",
        biografia="Administrador del sistema educativo actualizado"
    )
    if update_profile_result.get('success'):
        print(f"   ✅ Perfil actualizado exitosamente")
    else:
        print(f"   ❌ Error actualizando perfil: {update_profile_result.get('message')}")
    
    # Crear perfil para el usuario de prueba si existe
    test_token = None
    if register_result.get('success'):
        test_token = register_result.get('token')  # El registro devuelve un token
        
        # Hacer login como el usuario de prueba para demostrar cambio de sesión
        print(f"   📋 Cambiando a sesión del usuario de prueba...")
        client.auth_login(test_email, "demo123")
        
        print(f"   📋 Creando perfil para {test_email}...")
        test_profile_result = client.prof_create_profile(
            avatar="https://avatars.example.com/demo.jpg",
            biografia="Usuario de demostración del sistema"
        )
        if test_profile_result.get('success'):
            profile = test_profile_result.get('profile', {})
            print(f"   ✅ Perfil creado para usuario demo (ID: {profile.get('id_perfil')})")
            
            # Obtener el perfil creado (sin necesidad de especificar token)
            print("   📋 Obteniendo mi perfil...")
            get_profile_result = client.prof_get_profile()
            if get_profile_result.get('success'):
                profile = get_profile_result.get('profile', {})
                print(f"   ✅ Perfil obtenido: {profile.get('email')}")
                print(f"     🖼️  Avatar: {profile.get('avatar')}")
                print(f"     📝 Biografía: {profile.get('biografia')}")
            else:
                print(f"   ❌ Error obteniendo perfil: {get_profile_result.get('message')}")
            
            # Actualizar el perfil
            print("   📋 Actualizando mi perfil...")
            update_profile_result = client.prof_update_profile(
                avatar="https://avatars.example.com/demo_updated.jpg",
                biografia="Usuario de demostración actualizado con nueva información"
            )
            if update_profile_result.get('success'):
                print(f"   ✅ Perfil actualizado exitosamente")
            else:
                print(f"   ❌ Error actualizando perfil: {update_profile_result.get('message')}")
        else:
            print(f"   ❌ Error creando perfil demo: {test_profile_result.get('message')}")
        
        # Volver a loguearse como admin para las pruebas de moderador
        print("   📋 Volviendo a sesión de admin...")
        client.auth_login("admin@institucional.edu.co", "admin123")
    
    # Listar todos los perfiles (solo funciona con token de moderador)
    print("   📋 Listando todos los perfiles (como moderador)...")
    profiles_result = client.prof_list_profiles()
    if profiles_result.get('success'):
        profiles = profiles_result.get('profiles', [])
        print(f"   ✅ Total de perfiles: {len(profiles)}")
        for profile in profiles:
            print(f"     👤 {profile.get('email')} (ID: {profile.get('id_perfil')})")
            if profile.get('biografia'):
                bio_preview = profile.get('biografia')[:40] + ('...' if len(profile.get('biografia', '')) > 40 else '')
                print(f"       📝 {bio_preview}")
    else:
        print(f"   ❌ Error listando perfiles: {profiles_result.get('message')}")
    
    # Probar método admin para obtener perfil específico
    if test_email:
        print(f"   📋 Obteniendo perfil de {test_email} como moderador...")
        admin_get_result = client.prof_admin_get_profile(test_email)
        if admin_get_result.get('success'):
            profile = admin_get_result.get('profile', {})
            print(f"   ✅ Perfil obtenido via admin: {profile.get('email')}")
        else:
            print(f"   ❌ Error obteniendo perfil via admin: {admin_get_result.get('message')}")
    
    # Demostrar logout
    print("   📋 Cerrando sesión...")
    client.logout()
    
    # Probar servicio de foros
    print("\n4. 🗣️ Probando servicio de foros (con token automático)...")
    
    # Necesitamos estar logueados para probar foros
    print("   📋 Relogueándose como admin para pruebas de foros...")
    client.auth_login("admin@institucional.edu.co", "admin123")
    
    if not client.current_token:
        print("   ❌ No se pudo obtener token para pruebas de foros")
        return
    
    # Crear foro de ejemplo
    print("   📋 Creando foro de ejemplo...")
    create_forum_result = client.forum_create_forum(
        titulo="Bienvenida al Sistema",
        categoria="General"
    )
    if create_forum_result.get('success'):
        forum = create_forum_result.get('forum', {})
        print(f"   ✅ Foro creado: {forum.get('titulo')} (ID: {forum.get('id_foro')})")
        created_forum_id = forum.get('id_foro')
    else:
        print(f"   ❌ Error creando foro: {create_forum_result.get('message')}")
        created_forum_id = None
    
    # Crear otro foro
    print("   📋 Creando segundo foro...")
    create_forum2_result = client.forum_create_forum(
        titulo="Programación en Python",
        categoria="Tecnología"
    )
    if create_forum2_result.get('success'):
        forum2 = create_forum2_result.get('forum', {})
        print(f"   ✅ Segundo foro creado: {forum2.get('titulo')} (ID: {forum2.get('id_foro')})")
    else:
        print(f"   ❌ Error creando segundo foro: {create_forum2_result.get('message')}")
    
    # Listar todos los foros
    print("   📋 Listando todos los foros...")
    list_forums_result = client.forum_list_forums()
    if list_forums_result.get('success'):
        forums = list_forums_result.get('forums', [])
        print(f"   ✅ Total de foros encontrados: {len(forums)}")
        for forum in forums[-2:]:  # Mostrar solo los últimos 2
            print(f"     🗣️ {forum.get('titulo')} ({forum.get('categoria')}) por {forum.get('creador_email')}")
    else:
        print(f"   ❌ Error listando foros: {list_forums_result.get('message')}")
    
    # Obtener foro específico
    if created_forum_id:
        print(f"   📋 Obteniendo foro específico (ID: {created_forum_id})...")
        get_forum_result = client.forum_get_forum(str(created_forum_id))
        if get_forum_result.get('success'):
            forum = get_forum_result.get('forum', {})
            print(f"   ✅ Foro obtenido: {forum.get('titulo')}")
            print(f"     📂 Categoría: {forum.get('categoria')}")
            print(f"     👤 Creador: {forum.get('creador_email')}")
        else:
            print(f"   ❌ Error obteniendo foro: {get_forum_result.get('message')}")
    
    # Listar mis foros
    print("   📋 Listando mis foros...")
    my_forums_result = client.forum_list_my_forums()
    if my_forums_result.get('success'):
        my_forums = my_forums_result.get('forums', [])
        print(f"   ✅ Mis foros: {len(my_forums)}")
        for forum in my_forums[-2:]:  # Mostrar solo los últimos 2
            print(f"     🗣️ {forum.get('titulo')} - {forum.get('categoria')}")
    else:
        print(f"   ❌ Error listando mis foros: {my_forums_result.get('message')}")
    
    # Actualizar foro
    if created_forum_id:
        print(f"   📋 Actualizando foro (ID: {created_forum_id})...")
        update_forum_result = client.forum_update_forum(
            str(created_forum_id),
            "Bienvenida Actualizada",
            "Información"
        )
        if update_forum_result.get('success'):
            updated_forum = update_forum_result.get('forum', {})
            print(f"   ✅ Foro actualizado: {updated_forum.get('titulo')}")
        else:
            print(f"   ❌ Error actualizando foro: {update_forum_result.get('message')}")
    
    # Crear usuario de prueba para demostrar permisos
    import time
    test_email_forum = f"forum_test_{int(time.time())}@demo.com"
    print(f"   📋 Creando usuario de prueba: {test_email_forum}...")
    register_forum_result = client.auth_register(test_email_forum, "demo123", "estudiante")
    
    if register_forum_result.get('success'):
        print(f"   ✅ Usuario de prueba creado para foros")
        
        # Loguearse como el usuario de prueba
        print("   📋 Cambiando a sesión del usuario de prueba...")
        client.auth_login(test_email_forum, "demo123")
        
        # Crear foro como estudiante
        print("   📋 Creando foro como estudiante...")
        student_forum_result = client.forum_create_forum(
            "Dudas de Estudiante",
            "Ayuda"
        )
        if student_forum_result.get('success'):
            student_forum = student_forum_result.get('forum', {})
            student_forum_id = student_forum.get('id_foro')
            print(f"   ✅ Foro de estudiante creado: {student_forum.get('titulo')} (ID: {student_forum_id})")
            
            # Intentar eliminar foro de admin (debe fallar)
            if created_forum_id:
                print("   📋 Intentando eliminar foro de admin como estudiante (debe fallar)...")
                delete_admin_forum_result = client.forum_delete_forum(str(created_forum_id))
                if not delete_admin_forum_result.get('success'):
                    print(f"   ✅ Protección funcionando: {delete_admin_forum_result.get('message')}")
                else:
                    print(f"   ❌ Error en protección: estudiante pudo eliminar foro de admin")
            
            # Eliminar su propio foro
            print("   📋 Eliminando propio foro como estudiante...")
            delete_own_forum_result = client.forum_delete_forum(str(student_forum_id))
            if delete_own_forum_result.get('success'):
                print(f"   ✅ Foro propio eliminado exitosamente")
            else:
                print(f"   ❌ Error eliminando foro propio: {delete_own_forum_result.get('message')}")
        else:
            print(f"   ❌ Error creando foro de estudiante: {student_forum_result.get('message')}")
    
    # Volver a loguearse como admin
    print("   📋 Volviendo a sesión de admin...")
    client.auth_login("admin@institucional.edu.co", "admin123")
    
    # Probar servicio de posts
    print("\n5. 💬 Probando servicio de posts (con token automático)...")
    
    # Necesitamos tener foros disponibles para crear posts
    if not created_forum_id:
        # Crear un foro para las pruebas de posts
        print("   📋 Creando foro para pruebas de posts...")
        test_forum_result = client.forum_create_forum(
            titulo="Foro para Posts de Prueba",
            categoria="Testing"
        )
        if test_forum_result.get('success'):
            created_forum_id = test_forum_result.get('forum', {}).get('id_foro')
            print(f"   ✅ Foro de prueba creado (ID: {created_forum_id})")
    
    if created_forum_id:
        # Crear post de ejemplo
        print("   📋 Creando post de ejemplo...")
        create_post_result = client.post_create_post(
            str(created_forum_id),
            "Este es un post de demostración del sistema SOA. ¡Bienvenidos al foro!"
        )
        if create_post_result.get('success'):
            post = create_post_result.get('post', {})
            print(f"   ✅ Post creado exitosamente")
            print(f"     📝 Contenido: {post.get('contenido')[:50]}...")
            created_post_id = post.get('id_post')
        else:
            print(f"   ❌ Error creando post: {create_post_result.get('message')}")
            created_post_id = None
        
        # Crear otro post
        print("   📋 Creando segundo post...")
        create_post2_result = client.post_create_post(
            str(created_forum_id),
            "Este es otro post para demostrar múltiples mensajes en el foro."
        )
        if create_post2_result.get('success'):
            print(f"   ✅ Segundo post creado exitosamente")
        else:
            print(f"   ❌ Error creando segundo post: {create_post2_result.get('message')}")
        
        # Listar posts del foro
        print("   📋 Listando posts del foro...")
        list_posts_result = client.post_list_posts(str(created_forum_id))
        if list_posts_result.get('success'):
            posts = list_posts_result.get('posts', [])
            foro_info = list_posts_result.get('foro', {})
            print(f"   ✅ Total de posts en '{foro_info.get('titulo')}': {len(posts)}")
            for post in posts[-2:]:  # Mostrar solo los últimos 2
                print(f"     💬 {post.get('contenido')[:40]}... por {post.get('autor_email')}")
        else:
            print(f"   ❌ Error listando posts: {list_posts_result.get('message')}")
        
        # Obtener post específico
        if created_post_id:
            print(f"   📋 Obteniendo post específico (ID: {created_post_id})...")
            get_post_result = client.post_get_post(str(created_post_id))
            if get_post_result.get('success'):
                post = get_post_result.get('post', {})
                print(f"   ✅ Post obtenido: {post.get('contenido')[:40]}...")
                print(f"     👤 Autor: {post.get('autor_email')}")
                print(f"     🗣️ Foro: {post.get('foro_titulo')}")
            else:
                print(f"   ❌ Error obteniendo post: {get_post_result.get('message')}")
        
        # Listar mis posts
        print("   📋 Listando mis posts...")
        my_posts_result = client.post_list_my_posts()
        if my_posts_result.get('success'):
            my_posts = my_posts_result.get('posts', [])
            print(f"   ✅ Mis posts: {len(my_posts)}")
            for post in my_posts[-2:]:  # Mostrar solo los últimos 2
                print(f"     💬 {post.get('contenido')[:40]}... en '{post.get('foro_titulo')}'")
        else:
            print(f"   ❌ Error listando mis posts: {my_posts_result.get('message')}")
        
        # Actualizar post
        if created_post_id:
            print(f"   📋 Actualizando post (ID: {created_post_id})...")
            update_post_result = client.post_update_post(
                str(created_post_id),
                "Este post ha sido actualizado para demostrar la funcionalidad de edición."
            )
            if update_post_result.get('success'):
                print(f"   ✅ Post actualizado exitosamente")
            else:
                print(f"   ❌ Error actualizando post: {update_post_result.get('message')}")
        
        # Crear usuario de prueba para demostrar permisos de posts
        test_email_post = f"post_test_{int(time.time())}@demo.com"
        print(f"   📋 Creando usuario de prueba para posts: {test_email_post}...")
        register_post_result = client.auth_register(test_email_post, "demo123", "estudiante")
        
        if register_post_result.get('success'):
            print(f"   ✅ Usuario de prueba creado para posts")
            
            # Loguearse como el usuario de prueba
            print("   📋 Cambiando a sesión del usuario de prueba...")
            client.auth_login(test_email_post, "demo123")
            
            # Crear post como estudiante
            print("   📋 Creando post como estudiante...")
            student_post_result = client.post_create_post(
                str(created_forum_id),
                "Este es un post creado por un estudiante."
            )
            if student_post_result.get('success'):
                student_post = student_post_result.get('post', {})
                student_post_id = student_post.get('id_post')
                print(f"   ✅ Post de estudiante creado (ID: {student_post_id})")
                
                # Intentar editar post de admin (debe fallar)
                if created_post_id:
                    print("   📋 Intentando editar post de admin como estudiante (debe fallar)...")
                    edit_admin_post_result = client.post_update_post(
                        str(created_post_id),
                        "Intento de edición no autorizada"
                    )
                    if not edit_admin_post_result.get('success'):
                        print(f"   ✅ Protección funcionando: {edit_admin_post_result.get('message')}")
                    else:
                        print(f"   ❌ Error en protección: estudiante pudo editar post de admin")
                
                # Editar su propio post
                print("   📋 Editando propio post como estudiante...")
                edit_own_post_result = client.post_update_post(
                    str(student_post_id),
                    "Este post ha sido editado por su autor (estudiante)."
                )
                if edit_own_post_result.get('success'):
                    print(f"   ✅ Post propio editado exitosamente")
                else:
                    print(f"   ❌ Error editando post propio: {edit_own_post_result.get('message')}")
                
                # Eliminar su propio post
                print("   📋 Eliminando propio post como estudiante...")
                delete_own_post_result = client.post_delete_post(str(student_post_id))
                if delete_own_post_result.get('success'):
                    print(f"   ✅ Post propio eliminado exitosamente")
                else:
                    print(f"   ❌ Error eliminando post propio: {delete_own_post_result.get('message')}")
            else:
                print(f"   ❌ Error creando post de estudiante: {student_post_result.get('message')}")
        
        # Volver a loguearse como admin
        print("   📋 Volviendo a sesión de admin...")
        client.auth_login("admin@institucional.edu.co", "admin123")
        
        # Demostrar método admin_delete_post
        if created_post_id:
            print("   📋 Eliminando post como moderador...")
            admin_delete_post_result = client.post_admin_delete_post(str(created_post_id))
            if admin_delete_post_result.get('success'):
                print(f"   ✅ Post eliminado por moderador exitosamente")
            else:
                print(f"   ❌ Error eliminando post como moderador: {admin_delete_post_result.get('message')}")
    else:
        print("   ❌ No hay foros disponibles para probar posts")
    
    # Demostrar método admin_delete_forum
    if created_forum_id:
        print("   📋 Eliminando foro como moderador...")
        admin_delete_result = client.forum_admin_delete_forum(str(created_forum_id))
        if admin_delete_result.get('success'):
            print(f"   ✅ Foro eliminado por moderador exitosamente")
        else:
            print(f"   ❌ Error eliminando foro como moderador: {admin_delete_result.get('message')}")
    
    # Demostrar logout final
    print("   📋 Cerrando sesión final...")
    client.logout()

def main():
    import sys
    
    client = SOAClient()
    
    if len(sys.argv) > 1 and sys.argv[1] == 'demo':
        run_demo()
    else:
        client.interactive_mode()

if __name__ == "__main__":
    main()
