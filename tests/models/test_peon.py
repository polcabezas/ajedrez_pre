# -*- coding: utf-8 -*-

"""
Tests para la clase Peon.
"""
import pytest
from models.tablero import Tablero
from models.piezas.peon import Peon

def test_inicializacion_peon():
    """
    Verifica la inicialización correcta de un peón.
    """
    tablero = Tablero()
    peon_blanco = Peon('blanco', (1, 0), tablero)
    peon_negro = Peon('negro', (6, 7), tablero)

    assert peon_blanco.color == 'blanco'
    assert peon_blanco.posicion == (1, 0)
    assert peon_blanco.se_ha_movido is False

    assert peon_negro.color == 'negro'
    assert peon_negro.posicion == (6, 7)
    assert peon_negro.se_ha_movido is False

# Aquí se añadirán más tests para cubrir movimientos, capturas, promoción, etc. 