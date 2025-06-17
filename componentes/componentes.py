import tkinter as tk
from tkinter import ttk

class Header:
    def __init__(self, parent):
        self.parent = parent
        
        
       
        
       

class SeccionEntrada:
    def __init__(self, parent, controlador):
        self.parent = parent
        self.controlador = controlador
        self.crear_seccion()
        
    def crear_seccion(self):
        entrada_frame = tk.LabelFrame(self.parent, text=" Datos del Ticket ", 
                                    font=('Arial', 10, 'bold'), bg='#f8f9fa', 
                                    fg='#2c3e50', padx=15, pady=10)
        entrada_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Usar grid para mejor organización
        # Ticket
        tk.Label(entrada_frame, text="N° Ticket:", font=('Arial', 10, 'bold'), 
                bg='#f8f9fa', fg='#2c3e50').grid(row=0, column=0, sticky='w', pady=5)
        
        self.entry_ticket = tk.Entry(entrada_frame, textvariable=self.controlador.ticket_actual, 
                                   font=('Arial', 11), width=15, relief=tk.GROOVE, bd=1)
        self.entry_ticket.grid(row=0, column=1, sticky='w', padx=5, pady=5)
        self.entry_ticket.bind('<Return>', lambda e: self.controlador.procesar_ticket())
        
        # Fardo inicial
        tk.Label(entrada_frame, text="Fardo inicial:", font=('Arial', 10, 'bold'), 
                bg='#f8f9fa', fg='#2c3e50').grid(row=1, column=0, sticky='w', pady=5)
        
        # Validación para solo permitir números enteros
        def validate_int(action, value_if_allowed):
            if action == '1':  # Inserción
                if value_if_allowed == "":
                    return True
                try:
                    int(value_if_allowed)
                    return True
                except ValueError:
                    return False
            return True
        
        validate_cmd = (self.parent.register(validate_int), '%d', '%P')
        
        self.entry_fardo = tk.Entry(entrada_frame, textvariable=self.controlador.fardo_inicial, 
                                  font=('Arial', 11), width=15, state=tk.DISABLED,
                                  relief=tk.GROOVE, bd=1, validate="key", validatecommand=validate_cmd)
        self.entry_fardo.grid(row=1, column=1, sticky='w', padx=5, pady=5)
        self.entry_fardo.bind('<Return>', lambda e: self.controlador.procesar_fardo_inicial())
        
        # Estado del sistema
        self.label_estado = tk.Label(entrada_frame, text="Ingrese número de ticket", 
                                   font=('Arial', 10, 'italic'), bg='#f8f9fa', fg='#7f8c8d')
        self.label_estado.grid(row=2, column=0, columnspan=2, sticky='w', pady=10)
        
        # Datos adicionales
        datos_adicionales_frame = tk.LabelFrame(entrada_frame, text=" Datos Adicionales ", 
                                             font=('Arial', 9, 'bold'), bg='#f8f9fa', 
                                             fg='#2c3e50', padx=10, pady=5)
        datos_adicionales_frame.grid(row=3, column=0, columnspan=2, sticky='ew', pady=10)
        
        # Validación para solo permitir números y punto decimal
        def validate_float(action, value_if_allowed):
            if action == '1':  # Inserción
                if value_if_allowed == "":
                    return True
                try:
                    float(value_if_allowed)
                    return True
                except ValueError:
                    return False
            return True
        
        validate_float_cmd = (self.parent.register(validate_float), '%d', '%P')
        
        # Kg Bruto Romaneo
        tk.Label(datos_adicionales_frame, text="Kg Bruto:", font=('Arial', 9), 
                bg='#f8f9fa', fg='#2c3e50').grid(row=0, column=0, sticky='w', pady=2)
        
        self.entry_kg_bruto = tk.Entry(datos_adicionales_frame, width=10, 
                                     validate="key", validatecommand=validate_float_cmd)
        self.entry_kg_bruto.grid(row=0, column=1, sticky='w', padx=5, pady=2)
        
        # Agregado
        tk.Label(datos_adicionales_frame, text="Agregado:", font=('Arial', 9), 
                bg='#f8f9fa', fg='#2c3e50').grid(row=1, column=0, sticky='w', pady=2)
        
        self.entry_agregado = tk.Entry(datos_adicionales_frame, width=10, 
                                     validate="key", validatecommand=validate_float_cmd)
        self.entry_agregado.insert(0, "0")
        self.entry_agregado.grid(row=1, column=1, sticky='w', padx=5, pady=2)
        
        # Resto
        tk.Label(datos_adicionales_frame, text="Resto:", font=('Arial', 9), 
                bg='#f8f9fa', fg='#2c3e50').grid(row=2, column=0, sticky='w', pady=2)
        
        self.entry_resto = tk.Entry(datos_adicionales_frame, width=10, 
                                  validate="key", validatecommand=validate_float_cmd)
        self.entry_resto.insert(0, "0")
        self.entry_resto.grid(row=2, column=1, sticky='w', padx=5, pady=2)
        
        # Rinde
        tk.Label(datos_adicionales_frame, text="Rinde (%):", font=('Arial', 9, 'bold'), 
                bg='#f8f9fa', fg='#2c3e50').grid(row=3, column=0, sticky='w', pady=2)
        
        self.label_rinde = tk.Label(datos_adicionales_frame, text="0.00 %", font=('Arial', 9, 'bold'), 
                                  bg='#f8f9fa', fg='#e74c3c')
        self.label_rinde.grid(row=3, column=1, sticky='w', padx=5, pady=2)
        
        # Botón para calcular rinde
        self.btn_calcular_rinde = tk.Button(datos_adicionales_frame, text="Calcular", 
                                          font=('Arial', 8), bg='#3498db', fg='white',
                                          command=self.calcular_rinde, relief=tk.FLAT, 
                                          bd=0, cursor='hand2', padx=3, pady=1)
        self.btn_calcular_rinde.grid(row=3, column=2, sticky='w', padx=5, pady=2)
        
        # Vincular eventos para cálculo automático
        self.entry_kg_bruto.bind('<FocusOut>', lambda e: self.calcular_rinde())
        self.entry_agregado.bind('<FocusOut>', lambda e: self.calcular_rinde())
        self.entry_resto.bind('<FocusOut>', lambda e: self.calcular_rinde())
    
    def configurar_estado(self, estado, fardo_repeso=None):
        estados = {
            "esperando_ticket": {
                "text": "Ingrese número de ticket",
                "entry_ticket_state": tk.NORMAL,
                "entry_fardo_state": tk.DISABLED
            },
            "esperando_fardo_inicial": {
                "text": "Ingrese número de fardo inicial",
                "entry_ticket_state": tk.DISABLED,
                "entry_fardo_state": tk.NORMAL
            },
            "listo_para_pesar": {
                "text": "Sistema listo - Presione Enter para pesar",
                "entry_ticket_state": tk.DISABLED,
                "entry_fardo_state": tk.DISABLED
            },
            "fardo_registrado": {
                "text": "Fardo registrado - Listo para el siguiente",
                "entry_ticket_state": tk.DISABLED,
                "entry_fardo_state": tk.DISABLED
            },
            "fardo_repesado": {
                "text": "Fardo repesado correctamente",
                "entry_ticket_state": tk.DISABLED,
                "entry_fardo_state": tk.DISABLED
            },
            "modo_repeso": {
                "text": f"Presione Enter para repesar fardo {fardo_repeso}",
                "entry_ticket_state": tk.DISABLED,
                "entry_fardo_state": tk.DISABLED
            },
            "datos_guardados": {
                "text": "Datos guardados en base de datos",
                "entry_ticket_state": tk.DISABLED,
                "entry_fardo_state": tk.DISABLED
            }
        }
        
        config = estados.get(estado, {})
        self.label_estado.config(text=config.get("text", ""))
        self.entry_ticket.config(state=config.get("entry_ticket_state", tk.NORMAL))
        self.entry_fardo.config(state=config.get("entry_fardo_state", tk.DISABLED))
    
    def resetear(self):
        self.entry_ticket.config(state=tk.NORMAL)
        self.entry_fardo.config(state=tk.DISABLED)
        self.entry_kg_bruto.delete(0, tk.END)
        self.entry_agregado.delete(0, tk.END)
        self.entry_agregado.insert(0, "0")
        self.entry_resto.delete(0, tk.END)
        self.entry_resto.insert(0, "0")
        self.label_rinde.config(text="0.00 %")
        self.configurar_estado("esperando_ticket")
        
    def calcular_rinde(self):
        """Calcula el rinde según la fórmula: (kg total fardos + resto - agregado - tara)/Kgbrutos romaneo * 100"""
        try:
            # Obtener peso total de fardos
            peso_total_fardos = self.controlador.tabla_registros.obtener_peso_total()
            
            # Obtener resto, agregado y kg bruto
            resto = float(self.entry_resto.get() or 0)
            agregado = float(self.entry_agregado.get() or 0)
            kg_bruto = float(self.entry_kg_bruto.get() or 0)
            
            # Calcular tara (2kg por fardo)
            cantidad_fardos = len(self.controlador.fardos_data)
            tara = cantidad_fardos * 2  # 2kg por fardo
            
            # Calcular rinde
            if kg_bruto > 0:
                rinde = ((peso_total_fardos + resto - agregado - tara) / kg_bruto) * 100
                self.label_rinde.config(text=f"{rinde:.2f} %")
            else:
                self.label_rinde.config(text="N/A")
        except Exception as e:
            print(f"Error al calcular rinde: {e}")
            self.label_rinde.config(text="Error")

class SeccionPesoControles:
    def __init__(self, parent, controlador):
        self.parent = parent
        self.controlador = controlador
        self.crear_seccion()
        
    def crear_seccion(self):
        peso_frame = tk.LabelFrame(self.parent, text=" Control de Pesaje ", 
                                 font=('Arial', 10, 'bold'), bg='#f8f9fa', 
                                 fg='#2c3e50', padx=15, pady=10)
        peso_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Display de peso
        display_frame = tk.Frame(peso_frame, bg='#1a1a1a', relief=tk.RAISED, bd=2)
        display_frame.grid(row=0, column=0, rowspan=3, padx=10, pady=10, sticky='w')
        
        tk.Label(display_frame, text="PESO ACTUAL", font=('Arial', 9, 'bold'), 
                bg='#1a1a1a', fg='#cccccc').pack(pady=(10, 2))
        
        self.label_peso = tk.Label(display_frame, textvariable=self.controlador.peso_actual, 
                                 font=('Courier New', 28, 'bold'), bg='#1a1a1a', fg='#00ff41',
                                 width=10)
        self.label_peso.pack(pady=(0, 2))
        
        tk.Label(display_frame, text="Kilogramos", font=('Arial', 8), 
                bg='#1a1a1a', fg='#cccccc').pack(pady=(0, 10))
        
        # Fardo actual
        self.label_fardo_actual = tk.Label(peso_frame, text="", 
                                         font=('Arial', 12, 'bold'), bg='#f8f9fa', fg='#27ae60')
        self.label_fardo_actual.grid(row=0, column=1, sticky='w', padx=10, pady=5)
        
        # Campo para capturar Enter
        self.entry_pesar = tk.Entry(peso_frame, font=('Arial', 1), width=1, 
                                  relief=tk.FLAT, bd=0, bg='#f8f9fa', fg='#f8f9fa',
                                  insertbackground='#f8f9fa')
        self.entry_pesar.grid(row=1, column=1)
        self.entry_pesar.bind('<Return>', lambda e: self.controlador.pesar_fardo())
        
        # Botones de acción - más pequeños y prolijos
        buttons_frame = tk.Frame(peso_frame, bg='#f8f9fa')
        buttons_frame.grid(row=2, column=1, sticky='w', padx=10, pady=5)
        
        self.btn_pesar = tk.Button(buttons_frame, text="PESAR", 
                                 font=('Arial', 9, 'bold'), bg='#3498db', fg='white',
                                 command=self.controlador.pesar_fardo, state=tk.DISABLED, width=10,
                                 relief=tk.FLAT, bd=0, cursor='hand2', padx=5, pady=3)
        self.btn_pesar.pack(side=tk.LEFT)
        
        # Información
        info_frame = tk.Frame(peso_frame, bg='#f8f9fa')
        info_frame.grid(row=3, column=0, columnspan=2, sticky='w', padx=10, pady=5)
        
        tk.Label(info_frame, text="💡 Presione Enter para pesar rápidamente", 
                font=('Arial', 9), bg='#f8f9fa', fg='#7f8c8d').pack()
    
    def actualizar_display_fardo(self, fardo_actual, modo_repeso):
        if modo_repeso:
            self.label_fardo_actual.config(text=f"🔄 REPESANDO FARDO: {fardo_actual}")
        else:
            self.label_fardo_actual.config(text=f"📦 FARDO ACTUAL: {fardo_actual}")
    
    def configurar_modo_repeso(self, activo, fardo_repeso=None):
        if activo:
            self.btn_pesar.config(text="REPESAR", bg='#f39c12')
            self.actualizar_display_fardo(fardo_repeso, True)
        else:
            self.btn_pesar.config(text="PESAR", bg='#3498db')
            self.actualizar_display_fardo(self.controlador.fardo_actual, False)
    
    def resetear(self):
        self.label_fardo_actual.config(text="")
        self.btn_pesar.config(state=tk.DISABLED, text="PESAR", bg='#3498db')

class TablaRegistros:
    def __init__(self, parent, controlador):
        self.parent = parent
        self.controlador = controlador
        self.crear_tabla()
        
    def crear_tabla(self):
        tabla_container = tk.LabelFrame(self.parent, text=" Registro de Fardos ", 
                                      font=('Arial', 10, 'bold'), bg='#f8f9fa', 
                                      fg='#2c3e50', padx=10, pady=10)
        tabla_container.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Información del ticket - Subsección destacada
        info_frame = tk.LabelFrame(tabla_container, text=" Información Actual ", 
                                 font=('Arial', 9, 'bold'), bg='#f0f0f0', 
                                 fg='#2c3e50', padx=10, pady=5)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Usar grid para mejor organización
        # Ticket
        tk.Label(info_frame, text="N° Ticket:", 
               font=('Arial', 9, 'bold'), bg='#f0f0f0', fg='#2c3e50').grid(row=0, column=0, sticky='w', pady=2)
        
        self.label_ticket_info = tk.Label(info_frame, text="--", 
                                        font=('Arial', 9), bg='#f0f0f0', fg='#e74c3c')
        self.label_ticket_info.grid(row=0, column=1, sticky='w', padx=5, pady=2)
        
        # Fardo
        tk.Label(info_frame, text="N° Fardo:", 
               font=('Arial', 9, 'bold'), bg='#f0f0f0', fg='#2c3e50').grid(row=1, column=0, sticky='w', pady=2)
        
        self.label_fardo_info = tk.Label(info_frame, text="--", 
                                       font=('Arial', 9), bg='#f0f0f0', fg='#27ae60')
        self.label_fardo_info.grid(row=1, column=1, sticky='w', padx=5, pady=2)
        
        # Estadísticas
        stats_frame = tk.LabelFrame(tabla_container, text=" Estadísticas ", 
                                  font=('Arial', 9, 'bold'), bg='#f0f0f0', 
                                  fg='#2c3e50', padx=10, pady=5)
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Total de fardos
        tk.Label(stats_frame, text="Total fardos:", 
               font=('Arial', 9, 'bold'), bg='#f0f0f0', fg='#2c3e50').grid(row=0, column=0, sticky='w', pady=2)
        
        self.label_total_fardos = tk.Label(stats_frame, text="0", 
                                         font=('Arial', 9), bg='#f0f0f0', fg='#3498db')
        self.label_total_fardos.grid(row=0, column=1, sticky='w', padx=5, pady=2)
        
        # Peso total
        tk.Label(stats_frame, text="Peso total:", 
               font=('Arial', 9, 'bold'), bg='#f0f0f0', fg='#2c3e50').grid(row=1, column=0, sticky='w', pady=2)
        
        self.label_peso_total = tk.Label(stats_frame, text="0.00 kg", 
                                       font=('Arial', 9), bg='#f0f0f0', fg='#3498db')
        self.label_peso_total.grid(row=1, column=1, sticky='w', padx=5, pady=2)
        
        tabla_frame = tk.Frame(tabla_container, bg='#f8f9fa')
        tabla_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configurar Treeview
        columns = ('Fardo', 'Peso', 'Fecha', 'Hora')
        self.tree = ttk.Treeview(tabla_frame, columns=columns, show='headings', height=10)
        
        # Configurar columnas
        self.tree.heading('Fardo', text='N° Fardo')
        self.tree.heading('Peso', text='Peso (kg)')
        self.tree.heading('Fecha', text='Fecha')
        self.tree.heading('Hora', text='Hora')
        
        self.tree.column('Fardo', width=100, anchor=tk.CENTER)
        self.tree.column('Peso', width=120, anchor=tk.CENTER)
        self.tree.column('Fecha', width=120, anchor=tk.CENTER)
        self.tree.column('Hora', width=100, anchor=tk.CENTER)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tabla_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind
        self.tree.bind('<Button-1>', self.seleccionar_fardo)
        
        # Contador de fardos
        self.label_contador = tk.Label(tabla_container, text="Fardos registrados: 0", 
                                     font=('Arial', 9), bg='#f8f9fa', fg='#7f8c8d')
        self.label_contador.pack(pady=(5, 0))
        
    def actualizar_info_ticket(self, numero_ticket, fardo_actual):
        """Actualiza la información del ticket y fardo actual"""
        self.label_ticket_info.config(text=f"{numero_ticket}")
        self.label_fardo_info.config(text=f"{fardo_actual}")
        
    def resetear_info_ticket(self):
        """Resetea la información del ticket y fardo actual"""
        self.label_ticket_info.config(text="--")
        self.label_fardo_info.config(text="--")
    
    def seleccionar_fardo(self, event):
        item = self.tree.selection()[0] if self.tree.selection() else None
        if item:
            self.controlador.fardo_seleccionado = self.tree.item(item, 'values')
    
    def agregar_fardo(self, fardo, peso, fecha, hora):
        self.tree.insert('', 'end', values=(fardo, f"{peso:.2f}", fecha, hora))
        self.actualizar_contador()
        self.actualizar_estadisticas()
        if self.tree.get_children():
            self.tree.see(self.tree.get_children()[-1])
    
    def actualizar_fardo(self, fardo, peso, fecha, hora):
        for item in self.tree.get_children():
            valores = self.tree.item(item, 'values')
            if int(valores[0]) == fardo:
                self.tree.item(item, values=(fardo, f"{peso:.2f}", fecha, hora))
                break
        self.actualizar_estadisticas()
    
    def actualizar_contador(self):
        count = len(self.tree.get_children())
        self.label_contador.config(text=f"Fardos registrados: {count}")
        self.label_total_fardos.config(text=f"{count}")
    
    def actualizar_estadisticas(self):
        """Actualiza las estadísticas de peso total"""
        peso_total = 0.0
        for item in self.tree.get_children():
            valores = self.tree.item(item, 'values')
            try:
                peso_total += float(valores[1])
            except (ValueError, IndexError):
                pass
        
        self.label_peso_total.config(text=f"{peso_total:.2f} kg")
        
        # Actualizar rinde si hay datos
        try:
            self.controlador.seccion_entrada.calcular_rinde()
        except:
            pass
            
    def obtener_peso_total(self):
        """Retorna el peso total de los fardos"""
        peso_total = 0.0
        for item in self.tree.get_children():
            valores = self.tree.item(item, 'values')
            try:
                peso_total += float(valores[1])
            except (ValueError, IndexError):
                pass
        return peso_total
    
    def limpiar_tabla(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.actualizar_contador()
        self.actualizar_estadisticas()

class BotonesPrincipales:
    def __init__(self, parent, controlador):
        self.parent = parent
        self.controlador = controlador
        self.crear_botones()
        
    def crear_botones(self):
        # Usar grid para mejor organización
        botones_container = tk.Frame(self.parent, bg='#f8f9fa')
        botones_container.pack(fill=tk.X, pady=10)
        
        # Configurar columnas para centrar los botones
        botones_container.grid_columnconfigure(0, weight=1)
        botones_container.grid_columnconfigure(1, weight=1)
        botones_container.grid_columnconfigure(2, weight=1)
        botones_container.grid_columnconfigure(3, weight=1)
        
        # Botón Nuevo Ticket - más pequeño y prolijo
        self.btn_nuevo_ticket = tk.Button(botones_container, text="📋 NUEVO TICKET", 
                                        font=('Arial', 10, 'bold'), bg='#e74c3c', fg='white',
                                        command=self.controlador.nuevo_ticket, width=15, height=1,
                                        relief=tk.FLAT, bd=0, cursor='hand2', padx=5, pady=5)
        self.btn_nuevo_ticket.grid(row=0, column=0, padx=10, pady=5)
        
        # Botón Historial
        self.btn_historial = tk.Button(botones_container, text="📊 HISTORIAL", 
                                     font=('Arial', 10, 'bold'), bg='#9b59b6', fg='white',
                                     command=self.controlador.mostrar_historial, width=15, height=1,
                                     relief=tk.FLAT, bd=0, cursor='hand2', padx=5, pady=5)
        self.btn_historial.grid(row=0, column=1, padx=10, pady=5)
        
        # Botón Repesar
        self.btn_repesar = tk.Button(botones_container, text="🔁 REPESAR", 
                                    font=('Arial', 10, 'bold'), bg='#f39c12', fg='white',
                                    command=lambda: self.controlador.iniciar_repeso(
                                        self.controlador.tabla_registros.tree.item(
                                            self.controlador.tabla_registros.tree.selection()[0], 'values')
                                        if self.controlador.tabla_registros.tree.selection() else None
                                    ), width=15, height=1,
                                    state=tk.DISABLED, relief=tk.FLAT, bd=0, cursor='hand2', padx=5, pady=5)
        self.btn_repesar.grid(row=0, column=2, padx=10, pady=5)
        
        # Botón Guardar
        self.btn_guardar = tk.Button(botones_container, text="💾 GUARDAR", 
                                   font=('Arial', 10, 'bold'), bg='#27ae60', fg='white',
                                   command=self.controlador.guardar_datos, width=15, height=1, 
                                   state=tk.DISABLED, relief=tk.FLAT, bd=0, cursor='hand2', padx=5, pady=5)
        self.btn_guardar.grid(row=0, column=3, padx=10, pady=5)
    
    def habilitar_controles(self, habilitar):
        """Habilita o deshabilita los controles"""
        self.btn_repesar.config(state=tk.NORMAL if habilitar else tk.DISABLED)
        # Siempre habilitar el botón guardar cuando hay fardos
        self.btn_guardar.config(state=tk.NORMAL if habilitar else tk.DISABLED)
        
    def habilitar_boton_guardar(self, habilitar):
        """Habilita o deshabilita el botón guardar"""
        self.btn_guardar.config(state=tk.NORMAL if habilitar else tk.DISABLED)
        
    def resetear(self):
        """Resetea los botones a su estado inicial"""
        self.btn_guardar.config(state=tk.DISABLED)
        self.btn_repesar.config(state=tk.DISABLED)
    
    def habilitar_controles(self, habilitar):
        self.btn_repesar.config(state=tk.NORMAL if habilitar else tk.DISABLED)
        self.btn_guardar.config(state=tk.NORMAL if habilitar else tk.DISABLED)
    
    def habilitar_boton_guardar(self, habilitar):
        self.btn_guardar.config(state=tk.NORMAL if habilitar else tk.DISABLED)
    
    def resetear(self):
        self.btn_guardar.config(state=tk.DISABLED)
        self.btn_repesar.config(state=tk.DISABLED)




class BarraEstado:
    def __init__(self, parent, controlador):
        self.parent = parent
        self.controlador = controlador
        self.crear_barra()
        
    def crear_barra(self):
        # Asegurarse de que la barra de estado esté en la parte inferior
        estado_frame = tk.Frame(self.parent, bg='#34495e', relief=tk.SUNKEN, bd=1, height=25)
        estado_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 0))
        estado_frame.pack_propagate(False)  # Mantener altura fija
        
        # Base de datos
        bd_frame = tk.Frame(estado_frame, bg='#34495e')
        bd_frame.pack(side=tk.LEFT, padx=10, pady=3)
        
        self.label_bd_icon = tk.Label(bd_frame, text="🗄️", font=('Arial', 10), bg='#34495e', fg='white')
        self.label_bd_icon.pack(side=tk.LEFT)
        
        self.label_bd = tk.Label(bd_frame, textvariable=self.controlador.conexion_bd, 
                               font=('Arial', 9), bg='#34495e', fg='#e74c3c')
        self.label_bd.pack(side=tk.LEFT, padx=(3, 0))
        
        # Separador
        sep1 = tk.Label(estado_frame, text="│", font=('Arial', 12), bg='#34495e', fg='#7f8c8d')
        sep1.pack(side=tk.LEFT, padx=5)
        
        # Balanza
        balanza_frame = tk.Frame(estado_frame, bg='#34495e')
        balanza_frame.pack(side=tk.LEFT, padx=5, pady=3)
        
        self.label_balanza_icon = tk.Label(balanza_frame, text="⚖️", font=('Arial', 10), bg='#34495e', fg='white')
        self.label_balanza_icon.pack(side=tk.LEFT)
        
        self.label_balanza = tk.Label(balanza_frame, textvariable=self.controlador.conexion_balanza, 
                                    font=('Arial', 9), bg='#34495e', fg='#e74c3c')
        self.label_balanza.pack(side=tk.LEFT, padx=(3, 0))
        
        self.label_nombre_balanza = tk.Label(balanza_frame, textvariable=self.controlador.nombre_balanza, 
                                           font=('Arial', 9), bg='#34495e', fg='#95a5a6')
        self.label_nombre_balanza.pack(side=tk.LEFT, padx=(5, 0))
        
        # Separador
        sep2 = tk.Label(estado_frame, text="│", font=('Arial', 12), bg='#34495e', fg='#7f8c8d')
        sep2.pack(side=tk.LEFT, padx=5)
        
        # Internet
        internet_frame = tk.Frame(estado_frame, bg='#34495e')
        internet_frame.pack(side=tk.LEFT, padx=5, pady=3)
        
        self.label_internet_icon = tk.Label(internet_frame, text="🌐", font=('Arial', 10), bg='#34495e', fg='white')
        self.label_internet_icon.pack(side=tk.LEFT)
        
        self.label_internet = tk.Label(internet_frame, textvariable=self.controlador.estado_internet, 
                                     font=('Arial', 9), bg='#34495e', fg='#e74c3c')
        self.label_internet.pack(side=tk.LEFT, padx=(3, 0))
        
        # Información del sistema
        info_sistema = tk.Label(estado_frame, text="Sistema v1.0 - Listo", 
                              font=('Arial', 9), bg='#34495e', fg='#95a5a6')
        info_sistema.pack(side=tk.RIGHT, padx=10, pady=3)
    
    def actualizar_estados(self, bd_ok, balanza_ok, nombre_balanza, internet_ok):
        # Base de datos
        if bd_ok:
            self.controlador.conexion_bd.set("Conectado")
            self.label_bd.config(fg='#27ae60')
        else:
            self.controlador.conexion_bd.set("Desconectado")
            self.label_bd.config(fg='#e74c3c')
        
        # Balanza
        if balanza_ok:
            self.controlador.conexion_balanza.set("Conectado")
            self.label_balanza.config(fg='#27ae60')
            self.controlador.nombre_balanza.set(f"({nombre_balanza})")
        else:
            self.controlador.conexion_balanza.set("Desconectado")
            self.label_balanza.config(fg='#e74c3c')
            self.controlador.nombre_balanza.set("(No detectada)")
        
        # Internet
        if internet_ok:
            self.controlador.estado_internet.set("Conectado")
            self.label_internet.config(fg='#27ae60')
        else:
            self.controlador.estado_internet.set("Sin conexión")
            self.label_internet.config(fg='#e74c3c')
    
    def actualizar_estados(self, bd_ok, balanza_ok, nombre_balanza, internet_ok):
        # Base de datos
        if bd_ok:
            self.controlador.conexion_bd.set("Conectado")
            self.label_bd.config(fg='#27ae60')
        else:
            self.controlador.conexion_bd.set("Desconectado")
            self.label_bd.config(fg='#e74c3c')
        
        # Balanza
        if balanza_ok:
            self.controlador.conexion_balanza.set("Conectado")
            self.label_balanza.config(fg='#27ae60')
            self.controlador.nombre_balanza.set(f"({nombre_balanza})")
        else:
            self.controlador.conexion_balanza.set("Desconectado")
            self.label_balanza.config(fg='#e74c3c')
            self.controlador.nombre_balanza.set("(No detectada)")
        
        # Internet
        if internet_ok:
            self.controlador.estado_internet.set("Conectado")
            self.label_internet.config(fg='#27ae60')
        else:
            self.controlador.estado_internet.set("Sin conexión")
            self.label_internet.config(fg='#e74c3c')