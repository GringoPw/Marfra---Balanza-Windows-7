import tkinter as tk
from funciones.sistema_pesaje import SistemaPesajeFardos

def main():
    root = tk.Tk()
    app = SistemaPesajeFardos(root)
    
    # Configurar cierre de ventana
    def on_closing():
        app.cerrar_aplicacion()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()