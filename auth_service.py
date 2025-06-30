import json
import jwt
import bcrypt
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from soa_service_base import SOAServiceBase
from database_client import DatabaseClient

class AuthService(SOAServiceBase):
    def __init__(self, host: str = 'localhost', port: int = 0, proxy_url: str = "https://d1-database-proxy.maliagapacheco.workers.dev/query"):
        super().__init__(
            service_name="AUTH_",
            host=host,
            port=port,
            description="Servicio de autenticación con JWT y base de datos remota via HTTP"
        )
        
        # Clave secreta para JWT (en producción debería estar en variables de entorno)
        self.jwt_secret = "your-secret-key-here"
        self.jwt_algorithm = "HS256"
        self.jwt_expiration_hours = 168  # 7 días (24 * 7)
        
        # Cliente de base de datos HTTP
        self.db = DatabaseClient(proxy_url)
        
        # Inicializar base de datos
        self._init_database()
        
        # Crear un usuario admin por defecto si no existe
        self._create_default_admin()
    
    def _init_database(self):
        """Inicializa la base de datos remota y crea las tablas necesarias"""
        try:
            # Probar conexión
            if not self.db.test_connection():
                raise Exception("No se pudo conectar a la base de datos remota")
            
            # Inicializar tablas
            if not self.db.init_auth_tables():
                raise Exception("No se pudieron crear las tablas de autenticación")
            
            self.logger.info("Base de datos remota inicializada correctamente")
            
        except Exception as e:
            self.logger.error(f"Error inicializando base de datos: {e}")
            raise
    
    def _create_default_admin(self):
        """Crea un usuario administrador por defecto si no existe"""
        try:
            # Verificar si ya existe el usuario admin
            existing_user = self.db.fetch_one(
                'SELECT email FROM USUARIO WHERE email = ?', 
                ['admin@institucional.edu.co']
            )
            
            if existing_user:
                self.logger.info("Usuario admin ya existe en la base de datos")
                return
            
            # Crear usuario admin
            admin_password = self._hash_password("admin123")
            result = self.db.execute_update('''
                INSERT INTO USUARIO (email, password, rol, created_at)
                VALUES (?, ?, ?, ?)
            ''', ['admin@institucional.edu.co', admin_password, 'moderador', datetime.now().isoformat()])
            
            if result.get("success"):
                self.logger.info("Usuario admin creado en BD remota con email: admin@institucional.edu.co / admin123")
            else:
                self.logger.error(f"Error creando usuario admin: {result.get('error')}")
            
        except Exception as e:
            self.logger.error(f"Error creando usuario admin: {e}")
    
    def _hash_password(self, password: str) -> str:
        """Hashea una contraseña usando bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """Verifica una contraseña contra su hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def _generate_jwt(self, email: str, rol: str = "estudiante", id_usuario: int = None) -> str:
        """Genera un token JWT"""
        payload = {
            "email": email,
            "rol": rol,
            "id_usuario": id_usuario,
            "exp": datetime.utcnow() + timedelta(hours=self.jwt_expiration_hours),
            "iat": datetime.utcnow(),
            "iss": "auth_service"
        }
        
        token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
        return token
    
    def _verify_jwt(self, token: str) -> Optional[Dict]:
        """Verifica un token JWT"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def _get_user_by_email(self, email: str) -> Optional[Dict]:
        """Obtiene un usuario de la base de datos por email"""
        try:
            user = self.db.fetch_one('''
                SELECT id_usuario, email, password, rol, created_at, updated_at, is_active
                FROM USUARIO 
                WHERE email = ? AND is_active = 1
            ''', [email])
            
            return user
            
        except Exception as e:
            self.logger.error(f"Error obteniendo usuario {email}: {e}")
            return None
    
    def _create_user(self, email: str, password: str, rol: str = "estudiante") -> bool:
        """Crea un nuevo usuario en la base de datos"""
        try:
            hashed_password = self._hash_password(password)
            
            result = self.db.execute_update('''
                INSERT INTO USUARIO (email, password, rol, created_at)
                VALUES (?, ?, ?, ?)
            ''', [email, hashed_password, rol, datetime.now().isoformat()])
            
            if result.get("success"):
                self.logger.info(f"Usuario creado en BD remota: {email}")
                return True
            else:
                # Verificar si es error de duplicado
                error_msg = result.get("error", "").lower()
                if "unique" in error_msg or "duplicate" in error_msg:
                    self.logger.warning(f"Usuario ya existe: {email}")
                    return False
                else:
                    self.logger.error(f"Error creando usuario {email}: {result.get('error')}")
                    return False
            
        except Exception as e:
            self.logger.error(f"Error creando usuario {email}: {e}")
            return False
    
    def _get_all_users(self) -> list:
        """Obtiene todos los usuarios activos de la base de datos"""
        try:
            users = self.db.fetch_all('''
                SELECT email, rol, created_at, updated_at
                FROM USUARIO 
                WHERE is_active = 1
                ORDER BY created_at DESC
            ''')
            
            return users or []
            
        except Exception as e:
            self.logger.error(f"Error obteniendo usuarios: {e}")
            return []
    
    def _get_user_count(self) -> int:
        """Obtiene el número total de usuarios activos"""
        try:
            result = self.db.fetch_one('SELECT COUNT(*) as count FROM USUARIO WHERE is_active = 1')
            return result.get('count', 0) if result else 0
            
        except Exception as e:
            self.logger.error(f"Error contando usuarios: {e}")
            return 0
    
    def _delete_user_by_email(self, email: str) -> bool:
        """Elimina (desactiva) un usuario por email"""
        try:
            result = self.db.execute_update(
                'UPDATE USUARIO SET is_active = 0, updated_at = ? WHERE email = ?',
                [datetime.now().isoformat(), email]
            )
            
            if result.get("success") and result.get("changes", 0) > 0:
                self.logger.info(f"Usuario eliminado: {email}")
                return True
            else:
                self.logger.warning(f"No se encontró usuario para eliminar: {email}")
                return False
            
        except Exception as e:
            self.logger.error(f"Error eliminando usuario {email}: {e}")
            return False
    
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
            # Para auth service, mantenemos todos los parámetros como strings
            if isinstance(params, str) and params:
                # Dividir parámetros por espacios pero mantener como strings
                param_parts = params.split()
                
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
            "total_users": self._get_user_count(),
            "database": {
                "type": "HTTP Proxy to Cloudflare D1",
                "proxy_url": self.db.proxy_url,
                "connection_test": self.db.test_connection()
            }
        }
        return json.dumps(info_data)

    def service_register(self, email: str, password: str, rol: str = "estudiante") -> str:
        """
        Registra un nuevo usuario en el sistema
        
        Parámetros:
            email: Email del usuario (debe ser único)
            password: Contraseña del usuario (será hasheada con bcrypt)
            rol: Rol del usuario ('estudiante' o 'moderador', por defecto 'estudiante')
        
        Retorna:
            JSON con resultado de la operación
        """
        self.logger.info(f"Solicitud de registro para: {email} con rol: {rol}")
        
        # Validar email
        if not email or '@' not in email:
            return json.dumps({
                "success": False,
                "message": "Email inválido"
            })
        
        # Validar contraseña
        if not password or len(password) < 6:
            return json.dumps({
                "success": False,
                "message": "La contraseña debe tener al menos 6 caracteres"
            })
        
        # Validar rol
        if rol not in ['estudiante', 'moderador']:
            return json.dumps({
                "success": False,
                "message": "Rol inválido. Debe ser 'estudiante' o 'moderador'"
            })
        
        # Verificar si el usuario ya existe
        existing_user = self._get_user_by_email(email)
        if existing_user:
            return json.dumps({
                "success": False,
                "message": "El email ya está registrado"
            })
        
        # Crear el usuario
        if self._create_user(email, password, rol):
            # Obtener el usuario recién creado para obtener su ID
            user = self._get_user_by_email(email)
            if user:
                # Generar token JWT para el usuario recién creado
                token = self._generate_jwt(email, rol, user['id_usuario'])
                
                return json.dumps({
                    "success": True,
                    "message": f"Usuario {email} registrado exitosamente",
                    "user": {
                        "email": email,
                        "rol": rol
                    },
                    "token": token
                })
            else:
                return json.dumps({
                    "success": False,
                    "message": "Error obteniendo información del usuario creado"
                })
        else:
            return json.dumps({
                "success": False,
                "message": "Error creando el usuario en la base de datos"
            })

    def service_login(self, email: str, password: str) -> str:
        """
        Autentica un usuario y genera un token JWT
        
        Parámetros:
            email: Email del usuario
            password: Contraseña del usuario
        
        Retorna:
            JSON con token JWT si la autenticación es exitosa
        """
        self.logger.info(f"Intento de login para: {email}")
        
        # Obtener usuario de la base de datos
        user = self._get_user_by_email(email)
        
        if not user:
            self.logger.warning(f"Usuario no encontrado: {email}")
            return json.dumps({
                "success": False,
                "message": "Credenciales inválidas"
            })
        
        # Verificar contraseña
        if not self._verify_password(password, user['password']):
            self.logger.warning(f"Contraseña incorrecta para: {email}")
            return json.dumps({
                "success": False,
                "message": "Credenciales inválidas"
            })
        
        # Generar token JWT
        token = self._generate_jwt(user['email'], user['rol'], user['id_usuario'])
        
        self.logger.info(f"Login exitoso para: {email}")
        return json.dumps({
            "success": True,
            "message": f"Bienvenido {user['email']}",
            "user": {
                "email": user['email'],
                "rol": user['rol']
            },
            "token": token
        })

    def service_verify(self, token: str) -> str:
        """
        Verifica la validez de un token JWT
        
        Parámetros:
            token: Token JWT a verificar
        
        Retorna:
            JSON con información del token si es válido
        """
        self.logger.info("Solicitud de verificación de token")
        
        payload = self._verify_jwt(token)
        
        if payload:
            # Verificar que el usuario aún existe en la base de datos
            user = self._get_user_by_email(payload.get('email'))
            
            if user:
                return json.dumps({
                    "success": True,
                    "message": "Token válido",
                    "payload": payload
                })
            else:
                return json.dumps({
                    "success": False,
                    "message": "Usuario del token no existe"
                })
        else:
            return json.dumps({
                "success": False,
                "message": "Token inválido o expirado"
            })

    def service_refresh(self, token: str) -> str:
        """
        Renueva un token JWT válido
        
        Parámetros:
            token: Token JWT a renovar
        
        Retorna:
            JSON con nuevo token si el original es válido
        """
        self.logger.info("Solicitud de renovación de token")
        
        payload = self._verify_jwt(token)
        
        if payload:
            # Verificar que el usuario aún existe en la base de datos
            user = self._get_user_by_email(payload.get('email'))
            
            if user:
                # Generar nuevo token
                new_token = self._generate_jwt(user['email'], user['rol'], user['id_usuario'])
                
                return json.dumps({
                    "success": True,
                    "message": "Token renovado exitosamente",
                    "user": {
                        "email": user['email'],
                        "rol": user['rol']
                    },
                    "token": new_token
                })
            else:
                return json.dumps({
                    "success": False,
                    "message": "Usuario del token no existe"
                })
        else:
            return json.dumps({
                "success": False,
                "message": "Token inválido o expirado para renovar"
            })

    def service_users(self) -> str:
        """
        Lista todos los usuarios registrados
        
        Retorna:
            JSON con lista de usuarios
        """
        self.logger.info("Solicitud de listado de usuarios")
        
        users = self._get_all_users()
        
        return json.dumps({
            "success": True,
            "message": f"Se encontraron {len(users)} usuarios",
            "users": users
        })

    def service_delete_user(self, email: str) -> str:
        """
        Elimina un usuario del sistema
        
        Parámetros:
            email: Email del usuario a eliminar
        
        Retorna:
            JSON con resultado de la operación
        """
        self.logger.info(f"Solicitud de eliminación de usuario: {email}")
        
        # Verificar que el usuario existe
        user = self._get_user_by_email(email)
        if not user:
            return json.dumps({
                "success": False,
                "message": "Usuario no encontrado"
            })
        
        # Eliminar usuario
        if self._delete_user_by_email(email):
            return json.dumps({
                "success": True,
                "message": f"Usuario {email} eliminado exitosamente"
            })
        else:
            return json.dumps({
                "success": False,
                "message": "Error eliminando el usuario"
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
    service = AuthService(port=port, proxy_url=proxy_url)
    
    print(f"\n🔐 SERVICIO DE AUTENTICACIÓN JWT")
    print(f"===============================")
    print(f"Base de datos: {proxy_url}")
    print(f"Puerto: {service.port}")
    print(f"Métodos disponibles: {', '.join(service.get_available_methods())}")
    print(f"Usuario por defecto: admin@institucional.edu.co / admin123")
    print(f"Presiona Ctrl+C para detener")
    
    try:
        service.start_service()
    except KeyboardInterrupt:
        print(f"\n👋 Servicio de autenticación detenido")
        service.stop_service()

if __name__ == "__main__":
    main() 