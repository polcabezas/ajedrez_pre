# -*- coding: utf-8 -*-

"""
Tests para la clase Caballo.
"""
import pytest
from models.tablero import Tablero
from models.piezas.caballo import Caballo

def test_inicializacion_caballo():
    """
    Verifica la inicialización correcta de un caballo.
    """
    tablero = Tablero() # Aunque no se use directamente aquí, puede ser útil para tests futuros
    caballo_blanco = Caballo('blanco', (0, 1), tablero)
    caballo_negro = Caballo('negro', (7, 6), tablero)

    assert caballo_blanco.color == 'blanco'
    assert caballo_blanco.posicion == (0, 1)

    assert caballo_negro.color == 'negro'
    assert caballo_negro.posicion == (7, 6)

# Aquí se añadirán más tests para cubrir los movimientos en 'L'. 