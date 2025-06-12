import os
import socket
import threading
import logging
import time
from typing import Dict, Any, Callable, Optional
from abc import ABC, abstractmethod
from soa_protocol import SOAProtocol


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class SOAServiceBase(ABC):
    def __init__(self, service_name: str, host: str = 'localhost', port: int = 0, 
                 description: str = "", soa_server_host: str = 'localhost', 
                 soa_server_port: int = 8000):
        self.service_name = service_name
        
        # Auto-detect Docker environment and use container hostname
        if self._is_running_in_docker():
            # Use container hostname for service registration
            self.host = socket.gethostname()
            self.logger = logging.getLogger(f'SOA_Service_{service_name}')
            self.logger.info(f"Docker detected - using container hostname: {self.host}")
        else:
            self.host = host
            self.logger = logging.getLogger(f'SOA_Service_{service_name}')
        
        self.port = port
        self.description = description
        
        # Use environment variables if available, otherwise use defaults
        self.soa_server_host = os.getenv('SOA_SERVER_HOST', soa_server_host)
        self.soa_server_port = int(os.getenv('SOA_SERVER_PORT', soa_server_port))
        
        
        self.socket = None
        self.running = False
        
        
        self.methods: Dict[str, Callable] = {}
        
        
        self._register_methods()
    
    def _is_running_in_docker(self) -> bool:
        """Detect if running inside a Docker container"""
        try:
            # Check for /.dockerenv file
            if os.path.exists('/.dockerenv'):
                return True
            
            # Check cgroup for docker
            with open('/proc/1/cgroup', 'r') as f:
                content = f.read()
                if 'docker' in content or 'containerd' in content:
                    return True
        except:
            pass
        
        # Check for Docker-specific environment variables
        return os.getenv('HOSTNAME') and (
            os.getenv('HOSTNAME').startswith('auth-service') or
            os.getenv('HOSTNAME').startswith('profile-service') or
            os.getenv('HOSTNAME').startswith('forum-service') or
            os.getenv('HOSTNAME').startswith('post-service') or
            os.getenv('HOSTNAME').startswith('comment-service') or
            os.getenv('HOSTNAME').startswith('event-service') or
            os.getenv('HOSTNAME').startswith('message-service') or
            os.getenv('HOSTNAME').startswith('report-service') or
            os.getenv('HOSTNAME').startswith('notification-service')
        )
    
    def _register_methods(self):
        for attr_name in dir(self):
            if attr_name.startswith('service_') and callable(getattr(self, attr_name)):
                method_name = attr_name[8:]  
                self.methods[method_name] = getattr(self, attr_name)
                self.logger.info(f"Método registrado: {method_name}")
    
    def start_service(self):
        try:
            
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # In Docker, bind to 0.0.0.0 to accept connections from other containers
            bind_host = '0.0.0.0' if self._is_running_in_docker() else self.host
            self.socket.bind((bind_host, self.port))
            
            
            if self.port == 0:
                self.port = self.socket.getsockname()[1]
            
            self.socket.listen(5)
            self.running = True
            
            self.logger.info(f"Servicio '{self.service_name}' iniciado en {bind_host}:{self.port} (registrado como {self.host}:{self.port})")
            self.logger.info("Usando protocolo NNNNNSSSSSDATOS")
            
            
            if self._register_with_soa_server():
                self.logger.info(f"Servicio registrado exitosamente en el servidor SOA")
            else:
                self.logger.warning("No se pudo registrar en el servidor SOA, pero el servicio continúa ejecutándose")
            
            
            while self.running:
                try:
                    client_socket, address = self.socket.accept()
                    self.logger.info(f"Nueva conexión desde {address}")
                    
                    
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_socket, address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except socket.error as e:
                    if self.running:
                        self.logger.error(f"Error aceptando conexión: {e}")
                        
        except Exception as e:
            self.logger.error(f"Error iniciando servicio: {e}")
        finally:
            self.stop_service()
    
    def _handle_client(self, client_socket: socket.socket, address):
        try:
            data = client_socket.recv(4096)
            if not data:
                return
            
            try:
                
                message_str = data.decode('utf-8')
                self.logger.info(f"Mensaje raw recibido: {message_str}")
                
                
                request = SOAProtocol.parse_request(message_str)
                self.logger.info(f"Petición parseada: {request}")
                
                
                response = self._process_request(request)
                
                
                if response.get('status') == 'success':
                    result_str = str(response.get('result', ''))
                    
                    if request.get('method') in ['add', 'subtract', 'multiply', 'divide']:
                        params_str = request.get('params', '')
                        if params_str and ' ' in params_str:
                            parts = params_str.split()
                            if len(parts) >= 2:
                                operation_symbols = {
                                    'add': '+',
                                    'subtract': '-', 
                                    'multiply': '*',
                                    'divide': '/'
                                }
                                symbol = operation_symbols.get(request.get('method'), '?')
                                result_str = f"{parts[0]} {symbol} {parts[1]} = {response.get('result')}"
                    
                    response_msg = SOAProtocol.create_response(self.service_name, True, result_str)
                else:
                    error_msg = response.get('message', 'Error desconocido')
                    response_msg = SOAProtocol.create_response(self.service_name, False, error_msg=error_msg)
                
                self.logger.info(f"Enviando respuesta: {response_msg}")
                client_socket.send(response_msg.encode('utf-8'))
                
            except Exception as e:
                self.logger.error(f"Error procesando petición: {e}")
                error_response = SOAProtocol.create_response(self.service_name, False, error_msg=f"Error del servicio: {str(e)}")
                client_socket.send(error_response.encode('utf-8'))
                
        except Exception as e:
            self.logger.error(f"Error manejando cliente {address}: {e}")
        finally:
            client_socket.close()
    
    def _process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
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
            
            if isinstance(params, str) and params:
                
                param_parts = params.split()
                
                converted_params = []
                for part in param_parts:
                    try:
                        
                        converted_params.append(int(part))
                    except ValueError:
                        try:
                            
                            converted_params.append(float(part))
                        except ValueError:
                            
                            converted_params.append(part)
                
                
                if len(converted_params) == 1:
                    result = self.methods[method_name](converted_params[0])
                elif len(converted_params) == 2:
                    result = self.methods[method_name](converted_params[0], converted_params[1])
                elif len(converted_params) >= 3:
                    result = self.methods[method_name](*converted_params)
                else:
                    result = self.methods[method_name]()
            else:
                
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
    
    def _register_with_soa_server(self) -> bool:
        try:
            soa_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            soa_socket.connect((self.soa_server_host, self.soa_server_port))
            
            
            registration_data = f"{self.host}:{self.port}:{self.service_name}:{self.description}"
            registration_msg = SOAProtocol.encode_message("rgstr", registration_data)
            
            soa_socket.send(registration_msg.encode('utf-8'))
            
            response_data = soa_socket.recv(4096)
            response_str = response_data.decode('utf-8')
            response = SOAProtocol.parse_response(response_str)
            
            soa_socket.close()
            
            return response.get('status') == 'success'
            
        except Exception as e:
            self.logger.error(f"Error registrándose con servidor SOA: {e}")
            return False
    
    def _unregister_from_soa_server(self) -> bool:
        try:
            soa_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            soa_socket.connect((self.soa_server_host, self.soa_server_port))
            
            
            unregistration_data = f"unregister:{self.service_name}"
            unregistration_msg = SOAProtocol.encode_message("unrgs", unregistration_data)
            
            soa_socket.send(unregistration_msg.encode('utf-8'))
            
            response_data = soa_socket.recv(4096)
            response_str = response_data.decode('utf-8')
            response = SOAProtocol.parse_response(response_str)
            
            soa_socket.close()
            
            return response.get('status') == 'success'
            
        except Exception as e:
            self.logger.error(f"Error desregistrándose del servidor SOA: {e}")
            return False
    
    def stop_service(self):
        self.running = False
        
        if self._unregister_from_soa_server():
            self.logger.info("Servicio desregistrado exitosamente del servidor SOA")
        
        if self.socket:
            self.socket.close()
        
        self.logger.info(f"Servicio '{self.service_name}' detenido")
    
    def get_available_methods(self) -> Dict[str, str]:
        methods_info = {}
        for method_name, method_func in self.methods.items():
            methods_info[method_name] = method_func.__doc__ or "Sin documentación"
        return methods_info
    
    @abstractmethod
    def service_info(self) -> Dict[str, Any]:
        pass 