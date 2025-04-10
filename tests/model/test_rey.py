# -*- coding: utf-8 -*-

"""
Tests para la clase Rey.
"""
import pytest
from model.tablero import Tablero
from model.piezas.rey import Rey

def test_inicializacion_rey():
    """
    Verifica la inicialización correcta de un rey.
    """
    tablero = Tablero() # Puede ser útil para tests futuros
    rey_blanco = Rey('blanco', (0, 4), tablero)
    rey_negro = Rey('negro', (7, 4), tablero)

    assert rey_blanco.color == 'blanco'
    assert rey_blanco.posicion == (0, 4)
    assert rey_blanco.se_ha_movido is False # Estado inicial para enroque

    assert rey_negro.color == 'negro'
    assert rey_negro.posicion == (7, 4)
    assert rey_negro.se_ha_movido is False

# Aquí se añadirán más tests para cubrir movimientos de una casilla, capturas, jaque, jaque mate y enroque. 