import socket
import logging
from typing import Dict, Any
from soa_protocol import SOAProtocol

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('SOA_Client')

class SOAClient:
    def __init__(self, soa_server_host: str = 'localhost', soa_server_port: int = 8000):
        self.soa_server_host = soa_server_host
        self.soa_server_port = soa_server_port
    
    def _send_request(self, message: str) -> Dict[str, Any]:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.soa_server_host, self.soa_server_port))
            
            logger.info(f"Enviando: {message}")
            sock.send(message.encode('utf-8'))
            
            response_data = sock.recv(4096)
            response_str = response_data.decode('utf-8')
            logger.info(f"Recibido: {response_str}")
            
            response = SOAProtocol.parse_response(response_str)
            
            sock.close()
            return response
            
        except Exception as e:
            logger.error(f"Error enviando petición: {e}")
            return {
                "status": "error",
                "message": f"Connection error: {str(e)}"
            }
    
    def call_service(self, service_name: str, method: str, params_str: str = "") -> Dict[str, Any]:
        message = SOAProtocol.create_request(service_name, method, params_str)
        return self._send_request(message)
    
    def list_services(self) -> None:
        print("\n" + "="*60)
        print("SERVICIOS SOA DISPONIBLES")
        print("="*60)
        print("Descubrimiento de servicios deshabilitado.")
        print("Servicios conocidos:")
        print("  📋 calc - Servicio de calculadora (operaciones básicas)")
        print("     Métodos: add, subtract, multiply, divide")
    
    def get_service_methods(self, service_name: str) -> None:
        print(f"\n" + "="*60)
        print(f"MÉTODOS DEL SERVICIO: {service_name.upper()}")
        print("="*60)
        
        # Intentar obtener métodos llamando al método 'info' si existe
        methods_response = self.call_service(service_name, 'info', '')
        
        if methods_response.get('status') == 'success':
            result_str = methods_response.get('result', '')
            print(f"\n📋 Información del servicio:")
            print(f"   {result_str}")
        else:
            print(f"No se pudo obtener información de métodos: {methods_response.get('message', 'Unknown error')}")
    
    def interactive_mode(self):
        print("\n" + "="*60)
        print("🚀 CLIENTE SOA INTERACTIVO")
        print("="*60)
        print("Usando protocolo NNNNNSSSSSDATOS (SIN JSON)")
        print("="*60)
        print("Comandos disponibles:")
        print("  list - Lista servicios conocidos")
        print("  methods <servicio> - Métodos de un servicio")
        print("  call <servicio> <método> [parámetros] - Llama a un método")
        print("  quit - Salir")
        print("="*60)
        print("Ejemplos:")
        print("  call calc add 10 5")
        print("  call calc subtract 15 8")
        print("  call calc multiply 3 7")
        print("  call calc divide 20 4")
        print("="*60)
        
        while True:
            try:
                command = input("\n🎯 SOA> ").strip()
                
                if not command:
                    continue
                
                parts = command.split()
                cmd = parts[0].lower()
                
                if cmd == 'quit' or cmd == 'exit':
                    print("👋 ¡Hasta luego!")
                    break
                
                elif cmd == 'list':
                    self.list_services()
                
                elif cmd == 'methods' and len(parts) >= 2:
                    service_name = parts[1]
                    self.get_service_methods(service_name)
                
                elif cmd == 'call' and len(parts) >= 3:
                    service_name = parts[1]
                    method_name = parts[2]
                    
                    # Parámetros como string simple
                    params_str = ' '.join(parts[3:]) if len(parts) > 3 else ""
                    
                    print(f"\n🔄 Llamando {service_name}.{method_name}({params_str})...")
                    response = self.call_service(service_name, method_name, params_str)
                    
                    if response.get('status') == 'success':
                        result = response.get('result', '')
                        print(f"✅ Resultado: {result}")
                    else:
                        print(f"❌ Error: {response.get('message', 'Unknown error')}")
                
                else:
                    print("❌ Comando no reconocido. Use 'list', 'methods <servicio>', 'call <servicio> <método> [params]', o 'quit'")
            
            except KeyboardInterrupt:
                print("\n👋 ¡Hasta luego!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

def run_demo():
    client = SOAClient()
    
    print("\n" + "="*60)
    print("🚀 DEMOSTRACIÓN CLIENTE SOA")
    print("="*60)
    print("Usando protocolo NNNNNSSSSSDATOS (SIN JSON)")
    print("="*60)
    
    # Listar servicios conocidos
    print("\n1. 📋 Servicios conocidos...")
    client.list_services()
    
    # Probar servicio de calculadora
    print("\n2. 🧮 Probando servicio de calculadora...")
    calc_tests = [
        ("add", "10 5"),
        ("subtract", "15 8"),
        ("multiply", "7 8"),
        ("divide", "20 4")
    ]
    
    for method, params in calc_tests:
        response = client.call_service("calc", method, params)
        if response.get('status') == 'success':
            result = response.get('result', '')
            print(f"   ✅ {method}({params}) = {result}")
        else:
            print(f"   ❌ Error en {method}: {response.get('message')}")

def main():
    import sys
    
    client = SOAClient()
    
    if len(sys.argv) > 1 and sys.argv[1] == 'demo':
        run_demo()
    else:
        client.interactive_mode()

if __name__ == "__main__":
    main()
