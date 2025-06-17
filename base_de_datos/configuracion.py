# Configuración del Sistema de Pesaje de Fardos
# Aquí puedes modificar fácilmente todos los parámetros del sistema

import os
import json
from typing import Dict, Any

# === CONFIGURACIÓN DE CAMPOS ===
CAMPOS_CONFIG = {
    'tara_por_fardo': 2.0,  # kg de tara por cada fardo
    'precision_decimal': 2,  # decimales para mostrar pesos
    'numero_fardo_inicial': 1,  # número inicial de fardos
}

# === CONFIGURACIÓN DE BALANZA GAMA ===
BALANZA_CONFIG = {
    'puerto_serie': 'COM1',   # Puerto serie de la balanza
    'baudrate': 9600,         # Velocidad de comunicación
    'timeout': 1,             # Timeout en segundos
    'activar_dtr': True,      # Activar DTR para la balanza
    'activar_rts': True,      # Activar RTS para la balanza
    'protocolo': 'CONTINUO',  # Protocolo de comunicación
}

# === CONFIGURACIÓN VISUAL MEJORADA ===
COLORES = {
    # Colores principales
    'primario': '#2E86AB',      # Azul principal
    'secundario': '#A23B72',    # Rosa/magenta
    'acento': '#F18F01',        # Naranja
    'exito': '#C73E1D',         # Rojo para éxito/completado
    
    # Fondos
    'fondo_principal': '#F8F9FA',
    'fondo_panel': '#FFFFFF',
    'fondo_entrada': '#FFFFFF',
    'fondo_hover': '#E3F2FD',
    'fondo_seleccion': '#BBDEFB',
    
    # Textos
    'texto_principal': '#212529',
    'texto_secundario': '#6C757D',
    'texto_blanco': '#FFFFFF',
    'texto_exito': '#155724',
    'texto_error': '#721C24',
    
    # Bordes y separadores
    'borde_principal': '#DEE2E6',
    'borde_activo': '#2E86AB',
    'sombra': '#DDDDDD',
    
    # Estados
    'activo': '#28A745',
    'inactivo': '#6C757D',
    'peligro': '#DC3545',
    'advertencia': '#FFC107',
}

FUENTES = {
    'titulo': ('Segoe UI', 16, 'bold'),
    'subtitulo': ('Segoe UI', 12, 'bold'),
    'normal': ('Segoe UI', 10),
    'pequena': ('Segoe UI', 9),
    'monospace': ('Consolas', 10),
    'grande': ('Segoe UI', 14),
    'extra_grande': ('Segoe UI', 18, 'bold'),
}

DIMENSIONES = {
    'ventana_ancho': 1200,
    'ventana_alto': 700,
    'panel_fardos_ancho': 500,
    'panel_stats_ancho': 350,
    'altura_fila_tabla': 20,
    'padding_general': 15,
    'padding_pequeno': 8,
    'radio_borde': 8,
}

# === CONFIGURACIÓN DE EXPORTACIÓN ===
EXPORTACION_CONFIG = {
    'carpeta_destino': 'exportaciones',
    'formato_fecha': '%Y%m%d_%H%M%S',
    'separador_csv': ';',
    'encoding': 'utf-8-sig',  # Para compatibilidad con Excel
}

# === MENSAJES DEL SISTEMA ===
MENSAJES = {
    'ticket_creado': 'Ticket creado exitosamente',
    'fardo_agregado': 'Fardo agregado correctamente',
    'exportacion_exitosa': 'Archivo exportado correctamente',
    'error_conexion_balanza': 'Error al conectar con la balanza',
    'error_exportacion': 'Error al exportar archivo',
    'confirmacion_eliminar': '¿Está seguro de eliminar este fardo?',
    'sin_datos': 'No hay datos para exportar',
}

# === CONFIGURACIÓN DE VALIDACIONES ===
VALIDACIONES = {
    'ticket_min_length': 1,
    'ticket_max_length': 20,
    'peso_minimo': 0.1,
    'peso_maximo': 100000000.0,
    'numero_fardo_maximo': 10000000,
}

# === GESTOR DE CONFIGURACIÓN SIMPLE ===
class ConfiguracionManager:
    """Gestor simple de configuración - COMPATIBLE WINDOWS 7"""
    
    def __init__(self):
        self.config_file = os.path.join(os.path.dirname(__file__), 'configuracion.json')
        self.config_data = {}
        self.cargar_configuracion()
    
    def cargar_configuracion(self):
        """Carga la configuración desde JSON si existe"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config_data = json.load(f)
            else:
                # Usar configuración por defecto
                self.config_data = {
                    'base_datos': {
                        'nombre_archivo': 'pesaje_fardos.db',
                        'usar_ruta_compartida': False,
                        'ruta_compartida': '',
                        'timeout_conexion': 30,
                        'backup_automatico': True,
                        'carpeta_backup': 'backups'
                    },
                }
                self.guardar_configuracion()
        except Exception as e:
            print(f"Error al cargar configuración: {e}")
            self.config_data = {
                'base_datos': {
                    'nombre_archivo': 'pesaje_fardos.db',
                    'usar_ruta_compartida': False,
                    'ruta_compartida': '',
                    'timeout_conexion': 30,
                    'backup_automatico': True,
                    'carpeta_backup': 'backups'
                },
            }
    
    def guardar_configuracion(self):
        """Guarda la configuración en JSON"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error al guardar configuración: {e}")
            return False
    
    def obtener(self, seccion, defecto=None):
        """Obtiene una sección de la configuración"""
        return self.config_data.get(seccion, defecto)
    
    def obtener_configuracion(self):
        """Obtiene toda la configuración - MÉTODO REQUERIDO"""
        return self.config_data.copy()
    
    def establecer(self, seccion, valor):
        """Establece una sección de la configuración"""
        self.config_data[seccion] = valor
        return self.guardar_configuracion()
    
    def obtener_balanza(self):
        """Obtiene la configuración de la balanza"""
        return self.config_data.get('balanza', BALANZA_CONFIG.copy())
    
    def obtener_base_datos(self):
        """Obtiene la configuración de la base de datos"""
        return self.config_data.get('base_datos', {
            'nombre_archivo': 'pesaje_fardos.db',
            'usar_ruta_compartida': False,
            'ruta_compartida': '',
            'timeout_conexion': 30,
            'backup_automatico': True,
            'carpeta_backup': 'backups'
        })

# Instancia global del gestor - MANTENER COMPATIBILIDAD
config_manager = ConfiguracionManager()

# Alias para compatibilidad con código existente
ConfigManager = ConfiguracionManager

# === CLASE PARA GESTIONAR CONFIGURACIÓN DE BALANZAS ===
class Configuracion:
    """Clase para gestionar la configuración de balanzas"""
    
    def __init__(self):
        self.balanzas_config_file = os.path.join(os.path.dirname(__file__), 'balanzas_config.json')
        self.balanzas_config = self._cargar_configuracion_balanzas()
    
    def _cargar_configuracion_balanzas(self):
        """Carga la configuración de balanzas desde el archivo JSON"""
        try:
            if os.path.exists(self.balanzas_config_file):
                with open(self.balanzas_config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                print(f"Archivo de configuración de balanzas no encontrado: {self.balanzas_config_file}")
                return {}
        except Exception as e:
            print(f"Error al cargar configuración de balanzas: {e}")
            return {}
    
    def obtener_configuracion_balanza_activa(self):
        """Obtiene la configuración de la balanza activa"""
        try:
            # Obtener el nombre de la balanza activa
            config_general = self.balanzas_config.get('configuracion_general', {})
            balanza_activa = config_general.get('balanza_activa', 'balanza_1')
            
            # Obtener la configuración de la balanza activa
            return self.balanzas_config.get(balanza_activa, {})
        except Exception as e:
            print(f"Error al obtener configuración de balanza activa: {e}")
            return {}
