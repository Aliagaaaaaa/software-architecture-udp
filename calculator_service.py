from typing import Dict, Any
from soa_service_base import SOAServiceBase

class CalculatorService(SOAServiceBase):
    def __init__(self, host: str = 'localhost', port: int = 0):
        super().__init__(
            service_name="calc",
            host=host,
            port=port,
            description="Servicio de cálculos matemáticos básicos"
        )
    
    def service_info(self) -> Dict[str, Any]:
        return {
            "service_name": self.service_name,
            "description": self.description,
            "version": "1.0.0",
            "methods": self.get_available_methods(),
            "status": "running" if self.running else "stopped"
        }
    
    def service_add(self, a: float, b: float) -> float:
        return a + b
    
    def service_subtract(self, a: float, b: float) -> float:
        return a - b
    
    def service_multiply(self, a: float, b: float) -> float:
        return a * b
    
    def service_divide(self, a: float, b: float) -> float:
        if b == 0:
            raise ValueError("División por cero no permitida")
        return a / b

def main():
    service = CalculatorService(host='localhost', port=8001)
    
    try:
        print(f"Iniciando servicio de calculadora...")
        print(f"Nombre del servicio: '{service.service_name}' (protocolo NNNNNSSSSSDATOS)")
        service.start_service()
    except KeyboardInterrupt:
        print("\nDeteniendo servicio de calculadora...")
        service.stop_service()

if __name__ == "__main__":
    main()
