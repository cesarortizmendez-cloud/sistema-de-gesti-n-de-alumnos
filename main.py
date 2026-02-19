# ============================================
# main.py
# Punto de entrada del sistema:
# - Inicializa la base de datos
# - Inicia la interfaz Tkinter (UI única)
# ============================================

import traceback                                                  # Para obtener detalles del error (si ocurre)                   
from tkinter import messagebox                                     # Para mostrar errores en ventana (UI)                          

from modulos.bd_sqlite import inicializar_bd                       # Crea tablas / migraciones en SQLite                           
from modulos.ui_principal import AppPrincipal                      # Ventana principal con menú lateral                            

import os
import sys


def main():                                                        # Función principal del programa                                
    try:                                                           # Intenta ejecutar arranque completo                             
        inicializar_bd()                                            # 1) Asegura que la base de datos exista y esté lista            
        app = AppPrincipal()                                        # 2) Crea la ventana principal (Tkinter)                         
        app.mainloop()                                              # 3) Loop principal de Tkinter (mantiene la app viva)            
    except Exception as e:                                          # Si algo falla en el arranque                                  
        # IMPORTANTE:
        # Si falla antes de crear la ventana, mostramos un messagebox igualmente.
        try:                                                        # Intento de mostrar error visual                                
            messagebox.showerror(                                   # Ventana emergente                                             
                "Error al iniciar",                                 # Título                                                         
                f"Ocurrió un error al iniciar la aplicación:\n\n{e}\n\nDetalle:\n{traceback.format_exc()}"  # Mensaje detallado       
            )
        except Exception:                                           # Si incluso messagebox falla (caso extremo)                     
            print("Error crítico al iniciar la aplicación:")        # Muestra en consola                                             
            print(e)                                                # Imprime error                                                  
            print(traceback.format_exc())                           # Imprime trazas                                                 

def resource_path(ruta_relativa: str) -> str:
    # Si está ejecutándose como .exe (PyInstaller), toma la carpeta temporal _MEIPASS
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, ruta_relativa)
    # Si está en modo normal (python main.py), usa ruta del proyecto
    return os.path.join(os.path.abspath("."), ruta_relativa)

if __name__ == "__main__":                                          # Ejecuta solo si el archivo es llamado directo                  
    main()                                                         # Llama a la función principal                                   


