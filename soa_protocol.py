from typing import Dict, Any, Tuple

class SOAProtocol:
    
    @staticmethod
    def encode_message(service_name: str, data: str, status: str = "") -> str:
        service_name = service_name[:5].ljust(5)
        content = service_name + status + data
        content_length = len(content)
        length_str = f"{content_length:05d}"
        message = length_str + content
        
        return message
    
    @staticmethod
    def decode_message(message: str) -> Tuple[str, str, str, str]:
        if len(message) < 10:
            raise ValueError("Mensaje demasiado corto")
        
        
        length_str = message[:5]
        try:
            length = int(length_str)
        except ValueError:
            raise ValueError(f"Longitud inválida: {length_str}")
        
        
        content = message[5:]
        
        
        if len(content) != length:
            raise ValueError(f"Longitud esperada {length}, pero contenido tiene {len(content)} caracteres")
        
        
        service_name = content[:5].strip()
        remaining = content[5:]
        status = ""
        data = remaining
        
        if remaining.startswith("OK") or remaining.startswith("NK"):
            status = remaining[:2]
            data = remaining[2:]
        
        return length_str, service_name, status, data
    
    @staticmethod
    def create_request(service_name: str, method: str, params_str: str = "") -> str:
        if params_str:
            data_str = f"{method} {params_str}"
        else:
            data_str = method
        
        return SOAProtocol.encode_message(service_name, data_str)
    
    @staticmethod
    def create_response(service_name: str, success: bool, result: Any = None, error_msg: str = "") -> str:
        status = "OK" if success else "NK"
        
        if success:
            data_str = str(result) if result is not None else ""
        else:
            data_str = error_msg
        
        return SOAProtocol.encode_message(service_name, data_str, status)
    
    @staticmethod
    def create_register_request(service_name: str, host: str, port: int, description: str = "") -> str:
        data = f"{host}:{port}:{service_name}:{description}"
        return SOAProtocol.encode_message("rgstr", data)
    
    @staticmethod
    def parse_request(message: str) -> Dict[str, Any]:
        try:
            length, service_name, status, data = SOAProtocol.decode_message(message)
            
            
            if service_name == "rgstr":
                
                parts = data.split(":", 3)
                if len(parts) >= 3:
                    return {
                        "action": "register_service",
                        "service_name": parts[2],
                        "service_host": parts[0],
                        "service_port": int(parts[1]),
                        "description": parts[3] if len(parts) > 3 else ""
                    }
                else:
                    raise ValueError("Formato de registro inválido")
            elif service_name == "unrgs":
                
                if data.startswith("unregister:"):
                    service_to_unregister = data[11:]  
                    return {
                        "action": "unregister_service",
                        "service_name": service_to_unregister
                    }
                else:
                    raise ValueError("Formato de desregistro inválido")
            else:
                
                
                data_parts = data.split(" ", 1)
                method = data_parts[0] if data_parts else ""
                params_str = data_parts[1] if len(data_parts) > 1 else ""
                
                return {
                    "action": "call_service",
                    "service_name": service_name,
                    "method": method,
                    "params": params_str
                }
        
        except Exception as e:
            raise ValueError(f"Error parseando mensaje: {e}")
    
    @staticmethod
    def parse_response(message: str) -> Dict[str, Any]:
        try:
            length, service_name, status, data = SOAProtocol.decode_message(message)
            
            success = status == "OK"
            
            return {
                "status": "success" if success else "error",
                "service_name": service_name,
                "result": data if success else None,
                "message": data if not success else None
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error parsing response: {e}"
            }
