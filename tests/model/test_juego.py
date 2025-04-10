import pytest
from unittest.mock import Mock, patch
from model.juego import Juego
from model.tablero import Tablero
from model.piezas.peon import Peon
from model.piezas.rey import Rey
from model.piezas.torre import Torre

class TestJuego:
    """Tests para la clase Juego."""

    @pytest.fixture
    def tablero_mock(self):
        """Fixture que proporciona un mock de Tablero."""
        tablero = Mock(spec=Tablero)
        tablero.obtenerPosicionActual.return_value = "posicion_inicial"
        return tablero

    @pytest.fixture
    def juego(self, tablero_mock):
        """Fixture que proporciona una instancia de Juego con un tablero mockeado."""
        return Juego(tablero_mock)

    @pytest.fixture
    def tablero_real(self):
        """Fixture que proporciona un tablero real."""
        return Tablero()

    @pytest.fixture
    def juego_real(self, tablero_real):
        """Fixture que proporciona una instancia de Juego con un tablero real."""
        juego = Juego(tablero_real)
        tablero_real.juego = juego
        return juego

    def test_inicializacion(self, juego, tablero_mock):
        """Prueba la inicialización correcta del juego."""
        assert juego.tablero is tablero_mock
        assert juego.turno_blanco is True
        assert juego.estado_juego == 'en_curso'
        assert juego.contadorRegla50Movimientos == 0
        assert juego.contadorPly == 0
        assert juego.numero_movimiento == 1
        assert juego.historial_posiciones["posicion_inicial"] == 1
        assert juego.historial_movimientos == []
        assert juego.ultimo_movimiento is None

    def test_get_turno_color(self, juego):
        """Prueba que getTurnoColor devuelve el color correcto."""
        assert juego.getTurnoColor() == 'blanco'
        juego.turno_blanco = False
        assert juego.getTurnoColor() == 'negro'

    def test_cambiar_turno(self, juego):
        """Prueba que cambiarTurno alterna correctamente el turno."""
        assert juego.turno_blanco is True
        juego.cambiarTurno()
        assert juego.turno_blanco is False
        juego.cambiarTurno()
        assert juego.turno_blanco is True

    def test_actualizar_ultimo_movimiento(self, juego):
        """Prueba que actualizarUltimoMovimiento actualiza correctamente el último movimiento."""
        origen = (0, 0)
        destino = (0, 1)
        juego.actualizarUltimoMovimiento(origen, destino)
        assert juego.ultimo_movimiento == (origen, destino)

    def test_registrar_posicion(self, juego):
        """Prueba que registrarPosicion incrementa correctamente el contador de posiciones."""
        juego.registrarPosicion("posicion_test")
        assert juego.historial_posiciones["posicion_test"] == 1
        juego.registrarPosicion("posicion_test")
        assert juego.historial_posiciones["posicion_test"] == 2

    def test_es_triple_repeticion(self, juego):
        """Prueba que esTripleRepeticion detecta correctamente la triple repetición."""
        # Inicialmente no hay triple repetición
        assert juego.esTripleRepeticion("posicion_test") is False
        
        # Registrar dos veces más
        juego.registrarPosicion("posicion_test")
        juego.registrarPosicion("posicion_test")
        assert juego.esTripleRepeticion("posicion_test") is False
        
        # Registrar una tercera vez
        juego.registrarPosicion("posicion_test")
        assert juego.esTripleRepeticion("posicion_test") is True

    def test_actualizar_contadores_normal(self, juego):
        """Prueba actualizar contadores con un movimiento normal."""
        pieza_mock = Mock()
        pieza_mock.__class__.__name__ = "Alfil"
        
        # Movimiento normal (no captura, no peón)
        juego.actualizarContadores(pieza_mock, False)
        assert juego.contadorPly == 1
        assert juego.numero_movimiento == 1  # No cambia porque es turno de blancas
        assert juego.contadorRegla50Movimientos == 1

    def test_actualizar_contadores_captura(self, juego):
        """Prueba actualizar contadores con un movimiento de captura."""
        pieza_mock = Mock()
        pieza_mock.__class__.__name__ = "Alfil"
        
        # Movimiento con captura
        juego.actualizarContadores(pieza_mock, True)
        assert juego.contadorPly == 1
        assert juego.contadorRegla50Movimientos == 0  # Se resetea con captura

    def test_actualizar_contadores_peon(self, juego):
        """Prueba actualizar contadores con un movimiento de peón."""
        pieza_mock = Mock()
        pieza_mock.__class__.__name__ = "Peon"
        
        # Movimiento de peón
        juego.actualizarContadores(pieza_mock, False)
        assert juego.contadorPly == 1
        assert juego.contadorRegla50Movimientos == 0  # Se resetea con movimiento de peón

    def test_actualizar_contadores_cambio_turno(self, juego):
        """Prueba actualizar contadores cuando cambia el número de movimiento."""
        pieza_mock = Mock()
        pieza_mock.__class__.__name__ = "Alfil"
        
        # Turno de negras
        juego.turno_blanco = False
        juego.actualizarContadores(pieza_mock, False)
        assert juego.numero_movimiento == 2  # Incrementa después del movimiento de negras

    def test_procesar_movimiento_realizado(self, juego):
        """Prueba procesarMovimientoRealizado."""
        pieza_mock = Mock()
        pieza_mock.color = 'blanco'
        origen = (0, 0)
        destino = (0, 1)
        
        # Espiar los métodos que se llaman internamente
        with patch.object(juego, 'actualizarUltimoMovimiento') as mock_ult_mov, \
             patch.object(juego, 'actualizarContadores') as mock_cont, \
             patch.object(juego, 'cambiarTurno') as mock_turno, \
             patch.object(juego, 'registrarPosicionActual') as mock_reg_pos, \
             patch.object(juego, 'actualizarEstadoJuego') as mock_estado:
            
            juego.procesarMovimientoRealizado(pieza_mock, origen, destino, False)
            
            # Verificar que se llamaron todos los métodos necesarios
            mock_ult_mov.assert_called_once_with(origen, destino)
            mock_cont.assert_called_once_with(pieza_mock, False)
            mock_turno.assert_called_once()
            mock_reg_pos.assert_called_once()
            mock_estado.assert_called_once()
            
            # Verificar que se añadió al historial
            assert juego.historial_movimientos == [('blanco', origen, destino)]

    def test_procesar_enroque_realizado(self, juego):
        """Prueba procesarEnroqueRealizado."""
        color = 'blanco'
        tipo = 'corto'
        rey_pos_origen = (0, 4)
        rey_pos_destino = (0, 6)
        
        # Crear un mock para el rey
        rey_mock = Mock()
        juego.tablero.getPieza.return_value = rey_mock
        
        # Espiar los métodos que se llaman internamente
        with patch.object(juego, 'actualizarUltimoMovimiento') as mock_ult_mov, \
             patch.object(juego, 'actualizarContadores') as mock_cont, \
             patch.object(juego, 'cambiarTurno') as mock_turno, \
             patch.object(juego, 'registrarPosicionActual') as mock_reg_pos, \
             patch.object(juego, 'actualizarEstadoJuego') as mock_estado:
            
            juego.procesarEnroqueRealizado(color, tipo, rey_pos_origen, rey_pos_destino)
            
            # Verificar que se llamaron todos los métodos necesarios
            mock_ult_mov.assert_called_once_with(rey_pos_origen, rey_pos_destino)
            mock_cont.assert_called_once()  # Con el rey retornado por tablero.getPieza
            mock_turno.assert_called_once()
            mock_reg_pos.assert_called_once()
            mock_estado.assert_called_once()
            
            # Verificar que se añadió al historial
            assert juego.historial_movimientos == [(color, rey_pos_origen, rey_pos_destino)]

    # Tests con un tablero real

    def test_es_material_insuficiente_delegacion(self, juego_real):
        """Prueba que esMaterialInsuficiente delega al tablero."""
        with patch.object(juego_real.tablero, 'esMaterialInsuficiente', return_value=True):
            assert juego_real.esMaterialInsuficiente() is True

    def test_obtener_todos_movimientos_legales_delegacion(self, juego_real):
        """Prueba que obtener_todos_movimientos_legales delega al tablero."""
        movimientos_esperados = [((0, 0), (0, 1))]
        with patch.object(juego_real.tablero, 'obtener_todos_movimientos_legales', return_value=movimientos_esperados):
            assert juego_real.obtener_todos_movimientos_legales('blanco') == movimientos_esperados
            juego_real.tablero.obtener_todos_movimientos_legales.assert_called_once_with('blanco')

    def test_obtener_estado_juego(self, juego):
        """Prueba que obtenerEstadoJuego devuelve el estado actual."""
        juego.estado_juego = 'jaque'
        assert juego.obtenerEstadoJuego() == 'jaque'

    def test_actualizar_estado_juego(self, juego_real):
        """Prueba diferentes estados del juego."""
        # Configurar un escenario simple para probar la actualización de estado
        tablero = juego_real.tablero
        
        # 1. Estado normal (en_curso)
        with patch.object(tablero, 'encontrarRey', return_value=(0, 4)), \
             patch.object(tablero, 'esCasillaAmenazada', return_value=False), \
             patch.object(tablero, 'obtener_todos_movimientos_legales', return_value=[((0,0), (0,1))]):
            juego_real.actualizarEstadoJuego()
            assert juego_real.estado_juego == 'en_curso'

        # 2. Estado de jaque
        with patch.object(tablero, 'encontrarRey', return_value=(0, 4)), \
             patch.object(tablero, 'esCasillaAmenazada', return_value=True), \
             patch.object(tablero, 'obtener_todos_movimientos_legales', return_value=[((0,0), (0,1))]):
            juego_real.actualizarEstadoJuego()
            assert juego_real.estado_juego == 'jaque'

        # 3. Estado de jaque mate
        with patch.object(tablero, 'encontrarRey', return_value=(0, 4)), \
             patch.object(tablero, 'esCasillaAmenazada', return_value=True), \
             patch.object(tablero, 'obtener_todos_movimientos_legales', return_value=[]):
            juego_real.actualizarEstadoJuego()
            assert juego_real.estado_juego == 'jaque_mate'

        # 4. Estado de tablas por ahogado
        with patch.object(tablero, 'encontrarRey', return_value=(0, 4)), \
             patch.object(tablero, 'esCasillaAmenazada', return_value=False), \
             patch.object(tablero, 'obtener_todos_movimientos_legales', return_value=[]):
            juego_real.actualizarEstadoJuego()
            assert juego_real.estado_juego == 'tablas'

        # 5. Estado de tablas por triple repetición
        with patch.object(tablero, 'encontrarRey', return_value=(0, 4)), \
             patch.object(tablero, 'esCasillaAmenazada', return_value=False), \
             patch.object(tablero, 'obtener_todos_movimientos_legales', return_value=[((0,0), (0,1))]), \
             patch.object(juego_real, 'esTripleRepeticionActual', return_value=True):
            juego_real.actualizarEstadoJuego()
            assert juego_real.estado_juego == 'tablas'

        # 6. Estado de tablas por regla de 50 movimientos
        with patch.object(tablero, 'encontrarRey', return_value=(0, 4)), \
             patch.object(tablero, 'esCasillaAmenazada', return_value=False), \
             patch.object(tablero, 'obtener_todos_movimientos_legales', return_value=[((0,0), (0,1))]), \
             patch.object(juego_real, 'esTripleRepeticionActual', return_value=False):
            juego_real.contadorRegla50Movimientos = 50
            juego_real.actualizarEstadoJuego()
            assert juego_real.estado_juego == 'tablas'

        # 7. Estado de tablas por material insuficiente
        with patch.object(tablero, 'encontrarRey', return_value=(0, 4)), \
             patch.object(tablero, 'esCasillaAmenazada', return_value=False), \
             patch.object(tablero, 'obtener_todos_movimientos_legales', return_value=[((0,0), (0,1))]), \
             patch.object(juego_real, 'esTripleRepeticionActual', return_value=False), \
             patch.object(juego_real, 'esMaterialInsuficiente', return_value=True):
            juego_real.contadorRegla50Movimientos = 0
            juego_real.actualizarEstadoJuego()
            assert juego_real.estado_juego == 'tablas'

    def test_es_triple_repeticion_actual(self, juego):
        """Prueba que esTripleRepeticionActual consulta correctamente al tablero."""
        # Configurar el mock del tablero
        juego.tablero.obtenerPosicionActual.return_value = "posicion_repetida"
        
        # Espiar el método esTripleRepeticion
        with patch.object(juego, 'esTripleRepeticion', return_value=True) as mock_triple:
            assert juego.esTripleRepeticionActual() is True
            mock_triple.assert_called_once_with("posicion_repetida")

    def test_registrar_posicion_actual(self, juego):
        """Prueba que registrarPosicionActual consulta al tablero y registra la posición."""
        # Configurar el mock del tablero
        juego.tablero.obtenerPosicionActual.return_value = "posicion_actual"
        
        # Espiar el método registrarPosicion
        with patch.object(juego, 'registrarPosicion') as mock_registrar:
            juego.registrarPosicionActual()
            mock_registrar.assert_called_once_with("posicion_actual")
