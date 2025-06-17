import json
import serial
import re
import sys
import threading
import time
from typing import Dict, Any, Optional

class BalanzaReader:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, config_path: str = "configuracion.json"):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(BalanzaReader, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, config_path: str = "configuracion.json"):
        if self._initialized:
            return
            
        self.config_path = config_path
        self.config = self.load_config()
        self.ser = None
        self.buffer = ""
        self.peso_anterior = None
        self.peso_actual = None
        self._reading_thread = None
        self._stop_reading = False
        self._data_lock = threading.Lock()
        self._connected = False
        self._balanza_actual = None
        self._last_data_time = None
        self._initialized = True
        
    def load_config(self) -> Dict[str, Any]:
        """Carga la configuración desde el archivo JSON"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        except FileNotFoundError:
            print(f"Error: No se encontró el archivo {self.config_path}")
            self.create_default_config()
            print(f"Se creó un archivo de configuración por defecto: {self.config_path}")
            return self.load_config()
        except json.JSONDecodeError as e:
            print(f"Error al leer el archivo JSON: {e}")
            sys.exit(1)
    
    def create_default_config(self):
        """Crea un archivo de configuración por defecto"""
        default_config = {
            "balanzas": {
                "balanza1": {
                    "nombre": "Balanza Principal",
                    "puerto": "COM1",
                    "baudrate": 9600,
                    "bytesize": 8,
                    "parity": "none",
                    "stopbits": 1,
                    "timeout": 1,
                    "xonxoff": False,
                    "rtscts": False,
                    "dsrdtr": False,
                    "dtr": True,
                    "rts": True,
                    "unidad": "kg"
                },
                "balanza2": {
                    "nombre": "Balanza Secundaria",
                    "puerto": "COM2",
                    "baudrate": 9600,
                    "bytesize": 8,
                    "parity": "none",
                    "stopbits": 1,
                    "timeout": 1,
                    "xonxoff": False,
                    "rtscts": False,
                    "dsrdtr": False,
                    "dtr": True,
                    "rts": True,
                    "unidad": "kg"
                }
            }
        }
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=4, ensure_ascii=False)
    
    def get_balanzas_disponibles(self):
        """Devuelve un diccionario con las balanzas disponibles {key: nombre}"""
        balanzas = {}
        for key, balanza in self.config["balanzas"].items():
            balanzas[key] = balanza.get("nombre", key)
        return balanzas
    
    def get_parity(self, parity_str: str):
        """Convierte la paridad de string a constante de pyserial"""
        parity_map = {
            "none": serial.PARITY_NONE,
            "even": serial.PARITY_EVEN,
            "odd": serial.PARITY_ODD,
            "mark": serial.PARITY_MARK,
            "space": serial.PARITY_SPACE
        }
        return parity_map.get(parity_str.lower(), serial.PARITY_NONE)
    
    def conectar(self, balanza_key: str) -> bool:
        """Conecta a la balanza seleccionada (solo si no está ya conectada)"""
        # Si ya está conectada a la misma balanza, no hacer nada
        if self._connected and self._balanza_actual == balanza_key:
            print(f"✓ Ya conectado a {self.config['balanzas'][balanza_key]['nombre']}")
            return True
        
        # Si está conectada a otra balanza, desconectar primero
        if self._connected:
            print(f"Cambiando de {self._balanza_actual} a {balanza_key}...")
            self._desconectar_internal()
        
        if balanza_key not in self.config["balanzas"]:
            print(f"Error: Balanza '{balanza_key}' no encontrada en la configuración")
            return False
            
        balanza_config = self.config["balanzas"][balanza_key]
        
        try:
            print(f"Conectando a {balanza_config['nombre']} en {balanza_config['puerto']}...")
            
            self.ser = serial.Serial(
                port=balanza_config["puerto"],
                baudrate=balanza_config["baudrate"],
                bytesize=balanza_config["bytesize"],
                parity=self.get_parity(balanza_config["parity"]),
                stopbits=balanza_config["stopbits"],
                timeout=balanza_config["timeout"],
                xonxoff=balanza_config["xonxoff"],
                rtscts=balanza_config["rtscts"],
                dsrdtr=balanza_config["dsrdtr"]
            )
            
            # Verificar que la conexión se abrió correctamente
            if not self.ser.is_open:
                print("Error: No se pudo abrir el puerto serial")
                return False
            
            # Configurar DTR y RTS si están especificados
            if balanza_config.get("dtr"):
                self.ser.setDTR(True)
            if balanza_config.get("rts"):
                self.ser.setRTS(True)
            
            # Limpiar variables
            with self._data_lock:
                self.buffer = ""
                self.peso_actual = None
                self.peso_anterior = None
                self._last_data_time = time.time()
            
            # Iniciar el hilo de lectura continua
            self._start_reading_thread()
            
            self._connected = True
            self._balanza_actual = balanza_key
            
            print(f"✓ Conectado exitosamente a {balanza_config['nombre']}")
            return True
            
        except serial.SerialException as e:
            print(f"✗ Error al conectar con la balanza: {e}")
            self.ser = None
            return False
        except Exception as e:
            print(f"✗ Error inesperado al conectar: {e}")
            self.ser = None
            return False
    
    def _start_reading_thread(self):
        """Inicia el hilo de lectura continua en segundo plano"""
        self._stop_reading = False
        self._reading_thread = threading.Thread(target=self._read_continuously, daemon=True)
        self._reading_thread.start()
        print("✓ Hilo de lectura iniciado")
    
    def _read_continuously(self):
        """Función que se ejecuta en un hilo separado para leer continuamente"""
        print("🔄 Iniciando lectura continua...")
        
        while not self._stop_reading and self.ser and self.ser.is_open:
            try:
                if self.ser.in_waiting:
                    byte = self.ser.read().decode('ascii', errors='ignore')
                    if byte in ['\r', '\n']:  # Detectar fin de línea
                        if self.buffer.strip():
                            nuevo_peso = self.extraer_peso(self.buffer.strip())
                            if nuevo_peso is not None:
                                with self._data_lock:
                                    self.peso_actual = nuevo_peso
                                    self._last_data_time = time.time()
                                    # Debug: mostrar datos recibidos
                                    print(f"📊 Peso recibido: {nuevo_peso} kg")
                        self.buffer = ""
                    else:
                        self.buffer += byte
                else:
                    time.sleep(0.01)  # Pequeña pausa para no saturar la CPU
                    
                # Verificar si llevamos mucho tiempo sin datos (posible desconexión)
                if self._last_data_time and time.time() - self._last_data_time > 30:
                    print("⚠ Warning: No se han recibido datos en 30 segundos")
                    self._last_data_time = time.time()  # Reset warning
                    
            except Exception as e:
                print(f"💥 Error en lectura continua: {e}")
                print("🔄 Intentando recuperar conexión...")
                time.sleep(1)
                # No break - intentar continuar
        
        print("🛑 Hilo de lectura terminado")
    
    def _desconectar_internal(self):
        """Desconecta internamente sin resetear el singleton"""
        # Detener el hilo de lectura
        if hasattr(self, '_stop_reading'):
            self._stop_reading = True
            
        if hasattr(self, '_reading_thread') and self._reading_thread and self._reading_thread.is_alive():
            self._reading_thread.join(timeout=2.0)
        
        # Cerrar la conexión serial
        if self.ser and self.ser.is_open:
            try:
                self.ser.close()
                print("🔌 Conexión cerrada")
            except Exception as e:
                print(f"Error al cerrar conexión: {e}")
            finally:
                self.ser = None
        
        self._connected = False
        self._balanza_actual = None
    
    def desconectar(self):
        """Desconecta de la balanza"""
        self._desconectar_internal()
        # Reset de variables
        with self._data_lock:
            self.buffer = ""
            self.peso_actual = None
            self.peso_anterior = None
    
    def extraer_peso(self, texto: str) -> Optional[float]:
        """Extrae el valor numérico del peso del texto recibido"""
        # Buscar números con posibles decimales
        match = re.search(r'[-+]?\d*\.?\d+', texto)
        if match:
            try:
                return float(match.group())
            except ValueError:
                return None
        return None
    
    def leer_peso(self) -> Optional[float]:
        """Lee el peso actual de la balanza"""
        if not self._connected:
            return None
        
        with self._data_lock:
            return self.peso_actual
    
    def esta_conectado(self) -> bool:
        """Verifica si está conectado a una balanza"""
        return self._connected and self.ser and self.ser.is_open
    
    def get_status(self) -> Dict[str, Any]:
        """Devuelve el estado actual de la conexión"""
        return {
            "conectado": self._connected,
            "balanza_actual": self._balanza_actual,
            "peso_actual": self.leer_peso(),
            "ultimo_dato": self._last_data_time.strftime("%H:%M:%S") if self._last_data_time else None,
            "hilo_activo": self._reading_thread and self._reading_thread.is_alive() if hasattr(self, '_reading_thread') else False
        }
    
    def reiniciar_conexion(self):
        """Reinicia la conexión actual (útil en caso de error)"""
        if self._balanza_actual:
            balanza_key = self._balanza_actual
            print("🔄 Reiniciando conexión...")
            self._desconectar_internal()
            time.sleep(1)
            return self.conectar(balanza_key)
        return False

# Funciones globales para facilitar el uso
_reader_instance = None

def inicializar_balanza(balanza_key: str = "balanza1", config_path: str = "configuracion.json") -> bool:
    """Inicializa la conexión con la balanza (solo se hace una vez)"""
    global _reader_instance
    _reader_instance = BalanzaReader(config_path)
    return _reader_instance.conectar(balanza_key)

def obtener_peso() -> Optional[float]:
    """Obtiene el peso actual (función simple para usar desde cualquier parte)"""
    global _reader_instance
    if _reader_instance is None:
        print("⚠ Balanza no inicializada. Llama a inicializar_balanza() primero.")
        return None
    return _reader_instance.leer_peso()

def get_status_balanza() -> Dict[str, Any]:
    """Obtiene el estado de la balanza"""
    global _reader_instance
    if _reader_instance is None:
        return {"error": "Balanza no inicializada"}
    return _reader_instance.get_status()

def cerrar_balanza():
    """Cierra la conexión con la balanza"""
    global _reader_instance
    if _reader_instance:
        _reader_instance.desconectar()

# Para pruebas directas
if __name__ == "__main__":
    print("=== Test de Balanza Persistente ===")
    
    # Inicializar
    if inicializar_balanza("balanza1"):
        print("✓ Balanza inicializada correctamente")
        
        try:
            # Loop principal
            peso_anterior = None
            contador = 0
            
            while True:
                peso = obtener_peso()
                status = get_status_balanza()
                
                # Mostrar peso solo si cambió
                if peso != peso_anterior and peso is not None:
                    print(f"📊 Peso: {peso} kg")
                    peso_anterior = peso
                
                # Mostrar status cada 10 iteraciones
                contador += 1
                if contador % 20 == 0:
                    print(f"📈 Status: {status}")
                
                time.sleep(0.5)
                
        except KeyboardInterrupt:
            print("\n🛑 Finalizando...")
        finally:
            cerrar_balanza()
    else:
        print("✗ No se pudo inicializar la balanza")