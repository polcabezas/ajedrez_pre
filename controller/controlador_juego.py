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
from model.tablero import Tablero
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
        """
        config = self.vista.obtener_configuracion()
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

        # Limpiar la selección visual en la vista por si acaso
        self.vista.casilla_origen = None
        self.vista.movimientos_validos = []
        
        # Forzar una actualización inmediata para mostrar el tablero limpio
        # Pasamos el tablero recién inicializado/reseteado
        # self.vista.actualizar(self.obtener_tablero()) # El bucle principal se encargará

    def manejar_clic_casilla(self, casilla: Tuple[int, int]):
        """
        Gestiona la lógica principal cuando el usuario hace clic en una casilla del tablero.
        Incluye la selección de piezas y la ejecución de movimientos.

        Args:
            casilla: Tupla (fila, columna) de la casilla clickeada.
        """
        logger.debug("Controlador: Clic en casilla %s", casilla)
        if self.juego_terminado:
            logger.debug("Juego terminado, ignorando clic.")
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
                    for mov in movimientos:
                        # Comprobar si hay una pieza rival en la casilla destino
                        pieza_destino = tablero.getPieza(mov)
                        if pieza_destino is not None and pieza_destino.color != pieza.color:
                            # Es una captura
                            capturas.append(mov)
                        else:
                            # Es un movimiento normal
                            movimientos_sin_captura.append(mov)
                            
                    # Actualizar la vista para mostrar resaltados
                    self.vista.casilla_origen = casilla
                    self.vista.movimientos_validos = movimientos_sin_captura
                    self.vista.casillas_captura = capturas
                    
                    logger.debug("Pieza %s en %s seleccionada. Movimientos normales: %s, Capturas: %s", 
                                 pieza, casilla, movimientos_sin_captura, capturas)
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
                 try:
                     if hasattr(self.modelo, 'realizar_movimiento') and callable(self.modelo.realizar_movimiento):
                         # Idealmente, este método devuelve algo útil (True/False, estado, etc.)
                         resultado = self.modelo.realizar_movimiento(origen, casilla)
                         # Asumimos éxito si no hay excepción por ahora
                         # Podríamos necesitar ajustar esto según lo que devuelva tu método real
                         exito_movimiento = True 
                         logger.debug("Modelo realizó movimiento. Resultado: %s", resultado)
                     else:
                         logger.error("ERROR: El modelo Juego no tiene el método 'realizar_movimiento'")
                 except Exception as e:
                     logger.error("ERROR: Excepción al llamar a modelo.realizar_movimiento: %s", e)
                     # Podríamos querer no limpiar la selección si el movimiento falla en el modelo

                 if exito_movimiento:
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
         logger.debug("Selección limpiada.")

    def _actualizar_estado_post_movimiento(self):
        """
        Llamado después de que un movimiento se realiza con éxito en el modelo.
        Consulta el estado actualizado del juego (turno, jaque, mate, tablas) 
        y actualiza la vista si es necesario.
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
                self.mostrar_popup_fin_juego('tablas', 'material_insuficiente')
            elif estado_juego == 'ahogado':
                self.vista.mostrar_mensaje_estado("Ahogado. Tablas.")
                self.juego_terminado = True
                self.mostrar_popup_fin_juego('tablas', 'ahogado')
            else:
                self.vista.mostrar_mensaje_estado(None) # Limpiar mensaje si no hay estado especial
                
            # Actualizar tablero
            tablero_actual = self.obtener_tablero()
            self.vista.actualizar(tablero_actual)
            
        except Exception as e:
            logger.error(f"Excepción en _actualizar_estado_post_movimiento: {e}", exc_info=True)
            
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
        Maneja eventos y actualiza la vista hasta que el usuario cierre la aplicación.
        """
        self.running = True
        
        # Comentario: El bucle principal del juego.
        while self.running:
            # --- Usar logging en lugar de print --- 
            logger.debug("Inicio de iteración del bucle principal.")
            
            # Comentario: Procesa eventos de Pygame (input de usuario, cierre, etc.)
            # El método de la vista devuelve False si se detecta el evento QUIT.
            try:
                logger.debug("Llamando a vista.manejar_eventos()...")
                eventos_ok = self.vista.manejar_eventos() 
                logger.debug(f"vista.manejar_eventos() devolvió: {eventos_ok}")
                if not eventos_ok:
                    self.running = False
                    logger.info("manejador_eventos indicó salir.")
                    continue # Salir del bucle si manejar_eventos devuelve False
            except Exception as e:
                logger.error(f"Excepción en vista.manejar_eventos(): {e}")
                self.running = False # Salir en caso de error
                continue
                
            # Comentario: Actualiza y redibuja la pantalla. 
            # Le pasamos el tablero si estamos en la vista de tablero, None si no.
            tablero_actual = None
            if self.vista.vista_actual == 'tablero': 
                 tablero_actual = self.obtener_tablero() 
                 
            try:
                logger.debug("Llamando a vista.actualizar()...")
                self.vista.actualizar(tablero_actual)
                logger.debug("vista.actualizar() completado.")
            except Exception as e:
                logger.error(f"Excepción en vista.actualizar(): {e}")
                import traceback
                traceback.print_exc() # Imprimir traceback completo
                self.running = False # Salir en caso de error
                continue
            
            # Comentario: Pequeña pausa para evitar consumir 100% CPU.
            pygame.time.wait(30) # 30 ms de espera
            logger.debug("Fin de iteración del bucle principal.")
            # --- FIN Logging ---

        # Comentario: Finaliza Pygame cuando el bucle termina.
        pygame.quit()
        logger.info("Juego finalizado.") # Mantenido en INFO

    # ---------- MÉTODOS DE DESARROLLO (NO USAR EN PRODUCCIÓN) ----------
    def dev_forzar_fin_juego(self, resultado: str, motivo: str = None):
        """
        MÉTODO DE DESARROLLO - Fuerza el fin del juego para probar el popup de fin de juego.
        
        Args:
            resultado: Tipo de resultado ('victoria_blanco', 'victoria_negro', 'tablas')
            motivo: Motivo del fin de juego ('jaque_mate', 'ahogado', etc.)
        """
        logger.warning("⚠️ USANDO MÉTODO DE DESARROLLO PARA FORZAR FIN DE JUEGO")
        
        # Crear instancia de KillGame y forzar el fin
        killer = KillGame(self.modelo)
        killer.forzar_fin_juego(resultado, motivo)
        
        # Actualizar la vista para mostrar el fin de juego
        self._actualizar_estado_post_movimiento()
        
        # Marcar el juego como terminado
        self.juego_terminado = True
    
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