"""
Script principal para iniciar el juego, inicializa los componentes MVC.
Permite visualizar la interfaz gráfica.
"""
import pygame
# Eliminar importaciones innecesarias si el controlador real las maneja
# from view.interfaz_ajedrez import InterfazAjedrez 
# from model.tablero import Tablero
from typing import List, Tuple, Optional, Literal
import sys
import os
import logging

# Añadir el directorio raíz al sys.path para asegurar que los módulos se encuentren
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# Importar el controlador real
from controller.controlador_juego import ControladorJuego

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# --- Eliminar ControladorMock --- 
# class ControladorMock:
#     ...
# (Todo el código del mock eliminado)

# --- Función Principal (Modificada) ---
def main():
    """
    Inicializa pygame, crea el controlador real y ejecuta el bucle principal.
    """
    try:
        # Crear el controlador real. Este a su vez creará el modelo y la vista.
        controlador = ControladorJuego()
        
        # Iniciar el bucle principal a través del controlador
        controlador.iniciar()

        
    except ImportError as e:
        print(f"Error de importación en main.py: {e}")
        print("Asegúrate de que las carpetas 'model', 'view' y 'controller' están accesibles desde el directorio raíz.")
        # Intentar inicializar pygame para mostrar error gráfico si es posible
        try:
            pygame.init()
            screen = pygame.display.set_mode((600, 100))
            pygame.display.set_caption("Error de Importación")
            font = pygame.font.SysFont(None, 24)
            text_surface = font.render(f"Error al cargar módulos: {e}. Revisa la consola.", True, (255, 0, 0))
            screen.fill((200, 200, 200))
            screen.blit(text_surface, (10, 40))
            pygame.display.flip()
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                pygame.time.wait(50)
        except Exception as pygame_err:
             print(f"No se pudo inicializar pygame para mostrar el error: {pygame_err}")
             
    except Exception as e:
        print(f"Ocurrió un error inesperado en main.py: {e}")
        # Asegurarse de cerrar pygame si se inicializó parcialmente
        pygame.quit()

# --- Punto de Entrada (Sin cambios) ---
if __name__ == "__main__":
    main() 