#!/usr/bin/env python3
"""
Servicio de Gestión de Posts - SOA
Permite crear, gestionar y administrar posts en foros de discusión
"""

import logging
from typing import Dict, Any, List
import json
import jwt
from datetime import datetime
from database_client import DatabaseClient
from soa_service_base import SOAServiceBase

class PostService(SOAServiceBase):
    def __init__(self, host: str = 'localhost', port: int = 8005):
        super().__init__(
            service_name="POSTS",
            description="Servicio de gestión de posts en foros de discusión",
            host=host,
            port=port
        )
        
        # Cliente de base de datos remota
        self.db_client = DatabaseClient()
        
        # Secreto JWT (debe coincidir con auth_service)
        self.jwt_secret = "your-secret-key-here"  # En producción, usar variable de entorno
        
        # Configurar logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(f'PostService-{port}')
        
        # Inicializar base de datos
        self._init_database()
        
        self.logger.info("💬 Servicio de Posts inicializado")

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
            # Para el servicio de posts, pasar los parámetros como string
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
            # Crear tabla POST
            create_post_sql = """
            CREATE TABLE IF NOT EXISTS POST (
                id_post INTEGER PRIMARY KEY AUTOINCREMENT,
                contenido TEXT NOT NULL,
                fecha TEXT NOT NULL,
                id_foro INTEGER NOT NULL,
                autor_id INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT,
                FOREIGN KEY (id_foro) REFERENCES FORO (id_foro),
                FOREIGN KEY (autor_id) REFERENCES USUARIO (id_usuario)
            )
            """
            
            result = self.db_client.execute_query(create_post_sql)
            if result.get('success'):
                self.logger.info("✅ Tabla POST creada/verificada correctamente")
            else:
                self.logger.error(f"❌ Error creando tabla POST: {result.get('error')}")
                
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
                    # Formato dictionary: {'id_usuario': 1, 'email': 'test@email.com', 'rol': 'estudiante'}
                    return {
                        "success": True,
                        "user": {
                            "id_usuario": user_data.get('id_usuario'),
                            "email": user_data.get('email'),
                            "rol": user_data.get('rol')
                        }
                    }
                else:
                    # Formato tuple/list: [1, 'test@email.com', 'estudiante'] (fallback)
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

    def _get_foro_by_id(self, id_foro: int) -> Dict[str, Any]:
        """Verifica que un foro existe"""
        try:
            self.logger.info(f"Buscando foro con ID: {id_foro} (tipo: {type(id_foro)})")
            query = "SELECT id_foro, titulo FROM FORO WHERE id_foro = ?"
            result = self.db_client.execute_query(query, [id_foro])
            
            self.logger.info(f"Resultado consulta foro: {result}")
            
            if result.get('success') and result.get('results'):
                foro_data = result['results'][0]
                
                # La base de datos devuelve dictionaries, no tuples
                if isinstance(foro_data, dict):
                    # Formato dictionary: {'id_foro': 1, 'titulo': 'Nombre'}
                    foro_info = {
                        "success": True,
                        "foro": {
                            "id_foro": foro_data.get('id_foro'),
                            "titulo": foro_data.get('titulo')
                        }
                    }
                else:
                    # Formato tuple/list: [1, 'Nombre'] (fallback)
                    foro_info = {
                        "success": True,
                        "foro": {
                            "id_foro": foro_data[0],
                            "titulo": foro_data[1]
                        }
                    }
                
                self.logger.info(f"Foro encontrado: {foro_info}")
                return foro_info
            else:
                self.logger.warning(f"Foro {id_foro} no encontrado en la base de datos")
                return {"success": False, "message": "Foro no encontrado"}
                
        except Exception as e:
            self.logger.error(f"Error verificando foro {id_foro}: {e}")
            return {"success": False, "message": f"Error verificando foro: {str(e)}"}

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

    def service_create_post(self, params_str: str) -> str:
        """Crea un nuevo post en un foro (requiere autenticación)"""
        try:
            params = self._parse_quoted_params(params_str)
            if len(params) < 3:
                return json.dumps({"success": False, "message": "Parámetros requeridos: token id_foro 'contenido'"})
            
            token = params[0]
            id_foro = params[1]
            contenido = params[2]
            
            # Verificar token
            token_result = self._verify_token(token)
            if not token_result.get('success'):
                return json.dumps({"success": False, "message": token_result.get('message')})
            
            user_payload = token_result['payload']
            autor_id = user_payload.get('id_usuario')
            
            # Verificar que el foro existe
            try:
                id_foro_int = int(id_foro)
                foro_check = self._get_foro_by_id(id_foro_int)
            except ValueError:
                return json.dumps({"success": False, "message": "ID de foro debe ser un número válido"})
                
            if not foro_check.get('success'):
                return json.dumps({"success": False, "message": "El foro especificado no existe"})
            
            # Validar contenido
            if len(contenido.strip()) == 0:
                return json.dumps({"success": False, "message": "El contenido del post no puede estar vacío"})
            
            if len(contenido) > 5000:
                return json.dumps({"success": False, "message": "El contenido del post no puede exceder 5000 caracteres"})
            
            # Insertar post en la base de datos
            import datetime
            now = datetime.datetime.now().isoformat()
            query = """
            INSERT INTO POST (contenido, fecha, id_foro, autor_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            
            result = self.db_client.execute_query(query, [contenido, now, id_foro_int, autor_id, now, now])
            
            if result.get('success'):
                # Obtener el ID del post recién creado
                post_id = result.get('lastrowid')
                if not post_id:
                    # Fallback: buscar el último post creado por este usuario
                    last_post_query = "SELECT id_post FROM POST WHERE autor_id = ? ORDER BY id_post DESC LIMIT 1"
                    last_post_result = self.db_client.execute_query(last_post_query, [autor_id])
                    if last_post_result.get('success') and last_post_result.get('results'):
                        post_data = last_post_result['results'][0]
                        post_id = post_data.get('id_post') if isinstance(post_data, dict) else post_data[0]
                
                # Obtener información del autor
                user_info = self._get_user_by_id(autor_id)
                autor_email = user_info['user']['email'] if user_info.get('success') else 'Desconocido'
                
                self.logger.info(f"💬 Post creado en foro {id_foro_int} por {autor_email} con ID {post_id}")
                return json.dumps({
                    "success": True, 
                    "message": "Post creado exitosamente",
                    "post": {
                        "id_post": post_id,
                        "contenido": contenido,
                        "id_foro": id_foro_int,
                        "autor_id": autor_id,
                        "autor_email": autor_email,
                        "fecha": now
                    }
                })
            else:
                return json.dumps({"success": False, "message": f"Error creando post: {result.get('error')}"})
                
        except Exception as e:
            self.logger.error(f"Error en create_post: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_get_post(self, params_str: str) -> str:
        """Obtiene un post específico por ID (requiere autenticación)"""
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
            
            # Obtener post de la base de datos con información adicional
            query = """
            SELECT p.id_post, p.contenido, p.fecha, p.id_foro, p.autor_id, p.created_at, p.updated_at,
                   u.email as autor_email, f.titulo as foro_titulo
            FROM POST p
            LEFT JOIN USUARIO u ON p.autor_id = u.id_usuario
            LEFT JOIN FORO f ON p.id_foro = f.id_foro
            WHERE p.id_post = ?
            """
            
            result = self.db_client.execute_query(query, [id_post])
            
            if result.get('success') and result.get('results'):
                post_data = result['results'][0]
                
                # Extraer campos usando el helper
                fields = self._extract_db_fields(post_data, [
                    'id_post', 'contenido', 'fecha', 'id_foro', 'autor_id', 
                    'created_at', 'updated_at', 'autor_email', 'foro_titulo'
                ])
                
                post = {
                    "id_post": fields[0],
                    "contenido": fields[1],
                    "fecha": fields[2],
                    "id_foro": fields[3],
                    "autor_id": fields[4],
                    "created_at": fields[5],
                    "updated_at": fields[6],
                    "autor_email": fields[7] or 'Desconocido',
                    "foro_titulo": fields[8] or 'Foro eliminado'
                }
                
                return json.dumps({
                    "success": True,
                    "message": "Post encontrado",
                    "post": post
                })
            else:
                return json.dumps({"success": False, "message": "Post no encontrado"})
                
        except Exception as e:
            self.logger.error(f"Error en get_post: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_list_posts(self, params_str: str) -> str:
        """Lista todos los posts de un foro específico (requiere autenticación)"""
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
            
            # Verificar que el foro existe
            try:
                id_foro_int = int(id_foro)
                foro_check = self._get_foro_by_id(id_foro_int)
            except ValueError:
                return json.dumps({"success": False, "message": "ID de foro debe ser un número válido"})
                
            if not foro_check.get('success'):
                return json.dumps({"success": False, "message": "El foro especificado no existe"})
            
            # Obtener posts del foro
            query = """
            SELECT p.id_post, p.contenido, p.fecha, p.id_foro, p.autor_id, p.created_at, p.updated_at,
                   u.email as autor_email
            FROM POST p
            LEFT JOIN USUARIO u ON p.autor_id = u.id_usuario
            WHERE p.id_foro = ?
            ORDER BY p.fecha ASC
            """
            
            result = self.db_client.execute_query(query, [id_foro_int])
            
            if result.get('success'):
                posts = []
                for post_data in result.get('results', []):
                    # Extraer campos usando el helper
                    fields = self._extract_db_fields(post_data, [
                        'id_post', 'contenido', 'fecha', 'id_foro', 'autor_id',
                        'created_at', 'updated_at', 'autor_email'
                    ])
                    
                    post = {
                        "id_post": fields[0],
                        "contenido": fields[1],
                        "fecha": fields[2],
                        "id_foro": fields[3],
                        "autor_id": fields[4],
                        "created_at": fields[5],
                        "updated_at": fields[6],
                        "autor_email": fields[7] or 'Desconocido'
                    }
                    posts.append(post)
                
                foro_titulo = foro_check['foro']['titulo']
                return json.dumps({
                    "success": True,
                    "message": f"Se encontraron {len(posts)} posts en el foro '{foro_titulo}'",
                    "foro": foro_check['foro'],
                    "posts": posts
                })
            else:
                return json.dumps({"success": False, "message": f"Error obteniendo posts: {result.get('error')}"})
                
        except Exception as e:
            self.logger.error(f"Error en list_posts: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_list_my_posts(self, params_str: str) -> str:
        """Lista los posts creados por el usuario autenticado"""
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
            
            # Obtener posts del usuario
            query = """
            SELECT p.id_post, p.contenido, p.fecha, p.id_foro, p.autor_id, p.created_at, p.updated_at,
                   u.email as autor_email, f.titulo as foro_titulo
            FROM POST p
            LEFT JOIN USUARIO u ON p.autor_id = u.id_usuario
            LEFT JOIN FORO f ON p.id_foro = f.id_foro
            WHERE p.autor_id = ?
            ORDER BY p.fecha DESC
            """
            
            result = self.db_client.execute_query(query, [autor_id])
            
            if result.get('success'):
                posts = []
                for post_data in result.get('results', []):
                    # Extraer campos usando el helper
                    fields = self._extract_db_fields(post_data, [
                        'id_post', 'contenido', 'fecha', 'id_foro', 'autor_id',
                        'created_at', 'updated_at', 'autor_email', 'foro_titulo'
                    ])
                    
                    post = {
                        "id_post": fields[0],
                        "contenido": fields[1],
                        "fecha": fields[2],
                        "id_foro": fields[3],
                        "autor_id": fields[4],
                        "created_at": fields[5],
                        "updated_at": fields[6],
                        "autor_email": fields[7] or user_payload.get('email', 'Desconocido'),
                        "foro_titulo": fields[8] or 'Foro eliminado'
                    }
                    posts.append(post)
                
                return json.dumps({
                    "success": True,
                    "message": f"Tienes {len(posts)} posts creados",
                    "posts": posts
                })
            else:
                return json.dumps({"success": False, "message": f"Error obteniendo tus posts: {result.get('error')}"})
                
        except Exception as e:
            self.logger.error(f"Error en list_my_posts: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_update_post(self, params_str: str) -> str:
        """Actualiza un post (solo el autor o moderador)"""
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
            user_id = user_payload.get('id_usuario')
            user_rol = user_payload.get('rol')
            
            # Verificar que el post existe y obtener información
            check_query = "SELECT autor_id, contenido FROM POST WHERE id_post = ?"
            check_result = self.db_client.execute_query(check_query, [id_post])
            
            if not check_result.get('success') or not check_result.get('results'):
                return json.dumps({"success": False, "message": "Post no encontrado"})
            
            post_data = check_result['results'][0]
            # Extraer campos usando el helper
            fields = self._extract_db_fields(post_data, ['autor_id', 'contenido'])
            autor_id = fields[0]
            
            # Verificar permisos: solo el autor o moderador pueden actualizar
            if user_id != autor_id and user_rol != 'moderador':
                return json.dumps({"success": False, "message": "No tienes permisos para actualizar este post"})
            
            # Validar contenido
            if len(contenido.strip()) == 0:
                return json.dumps({"success": False, "message": "El contenido del post no puede estar vacío"})
            
            if len(contenido) > 5000:
                return json.dumps({"success": False, "message": "El contenido del post no puede exceder 5000 caracteres"})
            
            # Actualizar post
            import datetime
            now = datetime.datetime.now().isoformat()
            update_query = """
            UPDATE POST 
            SET contenido = ?, updated_at = ? 
            WHERE id_post = ?
            """
            
            result = self.db_client.execute_query(update_query, [contenido, now, id_post])
            
            if result.get('success'):
                self.logger.info(f"💬 Post {id_post} actualizado por {user_payload.get('email')}")
                return json.dumps({
                    "success": True,
                    "message": "Post actualizado exitosamente",
                    "post": {
                        "id_post": int(id_post),
                        "contenido": contenido,
                        "updated_at": now
                    }
                })
            else:
                return json.dumps({"success": False, "message": f"Error actualizando post: {result.get('error')}"})
                
        except Exception as e:
            self.logger.error(f"Error en update_post: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_delete_post(self, params_str: str) -> str:
        """Elimina un post (solo el autor o moderador)"""
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
            
            user_payload = token_result['payload']
            user_id = user_payload.get('id_usuario')
            user_rol = user_payload.get('rol')
            
            # Verificar que el post existe y obtener información
            check_query = "SELECT autor_id, contenido FROM POST WHERE id_post = ?"
            check_result = self.db_client.execute_query(check_query, [id_post])
            
            if not check_result.get('success') or not check_result.get('results'):
                return json.dumps({"success": False, "message": "Post no encontrado"})
            
            post_data = check_result['results'][0]
            # Extraer campos usando el helper
            fields = self._extract_db_fields(post_data, ['autor_id', 'contenido'])
            autor_id = fields[0]
            contenido = fields[1]
            
            # Verificar permisos: solo el autor o moderador pueden eliminar
            if user_id != autor_id and user_rol != 'moderador':
                return json.dumps({"success": False, "message": "No tienes permisos para eliminar este post"})
            
            # Eliminar post
            delete_query = "DELETE FROM POST WHERE id_post = ?"
            result = self.db_client.execute_query(delete_query, [id_post])
            
            if result.get('success'):
                self.logger.info(f"🗑️ Post {id_post} eliminado por {user_payload.get('email')}")
                return json.dumps({
                    "success": True,
                    "message": f"Post eliminado exitosamente"
                })
            else:
                return json.dumps({"success": False, "message": f"Error eliminando post: {result.get('error')}"})
                
        except Exception as e:
            self.logger.error(f"Error en delete_post: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_admin_delete_post(self, params_str: str) -> str:
        """Elimina cualquier post (solo moderadores)"""
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
            
            user_payload = token_result['payload']
            user_rol = user_payload.get('rol')
            
            # Verificar que es moderador
            if user_rol != 'moderador':
                return json.dumps({"success": False, "message": "Solo los moderadores pueden usar este método"})
            
            # Verificar que el post existe
            check_query = "SELECT contenido FROM POST WHERE id_post = ?"
            check_result = self.db_client.execute_query(check_query, [id_post])
            
            if not check_result.get('success') or not check_result.get('results'):
                return json.dumps({"success": False, "message": "Post no encontrado"})
            
            # Eliminar post
            delete_query = "DELETE FROM POST WHERE id_post = ?"
            result = self.db_client.execute_query(delete_query, [id_post])
            
            if result.get('success'):
                self.logger.info(f"🛡️ Post {id_post} eliminado por moderador {user_payload.get('email')}")
                return json.dumps({
                    "success": True,
                    "message": f"Post eliminado exitosamente por moderador"
                })
            else:
                return json.dumps({"success": False, "message": f"Error eliminando post: {result.get('error')}"})
                
        except Exception as e:
            self.logger.error(f"Error en admin_delete_post: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_info(self, *args) -> str:
        """Método abstracto requerido por SOAServiceBase"""
        info_data = {
            "service": "post",
            "description": "Servicio de gestión de posts en foros de discusión",
            "version": "1.0.0",
            "database": "Cloudflare D1 (remota)",
            "table": "POST",
            "authentication": "JWT Token required",
            "port": self.port,
            "host": self.host,
            "methods": list(self.methods.keys()) if hasattr(self, 'methods') else [],
            "dependencies": ["auth", "forum"],
            "permissions": {
                "estudiante": ["create_post", "get_post", "list_posts", "list_my_posts", "update_post (own)", "delete_post (own)"],
                "moderador": ["all student permissions", "admin_delete_post"]
            }
        }
        return json.dumps(info_data)

def main():
    try:
        service = PostService(host='localhost', port=8005)
        
        print(f"💬 Iniciando servicio de posts...")
        service.start_service()
        
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo servicio de posts...")

if __name__ == "__main__":
    main() 