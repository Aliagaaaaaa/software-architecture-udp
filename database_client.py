import requests
import json
import logging
from typing import Dict, Any, List, Optional, Union

logger = logging.getLogger(__name__)

class DatabaseClient:
    """Cliente para interactuar con la base de datos a través del proxy HTTP de Cloudflare D1"""
    
    def __init__(self, proxy_url: str = "https://d1-database-proxy.maliagapacheco.workers.dev/query"):
        self.proxy_url = proxy_url
        self.timeout = 30  # timeout en segundos
        
    def execute_query(self, sql: str, params: List[Any] = None) -> Dict[str, Any]:
        """
        Ejecuta una consulta SQL a través del proxy HTTP
        
        Args:
            sql: La consulta SQL a ejecutar
            params: Lista de parámetros para la consulta (opcional)
            
        Returns:
            Dict con el resultado de la consulta
        """
        try:
            # El proxy espera 'query' en lugar de 'sql'
            payload = {
                "query": sql,
                "params": params or []
            }
            
            logger.debug(f"Ejecutando consulta: {sql} con parámetros: {params}")
            
            response = requests.post(
                self.proxy_url,
                json=payload,
                timeout=self.timeout,
                headers={
                    'Content-Type': 'application/json'
                }
            )
            
            response.raise_for_status()
            result = response.json()
            
            logger.debug(f"Respuesta de BD: {result}")
            
            # Normalizar la respuesta para que sea compatible con el resto del código
            if result.get("success"):
                # El proxy devuelve 'data' pero nuestro código espera 'results'
                normalized_result = {
                    "success": True,
                    "results": result.get("data", []),
                    "meta": result.get("meta", {})
                }
                return normalized_result
            else:
                return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de red ejecutando consulta: {e}")
            return {
                "success": False,
                "error": f"Network error: {str(e)}"
            }
        except json.JSONDecodeError as e:
            logger.error(f"Error decodificando respuesta JSON: {e}")
            return {
                "success": False,
                "error": f"JSON decode error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Error inesperado ejecutando consulta: {e}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    def fetch_one(self, sql: str, params: List[Any] = None) -> Optional[Dict[str, Any]]:
        """
        Ejecuta una consulta y devuelve un solo resultado
        
        Returns:
            Dict con una fila de resultado o None si no hay resultados
        """
        result = self.execute_query(sql, params)
        
        if not result.get("success", False):
            logger.error(f"Error en consulta fetch_one: {result.get('error')}")
            return None
            
        results = result.get("results", [])
        if results:
            return results[0]
        return None
    
    def fetch_all(self, sql: str, params: List[Any] = None) -> List[Dict[str, Any]]:
        """
        Ejecuta una consulta y devuelve todos los resultados
        
        Returns:
            Lista de diccionarios con los resultados
        """
        result = self.execute_query(sql, params)
        
        if not result.get("success", False):
            logger.error(f"Error en consulta fetch_all: {result.get('error')}")
            return []
            
        return result.get("results", [])
    
    def execute_update(self, sql: str, params: List[Any] = None) -> Dict[str, Any]:
        """
        Ejecuta una consulta de actualización (INSERT, UPDATE, DELETE)
        
        Returns:
            Dict con información sobre la operación (success, changes, last_row_id)
        """
        result = self.execute_query(sql, params)
        
        if not result.get("success", False):
            logger.error(f"Error en execute_update: {result.get('error')}")
            return {
                "success": False,
                "error": result.get("error"),
                "changes": 0,
                "last_row_id": None
            }
        
        # Extraer metadatos del resultado
        meta = result.get("meta", {})
        
        return {
            "success": True,
            "changes": meta.get("rows_written", 0),
            "last_row_id": meta.get("last_row_id")
        }
    
    def init_auth_tables(self) -> bool:
        """Inicializa las tablas necesarias para el servicio de autenticación"""
        try:
            # Tabla USUARIO
            sql = '''
                CREATE TABLE IF NOT EXISTS USUARIO (
                    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    rol TEXT NOT NULL DEFAULT 'estudiante' CHECK (rol IN ('estudiante', 'moderador')),
                    password TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT,
                    is_active BOOLEAN DEFAULT 1
                )
            '''
            result = self.execute_query(sql)
            if not result.get("success", False):
                logger.error(f"Error creando tabla USUARIO: {result.get('error')}")
                return False
            
            # Índices
            indices = [
                'CREATE INDEX IF NOT EXISTS idx_email ON USUARIO(email)',
                'CREATE INDEX IF NOT EXISTS idx_rol ON USUARIO(rol)'
            ]
            
            for idx_sql in indices:
                result = self.execute_query(idx_sql)
                if not result.get("success", False):
                    logger.warning(f"Error creando índice: {result.get('error')}")
            
            logger.info("Tablas de autenticación inicializadas correctamente")
            return True
            
        except Exception as e:
            logger.error(f"Error inicializando tablas de autenticación: {e}")
            return False
    
    def init_profile_tables(self) -> bool:
        """Inicializa las tablas necesarias para el servicio de perfiles"""
        try:
            # Tabla PERFIL
            sql = '''
                CREATE TABLE IF NOT EXISTS PERFIL (
                    id_perfil INTEGER PRIMARY KEY AUTOINCREMENT,
                    avatar TEXT DEFAULT NULL,
                    biografia TEXT DEFAULT NULL,
                    id_usuario INTEGER UNIQUE NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT,
                    FOREIGN KEY (id_usuario) REFERENCES USUARIO(id_usuario)
                )
            '''
            result = self.execute_query(sql)
            if not result.get("success", False):
                logger.error(f"Error creando tabla PERFIL: {result.get('error')}")
                return False
            
            # Índices
            indices = [
                'CREATE INDEX IF NOT EXISTS idx_id_usuario ON PERFIL(id_usuario)',
                'CREATE INDEX IF NOT EXISTS idx_avatar ON PERFIL(avatar)'
            ]
            
            for idx_sql in indices:
                result = self.execute_query(idx_sql)
                if not result.get("success", False):
                    logger.warning(f"Error creando índice: {result.get('error')}")
            
            logger.info("Tablas de perfiles inicializadas correctamente")
            return True
            
        except Exception as e:
            logger.error(f"Error inicializando tablas de perfiles: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Prueba la conexión a la base de datos"""
        try:
            result = self.execute_query("SELECT 1 as test")
            return result.get("success", False)
        except Exception as e:
            logger.error(f"Error probando conexión: {e}")
            return False 