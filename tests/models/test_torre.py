# -*- coding: utf-8 -*-

"""
Tests para la clase Torre.
"""
import pytest
from models.tablero import Tablero
from models.piezas.torre import Torre

def test_inicializacion_torre():
    """
    Verifica la inicialización correcta de una torre.
    """
    tablero = Tablero() # Puede ser útil para tests futuros
    torre_blanca = Torre('blanco', (0, 0), tablero)
    torre_negra = Torre('negro', (7, 7), tablero)

    assert torre_blanca.color == 'blanco'
    assert torre_blanca.posicion == (0, 0)
    assert torre_blanca.se_ha_movido is False # Estado inicial de 'se_ha_movido' para enroque

    assert torre_negra.color == 'negro'
    assert torre_negra.posicion == (7, 7)
    assert torre_negra.se_ha_movido is False

# Aquí se añadirán más tests para cubrir movimientos horizontales/verticales, capturas y enroque. 