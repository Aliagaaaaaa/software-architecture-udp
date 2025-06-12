#!/usr/bin/env python3
"""
Servicio de Gestión de Foros - SOA
Permite crear, gestionar y administrar foros de discusión
"""

import logging
from typing import Dict, Any, List
import json
import jwt
from datetime import datetime
from database_client import DatabaseClient
from notification_helper import NotificationHelper
from soa_service_base import SOAServiceBase

class ForumService(SOAServiceBase):
    def __init__(self, host: str = 'localhost', port: int = 8003):
        super().__init__(
            service_name="FORUM",
            description="Servicio de gestión de foros de discusión",
            host=host,
            port=port
        )
        
        # Cliente de base de datos remota
        self.db_client = DatabaseClient()
        
        # Helper de notificaciones
        self.notification_helper = NotificationHelper()
        
        # Secreto JWT (debe coincidir con auth_service)
        self.jwt_secret = "mi_clave_secreta_super_segura_2024"
        
        # Configurar logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(f'ForumService-{port}')
        
        # Inicializar base de datos
        self._init_database()
        
        self.logger.info("🗣️ Servicio de Foros inicializado")

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
            # Para el servicio de foros, pasar los parámetros como string
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
            # Crear tabla FORO
            create_foro_sql = """
            CREATE TABLE IF NOT EXISTS FORO (
                id_foro INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                categoria TEXT NOT NULL,
                creador_id INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT,
                FOREIGN KEY (creador_id) REFERENCES USUARIO (id_usuario)
            )
            """
            
            result = self.db_client.execute_query(create_foro_sql)
            if result.get('success'):
                self.logger.info("✅ Tabla FORO creada/verificada correctamente")
            else:
                self.logger.error(f"❌ Error creando tabla FORO: {result.get('error')}")
                
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
            self.logger.info(f"Buscando usuario con ID: {user_id}")
            query = "SELECT id_usuario, email, rol FROM USUARIO WHERE id_usuario = ?"
            result = self.db_client.execute_query(query, [user_id])
            
            self.logger.info(f"Resultado consulta usuario: {result}")
            
            if result.get('success') and result.get('results'):
                user_data = result['results'][0]
                
                # La base de datos devuelve dictionaries, no tuples
                if isinstance(user_data, dict):
                    # Formato dictionary: {'id_usuario': 1, 'email': 'test@email.com', 'rol': 'estudiante'}
                    user_info = {
                        "success": True,
                        "user": {
                            "id_usuario": user_data.get('id_usuario'),
                            "email": user_data.get('email'),
                            "rol": user_data.get('rol')
                        }
                    }
                else:
                    # Formato tuple/list: [1, 'test@email.com', 'estudiante'] (fallback)
                    user_info = {
                        "success": True,
                        "user": {
                            "id_usuario": user_data[0],
                            "email": user_data[1],
                            "rol": user_data[2]
                        }
                    }
                
                self.logger.info(f"Usuario encontrado: {user_info}")
                return user_info
            else:
                self.logger.warning(f"Usuario {user_id} no encontrado")
                return {"success": False, "message": "Usuario no encontrado"}
                
        except Exception as e:
            self.logger.error(f"Error obteniendo usuario {user_id}: {e}")
            return {"success": False, "message": f"Error obteniendo usuario: {str(e)}"}

    def _parse_quoted_params(self, params_str: str) -> List[str]:
        """Parsea parámetros respetando comillas simples"""
        import shlex
        try:
            # shlex.split respeta las comillas y maneja espacios dentro de ellas
            return shlex.split(params_str)
        except ValueError:
            # Si falla shlex, hacer split simple como fallback
            return params_str.split()

    def _extract_db_fields(self, row_data, field_names):
        """Helper para extraer campos de una fila de base de datos, manejando tanto dict como tuple"""
        if isinstance(row_data, dict):
            # Formato dictionary de la nueva API
            return [row_data.get(field) for field in field_names]
        else:
            # Formato tuple/list (fallback)
            return list(row_data[:len(field_names)])

    def register_method(self, name: str, method):
        """Método helper para registrar métodos manualmente si es necesario"""
        self.methods[name] = method

    def service_create_forum(self, params_str: str) -> str:
        """Crea un nuevo foro (requiere autenticación)"""
        try:
            self.logger.info(f"Iniciando create_forum con params: {params_str}")
            
            params = self._parse_quoted_params(params_str)
            self.logger.info(f"Params parseados: {params}")
            
            if len(params) < 3:
                return json.dumps({"success": False, "message": "Parámetros requeridos: token 'titulo' 'categoria'"})
            
            token = params[0]
            titulo = params[1]
            categoria = params[2]
            
            self.logger.info(f"Token: {token[:20]}..., Titulo: {titulo}, Categoria: {categoria}")
            
            # Verificar token
            token_result = self._verify_token(token)
            self.logger.info(f"Verificación de token: {token_result.get('success')}")
            
            if not token_result.get('success'):
                return json.dumps({"success": False, "message": token_result.get('message')})
            
            user_payload = token_result['payload']
            creador_id = user_payload.get('id_usuario')
            
            self.logger.info(f"Usuario payload: {user_payload}")
            self.logger.info(f"Creador ID: {creador_id}")
            
            # Validar longitud del título
            if len(titulo) > 200:
                return json.dumps({"success": False, "message": "El título no puede exceder 200 caracteres"})
            
            # Validar longitud de la categoría
            if len(categoria) > 50:
                return json.dumps({"success": False, "message": "La categoría no puede exceder 50 caracteres"})
            
            # Insertar foro en la base de datos usando datetime.now().isoformat()
            import datetime
            now = datetime.datetime.now().isoformat()
            query = """
            INSERT INTO FORO (titulo, categoria, creador_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """
            
            self.logger.info(f"Ejecutando query: {query}")
            self.logger.info(f"Parámetros: {[titulo, categoria, creador_id, now, now]}")
            
            result = self.db_client.execute_query(query, [titulo, categoria, creador_id, now, now])
            
            self.logger.info(f"Resultado de insert: {result}")
            
            if result.get('success'):
                # Notificar a otros usuarios sobre el nuevo foro
                try:
                    # Obtener información del creador
                    user_info = self._get_user_by_id(creador_id)
                    creador_email = user_info['user']['email'] if user_info.get('success') else 'Desconocido'
                    
                    # Obtener IDs de usuarios para notificar (excluyendo al creador)
                    usuarios_ids = self.notification_helper.get_all_users_ids(exclude_user_id=creador_id)
                    
                    if usuarios_ids:
                        # Usar la función específica para foros del helper
                        self.notification_helper.notify_new_forum(
                            usuarios_ids, creador_email, titulo, result.get('last_id')
                        )
                        self.logger.info(f"🔔 Notificaciones enviadas a {len(usuarios_ids)} usuarios sobre nuevo foro '{titulo}'")
                except Exception as e:
                    self.logger.warning(f"⚠️ Error enviando notificaciones de foro: {e}")
                
                # Por ahora, simplificar la respuesta para evitar errores adicionales
                self.logger.info(f"📝 Foro creado exitosamente: {titulo}")
                return json.dumps({
                    "success": True, 
                    "message": f"Foro '{titulo}' creado exitosamente",
                    "debug": {
                        "titulo": titulo,
                        "categoria": categoria,
                        "creador_id": creador_id
                    }
                })
            else:
                return json.dumps({"success": False, "message": f"Error creando foro: {result.get('error')}"})
                
        except Exception as e:
            self.logger.error(f"Error en create_forum: {e}")
            self.logger.error(f"Tipo de error: {type(e)}")
            self.logger.error(f"Error args: {e.args}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_get_forum(self, params_str: str) -> str:
        """Obtiene un foro específico por ID (requiere autenticación)"""
        try:
            params = self._parse_quoted_params(params_str)
            if len(params) < 2:
                return json.dumps({"success": False, "message": "Parámetros requeridos: token id_foro"})
            
            token = params[0]
            id_foro = params[1]
            
            # Verificar token
            token_result = self._verify_token(token)
            if not token_result.get('success'):
                return json.dumps({"success": False, "message": token_result.get('message')})
            
            # Obtener foro de la base de datos
            query = """
            SELECT id_foro, titulo, categoria, creador_id, created_at, updated_at 
            FROM FORO 
            WHERE id_foro = ?
            """
            
            result = self.db_client.execute_query(query, [id_foro])
            
            if result.get('success') and result.get('results'):
                forum_data = result['results'][0]
                
                # Extraer campos usando el helper que maneja dict/tuple
                fields = self._extract_db_fields(forum_data, ['id_foro', 'titulo', 'categoria', 'creador_id', 'created_at', 'updated_at'])
                
                # Obtener información del creador
                user_info = self._get_user_by_id(fields[3])
                creator_email = user_info['user']['email'] if user_info.get('success') else 'Desconocido'
                
                forum = {
                    "id_foro": fields[0],
                    "titulo": fields[1],
                    "categoria": fields[2],
                    "creador_id": fields[3],
                    "creador_email": creator_email,
                    "created_at": fields[4],
                    "updated_at": fields[5]
                }
                
                return json.dumps({
                    "success": True,
                    "message": "Foro encontrado",
                    "forum": forum
                })
            else:
                return json.dumps({"success": False, "message": "Foro no encontrado"})
                
        except Exception as e:
            self.logger.error(f"Error en get_forum: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_list_forums(self, params_str: str) -> str:
        """Lista todos los foros disponibles (requiere autenticación)"""
        try:
            params = self._parse_quoted_params(params_str)
            if len(params) < 1:
                return json.dumps({"success": False, "message": "Parámetros requeridos: token"})
            
            token = params[0]
            
            # Verificar token
            token_result = self._verify_token(token)
            if not token_result.get('success'):
                return json.dumps({"success": False, "message": token_result.get('message')})
            
            # Obtener todos los foros
            query = """
            SELECT f.id_foro, f.titulo, f.categoria, f.creador_id, f.created_at, f.updated_at,
                   u.email as creador_email
            FROM FORO f
            LEFT JOIN USUARIO u ON f.creador_id = u.id_usuario
            ORDER BY f.created_at DESC
            """
            
            result = self.db_client.execute_query(query)
            
            if result.get('success'):
                forums = []
                for forum_data in result.get('results', []):
                    # Extraer campos usando el helper que maneja dict/tuple
                    fields = self._extract_db_fields(forum_data, ['id_foro', 'titulo', 'categoria', 'creador_id', 'created_at', 'updated_at', 'creador_email'])
                    
                    forum = {
                        "id_foro": fields[0],
                        "titulo": fields[1],
                        "categoria": fields[2],
                        "creador_id": fields[3],
                        "created_at": fields[4],
                        "updated_at": fields[5],
                        "creador_email": fields[6] or 'Desconocido'
                    }
                    forums.append(forum)
                
                return json.dumps({
                    "success": True,
                    "message": f"Se encontraron {len(forums)} foros",
                    "forums": forums
                })
            else:
                return json.dumps({"success": False, "message": f"Error obteniendo foros: {result.get('error')}"})
                
        except Exception as e:
            self.logger.error(f"Error en list_forums: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_list_my_forums(self, params_str: str) -> str:
        """Lista los foros creados por el usuario autenticado"""
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
            creador_id = user_payload.get('id_usuario')
            
            # Obtener foros del usuario
            query = """
            SELECT f.id_foro, f.titulo, f.categoria, f.creador_id, f.created_at, f.updated_at,
                   u.email as creador_email
            FROM FORO f
            LEFT JOIN USUARIO u ON f.creador_id = u.id_usuario
            WHERE f.creador_id = ?
            ORDER BY f.created_at DESC
            """
            
            result = self.db_client.execute_query(query, [creador_id])
            
            if result.get('success'):
                forums = []
                for forum_data in result.get('results', []):
                    # Extraer campos usando el helper que maneja dict/tuple
                    fields = self._extract_db_fields(forum_data, ['id_foro', 'titulo', 'categoria', 'creador_id', 'created_at', 'updated_at', 'creador_email'])
                    
                    forum = {
                        "id_foro": fields[0],
                        "titulo": fields[1],
                        "categoria": fields[2],
                        "creador_id": fields[3],
                        "created_at": fields[4],
                        "updated_at": fields[5],
                        "creador_email": fields[6] or user_payload.get('email', 'Desconocido')
                    }
                    forums.append(forum)
                
                return json.dumps({
                    "success": True,
                    "message": f"Tienes {len(forums)} foros creados",
                    "forums": forums
                })
            else:
                return json.dumps({"success": False, "message": f"Error obteniendo tus foros: {result.get('error')}"})
                
        except Exception as e:
            self.logger.error(f"Error en list_my_forums: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_update_forum(self, params_str: str) -> str:
        """Actualiza un foro (solo el creador o moderador)"""
        try:
            params = self._parse_quoted_params(params_str)
            if len(params) < 4:
                return json.dumps({"success": False, "message": "Parámetros requeridos: token id_foro 'titulo' 'categoria'"})
            
            token = params[0]
            id_foro = params[1]
            titulo = params[2]
            categoria = params[3]
            
            # Verificar token
            token_result = self._verify_token(token)
            if not token_result.get('success'):
                return json.dumps({"success": False, "message": token_result.get('message')})
            
            user_payload = token_result['payload']
            user_id = user_payload.get('id_usuario')
            user_rol = user_payload.get('rol')
            
            # Verificar que el foro existe y obtener información
            check_query = "SELECT creador_id, titulo FROM FORO WHERE id_foro = ?"
            check_result = self.db_client.execute_query(check_query, [id_foro])
            
            if not check_result.get('success') or not check_result.get('results'):
                return json.dumps({"success": False, "message": "Foro no encontrado"})
            
            forum_data = check_result['results'][0]
            creador_id = forum_data[0]
            
            # Verificar permisos: solo el creador o moderador pueden actualizar
            if user_id != creador_id and user_rol != 'moderador':
                return json.dumps({"success": False, "message": "No tienes permisos para actualizar este foro"})
            
            # Validar longitudes
            if len(titulo) > 200:
                return json.dumps({"success": False, "message": "El título no puede exceder 200 caracteres"})
            
            if len(categoria) > 50:
                return json.dumps({"success": False, "message": "La categoría no puede exceder 50 caracteres"})
            
            # Actualizar foro
            import datetime
            now = datetime.datetime.now().isoformat()
            update_query = """
            UPDATE FORO 
            SET titulo = ?, categoria = ?, updated_at = ? 
            WHERE id_foro = ?
            """
            
            result = self.db_client.execute_query(update_query, [titulo, categoria, now, id_foro])
            
            if result.get('success'):
                # Obtener foro actualizado
                get_updated_query = """
                SELECT f.id_foro, f.titulo, f.categoria, f.creador_id, f.created_at, f.updated_at,
                       u.email as creador_email
                FROM FORO f
                LEFT JOIN USUARIO u ON f.creador_id = u.id_usuario
                WHERE f.id_foro = ?
                """
                
                updated_result = self.db_client.execute_query(get_updated_query, [id_foro])
                
                if updated_result.get('success') and updated_result.get('results'):
                    forum_data = updated_result['results'][0]
                    forum = {
                        "id_foro": forum_data[0],
                        "titulo": forum_data[1],
                        "categoria": forum_data[2],
                        "creador_id": forum_data[3],
                        "created_at": forum_data[4],
                        "updated_at": forum_data[5],
                        "creador_email": forum_data[6] or 'Desconocido'
                    }
                    
                    self.logger.info(f"📝 Foro actualizado: {titulo} por {user_payload.get('email')}")
                    return json.dumps({
                        "success": True,
                        "message": "Foro actualizado exitosamente",
                        "forum": forum
                    })
                
            return json.dumps({"success": False, "message": f"Error actualizando foro: {result.get('error')}"})
                
        except Exception as e:
            self.logger.error(f"Error en update_forum: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_delete_forum(self, params_str: str) -> str:
        """Elimina un foro (solo el creador o moderador)"""
        try:
            params = self._parse_quoted_params(params_str)
            if len(params) < 2:
                return json.dumps({"success": False, "message": "Parámetros requeridos: token id_foro"})
            
            token = params[0]
            id_foro = params[1]
            
            # Verificar token
            token_result = self._verify_token(token)
            if not token_result.get('success'):
                return json.dumps({"success": False, "message": token_result.get('message')})
            
            user_payload = token_result['payload']
            user_id = user_payload.get('id_usuario')
            user_rol = user_payload.get('rol')
            
            # Verificar que el foro existe y obtener información
            check_query = "SELECT creador_id, titulo FROM FORO WHERE id_foro = ?"
            check_result = self.db_client.execute_query(check_query, [id_foro])
            
            if not check_result.get('success') or not check_result.get('results'):
                return json.dumps({"success": False, "message": "Foro no encontrado"})
            
            forum_data = check_result['results'][0]
            creador_id = forum_data[0]
            titulo = forum_data[1]
            
            # Verificar permisos: solo el creador o moderador pueden eliminar
            if user_id != creador_id and user_rol != 'moderador':
                return json.dumps({"success": False, "message": "No tienes permisos para eliminar este foro"})
            
            # Eliminar foro
            delete_query = "DELETE FROM FORO WHERE id_foro = ?"
            result = self.db_client.execute_query(delete_query, [id_foro])
            
            if result.get('success'):
                self.logger.info(f"🗑️ Foro eliminado: {titulo} por {user_payload.get('email')}")
                return json.dumps({
                    "success": True,
                    "message": f"Foro '{titulo}' eliminado exitosamente"
                })
            else:
                return json.dumps({"success": False, "message": f"Error eliminando foro: {result.get('error')}"})
                
        except Exception as e:
            self.logger.error(f"Error en delete_forum: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_admin_delete_forum(self, params_str: str) -> str:
        """Elimina cualquier foro (solo moderadores)"""
        try:
            params = self._parse_quoted_params(params_str)
            if len(params) < 2:
                return json.dumps({"success": False, "message": "Parámetros requeridos: token id_foro"})
            
            token = params[0]
            id_foro = params[1]
            
            # Verificar token
            token_result = self._verify_token(token)
            if not token_result.get('success'):
                return json.dumps({"success": False, "message": token_result.get('message')})
            
            user_payload = token_result['payload']
            user_rol = user_payload.get('rol')
            
            # Verificar que es moderador
            if user_rol != 'moderador':
                return json.dumps({"success": False, "message": "Solo los moderadores pueden usar este método"})
            
            # Verificar que el foro existe
            check_query = "SELECT titulo FROM FORO WHERE id_foro = ?"
            check_result = self.db_client.execute_query(check_query, [id_foro])
            
            if not check_result.get('success') or not check_result.get('results'):
                return json.dumps({"success": False, "message": "Foro no encontrado"})
            
            titulo = check_result['results'][0][0]
            
            # Eliminar foro
            delete_query = "DELETE FROM FORO WHERE id_foro = ?"
            result = self.db_client.execute_query(delete_query, [id_foro])
            
            if result.get('success'):
                self.logger.info(f"🛡️ Foro eliminado por moderador: {titulo} por {user_payload.get('email')}")
                return json.dumps({
                    "success": True,
                    "message": f"Foro '{titulo}' eliminado exitosamente por moderador"
                })
            else:
                return json.dumps({"success": False, "message": f"Error eliminando foro: {result.get('error')}"})
                
        except Exception as e:
            self.logger.error(f"Error en admin_delete_forum: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_info(self, *args) -> str:
        """Método abstracto requerido por SOAServiceBase"""
        info_data = {
            "service": "forum",
            "description": "Servicio de gestión de foros de discusión",
            "version": "1.0.0",
            "database": "Cloudflare D1 (remota)",
            "table": "FORO",
            "authentication": "JWT Token required",
            "port": self.port,
            "host": self.host,
            "methods": list(self.methods.keys()) if hasattr(self, 'methods') else [],
            "dependencies": ["auth"],
            "permissions": {
                "estudiante": ["create_forum", "get_forum", "list_forums", "list_my_forums", "update_forum (own)", "delete_forum (own)"],
                "moderador": ["all student permissions", "admin_delete_forum"]
            }
        }
        return json.dumps(info_data)

def main():
    try:
        service = ForumService(host='localhost', port=8003)
        
        print(f"🗣️ Iniciando servicio de foros...")
        service.start_service()
        
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo servicio de foros...")

if __name__ == "__main__":
    main() 