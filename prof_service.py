#!/usr/bin/env python3
"""
Servicio SOA para gestión de perfiles de usuario
Tabla PERFIL con avatar, biografía y referencia a USUARIO
Requiere autenticación con token JWT
Utiliza base de datos remota vía HTTP proxy
"""

import json
import jwt
import shlex
from datetime import datetime
from typing import Dict, Any, Optional, List
from soa_service_base import SOAServiceBase
from database_client import DatabaseClient

class ProfileService(SOAServiceBase):
    def __init__(self, host: str = 'localhost', port: int = 0, proxy_url: str = "https://d1-database-proxy.maliagapacheco.workers.dev/query"):
        super().__init__(
            service_name="PROFS",
            host=host,
            port=port,
            description="Servicio de gestión de perfiles de usuario con avatar y biografía (requiere autenticación)"
        )
        
        # Configuración JWT (debe coincidir con auth_service)
        self.jwt_secret = "your-secret-key-here"
        self.jwt_algorithm = "HS256"
        
        # Cliente de base de datos HTTP
        self.db = DatabaseClient(proxy_url)
        
        # Inicializar base de datos
        self._init_database()
        
        self.logger.info(f"Servicio de perfiles inicializado con BD remota: {proxy_url}")
        self.logger.info("🔐 Servicio requiere autenticación JWT")
    
    def _init_database(self):
        """Inicializa la base de datos remota y crea las tablas necesarias"""
        try:
            # Probar conexión
            if not self.db.test_connection():
                raise Exception("No se pudo conectar a la base de datos remota")
            
            # Inicializar tablas (incluye USUARIO y PERFIL)
            if not self.db.init_auth_tables():
                self.logger.warning("Las tablas de autenticación ya existen o hubo un error")
            
            if not self.db.init_profile_tables():
                raise Exception("No se pudieron crear las tablas de perfiles")
            
            self.logger.info("Base de datos remota de perfiles inicializada correctamente")
            
        except Exception as e:
            self.logger.error(f"Error inicializando base de datos: {e}")
            raise
    
    def _verify_jwt_token(self, token: str) -> Optional[Dict]:
        """Verifica un token JWT y devuelve el payload si es válido"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            self.logger.warning("Token JWT expirado")
            return None
        except jwt.InvalidTokenError:
            self.logger.warning("Token JWT inválido")
            return None
        except Exception as e:
            self.logger.error(f"Error verificando token JWT: {e}")
            return None
    
    def _get_user_info_from_token(self, token: str) -> Optional[Dict]:
        """Obtiene información del usuario desde el token y valida que existe en la BD"""
        payload = self._verify_jwt_token(token)
        if not payload:
            return None
        
        email = payload.get("email")
        rol = payload.get("rol")
        
        if not email:
            return None
        
        # Verificar que el usuario aún existe y está activo
        id_usuario = self._get_user_id_by_email(email)
        if not id_usuario:
            self.logger.warning(f"Usuario del token no existe o está inactivo: {email}")
            return None
        
        return {
            "email": email,
            "rol": rol,
            "id_usuario": id_usuario,
            "payload": payload
        }
    
    def _check_permission(self, user_info: Dict, target_email: str, operation: str) -> bool:
        """Verifica si el usuario tiene permisos para realizar la operación"""
        user_email = user_info.get("email")
        user_rol = user_info.get("rol")
        
        # Los moderadores pueden hacer cualquier operación
        if user_rol == "moderador":
            return True
        
        # Los estudiantes solo pueden operar sobre su propio perfil
        if user_rol == "estudiante":
            if operation in ["create_profile", "get_profile", "update_profile", "delete_profile"]:
                return user_email == target_email
            elif operation == "list_profiles":
                # Los estudiantes no pueden listar todos los perfiles
                return False
        
        return False
    
    def _user_exists(self, id_usuario: int) -> bool:
        """Verifica si un usuario existe en la base de datos de autenticación"""
        try:
            user = self.db.fetch_one(
                'SELECT id_usuario FROM USUARIO WHERE id_usuario = ? AND is_active = 1', 
                [id_usuario]
            )
            return user is not None
            
        except Exception as e:
            self.logger.error(f"Error verificando usuario {id_usuario}: {e}")
            return False
    
    def _get_user_email_by_id(self, id_usuario: int) -> Optional[str]:
        """Obtiene el email de un usuario por su ID"""
        try:
            user = self.db.fetch_one(
                'SELECT email FROM USUARIO WHERE id_usuario = ? AND is_active = 1', 
                [id_usuario]
            )
            return user.get('email') if user else None
            
        except Exception as e:
            self.logger.error(f"Error obteniendo email del usuario {id_usuario}: {e}")
            return None
    
    def _get_user_id_by_email(self, email: str) -> Optional[int]:
        """Obtiene el ID de un usuario por su email"""
        try:
            user = self.db.fetch_one(
                'SELECT id_usuario FROM USUARIO WHERE email = ? AND is_active = 1', 
                [email]
            )
            return user.get('id_usuario') if user else None
            
        except Exception as e:
            self.logger.error(f"Error obteniendo ID del usuario {email}: {e}")
            return None
    
    def _get_profile_by_user_id(self, id_usuario: int) -> Optional[Dict]:
        """Obtiene un perfil por ID de usuario"""
        try:
            profile = self.db.fetch_one('''
                SELECT id_perfil, avatar, biografia, id_usuario, created_at, updated_at
                FROM PERFIL 
                WHERE id_usuario = ?
            ''', [id_usuario])
            
            return profile
            
        except Exception as e:
            self.logger.error(f"Error obteniendo perfil del usuario {id_usuario}: {e}")
            return None
    
    def _get_profile_by_id(self, id_perfil: int) -> Optional[Dict]:
        """Obtiene un perfil por ID de perfil"""
        try:
            profile = self.db.fetch_one('''
                SELECT id_perfil, avatar, biografia, id_usuario, created_at, updated_at
                FROM PERFIL 
                WHERE id_perfil = ?
            ''', [id_perfil])
            
            return profile
            
        except Exception as e:
            self.logger.error(f"Error obteniendo perfil {id_perfil}: {e}")
            return None
    
    def _create_profile(self, id_usuario: int, avatar: str = None, biografia: str = None) -> bool:
        """Crea un nuevo perfil en la base de datos"""
        try:
            result = self.db.execute_update('''
                INSERT INTO PERFIL (avatar, biografia, id_usuario, created_at)
                VALUES (?, ?, ?, ?)
            ''', [avatar, biografia, id_usuario, datetime.now().isoformat()])
            
            if result.get("success"):
                self.logger.info(f"Perfil creado para usuario {id_usuario}")
                return True
            else:
                # Verificar si es error de duplicado
                error_msg = result.get("error", "").lower()
                if "unique" in error_msg or "duplicate" in error_msg:
                    self.logger.warning(f"El usuario {id_usuario} ya tiene un perfil")
                    return False
                else:
                    self.logger.error(f"Error creando perfil: {result.get('error')}")
                    return False
            
        except Exception as e:
            self.logger.error(f"Error creando perfil para usuario {id_usuario}: {e}")
            return False
    
    def _update_profile(self, id_usuario: int, avatar: str = None, biografia: str = None) -> bool:
        """Actualiza un perfil existente"""
        try:
            # Construir la consulta dinámicamente según los campos proporcionados
            updates = []
            params = []
            
            if avatar is not None:
                updates.append("avatar = ?")
                params.append(avatar)
            
            if biografia is not None:
                updates.append("biografia = ?")
                params.append(biografia)
            
            if not updates:
                # No hay nada que actualizar
                return True
            
            updates.append("updated_at = ?")
            params.append(datetime.now().isoformat())
            params.append(id_usuario)
            
            sql = f"UPDATE PERFIL SET {', '.join(updates)} WHERE id_usuario = ?"
            
            result = self.db.execute_update(sql, params)
            
            if result.get("success") and result.get("changes", 0) > 0:
                self.logger.info(f"Perfil actualizado para usuario {id_usuario}")
                return True
            else:
                self.logger.warning(f"No se encontró perfil para actualizar: usuario {id_usuario}")
                return False
            
        except Exception as e:
            self.logger.error(f"Error actualizando perfil del usuario {id_usuario}: {e}")
            return False
    
    def _delete_profile(self, id_usuario: int) -> bool:
        """Elimina un perfil de la base de datos"""
        try:
            result = self.db.execute_update(
                'DELETE FROM PERFIL WHERE id_usuario = ?',
                [id_usuario]
            )
            
            if result.get("success") and result.get("changes", 0) > 0:
                self.logger.info(f"Perfil eliminado para usuario {id_usuario}")
                return True
            else:
                self.logger.warning(f"No se encontró perfil para eliminar: usuario {id_usuario}")
                return False
            
        except Exception as e:
            self.logger.error(f"Error eliminando perfil del usuario {id_usuario}: {e}")
            return False
    
    def _get_all_profiles(self) -> List[Dict]:
        """Obtiene todos los perfiles con información del usuario asociado"""
        try:
            profiles = self.db.fetch_all('''
                SELECT p.id_perfil, p.avatar, p.biografia, p.id_usuario, 
                       p.created_at, p.updated_at, u.email, u.rol
                FROM PERFIL p
                JOIN USUARIO u ON p.id_usuario = u.id_usuario
                WHERE u.is_active = 1
                ORDER BY p.created_at DESC
            ''')
            
            return profiles or []
            
        except Exception as e:
            self.logger.error(f"Error obteniendo todos los perfiles: {e}")
            return []
    
    def _get_profile_count(self) -> int:
        """Obtiene el número total de perfiles"""
        try:
            result = self.db.fetch_one('SELECT COUNT(*) as count FROM PERFIL')
            return result.get('count', 0) if result else 0
            
        except Exception as e:
            self.logger.error(f"Error contando perfiles: {e}")
            return 0
    
    def _process_request(self, request):
        """Versión especializada que mantiene todos los parámetros como strings"""
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
            # Para profile service, mantenemos todos los parámetros como strings
            if isinstance(params, str) and params:
                # Usar shlex para dividir parámetros respetando comillas
                try:
                    param_parts = shlex.split(params)
                except ValueError as e:
                    # Si hay error de parsing (comillas sin cerrar, etc)
                    self.logger.error(f"Error parsing parameters: {e}")
                    return {
                        "status": "error",
                        "message": f"Invalid parameter format: {str(e)}"
                    }
                
                # Llamar al método con los parámetros apropiados
                if len(param_parts) == 1:
                    result = self.methods[method_name](param_parts[0])
                elif len(param_parts) == 2:
                    result = self.methods[method_name](param_parts[0], param_parts[1])
                elif len(param_parts) >= 3:
                    result = self.methods[method_name](*param_parts)
                else:
                    result = self.methods[method_name]()
            else:
                # Sin parámetros
                result = self.methods[method_name]()
            
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
    
    def service_info(self) -> str:
        info_data = {
            "service_name": self.service_name,
            "description": self.description,
            "version": "3.0.0",
            "methods": list(self.get_available_methods().keys()),
            "status": "running" if self.running else "stopped",
            "total_profiles": self._get_profile_count(),
            "database": {
                "type": "HTTP Proxy to Cloudflare D1",
                "proxy_url": self.db.proxy_url,
                "connection_test": self.db.test_connection()
            },
            "authentication": {
                "required": True,
                "jwt_algorithm": self.jwt_algorithm,
                "permissions": {
                    "estudiante": "Solo gestión de su propio perfil",
                    "moderador": "Gestión de todos los perfiles + métodos admin"
                }
            }
        }
        return json.dumps(info_data)

    def service_create_profile(self, token: str, avatar: str = "", biografia: str = "") -> str:
        """
        Crea un perfil para el usuario autenticado
        
        Parámetros:
            token: Token JWT del usuario autenticado
            avatar: URL del avatar (opcional)
            biografia: Biografía del usuario (opcional)
        
        Retorna:
            JSON con resultado de la operación
        """
        self.logger.info("Solicitud de creación de perfil")
        
        # Verificar token y obtener información del usuario
        user_info = self._get_user_info_from_token(token)
        if not user_info:
            return json.dumps({
                "success": False,
                "message": "Token inválido o expirado"
            })
        
        id_usuario = user_info["id_usuario"]
        email = user_info["email"]
        
        # Verificar si el usuario ya tiene un perfil
        existing_profile = self._get_profile_by_user_id(id_usuario)
        if existing_profile:
            return json.dumps({
                "success": False,
                "message": "El usuario ya tiene un perfil. Use update_profile para modificarlo."
            })
        
        # Crear el perfil
        if self._create_profile(id_usuario, avatar or None, biografia or None):
            # Obtener el perfil recién creado para devolver la información completa
            new_profile = self._get_profile_by_user_id(id_usuario)
            
            if new_profile:
                profile_data = dict(new_profile)
                profile_data["email"] = email
                
                return json.dumps({
                    "success": True,
                    "message": f"Perfil creado exitosamente para {email}",
                    "profile": profile_data
                })
            else:
                return json.dumps({
                    "success": False,
                    "message": "Error obteniendo el perfil recién creado"
                })
        else:
            return json.dumps({
                "success": False,
                "message": "Error creando el perfil en la base de datos"
            })

    def service_get_profile(self, token: str) -> str:
        """
        Obtiene el perfil del usuario autenticado
        
        Parámetros:
            token: Token JWT del usuario autenticado
        
        Retorna:
            JSON con el perfil del usuario
        """
        self.logger.info("Solicitud de obtención de perfil")
        
        # Verificar token y obtener información del usuario
        user_info = self._get_user_info_from_token(token)
        if not user_info:
            return json.dumps({
                "success": False,
                "message": "Token inválido o expirado"
            })
        
        id_usuario = user_info["id_usuario"]
        email = user_info["email"]
        
        # Obtener el perfil
        profile = self._get_profile_by_user_id(id_usuario)
        
        if profile:
            profile_data = dict(profile)
            profile_data["email"] = email
            
            return json.dumps({
                "success": True,
                "message": f"Perfil obtenido para {email}",
                "profile": profile_data
            })
        else:
            return json.dumps({
                "success": False,
                "message": "No se encontró perfil para este usuario. Use create_profile para crear uno."
            })

    def service_update_profile(self, token: str, avatar: str = "", biografia: str = "") -> str:
        """
        Actualiza el perfil del usuario autenticado
        
        Parámetros:
            token: Token JWT del usuario autenticado
            avatar: Nueva URL del avatar (opcional, vacío para mantener actual)
            biografia: Nueva biografía (opcional, vacío para mantener actual)
        
        Retorna:
            JSON con resultado de la operación
        """
        self.logger.info("Solicitud de actualización de perfil")
        
        # Verificar token y obtener información del usuario
        user_info = self._get_user_info_from_token(token)
        if not user_info:
            return json.dumps({
                "success": False,
                "message": "Token inválido o expirado"
            })
        
        id_usuario = user_info["id_usuario"]
        email = user_info["email"]
        
        # Verificar que el perfil existe
        existing_profile = self._get_profile_by_user_id(id_usuario)
        if not existing_profile:
            return json.dumps({
                "success": False,
                "message": "No se encontró perfil para este usuario. Use create_profile para crear uno."
            })
        
        # Preparar los valores para actualizar
        # Solo actualizar campos que no estén vacíos
        update_avatar = avatar if avatar else None
        update_biografia = biografia if biografia else None
        
        if update_avatar is None and update_biografia is None:
            return json.dumps({
                "success": False,
                "message": "Debe proporcionar al menos un campo para actualizar (avatar o biografía)"
            })
        
        # Actualizar el perfil
        if self._update_profile(id_usuario, update_avatar, update_biografia):
            # Obtener el perfil actualizado
            updated_profile = self._get_profile_by_user_id(id_usuario)
            
            if updated_profile:
                profile_data = dict(updated_profile)
                profile_data["email"] = email
                
                return json.dumps({
                    "success": True,
                    "message": f"Perfil actualizado exitosamente para {email}",
                    "profile": profile_data
                })
            else:
                return json.dumps({
                    "success": False,
                    "message": "Error obteniendo el perfil actualizado"
                })
        else:
            return json.dumps({
                "success": False,
                "message": "Error actualizando el perfil en la base de datos"
            })

    def service_delete_profile(self, token: str) -> str:
        """
        Elimina el perfil del usuario autenticado
        
        Parámetros:
            token: Token JWT del usuario autenticado
        
        Retorna:
            JSON con resultado de la operación
        """
        self.logger.info("Solicitud de eliminación de perfil")
        
        # Verificar token y obtener información del usuario
        user_info = self._get_user_info_from_token(token)
        if not user_info:
            return json.dumps({
                "success": False,
                "message": "Token inválido o expirado"
            })
        
        id_usuario = user_info["id_usuario"]
        email = user_info["email"]
        
        # Verificar que el perfil existe
        existing_profile = self._get_profile_by_user_id(id_usuario)
        if not existing_profile:
            return json.dumps({
                "success": False,
                "message": "No se encontró perfil para eliminar"
            })
        
        # Eliminar el perfil
        if self._delete_profile(id_usuario):
            return json.dumps({
                "success": True,
                "message": f"Perfil eliminado exitosamente para {email}"
            })
        else:
            return json.dumps({
                "success": False,
                "message": "Error eliminando el perfil de la base de datos"
            })

    def service_list_profiles(self, token: str) -> str:
        """
        Lista todos los perfiles (solo moderadores)
        
        Parámetros:
            token: Token JWT del usuario autenticado
        
        Retorna:
            JSON con lista de todos los perfiles
        """
        self.logger.info("Solicitud de listado de perfiles")
        
        # Verificar token y obtener información del usuario
        user_info = self._get_user_info_from_token(token)
        if not user_info:
            return json.dumps({
                "success": False,
                "message": "Token inválido o expirado"
            })
        
        # Verificar permisos (solo moderadores)
        if user_info["rol"] != "moderador":
            return json.dumps({
                "success": False,
                "message": "Acceso denegado. Solo los moderadores pueden listar todos los perfiles."
            })
        
        # Obtener todos los perfiles
        profiles = self._get_all_profiles()
        
        return json.dumps({
            "success": True,
            "message": f"Se encontraron {len(profiles)} perfiles",
            "profiles": profiles
        })

    def service_list_moderators(self, token: str) -> str:
        """
        Lista todos los moderadores del sistema (solo moderadores)
        
        Parámetros:
            token: Token JWT del moderador autenticado
        
        Retorna:
            JSON con lista de moderadores (email y nombre)
        """
        self.logger.info("Solicitud de listado de moderadores")
        
        # Verificar token y obtener información del usuario
        user_info = self._get_user_info_from_token(token)
        if not user_info:
            return json.dumps({
                "success": False,
                "message": "Token inválido o expirado"
            })
        
        # Verificar permisos (solo moderadores)
        if user_info["rol"] != "moderador":
            return json.dumps({
                "success": False,
                "message": "Acceso denegado. Solo los moderadores pueden listar otros moderadores."
            })
        
        try:
            # Obtener todos los moderadores activos
            moderators = self.db.fetch_all('''
                SELECT email, name FROM USUARIO 
                WHERE rol = 'moderador' AND is_active = 1
                ORDER BY name, email
            ''')
            
            # Formatear la respuesta
            moderators_list = []
            for mod in moderators:
                moderators_list.append({
                    "email": mod.get("email"),
                    "name": mod.get("name") or mod.get("email").split("@")[0]  # Usar email como nombre si no hay nombre
                })
            
            return json.dumps({
                "success": True,
                "message": f"Se encontraron {len(moderators_list)} moderadores",
                "moderators": moderators_list
            })
            
        except Exception as e:
            self.logger.error(f"Error obteniendo lista de moderadores: {e}")
            return json.dumps({
                "success": False,
                "message": "Error interno del servidor al obtener moderadores"
            })

    def service_admin_get_profile(self, token: str, email: str) -> str:
        """
        Obtiene el perfil de cualquier usuario (solo moderadores)
        
        Parámetros:
            token: Token JWT del moderador autenticado
            email: Email del usuario cuyo perfil se quiere obtener
        
        Retorna:
            JSON con el perfil del usuario especificado
        """
        self.logger.info(f"Solicitud admin de obtención de perfil para: {email}")
        
        # Verificar token y obtener información del usuario
        user_info = self._get_user_info_from_token(token)
        if not user_info:
            return json.dumps({
                "success": False,
                "message": "Token inválido o expirado"
            })
        
        # Verificar permisos (solo moderadores)
        if user_info["rol"] != "moderador":
            return json.dumps({
                "success": False,
                "message": "Acceso denegado. Solo los moderadores pueden usar métodos admin."
            })
        
        # Obtener ID del usuario objetivo
        target_id = self._get_user_id_by_email(email)
        if not target_id:
            return json.dumps({
                "success": False,
                "message": f"Usuario no encontrado: {email}"
            })
        
        # Obtener el perfil
        profile = self._get_profile_by_user_id(target_id)
        
        if profile:
            profile_data = dict(profile)
            profile_data["email"] = email
            
            return json.dumps({
                "success": True,
                "message": f"Perfil obtenido para {email}",
                "profile": profile_data
            })
        else:
            return json.dumps({
                "success": False,
                "message": f"No se encontró perfil para el usuario: {email}"
            })

    def service_admin_delete_profile(self, token: str, email: str) -> str:
        """
        Elimina el perfil de cualquier usuario (solo moderadores)
        
        Parámetros:
            token: Token JWT del moderador autenticado
            email: Email del usuario cuyo perfil se quiere eliminar
        
        Retorna:
            JSON con resultado de la operación
        """
        self.logger.info(f"Solicitud admin de eliminación de perfil para: {email}")
        
        # Verificar token y obtener información del usuario
        user_info = self._get_user_info_from_token(token)
        if not user_info:
            return json.dumps({
                "success": False,
                "message": "Token inválido o expirado"
            })
        
        # Verificar permisos (solo moderadores)
        if user_info["rol"] != "moderador":
            return json.dumps({
                "success": False,
                "message": "Acceso denegado. Solo los moderadores pueden usar métodos admin."
            })
        
        # Obtener ID del usuario objetivo
        target_id = self._get_user_id_by_email(email)
        if not target_id:
            return json.dumps({
                "success": False,
                "message": f"Usuario no encontrado: {email}"
            })
        
        # Verificar que el perfil existe
        existing_profile = self._get_profile_by_user_id(target_id)
        if not existing_profile:
            return json.dumps({
                "success": False,
                "message": f"No se encontró perfil para eliminar: {email}"
            })
        
        # Eliminar el perfil
        if self._delete_profile(target_id):
            return json.dumps({
                "success": True,
                "message": f"Perfil eliminado exitosamente para {email}"
            })
        else:
            return json.dumps({
                "success": False,
                "message": "Error eliminando el perfil de la base de datos"
            })

def main():
    import sys
    
    # Configurar logging más detallado para desarrollo
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Permitir especificar puerto por línea de comandos
    port = 0
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Puerto inválido, usando puerto automático")
    
    # Permitir especificar URL del proxy
    proxy_url = "https://d1-database-proxy.maliagapacheco.workers.dev/query"
    if len(sys.argv) > 2:
        proxy_url = sys.argv[2]
    
    # Crear y ejecutar el servicio
    service = ProfileService(port=port, proxy_url=proxy_url)
    
    print(f"\n👤 SERVICIO DE GESTIÓN DE PERFILES")
    print(f"===================================")
    print(f"Base de datos: {proxy_url}")
    print(f"Puerto: {service.port}")
    print(f"Métodos disponibles: {', '.join(service.get_available_methods())}")
    print(f"🔐 Todos los métodos requieren autenticación JWT")
    print(f"🎯 Permisos: estudiantes (propio perfil) | moderadores (todos + admin_*)")
    print(f"Presiona Ctrl+C para detener")
    
    try:
        service.start_service()
    except KeyboardInterrupt:
        print(f"\n👋 Servicio de perfiles detenido")
        service.stop_service()

if __name__ == "__main__":
    main() 