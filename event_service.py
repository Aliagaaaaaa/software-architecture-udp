#!/usr/bin/env python3
"""
Servicio de Gestión de Eventos - SOA
Permite crear, gestionar y administrar eventos
"""

import logging
from typing import Dict, Any, List
import json
import jwt
from datetime import datetime, date
from database_client import DatabaseClient
from soa_service_base import SOAServiceBase

class EventService(SOAServiceBase):
    def __init__(self, host: str = 'localhost', port: int = 8007):
        super().__init__(
            service_name="EVNTS",
            description="Servicio de gestión de eventos",
            host=host,
            port=port
        )
        
        # Cliente de base de datos remota
        self.db_client = DatabaseClient()
        
        # Secreto JWT (debe coincidir con auth_service)
        self.jwt_secret = "your-secret-key-here"  # En producción, usar variable de entorno
        
        # Configurar logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(f'EventService-{port}')
        
        # Inicializar base de datos
        self._init_database()
        
        self.logger.info("📅 Servicio de Eventos inicializado")

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
            # Para el servicio de eventos, pasar los parámetros como string
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
            # Crear tabla EVENTO
            create_event_sql = """
            CREATE TABLE IF NOT EXISTS EVENTO (
                id_evento INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre VARCHAR(100) NOT NULL,
                descripcion TEXT,
                fecha DATE NOT NULL,
                creador_id INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT,
                FOREIGN KEY (creador_id) REFERENCES USUARIO (id_usuario)
            )
            """
            
            result = self.db_client.execute_query(create_event_sql)
            if result.get('success'):
                self.logger.info("✅ Tabla EVENTO creada/verificada correctamente")
            else:
                self.logger.error(f"❌ Error creando tabla EVENTO: {result.get('error')}")
                
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

    def _validate_date(self, fecha_str: str) -> bool:
        """Valida que la fecha esté en formato YYYY-MM-DD"""
        try:
            datetime.strptime(fecha_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    def service_create_event(self, params_str: str) -> str:
        """Crea un nuevo evento (requiere autenticación)"""
        try:
            params = self._parse_quoted_params(params_str)
            if len(params) < 4:
                return json.dumps({"success": False, "message": "Parámetros requeridos: token 'nombre' 'descripcion' 'fecha'"})
            
            token = params[0]
            nombre = params[1]
            descripcion = params[2]
            fecha = params[3]
            
            # Verificar token
            token_result = self._verify_token(token)
            if not token_result.get('success'):
                return json.dumps({"success": False, "message": token_result.get('message')})
            
            user_payload = token_result['payload']
            creador_id = user_payload.get('id_usuario')
            
            # Validar parámetros
            if len(nombre.strip()) == 0:
                return json.dumps({"success": False, "message": "El nombre del evento no puede estar vacío"})
            
            if len(nombre) > 100:
                return json.dumps({"success": False, "message": "El nombre del evento no puede exceder 100 caracteres"})
            
            if not self._validate_date(fecha):
                return json.dumps({"success": False, "message": "La fecha debe estar en formato YYYY-MM-DD"})
            
            # Validar que la fecha no sea en el pasado
            event_date = datetime.strptime(fecha, '%Y-%m-%d').date()
            if event_date < date.today():
                return json.dumps({"success": False, "message": "La fecha del evento no puede ser en el pasado"})
            
            # Insertar evento en la base de datos
            now = datetime.now().isoformat()
            query = """
            INSERT INTO EVENTO (nombre, descripcion, fecha, creador_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            
            result = self.db_client.execute_query(query, [nombre, descripcion, fecha, creador_id, now, now])
            
            if result.get('success'):
                # Obtener el ID del evento recién creado
                evento_id = result.get('lastrowid')
                if not evento_id:
                    # Fallback: buscar el evento por datos únicos
                    query_id = "SELECT id_evento FROM EVENTO WHERE nombre = ? AND creador_id = ? AND created_at = ?"
                    id_result = self.db_client.execute_query(query_id, [nombre, creador_id, now])
                    if id_result.get('success') and id_result.get('results'):
                        evento_data = id_result['results'][0]
                        evento_id = evento_data.get('id_evento') if isinstance(evento_data, dict) else evento_data[0]
                
                # Obtener información del creador
                user_info = self._get_user_by_id(creador_id)
                creador_email = user_info['user']['email'] if user_info.get('success') else 'Desconocido'
                
                self.logger.info(f"📅 Evento '{nombre}' creado por {creador_email}")
                return json.dumps({
                    "success": True, 
                    "message": "Evento creado exitosamente",
                    "event": {
                        "id_evento": evento_id,
                        "nombre": nombre,
                        "descripcion": descripcion,
                        "fecha": fecha,
                        "creador_id": creador_id,
                        "creador_email": creador_email,
                        "created_at": now
                    }
                })
            else:
                return json.dumps({"success": False, "message": f"Error creando evento: {result.get('error')}"})
                
        except Exception as e:
            self.logger.error(f"Error en create_event: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_get_event(self, params_str: str) -> str:
        """Obtiene un evento específico por ID (requiere autenticación)"""
        try:
            params = self._parse_quoted_params(params_str)
            if len(params) < 2:
                return json.dumps({"success": False, "message": "Parámetros requeridos: token id_evento"})
            
            token = params[0]
            id_evento = params[1]
            
            # Verificar token
            token_result = self._verify_token(token)
            if not token_result.get('success'):
                return json.dumps({"success": False, "message": token_result.get('message')})
            
            # Obtener evento de la base de datos con información del creador
            query = """
            SELECT e.id_evento, e.nombre, e.descripcion, e.fecha, e.creador_id, e.created_at, e.updated_at,
                   u.email as creador_email
            FROM EVENTO e
            LEFT JOIN USUARIO u ON e.creador_id = u.id_usuario
            WHERE e.id_evento = ?
            """
            
            result = self.db_client.execute_query(query, [id_evento])
            
            if result.get('success') and result.get('results'):
                event_data = result['results'][0]
                
                # Extraer campos usando el helper
                fields = self._extract_db_fields(event_data, [
                    'id_evento', 'nombre', 'descripcion', 'fecha', 'creador_id', 
                    'created_at', 'updated_at', 'creador_email'
                ])
                
                event = {
                    "id_evento": fields[0],
                    "nombre": fields[1],
                    "descripcion": fields[2],
                    "fecha": fields[3],
                    "creador_id": fields[4],
                    "created_at": fields[5],
                    "updated_at": fields[6],
                    "creador_email": fields[7] or 'Desconocido'
                }
                
                return json.dumps({
                    "success": True,
                    "message": "Evento encontrado",
                    "event": event
                })
            else:
                return json.dumps({"success": False, "message": "Evento no encontrado"})
                
        except Exception as e:
            self.logger.error(f"Error en get_event: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_list_events(self, params_str: str) -> str:
        """Lista todos los eventos disponibles (requiere autenticación)"""
        try:
            params = self._parse_quoted_params(params_str)
            if len(params) < 1:
                return json.dumps({"success": False, "message": "Parámetros requeridos: token"})
            
            token = params[0]
            
            # Verificar token
            token_result = self._verify_token(token)
            if not token_result.get('success'):
                return json.dumps({"success": False, "message": token_result.get('message')})
            
            # Obtener todos los eventos ordenados por fecha
            query = """
            SELECT e.id_evento, e.nombre, e.descripcion, e.fecha, e.creador_id, e.created_at, e.updated_at,
                   u.email as creador_email
            FROM EVENTO e
            LEFT JOIN USUARIO u ON e.creador_id = u.id_usuario
            ORDER BY e.fecha ASC
            """
            
            result = self.db_client.execute_query(query)
            
            if result.get('success'):
                events = []
                for event_data in result.get('results', []):
                    # Extraer campos usando el helper
                    fields = self._extract_db_fields(event_data, [
                        'id_evento', 'nombre', 'descripcion', 'fecha', 'creador_id',
                        'created_at', 'updated_at', 'creador_email'
                    ])
                    
                    event = {
                        "id_evento": fields[0],
                        "nombre": fields[1],
                        "descripcion": fields[2],
                        "fecha": fields[3],
                        "creador_id": fields[4],
                        "created_at": fields[5],
                        "updated_at": fields[6],
                        "creador_email": fields[7] or 'Desconocido'
                    }
                    events.append(event)
                
                return json.dumps({
                    "success": True,
                    "message": f"Se encontraron {len(events)} eventos",
                    "events": events
                })
            else:
                return json.dumps({"success": False, "message": f"Error obteniendo eventos: {result.get('error')}"})
                
        except Exception as e:
            self.logger.error(f"Error en list_events: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_list_my_events(self, params_str: str) -> str:
        """Lista los eventos creados por el usuario autenticado"""
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
            
            # Obtener eventos del usuario
            query = """
            SELECT e.id_evento, e.nombre, e.descripcion, e.fecha, e.creador_id, e.created_at, e.updated_at,
                   u.email as creador_email
            FROM EVENTO e
            LEFT JOIN USUARIO u ON e.creador_id = u.id_usuario
            WHERE e.creador_id = ?
            ORDER BY e.fecha ASC
            """
            
            result = self.db_client.execute_query(query, [creador_id])
            
            if result.get('success'):
                events = []
                for event_data in result.get('results', []):
                    # Extraer campos usando el helper
                    fields = self._extract_db_fields(event_data, [
                        'id_evento', 'nombre', 'descripcion', 'fecha', 'creador_id',
                        'created_at', 'updated_at', 'creador_email'
                    ])
                    
                    event = {
                        "id_evento": fields[0],
                        "nombre": fields[1],
                        "descripcion": fields[2],
                        "fecha": fields[3],
                        "creador_id": fields[4],
                        "created_at": fields[5],
                        "updated_at": fields[6],
                        "creador_email": fields[7] or user_payload.get('email', 'Desconocido')
                    }
                    events.append(event)
                
                return json.dumps({
                    "success": True,
                    "message": f"Tienes {len(events)} eventos creados",
                    "events": events
                })
            else:
                return json.dumps({"success": False, "message": f"Error obteniendo tus eventos: {result.get('error')}"})
                
        except Exception as e:
            self.logger.error(f"Error en list_my_events: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_update_event(self, params_str: str) -> str:
        """Actualiza un evento (solo el creador o moderador)"""
        try:
            params = self._parse_quoted_params(params_str)
            if len(params) < 5:
                return json.dumps({"success": False, "message": "Parámetros requeridos: token id_evento 'nombre' 'descripcion' 'fecha'"})
            
            token = params[0]
            id_evento = params[1]
            nombre = params[2]
            descripcion = params[3]
            fecha = params[4]
            
            # Verificar token
            token_result = self._verify_token(token)
            if not token_result.get('success'):
                return json.dumps({"success": False, "message": token_result.get('message')})
            
            user_payload = token_result['payload']
            user_id = user_payload.get('id_usuario')
            user_rol = user_payload.get('rol')
            
            # Verificar que el evento existe y obtener información
            check_query = "SELECT creador_id, nombre FROM EVENTO WHERE id_evento = ?"
            check_result = self.db_client.execute_query(check_query, [id_evento])
            
            if not check_result.get('success') or not check_result.get('results'):
                return json.dumps({"success": False, "message": "Evento no encontrado"})
            
            event_data = check_result['results'][0]
            # Extraer campos usando el helper
            fields = self._extract_db_fields(event_data, ['creador_id', 'nombre'])
            creador_id = fields[0]
            
            # Verificar permisos: solo el creador o moderador pueden actualizar
            if user_id != creador_id and user_rol != 'moderador':
                return json.dumps({"success": False, "message": "No tienes permisos para actualizar este evento"})
            
            # Validar parámetros
            if len(nombre.strip()) == 0:
                return json.dumps({"success": False, "message": "El nombre del evento no puede estar vacío"})
            
            if len(nombre) > 100:
                return json.dumps({"success": False, "message": "El nombre del evento no puede exceder 100 caracteres"})
            
            if not self._validate_date(fecha):
                return json.dumps({"success": False, "message": "La fecha debe estar en formato YYYY-MM-DD"})
            
            # Validar que la fecha no sea en el pasado (solo si se está cambiando)
            event_date = datetime.strptime(fecha, '%Y-%m-%d').date()
            if event_date < date.today():
                return json.dumps({"success": False, "message": "La fecha del evento no puede ser en el pasado"})
            
            # Actualizar evento
            now = datetime.now().isoformat()
            update_query = """
            UPDATE EVENTO 
            SET nombre = ?, descripcion = ?, fecha = ?, updated_at = ? 
            WHERE id_evento = ?
            """
            
            result = self.db_client.execute_query(update_query, [nombre, descripcion, fecha, now, id_evento])
            
            if result.get('success'):
                self.logger.info(f"📅 Evento {id_evento} actualizado por {user_payload.get('email')}")
                return json.dumps({
                    "success": True,
                    "message": "Evento actualizado exitosamente",
                    "event": {
                        "id_evento": int(id_evento),
                        "nombre": nombre,
                        "descripcion": descripcion,
                        "fecha": fecha,
                        "updated_at": now
                    }
                })
            else:
                return json.dumps({"success": False, "message": f"Error actualizando evento: {result.get('error')}"})
                
        except Exception as e:
            self.logger.error(f"Error en update_event: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_delete_event(self, params_str: str) -> str:
        """Elimina un evento (solo el creador o moderador)"""
        try:
            params = self._parse_quoted_params(params_str)
            if len(params) < 2:
                return json.dumps({"success": False, "message": "Parámetros requeridos: token id_evento"})
            
            token = params[0]
            id_evento = params[1]
            
            # Verificar token
            token_result = self._verify_token(token)
            if not token_result.get('success'):
                return json.dumps({"success": False, "message": token_result.get('message')})
            
            user_payload = token_result['payload']
            user_id = user_payload.get('id_usuario')
            user_rol = user_payload.get('rol')
            
            # Verificar que el evento existe y obtener información
            check_query = "SELECT creador_id, nombre FROM EVENTO WHERE id_evento = ?"
            check_result = self.db_client.execute_query(check_query, [id_evento])
            
            if not check_result.get('success') or not check_result.get('results'):
                return json.dumps({"success": False, "message": "Evento no encontrado"})
            
            event_data = check_result['results'][0]
            # Extraer campos usando el helper
            fields = self._extract_db_fields(event_data, ['creador_id', 'nombre'])
            creador_id = fields[0]
            nombre = fields[1]
            
            # Verificar permisos: solo el creador o moderador pueden eliminar
            if user_id != creador_id and user_rol != 'moderador':
                return json.dumps({"success": False, "message": "No tienes permisos para eliminar este evento"})
            
            # Eliminar evento
            delete_query = "DELETE FROM EVENTO WHERE id_evento = ?"
            result = self.db_client.execute_query(delete_query, [id_evento])
            
            if result.get('success'):
                self.logger.info(f"🗑️ Evento {id_evento} ({nombre}) eliminado por {user_payload.get('email')}")
                return json.dumps({
                    "success": True,
                    "message": f"Evento '{nombre}' eliminado exitosamente"
                })
            else:
                return json.dumps({"success": False, "message": f"Error eliminando evento: {result.get('error')}"})
                
        except Exception as e:
            self.logger.error(f"Error en delete_event: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_admin_delete_event(self, params_str: str) -> str:
        """Elimina cualquier evento (solo moderadores)"""
        try:
            params = self._parse_quoted_params(params_str)
            if len(params) < 2:
                return json.dumps({"success": False, "message": "Parámetros requeridos: token id_evento"})
            
            token = params[0]
            id_evento = params[1]
            
            # Verificar token
            token_result = self._verify_token(token)
            if not token_result.get('success'):
                return json.dumps({"success": False, "message": token_result.get('message')})
            
            user_payload = token_result['payload']
            user_rol = user_payload.get('rol')
            
            # Verificar que es moderador
            if user_rol != 'moderador':
                return json.dumps({"success": False, "message": "Solo los moderadores pueden usar este método"})
            
            # Verificar que el evento existe
            check_query = "SELECT nombre FROM EVENTO WHERE id_evento = ?"
            check_result = self.db_client.execute_query(check_query, [id_evento])
            
            if not check_result.get('success') or not check_result.get('results'):
                return json.dumps({"success": False, "message": "Evento no encontrado"})
            
            event_data = check_result['results'][0]
            fields = self._extract_db_fields(event_data, ['nombre'])
            nombre = fields[0]
            
            # Eliminar evento
            delete_query = "DELETE FROM EVENTO WHERE id_evento = ?"
            result = self.db_client.execute_query(delete_query, [id_evento])
            
            if result.get('success'):
                self.logger.info(f"🛡️ Evento {id_evento} ({nombre}) eliminado por moderador {user_payload.get('email')}")
                return json.dumps({
                    "success": True,
                    "message": f"Evento '{nombre}' eliminado exitosamente por moderador"
                })
            else:
                return json.dumps({"success": False, "message": f"Error eliminando evento: {result.get('error')}"})
                
        except Exception as e:
            self.logger.error(f"Error en admin_delete_event: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_info(self, *args) -> str:
        """Método abstracto requerido por SOAServiceBase"""
        info_data = {
            "service": "event",
            "description": "Servicio de gestión de eventos",
            "version": "1.0.0",
            "database": "Cloudflare D1 (remota)",
            "table": "EVENTO",
            "authentication": "JWT Token required",
            "port": self.port,
            "host": self.host,
            "methods": list(self.methods.keys()) if hasattr(self, 'methods') else [],
            "dependencies": ["auth"],
            "permissions": {
                "estudiante": ["create_event", "get_event", "list_events", "list_my_events", "update_event (own)", "delete_event (own)"],
                "moderador": ["all student permissions", "admin_delete_event"]
            }
        }
        return json.dumps(info_data)

def main():
    try:
        service = EventService(host='localhost', port=8007)
        
        print(f"📅 Iniciando servicio de eventos...")
        service.start_service()
        
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo servicio de eventos...")

if __name__ == "__main__":
    main() 