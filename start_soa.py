import subprocess
import time
import sys
import signal
import os
from typing import List

class SOALauncher:
    def __init__(self):
        self.processes: List[subprocess.Popen] = []

    def start_server(self):
        print("🚀 Iniciando servidor SOA principal...")
        try:
            process = subprocess.Popen([
                sys.executable, "soa_server.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.processes.append(process)
            time.sleep(2)  
            print("✅ Servidor SOA iniciado")
            return True
        except Exception as e:
            print(f"❌ Error iniciando servidor SOA: {e}")
            return False
            
    def start_services(self):
        services = [
            ("calculator_service.py", "Servicio de Calculadora")
        ]
        
        for service_file, service_name in services:
            print(f"🔧 Iniciando {service_name}...")
            try:
                process = subprocess.Popen([
                    sys.executable, service_file
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.processes.append(process)
                time.sleep(1)  
                print(f"✅ {service_name} iniciado")
            except Exception as e:
                print(f"❌ Error iniciando {service_name}: {e}")
    def start_client(self, demo_mode: bool = False):
        print("\n🎯 Iniciando cliente SOA...")
        try:
            if demo_mode:
                process = subprocess.Popen([
                    sys.executable, "soa_client.py", "demo"
                ])
            else:
                process = subprocess.Popen([
                    sys.executable, "soa_client.py"
                ])
            process.wait()  
        except Exception as e:
            print(f"❌ Error iniciando cliente SOA: {e}")
    
    def stop_all(self):
        print("\n🛑 Deteniendo todos los servicios...")
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            except Exception:
                pass
        print("✅ Todos los servicios detenidos")
    
    def run_full_demo(self):
        print("="*60)
        print("🎬 DEMOSTRACIÓN COMPLETA SOA")
        print("="*60)
        print("Esta demostración:")
        print("1. Iniciará el servidor SOA")
        print("2. Registrará servicios de ejemplo")
        print("3. Ejecutará pruebas automáticas")
        print("4. Mostrará el cliente interactivo")
        print("="*60)
        
        try:
            
            if not self.start_server():
                return
            
            
            self.start_services()
            
            
            print("\n🎬 Ejecutando demostración automática...")
            time.sleep(2)
            self.start_client(demo_mode=True)
            
            
            print("\n" + "="*60)
            choice = input("¿Desea continuar con el modo interactivo? (y/n): ").lower()
            if choice in ['y', 'yes', 's', 'si']:
                self.start_client(demo_mode=False)
                
        except KeyboardInterrupt:
            print("\n👋 Demostración interrumpida por el usuario")
        finally:
            self.stop_all()
    
    def run_interactive(self):
        print("="*60)
        print("🎯 MODO INTERACTIVO SOA")
        print("="*60)
        
        try:
            
            if not self.start_server():
                return
            
            
            self.start_services()
            
            
            print("\n⏳ Esperando que todos los servicios se registren...")
            time.sleep(3)
            
            
            self.start_client(demo_mode=False)
                
        except KeyboardInterrupt:
            print("\n👋 Sesión interrumpida por el usuario")
        finally:
            self.stop_all()

def signal_handler(sig, frame):
    print("\n🛑 Recibida señal de interrupción...")
    sys.exit(0)

def main():
    
    signal.signal(signal.SIGINT, signal_handler)
    
    launcher = SOALauncher()
    
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--demo':
            launcher.run_full_demo()
        elif sys.argv[1] == '--interactive':
            launcher.run_interactive()
        elif sys.argv[1] == '--help':
            print("Uso del launcher SOA:")
            print("  python start_soa.py                 - Modo interactivo (por defecto)")
            print("  python start_soa.py --demo          - Demostración completa")
            print("  python start_soa.py --interactive   - Solo modo interactivo")
            print("  python start_soa.py --help          - Mostrar esta ayuda")
        else:
            print(f"Argumento no reconocido: {sys.argv[1]}")
            print("Use --help para ver las opciones disponibles")
    else:
        
        launcher.run_interactive()

if __name__ == "__main__":
    main() 