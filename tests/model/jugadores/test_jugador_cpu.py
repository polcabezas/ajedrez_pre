import pytest
from unittest.mock import patch, MagicMock, PropertyMock
import chess
import chess.engine
import logging # Import logging

# Importar las clases necesarias desde tu estructura
# Ajusta las rutas según sea necesario
from model.jugadores.jugador_cpu import JugadorCPU
from model.juego import Juego # Necesario para la firma de solicitarMovimiento
from model.tablero import Tablero # Necesario para simular el tablero

# Desactivar logging durante las pruebas para evitar ruido, excepto errores críticos
logging.disable(logging.CRITICAL)

# --- Fixtures ---

@pytest.fixture
def mock_tablero_inicial():
    """Crea un mock de Tablero con el estado inicial."""
    tablero = MagicMock(spec=Tablero)
    # Simular la estructura de casillas (simplificada)
    tablero.casillas = [[None] * 8 for _ in range(8)] # Inicialmente vacío para facilitar el mock
    # Simular el estado inicial que usa _convertir_a_chess_board
    tablero.getTurnoColor.return_value = 'blanco'
    tablero.derechosEnroque = {
        'blanco': {'corto': True, 'largo': True},
        'negro': {'corto': True, 'largo': True}
    }
    tablero.objetivoPeonAlPaso = None
    tablero.contadorRegla50Movimientos = 0
    tablero.numero_movimiento = 1

    # Simular getPieza para que devuelva mocks de piezas si es necesario
    # (Para _convertir_a_chess_board, necesitamos iterar sobre casillas,
    # así que llenaremos algunos mocks básicos)
    mock_peon_blanco = MagicMock()
    mock_peon_blanco.obtener_simbolo.return_value = 'P'
    mock_peon_blanco.get_color.return_value = 'blanco'
    tablero.casillas[1][4] = mock_peon_blanco # Simular peón en e2

    mock_rey_blanco = MagicMock()
    mock_rey_blanco.obtener_simbolo.return_value = 'K'
    mock_rey_blanco.get_color.return_value = 'blanco'
    tablero.casillas[0][4] = mock_rey_blanco # Simular rey en e1

    # Añadir una pieza negra para probar la conversión de color
    mock_peon_negro = MagicMock()
    mock_peon_negro.obtener_simbolo.return_value = 'P'
    mock_peon_negro.get_color.return_value = 'negro'
    tablero.casillas[6][4] = mock_peon_negro # Simular peón en e7

    return tablero

@pytest.fixture
def mock_juego(mock_tablero_inicial):
    """Crea un mock de Juego que contiene el mock_tablero_inicial."""
    juego = MagicMock(spec=Juego)
    # Usamos PropertyMock para simular el atributo tablero
    type(juego).tablero = PropertyMock(return_value=mock_tablero_inicial)
    return juego

@pytest.fixture
def jugador_cpu_blanco():
    """Crea una instancia de JugadorCPU para blanco, mockeando la inicialización del motor."""
    # Mockear popen_uci para evitar que intente iniciar Stockfish
    with patch('chess.engine.SimpleEngine.popen_uci') as mock_popen:
        mock_engine = MagicMock(spec=chess.engine.SimpleEngine)
        mock_popen.return_value = mock_engine # Devolver un motor mockeado
        jugador = JugadorCPU(nombre="CPU_Test_Blanco", color='blanco', nivel=1)
        jugador.engine = mock_engine # Asegurar que la instancia tiene el motor mockeado
        yield jugador # Usar yield para permitir limpieza si __del__ fuera complejo
        # Limpieza (opcional si __del__ es simple o mockeado)
        if jugador.engine:
             # Mockear quit para evitar errores si se llama
             jugador.engine.quit = MagicMock()
        jugador.__del__() # Llamar explícitamente si es necesario verificar llamadas a quit

# --- Tests de Conversión ---

def test_convertir_coordenada_a_indice():
    jugador = JugadorCPU("Test", "blanco") # Instancia temporal para método
    assert jugador._convertir_coordenada_a_indice((0, 0)) == chess.A1 # (0,0) -> a1 -> 0
    assert jugador._convertir_coordenada_a_indice((1, 4)) == chess.E2 # (1,4) -> e2 -> 12
    assert jugador._convertir_coordenada_a_indice((7, 7)) == chess.H8 # (7,7) -> h8 -> 63
    assert jugador._convertir_coordenada_a_indice((7, 0)) == chess.A8 # (7,0) -> a8 -> 56
    assert jugador._convertir_coordenada_a_indice((0, 7)) == chess.H1 # (0,7) -> h1 -> 7

def test_convertir_indice_a_coordenada():
    jugador = JugadorCPU("Test", "blanco")
    assert jugador._convertir_indice_a_coordenada(chess.A1) == (0, 0)
    assert jugador._convertir_indice_a_coordenada(chess.E2) == (1, 4)
    assert jugador._convertir_indice_a_coordenada(chess.H8) == (7, 7)
    assert jugador._convertir_indice_a_coordenada(chess.A8) == (7, 0)
    assert jugador._convertir_indice_a_coordenada(chess.H1) == (0, 7)

# Nota: testear _convertir_a_chess_board directamente es complejo por la dependencia del mock tablero.
# Se testea indirectamente a través de solicitarMovimiento.

# --- Tests de solicitarMovimiento ---

def test_solicitar_movimiento_simple(jugador_cpu_blanco, mock_juego):
    """Prueba un escenario simple donde el motor devuelve un movimiento."""
    # Configurar el mock del motor para devolver un movimiento específico
    movimiento_esperado_uci = "e2e4"
    movimiento_chess = chess.Move.from_uci(movimiento_esperado_uci)
    resultado_motor = chess.engine.PlayResult(movimiento_chess, None) # Sin ponderación
    jugador_cpu_blanco.engine.play.return_value = resultado_motor

    # Llamar al método
    movimiento_obtenido = jugador_cpu_blanco.solicitarMovimiento(mock_juego)

    # Verificar que se llamó al motor con el tablero correcto (convertido) y el límite de tiempo
    # (Necesitaríamos mockear _convertir_a_chess_board para verificar el board exacto,
    # o confiar en que la conversión funciona basada en los tests unitarios)
    jugador_cpu_blanco.engine.play.assert_called_once()
    args, kwargs = jugador_cpu_blanco.engine.play.call_args
    board_argument = args[0] # El tablero pasado a play
    limit_argument = args[1] # El límite pasado a play

    # Verificar tipo de argumentos
    assert isinstance(board_argument, chess.Board)
    assert isinstance(limit_argument, chess.engine.Limit)
    assert limit_argument.time == 0.1 * jugador_cpu_blanco.get_nivel() # Nivel es 1

    # Verificar el movimiento devuelto en nuestro formato
    # e2 -> (1, 4), e4 -> (3, 4)
    origen_esperado = (1, 4)
    destino_esperado = (3, 4)
    assert movimiento_obtenido == (origen_esperado, destino_esperado)

def test_solicitar_movimiento_motor_no_devuelve_movimiento(jugador_cpu_blanco, mock_juego):
    """Prueba el caso donde el motor devuelve None (fin de partida)."""
    resultado_motor = chess.engine.PlayResult(None, None) # Movimiento es None
    jugador_cpu_blanco.engine.play.return_value = resultado_motor

    movimiento_obtenido = jugador_cpu_blanco.solicitarMovimiento(mock_juego)

    # Verificar que devuelve el formato de "no movimiento"
    assert movimiento_obtenido == ((-1, -1), (-1, -1))

def test_solicitar_movimiento_motor_no_inicializado(mock_juego):
    """Prueba el caso donde el motor no se pudo inicializar."""
    # Mockear popen_uci para que falle (lance FileNotFoundError)
    with patch('chess.engine.SimpleEngine.popen_uci', side_effect=FileNotFoundError):
        jugador_cpu_error = JugadorCPU(nombre="CPU_Error", color='blanco', nivel=1)

        # El motor debería ser None
        assert jugador_cpu_error.engine is None

        # Llamar al método
        movimiento_obtenido = jugador_cpu_error.solicitarMovimiento(mock_juego)

        # Verificar que devuelve el formato de "no movimiento"
        assert movimiento_obtenido == ((-1, -1), (-1, -1))

def test_solicitar_movimiento_error_del_motor(jugador_cpu_blanco, mock_juego):
    """Prueba el caso donde el método play del motor lanza una excepción."""
    # Configurar el mock del motor para lanzar EngineError
    jugador_cpu_blanco.engine.play.side_effect = chess.engine.EngineError("Error simulado del motor")

    # Llamar al método
    movimiento_obtenido = jugador_cpu_blanco.solicitarMovimiento(mock_juego)

    # Verificar que devuelve el formato de "no movimiento"
    assert movimiento_obtenido == ((-1, -1), (-1, -1))

def test_solicitar_movimiento_error_conversion_tablero(jugador_cpu_blanco, mock_juego):
    """Prueba el caso donde _convertir_a_chess_board falla."""
    # Mockear _convertir_a_chess_board para que lance una excepción
    with patch.object(jugador_cpu_blanco, '_convertir_a_chess_board', side_effect=ValueError("Error de conversión simulado")):
        movimiento_obtenido = jugador_cpu_blanco.solicitarMovimiento(mock_juego)
        assert movimiento_obtenido == ((-1, -1), (-1, -1))
        # Verificar que play no fue llamado
        jugador_cpu_blanco.engine.play.assert_not_called()

# --- Test de Limpieza ---

def test_del_cierra_motor():
    """Verifica que __del__ llama a engine.quit()."""
    mock_engine = MagicMock(spec=chess.engine.SimpleEngine)
    with patch('chess.engine.SimpleEngine.popen_uci', return_value=mock_engine):
        jugador = JugadorCPU(nombre="CPU_Del_Test", color='negro', nivel=1)
        # Guardar referencia al mock de quit antes de eliminar el jugador
        mock_quit = jugador.engine.quit

    # Eliminar la referencia para invocar __del__ (si el garbage collector actúa)
    # Es más fiable llamar __del__ directamente en un test si es posible
    jugador.__del__() # Llamada explícita

    # Verificar que quit fue llamado
    mock_quit.assert_called_once()

def test_del_sin_motor_no_falla():
    """Verifica que __del__ no falla si el motor es None."""
    with patch('chess.engine.SimpleEngine.popen_uci', side_effect=FileNotFoundError):
        jugador = JugadorCPU(nombre="CPU_Del_NoEngine", color='negro', nivel=1)
        # El motor es None
        assert jugador.engine is None
        # Llamar a __del__ no debería lanzar excepciones
        try:
            jugador.__del__()
        except Exception as e:
            pytest.fail(f"__del__ lanzó una excepción inesperada cuando engine era None: {e}") 