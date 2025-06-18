import os
import sqlite3
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from ttkthemes import ThemedTk
import json
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
import subprocess
import tempfile
import math
from PIL import Image as PILImage, ImageTk

class VisorTickets:
    def __init__(self, root):
        self.root = root
        self.root.title("Visor de Tickets")
        self.root.geometry("1200x800")
        
        # Configurar estilo para Windows 11
        style = ttk.Style()
        style.theme_use("clam")  # Tema base más moderno
        
        # Personalizar colores para un aspecto más moderno
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabel", background="#f0f0f0", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10), padding=6)
        style.configure("TLabelframe", background="#f0f0f0", font=("Segoe UI", 10, "bold"))
        style.configure("TLabelframe.Label", font=("Segoe UI", 10, "bold"))
        
        # Estilo para Treeview (tabla de tickets)
        style.configure("Treeview", 
                        background="#ffffff",
                        foreground="#000000",
                        rowheight=25,
                        fieldbackground="#ffffff",
                        font=("Segoe UI", 10))
        style.configure("Treeview.Heading", 
                        font=("Segoe UI", 10, "bold"),
                        background="#e0e0e0")
        style.map("Treeview", background=[("selected", "#0078d7")])
        
        # Estilo para botones de acción principales (estilo Windows 11)
        style.configure("Accent.TButton",
                       font=("Segoe UI", 10, "bold"),
                       background="#0078d7",
                       foreground="#ffffff",
                       padding=(10, 8))
        style.map("Accent.TButton",
                 background=[("active", "#1e88e5"), ("pressed", "#0067c0")],
                 relief=[("pressed", "sunken")])
                 
        # Estilo para botones secundarios
        style.configure("Secondary.TButton",
                      font=("Segoe UI", 10),
                      padding=(8, 6))
        
        # Configuración
        self.config_file = os.path.join(os.path.dirname(__file__), "config.json")
        self.cargar_configuracion()
        
        # Variables
        self.tickets = []
        self.ticket_seleccionado = None
        
        # Crear interfaz
        self.crear_interfaz()
        
        # Cargar tickets si hay una BD configurada
        if self.db_path:
            self.cargar_tickets()
    
    def cargar_configuracion(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.db_path = config.get('db_path', '')
            else:
                self.db_path = ''
                self.guardar_configuracion()
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar la configuración: {str(e)}")
            self.db_path = ''
    
    def guardar_configuracion(self):
        try:
            config = {'db_path': self.db_path}
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar la configuración: {str(e)}")
    
    def crear_interfaz(self):
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Frame superior para configuración
        config_frame = ttk.LabelFrame(main_frame, text="Configuración")
        config_frame.pack(fill='x', padx=8, pady=8)
        
        # Ruta de la base de datos
        ttk.Label(config_frame, text="Base de datos:").grid(row=0, column=0, padx=8, pady=10, sticky='w')
        self.entry_db = ttk.Entry(config_frame, width=60, font=("Segoe UI", 10))
        self.entry_db.grid(row=0, column=1, padx=8, pady=10, sticky='ew')
        self.entry_db.insert(0, self.db_path)
        
        # Botones con iconos (simulados con texto)
        ttk.Button(config_frame, text="📂 Examinar", command=self.seleccionar_bd).grid(row=0, column=2, padx=8, pady=10)
        ttk.Button(config_frame, text="💾 Guardar", command=self.guardar_ruta_bd).grid(row=0, column=3, padx=8, pady=10)
        ttk.Button(config_frame, text="🔄 Actualizar", command=self.cargar_tickets).grid(row=0, column=4, padx=8, pady=10)
        
        config_frame.columnconfigure(1, weight=1)
        
        # Panel principal dividido en dos
        panel_frame = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        panel_frame.pack(fill='both', expand=True, padx=8, pady=8)
        
        # Panel izquierdo: Lista de tickets
        left_frame = ttk.Frame(panel_frame)
        panel_frame.add(left_frame, weight=1)
        
        list_frame = ttk.LabelFrame(left_frame, text="Lista de Tickets")
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Crear tabla de tickets con estilo mejorado
        columns = ('numero', 'fecha', 'hora', 'fardos', 'peso', 'rinde')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', selectmode='browse')
        
        # Configurar columnas
        self.tree.heading('numero', text='Número')
        self.tree.heading('fecha', text='Fecha')
        self.tree.heading('hora', text='Hora')
        self.tree.heading('fardos', text='Fardos')
        self.tree.heading('peso', text='Peso Total')
        self.tree.heading('rinde', text='Rinde')
        
        self.tree.column('numero', width=100, anchor='center')
        self.tree.column('fecha', width=100, anchor='center')
        self.tree.column('hora', width=100, anchor='center')
        self.tree.column('fardos', width=100, anchor='center')
        self.tree.column('peso', width=120, anchor='center')
        self.tree.column('rinde', width=100, anchor='center')
        
        # Scrollbars con estilo
        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(list_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Posicionar elementos
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)
        
        # Evento de selección
        self.tree.bind('<<TreeviewSelect>>', self.seleccionar_ticket)
        
        # Panel derecho: Detalles del ticket
        right_frame = ttk.Frame(panel_frame)
        panel_frame.add(right_frame, weight=1)
        
        # Frame para detalles del ticket
        self.detail_frame = ttk.LabelFrame(right_frame, text="Detalles del Ticket")
        self.detail_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Crear campos de detalles con mejor formato
        self.detalle_text = tk.Text(self.detail_frame, height=10, wrap=tk.WORD, 
                                   font=("Segoe UI", 10),
                                   bg="#ffffff", fg="#000000",
                                   padx=10, pady=10,
                                   borderwidth=1, relief="solid")
        self.detalle_text.pack(fill='both', expand=True, padx=8, pady=8)
        self.detalle_text.config(state=tk.DISABLED)
        
        # Scrollbar para el texto de detalles
        text_vsb = ttk.Scrollbar(self.detail_frame, orient="vertical", command=self.detalle_text.yview)
        self.detalle_text.configure(yscrollcommand=text_vsb.set)
        text_vsb.place(relx=1.0, rely=0.0, relheight=1.0, anchor='ne')
        
        # Frame para botones de acción
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill='x', padx=8, pady=12)
        
        # Botones modernos con iconos
        export_btn = ttk.Button(action_frame, text="📄 Exportar a PDF", command=self.exportar_pdf, 
                               width=20, style="Accent.TButton")
        export_btn.pack(side='left', padx=8)
        
        print_btn = ttk.Button(action_frame, text="🖨️ Imprimir", command=self.imprimir_ticket, 
                              width=15)
        print_btn.pack(side='left', padx=8)
        
        # Botón de ayuda
        help_btn = ttk.Button(action_frame, text="❓ Ayuda", 
                             width=10)
        help_btn.pack(side='right', padx=8)
    
    def seleccionar_bd(self):
        db_path = filedialog.askopenfilename(
            title="Seleccionar Base de Datos",
            filetypes=[("SQLite DB", "*.db"), ("Todos los archivos", "*.*")]
        )
        if db_path:
            self.entry_db.delete(0, tk.END)
            self.entry_db.insert(0, db_path)
    
    def guardar_ruta_bd(self):
        self.db_path = self.entry_db.get()
        self.guardar_configuracion()
        self.cargar_tickets()
        messagebox.showinfo("Éxito", "Ruta de base de datos guardada correctamente")
    
    def cargar_tickets(self):
        # Limpiar lista actual
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.tickets = []
        
        if not self.db_path or not os.path.exists(self.db_path):
            messagebox.showwarning("Advertencia", "No se ha configurado una base de datos válida")
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Verificar qué tablas existen en la base de datos
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tablas = [tabla[0] for tabla in cursor.fetchall()]
            
            if 'tickets' not in tablas or 'fardos' not in tablas:
                messagebox.showerror("Error", f"No se encontraron las tablas necesarias en la base de datos.\nTablas disponibles: {', '.join(tablas)}")
                conn.close()
                return
            
            # Consulta para obtener tickets con sus fardos
            cursor.execute("""
                SELECT t.id, t.numero, t.fecha_creacion, 
                       COUNT(f.id) as cantidad_fardos,
                       COALESCE(SUM(f.peso), 0) as peso_total,
                       '' as operador,
                       t.observaciones,
                       t.kg_bruto_romaneo,
                       t.agregado,
                       t.resto
                FROM tickets t
                LEFT JOIN fardos f ON t.id = f.ticket_id
                WHERE t.estado = 'ACTIVO'
                GROUP BY t.id, t.numero, t.fecha_creacion
                ORDER BY t.fecha_creacion DESC
            """)
            
            rows = cursor.fetchall()
            
            for row in rows:
                # Convertir fecha ISO a formato legible
                fecha_creacion = datetime.fromisoformat(row[2]) if row[2] else datetime.now()
                fecha_formateada = fecha_creacion.strftime("%d/%m/%Y")
                hora_formateada = fecha_creacion.strftime("%H:%M:%S")
                
                ticket = {
                    'id': row[0],
                    'numero': row[1],
                    'fecha': fecha_formateada,
                    'hora': hora_formateada,
                    'cantidad_fardos': row[3],
                    'peso': row[4],
                    'operador': row[5],
                    'observaciones': row[6],
                    'kg_bruto_romaneo': row[7] if row[7] is not None else 0,
                    'agregado': row[8] if row[8] is not None else 0,
                    'resto': row[9] if row[9] is not None else 0
                }
                self.tickets.append(ticket)
                
                # Calcular rinde si es posible
                rinde = 0
                if ticket['kg_bruto_romaneo'] > 0:
                    tara = ticket['cantidad_fardos'] * 2  # 2kg por fardo
                    rinde = ((ticket['peso'] + ticket['resto'] - ticket['agregado'] - tara) / ticket['kg_bruto_romaneo']) * 100
                    rinde = round(rinde, 2)
                
                self.tree.insert('', 'end', values=(
                    ticket['numero'],
                    ticket['fecha'],
                    ticket['hora'],
                    f"{ticket['cantidad_fardos']} fardos",
                    f"{ticket['peso']:.2f} kg",
                    f"{rinde:.2f}%"
                ))
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar los tickets: {str(e)}")
    
    def seleccionar_ticket(self, event):
        seleccion = self.tree.selection()
        if not seleccion:
            return
        
        item = seleccion[0]
        numero_ticket = self.tree.item(item, 'values')[0]
        
        # Buscar el ticket en la lista
        for ticket in self.tickets:
            if str(ticket['numero']) == str(numero_ticket):
                self.ticket_seleccionado = ticket
                self.cargar_detalles_fardos()
                self.mostrar_detalles_ticket()
                break
    
    def cargar_detalles_fardos(self):
        """Carga los detalles de los fardos del ticket seleccionado"""
        if not self.ticket_seleccionado:
            return
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Obtener los fardos del ticket
            cursor.execute("""
                SELECT f.numero, f.peso, f.hora_pesaje
                FROM fardos f
                JOIN tickets t ON f.ticket_id = t.id
                WHERE t.numero = ?
                ORDER BY f.numero
            """, (self.ticket_seleccionado['numero'],))
            
            fardos = cursor.fetchall()
            self.ticket_seleccionado['fardos'] = []
            
            for fardo in fardos:
                self.ticket_seleccionado['fardos'].append({
                    'numero': fardo[0],
                    'peso': fardo[1],
                    'hora_pesaje': fardo[2]
                })
                
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar detalles de fardos: {str(e)}")
    
    def mostrar_detalles_ticket(self):
        if not self.ticket_seleccionado:
            return
        
        # Habilitar el widget de texto para edición
        self.detalle_text.config(state=tk.NORMAL)
        self.detalle_text.delete(1.0, tk.END)
        
        # Calcular rinde
        rinde = 0
        if self.ticket_seleccionado['kg_bruto_romaneo'] > 0:
            tara = self.ticket_seleccionado['cantidad_fardos'] * 2  # 2kg por fardo
            rinde = ((self.ticket_seleccionado['peso'] + self.ticket_seleccionado['resto'] - 
                     self.ticket_seleccionado['agregado'] - tara) / 
                     self.ticket_seleccionado['kg_bruto_romaneo']) * 100
            rinde = round(rinde, 2)
        
        # Formatear detalles con mejor estilo
        self.detalle_text.tag_configure("titulo", font=("Segoe UI", 14, "bold"), foreground="#0078d7")
        self.detalle_text.tag_configure("subtitulo", font=("Segoe UI", 12, "bold"), foreground="#333333")
        self.detalle_text.tag_configure("etiqueta", font=("Segoe UI", 10, "bold"), foreground="#555555")
        self.detalle_text.tag_configure("valor", font=("Segoe UI", 10), foreground="#000000")
        self.detalle_text.tag_configure("destacado", font=("Segoe UI", 11, "bold"), foreground="#0078d7")
        self.detalle_text.tag_configure("separador", font=("Segoe UI", 1))
        
        # Título
        self.detalle_text.insert(tk.END, f"\nTICKET DE PESAJE #{self.ticket_seleccionado['numero']}\n", "titulo")
        self.detalle_text.insert(tk.END, "\n", "separador")
        
        # Información principal
        self.detalle_text.insert(tk.END, "Fecha: ", "etiqueta")
        self.detalle_text.insert(tk.END, f"{self.ticket_seleccionado['fecha']}\n", "valor")
        
        self.detalle_text.insert(tk.END, "Hora: ", "etiqueta")
        self.detalle_text.insert(tk.END, f"{self.ticket_seleccionado['hora']}\n", "valor")
        
        self.detalle_text.insert(tk.END, "Cantidad de fardos: ", "etiqueta")
        self.detalle_text.insert(tk.END, f"{self.ticket_seleccionado['cantidad_fardos']}\n", "valor")
        
        self.detalle_text.insert(tk.END, "Peso total: ", "etiqueta")
        self.detalle_text.insert(tk.END, f"{self.ticket_seleccionado['peso']:.2f} kg\n", "destacado")
        
        self.detalle_text.insert(tk.END, "Kg bruto romaneo: ", "etiqueta")
        self.detalle_text.insert(tk.END, f"{self.ticket_seleccionado['kg_bruto_romaneo']:.2f} kg\n", "valor")
        
        self.detalle_text.insert(tk.END, "Agregado: ", "etiqueta")
        self.detalle_text.insert(tk.END, f"{self.ticket_seleccionado['agregado']:.2f} kg\n", "valor")
        
        self.detalle_text.insert(tk.END, "Resto: ", "etiqueta")
        self.detalle_text.insert(tk.END, f"{self.ticket_seleccionado['resto']:.2f} kg\n", "valor")
        
        self.detalle_text.insert(tk.END, "Rinde: ", "etiqueta")
        self.detalle_text.insert(tk.END, f"{rinde:.2f}%\n", "destacado")
        
        self.detalle_text.insert(tk.END, "Observaciones: ", "etiqueta")
        self.detalle_text.insert(tk.END, f"{self.ticket_seleccionado['observaciones']}\n", "valor")
        
        self.detalle_text.insert(tk.END, "\n", "separador")
        self.detalle_text.insert(tk.END, "DETALLE DE FARDOS\n", "subtitulo")
        self.detalle_text.insert(tk.END, "\n", "separador")
        
        # Agregar detalle de fardos en formato de tabla
        if 'fardos' in self.ticket_seleccionado and self.ticket_seleccionado['fardos']:
            # Mostrar fardos en formato de tabla (3 columnas)
            fardos = self.ticket_seleccionado['fardos']
            columnas = 3  # Mostrar 3 fardos por fila
            
            # Encabezado de columnas
            self.detalle_text.insert(tk.END, f"{'Nº':^8} {'Peso (kg)':^10} {'Hora':^10}    " * columnas + "\n", "etiqueta")
            
            # Datos de fardos
            for i in range(0, len(fardos), columnas):
                linea = ""
                for j in range(columnas):
                    if i + j < len(fardos):
                        fardo = fardos[i + j]
                        hora = datetime.fromisoformat(fardo['hora_pesaje']).strftime("%H:%M") if fardo['hora_pesaje'] else "--:--"
                        linea += f"{fardo['numero']:^8} {fardo['peso']:^10.2f} {hora:^10}    "
                self.detalle_text.insert(tk.END, linea + "\n", "valor")
        else:
            self.detalle_text.insert(tk.END, "No hay información detallada de fardos disponible.", "valor")
        
        # Deshabilitar el widget de texto
        self.detalle_text.config(state=tk.DISABLED)
    
    def exportar_pdf(self):
        if not self.ticket_seleccionado:
            messagebox.showwarning("Advertencia", "No hay ticket seleccionado")
            return
        
        # Solicitar ubicación para guardar el PDF
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf"), ("Todos los archivos", "*.*")],
            initialfile=f"Ticket_{self.ticket_seleccionado['numero']}.pdf"
        )
        
        if not file_path:
            return
        
        try:
            self.generar_pdf(file_path)
            messagebox.showinfo("Éxito", f"PDF guardado en {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar el PDF: {str(e)}")
    
    def generar_pdf(self, file_path):
        # Crear documento con mejor tamaño de página
        doc = SimpleDocTemplate(file_path, pagesize=A4,
                              leftMargin=1.5*cm, rightMargin=1.5*cm,
                              topMargin=1.5*cm, bottomMargin=1.5*cm)
        elements = []
        
        # Verificar que hay ticket seleccionado
        if not self.ticket_seleccionado:
            raise ValueError("No hay ticket seleccionado para exportar a PDF.")
        
        # Estilos mejorados
        styles = getSampleStyleSheet()
        
        # Estilos personalizados para un aspecto más moderno
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            alignment=1,  # Centrado
            spaceAfter=0.3*cm,
            textColor=colors.HexColor("#0078d7")
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=14,
            alignment=0,  # Izquierda
            spaceAfter=0.2*cm,
            textColor=colors.HexColor("#333333")
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=0.1*cm
        )
        
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            alignment=1,  # Centrado
            textColor=colors.HexColor("#666666")
        )
        
        # Título con formato mejorado
        elements.append(Paragraph(f"TICKET DE PESAJE #{self.ticket_seleccionado['numero']}", title_style))
        elements.append(Spacer(1, 0.5*cm))
        
        # Calcular rinde
        rinde = 0
        if self.ticket_seleccionado['kg_bruto_romaneo'] > 0:
            tara = self.ticket_seleccionado['cantidad_fardos'] * 2  # 2kg por fardo
            rinde = ((self.ticket_seleccionado['peso'] + self.ticket_seleccionado['resto'] - 
                     self.ticket_seleccionado['agregado'] - tara) / 
                     self.ticket_seleccionado['kg_bruto_romaneo']) * 100
            rinde = round(rinde, 2)
        
        # Información del ticket con mejor formato
        data = [
            ["Número:", str(self.ticket_seleccionado['numero'])],
            ["Fecha:", self.ticket_seleccionado['fecha']],
            ["Hora:", self.ticket_seleccionado['hora']],
            ["Cantidad de fardos:", str(self.ticket_seleccionado['cantidad_fardos'])],
            ["Peso total:", f"{self.ticket_seleccionado['peso']:.2f} kg"],
            ["Kg bruto romaneo:", f"{self.ticket_seleccionado['kg_bruto_romaneo']:.2f} kg"],
            ["Agregado:", f"{self.ticket_seleccionado['agregado']:.2f} kg"],
            ["Resto:", f"{self.ticket_seleccionado['resto']:.2f} kg"],
            ["Rinde:", f"{rinde:.2f}%"],
            ["Observaciones:", self.ticket_seleccionado['observaciones'] if self.ticket_seleccionado['observaciones'] else "-"]
        ]
        
        # Crear tabla con estilo moderno
        info_table = Table(data, colWidths=[4*cm, 12*cm])
        info_table.setStyle(TableStyle([
            # Fondo de encabezados
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#f0f0f0")),
            # Color de texto
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor("#333333")),
            # Alineación
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            # Fuentes
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            # Padding
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            # Destacar información importante
            ('BACKGROUND', (1, 4), (1, 4), colors.HexColor("#e6f2ff")),  # Peso total
            ('BACKGROUND', (1, 8), (1, 8), colors.HexColor("#e6f2ff")),  # Rinde
            ('FONTNAME', (1, 4), (1, 4), 'Helvetica-Bold'),
            ('FONTNAME', (1, 8), (1, 8), 'Helvetica-Bold'),
            # Bordes
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#999999")),
            # Redondear esquinas (simulado con colores)
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f0f0f0")),
        ]))
        
        elements.append(info_table)
        elements.append(Spacer(1, 0.8*cm))
        
        # Agregar tabla de fardos si están disponibles
        if 'fardos' in self.ticket_seleccionado and self.ticket_seleccionado['fardos']:
            elements.append(Paragraph("DETALLE DE FARDOS", subtitle_style))
            elements.append(Spacer(1, 0.3*cm))
            
            fardos = self.ticket_seleccionado['fardos']
            
            # Determinar cuántas columnas usar según la cantidad de fardos
            if len(fardos) <= 10:
                cols = 1  # Una columna para pocos fardos
            elif len(fardos) <= 30:
                cols = 2  # Dos columnas para cantidad media
            else:
                cols = 3  # Tres columnas para muchos fardos
                
            # Organizar los fardos en columnas
            fardos_por_columna = math.ceil(len(fardos) / cols)
            
            # Crear datos para la tabla de fardos en múltiples columnas
            fardos_data = []
            
            # Crear encabezados para cada columna
            headers = []
            for i in range(cols):
                headers.extend(["Nº", "Peso (kg)", "Hora"])
            fardos_data.append(headers)
            
            # Llenar la tabla con los datos de fardos
            for i in range(fardos_por_columna):
                row = []
                for col in range(cols):
                    idx = i + col * fardos_por_columna
                    if idx < len(fardos):
                        fardo = fardos[idx]
                        hora = datetime.fromisoformat(fardo['hora_pesaje']).strftime("%H:%M") if fardo['hora_pesaje'] else "-"
                        row.extend([
                            str(fardo['numero']),
                            f"{fardo['peso']:.2f}",
                            hora
                        ])
                    else:
                        row.extend(["", "", ""])
                fardos_data.append(row)
            
            # Calcular anchos de columna
            col_widths = [1.5*cm, 2.5*cm, 2*cm] * cols
            
            # Crear tabla de fardos con estilo moderno
            fardos_table = Table(fardos_data, colWidths=col_widths)
            
            # Estilos para la tabla de fardos
            table_style = [
                # Encabezados
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e6e6e6")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#333333")),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                # Bordes
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#999999")),
                # Padding
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]
            
            # Aplicar colores alternados a las filas para mejor legibilidad
            for i in range(1, len(fardos_data)):
                if i % 2 == 0:
                    table_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor("#f9f9f9")))
            
            fardos_table.setStyle(TableStyle(table_style))
            
            elements.append(fardos_table)
            elements.append(Spacer(1, 0.8*cm))
        
        # Tabla de firmas con mejor estilo
        firma_data = [
            ["Operador", "Cliente"],
            ["", ""],
            ["", ""],
            ["", ""],
            ["_________________________", "_________________________"],
            ["Firma y aclaración", "Firma y aclaración"]
        ]
        
        firma_table = Table(firma_data, colWidths=[8*cm, 8*cm])
        firma_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 5), (1, 5), 'Helvetica'),
            ('FONTSIZE', (0, 5), (1, 5), 8),
            ('TEXTCOLOR', (0, 5), (1, 5), colors.HexColor("#666666")),
            ('LINEBELOW', (0, 4), (1, 4), 1, colors.HexColor("#333333")),
            ('TOPPADDING', (0, 1), (1, 3), 10),  # Espacio para la firma
        ]))
        
        elements.append(firma_table)
        
        # Pie de página
        elements.append(Spacer(1, 1*cm))
        elements.append(Paragraph(f"Documento generado el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", footer_style))
        
        # Generar PDF
        doc.build(elements)
    
    def imprimir_ticket(self):
        if not self.ticket_seleccionado:
            messagebox.showwarning("Advertencia", "No hay ticket seleccionado")
            return
        
        try:
            # Generar PDF temporal
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            temp_file.close()
            
            self.generar_pdf(temp_file.name)
            
            # Abrir el PDF con el visor predeterminado (que permitirá imprimir)
            if os.name == 'nt':  # Windows
                os.startfile(temp_file.name)
            else:  # Unix/Linux/Mac
                subprocess.call(['xdg-open', temp_file.name])
            
            # Mostrar mensaje informativo
            messagebox.showinfo("Información", 
                               "Se ha abierto el documento en su visor de PDF.\n"
                               "Utilice la función de impresión del visor para imprimir el ticket.")
            
            # Programar eliminación del archivo temporal después de un tiempo
            self.root.after(60000, lambda: self.eliminar_archivo_temp(temp_file.name))
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al preparar la impresión: {str(e)}")
    
    def eliminar_archivo_temp(self, filepath):
        try:
            if os.path.exists(filepath):
                os.unlink(filepath)
        except:
            pass  # Ignorar errores al eliminar archivos temporales

if __name__ == "__main__":
    # Configurar tema moderno para Windows 11
    try:
        root = ThemedTk(theme="azure")  # Tema más moderno y compatible con Windows 11
    except:
        # Si el tema azure no está disponible, usar un tema alternativo
        root = ThemedTk(theme="arc")
    
    # Configurar icono de la aplicación (opcional)
    # root.iconbitmap("path/to/icon.ico")  # Descomentar y ajustar si se tiene un icono
    
    # Configurar DPI para mejor visualización en pantallas de alta resolución
    root.tk.call('tk', 'scaling', 1.3)
    
    # Iniciar la aplicación
    app = VisorTickets(root)
    root.mainloop()