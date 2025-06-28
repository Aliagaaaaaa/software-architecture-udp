#!/usr/bin/env python3
"""
Servicio de Gestión de Notificaciones - SOA
Permite gestionar notificaciones para usuarios del sistema
"""

import logging
from typing import Dict, Any, List
import json
import jwt
from datetime import datetime
from database_client import DatabaseClient
from soa_service_base import SOAServiceBase

class NotificationService(SOAServiceBase):
    def __init__(self, host: str = 'localhost', port: int = 8010):
        super().__init__(
            service_name="NOTIF",
            description="Servicio de gestión de notificaciones",
            host=host,
            port=port
        )
        
        # Cliente de base de datos remota
        self.db_client = DatabaseClient()
        
        # Secreto JWT (debe coincidir con auth_service)
        self.jwt_secret = "your-secret-key-here"
        
        # Configurar logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(f'NotificationService-{port}')
        
        # Inicializar base de datos
        self._init_database()
        
        self.logger.info("🔔 Servicio de Notificaciones inicializado")

    def _process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Override para manejar correctamente parámetros con comillas"""
        method_name = request.get('method')
        params = request.get('params', '')
        
        if not method_name:
            return {
                "status": "error",
                "message": "Missing method name"
            }
        
        if method_name not in self.methods:
            return {
                "status": "error",
                "message": f"Method '{method_name}' not found. Available methods: {list(self.methods.keys())}"
            }
        
        try:
            # Para el servicio de notificaciones, pasar los parámetros como string
            # para que cada método haga su propio parsing
            result = self.methods[method_name](params)
            
            return {
                "status": "success",
                "result": result
            }
            
        except Exception as e:
            self.logger.error(f"Error ejecutando método '{method_name}': {e}")
            return {
                "status": "error",
                "message": f"Error executing method '{method_name}': {str(e)}"
            }

    def _init_database(self):
        """Inicializa las tablas necesarias en la base de datos"""
        try:
            # Crear tabla NOTIFICACION
            create_notification_sql = """
            CREATE TABLE IF NOT EXISTS NOTIFICACION (
                id_notificacion INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                titulo VARCHAR(100) NOT NULL,
                mensaje TEXT NOT NULL,
                tipo VARCHAR(50) NOT NULL,
                referencia_id INTEGER,
                leido BOOLEAN DEFAULT FALSE,
                fecha TIMESTAMP NOT NULL,
                FOREIGN KEY (usuario_id) REFERENCES USUARIO (id_usuario)
            )
            """
            
            result = self.db_client.execute_query(create_notification_sql)
            if result.get('success'):
                self.logger.info("✅ Tabla NOTIFICACION creada/verificada correctamente")
            else:
                self.logger.error(f"❌ Error creando tabla NOTIFICACION: {result.get('error')}")
                
        except Exception as e:
            self.logger.error(f"❌ Error inicializando base de datos: {e}")

    def _verify_token(self, token: str) -> Dict[str, Any]:
        """Verifica y decodifica un token JWT"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            return {"success": True, "payload": payload}
        except jwt.ExpiredSignatureError:
            return {"success": False, "message": "Token expirado"}
        except jwt.InvalidTokenError:
            return {"success": False, "message": "Token inválido"}
        except Exception as e:
            return {"success": False, "message": f"Error verificando token: {str(e)}"}

    def _get_user_by_id(self, user_id: int) -> Dict[str, Any]:
        """Obtiene información de un usuario por ID"""
        try:
            query = "SELECT id_usuario, email, rol FROM USUARIO WHERE id_usuario = ?"
            result = self.db_client.execute_query(query, [user_id])
            
            if result.get('success') and result.get('results'):
                user_data = result['results'][0]
                
                # La base de datos devuelve dictionaries, no tuples
                if isinstance(user_data, dict):
                    return {
                        "success": True,
                        "user": {
                            "id_usuario": user_data.get('id_usuario'),
                            "email": user_data.get('email'),
                            "rol": user_data.get('rol')
                        }
                    }
                else:
                    return {
                        "success": True,
                        "user": {
                            "id_usuario": user_data[0],
                            "email": user_data[1],
                            "rol": user_data[2]
                        }
                    }
            else:
                return {"success": False, "message": "Usuario no encontrado"}
                
        except Exception as e:
            return {"success": False, "message": f"Error obteniendo usuario: {str(e)}"}

    def _parse_quoted_params(self, params_str: str) -> List[str]:
        """Parsea parámetros respetando comillas simples"""
        import shlex
        try:
            return shlex.split(params_str)
        except ValueError:
            return params_str.split()

    def _extract_db_fields(self, row_data, field_names):
        """Helper para extraer campos de una fila de base de datos, manejando tanto dict como tuple"""
        if isinstance(row_data, dict):
            return [row_data.get(field) for field in field_names]
        else:
            return list(row_data[:len(field_names)])

    def service_list_notifications(self, params_str: str) -> str:
        """Lista las notificaciones del usuario autenticado"""
        try:
            params = self._parse_quoted_params(params_str)
            if len(params) < 1:
                return json.dumps({"success": False, "message": "Parámetros requeridos: token [limit]"})
            
            token = params[0]
            limit = int(params[1]) if len(params) > 1 else 50  # Límite por defecto
            
            # Verificar token
            token_result = self._verify_token(token)
            if not token_result.get('success'):
                return json.dumps({"success": False, "message": token_result.get('message')})
            
            user_payload = token_result['payload']
            usuario_id = user_payload.get('id_usuario')
            
            # Obtener notificaciones del usuario ordenadas por fecha (más recientes primero)
            query = """
            SELECT id_notificacion, usuario_id, titulo, mensaje, tipo, referencia_id, leido, fecha
            FROM NOTIFICACION
            WHERE usuario_id = ?
            ORDER BY fecha DESC
            LIMIT ?
            """
            
            result = self.db_client.execute_query(query, [usuario_id, limit])
            
            if result.get('success'):
                notifications = []
                for notification_data in result.get('results', []):
                    # Extraer campos usando el helper
                    fields = self._extract_db_fields(notification_data, [
                        'id_notificacion', 'usuario_id', 'titulo', 'mensaje', 'tipo', 'referencia_id', 'leido', 'fecha'
                    ])
                    
                    notification = {
                        "id_notificacion": fields[0],
                        "usuario_id": fields[1],
                        "titulo": fields[2],
                        "mensaje": fields[3],
                        "tipo": fields[4],
                        "referencia_id": fields[5],
                        "leido": bool(fields[6]),
                        "fecha": fields[7]
                    }
                    notifications.append(notification)
                
                return json.dumps({
                    "success": True,
                    "message": f"Tienes {len(notifications)} notificaciones",
                    "notifications": notifications
                })
            else:
                return json.dumps({"success": False, "message": f"Error obteniendo notificaciones: {result.get('error')}"})
                
        except Exception as e:
            self.logger.error(f"Error en list_notifications: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_get_unread_count(self, params_str: str) -> str:
        """Obtiene el número de notificaciones no leídas del usuario"""
        try:
            params = self._parse_quoted_params(params_str)
            if len(params) < 1:
                return json.dumps({"success": False, "message": "Parámetros requeridos: token"})
            
            token = params[0]
            
            # Verificar token
            token_result = self._verify_token(token)
            if not token_result.get('success'):
                return json.dumps({"success": False, "message": token_result.get('message')})
            
            user_payload = token_result['payload']
            usuario_id = user_payload.get('id_usuario')
            
            # Contar notificaciones no leídas
            query = "SELECT COUNT(*) as count FROM NOTIFICACION WHERE usuario_id = ? AND leido = FALSE"
            result = self.db_client.execute_query(query, [usuario_id])
            
            if result.get('success') and result.get('results'):
                count_data = result['results'][0]
                count = self._extract_db_fields(count_data, ['count'])[0]
                
                return json.dumps({
                    "success": True,
                    "message": f"Tienes {count} notificaciones no leídas",
                    "unread_count": count
                })
            else:
                return json.dumps({"success": False, "message": f"Error obteniendo contador: {result.get('error')}"})
                
        except Exception as e:
            self.logger.error(f"Error en get_unread_count: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_mark_as_read(self, params_str: str) -> str:
        """Marca una notificación específica como leída"""
        try:
            params = self._parse_quoted_params(params_str)
            if len(params) < 2:
                return json.dumps({"success": False, "message": "Parámetros requeridos: token id_notificacion"})
            
            token = params[0]
            id_notificacion = params[1]
            
            # Verificar token
            token_result = self._verify_token(token)
            if not token_result.get('success'):
                return json.dumps({"success": False, "message": token_result.get('message')})
            
            user_payload = token_result['payload']
            usuario_id = user_payload.get('id_usuario')
            
            # Verificar que la notificación pertenece al usuario
            check_query = "SELECT usuario_id FROM NOTIFICACION WHERE id_notificacion = ?"
            check_result = self.db_client.execute_query(check_query, [id_notificacion])
            
            if not check_result.get('success') or not check_result.get('results'):
                return json.dumps({"success": False, "message": "Notificación no encontrada"})
            
            notification_user_id = self._extract_db_fields(check_result['results'][0], ['usuario_id'])[0]
            
            if notification_user_id != usuario_id:
                return json.dumps({"success": False, "message": "No tienes permisos para modificar esta notificación"})
            
            # Marcar como leída
            update_query = "UPDATE NOTIFICACION SET leido = TRUE WHERE id_notificacion = ?"
            result = self.db_client.execute_query(update_query, [id_notificacion])
            
            if result.get('success'):
                self.logger.info(f"🔔 Notificación {id_notificacion} marcada como leída por {user_payload.get('email')}")
                return json.dumps({
                    "success": True,
                    "message": "Notificación marcada como leída"
                })
            else:
                return json.dumps({"success": False, "message": f"Error marcando como leída: {result.get('error')}"})
                
        except Exception as e:
            self.logger.error(f"Error en mark_as_read: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_mark_all_as_read(self, params_str: str) -> str:
        """Marca todas las notificaciones del usuario como leídas"""
        try:
            params = self._parse_quoted_params(params_str)
            if len(params) < 1:
                return json.dumps({"success": False, "message": "Parámetros requeridos: token"})
            
            token = params[0]
            
            # Verificar token
            token_result = self._verify_token(token)
            if not token_result.get('success'):
                return json.dumps({"success": False, "message": token_result.get('message')})
            
            user_payload = token_result['payload']
            usuario_id = user_payload.get('id_usuario')
            
            # Marcar todas como leídas
            update_query = "UPDATE NOTIFICACION SET leido = TRUE WHERE usuario_id = ? AND leido = FALSE"
            result = self.db_client.execute_query(update_query, [usuario_id])
            
            if result.get('success'):
                self.logger.info(f"🔔 Todas las notificaciones marcadas como leídas por {user_payload.get('email')}")
                return json.dumps({
                    "success": True,
                    "message": "Todas las notificaciones marcadas como leídas"
                })
            else:
                return json.dumps({"success": False, "message": f"Error marcando todas como leídas: {result.get('error')}"})
                
        except Exception as e:
            self.logger.error(f"Error en mark_all_as_read: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_get_notification(self, params_str: str) -> str:
        """Obtiene una notificación específica por ID"""
        try:
            params = self._parse_quoted_params(params_str)
            if len(params) < 2:
                return json.dumps({"success": False, "message": "Parámetros requeridos: token id_notificacion"})
            
            token = params[0]
            id_notificacion = params[1]
            
            # Verificar token
            token_result = self._verify_token(token)
            if not token_result.get('success'):
                return json.dumps({"success": False, "message": token_result.get('message')})
            
            user_payload = token_result['payload']
            usuario_id = user_payload.get('id_usuario')
            
            # Obtener notificación específica
            query = """
            SELECT id_notificacion, usuario_id, titulo, mensaje, tipo, referencia_id, leido, fecha
            FROM NOTIFICACION
            WHERE id_notificacion = ? AND usuario_id = ?
            """
            
            result = self.db_client.execute_query(query, [id_notificacion, usuario_id])
            
            if result.get('success') and result.get('results'):
                notification_data = result['results'][0]
                
                # Extraer campos usando el helper
                fields = self._extract_db_fields(notification_data, [
                    'id_notificacion', 'usuario_id', 'titulo', 'mensaje', 'tipo', 'referencia_id', 'leido', 'fecha'
                ])
                
                notification = {
                    "id_notificacion": fields[0],
                    "usuario_id": fields[1],
                    "titulo": fields[2],
                    "mensaje": fields[3],
                    "tipo": fields[4],
                    "referencia_id": fields[5],
                    "leido": bool(fields[6]),
                    "fecha": fields[7]
                }
                
                return json.dumps({
                    "success": True,
                    "message": "Notificación encontrada",
                    "notification": notification
                })
            else:
                return json.dumps({"success": False, "message": "Notificación no encontrada"})
                
        except Exception as e:
            self.logger.error(f"Error en get_notification: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_delete_notification(self, params_str: str) -> str:
        """Elimina una notificación específica"""
        try:
            params = self._parse_quoted_params(params_str)
            if len(params) < 2:
                return json.dumps({"success": False, "message": "Parámetros requeridos: token id_notificacion"})
            
            token = params[0]
            id_notificacion = params[1]
            
            # Verificar token
            token_result = self._verify_token(token)
            if not token_result.get('success'):
                return json.dumps({"success": False, "message": token_result.get('message')})
            
            user_payload = token_result['payload']
            usuario_id = user_payload.get('id_usuario')
            
            # Verificar que la notificación pertenece al usuario
            check_query = "SELECT usuario_id FROM NOTIFICACION WHERE id_notificacion = ?"
            check_result = self.db_client.execute_query(check_query, [id_notificacion])
            
            if not check_result.get('success') or not check_result.get('results'):
                return json.dumps({"success": False, "message": "Notificación no encontrada"})
            
            notification_user_id = self._extract_db_fields(check_result['results'][0], ['usuario_id'])[0]
            
            if notification_user_id != usuario_id:
                return json.dumps({"success": False, "message": "No tienes permisos para eliminar esta notificación"})
            
            # Eliminar notificación
            delete_query = "DELETE FROM NOTIFICACION WHERE id_notificacion = ?"
            result = self.db_client.execute_query(delete_query, [id_notificacion])
            
            if result.get('success'):
                self.logger.info(f"🗑️ Notificación {id_notificacion} eliminada por {user_payload.get('email')}")
                return json.dumps({
                    "success": True,
                    "message": "Notificación eliminada exitosamente"
                })
            else:
                return json.dumps({"success": False, "message": f"Error eliminando notificación: {result.get('error')}"})
                
        except Exception as e:
            self.logger.error(f"Error en delete_notification: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_clear_all_notifications(self, params_str: str) -> str:
        """Elimina todas las notificaciones del usuario"""
        try:
            params = self._parse_quoted_params(params_str)
            if len(params) < 1:
                return json.dumps({"success": False, "message": "Parámetros requeridos: token"})
            
            token = params[0]
            
            # Verificar token
            token_result = self._verify_token(token)
            if not token_result.get('success'):
                return json.dumps({"success": False, "message": token_result.get('message')})
            
            user_payload = token_result['payload']
            usuario_id = user_payload.get('id_usuario')
            
            # Eliminar todas las notificaciones del usuario
            delete_query = "DELETE FROM NOTIFICACION WHERE usuario_id = ?"
            result = self.db_client.execute_query(delete_query, [usuario_id])
            
            if result.get('success'):
                self.logger.info(f"🗑️ Todas las notificaciones eliminadas por {user_payload.get('email')}")
                return json.dumps({
                    "success": True,
                    "message": "Todas las notificaciones eliminadas exitosamente"
                })
            else:
                return json.dumps({"success": False, "message": f"Error eliminando notificaciones: {result.get('error')}"})
                
        except Exception as e:
            self.logger.error(f"Error en clear_all_notifications: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_admin_list_all_notifications(self, params_str: str) -> str:
        """Lista todas las notificaciones del sistema (solo moderadores)"""
        try:
            params = self._parse_quoted_params(params_str)
            if len(params) < 1:
                return json.dumps({"success": False, "message": "Parámetros requeridos: token [limit]"})
            
            token = params[0]
            limit = int(params[1]) if len(params) > 1 else 100  # Límite por defecto
            
            # Verificar token
            token_result = self._verify_token(token)
            if not token_result.get('success'):
                return json.dumps({"success": False, "message": token_result.get('message')})
            
            user_payload = token_result['payload']
            user_rol = user_payload.get('rol')
            
            # Solo moderadores pueden ver todas las notificaciones
            if user_rol != 'moderador':
                return json.dumps({"success": False, "message": "Solo los moderadores pueden ver todas las notificaciones"})
            
            # Obtener todas las notificaciones con información del usuario
            query = """
            SELECT n.id_notificacion, n.usuario_id, n.titulo, n.mensaje, n.tipo, 
                   n.referencia_id, n.leido, n.fecha, u.email as usuario_email
            FROM NOTIFICACION n
            LEFT JOIN USUARIO u ON n.usuario_id = u.id_usuario
            ORDER BY n.fecha DESC
            LIMIT ?
            """
            
            result = self.db_client.execute_query(query, [limit])
            
            if result.get('success'):
                notifications = []
                for notification_data in result.get('results', []):
                    # Extraer campos usando el helper
                    fields = self._extract_db_fields(notification_data, [
                        'id_notificacion', 'usuario_id', 'titulo', 'mensaje', 'tipo',
                        'referencia_id', 'leido', 'fecha', 'usuario_email'
                    ])
                    
                    notification = {
                        "id_notificacion": fields[0],
                        "usuario_id": fields[1],
                        "titulo": fields[2],
                        "mensaje": fields[3],
                        "tipo": fields[4],
                        "referencia_id": fields[5],
                        "leido": bool(fields[6]),
                        "fecha": fields[7],
                        "usuario_email": fields[8] or 'Desconocido'
                    }
                    notifications.append(notification)
                
                return json.dumps({
                    "success": True,
                    "message": f"Se encontraron {len(notifications)} notificaciones en el sistema",
                    "notifications": notifications
                })
            else:
                return json.dumps({"success": False, "message": f"Error obteniendo notificaciones: {result.get('error')}"})
                
        except Exception as e:
            self.logger.error(f"Error en admin_list_all_notifications: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_info(self, *args) -> str:
        """Método abstracto requerido por SOAServiceBase"""
        info_data = {
            "service": "notif",
            "description": "Servicio de gestión de notificaciones",
            "version": "1.0.0",
            "database": "Cloudflare D1 (remota)",
            "table": "NOTIFICACION",
            "authentication": "JWT Token required",
            "port": self.port,
            "host": self.host,
            "methods": list(self.methods.keys()) if hasattr(self, 'methods') else [],
            "dependencies": ["auth"],
            "permissions": {
                "estudiante": ["list_notifications", "get_unread_count", "mark_as_read", "mark_all_as_read", "get_notification", "delete_notification", "clear_all_notifications"],
                "moderador": ["all student permissions", "admin_list_all_notifications"]
            },
            "notification_types": ["mensaje", "reporte", "foro", "post", "comentario", "evento", "sistema"]
        }
        return json.dumps(info_data)

def main():
    try:
        service = NotificationService(host='localhost', port=8010)
        
        print(f"🔔 Iniciando servicio de notificaciones...")
        service.start_service()
        
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo servicio de notificaciones...")

if __name__ == "__main__":
    main() 