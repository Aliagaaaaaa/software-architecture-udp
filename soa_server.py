import socket
import threading
import logging
import time
from typing import Dict, Any
from soa_protocol import SOAProtocol

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('SOA_Server')

class SOAServer:
    def __init__(self, host: str = 'localhost', port: int = 8000):
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        
        self.services_registry: Dict[str, Dict[str, Any]] = {}
        self.registry_lock = threading.Lock()
        
        logger.info(f"Servidor SOA inicializado en {host}:{port}")
        logger.info("Usando protocolo NNNNNSSSSSDATOS (SIN JSON)")
    
    def start_server(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            self.running = True
            
            logger.info(f"Servidor SOA iniciado en {self.host}:{self.port}")
            logger.info("Esperando conexiones...")
            
            while self.running:
                try:
                    client_socket, address = self.socket.accept()
                    logger.info(f"Nueva conexión desde {address}")
                    
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_socket, address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except socket.error as e:
                    if self.running:
                        logger.error(f"Error aceptando conexión: {e}")
                        
        except Exception as e:
            logger.error(f"Error iniciando servidor: {e}")
        finally:
            self.stop_server()
    
    def _handle_client(self, client_socket: socket.socket, address):
        try:
            data = client_socket.recv(4096)
            if not data:
                return
            
            try:
                
                message_str = data.decode('utf-8')
                logger.info(f"Mensaje raw recibido: {message_str}")
                
                
                message = SOAProtocol.parse_request(message_str)
                logger.info(f"Mensaje parseado: {message}")
                
                
                response = self.process_request(message)
                
                
                if response.get('status') == 'success':
                    if message.get('action') == 'call_service':
                        
                        service_name = message.get('service_name', 'unknw')
                        result_str = str(response.get('result', ''))
                        response_msg = SOAProtocol.create_response(service_name, True, result_str)
                    else:
                        
                        response_msg = SOAProtocol.create_response("srvr", True, str(response.get('result', 'OK')))
                else:
                    
                    service_name = message.get('service_name', 'srvr')
                    error_msg = response.get('message', 'Error desconocido')
                    response_msg = SOAProtocol.create_response(service_name, False, error_msg=error_msg)
                
                logger.info(f"Enviando respuesta: {response_msg}")
                client_socket.send(response_msg.encode('utf-8'))
                
            except Exception as e:
                logger.error(f"Error procesando petición: {e}")
                error_response = SOAProtocol.create_response("srvr", False, error_msg=f"Server error: {str(e)}")
                client_socket.send(error_response.encode('utf-8'))
                
        except ConnectionResetError:
            logger.info(f"Cliente {address} desconectado")
        except Exception as e:
            logger.error(f"Error manejando cliente {address}: {e}")
        finally:
            client_socket.close()
    
    def process_request(self, message: Dict[str, Any]) -> Dict[str, Any]:
        action = message.get('action')
        
        if action == 'register_service':
            return self.register_service(message)
        elif action == 'unregister_service':
            return self.unregister_service(message)
        elif action == 'call_service':
            return self.call_service(message)
        else:
            return {
                "status": "error",
                "message": f"Unknown action: {action}"
            }
    
    def register_service(self, message: Dict[str, Any]) -> Dict[str, Any]:
        try:
            service_name = message.get('service_name')
            service_host = message.get('service_host')
            service_port = message.get('service_port')
            description = message.get('description', '')
            
            if not all([service_name, service_host, service_port]):
                return {
                    "status": "error",
                    "message": "Missing required fields: service_name, service_host, service_port"
                }
            
            with self.registry_lock:
                self.services_registry[service_name] = {
                    "host": service_host,
                    "port": service_port,
                    "description": description,
                    "registered_at": time.time()
                }
            
            logger.info(f"Servicio registrado: {service_name} en {service_host}:{service_port}")
            return {
                "status": "success",
                "result": f"Service {service_name} registered successfully"
            }
            
        except Exception as e:
            logger.error(f"Error registrando servicio: {e}")
            return {
                "status": "error",
                "message": f"Registration error: {str(e)}"
            }
    
    def unregister_service(self, message: Dict[str, Any]) -> Dict[str, Any]:
        try:
            service_name = message.get('service_name')
            
            if not service_name:
                return {
                    "status": "error",
                    "message": "Missing service_name"
                }
            
            with self.registry_lock:
                if service_name in self.services_registry:
                    del self.services_registry[service_name]
                    logger.info(f"Servicio desregistrado: {service_name}")
                    return {
                        "status": "success",
                        "result": f"Service {service_name} unregistered successfully"
                    }
                else:
                    return {
                        "status": "error",
                        "message": f"Service {service_name} not found"
                    }
                    
        except Exception as e:
            logger.error(f"Error desregistrando servicio: {e}")
            return {
                "status": "error",
                "message": f"Unregistration error: {str(e)}"
            }
    
    def call_service(self, message: Dict[str, Any]) -> Dict[str, Any]:
        try:
            service_name = message.get('service_name')
            method = message.get('method')
            params = message.get('params', '')
            
            if not all([service_name, method]):
                return {
                    "status": "error",
                    "message": "Missing required fields: service_name, method"
                }
            
            
            with self.registry_lock:
                if service_name not in self.services_registry:
                    return {
                        "status": "error",
                        "message": f"Service {service_name} not found"
                    }
                
                service_info = self.services_registry[service_name]
            
            
            service_host = service_info['host']
            service_port = service_info['port']
            
            service_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            service_socket.connect((service_host, service_port))
            
            
            service_request = SOAProtocol.create_request(service_name, method, params)
            service_socket.send(service_request.encode('utf-8'))
            
            
            response_data = service_socket.recv(4096)
            response_str = response_data.decode('utf-8')
            
            service_socket.close()
            
            
            service_response = SOAProtocol.parse_response(response_str)
            
            if service_response.get('status') == 'success':
                return {
                    "status": "success",
                    "result": service_response.get('result', '')
                }
            else:
                return {
                    "status": "error",
                    "message": service_response.get('message', 'Service error')
                }
                
        except Exception as e:
            logger.error(f"Error llamando servicio {service_name}: {e}")
            return {
                "status": "error",
                "message": f"Service call error: {str(e)}"
            }
    
    def stop_server(self):
        self.running = False
        if self.socket:
            self.socket.close()
        logger.info("Servidor SOA detenido")

def main():
    server = SOAServer(host='localhost', port=8000)
    
    try:
        server.start_server()
    except KeyboardInterrupt:
        logger.info("Deteniendo servidor...")
        server.stop_server()

if __name__ == "__main__":
    main()
