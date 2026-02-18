# ============================================
# main.py
# Punto de entrada de la aplicación
# ============================================

from modulos.bd_sqlite import inicializar_bd  # Crea la BD y tablas si no existen
from modulos.ui_principal import AppPrincipal  # Ventana principal


def main():
    inicializar_bd()          # Asegura que la BD exista antes de abrir la UI
    app = AppPrincipal()      # Crea la ventana principal
    app.mainloop()            # Inicia el loop de Tkinter


if __name__ == "__main__":
    main()
