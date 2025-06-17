import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime
import time
import threading
from componentes.componentes import (
    Header, SeccionEntrada, SeccionPesoControles,
    TablaRegistros, BotonesPrincipales, BarraEstado
)



class SistemaPesajeFardos:
    def __init__(self, root):
        self.root = root
        self.configurar_ventana_principal()
        self.inicializar_variables()
        self.crear_componentes()
        self.iniciar_servicios()

    def configurar_ventana_principal(self):
        self.root.title("Sistema de Pesaje de Fardos v1.0")

        # Obtener dimensiones de la pantalla
        ancho_pantalla = self.root.winfo_screenwidth()
        alto_pantalla = self.root.winfo_screenheight()

        # Tamaño inicial como porcentaje de la pantalla (80% del ancho y 85% del alto)
        ancho_ventana = int(ancho_pantalla * 0.8)
        alto_ventana = int(alto_pantalla * 0.85)

        # Posicionar la ventana en el centro
        x_pos = (ancho_pantalla // 2) - (ancho_ventana // 2)
        y_pos = (alto_pantalla // 2) - (alto_ventana // 2)

        self.root.geometry(f"{ancho_ventana}x{alto_ventana}+{x_pos}+{y_pos}")
        self.root.configure(bg='#f8f9fa')

        # Permitir redimensionamiento pero con límites mínimos
        self.root.minsize(800, 600)  # Tamaño mínimo
        self.root.maxsize(ancho_pantalla, alto_pantalla)  # Tamaño máximo

        # Configurar el peso de las filas y columnas para que los widgets se expandan
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
    
    
    

    def inicializar_variables(self):
        # Variables de datos
        self.ticket_actual = tk.StringVar()
        self.fardo_inicial = tk.StringVar()
        self.fardo_actual = 0
        self.peso_actual = tk.StringVar(value="0.00")
        self.fardos_data = []

        # Variables de estado
        self.modo_repeso = False
        self.fardo_repeso = None
        self.estado = "esperando_ticket"

        # Variables de sistema
        self.conexion_bd = tk.StringVar(value="Desconectado")
        self.conexion_balanza = tk.StringVar(value="Desconectado")
        self.nombre_balanza = tk.StringVar(value="No seleccionada")
        self.estado_internet = tk.StringVar(value="Sin conexión")

    def crear_componentes(self):
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#f8f9fa')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Header
        self.header = Header(main_frame)
        
        # Contenedor principal con pack
        contenedor_principal = tk.Frame(main_frame, bg='#f8f9fa')
        contenedor_principal.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Columna izquierda - Entrada de datos
        columna_izquierda = tk.Frame(contenedor_principal, bg='#f8f9fa')
        columna_izquierda.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Columna derecha - Estadísticas y datos adicionales
        columna_derecha = tk.Frame(contenedor_principal, bg='#f8f9fa')
        columna_derecha.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Componentes en columna izquierda
        self.seccion_entrada = SeccionEntrada(columna_izquierda, self)
        self.seccion_peso = SeccionPesoControles(columna_izquierda, self)
        
        # Componentes en columna derecha
        self.tabla_registros = TablaRegistros(columna_derecha, self)
        
        # Botones y barra de estado en el frame principal
        botones_frame = tk.Frame(main_frame, bg='#f8f9fa')
        botones_frame.pack(fill=tk.X, pady=10)
        self.botones_principales = BotonesPrincipales(botones_frame, self)
        
        # Barra de estado
        self.barra_estado = BarraEstado(main_frame, self)

        # Focus inicial
        self.seccion_entrada.entry_ticket.focus()

    def iniciar_servicios(self):
        self.iniciar_lectura_peso()
        self.actualizar_estados_sistema()

    # Métodos de servicios en segundo plano
    def leer_peso_balanza(self):
        """Lee el peso desde la balanza usando las funciones globales de balanza_reader"""
        try:
            import sys
            import os
            import tkinter as tk
            from tkinter import messagebox
            
            # Asegurarse de que el directorio raíz esté en el path
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            if root_dir not in sys.path:
                sys.path.append(root_dir)
                
            from balanza_reader import obtener_peso, inicializar_balanza
            
            # Si no se ha inicializado la balanza, inicializarla
            if not hasattr(self, '_balanza_inicializada') or not self._balanza_inicializada:
                try:
                    # Inicializar la balanza (esto crea una única instancia global)
                    if inicializar_balanza("balanza1"):
                        self._balanza_inicializada = True
                    else:
                        messagebox.showerror("Error de Conexión", 
                                           "No se pudo conectar a la balanza.\n"
                                           "Verifique que esté conectada y el puerto sea correcto.")
                        return 0.0
                except Exception as e:
                    messagebox.showerror("Error de Inicialización", 
                                       f"Error al inicializar la balanza: {str(e)}\n"
                                       f"Verifique que el archivo configuracion.json exista y sea válido.")
                    return 0.0
            
            # Leer el peso usando la función global
            try:
                peso = obtener_peso()
                
                # Si no hay peso, devolver 0
                if peso is None:
                    return 0.0
                    
                return round(peso, 2)
            except Exception as e:
                messagebox.showerror("Error de Lectura", 
                                   f"Error al leer el peso: {str(e)}\n"
                                   f"Verifique la conexión con la balanza.")
                return 0.0
                
        except Exception as e:
            messagebox.showerror("Error General", f"Error al leer peso de la balanza: {str(e)}")
            print(f"Error al leer peso de la balanza: {e}")
            return 0.0

    def obtener_peso_continuo(self):
        """Obtiene el peso cada segundo"""
        error_mostrado = False
        while True:
            try:
                peso = self.leer_peso_balanza()
                self.peso_actual.set(f"{peso:.2f}")
                error_mostrado = False  # Resetear el flag de error si la lectura fue exitosa
                time.sleep(1)
            except Exception as e:
                if not error_mostrado:  # Solo mostrar el error una vez
                    print(f"Error al leer peso: {e}")
                    error_mostrado = True
                time.sleep(1)

    def iniciar_lectura_peso(self):
        """Inicia el hilo para lectura continua del peso"""
        hilo_peso = threading.Thread(
            target=self.obtener_peso_continuo, daemon=True)
        hilo_peso.start()

    def actualizar_estados_sistema(self):
        """Actualiza los estados del sistema cada 5 segundos"""
        def actualizar():
            while True:
                try:
                    # Aquí llamarías a tus funciones externas
                    bd_ok = self.verificar_conexion_bd()
                    balanza_ok, nombre_balanza = self.verificar_conexion_balanza()
                    internet_ok = self.verificar_conexion_internet()

                    # Actualizar labels
                    self.barra_estado.actualizar_estados(
                        bd_ok, balanza_ok, nombre_balanza, internet_ok)

                except Exception as e:
                    print(f"Error actualizando estados: {e}")

                time.sleep(5)

        hilo_estados = threading.Thread(target=actualizar, daemon=True)
        hilo_estados.start()

    def verificar_conexion_bd(self):
        """IMPLEMENTAR: Verifica conexión a base de datos"""
        import random
        return random.choice([True, False])

    def verificar_conexion_balanza(self):
        """Verifica la conexión a la balanza usando las funciones globales"""
        try:
            import sys
            import os
            
            # Asegurarse de que el directorio raíz esté en el path
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            if root_dir not in sys.path:
                sys.path.append(root_dir)
                
            from balanza_reader import get_status_balanza
            
            # Obtener el estado actual de la balanza
            status = get_status_balanza()
            
            if "error" in status:
                # La balanza no está inicializada
                print("Balanza no inicializada")
                return False, ""
            
            if status["conectado"]:
                # Ya está conectada, usar la información del status
                return True, status.get("balanza_actual", "Balanza")
            
            print("Balanza no conectada")
            return False, ""
            
        except Exception as e:
            print(f"Error al verificar conexión con balanza: {e}")
            return False, ""

    def verificar_conexion_internet(self):
        """IMPLEMENTAR: Verifica conexión a internet"""
        import random
        return random.choice([True, False])

    # Métodos de lógica de negocio
    def procesar_ticket(self):
        """Procesa el ingreso del ticket"""
        if not self.ticket_actual.get().strip():
            messagebox.showwarning(
                "Advertencia", "Ingrese un número de ticket válido")
            return

        self.estado = "esperando_fardo_inicial"
        self.seccion_entrada.configurar_estado("esperando_fardo_inicial")
        self.seccion_entrada.entry_fardo.focus()
        
        # Actualizar información en la tabla
        self.tabla_registros.actualizar_info_ticket(self.ticket_actual.get(), "--")

    def procesar_fardo_inicial(self):
        """Procesa el fardo inicial"""
        try:
            fardo_inicial = int(self.fardo_inicial.get())
            if fardo_inicial <= 0:
                raise ValueError("El número debe ser positivo")

            self.fardo_actual = fardo_inicial
            self.estado = "listo_para_pesar"

            self.seccion_peso.actualizar_display_fardo(
                self.fardo_actual, False)
            self.seccion_peso.entry_pesar.focus()
            self.seccion_entrada.configurar_estado("listo_para_pesar")
            
            # Actualizar información en la tabla
            self.tabla_registros.actualizar_info_ticket(self.ticket_actual.get(), self.fardo_actual)

        except ValueError:
            messagebox.showerror("Error", "Ingrese un número de fardo válido")

    def pesar_fardo(self):
        """Pesa un fardo y guarda automáticamente en la base de datos"""
        if self.estado != "listo_para_pesar":
            return

        try:
            peso = float(self.peso_actual.get())

            if peso < 1.0:
                messagebox.showwarning(
                    "Advertencia", "El peso debe ser mayor a 1 kg")
                return

            ahora = datetime.now()
            fecha = ahora.strftime("%d/%m/%Y")
            hora = ahora.strftime("%H:%M:%S")

            if self.modo_repeso and self.fardo_repeso:
                # Repeso
                for i, fardo in enumerate(self.fardos_data):
                    if fardo[0] == self.fardo_repeso:
                        self.fardos_data[i] = (
                            self.fardo_repeso, peso, fecha, hora)
                        break

                self.tabla_registros.actualizar_fardo(
                    self.fardo_repeso, peso, fecha, hora)

                self.modo_repeso = False
                self.fardo_repeso = None
                self.seccion_peso.configurar_modo_repeso(False)
                self.seccion_entrada.configurar_estado("fardo_repesado")
            else:
                # Nuevo fardo
                fardo_data = (self.fardo_actual, peso, fecha, hora)
                self.fardos_data.append(fardo_data)
                self.tabla_registros.agregar_fardo(
                    self.fardo_actual, peso, fecha, hora)
                self.fardo_actual += 1
                self.seccion_entrada.configurar_estado("fardo_registrado")
                
                # Actualizar información en la tabla
                self.tabla_registros.actualizar_info_ticket(self.ticket_actual.get(), self.fardo_actual)

            # Habilitar controles y botón de guardar
            self.botones_principales.habilitar_controles(True)
            self.botones_principales.habilitar_boton_guardar(True)

            self.seccion_peso.actualizar_display_fardo(self.fardo_actual, False)
            self.seccion_peso.entry_pesar.focus()
        except Exception as e:
            messagebox.showerror("Error", f"Error al pesar fardo: {str(e)}")
            print(f"Error en pesar_fardo: {e}")

    def iniciar_repeso(self, fardo_seleccionado):
        """Inicia el proceso de repeso"""
        if not fardo_seleccionado:
            messagebox.showwarning(
                "Advertencia", "Seleccione un fardo de la tabla para repesar")
            return

        try:
            self.modo_repeso = True
            self.fardo_repeso = int(fardo_seleccionado[0])
            self.estado = "listo_para_pesar"  # Importante: establecer el estado correcto para permitir el pesaje

            self.seccion_entrada.configurar_estado(
                "modo_repeso", self.fardo_repeso)
            self.seccion_peso.configurar_modo_repeso(True, self.fardo_repeso)
            self.seccion_peso.entry_pesar.focus()
        except Exception as e:
            messagebox.showerror("Error", f"Error al iniciar repeso: {str(e)}")
            print(f"Error en iniciar_repeso: {e}")

    def nuevo_ticket(self):
        """Inicia un nuevo ticket"""
        if self.fardos_data:
            respuesta = messagebox.askyesno("Nuevo Ticket",
                                            f"¿Desea iniciar un nuevo ticket?\n\nDatos actuales:\n" +
                                            f"• Ticket: {self.ticket_actual.get()}\n" +
                                            f"• Fardos registrados: {len(self.fardos_data)}\n\n" +
                                            "Los datos no guardados se perderán.")
            if not respuesta:
                return

        self.resetear_interfaz()

    def mostrar_historial(self):
        """Muestra el historial de tickets y permite cargar uno seleccionado"""
        from base_de_datos.base_datos import BaseDatos
        
        # Crear ventana de historial
        historial_window = tk.Toplevel(self.root)
        historial_window.title("Historial de Tickets")
        historial_window.transient(self.root)
        historial_window.grab_set()
        
        # Configurar tamaño y posición
        ancho = 800
        alto = 500
        x = (historial_window.winfo_screenwidth() // 2) - (ancho // 2)
        y = (historial_window.winfo_screenheight() // 2) - (alto // 2)
        historial_window.geometry(f"{ancho}x{alto}+{x}+{y}")
        historial_window.configure(bg='#f8f9fa')
        
        # Frame principal
        main_frame = tk.Frame(historial_window, bg='#f8f9fa', padx=15, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título y búsqueda
        header_frame = tk.Frame(main_frame, bg='#f8f9fa')
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(header_frame, text="Historial de Tickets", font=('Arial', 14, 'bold'), 
                bg='#f8f9fa', fg='#2c3e50').pack(side=tk.LEFT)
        
        # Búsqueda
        search_frame = tk.Frame(header_frame, bg='#f8f9fa')
        search_frame.pack(side=tk.RIGHT)
        
        tk.Label(search_frame, text="Buscar:", bg='#f8f9fa', fg='#2c3e50').pack(side=tk.LEFT, padx=(0, 5))
        
        busqueda_var = tk.StringVar()
        entry_buscar = tk.Entry(search_frame, textvariable=busqueda_var, width=20)
        entry_buscar.pack(side=tk.LEFT, padx=(0, 5))
        
        # Tabla de tickets
        tabla_frame = tk.Frame(main_frame, bg='#f8f9fa')
        tabla_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Configurar Treeview
        columns = ('Ticket', 'Fecha', 'Fardos', 'Peso Total', 'Guardado')
        historial_tree = ttk.Treeview(tabla_frame, columns=columns, show='headings', height=15)
        
        # Configurar columnas
        historial_tree.heading('Ticket', text='N° Ticket')
        historial_tree.heading('Fecha', text='Fecha')
        historial_tree.heading('Fardos', text='Fardos')
        historial_tree.heading('Peso Total', text='Peso Total (kg)')
        historial_tree.heading('Guardado', text='Guardado')
        
        historial_tree.column('Ticket', width=100, anchor=tk.CENTER)
        historial_tree.column('Fecha', width=150, anchor=tk.CENTER)
        historial_tree.column('Fardos', width=80, anchor=tk.CENTER)
        historial_tree.column('Peso Total', width=120, anchor=tk.CENTER)
        historial_tree.column('Guardado', width=150, anchor=tk.CENTER)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tabla_frame, orient=tk.VERTICAL, command=historial_tree.yview)
        historial_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack
        historial_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Etiqueta para mostrar mensajes
        mensaje_label = tk.Label(main_frame, text="", font=('Arial', 11, 'italic'), 
                               bg='#f8f9fa', fg='#7f8c8d')
        mensaje_label.pack(pady=5)
        
        # Botones
        btn_frame = tk.Frame(main_frame, bg='#f8f9fa')
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        btn_cargar = tk.Button(btn_frame, text="Cargar Ticket", font=('Arial', 10), 
                             bg='#3498db', fg='white', relief=tk.FLAT, padx=15, pady=5,
                             state=tk.DISABLED, cursor='hand2')
        btn_cargar.pack(side=tk.LEFT, padx=5)
        
        btn_cerrar = tk.Button(btn_frame, text="Cerrar", font=('Arial', 10), 
                             bg='#e74c3c', fg='white', relief=tk.FLAT, padx=15, pady=5,
                             command=historial_window.destroy, cursor='hand2')
        btn_cerrar.pack(side=tk.LEFT, padx=5)
        
        # Función para cargar tickets en la tabla
        def cargar_tickets(tickets):
            # Limpiar tabla
            for item in historial_tree.get_children():
                historial_tree.delete(item)
                
            if not tickets:
                mensaje_label.config(text="No se encontraron tickets")
                return
                
            mensaje_label.config(text=f"Se encontraron {len(tickets)} tickets")
            
            for ticket in tickets:
                numero, fecha_creacion, cantidad_fardos, peso_total, fecha_guardado = ticket
                historial_tree.insert('', 'end', values=(
                    numero, 
                    datetime.fromisoformat(fecha_creacion).strftime("%d/%m/%Y %H:%M"),
                    cantidad_fardos,
                    f"{peso_total:.2f}",
                    datetime.fromisoformat(fecha_guardado).strftime("%d/%m/%Y %H:%M")
                ))
        
        # Función para buscar tickets
        def buscar_tickets():
            termino = busqueda_var.get().strip()
            bd = BaseDatos()
            
            if termino:
                tickets = bd.buscar_tickets(termino)
            else:
                tickets = bd.obtener_historial_tickets()
                
            cargar_tickets(tickets)
        
        # Botón de búsqueda
        btn_buscar = tk.Button(search_frame, text="Buscar", bg='#3498db', fg='white',
                             relief=tk.FLAT, command=buscar_tickets, cursor='hand2')
        btn_buscar.pack(side=tk.LEFT)
        
        # Vincular Enter a la búsqueda
        entry_buscar.bind('<Return>', lambda e: buscar_tickets())
        
        # Función para cargar ticket seleccionado
        def cargar_ticket_seleccionado():
            seleccion = historial_tree.selection()
            if not seleccion:
                return
                
            valores = historial_tree.item(seleccion[0], 'values')
            numero_ticket = valores[0]
            
            # Preguntar si desea cargar el ticket
            respuesta = messagebox.askyesno("Cargar Ticket", 
                                          f"¿Desea cargar el ticket {numero_ticket}?\n\n" +
                                          "Los datos no guardados se perderán.")
            if not respuesta:
                return
                
            # Cerrar ventana de historial
            historial_window.destroy()
            
            # Cargar ticket
            self._cargar_ticket_desde_bd(numero_ticket)
        
        # Habilitar botón cuando se selecciona un ticket
        def on_select(event):
            seleccion = historial_tree.selection()
            btn_cargar.config(state=tk.NORMAL if seleccion else tk.DISABLED)
            
        historial_tree.bind('<<TreeviewSelect>>', on_select)
        btn_cargar.config(command=cargar_ticket_seleccionado)
        
        # Doble clic para cargar
        historial_tree.bind('<Double-1>', lambda e: cargar_ticket_seleccionado())
        
        # Cargar datos iniciales
        try:
            bd = BaseDatos()
            tickets = bd.obtener_historial_tickets()
            cargar_tickets(tickets)
        except Exception as e:
            mensaje_label.config(text=f"Error al cargar historial: {str(e)}", fg='#e74c3c')
            
    def _cargar_ticket_desde_bd(self, numero_ticket):
        """Carga un ticket desde la base de datos"""
        from base_de_datos.base_datos import BaseDatos
        
        try:
            # Resetear interfaz actual
            self.resetear_interfaz()
            
            # Cargar ticket desde BD
            bd = BaseDatos()
            ticket = bd.cargar_ticket(numero_ticket)
            
            if not ticket:
                messagebox.showerror("Error", f"No se encontró el ticket {numero_ticket}")
                return
                
            # Establecer número de ticket
            self.ticket_actual.set(ticket.numero)
            
            # Procesar ticket (simular entrada de usuario)
            self.procesar_ticket()
            
            # Establecer fardo inicial
            if ticket.fardos:
                primer_fardo = min(fardo.numero for fardo in ticket.fardos)
                self.fardo_inicial.set(str(primer_fardo))
                self.procesar_fardo_inicial()
                
                # Cargar fardos
                for fardo in sorted(ticket.fardos, key=lambda f: f.numero):
                    # Convertir a formato de la aplicación
                    fecha = fardo.hora_pesaje.strftime("%d/%m/%Y")
                    hora = fardo.hora_pesaje.strftime("%H:%M:%S")
                    
                    # Agregar a la lista de fardos
                    fardo_data = (fardo.numero, fardo.peso, fecha, hora)
                    self.fardos_data.append(fardo_data)
                    
                    # Actualizar tabla
                    self.tabla_registros.agregar_fardo(fardo.numero, fardo.peso, fecha, hora)
                
                # Actualizar fardo actual
                self.fardo_actual = max(fardo.numero for fardo in ticket.fardos) + 1
                self.seccion_peso.actualizar_display_fardo(self.fardo_actual, False)
                
                # Actualizar información en la tabla
                self.tabla_registros.actualizar_info_ticket(self.ticket_actual.get(), self.fardo_actual)
                
                # Habilitar controles
                self.botones_principales.habilitar_controles(True)
                self.estado = "listo_para_pesar"
                
                # Cargar datos adicionales si existen
                if hasattr(ticket, 'kg_bruto_romaneo') and ticket.kg_bruto_romaneo is not None:
                    self.seccion_entrada.entry_kg_bruto.delete(0, tk.END)
                    self.seccion_entrada.entry_kg_bruto.insert(0, str(ticket.kg_bruto_romaneo))
                    
                if hasattr(ticket, 'agregado') and ticket.agregado is not None:
                    self.seccion_entrada.entry_agregado.delete(0, tk.END)
                    self.seccion_entrada.entry_agregado.insert(0, str(ticket.agregado))
                    
                if hasattr(ticket, 'resto') and ticket.resto is not None:
                    self.seccion_entrada.entry_resto.delete(0, tk.END)
                    self.seccion_entrada.entry_resto.insert(0, str(ticket.resto))
                    
                # Calcular rinde con los datos cargados
                self.seccion_entrada.calcular_rinde()
                
                messagebox.showinfo("Ticket Cargado", 
                                  f"Ticket {numero_ticket} cargado correctamente\n" +
                                  f"Fardos: {len(ticket.fardos)}")
            else:
                messagebox.showwarning("Advertencia", f"El ticket {numero_ticket} no tiene fardos")
                
        except Exception as e:
            print(f"Error detallado al cargar ticket: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Error al cargar ticket: {str(e)}")
            
    def guardar_datos(self):
        """Guarda los datos en la base de datos con datos adicionales"""
        from base_de_datos.base_datos import BaseDatos
        from base_de_datos.modelos_bd import Ticket, Fardo
        
        if not self.fardos_data:
            messagebox.showwarning("Advertencia", "No hay datos para guardar")
            return

        try:
            # Obtener datos adicionales de la interfaz
            kg_bruto = self.seccion_entrada.entry_kg_bruto.get().strip()
            agregado = self.seccion_entrada.entry_agregado.get().strip()
            resto = self.seccion_entrada.entry_resto.get().strip()
            
            # Crear ticket
            ticket = Ticket(self.ticket_actual.get())
            
            # Agregar fardos al ticket
            for fardo_data in self.fardos_data:
                numero_fardo, peso, fecha_str, hora_str = fardo_data
                fardo = Fardo(numero_fardo, peso)
                # Convertir fecha y hora a datetime
                fecha_hora_str = f"{fecha_str} {hora_str}"
                fardo.hora_pesaje = datetime.strptime(fecha_hora_str, "%d/%m/%Y %H:%M:%S")
                ticket.agregar_fardo(fardo)
            
            # Preparar datos adicionales para pasar al método guardar_ticket
            datos_adicionales = {
                'kg_bruto_romaneo': kg_bruto,
                'agregado': agregado,
                'resto': resto,
                'observaciones': ""
            }

            bd = BaseDatos() 
            resultado = bd.guardar_ticket(ticket, datos_adicionales)

            if resultado:
                messagebox.showinfo("Éxito",
                                f"Datos guardados correctamente\n\n" +
                                f"Ticket: {self.ticket_actual.get()}\n" +
                                f"Fardos: {len(self.fardos_data)}")
                self.botones_principales.habilitar_boton_guardar(False)
                self.seccion_entrada.configurar_estado("datos_guardados")
            else:
                messagebox.showerror("Error", "Error al guardar en base de datos")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")
            print(f"Error detallado al guardar: {e}")
            import traceback
            traceback.print_exc()
            
    def resetear_interfaz(self):
        """Resetea la interfaz para un nuevo ticket"""
        self.ticket_actual.set("")
        self.fardo_inicial.set("")
        self.fardo_actual = 0
        self.modo_repeso = False
        self.fardo_repeso = None
        self.estado = "esperando_ticket"
        self.fardos_data.clear()

        # Resetear componentes
        self.tabla_registros.limpiar_tabla()
        self.tabla_registros.resetear_info_ticket()
        self.seccion_entrada.resetear()
        self.seccion_peso.resetear()
        self.botones_principales.resetear()

        self.seccion_entrada.entry_ticket.focus()
        
    def cerrar_aplicacion(self):
        """Cierra la aplicación y libera recursos"""
        try:
            # Cerrar conexión con la balanza usando la función global
            import sys
            import os
            
            # Asegurarse de que el directorio raíz esté en el path
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            if root_dir not in sys.path:
                sys.path.append(root_dir)
                
            from balanza_reader import cerrar_balanza
            
            # Cerrar la conexión global con la balanza
            cerrar_balanza()
            print("Conexión con balanza cerrada correctamente")
        except Exception as e:
            print(f"Error al cerrar conexión con balanza: {e}")
        
        # Cerrar ventana principal
        self.root.destroy()