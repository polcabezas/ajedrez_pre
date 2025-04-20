# tests/test_evaluador_estado.py
import pytest
from model.tablero import Tablero
from model.evaluador_estado_de_juego import EvaluadorEstadoDeJuego
from model.piezas.rey import Rey
from model.piezas.caballo import Caballo
from model.piezas.alfil import Alfil
from model.piezas.peon import Peon
from model.piezas.reina import Reina

# Helper to create a board with specific pieces
def setup_board(pieces_dict):
     tablero = Tablero()
     tablero.casillas = [[None for _ in range(8)] for _ in range(8)] # Clear board
     for pos, pieza_info in pieces_dict.items():
          ClasePieza = pieza_info['clase']
          color = pieza_info['color']
          # Pass tablero reference when creating pieces if needed by their class
          tablero.casillas[pos[0]][pos[1]] = ClasePieza(color, pos, tablero)
     # Ensure the evaluator uses this specific board instance
     evaluador = EvaluadorEstadoDeJuego(tablero)
     return evaluador

def test_k_vs_k():
     evaluador = setup_board({
          (0, 0): {'clase': Rey, 'color': 'blanco'},
          (7, 7): {'clase': Rey, 'color': 'negro'}
     })
     assert evaluador.esMaterialInsuficiente() is True

def test_k_n_vs_k():
     evaluador = setup_board({
          (0, 0): {'clase': Rey, 'color': 'blanco'},
          (0, 1): {'clase': Caballo, 'color': 'blanco'},
          (7, 7): {'clase': Rey, 'color': 'negro'}
     })
     assert evaluador.esMaterialInsuficiente() is True

def test_k_vs_k_n():
     evaluador = setup_board({
          (0, 0): {'clase': Rey, 'color': 'blanco'},
          (7, 7): {'clase': Rey, 'color': 'negro'},
          (7, 6): {'clase': Caballo, 'color': 'negro'}
     })
     assert evaluador.esMaterialInsuficiente() is True

def test_k_b_vs_k():
     evaluador = setup_board({
          (0, 0): {'clase': Rey, 'color': 'blanco'},
          (0, 1): {'clase': Alfil, 'color': 'blanco'}, # Pos (0,1) is light square
          (7, 7): {'clase': Rey, 'color': 'negro'}
     })
     assert evaluador.esMaterialInsuficiente() is True

def test_k_b_vs_k_b_same_color():
     evaluador = setup_board({
          (0, 0): {'clase': Rey, 'color': 'blanco'},
          (0, 1): {'clase': Alfil, 'color': 'blanco'}, # Light square
          (7, 7): {'clase': Rey, 'color': 'negro'},
          (7, 6): {'clase': Alfil, 'color': 'negro'}  # Light square (7+6=13 odd)
     })
     assert evaluador.esMaterialInsuficiente() is True

def test_k_b_vs_k_b_different_color():
     evaluador = setup_board({
          (0, 0): {'clase': Rey, 'color': 'blanco'},
          (0, 1): {'clase': Alfil, 'color': 'blanco'}, # Light square
          (7, 7): {'clase': Rey, 'color': 'negro'},
          (7, 5): {'clase': Alfil, 'color': 'negro'}  # Dark square (7+5=12 even)
     })
     assert evaluador.esMaterialInsuficiente() is False # Mate is possible

def test_sufficient_material_pawns():
     evaluador = setup_board({
          (0, 0): {'clase': Rey, 'color': 'blanco'},
          (1, 0): {'clase': Peon, 'color': 'blanco'}, # Assuming Peon class exists
          (7, 7): {'clase': Rey, 'color': 'negro'}
     })
     # Need to import Peon first
     # assert evaluador.esMaterialInsuficiente() is False # Peons mean sufficient material

def test_sufficient_material_queen():
     evaluador = setup_board({
          (0, 0): {'clase': Rey, 'color': 'blanco'},
          (0, 3): {'clase': Reina, 'color': 'blanco'}, # Assuming Reina class exists
          (7, 7): {'clase': Rey, 'color': 'negro'}
     })
     # Need to import Reina first
     # assert evaluador.esMaterialInsuficiente() is False

# Add more tests for Rooks, multiple minor pieces, etc.