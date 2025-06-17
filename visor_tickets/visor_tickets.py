import os
import sqlite3
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from ttkthemes import ThemedTk
import json
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import subprocess
import tempfile

class VisorTickets:
    def __init__(self, root):
        self.root = root
        self.root.title("Visor de Tickets")
        self.root.geometry("1000x700")
        
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
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Frame superior para configuración
        config_frame = ttk.LabelFrame(main_frame, text="Configuración")
        config_frame.pack(fill='x', padx=5, pady=5)
        
        # Ruta de la base de datos
        ttk.Label(config_frame, text="Base de datos:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.entry_db = ttk.Entry(config_frame, width=50)
        self.entry_db.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        self.entry_db.insert(0, self.db_path)
        
        ttk.Button(config_frame, text="Examinar", command=self.seleccionar_bd).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(config_frame, text="Guardar", command=self.guardar_ruta_bd).grid(row=0, column=3, padx=5, pady=5)
        ttk.Button(config_frame, text="Actualizar", command=self.cargar_tickets).grid(row=0, column=4, padx=5, pady=5)
        
        config_frame.columnconfigure(1, weight=1)
        
        # Frame para la lista de tickets
        list_frame = ttk.LabelFrame(main_frame, text="Lista de Tickets")
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Crear tabla de tickets
        columns = ('numero', 'fecha', 'hora', 'fardos', 'peso', 'rinde')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        # Configurar columnas
        self.tree.heading('numero', text='Número')
        self.tree.heading('fecha', text='Fecha')
        self.tree.heading('hora', text='Hora')
        self.tree.heading('fardos', text='Fardos')
        self.tree.heading('peso', text='Peso Total')
        self.tree.heading('rinde', text='Rinde')
        
        self.tree.column('numero', width=100)
        self.tree.column('fecha', width=100)
        self.tree.column('hora', width=100)
        self.tree.column('fardos', width=100)
        self.tree.column('peso', width=100)
        self.tree.column('rinde', width=100)
        
        # Scrollbars
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
        
        # Frame para detalles del ticket
        self.detail_frame = ttk.LabelFrame(main_frame, text="Detalles del Ticket")
        self.detail_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Crear campos de detalles
        self.detalle_text = tk.Text(self.detail_frame, height=10, wrap=tk.WORD)
        self.detalle_text.pack(fill='both', expand=True, padx=5, pady=5)
        self.detalle_text.config(state=tk.DISABLED)
        
        # Frame para botones de acción
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(action_frame, text="Exportar a PDF", command=self.exportar_pdf).pack(side='left', padx=5)
        ttk.Button(action_frame, text="Imprimir", command=self.imprimir_ticket).pack(side='left', padx=5)
    
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
        
        # Formatear detalles
        detalles = f"""
TICKET DE PESAJE #{self.ticket_seleccionado['numero']}
==============================================
Fecha: {self.ticket_seleccionado['fecha']}
Hora: {self.ticket_seleccionado['hora']}
Cantidad de fardos: {self.ticket_seleccionado['cantidad_fardos']}
Peso total: {self.ticket_seleccionado['peso']:.2f} kg
Kg bruto romaneo: {self.ticket_seleccionado['kg_bruto_romaneo']:.2f} kg
Agregado: {self.ticket_seleccionado['agregado']:.2f} kg
Resto: {self.ticket_seleccionado['resto']:.2f} kg
Rinde: {rinde:.2f}%
Observaciones: {self.ticket_seleccionado['observaciones']}

DETALLE DE FARDOS:
==============================================
"""
        
        # Agregar detalle de fardos si están disponibles
        if 'fardos' in self.ticket_seleccionado and self.ticket_seleccionado['fardos']:
            for fardo in self.ticket_seleccionado['fardos']:
                hora = datetime.fromisoformat(fardo['hora_pesaje']).strftime("%H:%M:%S") if fardo['hora_pesaje'] else ""
                detalles += f"Fardo #{fardo['numero']}: {fardo['peso']:.2f} kg ({hora})\n"
        else:
            detalles += "No hay información detallada de fardos disponible."
        
        self.detalle_text.insert(tk.END, detalles)
        
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
        # Crear documento
        doc = SimpleDocTemplate(file_path, pagesize=letter)
        elements = []
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = styles['Heading1']
        subtitle_style = styles['Heading2']
        normal_style = styles['Normal']
        
        # Estilo personalizado para el encabezado
        header_style = ParagraphStyle(
            'Header',
            parent=styles['Heading1'],
            alignment=1,  # Centrado
            spaceAfter=12
        )
        
        # Título
        elements.append(Paragraph(f"TICKET DE PESAJE #{self.ticket_seleccionado['numero']}", header_style))
        elements.append(Spacer(1, 0.25*inch))
        
        # Calcular rinde
        rinde = 0
        if self.ticket_seleccionado['kg_bruto_romaneo'] > 0:
            tara = self.ticket_seleccionado['cantidad_fardos'] * 2  # 2kg por fardo
            rinde = ((self.ticket_seleccionado['peso'] + self.ticket_seleccionado['resto'] - 
                     self.ticket_seleccionado['agregado'] - tara) / 
                     self.ticket_seleccionado['kg_bruto_romaneo']) * 100
            rinde = round(rinde, 2)
        
        # Información del ticket
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
            ["Observaciones:", self.ticket_seleccionado['observaciones']]
        ]
        
        # Crear tabla
        table = Table(data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('BACKGROUND', (1, 4), (1, 4), colors.lightblue),  # Destacar el peso
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.5*inch))
        
        # Agregar tabla de fardos si están disponibles
        if 'fardos' in self.ticket_seleccionado and self.ticket_seleccionado['fardos']:
            elements.append(Spacer(1, 0.25*inch))
            elements.append(Paragraph("DETALLE DE FARDOS", subtitle_style))
            elements.append(Spacer(1, 0.15*inch))
            
            # Cabecera de la tabla de fardos
            fardos_data = [["Nº Fardo", "Peso (kg)", "Hora"]]
            
            # Datos de fardos
            for fardo in self.ticket_seleccionado['fardos']:
                hora = datetime.fromisoformat(fardo['hora_pesaje']).strftime("%H:%M:%S") if fardo['hora_pesaje'] else ""
                fardos_data.append([
                    str(fardo['numero']),
                    f"{fardo['peso']:.2f}",
                    hora
                ])
            
            # Crear tabla de fardos
            fardos_table = Table(fardos_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch])
            fardos_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(fardos_table)
            elements.append(Spacer(1, 0.5*inch))
        
        # Tabla de firmas
        firma_data = [
            ["Operador", "Cliente"],
            ["", ""],
            ["_________________", "_________________"],
            ["", ""]
        ]
        
        firma_table = Table(firma_data, colWidths=[3*inch, 3*inch])
        firma_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('LINEBELOW', (0, 2), (1, 2), 1, colors.black),
            ('TOPPADDING', (0, 1), (1, 1), 40),  # Espacio para la firma
        ]))
        
        elements.append(firma_table)
        
        # Pie de página
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph(f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", normal_style))
        
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
    root = ThemedTk(theme="arc")  # Usar un tema moderno
    app = VisorTickets(root)
    root.mainloop()