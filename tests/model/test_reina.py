# -*- coding: utf-8 -*-

"""
Tests para la clase Reina.
"""
import pytest
from model.tablero import Tablero
from model.piezas.reina import Reina

def test_inicializacion_reina():
    """
    Verifica la inicialización correcta de una reina.
    """
    tablero = Tablero() # Puede ser útil para tests futuros
    reina_blanca = Reina('blanco', (0, 3), tablero)
    reina_negra = Reina('negro', (7, 3), tablero)

    assert reina_blanca.color == 'blanco'
    assert reina_blanca.posicion == (0, 3)

    assert reina_negra.color == 'negro'
    assert reina_negra.posicion == (7, 3)

# Aquí se añadirán más tests para cubrir movimientos horizontales, verticales, diagonales y capturas. 