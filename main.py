"""
Script principal para iniciar el juego, inicializa los componentes MVC.
Permite visualizar la interfaz gráfica.
"""
import pygame
from view.interfaz_ajedrez import InterfazAjedrez
from model.tablero import Tablero
from typing import List, Tuple, Optional, Literal

# --- Controlador Mock (Temporal) ---
class ControladorMock:
    """
    Controlador simulado para permitir la visualización de la interfaz.
    Proporciona los métodos mínimos requeridos por InterfazAjedrez.
    """
    def __init__(self):
        """Inicializa el controlador mock con un tablero."""
        self.tablero = Tablero()

    def obtener_tablero(self):
        """Devuelve la instancia del tablero."""
        return self.tablero

    def obtener_movimientos_validos(self, casilla: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Devuelve una lista vacía de movimientos válidos (simulación).
        En una implementación real, calcularía los movimientos legales.
        """
        print(f"(Mock) Calculando movimientos válidos para: {casilla}")
        # Simulación simple: permitir mover a casillas adyacentes (no realista)
        movimientos = []
        fila, col = casilla
        for df in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if df == 0 and dc == 0:
                    continue
                nueva_fila, nueva_col = fila + df, col + dc
                if 0 <= nueva_fila <= 7 and 0 <= nueva_col <= 7:
                    movimientos.append((nueva_fila, nueva_col))
        return movimientos

    def mover_pieza(self, origen: Tuple[int, int], destino: Tuple[int, int]):
        """
        Simula el movimiento de una pieza (solo imprime la acción).
        En una implementación real, validaría y ejecutaría el movimiento en el tablero.
        """
        print(f"(Mock) Moviendo pieza de {origen} a {destino}")
        # Lógica de movimiento muy básica para la simulación visual
        pieza = self.tablero.getPieza(origen)
        if pieza:
            # Verificar si el destino es válido (no es necesario para este mock)
            # Simplemente mover la pieza en el tablero mock
            self.tablero.setPieza(destino, pieza)
            self.tablero.setPieza(origen, None)
            pieza.posicion = destino # Actualizar posición interna de la pieza
            print(f"(Mock) Pieza {pieza.getTipo()} movida.")
        else:
            print("(Mock) No hay pieza en el origen.")


# --- Función Principal ---
def main():
    """
    Inicializa pygame, crea los componentes (mock) y ejecuta el bucle principal.
    """
    # Crear componentes
    controlador = ControladorMock()
    tablero = controlador.obtener_tablero() # El mock controller ya tiene un tablero
    interfaz = InterfazAjedrez(controlador)
    
    # Bucle principal del juego
    corriendo = True
    while corriendo:
        # Manejar eventos
        corriendo = interfaz.manejar_eventos()
        
        # Actualizar la pantalla
        # Pasamos el tablero para que se dibuje correctamente en la vista del tablero
        interfaz.actualizar(tablero)
        
        # Pequeña pausa para no consumir 100% CPU
        pygame.time.Clock().tick(30)

    # Salir de pygame
    pygame.quit()

# --- Punto de Entrada ---
if __name__ == "__main__":
    main() 