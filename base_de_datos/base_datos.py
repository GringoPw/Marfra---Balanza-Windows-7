import sqlite3
import os
import shutil
from datetime import datetime
from typing import List, Optional, Tuple
from base_de_datos.modelos_bd import Ticket, Fardo
from base_de_datos.configuracion import ConfiguracionManager

class BaseDatos:
    """Clase para manejar la base de datos SQLite con configuración flexible"""
    
    def __init__(self, config_manager: ConfiguracionManager = None):
        self.config_manager = config_manager or ConfiguracionManager()
        # Obtener toda la configuración y luego extraer la sección base_datos
        config_completa = self.config_manager.obtener_configuracion()
        self.config_bd = config_completa.get('base_datos', {})
        
        # Determinar la ruta de la base de datos
        self.ruta_db = self._determinar_ruta_bd()
        
        print(f"📁 Base de datos configurada en: {self.ruta_db}")
        
        # Crear backup si está habilitado
        if self.config_bd.get('backup_automatico', True):
            self._crear_backup_si_necesario()
        
        self.inicializar_db()
    
    def _determinar_ruta_bd(self) -> str:
        """Determina la ruta de la base de datos según la configuración"""
        
        # Si se especifica usar ruta compartida
        if self.config_bd.get('usar_ruta_compartida', False):
            ruta_compartida = self.config_bd.get('ruta_compartida', '').strip()
            if ruta_compartida and os.path.exists(os.path.dirname(ruta_compartida)):
                print(f"🌐 Usando base de datos compartida: {ruta_compartida}")
                return ruta_compartida
            else:
                print(f"⚠️ Ruta compartida no válida: {ruta_compartida}")
        
        # Si se especifica ruta completa
        ruta_completa = self.config_bd.get('ruta_completa', '').strip()
        if ruta_completa:
            # Crear directorio si no existe
            directorio = os.path.dirname(ruta_completa)
            if directorio and not os.path.exists(directorio):
                try:
                    os.makedirs(directorio)
                    print(f"📁 Directorio creado: {directorio}")
                except Exception as e:
                    print(f"❌ Error creando directorio {directorio}: {e}")
            
            if os.path.exists(directorio) or not directorio:
                print(f"📄 Usando ruta personalizada: {ruta_completa}")
                return ruta_completa
        
        # Ruta por defecto (en el directorio del proyecto)
        nombre_archivo = self.config_bd.get('nombre_archivo', 'pesaje_fardos.db')
        ruta_defecto = os.path.join(os.path.dirname(os.path.dirname(__file__)), nombre_archivo)
        print(f"📄 Usando ruta por defecto: {ruta_defecto}")
        return ruta_defecto
    
    def _crear_backup_si_necesario(self):
        """Crea un backup de la base de datos si existe"""
        if os.path.exists(self.ruta_db):
            try:
                carpeta_backup = self.config_bd.get('carpeta_backup', 'backups')
                
                # Crear carpeta de backup si no existe
                if not os.path.isabs(carpeta_backup):
                    carpeta_backup = os.path.join(os.path.dirname(self.ruta_db), carpeta_backup)
                
                if not os.path.exists(carpeta_backup):
                    os.makedirs(carpeta_backup)
                
                # Crear nombre del backup con timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                nombre_base = os.path.splitext(os.path.basename(self.ruta_db))[0]
                nombre_backup = f"{nombre_base}_backup_{timestamp}.db"
                ruta_backup = os.path.join(carpeta_backup, nombre_backup)
                
                # Copiar archivo
                shutil.copy2(self.ruta_db, ruta_backup)
                print(f"💾 Backup creado: {ruta_backup}")
                
                # Limpiar backups antiguos (mantener solo los últimos 5)
                self._limpiar_backups_antiguos(carpeta_backup, nombre_base)
                
            except Exception as e:
                print(f"⚠️ Error creando backup: {e}")
    
    def _limpiar_backups_antiguos(self, carpeta_backup: str, nombre_base: str):
        """Mantiene solo los últimos 5 backups"""
        try:
            archivos_backup = []
            for archivo in os.listdir(carpeta_backup):
                if archivo.startswith(f"{nombre_base}_backup_") and archivo.endswith('.db'):
                    ruta_completa = os.path.join(carpeta_backup, archivo)
                    archivos_backup.append((ruta_completa, os.path.getmtime(ruta_completa)))
            
            # Ordenar por fecha (más reciente primero)
            archivos_backup.sort(key=lambda x: x[1], reverse=True)
            
            # Eliminar los que sobran (mantener solo 5)
            for ruta_archivo, _ in archivos_backup[5:]:
                os.remove(ruta_archivo)
                print(f"🗑️ Backup antiguo eliminado: {os.path.basename(ruta_archivo)}")
                
        except Exception as e:
            print(f"⚠️ Error limpiando backups: {e}")
    
    def inicializar_db(self):
        """Inicializa la base de datos y crea las tablas si no existen"""
        try:
            timeout = self.config_bd.get('timeout_conexion', 30)
            
            with sqlite3.connect(self.ruta_db, timeout=timeout) as conn:
                cursor = conn.cursor()
                
                # Tabla de tickets
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS tickets (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        numero TEXT UNIQUE NOT NULL,
                        fecha_creacion TIMESTAMP NOT NULL,
                        kg_bruto_romaneo REAL,
                        agregado REAL DEFAULT 0,
                        resto REAL DEFAULT 0,
                        observaciones TEXT,
                        estado TEXT DEFAULT 'ACTIVO',
                        fecha_guardado TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Tabla de fardos
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS fardos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ticket_id INTEGER NOT NULL,
                        numero INTEGER NOT NULL,
                        peso REAL NOT NULL,
                        hora_pesaje TIMESTAMP NOT NULL,
                        FOREIGN KEY (ticket_id) REFERENCES tickets (id),
                        UNIQUE(ticket_id, numero)
                    )
                ''')
                
                # Verificar si necesitamos agregar las nuevas columnas
                cursor.execute("PRAGMA table_info(tickets)")
                columnas_existentes = [columna[1] for columna in cursor.fetchall()]
                
                # Agregar nuevas columnas si no existen
                if 'kg_bruto_romaneo' not in columnas_existentes:
                    cursor.execute('ALTER TABLE tickets ADD COLUMN kg_bruto_romaneo REAL')
                    print("✅ Columna kg_bruto_romaneo agregada")
                
                if 'agregado' not in columnas_existentes:
                    cursor.execute('ALTER TABLE tickets ADD COLUMN agregado REAL DEFAULT 0')
                    print("✅ Columna agregado agregada")
                
                if 'resto' not in columnas_existentes:
                    cursor.execute('ALTER TABLE tickets ADD COLUMN resto REAL DEFAULT 0')
                    print("✅ Columna resto agregada")
                
                # Índices para mejor rendimiento
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_tickets_numero ON tickets(numero)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_tickets_fecha ON tickets(fecha_creacion)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_fardos_ticket ON fardos(ticket_id)')
                
                conn.commit()
                print("✅ Base de datos inicializada correctamente")
                
        except Exception as e:
            print(f"❌ Error al inicializar base de datos: {str(e)}")
            raise
    
    def cambiar_ubicacion_bd(self, nueva_ruta: str, copiar_datos: bool = True) -> bool:
        """Cambia la ubicación de la base de datos"""
        try:
            ruta_anterior = self.ruta_db
            
            # Verificar que la nueva ruta es válida
            directorio_nuevo = os.path.dirname(nueva_ruta)
            if directorio_nuevo and not os.path.exists(directorio_nuevo):
                os.makedirs(directorio_nuevo)
            
            # Copiar datos si se solicita y existe la BD anterior
            if copiar_datos and os.path.exists(ruta_anterior):
                shutil.copy2(ruta_anterior, nueva_ruta)
                print(f"📋 Datos copiados de {ruta_anterior} a {nueva_ruta}")
            
            # Actualizar configuración
            self.ruta_db = nueva_ruta
            
            # Inicializar la nueva BD
            self.inicializar_db()
            
            print(f"✅ Base de datos reubicada exitosamente")
            return True
            
        except Exception as e:
            print(f"❌ Error reubicando base de datos: {e}")
            return False
    
    def obtener_info_bd(self) -> dict:
        """Obtiene información sobre la base de datos actual"""
        try:
            info = {
                'ruta': self.ruta_db,
                'existe': os.path.exists(self.ruta_db),
                'tamaño_mb': 0,
                'accesible': False,
                'compartida': self.config_bd.get('usar_ruta_compartida', False)
            }
            
            if info['existe']:
                info['tamaño_mb'] = round(os.path.getsize(self.ruta_db) / (1024 * 1024), 2)
                
                # Probar acceso
                try:
                    with sqlite3.connect(self.ruta_db, timeout=5) as conn:
                        cursor = conn.cursor()
                        cursor.execute("SELECT COUNT(*) FROM tickets")
                        info['accesible'] = True
                        info['total_tickets'] = cursor.fetchone()[0]
                except:
                    info['accesible'] = False
            
            return info
            
        except Exception as e:
            print(f"❌ Error obteniendo info de BD: {e}")
            return {'error': str(e)}
    
    def guardar_ticket(self, ticket: Ticket, datos_adicionales: dict = None) -> bool:
        """Guarda un ticket completo en la base de datos"""
        try:
            timeout = self.config_bd.get('timeout_conexion', 30)
            
            with sqlite3.connect(self.ruta_db, timeout=timeout) as conn:
                cursor = conn.cursor()
                
                # Preparar datos adicionales
                kg_bruto_romaneo = None
                agregado = 0.0
                resto = 0.0
                observaciones = ""
                
                if datos_adicionales:
                    # Kg Bruto Romaneo
                    kg_bruto_str = datos_adicionales.get('kg_bruto_romaneo', '').strip()
                    if kg_bruto_str:
                        try:
                            kg_bruto_romaneo = float(kg_bruto_str.replace(',', '.'))
                        except ValueError:
                            kg_bruto_romaneo = None
                    
                    # Agregado
                    agregado_str = datos_adicionales.get('agregado', '0').strip()
                    try:
                        agregado = float(agregado_str.replace(',', '.'))
                    except ValueError:
                        agregado = 0.0
                    
                    # Resto
                    resto_str = datos_adicionales.get('resto', '0').strip()
                    try:
                        resto = float(resto_str.replace(',', '.'))
                    except ValueError:
                        resto = 0.0
                    
                    # Observaciones
                    observaciones = datos_adicionales.get('observaciones', '').strip()
                
                # Verificar si el ticket ya existe
                cursor.execute('SELECT id FROM tickets WHERE numero = ?', (ticket.numero,))
                ticket_existente = cursor.fetchone()
                
                if ticket_existente:
                    # Actualizar ticket existente
                    ticket_id = ticket_existente[0]
                    cursor.execute('''
                        UPDATE tickets 
                        SET kg_bruto_romaneo = ?, agregado = ?, resto = ?, 
                            observaciones = ?, fecha_guardado = CURRENT_TIMESTAMP
                        WHERE id = ?
                    ''', (kg_bruto_romaneo, agregado, resto, observaciones, ticket_id))
                    
                    # Eliminar fardos existentes para reemplazarlos
                    cursor.execute('DELETE FROM fardos WHERE ticket_id = ?', (ticket_id,))
                else:
                    # Insertar nuevo ticket
                    cursor.execute('''
                        INSERT INTO tickets (numero, fecha_creacion, kg_bruto_romaneo, 
                                           agregado, resto, observaciones)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (ticket.numero, ticket.fecha_creacion, kg_bruto_romaneo, 
                          agregado, resto, observaciones))
                    ticket_id = cursor.lastrowid
                
                # Insertar fardos
                for fardo in ticket.fardos:
                    cursor.execute('''
                        INSERT INTO fardos (ticket_id, numero, peso, hora_pesaje)
                        VALUES (?, ?, ?, ?)
                    ''', (ticket_id, fardo.numero, fardo.peso, fardo.hora_pesaje))
                
                conn.commit()
                print(f"✅ Ticket {ticket.numero} guardado correctamente")
                return True
                
        except Exception as e:
            print(f"❌ Error al guardar ticket: {str(e)}")
            return False
    
    def obtener_historial_tickets(self) -> List[Tuple]:
        """Obtiene el historial de todos los tickets"""
        try:
            timeout = self.config_bd.get('timeout_conexion', 30)
            
            with sqlite3.connect(self.ruta_db, timeout=timeout) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT t.numero, t.fecha_creacion, COUNT(f.id) as cantidad_fardos,
                           COALESCE(SUM(f.peso), 0) as peso_total, t.fecha_guardado
                    FROM tickets t
                    LEFT JOIN fardos f ON t.id = f.ticket_id
                    WHERE t.estado = 'ACTIVO'
                    GROUP BY t.id, t.numero, t.fecha_creacion, t.fecha_guardado
                    ORDER BY t.fecha_guardado DESC
                ''')
                return cursor.fetchall()
        except Exception as e:
            print(f"❌ Error al obtener historial: {str(e)}")
            return []
            
    def buscar_tickets(self, termino_busqueda: str) -> List[Tuple]:
        """Busca tickets por número o fecha"""
        try:
            timeout = self.config_bd.get('timeout_conexion', 30)
            
            with sqlite3.connect(self.ruta_db, timeout=timeout) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT t.numero, t.fecha_creacion, COUNT(f.id) as cantidad_fardos,
                           COALESCE(SUM(f.peso), 0) as peso_total, t.fecha_guardado
                    FROM tickets t
                    LEFT JOIN fardos f ON t.id = f.ticket_id
                    WHERE t.estado = 'ACTIVO' AND 
                          (t.numero LIKE ? OR date(t.fecha_creacion) LIKE ?)
                    GROUP BY t.id, t.numero, t.fecha_creacion, t.fecha_guardado
                    ORDER BY t.fecha_guardado DESC
                ''', (f'%{termino_busqueda}%', f'%{termino_busqueda}%'))
                return cursor.fetchall()
        except Exception as e:
            print(f"❌ Error al buscar tickets: {str(e)}")
            return []
    
    def cargar_ticket(self, numero_ticket: str) -> Optional[Ticket]:
        """Carga un ticket completo desde la base de datos"""
        try:
            timeout = self.config_bd.get('timeout_conexion', 30)
            
            with sqlite3.connect(self.ruta_db, timeout=timeout) as conn:
                cursor = conn.cursor()
                
                # Obtener datos del ticket
                cursor.execute('''
                    SELECT numero, fecha_creacion, kg_bruto_romaneo, agregado, resto, observaciones
                    FROM tickets 
                    WHERE numero = ? AND estado = 'ACTIVO'
                ''', (numero_ticket,))
                
                ticket_data = cursor.fetchone()
                if not ticket_data:
                    return None
                
                # Crear objeto ticket
                ticket = Ticket(ticket_data[0])
                ticket.fecha_creacion = datetime.fromisoformat(ticket_data[1])
                
                # Asignar datos adicionales
                ticket.kg_bruto_romaneo = ticket_data[2]
                ticket.agregado = ticket_data[3] if ticket_data[3] is not None else 0.0
                ticket.resto = ticket_data[4] if ticket_data[4] is not None else 0.0
                ticket.observaciones = ticket_data[5] or ""
                
                # Obtener fardos del ticket
                cursor.execute('''
                    SELECT id FROM tickets WHERE numero = ?
                ''', (numero_ticket,))
                ticket_id = cursor.fetchone()[0]
                
                cursor.execute('''
                    SELECT numero, peso, hora_pesaje
                    FROM fardos 
                    WHERE ticket_id = ?
                    ORDER BY numero
                ''', (ticket_id,))
                
                fardos_data = cursor.fetchall()
                for fardo_data in fardos_data:
                    fardo = Fardo(fardo_data[0], fardo_data[1])
                    fardo.hora_pesaje = datetime.fromisoformat(fardo_data[2])
                    ticket.fardos.append(fardo)
                
                print(f"✅ Ticket {numero_ticket} cargado correctamente con {len(ticket.fardos)} fardos")
                return ticket
                
        except Exception as e:
            print(f"❌ Error al cargar ticket: {str(e)}")
            return None
    
    def eliminar_ticket(self, numero_ticket: str) -> bool:
        """Marca un ticket como eliminado (soft delete)"""
        try:
            timeout = self.config_bd.get('timeout_conexion', 30)
            
            with sqlite3.connect(self.ruta_db, timeout=timeout) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE tickets 
                    SET estado = 'ELIMINADO', fecha_guardado = CURRENT_TIMESTAMP
                    WHERE numero = ?
                ''', (numero_ticket,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"❌ Error al eliminar ticket: {str(e)}")
            return False
    
    def obtener_estadisticas_generales(self) -> dict:
        """Obtiene estadísticas generales de la base de datos"""
        try:
            timeout = self.config_bd.get('timeout_conexion', 30)
            
            with sqlite3.connect(self.ruta_db, timeout=timeout) as conn:
                cursor = conn.cursor()
                
                # Total de tickets
                cursor.execute('SELECT COUNT(*) FROM tickets WHERE estado = "ACTIVO"')
                total_tickets = cursor.fetchone()[0]
                
                # Total de fardos
                cursor.execute('''
                    SELECT COUNT(*) FROM fardos f
                    JOIN tickets t ON f.ticket_id = t.id
                    WHERE t.estado = "ACTIVO"
                ''')
                total_fardos = cursor.fetchone()[0]
                
                # Peso total
                cursor.execute('''
                    SELECT COALESCE(SUM(f.peso), 0) FROM fardos f
                    JOIN tickets t ON f.ticket_id = t.id
                    WHERE t.estado = "ACTIVO"
                ''')
                peso_total = cursor.fetchone()[0]
                
                return {
                    'total_tickets': total_tickets,
                    'total_fardos': total_fardos,
                    'peso_total': peso_total
                }
        except Exception as e:
            print(f"❌ Error al obtener estadísticas: {str(e)}")
            return {'total_tickets': 0, 'total_fardos': 0, 'peso_total': 0}
