#!/usr/bin/env python3
"""
Servicio de Gestión de Comentarios - SOA
Permite crear, gestionar y administrar comentarios en posts
"""

import logging
from typing import Dict, Any, List
import json
import jwt
from datetime import datetime
from database_client import DatabaseClient
from soa_service_base import SOAServiceBase

class CommentService(SOAServiceBase):
    def __init__(self, host: str = 'localhost', port: int = 8006):
        super().__init__(
            service_name="COMMS",
            description="Servicio de gestión de comentarios en posts",
            host=host,
            port=port
        )
        
        # Cliente de base de datos remota
        self.db_client = DatabaseClient()
        
        # Secreto JWT (debe coincidir con auth_service)
        self.jwt_secret = "your-secret-key-here"  # En producción, usar variable de entorno
        
        # Configurar logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(f'CommentService-{port}')
        
        # Inicializar base de datos
        self._init_database()
        
        self.logger.info("💬 Servicio de Comentarios inicializado")

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
            # Para el servicio de comentarios, pasar los parámetros como string
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
            # Crear tabla COMENTARIO
            create_comment_sql = """
            CREATE TABLE IF NOT EXISTS COMENTARIO (
                id_comentario INTEGER PRIMARY KEY AUTOINCREMENT,
                contenido TEXT NOT NULL,
                fecha TEXT NOT NULL,
                id_post INTEGER NOT NULL,
                autor_id INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT,
                FOREIGN KEY (id_post) REFERENCES POST (id_post),
                FOREIGN KEY (autor_id) REFERENCES USUARIO (id_usuario)
            )
            """
            
            result = self.db_client.execute_query(create_comment_sql)
            if result.get('success'):
                self.logger.info("✅ Tabla COMENTARIO creada/verificada correctamente")
            else:
                self.logger.error(f"❌ Error creando tabla COMENTARIO: {result.get('error')}")
                
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

    def _get_post_by_id(self, id_post: int) -> Dict[str, Any]:
        """Verifica que un post existe"""
        try:
            self.logger.info(f"Buscando post con ID: {id_post} (tipo: {type(id_post)})")
            query = "SELECT id_post, contenido FROM POST WHERE id_post = ?"
            result = self.db_client.execute_query(query, [id_post])
            
            self.logger.info(f"Resultado consulta post: {result}")
            
            if result.get('success') and result.get('results'):
                post_data = result['results'][0]
                
                # La base de datos devuelve dictionaries, no tuples
                if isinstance(post_data, dict):
                    post_info = {
                        "success": True,
                        "post": {
                            "id_post": post_data.get('id_post'),
                            "contenido": post_data.get('contenido')
                        }
                    }
                else:
                    post_info = {
                        "success": True,
                        "post": {
                            "id_post": post_data[0],
                            "contenido": post_data[1]
                        }
                    }
                
                self.logger.info(f"Post encontrado: {post_info}")
                return post_info
            else:
                self.logger.warning(f"Post {id_post} no encontrado en la base de datos")
                return {"success": False, "message": "Post no encontrado"}
                
        except Exception as e:
            self.logger.error(f"Error verificando post {id_post}: {e}")
            return {"success": False, "message": f"Error verificando post: {str(e)}"}

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

    def service_create_comment(self, params_str: str) -> str:
        """Crea un nuevo comentario en un post (requiere autenticación)"""
        try:
            params = self._parse_quoted_params(params_str)
            if len(params) < 3:
                return json.dumps({"success": False, "message": "Parámetros requeridos: token id_post 'contenido'"})
            
            token = params[0]
            id_post = params[1]
            contenido = params[2]
            
            # Verificar token
            token_result = self._verify_token(token)
            if not token_result.get('success'):
                return json.dumps({"success": False, "message": token_result.get('message')})
            
            user_payload = token_result['payload']
            autor_id = user_payload.get('id_usuario')
            
            # Verificar que el post existe
            try:
                id_post_int = int(id_post)
                post_check = self._get_post_by_id(id_post_int)
            except ValueError:
                return json.dumps({"success": False, "message": "ID de post debe ser un número válido"})
                
            if not post_check.get('success'):
                return json.dumps({"success": False, "message": "El post especificado no existe"})
            
            # Validar contenido
            if len(contenido.strip()) == 0:
                return json.dumps({"success": False, "message": "El contenido del comentario no puede estar vacío"})
            
            if len(contenido) > 2000:
                return json.dumps({"success": False, "message": "El contenido del comentario no puede exceder 2000 caracteres"})
            
            # Insertar comentario en la base de datos
            import datetime
            now = datetime.datetime.now().isoformat()
            query = """
            INSERT INTO COMENTARIO (contenido, fecha, id_post, autor_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            
            result = self.db_client.execute_query(query, [contenido, now, id_post_int, autor_id, now, now])
            
            if result.get('success'):
                # Obtener el ID del comentario recién creado
                comment_id = result.get('lastrowid')
                if not comment_id:
                    # Fallback: buscar el último comentario creado por este usuario
                    last_comment_query = "SELECT id_comentario FROM COMENTARIO WHERE autor_id = ? ORDER BY id_comentario DESC LIMIT 1"
                    last_comment_result = self.db_client.execute_query(last_comment_query, [autor_id])
                    if last_comment_result.get('success') and last_comment_result.get('results'):
                        comment_data = last_comment_result['results'][0]
                        comment_id = comment_data.get('id_comentario') if isinstance(comment_data, dict) else comment_data[0]
                
                # Obtener información del autor
                user_info = self._get_user_by_id(autor_id)
                autor_email = user_info['user']['email'] if user_info.get('success') else 'Desconocido'
                
                self.logger.info(f"💬 Comentario creado en post {id_post_int} por {autor_email} con ID {comment_id}")
                return json.dumps({
                    "success": True, 
                    "message": "Comentario creado exitosamente",
                    "comment": {
                        "id_comentario": comment_id,
                        "contenido": contenido,
                        "id_post": id_post_int,
                        "autor_id": autor_id,
                        "autor_email": autor_email,
                        "fecha": now
                    }
                })
            else:
                return json.dumps({"success": False, "message": f"Error creando comentario: {result.get('error')}"})
                
        except Exception as e:
            self.logger.error(f"Error en create_comment: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_get_comment(self, params_str: str) -> str:
        """Obtiene un comentario específico por ID (requiere autenticación)"""
        try:
            params = self._parse_quoted_params(params_str)
            if len(params) < 2:
                return json.dumps({"success": False, "message": "Parámetros requeridos: token id_comentario"})
            
            token = params[0]
            id_comentario = params[1]
            
            # Verificar token
            token_result = self._verify_token(token)
            if not token_result.get('success'):
                return json.dumps({"success": False, "message": token_result.get('message')})
            
            # Obtener comentario de la base de datos con información adicional
            query = """
            SELECT c.id_comentario, c.contenido, c.fecha, c.id_post, c.autor_id, c.created_at, c.updated_at,
                   u.email as autor_email, p.contenido as post_contenido
            FROM COMENTARIO c
            LEFT JOIN USUARIO u ON c.autor_id = u.id_usuario
            LEFT JOIN POST p ON c.id_post = p.id_post
            WHERE c.id_comentario = ?
            """
            
            result = self.db_client.execute_query(query, [id_comentario])
            
            if result.get('success') and result.get('results'):
                comment_data = result['results'][0]
                
                # Extraer campos usando el helper
                fields = self._extract_db_fields(comment_data, [
                    'id_comentario', 'contenido', 'fecha', 'id_post', 'autor_id', 
                    'created_at', 'updated_at', 'autor_email', 'post_contenido'
                ])
                
                comment = {
                    "id_comentario": fields[0],
                    "contenido": fields[1],
                    "fecha": fields[2],
                    "id_post": fields[3],
                    "autor_id": fields[4],
                    "created_at": fields[5],
                    "updated_at": fields[6],
                    "autor_email": fields[7] or 'Desconocido',
                    "post_contenido": fields[8] or 'Post eliminado'
                }
                
                return json.dumps({
                    "success": True,
                    "message": "Comentario encontrado",
                    "comment": comment
                })
            else:
                return json.dumps({"success": False, "message": "Comentario no encontrado"})
                
        except Exception as e:
            self.logger.error(f"Error en get_comment: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_list_comments(self, params_str: str) -> str:
        """Lista todos los comentarios de un post específico (requiere autenticación)"""
        try:
            params = self._parse_quoted_params(params_str)
            if len(params) < 2:
                return json.dumps({"success": False, "message": "Parámetros requeridos: token id_post"})
            
            token = params[0]
            id_post = params[1]
            
            # Verificar token
            token_result = self._verify_token(token)
            if not token_result.get('success'):
                return json.dumps({"success": False, "message": token_result.get('message')})
            
            # Verificar que el post existe
            try:
                id_post_int = int(id_post)
                post_check = self._get_post_by_id(id_post_int)
            except ValueError:
                return json.dumps({"success": False, "message": "ID de post debe ser un número válido"})
                
            if not post_check.get('success'):
                return json.dumps({"success": False, "message": "El post especificado no existe"})
            
            # Obtener comentarios del post
            query = """
            SELECT c.id_comentario, c.contenido, c.fecha, c.id_post, c.autor_id, c.created_at, c.updated_at,
                   u.email as autor_email
            FROM COMENTARIO c
            LEFT JOIN USUARIO u ON c.autor_id = u.id_usuario
            WHERE c.id_post = ?
            ORDER BY c.fecha ASC
            """
            
            result = self.db_client.execute_query(query, [id_post_int])
            
            if result.get('success'):
                comments = []
                for comment_data in result.get('results', []):
                    # Extraer campos usando el helper
                    fields = self._extract_db_fields(comment_data, [
                        'id_comentario', 'contenido', 'fecha', 'id_post', 'autor_id',
                        'created_at', 'updated_at', 'autor_email'
                    ])
                    
                    comment = {
                        "id_comentario": fields[0],
                        "contenido": fields[1],
                        "fecha": fields[2],
                        "id_post": fields[3],
                        "autor_id": fields[4],
                        "created_at": fields[5],
                        "updated_at": fields[6],
                        "autor_email": fields[7] or 'Desconocido'
                    }
                    comments.append(comment)
                
                post_contenido = post_check['post']['contenido'][:50] + "..." if len(post_check['post']['contenido']) > 50 else post_check['post']['contenido']
                return json.dumps({
                    "success": True,
                    "message": f"Se encontraron {len(comments)} comentarios en el post",
                    "post": post_check['post'],
                    "post_preview": post_contenido,
                    "comments": comments
                })
            else:
                return json.dumps({"success": False, "message": f"Error obteniendo comentarios: {result.get('error')}"})
                
        except Exception as e:
            self.logger.error(f"Error en list_comments: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_list_my_comments(self, params_str: str) -> str:
        """Lista los comentarios creados por el usuario autenticado"""
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
            autor_id = user_payload.get('id_usuario')
            
            # Obtener comentarios del usuario
            query = """
            SELECT c.id_comentario, c.contenido, c.fecha, c.id_post, c.autor_id, c.created_at, c.updated_at,
                   u.email as autor_email, p.contenido as post_contenido
            FROM COMENTARIO c
            LEFT JOIN USUARIO u ON c.autor_id = u.id_usuario
            LEFT JOIN POST p ON c.id_post = p.id_post
            WHERE c.autor_id = ?
            ORDER BY c.fecha DESC
            """
            
            result = self.db_client.execute_query(query, [autor_id])
            
            if result.get('success'):
                comments = []
                for comment_data in result.get('results', []):
                    # Extraer campos usando el helper
                    fields = self._extract_db_fields(comment_data, [
                        'id_comentario', 'contenido', 'fecha', 'id_post', 'autor_id',
                        'created_at', 'updated_at', 'autor_email', 'post_contenido'
                    ])
                    
                    comment = {
                        "id_comentario": fields[0],
                        "contenido": fields[1],
                        "fecha": fields[2],
                        "id_post": fields[3],
                        "autor_id": fields[4],
                        "created_at": fields[5],
                        "updated_at": fields[6],
                        "autor_email": fields[7] or user_payload.get('email', 'Desconocido'),
                        "post_preview": (fields[8][:30] + "..." if fields[8] and len(fields[8]) > 30 else fields[8]) or 'Post eliminado'
                    }
                    comments.append(comment)
                
                return json.dumps({
                    "success": True,
                    "message": f"Tienes {len(comments)} comentarios creados",
                    "comments": comments
                })
            else:
                return json.dumps({"success": False, "message": f"Error obteniendo tus comentarios: {result.get('error')}"})
                
        except Exception as e:
            self.logger.error(f"Error en list_my_comments: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_update_comment(self, params_str: str) -> str:
        """Actualiza un comentario (solo el autor o moderador)"""
        try:
            params = self._parse_quoted_params(params_str)
            if len(params) < 3:
                return json.dumps({"success": False, "message": "Parámetros requeridos: token id_comentario 'contenido'"})
            
            token = params[0]
            id_comentario = params[1]
            contenido = params[2]
            
            # Verificar token
            token_result = self._verify_token(token)
            if not token_result.get('success'):
                return json.dumps({"success": False, "message": token_result.get('message')})
            
            user_payload = token_result['payload']
            user_id = user_payload.get('id_usuario')
            user_rol = user_payload.get('rol')
            
            # Verificar que el comentario existe y obtener información
            check_query = "SELECT autor_id, contenido FROM COMENTARIO WHERE id_comentario = ?"
            check_result = self.db_client.execute_query(check_query, [id_comentario])
            
            if not check_result.get('success') or not check_result.get('results'):
                return json.dumps({"success": False, "message": "Comentario no encontrado"})
            
            comment_data = check_result['results'][0]
            # Extraer campos usando el helper
            fields = self._extract_db_fields(comment_data, ['autor_id', 'contenido'])
            autor_id = fields[0]
            
            # Verificar permisos: solo el autor o moderador pueden actualizar
            if user_id != autor_id and user_rol != 'moderador':
                return json.dumps({"success": False, "message": "No tienes permisos para actualizar este comentario"})
            
            # Validar contenido
            if len(contenido.strip()) == 0:
                return json.dumps({"success": False, "message": "El contenido del comentario no puede estar vacío"})
            
            if len(contenido) > 2000:
                return json.dumps({"success": False, "message": "El contenido del comentario no puede exceder 2000 caracteres"})
            
            # Actualizar comentario
            import datetime
            now = datetime.datetime.now().isoformat()
            update_query = """
            UPDATE COMENTARIO 
            SET contenido = ?, updated_at = ? 
            WHERE id_comentario = ?
            """
            
            result = self.db_client.execute_query(update_query, [contenido, now, id_comentario])
            
            if result.get('success'):
                self.logger.info(f"💬 Comentario {id_comentario} actualizado por {user_payload.get('email')}")
                return json.dumps({
                    "success": True,
                    "message": "Comentario actualizado exitosamente",
                    "comment": {
                        "id_comentario": int(id_comentario),
                        "contenido": contenido,
                        "updated_at": now
                    }
                })
            else:
                return json.dumps({"success": False, "message": f"Error actualizando comentario: {result.get('error')}"})
                
        except Exception as e:
            self.logger.error(f"Error en update_comment: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_delete_comment(self, params_str: str) -> str:
        """Elimina un comentario (solo el autor o moderador)"""
        try:
            params = self._parse_quoted_params(params_str)
            if len(params) < 2:
                return json.dumps({"success": False, "message": "Parámetros requeridos: token id_comentario"})
            
            token = params[0]
            id_comentario = params[1]
            
            # Verificar token
            token_result = self._verify_token(token)
            if not token_result.get('success'):
                return json.dumps({"success": False, "message": token_result.get('message')})
            
            user_payload = token_result['payload']
            user_id = user_payload.get('id_usuario')
            user_rol = user_payload.get('rol')
            
            # Verificar que el comentario existe y obtener información
            check_query = "SELECT autor_id, contenido FROM COMENTARIO WHERE id_comentario = ?"
            check_result = self.db_client.execute_query(check_query, [id_comentario])
            
            if not check_result.get('success') or not check_result.get('results'):
                return json.dumps({"success": False, "message": "Comentario no encontrado"})
            
            comment_data = check_result['results'][0]
            # Extraer campos usando el helper
            fields = self._extract_db_fields(comment_data, ['autor_id', 'contenido'])
            autor_id = fields[0]
            contenido = fields[1]
            
            # Verificar permisos: solo el autor o moderador pueden eliminar
            if user_id != autor_id and user_rol != 'moderador':
                return json.dumps({"success": False, "message": "No tienes permisos para eliminar este comentario"})
            
            # Eliminar comentario
            delete_query = "DELETE FROM COMENTARIO WHERE id_comentario = ?"
            result = self.db_client.execute_query(delete_query, [id_comentario])
            
            if result.get('success'):
                self.logger.info(f"🗑️ Comentario {id_comentario} eliminado por {user_payload.get('email')}")
                return json.dumps({
                    "success": True,
                    "message": f"Comentario eliminado exitosamente"
                })
            else:
                return json.dumps({"success": False, "message": f"Error eliminando comentario: {result.get('error')}"})
                
        except Exception as e:
            self.logger.error(f"Error en delete_comment: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_admin_delete_comment(self, params_str: str) -> str:
        """Elimina cualquier comentario (solo moderadores)"""
        try:
            params = self._parse_quoted_params(params_str)
            if len(params) < 2:
                return json.dumps({"success": False, "message": "Parámetros requeridos: token id_comentario"})
            
            token = params[0]
            id_comentario = params[1]
            
            # Verificar token
            token_result = self._verify_token(token)
            if not token_result.get('success'):
                return json.dumps({"success": False, "message": token_result.get('message')})
            
            user_payload = token_result['payload']
            user_rol = user_payload.get('rol')
            
            # Verificar que es moderador
            if user_rol != 'moderador':
                return json.dumps({"success": False, "message": "Solo los moderadores pueden usar este método"})
            
            # Verificar que el comentario existe
            check_query = "SELECT contenido FROM COMENTARIO WHERE id_comentario = ?"
            check_result = self.db_client.execute_query(check_query, [id_comentario])
            
            if not check_result.get('success') or not check_result.get('results'):
                return json.dumps({"success": False, "message": "Comentario no encontrado"})
            
            # Eliminar comentario
            delete_query = "DELETE FROM COMENTARIO WHERE id_comentario = ?"
            result = self.db_client.execute_query(delete_query, [id_comentario])
            
            if result.get('success'):
                self.logger.info(f"🛡️ Comentario {id_comentario} eliminado por moderador {user_payload.get('email')}")
                return json.dumps({
                    "success": True,
                    "message": f"Comentario eliminado exitosamente por moderador"
                })
            else:
                return json.dumps({"success": False, "message": f"Error eliminando comentario: {result.get('error')}"})
                
        except Exception as e:
            self.logger.error(f"Error en admin_delete_comment: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_info(self, *args) -> str:
        """Método abstracto requerido por SOAServiceBase"""
        info_data = {
            "service": "comm",
            "description": "Servicio de gestión de comentarios en posts",
            "version": "1.0.0",
            "database": "Cloudflare D1 (remota)",
            "table": "COMENTARIO",
            "authentication": "JWT Token required",
            "port": self.port,
            "host": self.host,
            "methods": list(self.methods.keys()) if hasattr(self, 'methods') else [],
            "dependencies": ["auth", "post"],
            "permissions": {
                "estudiante": ["create_comment", "get_comment", "list_comments", "list_my_comments", "update_comment (own)", "delete_comment (own)"],
                "moderador": ["all student permissions", "admin_delete_comment"]
            }
        }
        return json.dumps(info_data)

def main():
    try:
        service = CommentService(host='localhost', port=8006)
        
        print(f"💬 Iniciando servicio de comentarios...")
        service.start_service()
        
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo servicio de comentarios...")

if __name__ == "__main__":
    main() 