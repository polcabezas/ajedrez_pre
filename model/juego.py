"""
Gestiona el estado general del juego (turno, jaque, jaque mate, tablas).
""" 
from typing import List, Tuple, Optional, Literal, Dict
from model.tablero import Tablero
from model.temporizador import Temporizador
from model.jugadores.jugador_humano import JugadorHumano
from model.jugadores.jugador_cpu import JugadorCPU
from model.configuracion_juego import ConfiguracionJuego
import logging
from .validador_movimiento import ValidadorMovimiento
from .ejecutor_movimiento import EjecutorMovimiento
from .evaluador_estado_de_juego import EvaluadorEstadoDeJuego
from .gestor_del_historico import GestorDelHistorico

logger = logging.getLogger(__name__)

class Juego:
    """
    Clase que gestiona el estado global del juego de ajedrez.
    Coordina el tablero, los jugadores, el estado del juego y el historial.
    """
    
    def __init__(self):
        """
        Inicializa una nueva instancia de juego con valores por defecto o vacíos.
        La configuración específica se aplica con configurar_nueva_partida.
        """
        self.tablero: Tablero = Tablero() # Crear tablero inicial
        self.jugadores: List[JugadorHumano] = []
        self.jugador_actual_idx: int = 0
        self.estado: Literal['inicio', 'en_curso', 'jaque', 'jaque_mate', 'tablas', 'ahogado'] = "inicio"
        self.color_activo: Optional[Literal['blanco', 'negro']] = None
        self.temporizador: Optional[Temporizador] = None
        self.config: Optional[Dict] = None

        # Instanciar helpers pasando la referencia inicial del tablero
        # ASUNCIÓN: Juego es responsable de crear estos helpers.
        # Si Tablero los crea internamente, esta parte no sería necesaria aquí.
        self.validador = ValidadorMovimiento(self.tablero)
        self.ejecutor = EjecutorMovimiento(self.tablero)
        self.evaluador = EvaluadorEstadoDeJuego(self.tablero)
        self.historial = GestorDelHistorico(self.tablero)
        # Asegurar que el tablero también tenga referencia a su gestor (si no lo crea él mismo)
        if not hasattr(self.tablero, 'gestor_historico') or self.tablero.gestor_historico is None:
             self.tablero.gestor_historico = self.historial
    
    def configurar_nueva_partida(self, config: dict):
        """
        Configura el juego para una nueva partida según las opciones dadas.
        Reinicia el tablero, estado, historial y configura jugadores/temporizador.

        Args:
            config: Diccionario con las opciones, ej:
                    {'tipo_juego': 'Clásico', 'modalidad': 'Humano vs Humano'}
        """
        logger.info("Configurando nueva partida con: %s", config)
        self.config = config
        
        # 1. Crear un nuevo Tablero
        self.tablero = Tablero() 
        self.estado = "en_curso"
        self.color_activo = "blanco"
        self.jugador_actual_idx = 0

        # 2. Actualizar referencias al tablero en los helpers
        self.validador.tablero = self.tablero
        self.ejecutor.tablero = self.tablero
        self.evaluador.tablero = self.tablero
        self.historial.tablero = self.tablero
        # Asegurar que el nuevo tablero tenga referencia al gestor
        self.tablero.gestor_historico = self.historial

        # 3. Reiniciar historial de posiciones y registrar posición inicial
        self.historial.historial_posiciones.clear()
        self.historial.registrar_posicion() # Registrar estado inicial
        
        # 4. Configurar Jugadores
        modalidad = config.get('modalidad', 'Humano vs Humano')
        self.jugadores = [] 
        try:
            if modalidad == 'Humano vs Humano':
                self.jugadores.append(JugadorHumano(nombre="Jugador 1", color='blanco'))
                self.jugadores.append(JugadorHumano(nombre="Jugador 2", color='negro'))
            elif modalidad == 'Humano vs CPU':
                self.jugadores.append(JugadorHumano(nombre="Humano", color='blanco'))
                self.jugadores.append(JugadorCPU(nombre="CPU", color='negro'))
            elif modalidad == 'CPU vs Humano':
                self.jugadores.append(JugadorCPU(nombre="CPU 1", color='blanco'))
                self.jugadores.append(JugadorHumano(nombre="Humano", color='negro'))
            elif modalidad == 'CPU vs CPU':
                self.jugadores.append(JugadorCPU(nombre="CPU 1", color='blanco'))
                self.jugadores.append(JugadorCPU(nombre="CPU 2", color='negro'))
            else:
                 logger.warning(f"Modalidad '{modalidad}' no reconocida, usando Humano vs Humano.")
                 self.jugadores.append(JugadorHumano(nombre="Jugador 1", color='blanco'))
                 self.jugadores.append(JugadorHumano(nombre="Jugador 2", color='negro'))
            logger.info(f"Jugadores configurados para modalidad: {modalidad}")
        except NameError as ne:
            logger.error(f"ERROR: Clase JugadorHumano o JugadorCPU no encontrada: {ne}.")
            self.jugadores = []
        except Exception as e:
            logger.error(f"Error al crear jugadores: {e}")
            self.jugadores = []

        # 5. Configurar Temporizador
        tipo_juego = config.get('tipo_juego', 'Clásico')
        tiempo_base = None
        if tipo_juego == 'Clásico':
            tiempo_base = 600
        elif tipo_juego == 'Rápido':
            tiempo_base = 300
        elif tipo_juego == 'Blitz':
            tiempo_base = 180
        
        if tiempo_base:
            try:
                tiempos = {'blanco': tiempo_base, 'negro': tiempo_base}
                self.temporizador = Temporizador(tiempos_iniciales=tiempos)
                logger.info(f"Temporizador configurado para tipo: {tipo_juego} ({tiempo_base}s)")
            except NameError:
                 logger.error("ERROR: Clase 'Temporizador' no encontrada.")
                 self.temporizador = None
            except Exception as e:
                logger.error(f"Error al crear temporizador: {e}")
                self.temporizador = None
        else:
            self.temporizador = None
            logger.info(f"No se configuró temporizador para tipo: {tipo_juego}")

        if self.temporizador:
            self.temporizador.iniciar_turno(self.color_activo)

    def realizar_movimiento(self, origen: Tuple[int, int], destino: Tuple[int, int]) -> Literal['ok', 'promocion_requerida', 'error']:
        """
        Ejecuta un movimiento (asumido legal) en el tablero.
        Utiliza EjecutorMovimiento para modificar el estado del tablero,
        actualizar historial, cambiar turno y estado del juego.
        Gestiona el temporizador.

        Args:
            origen (Tuple[int, int]): Coordenadas (fila, columna) de la casilla de origen.
            destino (Tuple[int, int]): Coordenadas (fila, columna) de la casilla de destino.

        Returns:
            Literal['ok', 'promocion_requerida', 'error']:
                - 'ok': Movimiento ejecutado correctamente.
                - 'promocion_requerida': El movimiento fue un peón a la última fila.
                - 'error': Ocurrió un error durante la ejecución.
        """
        logger.debug(f"Ejecutando movimiento: {origen} -> {destino} por {self.color_activo}")
        color_jugador_actual = self.color_activo

        try:
            # 1. Ejecutar el movimiento usando el Ejecutor
            # El ejecutor se encarga de: mover pieza, captura, actualizar tablero (enroque, ep, contadores), 
            # cambiar turno, llamar a actualizarEstadoJuego y registrar posición en historial.
            # ASUNCIÓN: Por ahora, solo manejamos movimientos normales aquí.
            # TODO: Determinar cómo se maneja el enroque (¿llamada separada o detectada por ejecutor?)
            resultado_ejecucion = self.ejecutor.ejecutar_movimiento_normal(origen, destino)

            if resultado_ejecucion == 'error':
                logger.error(f"Ejecutor devolvió error para movimiento {origen}->{destino}")
                # TODO: Considerar si hay que revertir el temporizador si falló
                return 'error'

            # 2. Actualizar estado del Juego y color activo (leer desde tablero)
            self.estado = self.tablero.estado_juego # El ejecutor llamó a actualizarEstadoJuego
            self.color_activo = self.tablero.getTurnoColor() # Leer el turno actual del tablero
            # Actualizar índice del jugador basado en el nuevo color activo
            if self.jugadores:
                self.jugador_actual_idx = 0 if self.color_activo == self.jugadores[0].get_color() else 1

            logger.info(f"Movimiento {origen}->{destino} ejecutado. Nuevo estado: {self.estado}. Turno de {self.color_activo}.")

            # 3. Iniciar temporizador del nuevo jugador (si existe y el juego no ha terminado)
            if self.temporizador and self.estado in ['en_curso', 'jaque']:
                self.temporizador.iniciar_turno(self.color_activo)

            # 4. Devolver resultado
            if resultado_ejecucion == 'promocion_necesaria':
                return 'promocion_requerida'
            else:
                return 'ok'

        except Exception as e:
            logger.error(f"Error inesperado durante realizar_movimiento {origen}->{destino}: {e}", exc_info=True)
            # TODO: Estado potencialmente inconsistente. ¿Revertir?
            return 'error'

    def getTurnoColor(self) -> Optional[Literal['blanco', 'negro']]:
        """
        Obtiene el color del jugador cuyo turno es.
        """
        return self.color_activo

    def getEstadoJuego(self) -> str:
        """ Devuelve el estado actual del juego. """
        return self.estado
        
    def obtener_datos_display(self) -> Dict[str, Dict]:
        """
        Recopila y devuelve los datos necesarios para actualizar la interfaz
        (tiempos, piezas capturadas).
        
        Returns:
            Un diccionario con la información para cada color:
            {
                'blanco': {'tiempo': 'MM:SS', 'capturadas': [Pieza, ...]},
                'negro': {'tiempo': 'MM:SS', 'capturadas': [Pieza, ...]}
            }
        """
        datos = {
            'blanco': {'tiempo': '--:--', 'capturadas': []},
            'negro': {'tiempo': '--:--', 'capturadas': []}
        }

        # Obtener tiempos
        if self.temporizador:
            tiempos_fmt = self.temporizador.get_tiempos_formateados()
            datos['blanco']['tiempo'] = tiempos_fmt.get('blanco', '--:--')
            datos['negro']['tiempo'] = tiempos_fmt.get('negro', '--:--')
            
        # Obtener piezas capturadas (usando la lista del tablero)
        piezas_capturadas_blancas = []
        piezas_capturadas_negras = []
        
        if hasattr(self.tablero, 'piezasCapturadas') and self.tablero.piezasCapturadas:
            for pieza in self.tablero.piezasCapturadas:
                try:
                    # Intentar obtener el color de la pieza (primero con get_color, luego con color)
                    color_pieza = None
                    if hasattr(pieza, 'get_color') and callable(pieza.get_color):
                        color_pieza = pieza.get_color()
                    elif hasattr(pieza, 'color'):
                        color_pieza = pieza.color
                    
                    # Distribuir la pieza según su color
                    if color_pieza == 'blanco':
                        piezas_capturadas_blancas.append(pieza)
                    elif color_pieza == 'negro':
                        piezas_capturadas_negras.append(pieza)
                    else:
                        logger.warning(f"Pieza capturada con color desconocido: {pieza}")
                except Exception as e:
                    logger.error(f"Error al procesar pieza capturada: {e}")
            
            # IMPORTANTE: Cada jugador ve las piezas que ha capturado, no las suyas que han sido capturadas
            # Blanco muestra las negras capturadas, Negro muestra las blancas capturadas.
            datos['blanco']['capturadas'] = piezas_capturadas_negras
            datos['negro']['capturadas'] = piezas_capturadas_blancas
            
            logger.debug(f"Piezas capturadas: Blancas={len(piezas_capturadas_blancas)}, Negras={len(piezas_capturadas_negras)}")
        else:
            logger.warning("El objeto Tablero no tiene el atributo 'piezasCapturadas' o está vacío")
            datos['blanco']['capturadas'] = []
            datos['negro']['capturadas'] = []

        return datos