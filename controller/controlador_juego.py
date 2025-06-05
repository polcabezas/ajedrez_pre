"""
Gestiona la entrada del usuario y la comunicación entre el Modelo y la Vista.
""" 

import pygame
import sys
import os
from typing import Tuple, List, Optional

# --- Añadir Logging ---
import logging

# Configuración básica de logging para este módulo
# Si tienes una config global en main.py, podrías omitir esto.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__) # Crear un logger específico para este módulo
# ---------------------

# Añadir el directorio raíz al sys.path para asegurar que los módulos se encuentren
# Esto asume que controlador_juego.py está en una subcarpeta 'controller' del directorio raíz del proyecto
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from model.juego import Juego
from model.piezas.pieza import Pieza
from model.piezas.rey import Rey
from model.tablero import Tablero
from model.jugadores.jugador_cpu import JugadorCPU
from view.interfaz_ajedrez import InterfazAjedrez

# Importar KillGame para uso en desarrollo
from model.kill_game import KillGame

class ControladorJuego:
    """
    Coordina la interacción entre el modelo (lógica del juego) y 
    la vista (interfaz gráfica).
    """
    def __init__(self):
        """
        Inicializa el controlador, creando instancias del modelo y la vista.
        """
        # Comentario: Instancia el modelo principal del juego.
        self.modelo = Juego() 
        
        # Comentario: Instancia la vista, pasándose a sí mismo como controlador.
        # La vista se encargará de inicializar pygame internamente.
        self.vista = InterfazAjedrez(self)
        
        self.running = False # Controla el bucle principal

    # --- Métodos para ser llamados por la Vista ---
    def obtener_tablero(self):
        """
        Devuelve el objeto tablero actual desde el modelo.
        Permite a la vista acceder al estado del tablero a través del controlador.
        
        Returns:
            Tablero: La instancia actual del tablero del modelo.
        """
        # >>> Añadir esta línea para depuración <<<
        logger.debug("ControladorJuego.obtener_tablero() llamado. Modelo es: %s", type(self.modelo))
        # Comentario: Delega la llamada al método correspondiente del modelo.
        # ASUNCIÓN: self.modelo tiene un método obtener_tablero()
        # return self.modelo.obtener_tablero() # <-- Código antiguo con error
        # Corrección: Acceder directamente al atributo 'tablero' del modelo Juego
        return self.modelo.tablero

    def obtener_movimientos_validos(self, casilla: Tuple[int, int], pieza: Optional[Pieza] = None) -> List[Tuple[int, int]]:
        """
        Obtiene la lista de movimientos válidos para la pieza en la casilla dada.
        Delega la lógica al modelo (específicamente a la pieza).

        Args:
            casilla: Tupla (fila, columna) de la casilla seleccionada.
            pieza: (Opcional) La instancia de la pieza ya obtenida.
                   Si es None, se buscará la pieza en el tablero.

        Returns:
            Lista de tuplas (fila, columna) representando las casillas destino válidas.
            Devuelve una lista vacía si no hay pieza o no tiene movimientos.
        """
        movimientos_validos = []
        if pieza is None:
            # Si no nos pasaron la pieza, la obtenemos
            pieza = self.modelo.tablero.getPieza(casilla)
        
        if pieza:
            # Asumimos que la pieza tiene un método que devuelve sus movimientos legales
            # Este método ya debería filtrar movimientos que dejen al rey en jaque.
            # Si este método no existe en tu clase Pieza base/subclases, necesitarás ajustarlo.
            try:
                movimientos_validos = pieza.obtener_movimientos_legales()
                logger.debug("Movimientos válidos para %s en %s: %s", pieza, casilla, movimientos_validos)
            except AttributeError:
                logger.error("ERROR: La pieza %s en %s no tiene el método 'obtener_movimientos_legales()'", type(pieza), casilla)
                movimientos_validos = [] # Devolver lista vacía en caso de error
            except Exception as e:
                logger.error("ERROR inesperado al obtener movimientos para %s en %s: %s", pieza, casilla, e)
                movimientos_validos = []
        else:
             logger.debug("No hay pieza en la casilla %s para obtener movimientos.", casilla)
             
        return movimientos_validos

    def solicitar_inicio_juego(self):
        """
        Llamado por la Vista cuando el usuario pulsa 'Jugar'.
        Obtiene la configuración, inicializa el modelo y cambia la vista.
        Valida que se hayan seleccionado las opciones requeridas antes de iniciar.
        """
        config = self.vista.obtener_configuracion()
        
        # Verificar si la configuración es válida
        if config is None:
            # Si no hay configuración válida, mostrar mensaje de error
            self.vista.mostrar_error_config("Debes seleccionar un tipo y una modalidad de juego")
            return
            
        logger.debug("Controlador solicitando inicio de juego con config: %s", config)
        
        # === PASO CLAVE: Inicializar/Configurar el modelo ===
        # Llama al método de configuración definido en el modelo.
        config_method_name = 'configurar_nueva_partida' # <- Nombre del método en la clase Juego
        try:
            config_method = getattr(self.modelo, config_method_name, None)
            if callable(config_method):
                config_method(config) # Llamar al método encontrado
                logger.info(f"Modelo configurado usando {config_method_name} con %s", config)
            else:
                # Fallback si el método no existe
                logger.warning(f"WARN: Modelo no tiene método '{config_method_name}'. Reiniciando tablero por defecto.")
                self.modelo.tablero = Tablero() # Crear un tablero nuevo
        except Exception as e:
            logger.error(f"ERROR al llamar a {config_method_name} en el modelo: %s", e)
            # return # Considerar no cambiar de vista si falla
            
        # Cambiar a la vista del tablero
        self.vista.cambiar_vista('tablero')
        logger.debug("Vista cambiada a 'tablero'")

        # Resetear estado interno del controlador relacionado con la selección
        self.casilla_origen_seleccionada = None
        self.movimientos_validos_cache = []
        self.juego_terminado = False 
        
        # Estado para gestión de promoción de peón
        self.promocion_en_proceso = False
        self.casilla_promocion = None  # Casilla donde está el peón que se promoverá
        self.origen_promocion = None   # Casilla de origen del movimiento de promoción 

        # Limpiar la selección visual en la vista por si acaso
        self.vista.casilla_origen = None
        self.vista.movimientos_validos = []
        
        # Forzar una actualización inmediata para mostrar el tablero limpio
        self.vista.actualizar(self.obtener_tablero())
        
        # AÑADIDO: Verificar si el jugador inicial es CPU y programar su movimiento
        if len(self.modelo.jugadores) >= 2:
            jugador_inicial = self.modelo.jugadores[self.modelo.jugador_actual_idx]
            if isinstance(jugador_inicial, JugadorCPU):
                logger.info("Programando movimiento inicial para jugador CPU")
                self.tiempo_movimiento_cpu = pygame.time.get_ticks() + 1000  # 1 segundo de delay inicial

    def manejar_clic_casilla(self, casilla: Tuple[int, int]):
        """
        Gestiona la lógica principal cuando el usuario hace clic en una casilla del tablero.
        """
        logger.debug("Controlador: Clic en casilla %s", casilla)
        if self.juego_terminado:
            logger.debug("Juego terminado, ignorando clic.")
            return

        # Verificar si el jugador actual es una CPU
        jugador_actual = self.modelo.jugadores[self.modelo.jugador_actual_idx]
        if isinstance(jugador_actual, JugadorCPU):
            logger.info("Turno de CPU, ignorando clic.")
            return

        # Obtener estado necesario
        tablero = self.modelo.tablero # Acceso directo al tablero del juego
        pieza = tablero.getPieza(casilla) # <<< Llamada 1 a getPieza
        turno_actual = self.modelo.getTurnoColor() # Asume que Juego tiene getTurnoColor

        # === CASO 1: No hay pieza seleccionada previamente ===
        if self.casilla_origen_seleccionada is None:
            # Intentar seleccionar la pieza en la casilla clickeada
            if pieza is not None and pieza.color == turno_actual:
                # Es una pieza propia, obtener sus movimientos
                # Pasar la pieza ya obtenida para evitar segunda llamada a getPieza
                movimientos = self.obtener_movimientos_validos(casilla, pieza=pieza)
                if movimientos:
                    # Si hay movimientos válidos, seleccionar la pieza
                    self.casilla_origen_seleccionada = casilla
                    self.movimientos_validos_cache = movimientos
                    
                    # Identificar cuáles son movimientos de captura (casillas con piezas rivales)
                    capturas = []
                    movimientos_sin_captura = []
                    enroques_disponibles = [] # Nueva lista para destinos de enroque del rey

                    if isinstance(pieza, Rey):
                        # Para el rey, los movimientos a 2 casillas de distancia horizontal son enroques
                        col_origen = casilla[1]
                        for mov in movimientos:
                            if abs(col_origen - mov[1]) == 2:
                                enroques_disponibles.append(mov)
                            else:
                                pieza_destino = tablero.getPieza(mov)
                                if pieza_destino is not None and pieza_destino.color != pieza.color:
                                    capturas.append(mov)
                                else:
                                    movimientos_sin_captura.append(mov)
                    else:
                        for mov in movimientos:
                            pieza_destino = tablero.getPieza(mov)
                            if pieza_destino is not None and pieza_destino.color != pieza.color:
                                capturas.append(mov)
                            else:
                                movimientos_sin_captura.append(mov)
                            
                    # Actualizar la vista para mostrar resaltados
                    self.vista.casilla_origen = casilla
                    self.vista.movimientos_validos = movimientos_sin_captura
                    self.vista.casillas_captura = capturas
                    self.vista.casillas_enroque_disponible = enroques_disponibles # Pasar a la vista
                    
                    logger.debug("Pieza %s en %s seleccionada. Movs normales: %s, Capturas: %s, Enroques: %s", 
                                 pieza, casilla, movimientos_sin_captura, capturas, enroques_disponibles)
                else:
                    # Pieza propia sin movimientos válidos
                    logger.debug("Pieza %s en %s no tiene movimientos válidos.", pieza, casilla)
                    self._limpiar_seleccion_vista() # Limpiar por si acaso
            else:
                # Clic en casilla vacía o pieza rival cuando nada estaba seleccionado
                logger.debug("Clic en casilla vacía o pieza rival (%s). No se selecciona.", pieza)
                self._limpiar_seleccion_vista()
        
        # === CASO 2: Ya había una pieza seleccionada ===
        else:
             # Verificar si el clic fue en un destino válido (movimiento normal o captura)
             if casilla in self.movimientos_validos_cache:
                 # --- Ejecutar Movimiento --- 
                 origen = self.casilla_origen_seleccionada
                 logger.debug("Intentando mover de %s a %s", origen, casilla)
                 
                 # ASUNCIÓN: El modelo tiene un método para realizar el movimiento
                 # Este método debe actualizar el tablero y el turno internamente.
                 # Reemplaza 'realizar_movimiento' si se llama diferente en tu clase Juego.
                 exito_movimiento = False
                 resultado_movimiento = None
                 try:
                     if hasattr(self.modelo, 'realizar_movimiento') and callable(self.modelo.realizar_movimiento):
                         # Idealmente, este método devuelve algo útil (True/False, estado, etc.)
                         resultado_movimiento = self.modelo.realizar_movimiento(origen, casilla)
                         exito_movimiento = True 
                         logger.debug("Modelo realizó movimiento. Resultado: %s", resultado_movimiento)
                     else:
                         logger.error("ERROR: El modelo Juego no tiene el método 'realizar_movimiento'")
                 except Exception as e:
                     logger.error("ERROR: Excepción al llamar a modelo.realizar_movimiento: %s", e)
                     # Podríamos querer no limpiar la selección si el movimiento falla en el modelo

                 if exito_movimiento:
                     # Verificar si el resultado indica que se necesita promoción
                     if resultado_movimiento == 'promocion_requerida':
                         # Promoción de peón detectada
                         self._iniciar_promocion_peon(origen, casilla)
                     else:
                         # Movimiento normal completado
                         self._limpiar_seleccion_vista() # Limpia selección interna y visual
                         self._actualizar_estado_post_movimiento() # Comprueba estado (jaque, mate, etc.)
                 # else: # Si el movimiento falla en el modelo, ¿qué hacer? ¿Mantener selección? 
                     # Por ahora, asumimos que si estaba en movs_validos, el modelo debe aceptarlo
                     # o lanzar una excepción que capturamos.

             elif pieza is not None and pieza.color == turno_actual:
                 # --- Cambiar Selección a otra pieza propia ---
                 logger.debug("Cambiando selección de %s a %s", self.casilla_origen_seleccionada, casilla)
                 self._limpiar_seleccion_vista() # Limpia la selección anterior
                 self.manejar_clic_casilla(casilla) # Llama de nuevo para seleccionar la nueva
             
             else:
                 # --- Clic Inválido (fuera de movimientos, casilla vacía o rival) ---
                 logger.debug("Clic en destino inválido %s. Deseleccionando.", casilla)
                 self._limpiar_seleccion_vista() # Simplemente deseleccionar

    def _limpiar_seleccion_vista(self):
         """ Resetea el estado de selección interno y en la vista. """
         self.casilla_origen_seleccionada = None
         self.movimientos_validos_cache = []
         # Actualizar vista para quitar resaltados
         if self.vista: # Asegurarse de que la vista existe
             self.vista.casilla_origen = None
             self.vista.movimientos_validos = []
             self.vista.casillas_captura = []
             self.vista.casillas_enroque_disponible = [] # Asegurarse de limpiar aquí también
         logger.debug("Selección limpiada.")

    def _actualizar_estado_post_movimiento(self):
        """
        Comprueba el estado del juego después de un movimiento y
        actualiza la interfaz según corresponda.
        """
        logger.debug("Controlador: Actualizando estado post-movimiento.")
        
        # === Obtener TODOS los datos necesarios del modelo ===
        try:
            nuevo_turno = self.modelo.getTurnoColor()
            
            # === Actualizar Temporizador en la Vista PRIMERO ===
            # Asegurarse de llamar a esto antes de actualizar el resto de la UI que podría depender del turno
            self.vista.cambiar_turno_temporizador(nuevo_turno)
            
            # Usar el nuevo método para obtener todos los datos para la vista
            datos_display = self.modelo.obtener_datos_display()
            estado_juego = self.modelo.getEstadoJuego() 
            
            logger.debug("Nuevo turno: %s, Estado: %s, Datos Display: %s", nuevo_turno, estado_juego, datos_display)
            
            # === Actualizar Resto de la Vista ===
            # Actualizar datos de jugadores (nombre se mantiene, tiempo y capturas cambian)
            if 'blanco' in datos_display and 'capturadas' in datos_display['blanco']:
                piezas_capturadas_blanco = datos_display['blanco']['capturadas']
                self.vista.jugadores['blanco']['piezas_capturadas'] = piezas_capturadas_blanco
                if piezas_capturadas_blanco:
                    tipos_capturados = [type(p).__name__ for p in piezas_capturadas_blanco]
                    logger.debug(f"Actualizadas piezas capturadas del jugador blanco: {len(piezas_capturadas_blanco)} piezas: {tipos_capturados}")
                
            if 'negro' in datos_display and 'capturadas' in datos_display['negro']:
                piezas_capturadas_negro = datos_display['negro']['capturadas']
                self.vista.jugadores['negro']['piezas_capturadas'] = piezas_capturadas_negro
                if piezas_capturadas_negro:
                    tipos_capturados = [type(p).__name__ for p in piezas_capturadas_negro]
                    logger.debug(f"Actualizadas piezas capturadas del jugador negro: {len(piezas_capturadas_negro)} piezas: {tipos_capturados}")
            
            # Verificar el estado del juego
            self.juego_terminado = estado_juego in ['jaque_mate', 'tablas', 'ahogado']
            
            # Actualizar mensaje de estado del juego si es necesario
            if estado_juego == 'jaque':
                self.vista.mostrar_mensaje_estado(f"Jaque al Rey {nuevo_turno}")
            elif estado_juego == 'jaque_mate':
                color_ganador = 'negro' if nuevo_turno == 'blanco' else 'blanco'
                self.vista.mostrar_mensaje_estado(f"Jaque Mate. Gana {color_ganador}.")
                self.juego_terminado = True
                self.mostrar_popup_fin_juego('victoria_' + color_ganador, 'jaque_mate')
            elif estado_juego == 'tablas':
                self.vista.mostrar_mensaje_estado("Tablas.")
                self.juego_terminado = True
                # Obtener el motivo específico de tablas desde el modelo
                motivo_tablas = self.modelo.getMotivoTablas() or 'material_insuficiente'
                self.mostrar_popup_fin_juego('tablas', motivo_tablas)
            elif estado_juego == 'ahogado':
                self.vista.mostrar_mensaje_estado("Ahogado. Tablas.")
                self.juego_terminado = True
                self.mostrar_popup_fin_juego('tablas', 'ahogado')
            else:
                self.vista.mostrar_mensaje_estado(None) # Limpiar mensaje si no hay estado especial
            
            # Actualizar tablero
            tablero_actual = self.obtener_tablero()
            self.vista.actualizar(tablero_actual)
            
            # 3. Programar próximo movimiento CPU si corresponde
            if not self.juego_terminado:
                # Verificar si el próximo jugador es CPU
                if len(self.modelo.jugadores) >= 2:
                    jugador_actual = self.modelo.jugadores[self.modelo.jugador_actual_idx]
                    if isinstance(jugador_actual, JugadorCPU):
                        # Programar procesamiento de movimiento CPU con un pequeño delay
                        # para que la interfaz tenga tiempo de actualizarse
                        # Usar un delay más largo para CPU vs CPU para que sea más visible
                        if all(isinstance(j, JugadorCPU) for j in self.modelo.jugadores):
                            delay = 1000  # 1 segundo para CPU vs CPU
                        else:
                            delay = 1000   # 1 segundos para Humano vs CPU
                        
                        self.tiempo_movimiento_cpu = pygame.time.get_ticks() + delay
                        logger.info(f"Programando movimiento CPU para {jugador_actual.get_nombre()} en {delay}ms")
            
        except Exception as e:
            logger.error(f"Excepción en _actualizar_estado_post_movimiento: {e}", exc_info=True)
    
    def _iniciar_promocion_peon(self, origen, destino):
        """
        Inicia el proceso de promoción de peón.
        Guarda el estado del movimiento y muestra el popup de selección.
        
        Args:
            origen: Casilla de origen del peón que se está promoviendo
            destino: Casilla de destino (donde llegó el peón)
        """
        self.promocion_en_proceso = True
        self.origen_promocion = origen
        self.casilla_promocion = destino
        
        # Obtener el color del peón para mostrar las opciones correctas
        pieza_promocion = self.modelo.tablero.getPieza(destino)
        color_promocion = pieza_promocion.color if pieza_promocion else 'blanco'
        
        # Limpiar selección visual pero mantener estado de promoción
        self.casilla_origen_seleccionada = None
        self.movimientos_validos_cache = []
        self.vista.casilla_origen = None
        self.vista.movimientos_validos = []
        self.vista.casillas_captura = []
        self.vista.casillas_enroque_disponible = []
        
        # Mostrar popup de promoción
        self.vista.mostrar_promocion_peon(color_promocion)
        
        logger.info(f"Iniciando promoción de peón {color_promocion} en {destino}")
    
    def manejar_promocion_seleccionada(self, tipo_pieza):
        """
        Maneja la selección de pieza para promoción.
        Recibe el tipo de pieza seleccionada y completa la promoción.
        
        Args:
            tipo_pieza: Tipo de pieza seleccionada ('reina', 'torre', 'alfil', 'caballo')
        """
        if not self.promocion_en_proceso:
            logger.warning("No hay promoción en proceso")
            return
            
        if tipo_pieza is None:
            logger.warning("No se ha seleccionado ninguna pieza para promoción")
            return
            
        # Completar la promoción en el modelo
        try:
            if hasattr(self.modelo, 'completar_promocion') and callable(self.modelo.completar_promocion):
                exito = self.modelo.completar_promocion(self.casilla_promocion, tipo_pieza)
                
                if exito:
                    logger.info(f"Promoción completada: {tipo_pieza} en {self.casilla_promocion}")
                    
                    # Limpiar estado de promoción
                    self._finalizar_promocion()
                    
                    # Cerrar popup y actualizar estado del juego
                    self.vista.cerrar_popup_promocion()
                    self._actualizar_estado_post_movimiento()
                else:
                    logger.error("Error al completar la promoción en el modelo")
            else:
                logger.error("El modelo no tiene el método 'completar_promocion'")
                
        except Exception as e:
            logger.error(f"Excepción al completar promoción: {e}")
    
    def _finalizar_promocion(self):
        """
        Limpia el estado de promoción del controlador.
        """
        self.promocion_en_proceso = False
        self.casilla_promocion = None
        self.origen_promocion = None
        logger.debug("Estado de promoción limpiado")

    def mostrar_popup_fin_juego(self, resultado, motivo=None):
        """
        Muestra el popup de fin de juego con el resultado correspondiente.
        
        Args:
            resultado: Tipo de resultado ('victoria_blanco', 'victoria_negro', 'tablas')
            motivo: Motivo específico del fin de juego ('jaque_mate', 'ahogado', etc.)
        """
        if not self.juego_terminado:
            self.juego_terminado = True
        
        logger.info(f"Fin del juego: {resultado} por {motivo}")
        self.vista.mostrar_fin_de_juego(resultado, motivo)
    
    def reiniciar_juego(self):
        """
        Reinicia el juego con la misma configuración.
        """
        logger.info("Reiniciando juego con la misma configuración")
        
        # Reiniciar estado del controlador
        self.casilla_origen_seleccionada = None
        self.movimientos_validos_cache = []
        self.juego_terminado = False
        
        # Limpiar estado de promoción
        self._finalizar_promocion()
        
        # Reiniciar modelo (tablero, estado de juego, etc.)
        exito_reinicio = False
        if hasattr(self.modelo, 'reiniciar') and callable(self.modelo.reiniciar):
            exito_reinicio = self.modelo.reiniciar()
        else:
            # Fallback si no existe el método reiniciar
            config = self.vista.obtener_configuracion()
            if hasattr(self.modelo, 'configurar_nueva_partida') and callable(self.modelo.configurar_nueva_partida):
                self.modelo.configurar_nueva_partida(config)
                exito_reinicio = True
            else:
                logger.warning("No se encontró método para reiniciar el modelo. Creando nuevo tablero.")
                self.modelo.tablero = Tablero()
                exito_reinicio = True
        
        # Actualizar la vista con los datos del modelo reiniciado
        if exito_reinicio:
            # Limpiar piezas capturadas en la vista (siguiendo patrón MVC)
            self.vista.jugadores['blanco']['piezas_capturadas'] = []
            self.vista.jugadores['negro']['piezas_capturadas'] = []
            
            # Si el modelo tiene datos de jugador/piezas capturadas, usarlos para actualizar la vista
            try:
                datos_display = self.modelo.obtener_datos_display()
                if 'blanco' in datos_display and 'capturadas' in datos_display['blanco']:
                    self.vista.jugadores['blanco']['piezas_capturadas'] = datos_display['blanco']['capturadas']
                if 'negro' in datos_display and 'capturadas' in datos_display['negro']:
                    self.vista.jugadores['negro']['piezas_capturadas'] = datos_display['negro']['capturadas']
                logger.debug("Piezas capturadas actualizadas en vista desde modelo después de reiniciar")
            except Exception as e:
                logger.error(f"Error al obtener datos de display después de reiniciar: {e}")
        
        # La vista ya habrá sido actualizada visualmente por el método _reiniciar_juego de InterfazAjedrez
    
    def volver_menu_principal(self):
        """
        Vuelve al menú principal/pantalla de configuración.
        También reinicia el estado del juego para que esté limpio para la próxima partida.
        """
        logger.info("Volviendo al menú principal")
        
        # Reiniciar estado del controlador
        self.casilla_origen_seleccionada = None
        self.movimientos_validos_cache = []
        self.juego_terminado = False
        
        # Limpiar estado de promoción
        self._finalizar_promocion()
        
        # Reiniciar el modelo para que esté limpio (igual que en reiniciar_juego)
        # Esto garantiza que no queden datos residuales cuando se inicie una nueva partida
        if hasattr(self.modelo, 'reiniciar') and callable(self.modelo.reiniciar):
            self.modelo.reiniciar()
        else:
            # Fallback si no existe el método reiniciar - crear un tablero nuevo
            self.modelo.tablero = Tablero()
            logger.warning("No se encontró método para reiniciar el modelo. Creando nuevo tablero.")
        
        # Limpiar datos en la vista que dependen del modelo
        self.vista.jugadores['blanco']['piezas_capturadas'] = []
        self.vista.jugadores['negro']['piezas_capturadas'] = []
        
        # No es necesario reiniciar el modelo aquí ya que se configurará
        # cuando el usuario seleccione nuevas opciones y presione "Jugar"
        
        # La vista ya habrá sido actualizada por _volver_menu_principal de InterfazAjedrez
    
    def iniciar(self):
        """
        Inicia el bucle principal del juego.
        """
        # Marcar que el controlador está ejecutándose
        self.running = True
        
        # Variable para controlar tiempo del próximo movimiento CPU
        self.tiempo_movimiento_cpu = None
        
        # Bucle principal del juego
        reloj = pygame.time.Clock()
        
        # Iniciar el bucle
        while self.running:
            # --- Procesar eventos de pygame ---
            if not self.vista.manejar_eventos():
                # Si manejar_eventos devuelve False, salir del bucle
                self.running = False
                break
                
            # --- Procesar lógica del juego ---
            tiempo_actual = pygame.time.get_ticks()
            
            # Verificar si es tiempo de realizar un movimiento de CPU
            if self.tiempo_movimiento_cpu and tiempo_actual >= self.tiempo_movimiento_cpu:
                # Resetear inmediatamente para evitar problemas de timing
                self.tiempo_movimiento_cpu = None
                
                movimiento_realizado = self.procesar_movimiento_cpu()
                
                # Si se realizó un movimiento, forzar actualización de vista
                if movimiento_realizado:
                    self.vista.actualizar(self.obtener_tablero())
            
            # --- Actualizar vista ---
            # Pasar el tablero a la vista para que lo dibuje
            self.vista.actualizar(self.obtener_tablero())
            
            # Limitar fps 
            reloj.tick(60)  # 60 FPS para mejor respuesta
        
        # Salir limpiamente
        pygame.quit()
        sys.exit()

    # --- Métodos para manejar las jugadas del CPU ---
    def procesar_movimiento_cpu(self):
        """
        Solicita y procesa un movimiento del jugador CPU actual si es su turno.
        Este método debe ser llamado periódicamente en el bucle principal cuando
        el turno corresponde a un jugador CPU.
        
        Returns:
            bool: True si un movimiento CPU fue procesado, False si no corresponde o hubo error.
        """
        if self.juego_terminado:
            return False
            
        # Obtener el jugador actual
        if not self.modelo.jugadores or len(self.modelo.jugadores) < 2:
            logger.error("No hay suficientes jugadores configurados para procesar movimiento CPU")
            return False
            
        jugador_actual = self.modelo.jugadores[self.modelo.jugador_actual_idx]
        turno_color = self.modelo.getTurnoColor()
        
        # Verificar que el jugador actual coincida con el turno actual
        if jugador_actual.get_color() != turno_color:
            # Try to find the correct player based on color
            for i, jugador in enumerate(self.modelo.jugadores):
                if jugador.get_color() == turno_color:
                    self.modelo.jugador_actual_idx = i
                    jugador_actual = jugador
                    break
        
        # Verificar si el jugador actual es una CPU
        if not isinstance(jugador_actual, JugadorCPU):
            # No es CPU, nada que hacer
            return False
            
        # Verificar que el color del jugador coincida con el turno actual
        if jugador_actual.get_color() != turno_color:
            logger.error(f"Error: Color del jugador CPU ({jugador_actual.get_color()}) "
                         f"no coincide con el turno actual ({turno_color})")
            return False
            
        logger.info(f"Solicitando movimiento a jugador CPU {jugador_actual.get_nombre()}")
        
        try:
            # Solicitar movimiento al jugador CPU
            origen, destino = jugador_actual.solicitarMovimiento(self.modelo)
            
            # Verificar si el movimiento es válido ((-1,-1),(-1,-1) indica error/fin de juego)
            if origen == (-1,-1) or destino == (-1,-1):
                logger.error(f"El jugador CPU {jugador_actual.get_nombre()} no pudo generar un movimiento válido")
                return False
                
            # Ejecutar el movimiento
            logger.info(f"Ejecutando movimiento CPU: {origen} -> {destino}")
            if hasattr(self.modelo, 'realizar_movimiento') and callable(self.modelo.realizar_movimiento):
                resultado = self.modelo.realizar_movimiento(origen, destino)
                
                # Actualizar el estado del juego después del movimiento
                self._actualizar_estado_post_movimiento()
                
                # IMPORTANTE: No programar aquí el próximo movimiento CPU,
                # ya que eso se hace en _actualizar_estado_post_movimiento
                # y podría interferir con el flujo normal del juego.
                
                return True
            else:
                logger.error("El modelo no tiene un método 'realizar_movimiento' válido")
                return False
                
        except Exception as e:
            logger.exception(f"Error al procesar movimiento CPU: {e}")
            return False
            
    def _manejar_fin_juego(self, estado):
        """
        Maneja el fin del juego, mostrando el mensaje apropiado según el estado.
        
        Args:
            estado: Estado del juego ('jaque_mate', 'tablas', 'ahogado', etc.)
        """
        color_perdedor = self.modelo.getTurnoColor()  # El color del jugador que no puede mover
        color_ganador = 'negro' if color_perdedor == 'blanco' else 'blanco'
        
        if estado == 'jaque_mate':
            mensaje = f"¡Jaque Mate! Ganan las {color_ganador}s."
            self.vista.mostrar_fin_de_juego(f"victoria_{color_ganador}", f"¡Jaque Mate! El rey {color_perdedor} no puede escapar.")
        elif estado == 'ahogado':
            mensaje = f"¡Tablas por ahogado! El rey {color_perdedor} no puede moverse pero no está en jaque."
            self.vista.mostrar_fin_de_juego('tablas', mensaje)
        elif estado == 'tablas':
            # Obtener el motivo de tablas (regla 50 movimientos, repetición, material insuficiente)
            motivo = self.modelo.getMotivoTablas() if hasattr(self.modelo, 'getMotivoTablas') else "Tablas"
            self.vista.mostrar_fin_de_juego('tablas', motivo)
        else:
            logger.warning(f"Estado de fin de juego desconocido: {estado}")
            self.vista.mostrar_fin_de_juego('tablas', f"Fin de partida: {estado}")
            
        # Asegurarse de que se detenga el temporizador
        self.vista.detener_temporizador()

    # ---------- MÉTODOS DE DESARROLLO (NO USAR EN PRODUCCIÓN) ----------
    def dev_forzar_fin_juego(self, resultado: str, motivo: str = None):
        """
        MÉTODO DE DESARROLLO - Fuerza el fin del juego para probar el popup de fin de juego.
        
        Args:
            resultado: Tipo de resultado ('victoria_blanco', 'victoria_negro', 'tablas')
            motivo: Motivo del fin de juego ('jaque_mate', 'ahogado', etc.)
        """
        logger.warning("⚠️ USANDO MÉTODO DE DESARROLLO PARA FORZAR FIN DE JUEGO")
        
        try:
            # Crear instancia de KillGame y forzar el fin
            killer = KillGame(self.modelo)
            killer.forzar_fin_juego(resultado, motivo)
            
            # Asegurarnos de que el modelo y la vista estén sincronizados
            self.modelo.estado = self.modelo.getEstadoJuego()
            
            # Actualizar la vista para mostrar el fin de juego
            self._actualizar_estado_post_movimiento()
            
            # Marcar el juego como terminado
            self.juego_terminado = True
        except Exception as e:
            logger.error(f"Error al forzar fin de juego: {e}", exc_info=True)
        
    def dev_test_victoria_blancas(self):
        """MÉTODO DE DESARROLLO - Simula victoria de las blancas por jaque mate"""
        self.dev_forzar_fin_juego('victoria_blanco', 'jaque_mate')
        
    def dev_test_victoria_negras(self):
        """MÉTODO DE DESARROLLO - Simula victoria de las negras por jaque mate"""
        self.dev_forzar_fin_juego('victoria_negro', 'jaque_mate')
        
    def dev_test_tablas_ahogado(self):
        """MÉTODO DE DESARROLLO - Simula tablas por ahogado"""
        self.dev_forzar_fin_juego('tablas', 'ahogado')
        
    def dev_test_tablas_insuficiente(self):
        """MÉTODO DE DESARROLLO - Simula tablas por material insuficiente"""
        self.dev_forzar_fin_juego('tablas', 'material_insuficiente')
        
    def dev_test_tablas_repeticion(self):
        """MÉTODO DE DESARROLLO - Simula tablas por triple repetición"""
        self.dev_forzar_fin_juego('tablas', 'repeticion')
        
    def dev_test_tablas_50_movimientos(self):
        """MÉTODO DE DESARROLLO - Simula tablas por regla de 50 movimientos"""
        self.dev_forzar_fin_juego('tablas', 'regla_50_movimientos')
    # ------------------------------------------------------------------

# Código para ejecutar el juego si este script es el principal
# (Útil para pruebas rápidas)
# if __name__ == '__main__':
#     try:
#         controlador = ControladorJuego()
#         controlador.iniciar()
#     except ImportError as e:
#         print(f"Error de importación: {e}")
#         print("Asegúrate de que las carpetas 'model' y 'view' están accesibles y que estás ejecutando desde el directorio raíz o que el PYTHONPATH está configurado.")
#     except Exception as e:
#         print(f"Ocurrió un error inesperado: {e}")
#         pygame.quit() # Asegurarse de cerrar pygame en caso de error 