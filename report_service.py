#!/usr/bin/env python3
"""
Report Service - SOA
Servicio de gestión de reportes de contenido
"""

import logging
from typing import Dict, Any, List
import json
import jwt
from datetime import datetime
from database_client import DatabaseClient
from soa_service_base import SOAServiceBase

class ReportService(SOAServiceBase):
    def __init__(self, host: str = 'localhost', port: int = 8009):
        super().__init__(service_name="reprt", host=host, port=port)
        self.db_client = DatabaseClient()
        self.jwt_secret = "your-secret-key-here"  # En producción, usar variable de entorno
        
        # Configurar logging específico para este servicio
        self.logger = logging.getLogger('ReportService')
        self.logger.setLevel(logging.INFO)
        
        # Inicializar base de datos
        self._init_database()

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
            # Para el servicio de reportes, pasar los parámetros como string
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
            # Crear tabla REPORTE
            create_report_sql = """
            CREATE TABLE IF NOT EXISTS REPORTE (
                id_reporte INTEGER PRIMARY KEY AUTOINCREMENT,
                contenido_id INTEGER NOT NULL,
                tipo_contenido VARCHAR(20) NOT NULL CHECK (tipo_contenido IN ('post', 'comentario')),
                razon VARCHAR(100) NOT NULL,
                fecha TIMESTAMP NOT NULL,
                reportado_por INTEGER NOT NULL,
                estado VARCHAR(20) DEFAULT 'pendiente' CHECK (estado IN ('pendiente', 'revisado', 'resuelto', 'descartado')),
                revisado_por INTEGER,
                fecha_revision TIMESTAMP,
                FOREIGN KEY (reportado_por) REFERENCES USUARIO (id_usuario),
                FOREIGN KEY (revisado_por) REFERENCES USUARIO (id_usuario)
            )
            """
            
            result = self.db_client.execute_query(create_report_sql)
            if result.get('success'):
                self.logger.info("✅ Tabla REPORTE creada/verificada correctamente")
            else:
                self.logger.error(f"❌ Error creando tabla REPORTE: {result.get('error')}")
                
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

    def _verify_content_exists(self, contenido_id: int, tipo_contenido: str) -> Dict[str, Any]:
        """Verifica que el contenido a reportar existe"""
        try:
            if tipo_contenido == "post":
                query = "SELECT id_post, contenido, autor_id FROM POST WHERE id_post = ?"
                result = self.db_client.execute_query(query, [contenido_id])
                if result.get('success') and result.get('results'):
                    return {"success": True, "content_type": "post"}
            elif tipo_contenido == "comentario":
                query = "SELECT id_comentario, contenido, autor_id FROM COMENTARIO WHERE id_comentario = ?"
                result = self.db_client.execute_query(query, [contenido_id])
                if result.get('success') and result.get('results'):
                    return {"success": True, "content_type": "comentario"}
            
            return {"success": False, "message": f"{tipo_contenido.capitalize()} no encontrado"}
                
        except Exception as e:
            return {"success": False, "message": f"Error verificando contenido: {str(e)}"}

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

    def service_create_report(self, params_str: str) -> str:
        """Crea un nuevo reporte de contenido (requiere autenticación)"""
        try:
            params = self._parse_quoted_params(params_str)
            if len(params) < 4:
                return json.dumps({"success": False, "message": "Parámetros requeridos: token contenido_id tipo_contenido 'razon'"})
            
            token = params[0]
            contenido_id = params[1]
            tipo_contenido = params[2].lower()
            razon = params[3]
            
            # Verificar token
            token_result = self._verify_token(token)
            if not token_result.get('success'):
                return json.dumps({"success": False, "message": token_result.get('message')})
            
            user_payload = token_result['payload']
            reportado_por = user_payload.get('id_usuario')
            
            # Validar tipo de contenido
            if tipo_contenido not in ['post', 'comentario']:
                return json.dumps({"success": False, "message": "tipo_contenido debe ser 'post' o 'comentario'"})
            
            # Validar razón
            if len(razon.strip()) == 0:
                return json.dumps({"success": False, "message": "La razón del reporte no puede estar vacía"})
            
            if len(razon) > 100:
                return json.dumps({"success": False, "message": "La razón del reporte no puede exceder 100 caracteres"})
            
            # Verificar que el contenido existe
            content_check = self._verify_content_exists(int(contenido_id), tipo_contenido)
            if not content_check.get('success'):
                return json.dumps({"success": False, "message": content_check.get('message')})
            
            # Verificar que no haya reportado ya este contenido
            duplicate_query = """
            SELECT id_reporte FROM REPORTE 
            WHERE contenido_id = ? AND tipo_contenido = ? AND reportado_por = ?
            """
            duplicate_result = self.db_client.execute_query(duplicate_query, [contenido_id, tipo_contenido, reportado_por])
            
            if duplicate_result.get('success') and duplicate_result.get('results'):
                return json.dumps({"success": False, "message": "Ya has reportado este contenido anteriormente"})
            
            # Insertar reporte en la base de datos
            now = datetime.now().isoformat()
            query = """
            INSERT INTO REPORTE (contenido_id, tipo_contenido, razon, fecha, reportado_por, estado)
            VALUES (?, ?, ?, ?, ?, 'pendiente')
            """
            
            result = self.db_client.execute_query(query, [contenido_id, tipo_contenido, razon, now, reportado_por])
            
            if result.get('success'):
                # Obtener el ID del reporte recién creado
                reporte_id = result.get('lastrowid')
                if not reporte_id:
                    # Fallback: buscar el reporte por datos únicos
                    query_id = "SELECT id_reporte FROM REPORTE WHERE contenido_id = ? AND tipo_contenido = ? AND reportado_por = ? AND fecha = ?"
                    id_result = self.db_client.execute_query(query_id, [contenido_id, tipo_contenido, reportado_por, now])
                    if id_result.get('success') and id_result.get('results'):
                        reporte_data = id_result['results'][0]
                        reporte_id = reporte_data.get('id_reporte') if isinstance(reporte_data, dict) else reporte_data[0]
                
                # Obtener información del usuario que reporta
                user_info = self._get_user_by_id(reportado_por)
                reportador_email = user_info['user']['email'] if user_info.get('success') else 'Desconocido'
                
                self.logger.info(f"📋 Reporte creado: {tipo_contenido} {contenido_id} por {reportador_email}")
                return json.dumps({
                    "success": True, 
                    "message": "Reporte creado exitosamente",
                    "report": {
                        "id_reporte": reporte_id,
                        "contenido_id": int(contenido_id),
                        "tipo_contenido": tipo_contenido,
                        "razon": razon,
                        "fecha": now,
                        "reportado_por": reportado_por,
                        "reportador_email": reportador_email,
                        "estado": "pendiente"
                    }
                })
            else:
                return json.dumps({"success": False, "message": f"Error creando reporte: {result.get('error')}"})
                
        except Exception as e:
            self.logger.error(f"Error en create_report: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_get_report(self, params_str: str) -> str:
        """Obtiene un reporte específico por ID (solo moderadores)"""
        try:
            params = self._parse_quoted_params(params_str)
            if len(params) < 2:
                return json.dumps({"success": False, "message": "Parámetros requeridos: token id_reporte"})
            
            token = params[0]
            id_reporte = params[1]
            
            # Verificar token
            token_result = self._verify_token(token)
            if not token_result.get('success'):
                return json.dumps({"success": False, "message": token_result.get('message')})
            
            user_payload = token_result['payload']
            user_rol = user_payload.get('rol')
            
            # Solo moderadores pueden ver reportes específicos
            if user_rol != 'moderador':
                return json.dumps({"success": False, "message": "Solo los moderadores pueden ver reportes específicos"})
            
            # Obtener reporte de la base de datos con información del reportador
            query = """
            SELECT r.id_reporte, r.contenido_id, r.tipo_contenido, r.razon, r.fecha, 
                   r.reportado_por, r.estado, r.revisado_por, r.fecha_revision,
                   u1.email as reportador_email, u2.email as revisor_email
            FROM REPORTE r
            LEFT JOIN USUARIO u1 ON r.reportado_por = u1.id_usuario
            LEFT JOIN USUARIO u2 ON r.revisado_por = u2.id_usuario
            WHERE r.id_reporte = ?
            """
            
            result = self.db_client.execute_query(query, [id_reporte])
            
            if result.get('success') and result.get('results'):
                report_data = result['results'][0]
                
                # Extraer campos usando el helper
                fields = self._extract_db_fields(report_data, [
                    'id_reporte', 'contenido_id', 'tipo_contenido', 'razon', 'fecha',
                    'reportado_por', 'estado', 'revisado_por', 'fecha_revision',
                    'reportador_email', 'revisor_email'
                ])
                
                report = {
                    "id_reporte": fields[0],
                    "contenido_id": fields[1],
                    "tipo_contenido": fields[2],
                    "razon": fields[3],
                    "fecha": fields[4],
                    "reportado_por": fields[5],
                    "estado": fields[6],
                    "revisado_por": fields[7],
                    "fecha_revision": fields[8],
                    "reportador_email": fields[9] or 'Desconocido',
                    "revisor_email": fields[10] or 'No revisado'
                }
                
                return json.dumps({
                    "success": True,
                    "message": "Reporte encontrado",
                    "report": report
                })
            else:
                return json.dumps({"success": False, "message": "Reporte no encontrado"})
                
        except Exception as e:
            self.logger.error(f"Error en get_report: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_list_reports(self, params_str: str) -> str:
        """Lista todos los reportes (solo moderadores)"""
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
            user_rol = user_payload.get('rol')
            
            # Solo moderadores pueden ver todos los reportes
            if user_rol != 'moderador':
                return json.dumps({"success": False, "message": "Solo los moderadores pueden ver todos los reportes"})
            
            # Obtener todos los reportes ordenados por fecha
            query = """
            SELECT r.id_reporte, r.contenido_id, r.tipo_contenido, r.razon, r.fecha,
                   r.reportado_por, r.estado, r.revisado_por, r.fecha_revision,
                   u1.email as reportador_email, u2.email as revisor_email
            FROM REPORTE r
            LEFT JOIN USUARIO u1 ON r.reportado_por = u1.id_usuario
            LEFT JOIN USUARIO u2 ON r.revisado_por = u2.id_usuario
            ORDER BY r.fecha DESC
            """
            
            result = self.db_client.execute_query(query)
            
            if result.get('success'):
                reports = []
                for report_data in result.get('results', []):
                    # Extraer campos usando el helper
                    fields = self._extract_db_fields(report_data, [
                        'id_reporte', 'contenido_id', 'tipo_contenido', 'razon', 'fecha',
                        'reportado_por', 'estado', 'revisado_por', 'fecha_revision',
                        'reportador_email', 'revisor_email'
                    ])
                    
                    report = {
                        "id_reporte": fields[0],
                        "contenido_id": fields[1],
                        "tipo_contenido": fields[2],
                        "razon": fields[3],
                        "fecha": fields[4],
                        "reportado_por": fields[5],
                        "estado": fields[6],
                        "revisado_por": fields[7],
                        "fecha_revision": fields[8],
                        "reportador_email": fields[9] or 'Desconocido',
                        "revisor_email": fields[10] or 'No revisado'
                    }
                    reports.append(report)
                
                return json.dumps({
                    "success": True,
                    "message": f"Se encontraron {len(reports)} reportes",
                    "reports": reports
                })
            else:
                return json.dumps({"success": False, "message": f"Error obteniendo reportes: {result.get('error')}"})
                
        except Exception as e:
            self.logger.error(f"Error en list_reports: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_list_my_reports(self, params_str: str) -> str:
        """Lista los reportes creados por el usuario autenticado"""
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
            reportado_por = user_payload.get('id_usuario')
            
            # Obtener reportes del usuario
            query = """
            SELECT r.id_reporte, r.contenido_id, r.tipo_contenido, r.razon, r.fecha,
                   r.reportado_por, r.estado, r.revisado_por, r.fecha_revision,
                   u1.email as reportador_email, u2.email as revisor_email
            FROM REPORTE r
            LEFT JOIN USUARIO u1 ON r.reportado_por = u1.id_usuario
            LEFT JOIN USUARIO u2 ON r.revisado_por = u2.id_usuario
            WHERE r.reportado_por = ?
            ORDER BY r.fecha DESC
            """
            
            result = self.db_client.execute_query(query, [reportado_por])
            
            if result.get('success'):
                reports = []
                for report_data in result.get('results', []):
                    # Extraer campos usando el helper
                    fields = self._extract_db_fields(report_data, [
                        'id_reporte', 'contenido_id', 'tipo_contenido', 'razon', 'fecha',
                        'reportado_por', 'estado', 'revisado_por', 'fecha_revision',
                        'reportador_email', 'revisor_email'
                    ])
                    
                    report = {
                        "id_reporte": fields[0],
                        "contenido_id": fields[1],
                        "tipo_contenido": fields[2],
                        "razon": fields[3],
                        "fecha": fields[4],
                        "reportado_por": fields[5],
                        "estado": fields[6],
                        "revisado_por": fields[7],
                        "fecha_revision": fields[8],
                        "reportador_email": fields[9] or user_payload.get('email', 'Desconocido'),
                        "revisor_email": fields[10] or 'No revisado'
                    }
                    reports.append(report)
                
                return json.dumps({
                    "success": True,
                    "message": f"Tienes {len(reports)} reportes creados",
                    "reports": reports
                })
            else:
                return json.dumps({"success": False, "message": f"Error obteniendo tus reportes: {result.get('error')}"})
                
        except Exception as e:
            self.logger.error(f"Error en list_my_reports: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_update_report_status(self, params_str: str) -> str:
        """Actualiza el estado de un reporte (solo moderadores)"""
        try:
            params = self._parse_quoted_params(params_str)
            if len(params) < 3:
                return json.dumps({"success": False, "message": "Parámetros requeridos: token id_reporte estado"})
            
            token = params[0]
            id_reporte = params[1]
            nuevo_estado = params[2].lower()
            
            # Verificar token
            token_result = self._verify_token(token)
            if not token_result.get('success'):
                return json.dumps({"success": False, "message": token_result.get('message')})
            
            user_payload = token_result['payload']
            user_id = user_payload.get('id_usuario')
            user_rol = user_payload.get('rol')
            
            # Solo moderadores pueden actualizar estado
            if user_rol != 'moderador':
                return json.dumps({"success": False, "message": "Solo los moderadores pueden actualizar el estado de reportes"})
            
            # Validar estado
            estados_validos = ['pendiente', 'revisado', 'resuelto', 'descartado']
            if nuevo_estado not in estados_validos:
                return json.dumps({"success": False, "message": f"Estado debe ser uno de: {', '.join(estados_validos)}"})
            
            # Verificar que el reporte existe
            check_query = "SELECT estado FROM REPORTE WHERE id_reporte = ?"
            check_result = self.db_client.execute_query(check_query, [id_reporte])
            
            if not check_result.get('success') or not check_result.get('results'):
                return json.dumps({"success": False, "message": "Reporte no encontrado"})
            
            # Actualizar estado
            now = datetime.now().isoformat()
            update_query = """
            UPDATE REPORTE 
            SET estado = ?, revisado_por = ?, fecha_revision = ?
            WHERE id_reporte = ?
            """
            
            result = self.db_client.execute_query(update_query, [nuevo_estado, user_id, now, id_reporte])
            
            if result.get('success'):
                self.logger.info(f"📋 Reporte {id_reporte} actualizado a '{nuevo_estado}' por {user_payload.get('email')}")
                return json.dumps({
                    "success": True,
                    "message": f"Estado del reporte actualizado a '{nuevo_estado}'",
                    "report": {
                        "id_reporte": int(id_reporte),
                        "estado": nuevo_estado,
                        "revisado_por": user_id,
                        "revisor_email": user_payload.get('email'),
                        "fecha_revision": now
                    }
                })
            else:
                return json.dumps({"success": False, "message": f"Error actualizando reporte: {result.get('error')}"})
                
        except Exception as e:
            self.logger.error(f"Error en update_report_status: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_delete_report(self, params_str: str) -> str:
        """Elimina un reporte (solo el creador o moderador)"""
        try:
            params = self._parse_quoted_params(params_str)
            if len(params) < 2:
                return json.dumps({"success": False, "message": "Parámetros requeridos: token id_reporte"})
            
            token = params[0]
            id_reporte = params[1]
            
            # Verificar token
            token_result = self._verify_token(token)
            if not token_result.get('success'):
                return json.dumps({"success": False, "message": token_result.get('message')})
            
            user_payload = token_result['payload']
            user_id = user_payload.get('id_usuario')
            user_rol = user_payload.get('rol')
            
            # Verificar que el reporte existe y obtener información
            check_query = "SELECT reportado_por, razon FROM REPORTE WHERE id_reporte = ?"
            check_result = self.db_client.execute_query(check_query, [id_reporte])
            
            if not check_result.get('success') or not check_result.get('results'):
                return json.dumps({"success": False, "message": "Reporte no encontrado"})
            
            report_data = check_result['results'][0]
            # Extraer campos usando el helper
            fields = self._extract_db_fields(report_data, ['reportado_por', 'razon'])
            reportado_por = fields[0]
            
            # Verificar permisos: solo el creador o moderador pueden eliminar
            if user_id != reportado_por and user_rol != 'moderador':
                return json.dumps({"success": False, "message": "No tienes permisos para eliminar este reporte"})
            
            # Eliminar reporte
            delete_query = "DELETE FROM REPORTE WHERE id_reporte = ?"
            result = self.db_client.execute_query(delete_query, [id_reporte])
            
            if result.get('success'):
                self.logger.info(f"🗑️ Reporte {id_reporte} eliminado por {user_payload.get('email')}")
                return json.dumps({
                    "success": True,
                    "message": "Reporte eliminado exitosamente"
                })
            else:
                return json.dumps({"success": False, "message": f"Error eliminando reporte: {result.get('error')}"})
                
        except Exception as e:
            self.logger.error(f"Error en delete_report: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_admin_delete_report(self, params_str: str) -> str:
        """Elimina cualquier reporte (solo moderadores)"""
        try:
            params = self._parse_quoted_params(params_str)
            if len(params) < 2:
                return json.dumps({"success": False, "message": "Parámetros requeridos: token id_reporte"})
            
            token = params[0]
            id_reporte = params[1]
            
            # Verificar token
            token_result = self._verify_token(token)
            if not token_result.get('success'):
                return json.dumps({"success": False, "message": token_result.get('message')})
            
            user_payload = token_result['payload']
            user_rol = user_payload.get('rol')
            
            # Verificar que es moderador
            if user_rol != 'moderador':
                return json.dumps({"success": False, "message": "Solo los moderadores pueden usar este método"})
            
            # Verificar que el reporte existe
            check_query = "SELECT razon FROM REPORTE WHERE id_reporte = ?"
            check_result = self.db_client.execute_query(check_query, [id_reporte])
            
            if not check_result.get('success') or not check_result.get('results'):
                return json.dumps({"success": False, "message": "Reporte no encontrado"})
            
            # Eliminar reporte
            delete_query = "DELETE FROM REPORTE WHERE id_reporte = ?"
            result = self.db_client.execute_query(delete_query, [id_reporte])
            
            if result.get('success'):
                self.logger.info(f"🛡️ Reporte {id_reporte} eliminado por moderador {user_payload.get('email')}")
                return json.dumps({
                    "success": True,
                    "message": "Reporte eliminado exitosamente por moderador"
                })
            else:
                return json.dumps({"success": False, "message": f"Error eliminando reporte: {result.get('error')}"})
                
        except Exception as e:
            self.logger.error(f"Error en admin_delete_report: {e}")
            return json.dumps({"success": False, "message": f"Error interno: {str(e)}"})

    def service_info(self, *args) -> str:
        """Método abstracto requerido por SOAServiceBase"""
        info_data = {
            "service": "reprt",
            "description": "Servicio de gestión de reportes",
            "version": "1.0.0",
            "database": "Cloudflare D1 (remota)",
            "table": "REPORTE",
            "authentication": "JWT Token required",
            "port": self.port,
            "host": self.host,
            "methods": list(self.methods.keys()) if hasattr(self, 'methods') else [],
            "dependencies": ["auth", "post", "comm"],
            "permissions": {
                "estudiante": ["create_report", "list_my_reports", "delete_report (own)"],
                "moderador": ["all student permissions", "get_report", "list_reports", "update_report_status", "admin_delete_report"]
            },
            "content_types": ["post", "comentario"],
            "report_states": ["pendiente", "revisado", "resuelto", "descartado"]
        }
        return json.dumps(info_data)

def main():
    try:
        service = ReportService(host='localhost', port=8009)
        
        print(f"📋 Iniciando servicio de reportes...")
        service.start_service()
        
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo servicio de reportes...")

if __name__ == "__main__":
    main() 