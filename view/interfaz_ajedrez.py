"""
Se encarga de la presentación de la interfaz gráfica de usuario (dibujar el tablero, piezas, etc.).
"""
import pygame
import pygame.font
from typing import Dict, List, Tuple, Optional, Literal, Union, Callable
import os
import math
import time # Añadir import para time

class InterfazAjedrez:
    """
    Clase que maneja la interfaz gráfica del juego de ajedrez.
    Implementa dos vistas principales: configuración inicial y tablero de juego.
    """

    # Constantes de colores
    COLORES = {
        'blanco': (255, 255, 255),
        'negro': (0, 0, 0),
        'gris_oscuro': (45, 45, 45),
        'gris_medio': (90, 90, 90),
        'gris_claro': (200, 200, 200),
        'casilla_clara': (220, 220, 220),
        'casilla_oscura': (150, 150, 150),
        'seleccion': (100, 180, 100, 128),  # Verde semi-transparente
        'movimiento_valido': (100, 100, 180, 128),  # Azul semi-transparente
        'fondo': (240, 240, 240),
        'borde_tablero': (30, 30, 30),
        'panel_lateral': (200, 200, 200),
    }

    # Constantes de dimensiones
    DIMENSIONES = {
        'ventana': (1000, 700),
        'tablero': 560,  # Reducido de 600 a 560
        'casilla': 70,  # Calculado como 560 / 8
        'panel_lateral': 200,  # Ancho de los paneles laterales
        'boton': (150, 50),  # Tamaño de botones
        'dropdown': (250, 50),  # Tamaño de menús desplegables
    }

    def __init__(self, controlador):
        """
        Inicializa la interfaz gráfica del juego.
        
        Args:
            controlador: Instancia del controlador del juego para manejar las acciones del usuario.
        """
        # Inicializar pygame
        pygame.init()
        pygame.font.init()
        
        # Referencia al controlador
        self.controlador = controlador
        
        # Configurar ventana
        self.ventana = pygame.display.set_mode(self.DIMENSIONES['ventana'])
        pygame.display.set_caption("TU AJEDREZ")
        
        # Cargar fuentes (Intentar San Francisco, con Arial como fallback)
        # Nota: La disponibilidad real de 'SF Pro' puede depender de la instalación de Pygame/SDL
        fuente_principal = 'SF Pro, Arial' 
        self.fuente_titulo = pygame.font.SysFont(fuente_principal, 48, italic=False, bold=True)
        self.fuente_subtitulo = pygame.font.SysFont(fuente_principal, 24, bold=False, italic=False)
        self.fuente_normal = pygame.font.SysFont(fuente_principal, 20, bold=False, italic=False)
        self.fuente_pequeña = pygame.font.SysFont(fuente_principal, 16, bold=False, italic=False)
        
        # Variables de estado
        self.vista_actual = 'configuracion'  # 'configuracion' o 'tablero'
        self.turno_actual = 'blanco' # Añadir estado para saber el turno a mostrar
        self.pieza_seleccionada = None
        self.mensaje_estado = None # Para mostrar mensajes como Jaque, Mate, etc.
        self.casilla_origen = None
        self.movimientos_validos = []
        
        # Estado de los menús desplegables
        self.dropdown_tipo_juego = {
            'abierto': False,
            'opciones': ['Clásico (90 minutos + 30 segundos/movimiento)', 'Rápido (25 minutos + 10 segundos/movimiento)', 'Blitz (3 minutos + 2 segundos/movimiento o 5 minutos en total)'],
            'seleccionado': 'Escoge el tipo de juego',
        }
        
        self.dropdown_modalidad = {
            'abierto': False,
            'opciones': ['Humano vs Humano', 'Humano vs CPU', 'CPU vs CPU'],
            'seleccionado': 'Escoge la modalidad',
        }
        
        # Elementos de UI
        self.elementos_ui = {}
        self._inicializar_ui()
        
        # Información de jugadores y temporizador
        self.jugadores = {
            'blanco': {'nombre': 'Jugador 1', 'tiempo': '00:00', 'piezas_capturadas': []},
            'negro': {'nombre': 'Jugador 2', 'tiempo': '00:00', 'piezas_capturadas': []},
        }
        self.tiempo_acumulado = {'blanco': 0, 'negro': 0} # Tiempo en milisegundos
        self.tiempo_inicio_turno = None # Momento (ticks) en que empezó el turno actual
        self.temporizador_activo = False
        
        # Inicializar recursos gráficos (piezas)
        self.imagenes_piezas = self._cargar_imagenes_piezas()
    
    def _inicializar_ui(self):
        """
        Inicializa los elementos de la interfaz de usuario.
        """
        # Definir posiciones y dimensiones de los elementos UI
        centro_x = self.DIMENSIONES['ventana'][0] // 2
        
        # Posiciones para la vista de configuración (Ajustadas para mejor espaciado)
        y_inicial = 150 # Empezar un poco más abajo
        espacio_grande = 80 # Aumentado de 60 a 80 para más padding
        espacio_medio = 60
        espacio_pequeño = 25 # Espacio entre etiqueta y su dropdown
        espacio_dropdown = 80 # Espacio entre los dos dropdowns completos (label+box)
        
        icono_y = y_inicial
        titulo_y = icono_y + espacio_grande
        subtitulo_y = titulo_y + espacio_medio
        
        tipo_juego_label_y = subtitulo_y + espacio_medio
        tipo_juego_y = tipo_juego_label_y + espacio_pequeño + self.DIMENSIONES['dropdown'][1] // 2 # Centrar dropdown respecto a su Y
        
        modalidad_label_y = tipo_juego_y + self.DIMENSIONES['dropdown'][1] // 2 + espacio_medio
        modalidad_y = modalidad_label_y + espacio_pequeño + self.DIMENSIONES['dropdown'][1] // 2
        
        boton_jugar_y = modalidad_y + self.DIMENSIONES['dropdown'][1] // 2 + espacio_grande
        
        self.elementos_ui['config'] = {
            'icono_pos': (centro_x, icono_y),
            'titulo_pos': (centro_x, titulo_y),
            'subtitulo_pos': (centro_x, subtitulo_y),
            'tipo_juego_label_pos': (centro_x, tipo_juego_label_y),
            'tipo_juego_pos': (centro_x, tipo_juego_y),
            'modalidad_label_pos': (centro_x, modalidad_label_y),
            'modalidad_pos': (centro_x, modalidad_y),
            'boton_jugar_pos': (centro_x, boton_jugar_y),
        }
        
        # Posiciones para la vista del tablero (Ajustadas)
        self.elementos_ui['tablero'] = {
            'tablero_pos': (500, 400),  # Bajado de 370 a 400 para más espacio arriba
            'panel_izq_pos': (0, 0),
            'panel_der_pos': (800, 0),
            'reloj_pos': (500, 40),   # Subido de 50 a 40
        }
    
    def _cargar_imagenes_piezas(self) -> Dict[str, Dict[str, Optional[pygame.Surface]]]:
        """
        Carga las imágenes de las piezas desde la carpeta 'assets/imagenes_piezas'.
        Escala las imágenes para que encajen en las casillas.
        
        Returns:
            Diccionario con las imágenes de las piezas cargadas y escaladas por color y tipo.
            Devuelve None para una pieza si la imagen no se encuentra o no se puede cargar.
        """
        piezas = {'blanco': {}, 'negro': {}}
        # Usar el tamaño de casilla actualizado para calcular el tamaño de pieza
        tamaño_pieza = self.DIMENSIONES['casilla'] - 10 # Ahora 70 - 10 = 60
        ruta_base = os.path.join('assets', 'imagenes_piezas')

        # Mapeo de nombres internos a nombres de archivo (ajustar si es necesario)
        nombres_piezas_archivos = {
            'torre': 'Torre',
            'caballo': 'Caballo',
            'alfil': 'Alfil',
            'reina': 'Reina',  # 'reina' se usa internamente en _dibujar_pieza
            'rey': 'Rey',
            'peon': 'Peon'
        }
        colores_archivos = {'blanco': 'blanco', 'negro': 'negro'}

        print(f"Intentando cargar imágenes desde: {os.path.abspath(ruta_base)}")

        for color_key, color_nombre in colores_archivos.items():
            for tipo_key, tipo_nombre_archivo in nombres_piezas_archivos.items():
                nombre_archivo = f"{tipo_nombre_archivo} {color_nombre}.png"
                ruta_completa = os.path.join(ruta_base, nombre_archivo)
                
                try:
                    # Cargar la imagen
                    imagen = pygame.image.load(ruta_completa).convert_alpha()
                    
                    # Escalar la imagen
                    imagen_escalada = pygame.transform.smoothscale(imagen, (tamaño_pieza, tamaño_pieza))
                    
                    piezas[color_key][tipo_key] = imagen_escalada
                    # print(f"[Éxito] Imagen cargada y escalada: {ruta_completa}") # Descomentar para depuración detallada
                except pygame.error as e:
                    print(f"[Error] No se pudo cargar la imagen '{ruta_completa}': {e}")
                    piezas[color_key][tipo_key] = None # Marcar como no cargada
                    # Podríamos añadir un fallback a dibujo vectorial aquí si quisiéramos
                except FileNotFoundError:
                    print(f"[Error] Archivo no encontrado: '{ruta_completa}'")
                    piezas[color_key][tipo_key] = None

        if not any(img for imgs in piezas.values() for img in imgs.values()):
             print("[Advertencia] No se cargó ninguna imagen de pieza. ¿Es correcta la ruta 'assets/imagenes_piezas'?")
        elif None in [img for imgs in piezas.values() for img in imgs.values()]:
             print("[Advertencia] Faltan algunas imágenes de piezas o no se pudieron cargar.")
        else:
             print("[Info] Todas las imágenes de piezas cargadas correctamente.")

        return piezas
    
    def _render_text_with_spacing(self, text: str, font: pygame.font.Font, color: Tuple[int, int, int], spacing: int) -> Tuple[pygame.Surface, pygame.Rect]:
        """
        Renderiza texto aplicando un espaciado adicional entre caracteres.

        Args:
            text: El texto a renderizar.
            font: La fuente de pygame a usar.
            color: El color del texto.
            spacing: Píxeles de espaciado adicional entre cada letra.

        Returns:
            Una tupla con la superficie renderizada y su rectángulo.
        """
        if not text:
            surf = pygame.Surface((0, 0), pygame.SRCALPHA)
            return surf, surf.get_rect()
            
        char_surfaces = []
        total_width = 0
        max_height = 0

        # 1. Renderizar cada caracter y calcular dimensiones totales
        for i, char in enumerate(text):
            char_surf = font.render(char, True, color)
            char_surfaces.append(char_surf)
            total_width += char_surf.get_width()
            if i < len(text) - 1: # Añadir espaciado excepto después del último caracter
                total_width += spacing
            max_height = max(max_height, char_surf.get_height())

        # 2. Crear la superficie final
        final_surf = pygame.Surface((total_width, max_height), pygame.SRCALPHA)

        # 3. Blitear cada caracter en la superficie final
        current_x = 0
        for i, char_surf in enumerate(char_surfaces):
            final_surf.blit(char_surf, (current_x, 0))
            current_x += char_surf.get_width()
            if i < len(text) - 1:
                current_x += spacing
                
        return final_surf, final_surf.get_rect()

    def dibujar_pantalla_configuracion(self):
        """
        Dibuja la pantalla de configuración inicial, gestionando el orden de dibujado
        para que los menús desplegables abiertos aparezcan encima.
        """
        # Limpiar pantalla
        self.ventana.fill(self.COLORES['fondo'])
        
        # --- 1. Dibujar elementos de fondo y estáticos ---
        # Icono
        icono_rey_img = self.imagenes_piezas.get('negro', {}).get('rey')
        if icono_rey_img:
            icono_surf = pygame.transform.smoothscale(icono_rey_img, (60, 60))
        else:
            icono_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
            pygame.draw.rect(icono_surf, self.COLORES['negro'], (15, 10, 30, 40), 2)
            pygame.draw.rect(icono_surf, self.COLORES['negro'], (10, 5, 40, 10), 2) 
        icono_rect = icono_surf.get_rect(center=self.elementos_ui['config']['icono_pos'])
        self.ventana.blit(icono_surf, icono_rect)
        
        # Título (con espaciado)
        title_surf, title_rect = self._render_text_with_spacing("TU AJEDREZ", self.fuente_titulo, self.COLORES['negro'], 5) # 5px de espaciado
        title_rect.center = self.elementos_ui['config']['titulo_pos']
        self.ventana.blit(title_surf, title_rect)
        
        # Subtítulo
        texto_subtitulo = self.fuente_subtitulo.render("Configura tu modo favorito y empieza a jugar", True, self.COLORES['gris_medio'])
        rect_subtitulo = texto_subtitulo.get_rect(center=self.elementos_ui['config']['subtitulo_pos'])
        self.ventana.blit(texto_subtitulo, rect_subtitulo)
        
        # Etiquetas para los menús desplegables
        tipo_juego_label = self.fuente_normal.render("Tipo de juego", True, self.COLORES['negro'])
        rect_tipo_juego_label = tipo_juego_label.get_rect(center=self.elementos_ui['config']['tipo_juego_label_pos'])
        self.ventana.blit(tipo_juego_label, rect_tipo_juego_label)
        
        modalidad_label = self.fuente_normal.render("Modalidad", True, self.COLORES['negro'])
        rect_modalidad_label = modalidad_label.get_rect(center=self.elementos_ui['config']['modalidad_label_pos'])
        self.ventana.blit(modalidad_label, rect_modalidad_label)
        
        # --- 2. Determinar qué dropdown está abierto --- 
        dropdown_abierto = None
        if self.dropdown_tipo_juego['abierto']:
            dropdown_abierto = 'tipo_juego'
        elif self.dropdown_modalidad['abierto']:
            dropdown_abierto = 'modalidad'
            
        # --- 3. Dibujar dropdowns cerrados y botón --- 
        # Dibujar el dropdown de tipo de juego si está cerrado o si ningún dropdown está abierto
        if dropdown_abierto != 'tipo_juego':
             self._dibujar_dropdown('tipo_juego', self.elementos_ui['config']['tipo_juego_pos'])
             
        # Dibujar el dropdown de modalidad si está cerrado o si ningún dropdown está abierto
        if dropdown_abierto != 'modalidad':
             self._dibujar_dropdown('modalidad', self.elementos_ui['config']['modalidad_pos'])
             
        # Dibujar botón Jugar (se dibuja antes del dropdown abierto)
        self._dibujar_boton("Jugar", self.elementos_ui['config']['boton_jugar_pos'], 
                          accion=self.controlador.solicitar_inicio_juego)

        # --- 4. Dibujar el dropdown abierto (si existe) al final --- 
        if dropdown_abierto:
            self._dibujar_dropdown(dropdown_abierto, self.elementos_ui['config'][f'{dropdown_abierto}_pos'])
    
    def _dibujar_dropdown(self, nombre, posicion):
        """
        Dibuja un menú desplegable.
        
        Args:
            nombre: Nombre del menú desplegable ('tipo_juego' o 'modalidad').
            posicion: Posición central del menú desplegable.
        """
        dropdown = getattr(self, f'dropdown_{nombre}')
        ancho, alto = self.DIMENSIONES['dropdown']
        opciones = dropdown['opciones']
        
        # Posición de la esquina superior izquierda del cuadro principal
        x = posicion[0] - ancho // 2
        y = posicion[1] - alto // 2
        
        # Determinar el rectángulo a dibujar (cerrado o abierto)
        rect_principal = pygame.Rect(x, y, ancho, alto)
        altura_total_abierto = alto * (len(opciones) + 1)
        rect_abierto = pygame.Rect(x, y, ancho, altura_total_abierto)
        
        # Dibujar el fondo (blanco) y borde (gris)
        if dropdown['abierto']:
            pygame.draw.rect(self.ventana, self.COLORES['blanco'], rect_abierto)
            pygame.draw.rect(self.ventana, self.COLORES['gris_medio'], rect_abierto, 1)
        else:
            pygame.draw.rect(self.ventana, self.COLORES['blanco'], rect_principal)
            pygame.draw.rect(self.ventana, self.COLORES['gris_medio'], rect_principal, 1)
        
        # Dibujar texto de la selección actual
        texto_seleccion = self.fuente_normal.render(dropdown['seleccionado'], True, self.COLORES['gris_oscuro'])
        self.ventana.blit(texto_seleccion, (x + 10, y + alto // 2 - texto_seleccion.get_height() // 2))
        
        # Dibujar flecha del menú
        flecha_puntos = [
            (x + ancho - 20, y + alto // 2 - 3),
            (x + ancho - 10, y + alto // 2 - 3),
            (x + ancho - 15, y + alto // 2 + 3)
        ]
        pygame.draw.polygon(self.ventana, self.COLORES['gris_oscuro'], flecha_puntos)
        
        # Si el menú está abierto, dibujar las opciones y las líneas separadoras
        if dropdown['abierto']:
            y_opcion_base = y + alto
            for i, opcion in enumerate(opciones):
                y_opcion_actual = y_opcion_base + i * alto
                # Dibujar línea separadora encima de cada opción (excepto la primera)
                pygame.draw.line(self.ventana, self.COLORES['gris_claro'], (x + 1, y_opcion_actual), (x + ancho - 1, y_opcion_actual), 1)
                
                # Dibujar texto de la opción
                texto_opcion = self.fuente_normal.render(opcion, True, self.COLORES['gris_oscuro'])
                # Añadir un pequeño margen
                self.ventana.blit(texto_opcion, (x + 10, y_opcion_actual + alto // 2 - texto_opcion.get_height() // 2))
                
                # Almacenar rectángulos de opciones para detección de clics (opcional, ya se hace en _verificar_clic_dropdown)
                # rect_opcion = pygame.Rect(x, y_opcion_actual, ancho, alto)
                # Almacenar rect para detección de hover si se quisiera implementar resaltado
    
    def _dibujar_boton(self, texto, posicion, accion=None, ancho_alto=None):
        """
        Dibuja un botón en la pantalla.
        
        Args:
            texto: Texto a mostrar en el botón.
            posicion: Posición central del botón.
            accion: Función a ejecutar cuando se presiona el botón.
            ancho_alto: Tupla (ancho, alto) o None para usar el valor por defecto.
        """
        if ancho_alto is None:
            ancho, alto = self.DIMENSIONES['boton']
        else:
            ancho, alto = ancho_alto
            
        x = posicion[0] - ancho // 2
        y = posicion[1] - alto // 2
        
        # Dibujar rectángulo del botón
        pygame.draw.rect(self.ventana, self.COLORES['gris_oscuro'], (x, y, ancho, alto))
        
        # Dibujar texto del botón
        texto_renderizado = self.fuente_normal.render(texto, True, self.COLORES['blanco'])
        self.ventana.blit(texto_renderizado, (x + ancho // 2 - texto_renderizado.get_width() // 2,
                                            y + alto // 2 - texto_renderizado.get_height() // 2))
        
        # Almacenar el rectángulo y la acción para detectar clics
        rect = pygame.Rect(x, y, ancho, alto)
        if 'botones' not in self.elementos_ui:
            self.elementos_ui['botones'] = {}
        self.elementos_ui['botones'][texto] = {'rect': rect, 'accion': accion}
    
    def dibujar_pantalla_tablero(self, tablero):
        """
        Dibuja la pantalla del tablero de ajedrez.
        
        Args:
            tablero: Instancia del tablero con el estado actual del juego.
        """
        # Limpiar pantalla
        self.ventana.fill(self.COLORES['fondo'])
        
        # Dibujar paneles laterales
        self._dibujar_panel_lateral(0, self.jugadores['blanco'])  # Panel izquierdo
        self._dibujar_panel_lateral(self.DIMENSIONES['ventana'][0] - self.DIMENSIONES['panel_lateral'], 
                                   self.jugadores['negro'])  # Panel derecho
        
        # Dibujar Indicador de Turno (debajo del reloj)
        self._dibujar_indicador_turno()
        
        # Dibujar Mensaje de Estado (si existe)
        self._dibujar_mensaje_estado()
        
        # Dibujar reloj
        self._dibujar_reloj()
        
        # Dibujar tablero
        self._dibujar_tablero(tablero)
    
    def _dibujar_panel_lateral(self, x, jugador):
        """
        Dibuja un panel lateral con información del jugador.
        
        Args:
            x: Posición x del borde izquierdo del panel.
            jugador: Diccionario con información del jugador.
        """
        # Rectángulo del panel
        panel_rect = pygame.Rect(x, 0, self.DIMENSIONES['panel_lateral'], self.DIMENSIONES['ventana'][1])
        pygame.draw.rect(self.ventana, self.COLORES['panel_lateral'], panel_rect)
        
        # Nombre del jugador
        texto_nombre = self.fuente_normal.render(jugador['nombre'], True, self.COLORES['gris_oscuro'])
        self.ventana.blit(texto_nombre, (x + 10, 50))
        
        # --- Dibujar Piezas Capturadas ---
        y_capturas = 90 # Posición Y inicial para las capturas
        x_capturas_start = x + 10
        max_ancho_panel = self.DIMENSIONES['panel_lateral'] - 20 # Margen
        tamaño_captura = 20 # Tamaño pequeño para los iconos
        espacio_captura = 5 # Espacio entre iconos
        x_actual = x_capturas_start
        
        if 'piezas_capturadas' in jugador:
            # Ordenar por valor (opcional, pero común) - Requiere método getValor() en Pieza
            # piezas_ordenadas = sorted(jugador['piezas_capturadas'], key=lambda p: p.getValor(), reverse=True)
            piezas_ordenadas = jugador['piezas_capturadas'] # Sin ordenar por ahora
            
            for pieza in piezas_ordenadas:
                tipo = type(pieza).__name__.lower()
                color_pieza = pieza.get_color()
                imagen_orig = self.imagenes_piezas.get(color_pieza, {}).get(tipo)
                
                if imagen_orig:
                    imagen_captura = pygame.transform.smoothscale(imagen_orig, (tamaño_captura, tamaño_captura))
                    # Comprobar si cabe en la línea actual
                    if x_actual + tamaño_captura > x + max_ancho_panel:
                         # Pasar a la siguiente línea
                         x_actual = x_capturas_start
                         y_capturas += tamaño_captura + espacio_captura
                         
                    self.ventana.blit(imagen_captura, (x_actual, y_capturas))
                    x_actual += tamaño_captura + espacio_captura
                else:
                    logger.warning(f"No se encontró imagen para pieza capturada: {tipo} {color_pieza}")
                    # Dibujar un placeholder? 
                    # pygame.draw.rect(self.ventana, (100,100,100), (x_actual, y_capturas, tamaño_captura, tamaño_captura), 1)
                    # x_actual += tamaño_captura + espacio_captura
    
    def _dibujar_indicador_turno(self):
        """ Dibuja un texto indicando de quién es el turno. """
        texto = f"Turno de: {self.turno_actual.capitalize()}"
        color_texto = self.COLORES['gris_oscuro']
        fuente_turno = self.fuente_normal
        
        texto_surf = fuente_turno.render(texto, True, color_texto)
        
        # Posicionar debajo del reloj
        reloj_centro_x, reloj_centro_y = self.elementos_ui['tablero']['reloj_pos']
        # Asumimos altura del reloj (aproximada por fuente + padding)
        altura_reloj_aprox = fuente_turno.get_height() + 20 
        pos_y = reloj_centro_y + altura_reloj_aprox // 2 + 15 # Espacio debajo del reloj
        pos_x = reloj_centro_x
        
        texto_rect = texto_surf.get_rect(center=(pos_x, pos_y))
        self.ventana.blit(texto_surf, texto_rect)

    def _dibujar_mensaje_estado(self):
        """ Dibuja el mensaje de estado actual si existe. """
        if self.mensaje_estado:
            color_texto = self.COLORES['negro'] 
            # Podríamos usar un color diferente para jaque vs mate/tablas
            # if "Mate" in self.mensaje_estado or "Tablas" in self.mensaje_estado:
            #     color_texto = (200, 0, 0) # Rojo oscuro
            # elif "Jaque" in self.mensaje_estado:
            #     color_texto = (200, 100, 0) # Naranja oscuro
                
            fuente_mensaje = self.fuente_subtitulo # Usar fuente más grande
            
            texto_surf = fuente_mensaje.render(self.mensaje_estado, True, color_texto)
            
            # Posicionar en la parte superior central, encima del reloj/turno
            centro_x = self.DIMENSIONES['ventana'][0] // 2
            pos_y = 25 # Más arriba
            
            texto_rect = texto_surf.get_rect(center=(centro_x, pos_y))
            
            # Fondo semi-transparente opcional para legibilidad
            fondo_rect = texto_rect.inflate(20, 10) # Añadir padding
            fondo_surf = pygame.Surface(fondo_rect.size, pygame.SRCALPHA)
            fondo_surf.fill((220, 220, 220, 180)) # Gris claro semi-transparente
            self.ventana.blit(fondo_surf, fondo_rect)
            
            # Dibujar texto encima del fondo
            self.ventana.blit(texto_surf, texto_rect)

    def _dibujar_reloj(self):
        """
        Dibuja el reloj/temporizador en la parte superior con fondo gris claro.
        Ahora usa los tiempos del diccionario self.jugadores (actualizados en 'actualizar').
        """
        # Obtener tiempo del jugador cuyo turno es (ya formateados)
        tiempo_blanco = self.jugadores['blanco'].get('tiempo', '00:00')
        tiempo_negro = self.jugadores['negro'].get('tiempo', '00:00')
        
        # Mostrar ambos tiempos
        texto_tiempo = f"B: {tiempo_blanco} | N: {tiempo_negro}"
        
        color_texto = self.COLORES['gris_oscuro']
        color_fondo = self.COLORES['gris_claro']
        fuente_reloj = self.fuente_normal # Usar fuente más pequeña
        padding = 10 # Espacio entre el texto y el borde del fondo

        # Renderizar el texto para obtener su tamaño
        texto_surf = fuente_reloj.render(texto_tiempo, True, color_texto)
        texto_rect = texto_surf.get_rect()

        # Calcular tamaño y posición del rectángulo de fondo
        fondo_ancho = texto_rect.width + 2 * padding
        fondo_alto = texto_rect.height + 2 * padding
        pos_centro = self.elementos_ui['tablero']['reloj_pos']
        fondo_rect = pygame.Rect(0, 0, fondo_ancho, fondo_alto)
        fondo_rect.center = pos_centro

        # Dibujar el rectángulo de fondo 
        pygame.draw.rect(self.ventana, color_fondo, fondo_rect)

        # Centrar el texto dentro del rectángulo de fondo
        texto_rect.center = fondo_rect.center
        self.ventana.blit(texto_surf, texto_rect)
    
    def _dibujar_tablero(self, tablero):
        """
        Dibuja el tablero de ajedrez con sus piezas.
        
        Args:
            tablero: Instancia del tablero con el estado actual del juego.
        """
        # Posición central del tablero
        centro_x, centro_y = self.elementos_ui['tablero']['tablero_pos']
        tamaño_tablero = self.DIMENSIONES['tablero']
        tamaño_casilla = self.DIMENSIONES['casilla']
        
        # Esquina superior izquierda del tablero
        x0 = centro_x - tamaño_tablero // 2
        y0 = centro_y - tamaño_tablero // 2
        
        # Dibujar borde del tablero
        borde = 10  # Ancho del borde
        pygame.draw.rect(self.ventana, self.COLORES['borde_tablero'], 
                        (x0 - borde, y0 - borde, 
                        tamaño_tablero + 2*borde, tamaño_tablero + 2*borde))
        
        # Dibujar casillas
        for fila in range(8):
            for columna in range(8):
                x = x0 + columna * tamaño_casilla
                y = y0 + (7 - fila) * tamaño_casilla  # Invertir filas para que 0,0 sea abajo a la izquierda
                
                # Alternar colores
                if (fila + columna) % 2 == 0:
                    color = self.COLORES['casilla_clara']
                else:
                    color = self.COLORES['casilla_oscura']
                
                # Dibujar casilla
                pygame.draw.rect(self.ventana, color, (x, y, tamaño_casilla, tamaño_casilla))
                
                # Resaltar casilla seleccionada
                if self.casilla_origen == (fila, columna):
                    pygame.draw.rect(self.ventana, self.COLORES['seleccion'], 
                                    (x, y, tamaño_casilla, tamaño_casilla))
                
                # Resaltar movimientos válidos
                if (fila, columna) in self.movimientos_validos:
                    pygame.draw.rect(self.ventana, self.COLORES['movimiento_valido'], 
                                    (x, y, tamaño_casilla, tamaño_casilla))
                
                # Dibujar pieza si hay alguna
                pieza = tablero.getPieza((fila, columna))
                if pieza:
                    self._dibujar_pieza(pieza, x, y)
    
    def _dibujar_pieza(self, pieza, x, y):
        """
        Dibuja una pieza en la posición especificada.
        
        Args:
            pieza: Objeto pieza a dibujar.
            x: Posición x de la esquina superior izquierda de la casilla.
            y: Posición y de la esquina superior izquierda de la casilla.
        """
        tamaño_casilla = self.DIMENSIONES['casilla']
        
        # Obtener tipo y color de la pieza
        tipo = type(pieza).__name__.lower()
        color = pieza.color
        
        # Obtener imagen
        imagen = self.imagenes_piezas.get(color, {}).get(tipo)
        
        if imagen:
            # Centrar la imagen en la casilla
            rect = imagen.get_rect(center=(x + tamaño_casilla/2, y + tamaño_casilla/2))
            self.ventana.blit(imagen, rect)
    
    # --- Métodos para el Temporizador ---

    def iniciar_temporizador(self):
        """
        Inicia el temporizador del juego. Reinicia tiempos acumulados
        y registra el inicio del primer turno.
        """
        print("[Interfaz] Iniciando temporizador...") # Log
        self.tiempo_acumulado = {'blanco': 0, 'negro': 0}
        self.tiempo_inicio_turno = pygame.time.get_ticks()
        self.temporizador_activo = True
        self.turno_actual = 'blanco' # Asegurar que empieza blanco
        # Actualizar inmediatamente la pantalla para mostrar 00:00
        self._actualizar_display_tiempos()

    def detener_temporizador(self):
        """ Detiene el temporizador (por ejemplo, al final del juego). """
        print("[Interfaz] Deteniendo temporizador...") # Log
        # Acumular el último fragmento de tiempo del jugador actual
        if self.temporizador_activo and self.tiempo_inicio_turno is not None:
            tiempo_transcurrido = pygame.time.get_ticks() - self.tiempo_inicio_turno
            self.tiempo_acumulado[self.turno_actual] += tiempo_transcurrido
        self.temporizador_activo = False
        self.tiempo_inicio_turno = None # Indicar que no hay turno activo en el timer
        self._actualizar_display_tiempos() # Actualizar una última vez

    def cambiar_turno_temporizador(self, nuevo_turno: str):
        """
        Gestiona el cambio de turno en el temporizador.
        Acumula el tiempo del jugador anterior y reinicia el contador para el nuevo.

        Args:
            nuevo_turno: El color del jugador cuyo turno comienza ('blanco' o 'negro').
        """
        if not self.temporizador_activo or self.tiempo_inicio_turno is None:
            print("[Interfaz Warning] Se intentó cambiar turno sin temporizador activo.")
            # Aún así, actualizamos el turno visualmente
            self.turno_actual = nuevo_turno
            return

        # Calcular tiempo transcurrido en el turno que termina
        tiempo_transcurrido = pygame.time.get_ticks() - self.tiempo_inicio_turno
        
        # Acumular tiempo para el jugador que acaba de mover
        self.tiempo_acumulado[self.turno_actual] += tiempo_transcurrido
        print(f"[Interfaz] Tiempo acumulado {self.turno_actual}: {self.tiempo_acumulado[self.turno_actual]/1000:.2f}s") # Log
        
        # Actualizar al nuevo turno
        self.turno_actual = nuevo_turno
        
        # Registrar el inicio del nuevo turno
        self.tiempo_inicio_turno = pygame.time.get_ticks()
        
        # Actualizar la visualización inmediatamente
        self._actualizar_display_tiempos()

    def _formatear_tiempo(self, milisegundos: int) -> str:
        """ Convierte milisegundos a formato MM:SS. """
        if milisegundos < 0: milisegundos = 0 # Evitar tiempos negativos
        total_segundos = milisegundos // 1000
        minutos = total_segundos // 60
        segundos = total_segundos % 60
        return f"{minutos:02}:{segundos:02}"

    def _actualizar_display_tiempos(self):
        """
        Calcula los tiempos actuales (acumulado + transcurrido_turno_actual si aplica)
        y actualiza el diccionario self.jugadores para que _dibujar_reloj los use.
        """
        tiempo_actual_ms = pygame.time.get_ticks()
        
        for color in ['blanco', 'negro']:
            tiempo_total_ms = self.tiempo_acumulado[color]
            # Si es el turno del jugador actual y el timer está activo, añadir tiempo transcurrido
            if self.temporizador_activo and color == self.turno_actual and self.tiempo_inicio_turno is not None:
                 tiempo_transcurrido_turno = tiempo_actual_ms - self.tiempo_inicio_turno
                 tiempo_total_ms += tiempo_transcurrido_turno
                 
            self.jugadores[color]['tiempo'] = self._formatear_tiempo(tiempo_total_ms)

    # ----------------------------------
    
    def _iniciar_juego(self):
        """
        Cambia a la vista del tablero e inicia el juego.
        """
        self.vista_actual = 'tablero'
        self.iniciar_temporizador() # Iniciar el temporizador al cambiar a la vista tablero
        # Aquí se podría notificar al controlador para iniciar el juego (si no lo hizo ya)
    
    def manejar_eventos(self):
        """
        Maneja los eventos de entrada del usuario.
        
        Returns:
            bool: True si se debe continuar, False si se debe salir.
        """
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False
            
            # Eventos para la vista de configuración
            if self.vista_actual == 'configuracion':
                if evento.type == pygame.MOUSEBUTTONDOWN:
                    self._manejar_clic_configuracion(evento.pos)
            
            # Eventos para la vista del tablero
            elif self.vista_actual == 'tablero':
                if evento.type == pygame.MOUSEBUTTONDOWN:
                    self._manejar_clic_tablero(evento.pos)
                elif evento.type == pygame.MOUSEMOTION and self.pieza_seleccionada:
                    # Manejar arrastre de piezas (implementar si se desea)
                    pass
                elif evento.type == pygame.MOUSEBUTTONUP and self.pieza_seleccionada:
                    # Soltar pieza (implementar si se desea)
                    pass
        
        return True
    
    def _manejar_clic_configuracion(self, pos):
        """
        Maneja los clics en la vista de configuración, asegurando que los clics
        no atraviesen los menús desplegables abiertos.
        
        Args:
            pos: Posición (x, y) del clic.
        """
        dropdown_abierto_nombre = None
        dropdown_abierto_obj = None
        rect_dropdown_abierto_completo = None

        # 1. Verificar si un dropdown está abierto y obtener su rectángulo completo
        if self.dropdown_tipo_juego['abierto']:
            dropdown_abierto_nombre = 'tipo_juego'
            dropdown_abierto_obj = self.dropdown_tipo_juego
        elif self.dropdown_modalidad['abierto']:
            dropdown_abierto_nombre = 'modalidad'
            dropdown_abierto_obj = self.dropdown_modalidad

        if dropdown_abierto_nombre:
            # Calcular el rectángulo completo del dropdown abierto (cabecera + opciones)
            ancho, alto = self.DIMENSIONES['dropdown']
            centro_x, centro_y = self.elementos_ui['config'][f'{dropdown_abierto_nombre}_pos']
            x = centro_x - ancho // 2
            y = centro_y - alto // 2
            altura_total_abierto = alto * (len(dropdown_abierto_obj['opciones']) + 1)
            rect_dropdown_abierto_completo = pygame.Rect(x, y, ancho, altura_total_abierto)

            # 2. Procesar clic si un dropdown está abierto
            if rect_dropdown_abierto_completo.collidepoint(pos):
                # El clic está DENTRO del área del dropdown abierto
                # -> Procesar selección de opción o cierre por clic en cabecera
                self._verificar_clic_dropdown(dropdown_abierto_nombre, pos)
            else:
                # El clic está FUERA del área del dropdown abierto
                # -> Simplemente cerrar el dropdown abierto
                dropdown_abierto_obj['abierto'] = False
            return # El clic ha sido manejado (ya sea interactuando o cerrando)

        # 3. Si NINGÚN dropdown estaba abierto, procesar clics normalmente
        # Verificar clic en botones primero
        for nombre_boton, datos_boton in self.elementos_ui.get('botones', {}).items():
            if datos_boton['rect'].collidepoint(pos) and datos_boton['accion']:
                datos_boton['accion']()
                return # El clic ha sido manejado por el botón
        
        # Verificar clics en las cabeceras de los dropdowns (ambos están cerrados)
        self._verificar_clic_dropdown('tipo_juego', pos) 
        self._verificar_clic_dropdown('modalidad', pos) # Ahora es seguro verificar ambos
    
    def _verificar_clic_dropdown(self, nombre, pos):
        """
        Verifica si se hizo clic en un menú desplegable (cabecera u opción)
        y maneja el evento.
        
        Args:
            nombre: Nombre del menú ('tipo_juego' o 'modalidad').
            pos: Posición (x, y) del clic.
        """
        dropdown = getattr(self, f'dropdown_{nombre}')
        ancho, alto = self.DIMENSIONES['dropdown']
        centro_x, centro_y = self.elementos_ui['config'][f'{nombre}_pos']
        
        # Rectángulo de la cabecera del menú
        x = centro_x - ancho // 2
        y = centro_y - alto // 2
        rect_cabecera = pygame.Rect(x, y, ancho, alto)
        
        # Verificar clic en la cabecera
        if rect_cabecera.collidepoint(pos):
            # Alternar estado abierto/cerrado
            dropdown['abierto'] = not dropdown['abierto']
            # Si se acaba de abrir este, cerrar el otro
            if dropdown['abierto']:
                otro_nombre = 'modalidad' if nombre == 'tipo_juego' else 'tipo_juego'
                otro_dropdown = getattr(self, f'dropdown_{otro_nombre}')
                otro_dropdown['abierto'] = False
            return # Clic manejado
        
        # Si el menú está abierto, verificar clic en las opciones
        if dropdown['abierto']:
            y_opcion_base = y + alto
            for i, opcion in enumerate(dropdown['opciones']):
                rect_opcion = pygame.Rect(x, y_opcion_base + i * alto, ancho, alto)
                if rect_opcion.collidepoint(pos):
                    dropdown['seleccionado'] = opcion
                    dropdown['abierto'] = False # Cerrar al seleccionar
                    # Aquí podrías llamar a una función del controlador si la selección debe tener efecto inmediato
                    # self.controlador.actualizar_configuracion(nombre, opcion)
                    return # Clic manejado
            
            # Si el clic fue dentro del área abierta pero no en una opción ni en la cabecera,
            # podríamos decidir cerrarlo o no hacer nada. Por ahora, no hace nada si no 
            # colisiona con nada específico dentro del área abierta.

    
    def _manejar_clic_tablero(self, pos):
        """
        Maneja los clics en la vista de tablero.
        
        Args:
            pos: Posición (x, y) del clic.
        """
        # Posición central del tablero
        centro_x, centro_y = self.elementos_ui['tablero']['tablero_pos']
        tamaño_tablero = self.DIMENSIONES['tablero']
        tamaño_casilla = self.DIMENSIONES['casilla']
        
        # Esquina superior izquierda del tablero
        x0 = centro_x - tamaño_tablero // 2
        y0 = centro_y - tamaño_tablero // 2
        
        # Verificar si el clic fue dentro del tablero
        if (x0 <= pos[0] <= x0 + tamaño_tablero and 
            y0 <= pos[1] <= y0 + tamaño_tablero):
            
            # Calcular fila y columna
            columna = (pos[0] - x0) // tamaño_casilla
            fila = 7 - (pos[1] - y0) // tamaño_casilla  # Convertir coordenada y a fila del tablero
            
            # Notificar al controlador o seleccionar la pieza
            self.controlador.manejar_clic_casilla((fila, columna))
    
    def actualizar(self, tablero=None):
        """
        Actualiza la interfaz con el estado actual del juego.
        
        Args:
            tablero: Instancia del tablero con el estado actual del juego.
        """
        if self.vista_actual == 'configuracion':
            self.dibujar_pantalla_configuracion()
        elif self.vista_actual == 'tablero' and tablero:
            # Actualizar los strings de tiempo ANTES de dibujar
            self._actualizar_display_tiempos()
            self.dibujar_pantalla_tablero(tablero)
        
        pygame.display.flip()
    
    def cambiar_vista(self, vista):
        """
        Cambia la vista actual.
        
        Args:
            vista: String que indica la vista ('configuracion' o 'tablero').
        """
        if vista in ['configuracion', 'tablero']:
            self.vista_actual = vista
            if vista == 'tablero' and not self.temporizador_activo:
                 # Si cambiamos a tablero y el timer no estaba activo, iniciarlo.
                 # Esto es útil si el controlador cambia la vista externamente.
                 self.iniciar_temporizador()
            elif vista == 'configuracion' and self.temporizador_activo:
                 # Si volvemos a configuración, detener el timer.
                 self.detener_temporizador()
    
    def obtener_configuracion(self):
        """
        Obtiene la configuración seleccionada por el usuario.
        
        Returns:
            Dict: Diccionario con la configuración seleccionada.
        """
        return {
            'tipo_juego': self.dropdown_tipo_juego['seleccionado'],
            'modalidad': self.dropdown_modalidad['seleccionado']
        } 

    def mostrar_mensaje_estado(self, texto: Optional[str]):
        """
        Actualiza el mensaje de estado que se mostrará en la pantalla.
        Si texto es None, limpia el mensaje.
        """
        self.mensaje_estado = texto
        # Podríamos añadir lógica para que mensajes no persistentes desaparezcan
        # después de un tiempo, pero por ahora se mantienen hasta el siguiente cambio.
    
    def obtener_configuracion(self):
        """
        Obtiene la configuración seleccionada por el usuario.
        
        Returns:
            Dict: Diccionario con la configuración seleccionada.
        """
        return {
            'tipo_juego': self.dropdown_tipo_juego['seleccionado'],
            'modalidad': self.dropdown_modalidad['seleccionado']
        } 