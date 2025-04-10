# -*- coding: utf-8 -*-

"""
Tests para la clase Alfil.
"""
import pytest
from model.tablero import Tablero
from model.piezas.alfil import Alfil

def test_inicializacion_alfil():
    """
    Verifica la inicialización correcta de un alfil.
    """
    tablero = Tablero() # Puede ser útil para tests futuros
    alfil_blanco = Alfil('blanco', (0, 2), tablero)
    alfil_negro = Alfil('negro', (7, 5), tablero)

    assert alfil_blanco.color == 'blanco'
    assert alfil_blanco.posicion == (0, 2)

    assert alfil_negro.color == 'negro'
    assert alfil_negro.posicion == (7, 5)

# Aquí se añadirán más tests para cubrir movimientos diagonales y capturas. 