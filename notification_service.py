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
        
        # Los métodos se registran automáticamente por la clase base
        # Todos los métodos que empiecen con 'service_' se registran automáticamente
        
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
            # Crear tabla NOTIFICACION (mejorada)
            create_notification_sql = """
            CREATE TABLE IF NOT EXISTS NOTIFICACION (
                id_notificacion INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                titulo VARCHAR(100) NOT NULL,
                mensaje TEXT NOT NULL,
                tipo VARCHAR(50) NOT NULL,
                referencia_id INTEGER,
                referencia_tipo VARCHAR(20),
                leido BOOLEAN DEFAULT FALSE,
                fecha TIMESTAMP NOT NULL,
                creador_id INTEGER,
                FOREIGN KEY (usuario_id) REFERENCES USUARIO (id_usuario),
                FOREIGN KEY (creador_id) REFERENCES USUARIO (id_usuario)
            )
            """
            
            # Crear tabla SUSCRIPCION_FORO
            create_forum_subscription_sql = """
            CREATE TABLE IF NOT EXISTS SUSCRIPCION_FORO (
                id_suscripcion INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                foro_id INTEGER NOT NULL,
                fecha_suscripcion TIMESTAMP NOT NULL,
                activa BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (usuario_id) REFERENCES USUARIO (id_usuario),
                FOREIGN KEY (foro_id) REFERENCES FORO (id_foro),
                UNIQUE(usuario_id, foro_id)
            )
            """
            
            # Crear tabla SUSCRIPCION_POST
            create_post_subscription_sql = """
            CREATE TABLE IF NOT EXISTS SUSCRIPCION_POST (
                id_suscripcion INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                post_id INTEGER NOT NULL,
                fecha_suscripcion TIMESTAMP NOT NULL,
                activa BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (usuario_id) REFERENCES USUARIO (id_usuario),
                FOREIGN KEY (post_id) REFERENCES POST (id_post),
                UNIQUE(usuario_id, post_id)
            )
            """
            
            # Ejecutar creación de tablas
            tables = [
                ("NOTIFICACION", create_notification_sql),
                ("SUSCRIPCION_FORO", create_forum_subscription_sql),
                ("SUSCRIPCION_POST", create_post_subscription_sql)
            ]
            
            for table_name, sql in tables:
                result = self.db_client.execute_query(sql)
                if result.get('success'):
                    self.logger.info(f"✅ Tabla {table_name} creada/verificada correctamente")
                else:
                    self.logger.error(f"❌ Error creando tabla {table_name}: {result.get('error')}")
                
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
        """Extrae campos de fila de base de datos"""
        if isinstance(row_data, dict):
            return {field: row_data.get(field) for field in field_names}
        else:
            return dict(zip(field_names, row_data))

    def service_list_notifications(self, params_str: str) -> str:
        """Lista las notificaciones del usuario autenticado"""
        try:
            params = self._parse_quoted_params(params_str)
            if len(params) < 1:
                return json.dumps({"success": False, "message": "Parámetros requeridos: token [limit]"})
            
            token = params[0]
            try:
                limit = int(params[1]) if len(params) > 1 else 50  # Límite por defecto
            except ValueError:
                limit = 50
            
            # Verificar token
            token_result = self._verify_token(token)
            if not token_result.get('success'):
                return json.dumps({"success": False, "message": token_result.get('message')})
            
            user_payload = token_result['payload']
            usuario_id = user_payload.get('id_usuario')
            
            # Obtener notificaciones del usuario ordenadas por fecha (más recientes primero)
            query = """
            SELECT id_notificacion, usuario_id, titulo, mensaje, tipo, referencia_id, referencia_tipo, leido, fecha, creador_id
            FROM NOTIFICACION
            WHERE usuario_id = ?
            ORDER BY fecha DESC
            LIMIT ?
            """
            
            result = self.db_client.execute_query(query, [usuario_id, limit])
            
            if result.get('success'):
                notifications = []
                for notification_data in result.get('results', []):
                    # Manejar tanto diccionarios como tuplas
                    if isinstance(notification_data, dict):
                        notification = {
                            "id_notificacion": notification_data.get('id_notificacion'),
                            "usuario_id": notification_data.get('usuario_id'),
                            "titulo": notification_data.get('titulo'),
                            "mensaje": notification_data.get('mensaje'),
                            "tipo": notification_data.get('tipo'),
                            "referencia_id": notification_data.get('referencia_id'),
                            "referencia_tipo": notification_data.get('referencia_tipo'),
                            "leido": bool(notification_data.get('leido')),
                            "fecha": notification_data.get('fecha'),
                            "creador_id": notification_data.get('creador_id')
                        }
                    else:
                        # Manejo de tuplas
                        notification = {
                            "id_notificacion": notification_data[0] if len(notification_data) > 0 else None,
                            "usuario_id": notification_data[1] if len(notification_data) > 1 else None,
                            "titulo": notification_data[2] if len(notification_data) > 2 else "",
                            "mensaje": notification_data[3] if len(notification_data) > 3 else "",
                            "tipo": notification_data[4] if len(notification_data) > 4 else "",
                            "referencia_id": notification_data[5] if len(notification_data) > 5 else None,
                            "referencia_tipo": notification_data[6] if len(notification_data) > 6 else "",
                            "leido": bool(notification_data[7]) if len(notification_data) > 7 else False,
                            "fecha": notification_data[8] if len(notification_data) > 8 else "",
                            "creador_id": notification_data[9] if len(notification_data) > 9 else None
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
                
                # Manejar tanto diccionarios como tuplas
                if isinstance(count_data, dict):
                    count = count_data.get('count', 0)
                else:
                    count = count_data[0] if len(count_data) > 0 else 0
                
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
            
            user_data = check_result['results'][0]
            if isinstance(user_data, dict):
                notification_user_id = user_data.get('usuario_id')
            else:
                notification_user_id = user_data[0] if len(user_data) > 0 else None
            
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
            SELECT id_notificacion, usuario_id, titulo, mensaje, tipo, referencia_id, referencia_tipo, leido, fecha, creador_id
            FROM NOTIFICACION
            WHERE id_notificacion = ? AND usuario_id = ?
            """
            
            result = self.db_client.execute_query(query, [id_notificacion, usuario_id])
            
            if result.get('success') and result.get('results'):
                notification_data = result['results'][0]
                
                # Manejar tanto diccionarios como tuplas
                if isinstance(notification_data, dict):
                    notification = {
                        "id_notificacion": notification_data.get('id_notificacion'),
                        "usuario_id": notification_data.get('usuario_id'),
                        "titulo": notification_data.get('titulo'),
                        "mensaje": notification_data.get('mensaje'),
                        "tipo": notification_data.get('tipo'),
                        "referencia_id": notification_data.get('referencia_id'),
                        "referencia_tipo": notification_data.get('referencia_tipo'),
                        "leido": bool(notification_data.get('leido')),
                        "fecha": notification_data.get('fecha'),
                        "creador_id": notification_data.get('creador_id')
                    }
                else:
                    # Manejo de tuplas
                    notification = {
                        "id_notificacion": notification_data[0] if len(notification_data) > 0 else None,
                        "usuario_id": notification_data[1] if len(notification_data) > 1 else None,
                        "titulo": notification_data[2] if len(notification_data) > 2 else "",
                        "mensaje": notification_data[3] if len(notification_data) > 3 else "",
                        "tipo": notification_data[4] if len(notification_data) > 4 else "",
                        "referencia_id": notification_data[5] if len(notification_data) > 5 else None,
                        "referencia_tipo": notification_data[6] if len(notification_data) > 6 else "",
                        "leido": bool(notification_data[7]) if len(notification_data) > 7 else False,
                        "fecha": notification_data[8] if len(notification_data) > 8 else "",
                        "creador_id": notification_data[9] if len(notification_data) > 9 else None
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
            
            user_data = check_result['results'][0]
            if isinstance(user_data, dict):
                notification_user_id = user_data.get('usuario_id')
            else:
                notification_user_id = user_data[0] if len(user_data) > 0 else None
            
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
            try:
                limit = int(params[1]) if len(params) > 1 else 100  # Límite por defecto
            except ValueError:
                limit = 100
            
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
                   n.referencia_id, n.referencia_tipo, n.leido, n.fecha, n.creador_id, u.email as usuario_email
            FROM NOTIFICACION n
            LEFT JOIN USUARIO u ON n.usuario_id = u.id_usuario
            ORDER BY n.fecha DESC
            LIMIT ?
            """
            
            result = self.db_client.execute_query(query, [limit])
            
            if result.get('success'):
                notifications = []
                for notification_data in result.get('results', []):
                    # Manejar tanto diccionarios como tuplas
                    if isinstance(notification_data, dict):
                        notification = {
                            "id_notificacion": notification_data.get('id_notificacion'),
                            "usuario_id": notification_data.get('usuario_id'),
                            "titulo": notification_data.get('titulo'),
                            "mensaje": notification_data.get('mensaje'),
                            "tipo": notification_data.get('tipo'),
                            "referencia_id": notification_data.get('referencia_id'),
                            "referencia_tipo": notification_data.get('referencia_tipo'),
                            "leido": bool(notification_data.get('leido')),
                            "fecha": notification_data.get('fecha'),
                            "creador_id": notification_data.get('creador_id'),
                            "usuario_email": notification_data.get('usuario_email') or 'Desconocido'
                        }
                    else:
                        # Manejo de tuplas
                        notification = {
                            "id_notificacion": notification_data[0] if len(notification_data) > 0 else None,
                            "usuario_id": notification_data[1] if len(notification_data) > 1 else None,
                            "titulo": notification_data[2] if len(notification_data) > 2 else "",
                            "mensaje": notification_data[3] if len(notification_data) > 3 else "",
                            "tipo": notification_data[4] if len(notification_data) > 4 else "",
                            "referencia_id": notification_data[5] if len(notification_data) > 5 else None,
                            "referencia_tipo": notification_data[6] if len(notification_data) > 6 else "",
                            "leido": bool(notification_data[7]) if len(notification_data) > 7 else False,
                            "fecha": notification_data[8] if len(notification_data) > 8 else "",
                            "creador_id": notification_data[9] if len(notification_data) > 9 else None,
                            "usuario_email": notification_data[10] if len(notification_data) > 10 else 'Desconocido'
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

    # === MÉTODOS DE SUSCRIPCIONES ===
    
    def service_subscribe_forum(self, params_str: str) -> str:
        """Suscribe al usuario a un foro para recibir notificaciones"""
        try:
            params = self._parse_quoted_params(params_str)
            if len(params) < 2:
                return json.dumps({"success": False, "message": "Parámetros requeridos: token foro_id"})
            
            token = params[0]
            try:
                foro_id = int(params[1])
            except ValueError:
                return json.dumps({"success": False, "message": "foro_id debe ser un número válido"})
            
            # Verificar token
            token_result = self._verify_token(token)
            if not token_result.get('success'):
                return json.dumps({"success": False, "message": token_result.get('message')})
            
            user_payload = token_result['payload']
            usuario_id = user_payload.get('id_usuario')
            
            # Verificar que el foro existe
            check_forum_query = "SELECT titulo FROM FORO WHERE id_foro = ?"
            forum_result = self.db_client.execute_query(check_forum_query, [foro_id])
            
            if not forum_result.get('success') or not forum_result.get('results'):
                return json.dumps({"success": False, "message": "Foro no encontrado"})
            
            # Crear suscripción (el UNIQUE evita duplicados)
            from datetime import datetime
            now = datetime.now().isoformat()
            
            insert_query = """
            INSERT OR REPLACE INTO SUSCRIPCION_FORO (usuario_id, foro_id, fecha_suscripcion, activa)
            VALUES (?, ?, ?, TRUE)
            """
            
            result = self.db_client.execute_query(insert_query, [usuario_id, foro_id, now])
            
            if result.get('success'):
                # Obtener título del foro
                forum_data = forum_result['results'][0]
                if isinstance(forum_data, dict):
                    titulo_foro = forum_data.get('titulo', 'Foro')
                else:
                    titulo_foro = forum_data[0] if forum_data else 'Foro'
                
                self.logger.info(f"📧 Usuario {user_payload.get('email')} suscrito al foro {titulo_foro}")
                return json.dumps({
                    "success": True,
                    "message": f"Te has suscrito exitosamente al foro '{titulo_foro}'"
                })
            else:
                return json.dumps({"success": False, "message": f"Error creando suscripción: {result.get('error')}"})
                
        except Exception as e:
            self.logger.error(f"Error en subscribe_forum: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_unsubscribe_forum(self, params_str: str) -> str:
        """Desuscribe al usuario de un foro"""
        try:
            params = self._parse_quoted_params(params_str)
            if len(params) < 2:
                return json.dumps({"success": False, "message": "Parámetros requeridos: token foro_id"})
            
            token = params[0]
            try:
                foro_id = int(params[1])
            except ValueError:
                return json.dumps({"success": False, "message": "foro_id debe ser un número válido"})
            
            # Verificar token
            token_result = self._verify_token(token)
            if not token_result.get('success'):
                return json.dumps({"success": False, "message": token_result.get('message')})
            
            user_payload = token_result['payload']
            usuario_id = user_payload.get('id_usuario')
            
            # Eliminar suscripción
            delete_query = "DELETE FROM SUSCRIPCION_FORO WHERE usuario_id = ? AND foro_id = ?"
            result = self.db_client.execute_query(delete_query, [usuario_id, foro_id])
            
            if result.get('success'):
                self.logger.info(f"📧❌ Usuario {user_payload.get('email')} desuscrito del foro {foro_id}")
                return json.dumps({
                    "success": True,
                    "message": "Te has desuscrito exitosamente del foro"
                })
            else:
                return json.dumps({"success": False, "message": f"Error eliminando suscripción: {result.get('error')}"})
                
        except Exception as e:
            self.logger.error(f"Error en unsubscribe_forum: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_subscribe_post(self, params_str: str) -> str:
        """Suscribe al usuario a un post para recibir notificaciones"""
        try:
            params = self._parse_quoted_params(params_str)
            if len(params) < 2:
                return json.dumps({"success": False, "message": "Parámetros requeridos: token post_id"})
            
            token = params[0]
            try:
                post_id = int(params[1])
            except ValueError:
                return json.dumps({"success": False, "message": "post_id debe ser un número válido"})
            
            # Verificar token
            token_result = self._verify_token(token)
            if not token_result.get('success'):
                return json.dumps({"success": False, "message": token_result.get('message')})
            
            user_payload = token_result['payload']
            usuario_id = user_payload.get('id_usuario')
            
            # Verificar que el post existe
            check_post_query = "SELECT contenido FROM POST WHERE id_post = ?"
            post_result = self.db_client.execute_query(check_post_query, [post_id])
            
            if not post_result.get('success') or not post_result.get('results'):
                return json.dumps({"success": False, "message": "Post no encontrado"})
            
            # Crear suscripción
            from datetime import datetime
            now = datetime.now().isoformat()
            
            insert_query = """
            INSERT OR REPLACE INTO SUSCRIPCION_POST (usuario_id, post_id, fecha_suscripcion, activa)
            VALUES (?, ?, ?, TRUE)
            """
            
            result = self.db_client.execute_query(insert_query, [usuario_id, post_id, now])
            
            if result.get('success'):
                # Obtener contenido del post
                post_data = post_result['results'][0]
                if isinstance(post_data, dict):
                    contenido_post = post_data.get('contenido', 'Post')
                else:
                    contenido_post = post_data[0] if post_data else 'Post'
                
                # Crear título corto del post
                titulo_post = contenido_post[:50] + "..." if len(contenido_post) > 50 else contenido_post
                
                self.logger.info(f"📧 Usuario {user_payload.get('email')} suscrito al post {titulo_post}")
                return json.dumps({
                    "success": True,
                    "message": f"Te has suscrito exitosamente al post"
                })
            else:
                return json.dumps({"success": False, "message": f"Error creando suscripción: {result.get('error')}"})
                
        except Exception as e:
            self.logger.error(f"Error en subscribe_post: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_unsubscribe_post(self, params_str: str) -> str:
        """Desuscribe al usuario de un post"""
        try:
            params = self._parse_quoted_params(params_str)
            if len(params) < 2:
                return json.dumps({"success": False, "message": "Parámetros requeridos: token post_id"})
            
            token = params[0]
            try:
                post_id = int(params[1])
            except ValueError:
                return json.dumps({"success": False, "message": "post_id debe ser un número válido"})
            
            # Verificar token
            token_result = self._verify_token(token)
            if not token_result.get('success'):
                return json.dumps({"success": False, "message": token_result.get('message')})
            
            user_payload = token_result['payload']
            usuario_id = user_payload.get('id_usuario')
            
            # Eliminar suscripción
            delete_query = "DELETE FROM SUSCRIPCION_POST WHERE usuario_id = ? AND post_id = ?"
            result = self.db_client.execute_query(delete_query, [usuario_id, post_id])
            
            if result.get('success'):
                self.logger.info(f"📧❌ Usuario {user_payload.get('email')} desuscrito del post {post_id}")
                return json.dumps({
                    "success": True,
                    "message": "Te has desuscrito exitosamente del post"
                })
            else:
                return json.dumps({"success": False, "message": f"Error eliminando suscripción: {result.get('error')}"})
                
        except Exception as e:
            self.logger.error(f"Error en unsubscribe_post: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_list_forum_subscriptions(self, params_str: str) -> str:
        """Lista las suscripciones a foros del usuario"""
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
            
            # Obtener suscripciones con información del foro
            query = """
            SELECT sf.id_suscripcion, sf.foro_id, sf.fecha_suscripcion, 
                   f.titulo, f.categoria
            FROM SUSCRIPCION_FORO sf
            LEFT JOIN FORO f ON sf.foro_id = f.id_foro
            WHERE sf.usuario_id = ? AND sf.activa = TRUE
            ORDER BY sf.fecha_suscripcion DESC
            """
            
            result = self.db_client.execute_query(query, [usuario_id])
            
            if result.get('success'):
                subscriptions = []
                for sub_data in result.get('results', []):
                    if isinstance(sub_data, dict):
                        subscription = {
                            "id_suscripcion": sub_data.get('id_suscripcion'),
                            "foro_id": sub_data.get('foro_id'),
                            "fecha_suscripcion": sub_data.get('fecha_suscripcion'),
                            "titulo_foro": sub_data.get('titulo') or 'Foro eliminado',
                            "categoria": sub_data.get('categoria') or 'N/A'
                        }
                    else:
                        # Caso de tupla/lista
                        subscription = {
                            "id_suscripcion": sub_data[0] if len(sub_data) > 0 else None,
                            "foro_id": sub_data[1] if len(sub_data) > 1 else None,
                            "fecha_suscripcion": sub_data[2] if len(sub_data) > 2 else None,
                            "titulo_foro": sub_data[3] if len(sub_data) > 3 else 'Foro eliminado',
                            "categoria": sub_data[4] if len(sub_data) > 4 else 'N/A'
                        }
                    subscriptions.append(subscription)
                
                return json.dumps({
                    "success": True,
                    "message": f"Se encontraron {len(subscriptions)} suscripciones a foros",
                    "subscriptions": subscriptions
                })
            else:
                return json.dumps({"success": False, "message": f"Error obteniendo suscripciones: {result.get('error')}"})
                
        except Exception as e:
            self.logger.error(f"Error en list_forum_subscriptions: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_list_post_subscriptions(self, params_str: str) -> str:
        """Lista las suscripciones a posts del usuario"""
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
            
            # Obtener suscripciones con información del post
            query = """
            SELECT sp.id_suscripcion, sp.post_id, sp.fecha_suscripcion, 
                   p.contenido
            FROM SUSCRIPCION_POST sp
            LEFT JOIN POST p ON sp.post_id = p.id_post
            WHERE sp.usuario_id = ? AND sp.activa = TRUE
            ORDER BY sp.fecha_suscripcion DESC
            """
            
            result = self.db_client.execute_query(query, [usuario_id])
            
            if result.get('success'):
                subscriptions = []
                for sub_data in result.get('results', []):
                    if isinstance(sub_data, dict):
                        contenido = sub_data.get('contenido') or 'Post eliminado'
                        titulo_post = contenido[:50] + "..." if len(contenido) > 50 else contenido
                        
                        subscription = {
                            "id_suscripcion": sub_data.get('id_suscripcion'),
                            "post_id": sub_data.get('post_id'),
                            "fecha_suscripcion": sub_data.get('fecha_suscripcion'),
                            "titulo_post": titulo_post
                        }
                    else:
                        # Caso de tupla/lista
                        contenido = sub_data[3] if len(sub_data) > 3 and sub_data[3] else 'Post eliminado'
                        titulo_post = contenido[:50] + "..." if len(contenido) > 50 else contenido
                        
                        subscription = {
                            "id_suscripcion": sub_data[0] if len(sub_data) > 0 else None,
                            "post_id": sub_data[1] if len(sub_data) > 1 else None,
                            "fecha_suscripcion": sub_data[2] if len(sub_data) > 2 else None,
                            "titulo_post": titulo_post
                        }
                    subscriptions.append(subscription)
                
                return json.dumps({
                    "success": True,
                    "message": f"Se encontraron {len(subscriptions)} suscripciones a posts",
                    "subscriptions": subscriptions
                })
            else:
                return json.dumps({"success": False, "message": f"Error obteniendo suscripciones: {result.get('error')}"})
                
        except Exception as e:
            self.logger.error(f"Error en list_post_subscriptions: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    # === MÉTODOS PARA CREAR NOTIFICACIONES ===
    
    def service_create_post_notification(self, params_str: str) -> str:
        """Crea notificaciones para usuarios suscritos a un foro cuando se publica un nuevo post"""
        try:
            params = self._parse_quoted_params(params_str)
            if len(params) < 4:
                return json.dumps({"success": False, "message": "Parámetros requeridos: token foro_id post_id titulo_post"})
            
            token = params[0]
            try:
                foro_id = int(params[1])
                post_id = int(params[2])
            except ValueError:
                return json.dumps({"success": False, "message": "foro_id y post_id deben ser números válidos"})
            
            titulo_post = params[3]
            
            # Verificar token (el que crea el post)
            token_result = self._verify_token(token)
            if not token_result.get('success'):
                return json.dumps({"success": False, "message": token_result.get('message')})
            
            user_payload = token_result['payload']
            creador_id = user_payload.get('id_usuario')
            creador_email = user_payload.get('email')
            
            # Obtener usuarios suscritos al foro (excepto el creador del post)
            query = """
            SELECT sf.usuario_id, u.email 
            FROM SUSCRIPCION_FORO sf
            LEFT JOIN USUARIO u ON sf.usuario_id = u.id_usuario
            WHERE sf.foro_id = ? AND sf.activa = TRUE AND sf.usuario_id != ?
            """
            
            result = self.db_client.execute_query(query, [foro_id, creador_id])
            
            if result.get('success'):
                subscribers = result.get('results', [])
                notifications_created = 0
                
                from datetime import datetime
                now = datetime.now().isoformat()
                
                for subscriber_data in subscribers:
                    if isinstance(subscriber_data, dict):
                        usuario_id = subscriber_data.get('usuario_id')
                    else:
                        usuario_id = subscriber_data[0] if len(subscriber_data) > 0 else None
                    
                    if not usuario_id:
                        continue
                    
                    # Crear notificación
                    insert_query = """
                    INSERT INTO NOTIFICACION (usuario_id, titulo, mensaje, tipo, referencia_id, referencia_tipo, fecha, creador_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    
                    titulo = "📝 Nuevo post en foro suscrito"
                    mensaje = f"{creador_email} publicó '{titulo_post}'"
                    
                    notif_result = self.db_client.execute_query(insert_query, [
                        usuario_id, titulo, mensaje, 'foro', post_id, 'post', now, creador_id
                    ])
                    
                    if notif_result.get('success'):
                        notifications_created += 1
                
                self.logger.info(f"📧 {notifications_created} notificaciones creadas para nuevo post en foro {foro_id}")
                return json.dumps({
                    "success": True,
                    "message": f"Se crearon {notifications_created} notificaciones",
                    "notifications_created": notifications_created
                })
            else:
                return json.dumps({"success": False, "message": f"Error obteniendo suscriptores: {result.get('error')}"})
                
        except Exception as e:
            self.logger.error(f"Error en create_post_notification: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_create_comment_notification(self, params_str: str) -> str:
        """Crea notificaciones para usuarios suscritos a un post cuando se agrega un comentario"""
        try:
            params = self._parse_quoted_params(params_str)
            if len(params) < 4:
                return json.dumps({"success": False, "message": "Parámetros requeridos: token post_id comentario_id titulo_post"})
            
            token = params[0]
            try:
                post_id = int(params[1])
                comentario_id = int(params[2])
            except ValueError:
                return json.dumps({"success": False, "message": "post_id y comentario_id deben ser números válidos"})
            
            titulo_post = params[3]
            
            # Verificar token (el que crea el comentario)
            token_result = self._verify_token(token)
            if not token_result.get('success'):
                return json.dumps({"success": False, "message": token_result.get('message')})
            
            user_payload = token_result['payload']
            creador_id = user_payload.get('id_usuario')
            creador_email = user_payload.get('email')
            
            # Obtener usuarios suscritos al post (excepto el creador del comentario)
            # También incluir al autor del post si no está suscrito explícitamente
            query = """
            SELECT DISTINCT u.id_usuario, u.email
            FROM USUARIO u
            WHERE u.id_usuario IN (
                SELECT sp.usuario_id 
                FROM SUSCRIPCION_POST sp 
                WHERE sp.post_id = ? AND sp.activa = TRUE
                UNION
                SELECT p.autor_id 
                FROM POST p 
                WHERE p.id_post = ?
            ) AND u.id_usuario != ?
            """
            
            result = self.db_client.execute_query(query, [post_id, post_id, creador_id])
            
            if result.get('success'):
                subscribers = result.get('results', [])
                notifications_created = 0
                
                from datetime import datetime
                now = datetime.now().isoformat()
                
                for subscriber_data in subscribers:
                    if isinstance(subscriber_data, dict):
                        usuario_id = subscriber_data.get('id_usuario')
                    else:
                        usuario_id = subscriber_data[0] if len(subscriber_data) > 0 else None
                    
                    if not usuario_id:
                        continue
                    
                    # Crear notificación
                    insert_query = """
                    INSERT INTO NOTIFICACION (usuario_id, titulo, mensaje, tipo, referencia_id, referencia_tipo, fecha, creador_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    
                    titulo = "💬 Nuevo comentario en post suscrito"
                    mensaje = f"{creador_email} comentó en '{titulo_post}'"
                    
                    notif_result = self.db_client.execute_query(insert_query, [
                        usuario_id, titulo, mensaje, 'post', comentario_id, 'comentario', now, creador_id
                    ])
                    
                    if notif_result.get('success'):
                        notifications_created += 1
                
                self.logger.info(f"💬 {notifications_created} notificaciones creadas para nuevo comentario en post {post_id}")
                return json.dumps({
                    "success": True,
                    "message": f"Se crearon {notifications_created} notificaciones",
                    "notifications_created": notifications_created
                })
            else:
                return json.dumps({"success": False, "message": f"Error obteniendo suscriptores: {result.get('error')}"})
                
        except Exception as e:
            self.logger.error(f"Error en create_comment_notification: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_create_message_notification(self, params_str: str) -> str:
        """Crea una notificación para el destinatario de un mensaje"""
        try:
            params = self._parse_quoted_params(params_str)
            if len(params) < 4:
                return json.dumps({"success": False, "message": "Parámetros requeridos: token destinatario_email mensaje_id preview_contenido"})
            
            token = params[0]
            destinatario_email = params[1]
            try:
                mensaje_id = int(params[2])
            except ValueError:
                return json.dumps({"success": False, "message": "mensaje_id debe ser un número válido"})
            
            preview_contenido = params[3]
            
            # Verificar token (el que envía el mensaje)
            token_result = self._verify_token(token)
            if not token_result.get('success'):
                return json.dumps({"success": False, "message": token_result.get('message')})
            
            user_payload = token_result['payload']
            remitente_id = user_payload.get('id_usuario')
            remitente_email = user_payload.get('email')
            
            # Obtener ID del destinatario por email
            check_user_query = "SELECT id_usuario FROM USUARIO WHERE email = ?"
            user_result = self.db_client.execute_query(check_user_query, [destinatario_email])
            
            if not user_result.get('success') or not user_result.get('results'):
                return json.dumps({"success": False, "message": "Destinatario no encontrado"})
            
            user_data = user_result['results'][0]
            destinatario_id = user_data.get('id_usuario') if isinstance(user_data, dict) else user_data[0]
            
            # Crear notificación
            from datetime import datetime
            now = datetime.now().isoformat()
            
            insert_query = """
            INSERT INTO NOTIFICACION (usuario_id, titulo, mensaje, tipo, referencia_id, referencia_tipo, fecha, creador_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            titulo = "📩 Nuevo mensaje recibido"
            mensaje = f"Mensaje de {remitente_email}: {preview_contenido[:50]}{'...' if len(preview_contenido) > 50 else ''}"
            
            result = self.db_client.execute_query(insert_query, [
                destinatario_id, titulo, mensaje, 'mensaje', mensaje_id, 'mensaje', now, remitente_id
            ])
            
            if result.get('success'):
                self.logger.info(f"📩 Notificación de mensaje creada para usuario {destinatario_id}")
                return json.dumps({
                    "success": True,
                    "message": "Notificación de mensaje creada exitosamente"
                })
            else:
                return json.dumps({"success": False, "message": f"Error creando notificación: {result.get('error')}"})
                
        except Exception as e:
            self.logger.error(f"Error en create_message_notification: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_info(self, *args) -> str:
        """Método abstracto requerido por SOAServiceBase"""
        info_data = {
            "service": "notif",
            "description": "Servicio de gestión de notificaciones con suscripciones",
            "version": "2.0.0",
            "database": "Cloudflare D1 (remota)",
            "tables": ["NOTIFICACION", "SUSCRIPCION_FORO", "SUSCRIPCION_POST"],
            "authentication": "JWT Token required",
            "port": self.port,
            "host": self.host,
            "methods": list(self.methods.keys()) if hasattr(self, 'methods') else [],
            "dependencies": ["auth"],
            "permissions": {
                "estudiante": [
                    "list_notifications", "get_unread_count", "mark_as_read", "mark_all_as_read",
                    "get_notification", "delete_notification", "clear_all_notifications",
                    "subscribe_forum", "unsubscribe_forum", "subscribe_post", "unsubscribe_post",
                    "list_forum_subscriptions", "list_post_subscriptions"
                ],
                "moderador": ["all student permissions", "admin_list_all_notifications"],
                "servicios": ["create_post_notification", "create_comment_notification", "create_message_notification"]
            },
            "notification_types": ["mensaje", "foro", "post", "comentario"],
            "subscription_features": {
                "forum_subscriptions": "Usuarios se suscriben a foros para recibir notificaciones de nuevos posts",
                "post_subscriptions": "Usuarios se suscriben a posts para recibir notificaciones de nuevos comentarios",
                "auto_notifications": "Notificaciones automáticas para mensajes directos"
            }
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