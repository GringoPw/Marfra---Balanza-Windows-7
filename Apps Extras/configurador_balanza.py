import json
import os
import tkinter as tk
from tkinter import ttk, messagebox

class ConfiguradorBalanza:
    def __init__(self, root):
        self.root = root
        self.root.title("Configurador de Balanzas")
        self.root.geometry("800x600")
        
        # Ruta del archivo de configuración
        self.config_file = "configuracion.json"
        
        # Cargar configuración existente
        self.cargar_configuracion()
        
        # Crear interfaz
        self.crear_interfaz()
    
    def cargar_configuracion(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
                    # Asegurar que existe la sección balanzas
                    if 'balanzas' not in self.config:
                        self.config['balanzas'] = {}
                    # Verificar si existe balanza_por_defecto
                    if 'balanza_por_defecto' not in self.config:
                        self.config['balanza_por_defecto'] = ""
            else:
                # Crear configuración por defecto
                self.config = {
                    'balanzas': {},
                    'balanza_por_defecto': ""
                }
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar la configuración: {str(e)}")
            self.config = {'balanzas': {}, 'balanza_por_defecto': ""}
    
    def guardar_configuracion(self):
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            messagebox.showinfo("Éxito", "Configuración guardada correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar la configuración: {str(e)}")
    
    def crear_interfaz(self):
        # Frame principal con pestañas
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Pestaña de lista de balanzas
        tab_lista = ttk.Frame(notebook)
        notebook.add(tab_lista, text="Lista de Balanzas")
        
        # Pestaña de edición
        self.tab_edicion = ttk.Frame(notebook)
        notebook.add(self.tab_edicion, text="Editar Balanza")
        
        # Contenido de la pestaña de lista
        self.crear_tab_lista(tab_lista)
        
        # Contenido de la pestaña de edición
        self.crear_tab_edicion()
    
    def crear_tab_lista(self, tab):
        # Frame superior con botones
        frame_botones = ttk.Frame(tab)
        frame_botones.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(frame_botones, text="Nueva Balanza", command=self.nueva_balanza).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="Eliminar Balanza", command=self.eliminar_balanza).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="Guardar Cambios", command=self.guardar_configuracion).pack(side='right', padx=5)
        
        # Frame para la lista de balanzas y selección de balanza por defecto
        frame_lista = ttk.Frame(tab)
        frame_lista.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Lista de balanzas
        ttk.Label(frame_lista, text="Balanzas configuradas:").pack(anchor='w', padx=5, pady=5)
        
        # Frame para la lista y scrollbar
        frame_treeview = ttk.Frame(frame_lista)
        frame_treeview.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_treeview)
        scrollbar.pack(side='right', fill='y')
        
        # Treeview para mostrar las balanzas
        self.tree = ttk.Treeview(frame_treeview, columns=('ID', 'Nombre', 'Puerto', 'Unidad'), show='headings')
        self.tree.heading('ID', text='ID')
        self.tree.heading('Nombre', text='Nombre')
        self.tree.heading('Puerto', text='Puerto')
        self.tree.heading('Unidad', text='Unidad')
        self.tree.column('ID', width=100)
        self.tree.column('Nombre', width=200)
        self.tree.column('Puerto', width=100)
        self.tree.column('Unidad', width=100)
        self.tree.pack(side='left', fill='both', expand=True)
        
        # Configurar scrollbar
        scrollbar.config(command=self.tree.yview)
        self.tree.config(yscrollcommand=scrollbar.set)
        
        # Evento de doble clic para editar
        self.tree.bind('<Double-1>', self.editar_balanza)
        
        # Frame para seleccionar balanza por defecto
        frame_defecto = ttk.Frame(tab)
        frame_defecto.pack(fill='x', padx=5, pady=10)
        
        ttk.Label(frame_defecto, text="Balanza por defecto:").pack(side='left', padx=5)
        
        # Combobox para seleccionar balanza por defecto
        self.combo_defecto = ttk.Combobox(frame_defecto, state="readonly")
        self.combo_defecto.pack(side='left', padx=5, fill='x', expand=True)
        
        ttk.Button(frame_defecto, text="Establecer como predeterminada", 
                  command=self.establecer_balanza_defecto).pack(side='left', padx=5)
        
        # Cargar balanzas en la lista
        self.actualizar_lista_balanzas()
    
    def crear_tab_edicion(self):
        # Variables para los campos
        self.var_id = tk.StringVar()
        self.var_nombre = tk.StringVar()
        self.var_puerto = tk.StringVar()
        self.var_baudrate = tk.IntVar(value=9600)
        self.var_bytesize = tk.IntVar(value=8)
        self.var_parity = tk.StringVar(value="none")
        self.var_stopbits = tk.IntVar(value=1)
        self.var_timeout = tk.IntVar(value=1)
        self.var_xonxoff = tk.BooleanVar(value=False)
        self.var_rtscts = tk.BooleanVar(value=False)
        self.var_dsrdtr = tk.BooleanVar(value=False)
        self.var_dtr = tk.BooleanVar(value=True)
        self.var_rts = tk.BooleanVar(value=True)
        self.var_unidad = tk.StringVar(value="kg")
        
        # Frame principal
        main_frame = ttk.Frame(self.tab_edicion)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Crear un canvas con scrollbar
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Campos de edición
        ttk.Label(scrollable_frame, text="ID de la balanza:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        ttk.Entry(scrollable_frame, textvariable=self.var_id).grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        
        ttk.Label(scrollable_frame, text="Nombre:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        ttk.Entry(scrollable_frame, textvariable=self.var_nombre).grid(row=1, column=1, sticky='ew', padx=5, pady=5)
        
        ttk.Label(scrollable_frame, text="Puerto:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        ttk.Entry(scrollable_frame, textvariable=self.var_puerto).grid(row=2, column=1, sticky='ew', padx=5, pady=5)
        
        ttk.Label(scrollable_frame, text="Baudrate:").grid(row=3, column=0, sticky='w', padx=5, pady=5)
        ttk.Combobox(scrollable_frame, textvariable=self.var_baudrate, 
                    values=[1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200]).grid(row=3, column=1, sticky='ew', padx=5, pady=5)
        
        ttk.Label(scrollable_frame, text="Bytesize:").grid(row=4, column=0, sticky='w', padx=5, pady=5)
        ttk.Combobox(scrollable_frame, textvariable=self.var_bytesize, 
                    values=[5, 6, 7, 8]).grid(row=4, column=1, sticky='ew', padx=5, pady=5)
        
        ttk.Label(scrollable_frame, text="Parity:").grid(row=5, column=0, sticky='w', padx=5, pady=5)
        ttk.Combobox(scrollable_frame, textvariable=self.var_parity, 
                    values=["none", "even", "odd", "mark", "space"]).grid(row=5, column=1, sticky='ew', padx=5, pady=5)
        
        ttk.Label(scrollable_frame, text="Stopbits:").grid(row=6, column=0, sticky='w', padx=5, pady=5)
        ttk.Combobox(scrollable_frame, textvariable=self.var_stopbits, 
                    values=[1, 1.5, 2]).grid(row=6, column=1, sticky='ew', padx=5, pady=5)
        
        ttk.Label(scrollable_frame, text="Timeout:").grid(row=7, column=0, sticky='w', padx=5, pady=5)
        ttk.Entry(scrollable_frame, textvariable=self.var_timeout).grid(row=7, column=1, sticky='ew', padx=5, pady=5)
        
        ttk.Label(scrollable_frame, text="Unidad:").grid(row=8, column=0, sticky='w', padx=5, pady=5)
        ttk.Combobox(scrollable_frame, textvariable=self.var_unidad, 
                    values=["kg", "g", "lb", "oz"]).grid(row=8, column=1, sticky='ew', padx=5, pady=5)
        
        # Checkboxes
        ttk.Checkbutton(scrollable_frame, text="XON/XOFF", variable=self.var_xonxoff).grid(row=9, column=0, columnspan=2, sticky='w', padx=5, pady=5)
        ttk.Checkbutton(scrollable_frame, text="RTS/CTS", variable=self.var_rtscts).grid(row=10, column=0, columnspan=2, sticky='w', padx=5, pady=5)
        ttk.Checkbutton(scrollable_frame, text="DSR/DTR", variable=self.var_dsrdtr).grid(row=11, column=0, columnspan=2, sticky='w', padx=5, pady=5)
        ttk.Checkbutton(scrollable_frame, text="DTR", variable=self.var_dtr).grid(row=12, column=0, columnspan=2, sticky='w', padx=5, pady=5)
        ttk.Checkbutton(scrollable_frame, text="RTS", variable=self.var_rts).grid(row=13, column=0, columnspan=2, sticky='w', padx=5, pady=5)
        
        # Botones
        frame_botones = ttk.Frame(scrollable_frame)
        frame_botones.grid(row=14, column=0, columnspan=2, pady=10)
        
        ttk.Button(frame_botones, text="Guardar", command=self.guardar_balanza).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="Cancelar", command=self.cancelar_edicion).pack(side='left', padx=5)
        
        # Configurar grid
        scrollable_frame.columnconfigure(1, weight=1)
    
    def actualizar_lista_balanzas(self):
        # Limpiar lista actual
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Actualizar combobox de balanza por defecto
        balanzas_ids = list(self.config['balanzas'].keys())
        self.combo_defecto['values'] = balanzas_ids
        
        # Seleccionar la balanza por defecto actual
        if 'balanza_por_defecto' in self.config and self.config['balanza_por_defecto'] in balanzas_ids:
            self.combo_defecto.set(self.config['balanza_por_defecto'])
        
        # Llenar la lista con las balanzas
        for balanza_id, datos in self.config['balanzas'].items():
            self.tree.insert('', 'end', values=(
                balanza_id,
                datos.get('nombre', ''),
                datos.get('puerto', ''),
                datos.get('unidad', '')
            ))
    
    def nueva_balanza(self):
        # Limpiar campos
        self.var_id.set("")
        self.var_nombre.set("")
        self.var_puerto.set("")
        self.var_baudrate.set(9600)
        self.var_bytesize.set(8)
        self.var_parity.set("none")
        self.var_stopbits.set(1)
        self.var_timeout.set(1)
        self.var_xonxoff.set(False)
        self.var_rtscts.set(False)
        self.var_dsrdtr.set(False)
        self.var_dtr.set(True)
        self.var_rts.set(True)
        self.var_unidad.set("kg")
        
        # Cambiar a la pestaña de edición
        self.root.nametowidget('.!notebook').select(1)
    
    def editar_balanza(self, event):
        # Obtener el item seleccionado
        item = self.tree.selection()[0]
        balanza_id = self.tree.item(item, 'values')[0]
        
        # Cargar datos de la balanza
        if balanza_id in self.config['balanzas']:
            datos = self.config['balanzas'][balanza_id]
            
            self.var_id.set(balanza_id)
            self.var_nombre.set(datos.get('nombre', ''))
            self.var_puerto.set(datos.get('puerto', ''))
            self.var_baudrate.set(datos.get('baudrate', 9600))
            self.var_bytesize.set(datos.get('bytesize', 8))
            self.var_parity.set(datos.get('parity', 'none'))
            self.var_stopbits.set(datos.get('stopbits', 1))
            self.var_timeout.set(datos.get('timeout', 1))
            self.var_xonxoff.set(datos.get('xonxoff', False))
            self.var_rtscts.set(datos.get('rtscts', False))
            self.var_dsrdtr.set(datos.get('dsrdtr', False))
            self.var_dtr.set(datos.get('dtr', True))
            self.var_rts.set(datos.get('rts', True))
            self.var_unidad.set(datos.get('unidad', 'kg'))
            
            # Cambiar a la pestaña de edición
            self.root.nametowidget('.!notebook').select(1)
    
    def guardar_balanza(self):
        # Validar campos obligatorios
        if not self.var_id.get() or not self.var_nombre.get() or not self.var_puerto.get():
            messagebox.showerror("Error", "Los campos ID, Nombre y Puerto son obligatorios")
            return
        
        # Crear diccionario con los datos de la balanza
        balanza_id = self.var_id.get()
        datos = {
            'nombre': self.var_nombre.get(),
            'puerto': self.var_puerto.get(),
            'baudrate': self.var_baudrate.get(),
            'bytesize': self.var_bytesize.get(),
            'parity': self.var_parity.get(),
            'stopbits': self.var_stopbits.get(),
            'timeout': self.var_timeout.get(),
            'xonxoff': self.var_xonxoff.get(),
            'rtscts': self.var_rtscts.get(),
            'dsrdtr': self.var_dsrdtr.get(),
            'dtr': self.var_dtr.get(),
            'rts': self.var_rts.get(),
            'unidad': self.var_unidad.get()
        }
        
        # Guardar en la configuración
        self.config['balanzas'][balanza_id] = datos
        
        # Si es la primera balanza, establecerla como predeterminada
        if len(self.config['balanzas']) == 1 and not self.config.get('balanza_por_defecto'):
            self.config['balanza_por_defecto'] = balanza_id
        
        # Actualizar lista
        self.actualizar_lista_balanzas()
        
        # Volver a la pestaña de lista
        self.root.nametowidget('.!notebook').select(0)
        
        messagebox.showinfo("Éxito", f"Balanza '{balanza_id}' guardada correctamente")
    
    def eliminar_balanza(self):
        # Verificar si hay una balanza seleccionada
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione una balanza para eliminar")
            return
        
        # Obtener el ID de la balanza
        item = seleccion[0]
        balanza_id = self.tree.item(item, 'values')[0]
        
        # Confirmar eliminación
        if messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar la balanza '{balanza_id}'?"):
            # Eliminar de la configuración
            if balanza_id in self.config['balanzas']:
                del self.config['balanzas'][balanza_id]
                
                # Si era la balanza por defecto, quitar esa configuración
                if self.config.get('balanza_por_defecto') == balanza_id:
                    self.config['balanza_por_defecto'] = ""
                
                # Actualizar lista
                self.actualizar_lista_balanzas()
                
                messagebox.showinfo("Éxito", f"Balanza '{balanza_id}' eliminada correctamente")
    
    def establecer_balanza_defecto(self):
        # Obtener la balanza seleccionada
        balanza_id = self.combo_defecto.get()
        
        if not balanza_id:
            messagebox.showwarning("Advertencia", "Seleccione una balanza para establecer como predeterminada")
            return
        
        # Establecer como predeterminada
        self.config['balanza_por_defecto'] = balanza_id
        messagebox.showinfo("Éxito", f"Balanza '{balanza_id}' establecida como predeterminada")
    
    def cancelar_edicion(self):
        # Volver a la pestaña de lista
        self.root.nametowidget('.!notebook').select(0)

if __name__ == "__main__":
    root = tk.Tk()
    app = ConfiguradorBalanza(root)
    root.mainloop()