"""
Tests de integración para el jugador CPU y la selección de modos de juego.
"""

import pytest
from unittest.mock import patch, MagicMock
import logging

# Importar las clases necesarias
from model.juego import Juego
from model.jugadores.jugador_cpu import JugadorCPU
from model.jugadores.jugador_humano import JugadorHumano

# Desactivar logging durante las pruebas
logging.disable(logging.CRITICAL)

# --- Fixtures ---

@pytest.fixture
def juego_mock():
    """Crea un mock de Juego para las pruebas de integración."""
    with patch('model.juego.Tablero'):  # Mock el tablero para evitar inicialización completa
        juego = Juego()
        # Asegurarse de que los ayudantes estén correctamente mockeados
        juego.validador = MagicMock()
        juego.ejecutor = MagicMock() 
        juego.evaluador = MagicMock()
        juego.historial = MagicMock()
        return juego

@pytest.fixture
def juego_con_stockfish_mock():
    """Crea un mock de Juego con Stockfish mockeado para CPU."""
    # Mockea el motor de Stockfish
    with patch('chess.engine.SimpleEngine.popen_uci') as mock_popen:
        mock_engine = MagicMock()
        mock_popen.return_value = mock_engine
        
        # Crear el juego con el tablero mockeado
        with patch('model.juego.Tablero'):
            juego = Juego()
            # Mockear ayudantes
            juego.validador = MagicMock()
            juego.ejecutor = MagicMock()
            juego.evaluador = MagicMock()
            juego.historial = MagicMock()
            return juego

# --- Tests ---

def test_configuracion_humano_vs_humano(juego_mock):
    """Test que verifica la correcta configuración de jugadores en modo Humano vs Humano."""
    # Configurar una partida "Humano vs Humano"
    config = {
        'tipo_juego': 'Clásico',
        'modalidad': 'Humano vs Humano'
    }
    
    juego_mock.configurar_nueva_partida(config)
    
    # Verificar que se crearon dos jugadores humanos
    assert len(juego_mock.jugadores) == 2
    assert isinstance(juego_mock.jugadores[0], JugadorHumano)
    assert isinstance(juego_mock.jugadores[1], JugadorHumano)
    assert juego_mock.jugadores[0].get_color() == 'blanco'
    assert juego_mock.jugadores[1].get_color() == 'negro'

def test_configuracion_humano_vs_cpu(juego_con_stockfish_mock):
    """Test que verifica la correcta configuración de jugadores en modo Humano vs CPU."""
    # Configurar una partida "Humano vs CPU" con nivel 3
    config = {
        'tipo_juego': 'Rápido',
        'modalidad': 'Humano vs CPU',
        'nivel_cpu': 3
    }
    
    juego_con_stockfish_mock.configurar_nueva_partida(config)
    
    # Verificar que se crearon un jugador humano y uno CPU
    assert len(juego_con_stockfish_mock.jugadores) == 2
    assert isinstance(juego_con_stockfish_mock.jugadores[0], JugadorHumano)
    assert isinstance(juego_con_stockfish_mock.jugadores[1], JugadorCPU)
    assert juego_con_stockfish_mock.jugadores[0].get_color() == 'blanco'
    assert juego_con_stockfish_mock.jugadores[1].get_color() == 'negro'
    assert juego_con_stockfish_mock.jugadores[1].get_nivel() == 3

def test_configuracion_cpu_vs_humano(juego_con_stockfish_mock):
    """Test que verifica la correcta configuración de jugadores en modo CPU vs Humano."""
    # Configurar una partida "CPU vs Humano" con nivel 5
    config = {
        'tipo_juego': 'Blitz',
        'modalidad': 'CPU vs Humano',
        'nivel_cpu': 5
    }
    
    juego_con_stockfish_mock.configurar_nueva_partida(config)
    
    # Verificar que se crearon un jugador CPU y uno humano
    assert len(juego_con_stockfish_mock.jugadores) == 2
    assert isinstance(juego_con_stockfish_mock.jugadores[0], JugadorCPU)
    assert isinstance(juego_con_stockfish_mock.jugadores[1], JugadorHumano)
    assert juego_con_stockfish_mock.jugadores[0].get_color() == 'blanco'
    assert juego_con_stockfish_mock.jugadores[1].get_color() == 'negro'
    assert juego_con_stockfish_mock.jugadores[0].get_nivel() == 5

def test_configuracion_cpu_vs_cpu(juego_con_stockfish_mock):
    """Test que verifica la correcta configuración de jugadores en modo CPU vs CPU."""
    # Configurar una partida "CPU vs CPU" con nivel 10
    config = {
        'tipo_juego': 'Clásico',
        'modalidad': 'CPU vs CPU',
        'nivel_cpu': 10
    }
    
    juego_con_stockfish_mock.configurar_nueva_partida(config)
    
    # Verificar que se crearon dos jugadores CPU
    assert len(juego_con_stockfish_mock.jugadores) == 2
    assert isinstance(juego_con_stockfish_mock.jugadores[0], JugadorCPU)
    assert isinstance(juego_con_stockfish_mock.jugadores[1], JugadorCPU)
    assert juego_con_stockfish_mock.jugadores[0].get_color() == 'blanco'
    assert juego_con_stockfish_mock.jugadores[1].get_color() == 'negro'
    assert juego_con_stockfish_mock.jugadores[0].get_nivel() == 10
    assert juego_con_stockfish_mock.jugadores[1].get_nivel() == 10

def test_nivel_cpu_por_defecto(juego_con_stockfish_mock):
    """Test que verifica que se asigna el nivel 1 por defecto a CPU si no se especifica."""
    # Configurar una partida "Humano vs CPU" sin especificar nivel
    config = {
        'tipo_juego': 'Rápido',
        'modalidad': 'Humano vs CPU'
    }
    
    juego_con_stockfish_mock.configurar_nueva_partida(config)
    
    # Verificar que el nivel por defecto es 1
    assert isinstance(juego_con_stockfish_mock.jugadores[1], JugadorCPU)
    assert juego_con_stockfish_mock.jugadores[1].get_nivel() == 1 