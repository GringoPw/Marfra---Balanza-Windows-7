"""
Script para probar la conexión con la balanza directamente.
Ejecutar este script antes de iniciar la aplicación principal para verificar
que la balanza está correctamente configurada y conectada.
"""

import tkinter as tk
from tkinter import messagebox, ttk
import sys
import traceback

def probar_conexion():
    try:
        from balanza_reader import BalanzaReader
        
        # Crear lector de balanza
        reader = BalanzaReader()
        
        # Obtener balanzas disponibles
        balanzas = reader.get_balanzas_disponibles()
        
        if not balanzas:
            resultado_text.insert(tk.END, "ERROR: No hay balanzas configuradas en configuracion.json\n")
            return
        
        resultado_text.insert(tk.END, "Balanzas configuradas:\n")
        for key, nombre in balanzas.items():
            resultado_text.insert(tk.END, f"  - {key}: {nombre}\n")
        
        # Intentar conectar con la primera balanza disponible
        balanza_key = list(balanzas.keys())[0]
        resultado_text.insert(tk.END, f"\nIntentando conectar a {balanzas[balanza_key]}...\n")
        
        if reader.conectar(balanza_key):
            resultado_text.insert(tk.END, f"ÉXITO: Conexión establecida con {balanzas[balanza_key]}\n")
            
            # Intentar leer el peso
            resultado_text.insert(tk.END, "Intentando leer peso...\n")
            
            # Leer varias veces para asegurar que tengamos un valor
            import time
            for i in range(5):
                peso = reader.leer_peso()
                if peso is not None:
                    resultado_text.insert(tk.END, f"ÉXITO: Peso leído: {peso} kg\n")
                    break
                resultado_text.insert(tk.END, f"Intento {i+1}: Esperando datos...\n")
                time.sleep(1)
            else:
                resultado_text.insert(tk.END, "ADVERTENCIA: No se recibieron datos de peso después de varios intentos.\n")
                resultado_text.insert(tk.END, "Verifique que la balanza esté enviando datos.\n")
            
            reader.desconectar()
            resultado_text.insert(tk.END, "Conexión cerrada.\n")
        else:
            resultado_text.insert(tk.END, f"ERROR: No se pudo conectar a {balanzas[balanza_key]}\n")
            resultado_text.insert(tk.END, "Verifique que la balanza esté encendida y conectada al puerto correcto.\n")
    
    except Exception as e:
        resultado_text.insert(tk.END, f"ERROR: {str(e)}\n")
        resultado_text.insert(tk.END, "Detalles del error:\n")
        resultado_text.insert(tk.END, traceback.format_exc())

# Crear ventana
root = tk.Tk()
root.title("Prueba de Conexión con Balanza")
root.geometry("600x400")
root.configure(padx=20, pady=20)

# Frame principal
main_frame = ttk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True)

# Título
ttk.Label(main_frame, text="Prueba de Conexión con Balanza", font=("Arial", 14, "bold")).pack(pady=(0, 10))

# Botón para probar conexión
ttk.Button(main_frame, text="Probar Conexión", command=probar_conexion).pack(pady=(0, 10))

# Área de resultados
resultado_frame = ttk.LabelFrame(main_frame, text="Resultados")
resultado_frame.pack(fill=tk.BOTH, expand=True)

resultado_text = tk.Text(resultado_frame, wrap=tk.WORD, height=15)
resultado_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

scrollbar = ttk.Scrollbar(resultado_text, command=resultado_text.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
resultado_text.config(yscrollcommand=scrollbar.set)

# Instrucciones
instrucciones = """
Instrucciones:
1. Asegúrese de que la balanza esté conectada y encendida.
2. Verifique que el puerto COM configurado en 'configuracion.json' sea correcto.
3. Haga clic en 'Probar Conexión' para verificar la comunicación.
4. Si la prueba es exitosa, puede iniciar la aplicación principal.
"""
resultado_text.insert(tk.END, instrucciones)

# Iniciar la aplicación
root.mainloop()