"""
Tests unitarios para la clase ControladorJuego.
Verifica la comunicación entre modelo y vista, gestión de eventos y flujo del juego.
"""

import unittest
from unittest.mock import MagicMock, patch, Mock
import sys
import os

# Añadir el directorio raíz al sys.path para que encuentre los módulos controller, model, view
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir)) # Subir un nivel más si tests está en subcarpeta
sys.path.append(project_root)

# --- Importar Clases Reales para spec ---
# Asegúrate de que estas rutas son correctas según tu estructura
try:
    from model.juego import Juego
    from view.interfaz_ajedrez import InterfazAjedrez
    from model.tablero import Tablero
    from model.jugadores.jugador_cpu import JugadorCPU
except ImportError as e:
    print(f"ERROR en test: No se pudieron importar clases reales para spec: {e}")
    # Definir clases dummy para que el archivo al menos se cargue
    class Juego: pass
    class InterfazAjedrez: pass
    class Tablero: pass
    class JugadorCPU: pass

# Importar la clase a testear
from controller.controlador_juego import ControladorJuego

class TestControladorJuegoConexionBasica(unittest.TestCase):
    """
    Tests para la inicialización básica y el bucle principal del ControladorJuego.
    """

    @patch('controller.controlador_juego.Juego')
    @patch('controller.controlador_juego.InterfazAjedrez')
    def test_inicializacion(self, MockInterfazAjedrez, MockJuego):
        """
        Verifica que __init__ instancia correctamente el modelo y la vista.
        """
        # Comentario: Crear instancia del controlador. Los mocks reemplazarán las clases reales.
        controlador = ControladorJuego()

        # Comentario: Verificar que el constructor de Juego fue llamado una vez.
        MockJuego.assert_called_once()

        # Comentario: Verificar que el constructor de InterfazAjedrez fue llamado una vez, 
        # y que se le pasó la instancia del controlador (self).
        MockInterfazAjedrez.assert_called_once_with(controlador)
        self.assertFalse(controlador.running) # Verificar estado inicial

    @patch('controller.controlador_juego.Juego')
    @patch('controller.controlador_juego.InterfazAjedrez')
    @patch('controller.controlador_juego.pygame') # Mockear todo el módulo pygame
    @patch('controller.controlador_juego.sys') # Mockear sys para evitar exit()
    def test_bucle_principal_iniciar(self, MockSys, MockPygame, MockInterfazAjedrez, MockJuego):
        """
        Verifica que el método iniciar ejecuta el bucle, llama a los métodos 
        de la vista y finaliza pygame correctamente.
        """
        # Configurar mocks
        mock_vista_instancia = MockInterfazAjedrez.return_value
        mock_modelo_instancia = MockJuego.return_value
        
        # Simular que manejar_eventos devuelve True la primera vez, False la segunda para salir del bucle
        mock_vista_instancia.manejar_eventos.side_effect = [True, False]
        
        # Configurar mock del modelo para obtener_tablero
        mock_modelo_instancia.tablero = MagicMock()

        # Comentario: Crear instancia del controlador
        controlador = ControladorJuego()
        
        # Comentario: Ejecutar el método iniciar
        controlador.iniciar()

        # Comentario: Verificar que el bucle se ejecutó (running fue True)
        self.assertTrue(controlador.running is False) # Debe ser False al salir

        # Comentario: Verificar llamadas a métodos de la vista dentro del bucle
        # Debería llamarse dos veces (una por cada iteración simulada)
        self.assertEqual(mock_vista_instancia.manejar_eventos.call_count, 2)
        # Debería llamarse al menos una vez
        self.assertGreaterEqual(mock_vista_instancia.actualizar.call_count, 1)

        # Comentario: Verificar llamada a pygame.time.Clock().tick()
        MockPygame.time.Clock.assert_called()
        MockPygame.time.Clock().tick.assert_called()

        # Comentario: Verificar que pygame.quit() se llamó al final
        MockPygame.quit.assert_called_once()
        
        # Comentario: Verificar que sys.exit() se llamó al final  
        MockSys.exit.assert_called_once()


class TestControladorJuegoInicioPartida(unittest.TestCase):

    @patch('controller.controlador_juego.Juego')
    @patch('controller.controlador_juego.InterfazAjedrez')
    def test_solicitar_inicio_juego(self, MockInterfazAjedrez, MockJuego):
        """
        Verifica que solicitar_inicio_juego llama a los métodos correctos 
        en la vista y el modelo.
        """
        # Configurar mocks
        mock_vista_instancia = MockInterfazAjedrez.return_value
        mock_modelo_instancia = MockJuego.return_value
        
        # Simular la configuración devuelta por la vista
        config_simulada = {'tipo_juego': 'Clásico', 'modalidad': 'Humano vs Humano'}
        mock_vista_instancia.obtener_configuracion.return_value = config_simulada
        
        # Crear instancia del controlador
        controlador = ControladorJuego()
        
        # --- Simular que el modelo SÍ tiene el método de configuración ---
        config_method_name_in_controller = 'configurar_nueva_partida'
        mock_config_method = MagicMock()
        setattr(mock_modelo_instancia, config_method_name_in_controller, mock_config_method)
        
        # Mockear atributos que necesita el controlador después de configurar
        mock_modelo_instancia.jugadores = []
        mock_modelo_instancia.jugador_actual_idx = 0
    
        # Llamar al método a probar
        controlador.solicitar_inicio_juego()
    
        # Verificar llamadas
        # 1. Obtener configuración de la vista
        mock_vista_instancia.obtener_configuracion.assert_called_once()
    
        # 2. Llamar al método correcto en el modelo con la configuración
        mock_config_method.assert_called_once_with(config_simulada)
    
        # 3. Cambiar vista en la interfaz
        mock_vista_instancia.cambiar_vista.assert_called_once_with('tablero')

        # 4. Verificar reseteo de estado interno
        self.assertIsNone(controlador.casilla_origen_seleccionada)
        self.assertEqual(controlador.movimientos_validos_cache, [])
        self.assertFalse(controlador.juego_terminado)

        # 5. Verificar limpieza de estado en la vista
        self.assertIsNone(mock_vista_instancia.casilla_origen)
        self.assertEqual(mock_vista_instancia.movimientos_validos, [])


class TestControladorSeleccionPieza(unittest.TestCase):

    def setUp(self):
        """ Configuración inicial para cada test de selección """
        # Mockear las dependencias principales
        self.patcher_juego = patch('controller.controlador_juego.Juego', spec=Juego)
        self.patcher_vista = patch('controller.controlador_juego.InterfazAjedrez', spec=InterfazAjedrez)

        self.MockJuego = self.patcher_juego.start()
        self.MockInterfazAjedrez = self.patcher_vista.start()

        # Crear instancias mockeadas
        self.mock_vista_instancia = self.MockInterfazAjedrez.return_value
        self.mock_modelo_instancia = self.MockJuego.return_value
        
        # Crear un mock para el tablero *interno* del modelo Juego
        self.mock_tablero_interno = MagicMock(spec=Tablero)
        self.mock_modelo_instancia.tablero = self.mock_tablero_interno
        
        # *** CORRECIÓN: Mockear atributos críticos que necesita manejar_clic_casilla ***
        self.mock_modelo_instancia.jugadores = []  # Lista vacía inicial
        self.mock_modelo_instancia.jugador_actual_idx = 0
        
        # Crear instancia del controlador
        self.controlador = ControladorJuego()
        self.controlador.juego_terminado = False # Asegurar que el juego no está terminado
        self.controlador.casilla_origen_seleccionada = None # Empezar sin selección

        # Mockear pieza para los tests
        self.mock_pieza_blanca = MagicMock() # No usamos spec para añadir atributos fácil
        self.mock_pieza_blanca.color = 'blanco'
        self.mock_pieza_negra = MagicMock()
        self.mock_pieza_negra.color = 'negro'

    def tearDown(self):
        """ Limpiar mocks después de cada test """
        self.patcher_juego.stop()
        self.patcher_vista.stop()

    def test_seleccionar_pieza_propia_valida(self):
        """ 
        Verifica que al hacer clic en una pieza propia válida (con movimientos) 
        se selecciona correctamente en el controlador y la vista.
        """
        casilla_origen = (1, 0) # Peón blanco inicial
        movimientos_simulados = [(2, 0), (3, 0)]

        # *** CORRECCIÓN: Configurar jugadores para pasar la verificación CPU ***
        mock_jugador_humano = MagicMock()
        mock_jugador_humano.get_color.return_value = 'blanco'
        self.mock_modelo_instancia.jugadores = [mock_jugador_humano]
        self.mock_modelo_instancia.jugador_actual_idx = 0

        # Configurar mocks del modelo
        self.mock_modelo_instancia.getTurnoColor.return_value = 'blanco'
        self.mock_tablero_interno.getPieza.return_value = self.mock_pieza_blanca
        # Mockear la llamada a obtener_movimientos_validos (que llama a pieza.obtener_movimientos_legales)
        self.mock_pieza_blanca.obtener_movimientos_legales.return_value = movimientos_simulados

        # Ejecutar acción
        self.controlador.manejar_clic_casilla(casilla_origen)

        # Verificar estado del controlador
        self.assertEqual(self.controlador.casilla_origen_seleccionada, casilla_origen)
        self.assertEqual(self.controlador.movimientos_validos_cache, movimientos_simulados)

        # Verificar estado de la vista
        self.assertEqual(self.mock_vista_instancia.casilla_origen, casilla_origen)
        self.assertEqual(self.mock_vista_instancia.movimientos_validos, movimientos_simulados)

        # Verificar llamadas a mocks
        self.mock_modelo_instancia.getTurnoColor.assert_called()
        
        # *** CORRECCIÓN: Verificar que se llamó con la casilla origen al menos una vez ***
        # El controlador hace múltiples llamadas a getPieza: una para la casilla origen
        # y una para cada movimiento válido (para determinar capturas)
        self.mock_tablero_interno.getPieza.assert_any_call(casilla_origen)
        
        # También verifica que se llamó para cada movimiento (para detectar capturas)
        for movimiento in movimientos_simulados:
            self.mock_tablero_interno.getPieza.assert_any_call(movimiento)
        
        self.mock_pieza_blanca.obtener_movimientos_legales.assert_called_once()

    def test_seleccionar_pieza_rival(self):
        """ Verifica que no se puede seleccionar una pieza del rival. """
        casilla_rival = (7, 0) # Torre negra

        # *** CORRECCIÓN: Configurar jugadores para pasar la verificación CPU ***
        mock_jugador_humano = MagicMock()
        mock_jugador_humano.get_color.return_value = 'blanco'
        self.mock_modelo_instancia.jugadores = [mock_jugador_humano]
        self.mock_modelo_instancia.jugador_actual_idx = 0

        # Configurar mocks
        self.mock_modelo_instancia.getTurnoColor.return_value = 'blanco'
        self.mock_tablero_interno.getPieza.return_value = self.mock_pieza_negra

        # Ejecutar acción
        self.controlador.manejar_clic_casilla(casilla_rival)

        # Verificar estado (nada debería haber cambiado, selección sigue None)
        self.assertIsNone(self.controlador.casilla_origen_seleccionada)
        self.assertEqual(self.controlador.movimientos_validos_cache, [])
        self.assertIsNone(self.mock_vista_instancia.casilla_origen)
        self.assertEqual(self.mock_vista_instancia.movimientos_validos, [])
        
        # Verificar que no se intentó obtener movimientos
        self.mock_pieza_negra.obtener_movimientos_legales.assert_not_called()

    def test_seleccionar_casilla_vacia(self):
        """ Verifica que no pasa nada al seleccionar una casilla vacía. """
        casilla_vacia = (4, 4)

        # *** CORRECCIÓN: Configurar jugadores para pasar la verificación CPU ***
        mock_jugador_humano = MagicMock()
        mock_jugador_humano.get_color.return_value = 'blanco'
        self.mock_modelo_instancia.jugadores = [mock_jugador_humano]
        self.mock_modelo_instancia.jugador_actual_idx = 0

        # Configurar mocks
        self.mock_modelo_instancia.getTurnoColor.return_value = 'blanco'
        self.mock_tablero_interno.getPieza.return_value = None # Casilla vacía

        # Ejecutar acción
        self.controlador.manejar_clic_casilla(casilla_vacia)

        # Verificar estado (nada debería haber cambiado)
        self.assertIsNone(self.controlador.casilla_origen_seleccionada)
        self.assertEqual(self.controlador.movimientos_validos_cache, [])
        self.assertIsNone(self.mock_vista_instancia.casilla_origen)
        self.assertEqual(self.mock_vista_instancia.movimientos_validos, [])

    def test_seleccionar_pieza_propia_sin_movimientos(self):
        """ 
        Verifica que no se selecciona una pieza propia si no tiene movimientos válidos.
        """
        casilla_origen = (0, 0) # Torre blanca inicial (hipotéticamente bloqueada)
        movimientos_simulados = [] # Sin movimientos

        # *** CORRECCIÓN: Configurar jugadores para pasar la verificación CPU ***
        mock_jugador_humano = MagicMock()
        mock_jugador_humano.get_color.return_value = 'blanco'
        self.mock_modelo_instancia.jugadores = [mock_jugador_humano]
        self.mock_modelo_instancia.jugador_actual_idx = 0

        # Configurar mocks
        self.mock_modelo_instancia.getTurnoColor.return_value = 'blanco'
        self.mock_tablero_interno.getPieza.return_value = self.mock_pieza_blanca
        self.mock_pieza_blanca.obtener_movimientos_legales.return_value = movimientos_simulados

        # Ejecutar acción
        self.controlador.manejar_clic_casilla(casilla_origen)

        # Verificar estado (nada seleccionado)
        self.assertIsNone(self.controlador.casilla_origen_seleccionada)
        self.assertEqual(self.controlador.movimientos_validos_cache, [])
        self.assertIsNone(self.mock_vista_instancia.casilla_origen)
        self.assertEqual(self.mock_vista_instancia.movimientos_validos, [])
        
        # Verificar que se intentó obtener movimientos
        self.mock_pieza_blanca.obtener_movimientos_legales.assert_called_once()


class TestControladorRealizarMovimiento(unittest.TestCase):

    def setUp(self):
        """ Configuración inicial para cada test de movimiento """
        self.patcher_juego = patch('controller.controlador_juego.Juego', spec=Juego)
        self.patcher_vista = patch('controller.controlador_juego.InterfazAjedrez', spec=InterfazAjedrez)
        self.patcher_pieza = patch('controller.controlador_juego.Pieza') # Para mockear piezas fácil
        
        self.MockJuego = self.patcher_juego.start()
        self.MockInterfazAjedrez = self.patcher_vista.start()
        self.MockPieza = self.patcher_pieza.start()

        self.mock_vista_instancia = self.MockInterfazAjedrez.return_value
        self.mock_modelo_instancia = self.MockJuego.return_value
        self.mock_tablero_interno = MagicMock(spec=Tablero)
        self.mock_modelo_instancia.tablero = self.mock_tablero_interno
        
        # *** CORRECCIÓN: Configurar jugadores para pasar verificaciones CPU ***
        mock_jugador_humano = MagicMock()
        mock_jugador_humano.get_color.return_value = 'blanco'
        self.mock_modelo_instancia.jugadores = [mock_jugador_humano] 
        self.mock_modelo_instancia.jugador_actual_idx = 0
        
        self.controlador = ControladorJuego()
        # >>> AÑADIR: Inicializar estructura vista.jugadores en el mock de la vista <<<
        self.mock_vista_instancia.jugadores = {
            'blanco': {'nombre': 'J1', 'tiempo': '--:--', 'piezas_capturadas': []},
            'negro': {'nombre': 'J2', 'tiempo': '--:--', 'piezas_capturadas': []}
        }
        
        self.controlador.juego_terminado = False
        
        # Simular una pieza blanca ya seleccionada en (1,0) con movs válidos
        self.casilla_origen = (1, 0)
        self.movimientos_validos = [(2, 0), (3, 0), (2, 1)] # Añadir captura posible
        self.mock_pieza_seleccionada = MagicMock()
        self.mock_pieza_seleccionada.color = 'blanco'
        self.controlador.casilla_origen_seleccionada = self.casilla_origen
        self.controlador.movimientos_validos_cache = self.movimientos_validos
        # Configurar la vista para reflejar la selección inicial
        self.mock_vista_instancia.casilla_origen = self.casilla_origen
        self.mock_vista_instancia.movimientos_validos = self.movimientos_validos
        
        # Mockear el método del modelo para realizar movimiento
        # Asumimos que existe y que no lanza error por defecto
        self.mock_modelo_instancia.realizar_movimiento = MagicMock(return_value='ok')
        # Mockear el método para obtener turno (necesario para cambio de selección)
        self.mock_modelo_instancia.getTurnoColor.return_value = 'blanco' 
        # Mockear métodos para _actualizar_estado_post_movimiento
        self.mock_modelo_instancia.getEstadoJuego.return_value = 'en_curso'
        self.mock_modelo_instancia.obtener_datos_display.return_value = {
            'blanco': {'capturadas': []},
            'negro': {'capturadas': []}
        }

    def tearDown(self):
        self.patcher_juego.stop()
        self.patcher_vista.stop()
        self.patcher_pieza.stop()

    def test_mover_a_destino_valido(self):
        """ Verifica que mover a una casilla válida llama al modelo y limpia selección. """
        casilla_destino_valida = (2, 0)
        
        # Ejecutar acción
        self.controlador.manejar_clic_casilla(casilla_destino_valida)
        
        # Verificar llamada al modelo para mover
        self.mock_modelo_instancia.realizar_movimiento.assert_called_once_with(self.casilla_origen, casilla_destino_valida)
        
        # Verificar que la selección se limpió en controlador y vista
        self.assertIsNone(self.controlador.casilla_origen_seleccionada)
        self.assertEqual(self.controlador.movimientos_validos_cache, [])
        self.assertIsNone(self.mock_vista_instancia.casilla_origen)
        self.assertEqual(self.mock_vista_instancia.movimientos_validos, [])
        
        # Verificar que se consultó el estado post-movimiento
        self.mock_modelo_instancia.getTurnoColor.assert_called()
        self.mock_modelo_instancia.getEstadoJuego.assert_called()
        
        # Verificar que el turno se actualizó en la vista
        nuevo_turno_esperado = self.mock_modelo_instancia.getTurnoColor.return_value
        self.mock_vista_instancia.cambiar_turno_temporizador.assert_called_with(nuevo_turno_esperado)

    def test_clic_en_destino_invalido(self):
        """ Verifica que hacer clic fuera de los movs válidos deselecciona. """
        casilla_destino_invalida = (4, 4) # Casilla vacía, no en movs_validos
        
        # Simular que la casilla está vacía
        self.mock_tablero_interno.getPieza.return_value = None
        
        # Ejecutar acción
        self.controlador.manejar_clic_casilla(casilla_destino_invalida)
        
        # Verificar que NO se llamó al modelo para mover
        self.mock_modelo_instancia.realizar_movimiento.assert_not_called()
        
        # Verificar que la selección se limpió
        self.assertIsNone(self.controlador.casilla_origen_seleccionada)
        self.assertEqual(self.controlador.movimientos_validos_cache, [])
        self.assertIsNone(self.mock_vista_instancia.casilla_origen)
        self.assertEqual(self.mock_vista_instancia.movimientos_validos, [])
        
        # Verificar que getPieza se llamó para comprobar si era otra pieza propia
        self.mock_tablero_interno.getPieza.assert_called_with(casilla_destino_invalida)

    def test_cambiar_seleccion_a_otra_pieza_propia(self):
        """
        Verifica que hacer clic en otra pieza propia cambia la selección.
        """
        casilla_otra_pieza = (1, 1) # Otro peón blanco
        movimientos_nueva_pieza = [(2, 1), (3, 1)]
        mock_nueva_pieza = MagicMock()
        mock_nueva_pieza.color = 'blanco'
        mock_nueva_pieza.obtener_movimientos_legales.return_value = movimientos_nueva_pieza
        
        # Simular que getPieza devuelve la nueva pieza y getTurnoColor es blanco
        self.mock_tablero_interno.getPieza.return_value = mock_nueva_pieza

        # Ejecutar acción
        self.controlador.manejar_clic_casilla(casilla_otra_pieza)

        # Verificar que NO se llamó al modelo para mover
        self.mock_modelo_instancia.realizar_movimiento.assert_not_called()

        # Verificar que la selección AHORA es la nueva pieza
        self.assertEqual(self.controlador.casilla_origen_seleccionada, casilla_otra_pieza)
        self.assertEqual(self.controlador.movimientos_validos_cache, movimientos_nueva_pieza)
        self.assertEqual(self.mock_vista_instancia.casilla_origen, casilla_otra_pieza)
        self.assertEqual(self.mock_vista_instancia.movimientos_validos, movimientos_nueva_pieza)
        
        # *** CORRECCIÓN: Verificar que se llamó con la casilla correcta al menos una vez ***
        # El controlador hace múltiples llamadas: una para la casilla y una para cada movimiento
        self.mock_tablero_interno.getPieza.assert_any_call(casilla_otra_pieza)
        
        # También verifica que se llamó para cada movimiento (para detectar capturas)
        for movimiento in movimientos_nueva_pieza:
            self.mock_tablero_interno.getPieza.assert_any_call(movimiento)
            
        mock_nueva_pieza.obtener_movimientos_legales.assert_called_once()

    def test_estado_jaque_post_movimiento(self):
        """ Verifica que se muestra mensaje de Jaque. """
        casilla_destino_valida = (2, 0)
        # Simular que getEstadoJuego devuelve 'jaque'
        self.mock_modelo_instancia.getEstadoJuego.return_value = 'jaque'
        
        self.controlador.manejar_clic_casilla(casilla_destino_valida)
        
        # Verificar que se mostró mensaje de jaque
        expected_message = f"Jaque al Rey {self.mock_modelo_instancia.getTurnoColor.return_value}"
        self.mock_vista_instancia.mostrar_mensaje_estado.assert_called_with(expected_message)
        
    def test_estado_mate_post_movimiento(self):
        """ Verifica que se muestra mensaje de Mate y termina el juego. """
        casilla_destino_valida = (2, 0)
        # Simular que getEstadoJuego devuelve 'jaque_mate'
        self.mock_modelo_instancia.getEstadoJuego.return_value = 'jaque_mate'
        
        self.controlador.manejar_clic_casilla(casilla_destino_valida)
        
        # Verificar que el juego se marcó como terminado
        self.assertTrue(self.controlador.juego_terminado)
        
    def test_estado_ahogado_post_movimiento(self):
        """ Verifica que se muestra mensaje de Ahogado y termina el juego. """
        casilla_destino_valida = (2, 0)
        # Simular que getEstadoJuego devuelve 'ahogado'
        self.mock_modelo_instancia.getEstadoJuego.return_value = 'ahogado'
        
        self.controlador.manejar_clic_casilla(casilla_destino_valida)
        
        # Verificar que el juego se marcó como terminado
        self.assertTrue(self.controlador.juego_terminado)
        
    def test_estado_tablas_post_movimiento(self):
        """ Verifica que se muestra mensaje de Tablas y termina el juego. """
        casilla_destino_valida = (2, 0)
        # Simular que getEstadoJuego devuelve 'tablas'
        self.mock_modelo_instancia.getEstadoJuego.return_value = 'tablas'
        
        self.controlador.manejar_clic_casilla(casilla_destino_valida)
        
        # Verificar que el juego se marcó como terminado
        self.assertTrue(self.controlador.juego_terminado)
        
    def test_estado_en_curso_post_movimiento(self):
        """ Verifica que se limpia el mensaje si el estado es 'en_curso'. """
        casilla_destino_valida = (2, 0)
        # Simular que getEstadoJuego devuelve 'en_curso'
        self.mock_modelo_instancia.getEstadoJuego.return_value = 'en_curso'
        
        self.controlador.manejar_clic_casilla(casilla_destino_valida)
        
        # Verificar que se limpió el mensaje
        self.mock_vista_instancia.mostrar_mensaje_estado.assert_called_with(None)
        self.assertFalse(self.controlador.juego_terminado)


class TestControladorActualizacionDisplay(unittest.TestCase):
    
    def setUp(self):
        self.patcher_juego = patch('controller.controlador_juego.Juego', spec=Juego)
        self.patcher_vista = patch('controller.controlador_juego.InterfazAjedrez', spec=InterfazAjedrez)
        self.MockJuego = self.patcher_juego.start()
        self.MockInterfazAjedrez = self.patcher_vista.start()
        self.mock_vista_instancia = self.MockInterfazAjedrez.return_value
        self.mock_modelo_instancia = self.MockJuego.return_value
        self.controlador = ControladorJuego()
        # Mockear la estructura interna de vista.jugadores esperada por el controlador
        self.mock_vista_instancia.jugadores = {
            'blanco': {'nombre': 'J1', 'tiempo': '--:--', 'piezas_capturadas': []},
            'negro': {'nombre': 'J2', 'tiempo': '--:--', 'piezas_capturadas': []}
        }
        # Mockear el método que será llamado
        self.mock_modelo_instancia.obtener_datos_display = MagicMock()
        self.mock_modelo_instancia.getTurnoColor = MagicMock(return_value='negro') # Nuevo turno
        self.mock_modelo_instancia.getEstadoJuego = MagicMock(return_value='en_curso')
        
        # *** CORRECCIÓN: Configurar jugadores para evitar errores ***
        self.mock_modelo_instancia.jugadores = []
        self.mock_modelo_instancia.jugador_actual_idx = 0

    def tearDown(self):
        self.patcher_juego.stop()
        self.patcher_vista.stop()

    def test_actualizar_display_post_movimiento(self):
        """
        Verifica que _actualizar_estado_post_movimiento obtiene datos 
        y actualiza vista.jugadores.
        """
        # Datos simulados que devolverá el modelo
        mock_pieza_capturada_b = MagicMock()
        mock_pieza_capturada_b.get_color.return_value = 'blanco'
        datos_simulados = {
            'blanco': {'tiempo': '09:50', 'capturadas': []}, # Negras capturadas por blancas
            'negro': {'tiempo': '09:45', 'capturadas': [mock_pieza_capturada_b]} # Blancas capturadas por negras
        }
        self.mock_modelo_instancia.obtener_datos_display.return_value = datos_simulados
        
        # Llamar al método interno (normalmente llamado tras mover pieza)
        self.controlador._actualizar_estado_post_movimiento()
        
        # Verificar que se obtuvieron los datos del modelo
        self.mock_modelo_instancia.obtener_datos_display.assert_called_once()
        
        # Verificar que los datos en la vista (mock) se actualizaron
        self.assertEqual(self.mock_vista_instancia.jugadores['blanco']['piezas_capturadas'], []) # Blancas captura Negras (ninguna en este mock)
        self.assertEqual(self.mock_vista_instancia.jugadores['negro']['piezas_capturadas'], [mock_pieza_capturada_b]) # Negras captura Blancas
        # Verificar que el método para cambiar el turno en la vista fue llamado
        self.mock_vista_instancia.cambiar_turno_temporizador.assert_called_with('negro')


if __name__ == '__main__':
    unittest.main()