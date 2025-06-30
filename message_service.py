#!/usr/bin/env python3
"""
Servicio de Gestión de Mensajes - SOA
Permite enviar, recibir y administrar mensajes entre usuarios
"""

import logging
from typing import Dict, Any, List
import json
import jwt
from datetime import datetime
from database_client import DatabaseClient
from soa_service_base import SOAServiceBase

class MessageService(SOAServiceBase):
    def __init__(self, host: str = 'localhost', port: int = 8008):
        super().__init__(
            service_name="MSGES",
            description="Servicio de gestión de mensajes",
            host=host,
            port=port
        )
        
        # Cliente de base de datos remota
        self.db_client = DatabaseClient()
        
        # Secreto JWT (debe coincidir con auth_service)
        self.jwt_secret = "your-secret-key-here"  # En producción, usar variable de entorno
        
        # Configurar logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(f'MessageService-{port}')
        
        # Inicializar base de datos
        self._init_database()
        
        self.logger.info("💬 Servicio de Mensajes inicializado")

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
            # Para el servicio de mensajes, pasar los parámetros como string
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
            # Crear tabla MENSAJE
            create_message_sql = """
            CREATE TABLE IF NOT EXISTS MENSAJE (
                id_mensaje INTEGER PRIMARY KEY AUTOINCREMENT,
                contenido TEXT NOT NULL,
                fecha TIMESTAMP NOT NULL,
                emisor_id INTEGER NOT NULL,
                receptor_id INTEGER NOT NULL,
                FOREIGN KEY (emisor_id) REFERENCES USUARIO (id_usuario),
                FOREIGN KEY (receptor_id) REFERENCES USUARIO (id_usuario)
            )
            """
            
            result = self.db_client.execute_query(create_message_sql)
            if result.get('success'):
                self.logger.info("✅ Tabla MENSAJE creada/verificada correctamente")
            else:
                self.logger.error(f"❌ Error creando tabla MENSAJE: {result.get('error')}")
                
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

    def _get_user_by_email(self, email: str) -> Dict[str, Any]:
        """Obtiene información de un usuario por email"""
        try:
            query = "SELECT id_usuario, email, rol FROM USUARIO WHERE email = ?"
            result = self.db_client.execute_query(query, [email])
            
            if result.get('success') and result.get('results'):
                user_data = result['results'][0]
                
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

    def service_send_message(self, params_str: str) -> str:
        """Envía un mensaje a otro usuario (requiere autenticación)"""
        try:
            params = self._parse_quoted_params(params_str)
            if len(params) < 3:
                return json.dumps({"success": False, "message": "Parámetros requeridos: token email_receptor 'contenido'"})
            
            token = params[0]
            email_receptor = params[1]
            contenido = params[2]
            
            # Verificar token
            token_result = self._verify_token(token)
            if not token_result.get('success'):
                return json.dumps({"success": False, "message": token_result.get('message')})
            
            user_payload = token_result['payload']
            emisor_id = user_payload.get('id_usuario')
            
            # Validar contenido
            if len(contenido.strip()) == 0:
                return json.dumps({"success": False, "message": "El contenido del mensaje no puede estar vacío"})
            
            if len(contenido) > 2000:
                return json.dumps({"success": False, "message": "El contenido del mensaje no puede exceder 2000 caracteres"})
            
            # Verificar que el receptor existe
            receptor_info = self._get_user_by_email(email_receptor)
            if not receptor_info.get('success'):
                return json.dumps({"success": False, "message": f"Usuario receptor '{email_receptor}' no encontrado"})
            
            receptor_id = receptor_info['user']['id_usuario']
            
            # No permitir enviarse mensajes a sí mismo
            if emisor_id == receptor_id:
                return json.dumps({"success": False, "message": "No puedes enviarte mensajes a ti mismo"})
            
            # Insertar mensaje en la base de datos
            now = datetime.now().isoformat()
            query = """
            INSERT INTO MENSAJE (contenido, fecha, emisor_id, receptor_id)
            VALUES (?, ?, ?, ?)
            """
            
            result = self.db_client.execute_query(query, [contenido, now, emisor_id, receptor_id])
            
            if result.get('success'):
                # Obtener el ID del mensaje recién creado
                message_id = result.get('lastrowid')
                if not message_id:
                    # Fallback: buscar el último mensaje creado por este usuario
                    last_message_query = "SELECT id_mensaje FROM MENSAJE WHERE emisor_id = ? ORDER BY id_mensaje DESC LIMIT 1"
                    last_message_result = self.db_client.execute_query(last_message_query, [emisor_id])
                    if last_message_result.get('success') and last_message_result.get('results'):
                        message_data = last_message_result['results'][0]
                        message_id = message_data.get('id_mensaje') if isinstance(message_data, dict) else message_data[0]
                
                # Obtener información del emisor
                emisor_info = self._get_user_by_id(emisor_id)
                emisor_email = emisor_info['user']['email'] if emisor_info.get('success') else 'Desconocido'
                
                self.logger.info(f"💬 Mensaje enviado de {emisor_email} a {email_receptor} con ID {message_id}")
                
                return json.dumps({
                    "success": True, 
                    "message": "Mensaje enviado exitosamente",
                    "message": {
                        "id_mensaje": message_id,
                        "contenido": contenido,
                        "fecha": now,
                        "emisor_email": emisor_email,
                        "receptor_email": email_receptor,
                        "emisor_id": emisor_id,
                        "receptor_id": receptor_id
                    }
                })
            else:
                return json.dumps({"success": False, "message": f"Error enviando mensaje: {result.get('error')}"})
                
        except Exception as e:
            self.logger.error(f"Error en send_message: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_get_message(self, params_str: str) -> str:
        """Obtiene un mensaje específico por ID (solo emisor, receptor o moderador)"""
        try:
            params = self._parse_quoted_params(params_str)
            if len(params) < 2:
                return json.dumps({"success": False, "message": "Parámetros requeridos: token id_mensaje"})
            
            token = params[0]
            id_mensaje = params[1]
            
            # Verificar token
            token_result = self._verify_token(token)
            if not token_result.get('success'):
                return json.dumps({"success": False, "message": token_result.get('message')})
            
            user_payload = token_result['payload']
            user_id = user_payload.get('id_usuario')
            user_rol = user_payload.get('rol')
            
            # Obtener mensaje de la base de datos con información del emisor y receptor
            query = """
            SELECT m.id_mensaje, m.contenido, m.fecha, m.emisor_id, m.receptor_id,
                   e.email as emisor_email, r.email as receptor_email
            FROM MENSAJE m
            LEFT JOIN USUARIO e ON m.emisor_id = e.id_usuario
            LEFT JOIN USUARIO r ON m.receptor_id = r.id_usuario
            WHERE m.id_mensaje = ?
            """
            
            result = self.db_client.execute_query(query, [id_mensaje])
            
            if result.get('success') and result.get('results'):
                message_data = result['results'][0]
                
                # Extraer campos usando el helper
                fields = self._extract_db_fields(message_data, [
                    'id_mensaje', 'contenido', 'fecha', 'emisor_id', 'receptor_id',
                    'emisor_email', 'receptor_email'
                ])
                
                emisor_id = fields[3]
                receptor_id = fields[4]
                
                # Verificar permisos: solo emisor, receptor o moderador pueden ver el mensaje
                if user_id != emisor_id and user_id != receptor_id and user_rol != 'moderador':
                    return json.dumps({"success": False, "message": "No tienes permisos para ver este mensaje"})
                
                message = {
                    "id_mensaje": fields[0],
                    "contenido": fields[1],
                    "fecha": fields[2],
                    "emisor_id": fields[3],
                    "receptor_id": fields[4],
                    "emisor_email": fields[5] or 'Desconocido',
                    "receptor_email": fields[6] or 'Desconocido'
                }
                
                return json.dumps({
                    "success": True,
                    "message": "Mensaje encontrado",
                    "message_data": message
                })
            else:
                return json.dumps({"success": False, "message": "Mensaje no encontrado"})
                
        except Exception as e:
            self.logger.error(f"Error en get_message: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_list_sent_messages(self, params_str: str) -> str:
        """Lista los mensajes enviados por el usuario autenticado"""
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
            emisor_id = user_payload.get('id_usuario')
            
            # Obtener mensajes enviados del usuario
            query = """
            SELECT m.id_mensaje, m.contenido, m.fecha, m.emisor_id, m.receptor_id,
                   e.email as emisor_email, r.email as receptor_email
            FROM MENSAJE m
            LEFT JOIN USUARIO e ON m.emisor_id = e.id_usuario
            LEFT JOIN USUARIO r ON m.receptor_id = r.id_usuario
            WHERE m.emisor_id = ?
            ORDER BY m.fecha DESC
            """
            
            result = self.db_client.execute_query(query, [emisor_id])
            
            if result.get('success'):
                messages = []
                for message_data in result.get('results', []):
                    # Extraer campos usando el helper
                    fields = self._extract_db_fields(message_data, [
                        'id_mensaje', 'contenido', 'fecha', 'emisor_id', 'receptor_id',
                        'emisor_email', 'receptor_email'
                    ])
                    
                    message = {
                        "id_mensaje": fields[0],
                        "contenido": fields[1],
                        "fecha": fields[2],
                        "emisor_id": fields[3],
                        "receptor_id": fields[4],
                        "emisor_email": fields[5] or user_payload.get('email', 'Desconocido'),
                        "receptor_email": fields[6] or 'Desconocido'
                    }
                    messages.append(message)
                
                return json.dumps({
                    "success": True,
                    "message": f"Tienes {len(messages)} mensajes enviados",
                    "messages": messages
                })
            else:
                return json.dumps({"success": False, "message": f"Error obteniendo mensajes enviados: {result.get('error')}"})
                
        except Exception as e:
            self.logger.error(f"Error en list_sent_messages: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_list_received_messages(self, params_str: str) -> str:
        """Lista los mensajes recibidos por el usuario autenticado"""
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
            receptor_id = user_payload.get('id_usuario')
            
            # Obtener mensajes recibidos del usuario
            query = """
            SELECT m.id_mensaje, m.contenido, m.fecha, m.emisor_id, m.receptor_id,
                   e.email as emisor_email, r.email as receptor_email
            FROM MENSAJE m
            LEFT JOIN USUARIO e ON m.emisor_id = e.id_usuario
            LEFT JOIN USUARIO r ON m.receptor_id = r.id_usuario
            WHERE m.receptor_id = ?
            ORDER BY m.fecha DESC
            """
            
            result = self.db_client.execute_query(query, [receptor_id])
            
            if result.get('success'):
                messages = []
                for message_data in result.get('results', []):
                    # Extraer campos usando el helper
                    fields = self._extract_db_fields(message_data, [
                        'id_mensaje', 'contenido', 'fecha', 'emisor_id', 'receptor_id',
                        'emisor_email', 'receptor_email'
                    ])
                    
                    message = {
                        "id_mensaje": fields[0],
                        "contenido": fields[1],
                        "fecha": fields[2],
                        "emisor_id": fields[3],
                        "receptor_id": fields[4],
                        "emisor_email": fields[5] or 'Desconocido',
                        "receptor_email": fields[6] or user_payload.get('email', 'Desconocido')
                    }
                    messages.append(message)
                
                return json.dumps({
                    "success": True,
                    "message": f"Tienes {len(messages)} mensajes recibidos",
                    "messages": messages
                })
            else:
                return json.dumps({"success": False, "message": f"Error obteniendo mensajes recibidos: {result.get('error')}"})
                
        except Exception as e:
            self.logger.error(f"Error en list_received_messages: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_list_conversation(self, params_str: str) -> str:
        """Lista la conversación entre el usuario autenticado y otro usuario"""
        try:
            params = self._parse_quoted_params(params_str)
            if len(params) < 2:
                return json.dumps({"success": False, "message": "Parámetros requeridos: token email_otro_usuario"})
            
            token = params[0]
            email_otro_usuario = params[1]
            
            # Verificar token
            token_result = self._verify_token(token)
            if not token_result.get('success'):
                return json.dumps({"success": False, "message": token_result.get('message')})
            
            user_payload = token_result['payload']
            user_id = user_payload.get('id_usuario')
            
            # Verificar que el otro usuario existe
            otro_user_info = self._get_user_by_email(email_otro_usuario)
            if not otro_user_info.get('success'):
                return json.dumps({"success": False, "message": f"Usuario '{email_otro_usuario}' no encontrado"})
            
            otro_user_id = otro_user_info['user']['id_usuario']
            
            # Obtener conversación entre ambos usuarios
            query = """
            SELECT m.id_mensaje, m.contenido, m.fecha, m.emisor_id, m.receptor_id,
                   e.email as emisor_email, r.email as receptor_email
            FROM MENSAJE m
            LEFT JOIN USUARIO e ON m.emisor_id = e.id_usuario
            LEFT JOIN USUARIO r ON m.receptor_id = r.id_usuario
            WHERE (m.emisor_id = ? AND m.receptor_id = ?) OR (m.emisor_id = ? AND m.receptor_id = ?)
            ORDER BY m.fecha ASC
            """
            
            result = self.db_client.execute_query(query, [user_id, otro_user_id, otro_user_id, user_id])
            
            if result.get('success'):
                messages = []
                for message_data in result.get('results', []):
                    # Extraer campos usando el helper
                    fields = self._extract_db_fields(message_data, [
                        'id_mensaje', 'contenido', 'fecha', 'emisor_id', 'receptor_id',
                        'emisor_email', 'receptor_email'
                    ])
                    
                    message = {
                        "id_mensaje": fields[0],
                        "contenido": fields[1],
                        "fecha": fields[2],
                        "emisor_id": fields[3],
                        "receptor_id": fields[4],
                        "emisor_email": fields[5] or 'Desconocido',
                        "receptor_email": fields[6] or 'Desconocido',
                        "is_sent": fields[3] == user_id  # True si el usuario actual envió el mensaje
                    }
                    messages.append(message)
                
                return json.dumps({
                    "success": True,
                    "message": f"Conversación con {email_otro_usuario} ({len(messages)} mensajes)",
                    "messages": messages,
                    "other_user": email_otro_usuario
                })
            else:
                return json.dumps({"success": False, "message": f"Error obteniendo conversación: {result.get('error')}"})
                
        except Exception as e:
            self.logger.error(f"Error en list_conversation: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_delete_message(self, params_str: str) -> str:
        """Elimina un mensaje (solo el emisor o moderador)"""
        try:
            params = self._parse_quoted_params(params_str)
            if len(params) < 2:
                return json.dumps({"success": False, "message": "Parámetros requeridos: token id_mensaje"})
            
            token = params[0]
            id_mensaje = params[1]
            
            # Verificar token
            token_result = self._verify_token(token)
            if not token_result.get('success'):
                return json.dumps({"success": False, "message": token_result.get('message')})
            
            user_payload = token_result['payload']
            user_id = user_payload.get('id_usuario')
            user_rol = user_payload.get('rol')
            
            # Verificar que el mensaje existe y obtener información
            check_query = "SELECT emisor_id, contenido FROM MENSAJE WHERE id_mensaje = ?"
            check_result = self.db_client.execute_query(check_query, [id_mensaje])
            
            if not check_result.get('success') or not check_result.get('results'):
                return json.dumps({"success": False, "message": "Mensaje no encontrado"})
            
            message_data = check_result['results'][0]
            # Extraer campos usando el helper
            fields = self._extract_db_fields(message_data, ['emisor_id', 'contenido'])
            emisor_id = fields[0]
            contenido = fields[1]
            
            # Verificar permisos: solo el emisor o moderador pueden eliminar
            if user_id != emisor_id and user_rol != 'moderador':
                return json.dumps({"success": False, "message": "No tienes permisos para eliminar este mensaje"})
            
            # Eliminar mensaje
            delete_query = "DELETE FROM MENSAJE WHERE id_mensaje = ?"
            result = self.db_client.execute_query(delete_query, [id_mensaje])
            
            if result.get('success'):
                self.logger.info(f"🗑️ Mensaje {id_mensaje} eliminado por {user_payload.get('email')}")
                return json.dumps({
                    "success": True,
                    "message": "Mensaje eliminado exitosamente"
                })
            else:
                return json.dumps({"success": False, "message": f"Error eliminando mensaje: {result.get('error')}"})
                
        except Exception as e:
            self.logger.error(f"Error en delete_message: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_admin_delete_message(self, params_str: str) -> str:
        """Elimina cualquier mensaje (solo moderadores)"""
        try:
            params = self._parse_quoted_params(params_str)
            if len(params) < 2:
                return json.dumps({"success": False, "message": "Parámetros requeridos: token id_mensaje"})
            
            token = params[0]
            id_mensaje = params[1]
            
            # Verificar token
            token_result = self._verify_token(token)
            if not token_result.get('success'):
                return json.dumps({"success": False, "message": token_result.get('message')})
            
            user_payload = token_result['payload']
            user_rol = user_payload.get('rol')
            
            # Verificar que es moderador
            if user_rol != 'moderador':
                return json.dumps({"success": False, "message": "Solo los moderadores pueden usar este método"})
            
            # Verificar que el mensaje existe
            check_query = "SELECT contenido FROM MENSAJE WHERE id_mensaje = ?"
            check_result = self.db_client.execute_query(check_query, [id_mensaje])
            
            if not check_result.get('success') or not check_result.get('results'):
                return json.dumps({"success": False, "message": "Mensaje no encontrado"})
            
            # Eliminar mensaje
            delete_query = "DELETE FROM MENSAJE WHERE id_mensaje = ?"
            result = self.db_client.execute_query(delete_query, [id_mensaje])
            
            if result.get('success'):
                self.logger.info(f"🛡️ Mensaje {id_mensaje} eliminado por moderador {user_payload.get('email')}")
                return json.dumps({
                    "success": True,
                    "message": "Mensaje eliminado exitosamente por moderador"
                })
            else:
                return json.dumps({"success": False, "message": f"Error eliminando mensaje: {result.get('error')}"})
                
        except Exception as e:
            self.logger.error(f"Error en admin_delete_message: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_info(self, *args) -> str:
        """Método abstracto requerido por SOAServiceBase"""
        info_data = {
            "service": "msg",
            "description": "Servicio de gestión de mensajes",
            "version": "1.0.0",
            "database": "Cloudflare D1 (remota)",
            "table": "MENSAJE",
            "authentication": "JWT Token required",
            "port": self.port,
            "host": self.host,
            "methods": list(self.methods.keys()) if hasattr(self, 'methods') else [],
            "dependencies": ["auth"],
            "permissions": {
                "estudiante": ["send_message", "get_message (own)", "list_sent_messages", "list_received_messages", "list_conversation", "delete_message (own)"],
                "moderador": ["all student permissions", "admin_delete_message", "get_message (any)"]
            }
        }
        return json.dumps(info_data)

def main():
    try:
        service = MessageService(host='localhost', port=8008)
        
        print(f"💬 Iniciando servicio de mensajes...")
        service.start_service()
        
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo servicio de mensajes...")

if __name__ == "__main__":
    main() 