"""
Se encarga de la presentación de la interfaz gráfica de usuario (dibujar el tablero, piezas, etc.).
"""
import pygame
import pygame.font
from typing import Dict, List, Tuple, Optional, Literal, Union, Callable
import os
import math
import time # Añadir import para time
import logging

# Configuración del logger para este módulo
logger = logging.getLogger(__name__)

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
        'captura': (220, 80, 80, 128),  # Rojo semi-transparente para capturas
        'fondo': (240, 240, 240),
        'borde_tablero': (30, 30, 30),
        'panel_lateral': (200, 200, 200),
        'overlay': (0, 0, 0, 128),  # Negro semi-transparente para overlay
    }

    # Constantes de dimensiones
    DIMENSIONES = {
        'ventana': (1000, 700),
        'tablero': 560,  # Reducido de 600 a 560
        'casilla': 70,  # Calculado como 560 / 8
        'panel_lateral': 200,  # Ancho de los paneles laterales
        'boton': (100, 30),  # Tamaño de botones
        'dropdown': (450, 30),  # Tamaño de menús desplegables
        'popup': (400, 300),  # Tamaño del popup de fin de juego
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
        self.fuente_normal = pygame.font.SysFont(fuente_principal, 16, bold=False, italic=False)
        self.fuente_pequeña = pygame.font.SysFont(fuente_principal, 12, bold=False, italic=False)
        
        # Variables de estado
        self.vista_actual = 'configuracion'  # 'configuracion' o 'tablero'
        self.turno_actual = 'blanco' # Añadir estado para saber el turno a mostrar
        self.pieza_seleccionada = None
        self.mensaje_estado = None # Para mostrar mensajes como Jaque, Mate, etc.
        self.casilla_origen = None
        self.movimientos_validos = []
        self.casillas_captura = [] # Para guardar las casillas donde se puede capturar una pieza
        
        # Estado para el popup de fin de juego
        self.mostrar_popup_fin_juego = False
        self.mensaje_fin_juego = ""
        self.tipo_fin_juego = None  # Puede ser: 'victoria_blanco', 'victoria_negro', 'tablas'
        
        # Estado para el botón de desarrollo y su menú
        self.mostrar_menu_dev = False
        self.botones_desarrollo = {}
        
        # Estado de los menús desplegables
        self.dropdown_tipo_juego = {
            'abierto': False,
            'opciones': ['Clásico (90 minutos + 30 segundos/movimiento)', 'Rápido (25 minutos + 10 segundos/movimiento)', 'Blitz (3 minutos + 2 segundos/movimiento o 5 minutos en total)'],
            'seleccionado': 'Escoge el tipo de juego',
        }
        
        self.dropdown_modalidad = {
            'abierto': False,
            'opciones': ['Humano vs Humano', 'Humano vs CPU', 'CPU vs Humano', 'CPU vs CPU'],
            'seleccionado': 'Escoge la modalidad',
        }
        
        # Nuevo dropdown para el nivel de dificultad de la CPU
        self.dropdown_dificultad_cpu = {
            'abierto': False,
            'opciones': ['Nivel 1 (Principiante)', 'Nivel 3 (Intermedio)', 'Nivel 5 (Avanzado)', 'Nivel 10 (Experto)'],
            'seleccionado': 'Selecciona nivel de dificultad',
            'visible': False  # Solo visible cuando se selecciona una modalidad con CPU
        }

        # Mensaje de error para la pantalla de configuración
        self.mensaje_error_config = None
        self.tiempo_mostrar_error = None
        
        # Elementos de UI
        self.elementos_ui = {}
        self._inicializar_ui()
        
        # Información de jugadores y temporizador
        self.jugadores = {
            'blanco': {'nombre': 'Jugador 1', 'tiempo': '00:00', 'piezas_capturadas': [], 'color': 'blanco'},
            'negro': {'nombre': 'Jugador 2', 'tiempo': '00:00', 'piezas_capturadas': [], 'color': 'negro'},
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
        y_inicial = 120  # Reducido para empezar más arriba
        espacio_grande = 60  # Reducido de 80 a 60
        espacio_medio = 40   # Reducido de 60 a 40
        espacio_pequeño = 15  # Reducido de 25 a 15
        
        icono_y = y_inicial
        titulo_y = icono_y + espacio_grande
        subtitulo_y = titulo_y + espacio_medio
        
        tipo_juego_label_y = subtitulo_y + espacio_medio
        tipo_juego_y = tipo_juego_label_y + espacio_pequeño + self.DIMENSIONES['dropdown'][1] // 2
        
        modalidad_label_y = tipo_juego_y + self.DIMENSIONES['dropdown'][1] // 2 + espacio_medio
        modalidad_y = modalidad_label_y + espacio_pequeño + self.DIMENSIONES['dropdown'][1] // 2
        
        # Nueva posición para el dropdown de dificultad de CPU
        dificultad_cpu_label_y = modalidad_y + self.DIMENSIONES['dropdown'][1] // 2 + espacio_medio
        dificultad_cpu_y = dificultad_cpu_label_y + espacio_pequeño + self.DIMENSIONES['dropdown'][1] // 2
        
        # Ajustar posición del botón jugar para que esté debajo del nuevo dropdown
        boton_jugar_y = dificultad_cpu_y + self.DIMENSIONES['dropdown'][1] // 2 + espacio_medio
        
        self.elementos_ui['config'] = {
            'icono_pos': (centro_x, icono_y),
            'titulo_pos': (centro_x, titulo_y),
            'subtitulo_pos': (centro_x, subtitulo_y),
            'tipo_juego_label_pos': (centro_x, tipo_juego_label_y),
            'tipo_juego_pos': (centro_x, tipo_juego_y),
            'modalidad_label_pos': (centro_x, modalidad_label_y),
            'modalidad_pos': (centro_x, modalidad_y),
            'dificultad_cpu_label_pos': (centro_x, dificultad_cpu_label_y),
            'dificultad_cpu_pos': (centro_x, dificultad_cpu_y),
            'boton_jugar_pos': (centro_x, boton_jugar_y),
        }
        
        # Posiciones para la vista del tablero (Ajustadas)
        self.elementos_ui['tablero'] = {
            'tablero_pos': (500, 400),  # Bajado de 370 a 400 para más espacio arriba
            'panel_izq_pos': (0, 0),
            'panel_der_pos': (800, 0),
            'reloj_pos': (500, 75),   # Aumentado a 75 para acercar el reloj al tablero
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
        
        # Verificar si debemos mostrar el nivel de dificultad de CPU
        modalidad_seleccionada = self.dropdown_modalidad['seleccionado']
        modalidad_tiene_cpu = any(cpu in modalidad_seleccionada for cpu in ["CPU vs", "vs CPU"])
        
        # Actualizar visibilidad del dropdown de dificultad CPU
        self.dropdown_dificultad_cpu['visible'] = modalidad_tiene_cpu
        
        # Mostrar etiqueta de dificultad CPU si es visible
        if self.dropdown_dificultad_cpu['visible']:
            dificultad_cpu_label = self.fuente_normal.render("Nivel de dificultad CPU", True, self.COLORES['negro'])
            rect_dificultad_cpu_label = dificultad_cpu_label.get_rect(center=self.elementos_ui['config']['dificultad_cpu_label_pos'])
            self.ventana.blit(dificultad_cpu_label, rect_dificultad_cpu_label)
        
        # --- 2. Determinar qué dropdown está abierto --- 
        dropdown_abierto = None
        if self.dropdown_tipo_juego['abierto']:
            dropdown_abierto = 'tipo_juego'
        elif self.dropdown_modalidad['abierto']:
            dropdown_abierto = 'modalidad'
        elif self.dropdown_dificultad_cpu['abierto']:
            dropdown_abierto = 'dificultad_cpu'
            
        # --- 3. Dibujar dropdowns cerrados y botón --- 
        # Dibujar el dropdown de tipo de juego si está cerrado o si ningún dropdown está abierto
        if dropdown_abierto != 'tipo_juego':
             self._dibujar_dropdown('tipo_juego', self.elementos_ui['config']['tipo_juego_pos'])
             
        # Dibujar el dropdown de modalidad si está cerrado o si ningún dropdown está abierto
        if dropdown_abierto != 'modalidad':
             self._dibujar_dropdown('modalidad', self.elementos_ui['config']['modalidad_pos'])
        
        # Dibujar el dropdown de dificultad CPU si está cerrado, visible y si ningún dropdown está abierto 
        if dropdown_abierto != 'dificultad_cpu' and self.dropdown_dificultad_cpu['visible']:
             self._dibujar_dropdown('dificultad_cpu', self.elementos_ui['config']['dificultad_cpu_pos'])
             
        # Dibujar botón Jugar (se dibuja antes del dropdown abierto)
        self._dibujar_boton("Jugar", self.elementos_ui['config']['boton_jugar_pos'], 
                          accion=self.controlador.solicitar_inicio_juego)

        # --- 4. Dibujar el dropdown abierto (si existe) al final --- 
        if dropdown_abierto:
            self._dibujar_dropdown(dropdown_abierto, self.elementos_ui['config'][f'{dropdown_abierto}_pos'])
            
        # --- 5. Dibujar mensaje de error si existe ---
        self._dibujar_mensaje_error_config()
            
    def _dibujar_mensaje_error_config(self):
        """
        Dibuja un mensaje de error en la pantalla de configuración, si existe.
        El mensaje se muestra en rojo debajo del botón Jugar.
        """
        if self.mensaje_error_config:
            # Verificar si el tiempo de mostrar error ha expirado
            if self.tiempo_mostrar_error and pygame.time.get_ticks() > self.tiempo_mostrar_error:
                self.mensaje_error_config = None
                self.tiempo_mostrar_error = None
                return
            
            # Renderizar mensaje de error en color rojo
            texto_error = self.fuente_normal.render(self.mensaje_error_config, True, (200, 0, 0))  # Rojo
            
            # Posicionar debajo del botón Jugar
            pos_boton_jugar = self.elementos_ui['config']['boton_jugar_pos']
            pos_error = (pos_boton_jugar[0], pos_boton_jugar[1] + 40)  # 40px debajo del botón
            
            # Centrar horizontalmente
            rect_error = texto_error.get_rect(center=pos_error)
            
            # Dibujar texto
            self.ventana.blit(texto_error, rect_error)
            
    def mostrar_error_config(self, mensaje, duracion=3000):
        """
        Establece un mensaje de error para mostrar en la pantalla de configuración.
        
        Args:
            mensaje: Texto del mensaje de error.
            duracion: Duración en milisegundos que se mostrará el mensaje (por defecto 3 segundos).
        """
        self.mensaje_error_config = mensaje
        self.tiempo_mostrar_error = pygame.time.get_ticks() + duracion
        
        # Forzar actualización inmediata para mostrar el error
        self.actualizar()
    
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
        # Centrar el texto horizontalmente
        texto_x = x + (ancho - texto_seleccion.get_width()) // 2
        texto_y = y + alto // 2 - texto_seleccion.get_height() // 2
        self.ventana.blit(texto_seleccion, (texto_x, texto_y))
        
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
                # Centrar el texto horizontalmente
                texto_opcion_x = x + (ancho - texto_opcion.get_width()) // 2
                texto_opcion_y = y_opcion_actual + alto // 2 - texto_opcion.get_height() // 2
                self.ventana.blit(texto_opcion, (texto_opcion_x, texto_opcion_y))
                
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
        
        # Dibujar botón de desarrollo
        self._dibujar_boton_desarrollo()
        
        # Dibujar menú de desarrollo si está abierto
        if self.mostrar_menu_dev:
            self._dibujar_menu_desarrollo()
    
    def _dibujar_panel_lateral(self, x, jugador):
        """
        Dibuja un panel lateral con información del jugador.
        Incluye la sección de piezas capturadas con su valor total.
        
        Args:
            x: Posición x del borde izquierdo del panel.
            jugador: Diccionario con información del jugador.
        """
        # Rectángulo del panel
        panel_rect = pygame.Rect(x, 0, self.DIMENSIONES['panel_lateral'], self.DIMENSIONES['ventana'][1])
        pygame.draw.rect(self.ventana, self.COLORES['panel_lateral'], panel_rect)
        
        # Nombre del jugador
        texto_nombre = self.fuente_normal.render(jugador['nombre'], True, self.COLORES['gris_oscuro'])
        self.ventana.blit(texto_nombre, (x + 10, 20))
        
        # Línea separadora debajo del nombre
        pygame.draw.line(self.ventana, self.COLORES['gris_oscuro'], 
                        (x + 5, 45), (x + self.DIMENSIONES['panel_lateral'] - 5, 45), 1)
        
        # --- Dibujar Piezas Capturadas ---
        # Encabezado de piezas capturadas
        texto_capturas = self.fuente_normal.render("Piezas capturadas:", True, self.COLORES['gris_oscuro'])
        self.ventana.blit(texto_capturas, (x + 10, 55))
        
        # Línea separadora debajo del encabezado
        pygame.draw.line(self.ventana, self.COLORES['gris_oscuro'], 
                        (x + 5, 80), (x + self.DIMENSIONES['panel_lateral'] - 5, 80), 1)
        
        y_capturas = 90  # Posición Y inicial para las capturas
        x_capturas_start = x + 10
        max_ancho_panel = self.DIMENSIONES['panel_lateral'] - 20  # Margen
        tamaño_captura = 30  # Tamaño para los iconos
        espacio_captura = 5  # Espacio entre iconos
        piezas_por_fila = max(1, (max_ancho_panel - espacio_captura) // (tamaño_captura + espacio_captura))
        
        # Contadores para agrupar piezas por tipo
        conteo_tipos = {
            'peon': 0,
            'caballo': 0,
            'alfil': 0,
            'torre': 0,
            'reina': 0,
            'rey': 0
        }
        
        # Valor total de piezas capturadas
        valor_total = 0
        
        # Inicializar y_actual a y_capturas por defecto (para cuando no hay piezas capturadas)
        y_actual = y_capturas
        x_actual = x_capturas_start
        i = 0
        
        # Registrar en el log lo que se va a dibujar
        if 'piezas_capturadas' in jugador:
            num_piezas = len(jugador['piezas_capturadas']) if jugador['piezas_capturadas'] else 0
            logger.debug(f"Dibujando {num_piezas} piezas capturadas para {jugador.get('nombre', 'Jugador')} ({jugador.get('color', 'color desconocido')})")
        
        if 'piezas_capturadas' in jugador and jugador['piezas_capturadas']:
            # Contar piezas por tipo y calcular valor total
            for pieza in jugador['piezas_capturadas']:
                tipo = type(pieza).__name__.lower()
                if tipo in conteo_tipos:
                    conteo_tipos[tipo] += 1
                    try:
                        if hasattr(pieza, 'getValor') and callable(pieza.getValor):
                            valor_total += pieza.getValor()
                        else:
                            # Valores predeterminados si getValor no está disponible
                            valores_default = {'peon': 1, 'caballo': 3, 'alfil': 3, 'torre': 5, 'reina': 9, 'rey': 0}
                            valor_total += valores_default.get(tipo, 0)
                    except Exception as e:
                        logger.error(f"Error al calcular valor de pieza: {e}")
            
            # Dibujar piezas agrupadas por tipo
            # Ordenar por valor (de mayor a menor)
            # Utilizamos valores predeterminados para ordenar
            valores_orden = {'reina': 9, 'torre': 5, 'alfil': 3, 'caballo': 3, 'peon': 1, 'rey': 0}
            tipos_ordenados = sorted(conteo_tipos.keys(), 
                                    key=lambda t: valores_orden.get(t, 0), 
                                    reverse=True)
            
            for tipo in tipos_ordenados:
                cantidad = conteo_tipos[tipo]
                if cantidad > 0:
                    # Solo dibujar los tipos que tienen al menos una pieza
                    # Buscar el color correspondiente (para capturadas, es el color opuesto al jugador)
                    try:
                        color_pieza = 'negro' if jugador.get('color', 'blanco') == 'blanco' else 'blanco'
                        imagen_orig = self.imagenes_piezas.get(color_pieza, {}).get(tipo)
                        
                        if imagen_orig:
                            imagen_captura = pygame.transform.smoothscale(imagen_orig, (tamaño_captura, tamaño_captura))
                            
                            # Cambiar de fila si no hay espacio
                            if i % piezas_por_fila == 0 and i > 0:
                                x_actual = x_capturas_start
                                y_actual += tamaño_captura + espacio_captura
                            
                            # Dibujar la pieza
                            self.ventana.blit(imagen_captura, (x_actual, y_actual))
                            
                            # Si hay más de una del mismo tipo, mostrar un contador
                            if cantidad > 1:
                                texto_contador = self.fuente_pequeña.render(f"x{cantidad}", True, self.COLORES['negro'])
                                self.ventana.blit(texto_contador, (x_actual + tamaño_captura - 15, y_actual + tamaño_captura - 15))
                            
                            x_actual += tamaño_captura + espacio_captura
                            i += 1
                        else:
                            logger.warning(f"No se encontró imagen para pieza capturada: {tipo} {color_pieza}")
                    except Exception as e:
                        logger.error(f"Error al dibujar pieza capturada de tipo {tipo}: {e}")
        
        # Mostrar valor total de captura
        y_valor = y_actual + tamaño_captura + 15
        texto_valor = self.fuente_normal.render(f"Valor total: {valor_total}", True, self.COLORES['gris_oscuro'])
        self.ventana.blit(texto_valor, (x + 10, y_valor))
        
        # --- Dibujar Historial de Movimientos (en ambos paneles) ---
        self._dibujar_historial_movimientos(x, y_valor + 25, jugador.get('color', 'blanco'))
            
    def _dibujar_historial_movimientos(self, x, y_inicial, color_jugador):
        """
        Dibuja el historial de movimientos específico para cada jugador.
        En el panel izquierdo se muestran los movimientos del jugador blanco,
        en el panel derecho los del jugador negro.
        
        Args:
            x: Posición x donde comenzar a dibujar.
            y_inicial: Posición y donde comenzar a dibujar.
            color_jugador: Color del jugador ('blanco' o 'negro').
        """
        # Rectángulo para el historial
        ancho_historial = self.DIMENSIONES['panel_lateral'] - 20  # Margen
        alto_historial = 200  # Alto fijo para el área de historial
        x_historial = x + 10
        
        # Encabezado del historial
        texto_historial = self.fuente_normal.render("Histórico de movimientos:", True, self.COLORES['gris_oscuro'])
        self.ventana.blit(texto_historial, (x_historial, y_inicial))
        
        # Línea separadora debajo del encabezado
        pygame.draw.line(self.ventana, self.COLORES['gris_oscuro'], 
                       (x + 5, y_inicial + 25), (x + self.DIMENSIONES['panel_lateral'] - 5, y_inicial + 25), 1)
        
        # Obtener el historial de movimientos del tablero
        tablero = self.controlador.obtener_tablero()
        if not tablero or not hasattr(tablero, 'gestor_historico'):
            return
        
        # Filtrar movimientos para mostrar solo los del color correspondiente al panel
        movimientos_filtrados = []
        try:
            if hasattr(tablero, 'gestor_historico') and tablero.gestor_historico:
                for idx, mov in enumerate(tablero.gestor_historico.historial_completo):
                    if mov['color'] == color_jugador:
                        num = idx // 2 + 1  # Convertir a número de movimiento (1, 2, 3...)
                        movimientos_filtrados.append({
                            'numero': num,
                            'notacion_san': mov['notacion_san'],
                            'color': mov['color'],
                            'es_enroque': mov.get('es_enroque', False),
                        })
        except Exception as e:
            logger.error(f"Error al procesar historial de movimientos: {e}")
            
        # Mostrar los movimientos en formato simple
        y_offset = 35  # Margen inicial desde el encabezado
        for idx, mov in enumerate(movimientos_filtrados):
            numero = mov['numero']
            notacion = mov['notacion_san']
            
            # Formatear como se muestra en la imagen
            if mov.get('es_enroque', False) and 'O-O' in notacion and '-O' not in notacion:
                texto_mov = f"{numero}. O-O (Enroque corto)"
            else:
                texto_mov = f"{numero}. {notacion}"
                
            mov_surf = self.fuente_pequeña.render(texto_mov, True, self.COLORES['gris_oscuro'])
            self.ventana.blit(mov_surf, (x_historial, y_inicial + y_offset))
            y_offset += self.fuente_pequeña.get_height() + 5

    def _dibujar_indicador_turno(self):
        """ Dibuja un texto indicando de quién es el turno. """
        # Solo mostrar el indicador de turno si no hay un mensaje de estado activo
        if not self.mensaje_estado:
            texto = f"Turno de: {self.turno_actual.capitalize()}"
            color_texto = self.COLORES['negro']
            # Usar fuente normal en lugar de subtitulo para reducir tamaño
            fuente_turno = self.fuente_normal
            
            texto_surf = fuente_turno.render(texto, True, color_texto)
            
            # Posicionar más abajo pero todavía separado del timer
            centro_x = self.DIMENSIONES['ventana'][0] // 2
            pos_y = 30 # Ajustado a 30 para bajar el mensaje
            
            texto_rect = texto_surf.get_rect(center=(centro_x, pos_y))
            
            # Dibujar solo el texto, sin fondo ni borde
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
                
            # Usar fuente normal en lugar de subtitulo para hacer texto más pequeño
            fuente_mensaje = self.fuente_normal
            
            texto_surf = fuente_mensaje.render(self.mensaje_estado, True, color_texto)
            
            # Posicionar más abajo pero todavía separado del timer
            centro_x = self.DIMENSIONES['ventana'][0] // 2
            pos_y = 30 # Ajustado a 30 para bajar el mensaje
            
            texto_rect = texto_surf.get_rect(center=(centro_x, pos_y))
            
            # Dibujar solo el texto, sin fondo ni borde
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
        padding_horizontal = 15 # Aumentado de 10 a 15
        padding_vertical = 12   # Aumentado para más espacio vertical

        # Renderizar el texto para obtener su tamaño
        texto_surf = fuente_reloj.render(texto_tiempo, True, color_texto)
        texto_rect = texto_surf.get_rect()

        # Calcular tamaño y posición del rectángulo de fondo
        fondo_ancho = texto_rect.width + 2 * padding_horizontal
        fondo_alto = texto_rect.height + 2 * padding_vertical
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
                
                # Resaltar casillas de captura (piezas rivales que pueden ser tomadas)
                elif (fila, columna) in self.casillas_captura:
                    pygame.draw.rect(self.ventana, self.COLORES['captura'], 
                                    (x, y, tamaño_casilla, tamaño_casilla))
                # Resaltar movimientos válidos normales (sin captura)
                elif (fila, columna) in self.movimientos_validos:
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
        También actualiza los colores de los jugadores si es necesario.

        Args:
            nuevo_turno: El color del jugador cuyo turno comienza ('blanco' o 'negro').
        """
        if not self.temporizador_activo or self.tiempo_inicio_turno is None:
            logger.warning("[Interfaz] Se intentó cambiar turno sin temporizador activo.")
            # Aún así, actualizamos el turno visualmente
            self.turno_actual = nuevo_turno
            return

        # Calcular tiempo transcurrido en el turno que termina
        tiempo_transcurrido = pygame.time.get_ticks() - self.tiempo_inicio_turno
        
        # Acumular tiempo para el jugador que acaba de mover
        self.tiempo_acumulado[self.turno_actual] += tiempo_transcurrido
        logger.debug(f"[Interfaz] Tiempo acumulado {self.turno_actual}: {self.tiempo_acumulado[self.turno_actual]/1000:.2f}s")
        
        # Actualizar al nuevo turno
        self.turno_actual = nuevo_turno
        
        # Asegurar que los jugadores tengan sus colores establecidos
        # Esto es importante para mostrar correctamente las piezas capturadas
        self.jugadores['blanco']['color'] = 'blanco'
        self.jugadores['negro']['color'] = 'negro'
        
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
                    # Si el popup de fin de juego está abierto, manejarlo primero
                    if self.mostrar_popup_fin_juego:
                        self._manejar_clic_popup_fin_juego(evento.pos)
                    # Si el menú de desarrollo está abierto, manejarlo
                    elif self.mostrar_menu_dev:
                        self._manejar_clic_menu_desarrollo(evento.pos)
                    # Verificar clic en el botón de desarrollo
                    elif self._es_clic_en_boton_desarrollo(evento.pos):
                        self.mostrar_menu_dev = True
                    # Verificar si se hizo clic en el historial de movimientos
                    elif self._es_clic_en_historial(evento.pos):
                        self._manejar_clic_historial(evento.pos)
                    else:
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
        elif self.dropdown_dificultad_cpu['abierto']:
            dropdown_abierto_nombre = 'dificultad_cpu'
            dropdown_abierto_obj = self.dropdown_dificultad_cpu

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
        
        # Verificar clics en las cabeceras de los dropdowns (todos están cerrados)
        self._verificar_clic_dropdown('tipo_juego', pos) 
        self._verificar_clic_dropdown('modalidad', pos)
        
        # Solo verificar el dropdown de dificultad CPU si es visible
        if self.dropdown_dificultad_cpu['visible']:
            self._verificar_clic_dropdown('dificultad_cpu', pos)
    
    def _verificar_clic_dropdown(self, nombre, pos):
        """
        Verifica si se hizo clic en un menú desplegable (cabecera u opción)
        y maneja el evento.
        
        Args:
            nombre: Nombre del menú ('tipo_juego', 'modalidad' o 'dificultad_cpu').
            pos: Posición (x, y) del clic.
        """
        dropdown = getattr(self, f'dropdown_{nombre}')
        
        # Si es el dropdown de dificultad CPU y no está visible, ignorar
        if nombre == 'dificultad_cpu' and not dropdown['visible']:
            return
            
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
            # Si se acaba de abrir este, cerrar los otros
            if dropdown['abierto']:
                for otro_nombre in ['tipo_juego', 'modalidad', 'dificultad_cpu']:
                    if otro_nombre != nombre:
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
                    
                    # Si cambia la modalidad, actualizar la visibilidad del dropdown de dificultad CPU
                    if nombre == 'modalidad':
                        modalidad_tiene_cpu = any(cpu in opcion for cpu in ["CPU vs", "vs CPU"])
                        self.dropdown_dificultad_cpu['visible'] = modalidad_tiene_cpu
                    
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
            
            # Si hay un popup de fin de juego que mostrar, dibujarlo encima
            if self.mostrar_popup_fin_juego:
                self._dibujar_popup_fin_juego()
        
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
            None: Si no se ha seleccionado alguna opción requerida.
        """
        # Valores por defecto de los dropdowns
        tipo_juego_default = 'Escoge el tipo de juego'
        modalidad_default = 'Escoge la modalidad'
        dificultad_cpu_default = 'Selecciona nivel de dificultad'
        
        # Verificar si los dropdowns requeridos tienen selecciones válidas
        tipo_juego_seleccionado = self.dropdown_tipo_juego['seleccionado']
        modalidad_seleccionada = self.dropdown_modalidad['seleccionado']
        
        # Si alguno de los principales tiene el valor por defecto, retornar None
        if tipo_juego_seleccionado == tipo_juego_default or modalidad_seleccionada == modalidad_default:
            return None
            
        # Verificar si se necesita el nivel de dificultad de CPU
        if any(cpu in modalidad_seleccionada for cpu in ["CPU vs", "vs CPU"]):
            dificultad_cpu_seleccionada = self.dropdown_dificultad_cpu['seleccionado']
            if dificultad_cpu_seleccionada == dificultad_cpu_default:
                return None  # Si se requiere nivel CPU pero no se ha seleccionado
                
            # Extraer el número de nivel de la selección (e.g., "Nivel 3 (Intermedio)" -> 3)
            nivel_cpu = int(dificultad_cpu_seleccionada.split()[1].split('(')[0])
        else:
            nivel_cpu = None  # No se necesita nivel CPU para Humano vs Humano
        
        # Crear y retornar el diccionario de configuración
        config = {
            'tipo_juego': tipo_juego_seleccionado,
            'modalidad': modalidad_seleccionada
        }
        
        # Añadir nivel de CPU si es aplicable
        if nivel_cpu is not None:
            config['nivel_cpu'] = nivel_cpu
            
        return config

    def mostrar_mensaje_estado(self, texto: Optional[str]):
        """
        Actualiza el mensaje de estado que se mostrará en la pantalla.
        Si texto es None, limpia el mensaje.
        """
        self.mensaje_estado = texto
        # Podríamos añadir lógica para que mensajes no persistentes desaparezcan
        # después de un tiempo, pero por ahora se mantienen hasta el siguiente cambio.
    
    def mostrar_fin_de_juego(self, resultado, motivo=None):
        """
        Muestra el popup de fin de juego con el resultado correspondiente.
        
        Args:
            resultado: Tipo de resultado ('victoria_blanco', 'victoria_negro', 'tablas')
            motivo: Opcional, motivo específico del fin de juego (por ejemplo, 'jaque_mate', 'ahogado', etc.)
        """
        self.mostrar_popup_fin_juego = True
        self.tipo_fin_juego = resultado
        
        # Detener el temporizador cuando el juego termina
        self.detener_temporizador()
        
        # Determinar el mensaje según el resultado y motivo
        if resultado == 'victoria_blanco':
            self.mensaje_fin_juego = f"¡Gana el {self.jugadores['blanco']['nombre']}!"
        elif resultado == 'victoria_negro':
            self.mensaje_fin_juego = f"¡Gana el {self.jugadores['negro']['nombre']}!"
        elif resultado == 'tablas':
            if motivo == 'ahogado':
                self.mensaje_fin_juego = "¡Tablas por ahogado!"
            elif motivo == 'material_insuficiente':
                self.mensaje_fin_juego = "¡Tablas por material insuficiente!"
            elif motivo == 'repeticion':
                self.mensaje_fin_juego = "¡Tablas por repetición!"
            elif motivo == 'regla_50_movimientos':
                self.mensaje_fin_juego = "¡Tablas por regla de 50 movimientos!"
            else:
                self.mensaje_fin_juego = "¡Tablas!"
        
        # Actualizar la pantalla para mostrar el popup inmediatamente
        self.actualizar(self.controlador.obtener_tablero())
        
    def _dibujar_popup_fin_juego(self):
        """
        Dibuja el popup de fin de juego con el mensaje de resultado y botones.
        El tamaño se adapta automáticamente al contenido.
        """
        # 1. Dibujar overlay semi-transparente
        overlay = pygame.Surface(self.DIMENSIONES['ventana'], pygame.SRCALPHA)
        overlay.fill(self.COLORES['overlay'])
        self.ventana.blit(overlay, (0, 0))
        
        # 2. Calcular tamaños de los elementos para adaptar el popup
        titulo_texto = self.fuente_subtitulo.render("Final del Juego", True, self.COLORES['negro'])
        mensaje_texto = self.fuente_titulo.render(self.mensaje_fin_juego, True, self.COLORES['negro'])
        texto_revancha = self.fuente_normal.render("Revancha", True, self.COLORES['blanco'])
        texto_menu = self.fuente_normal.render("Menú Principal", True, self.COLORES['negro'])
        
        # Calcular ancho mínimo basado en el texto más ancho
        padding_horizontal = 40  # Padding a cada lado
        ancho_minimo = 400  # Ancho mínimo por defecto
        ancho_titulo = titulo_texto.get_width() + padding_horizontal*2
        ancho_mensaje = mensaje_texto.get_width() + padding_horizontal*2
        ancho_botones = max(160, texto_revancha.get_width() + 40, texto_menu.get_width() + 40)  # Botones de al menos 160px
        
        # El popup debe ser al menos tan ancho como el elemento más ancho
        popup_ancho = max(ancho_minimo, ancho_titulo, ancho_mensaje, ancho_botones + padding_horizontal*2)
        
        # Calcular alto basado en el contenido
        padding_vertical = 30  # Padding vertical entre elementos
        padding_mensaje_botones = 60  # Padding adicional entre el mensaje y los botones
        alto_titulo = titulo_texto.get_height()
        alto_mensaje = mensaje_texto.get_height()
        alto_botones = 40 * 2 + 20  # Dos botones de 40px con 20px entre ellos
        
        # Calcular alto total con padding adecuado
        popup_alto = padding_vertical + alto_titulo + padding_vertical + alto_mensaje + padding_vertical + padding_mensaje_botones + alto_botones + padding_vertical
        
        # 3. Calcular posición del popup (centrado)
        ventana_ancho, ventana_alto = self.DIMENSIONES['ventana']
        popup_x = (ventana_ancho - popup_ancho) // 2
        popup_y = (ventana_alto - popup_alto) // 2 - 20  # Un poco más arriba del centro exacto
        
        # 4. Dibujar fondo del popup
        popup_rect = pygame.Rect(popup_x, popup_y, popup_ancho, popup_alto)
        pygame.draw.rect(self.ventana, self.COLORES['blanco'], popup_rect)
        pygame.draw.rect(self.ventana, self.COLORES['gris_oscuro'], popup_rect, 2)  # Borde
        
        # 5. Dibujar título "Final del Juego"
        titulo_rect = titulo_texto.get_rect(center=(popup_x + popup_ancho // 2, popup_y + padding_vertical + alto_titulo // 2))
        self.ventana.blit(titulo_texto, titulo_rect)
        
        # 6. Dibujar mensaje de resultado
        mensaje_rect = mensaje_texto.get_rect(center=(popup_x + popup_ancho // 2, popup_y + padding_vertical*2 + alto_titulo + alto_mensaje // 2))
        self.ventana.blit(mensaje_texto, mensaje_rect)
        
        # 7. Dibujar botones
        # Posición Y para los botones, añadiendo el padding extra
        botones_y = popup_y + padding_vertical*3 + alto_titulo + alto_mensaje + padding_mensaje_botones
        
        # Botón "Revancha"
        boton_revancha_rect = pygame.Rect(0, 0, ancho_botones, 40)
        boton_revancha_rect.center = (popup_x + popup_ancho // 2, botones_y)
        pygame.draw.rect(self.ventana, self.COLORES['negro'], boton_revancha_rect)
        texto_revancha_rect = texto_revancha.get_rect(center=boton_revancha_rect.center)
        self.ventana.blit(texto_revancha, texto_revancha_rect)
        
        # Botón "Menú Principal"
        boton_menu_rect = pygame.Rect(0, 0, ancho_botones, 40)
        boton_menu_rect.center = (popup_x + popup_ancho // 2, botones_y + 60)
        pygame.draw.rect(self.ventana, self.COLORES['blanco'], boton_menu_rect)
        pygame.draw.rect(self.ventana, self.COLORES['negro'], boton_menu_rect, 2)  # Borde
        texto_menu_rect = texto_menu.get_rect(center=boton_menu_rect.center)
        self.ventana.blit(texto_menu, texto_menu_rect)
        
        # Guardar referencias a los rectángulos de los botones para detectar clics
        self.elementos_ui['popup_fin_juego'] = {
            'revancha': boton_revancha_rect,
            'menu_principal': boton_menu_rect
        }
    
    def _manejar_clic_popup_fin_juego(self, pos):
        """
        Maneja los clics en los botones del popup de fin de juego.
        
        Args:
            pos: Posición (x, y) del clic.
        """
        if 'popup_fin_juego' not in self.elementos_ui:
            return
            
        # Verificar clic en botón "Revancha"
        if self.elementos_ui['popup_fin_juego']['revancha'].collidepoint(pos):
            self._reiniciar_juego()
            
        # Verificar clic en botón "Menú Principal"
        elif self.elementos_ui['popup_fin_juego']['menu_principal'].collidepoint(pos):
            self._volver_menu_principal()
    
    def _reiniciar_juego(self):
        """
        Reinicia el juego con la misma configuración.
        """
        # Ocultar el popup
        self.mostrar_popup_fin_juego = False
        
        # Limpiar estados de la UI
        self.pieza_seleccionada = None
        self.casilla_origen = None
        self.movimientos_validos = []
        self.casillas_captura = []
        self.mensaje_estado = None
        
        # Solicitar al controlador reiniciar el juego
        # El controlador es responsable de actualizar los datos del modelo
        # y actualizar los datos en la vista (siguiendo patrón MVC)
        self.controlador.reiniciar_juego()
        
        # Reiniciar el temporizador
        self.iniciar_temporizador()
    
    def _volver_menu_principal(self):
        """
        Vuelve al menú principal/pantalla de configuración.
        """
        # Ocultar el popup
        self.mostrar_popup_fin_juego = False
        
        # Limpiar estados de la UI
        self.pieza_seleccionada = None
        self.casilla_origen = None
        self.movimientos_validos = []
        self.casillas_captura = []
        self.mensaje_estado = None
        
        # Cambiar a la vista de configuración
        self.cambiar_vista('configuracion')
        
        # Notificar al controlador
        self.controlador.volver_menu_principal()

    def _es_clic_en_historial(self, pos):
        """
        Verifica si un clic fue en el área del historial de movimientos.
        
        Args:
            pos: Posición (x, y) del clic.
            
        Returns:
            bool: True si el clic fue en el área del historial.
        """
        # Coordenadas del panel lateral derecho (negro)
        x_panel = self.DIMENSIONES['ventana'][0] - self.DIMENSIONES['panel_lateral']
        
        # Solo si el clic está en el panel lateral derecho
        if pos[0] < x_panel:
            return False
            
        # Para determinar la posición y, necesitamos calcular dónde comienza el historial
        # Esto depende de cuántas piezas capturadas hay, por lo que es variable
        tablero = self.controlador.obtener_tablero()
        if not tablero:
            return False
            
        # Aproximación: verificar si el clic está en la mitad inferior del panel
        return pos[1] > 250  # Valor ajustado para la nueva posición del historial
        
    def _manejar_clic_historial(self, pos):
        """
        Maneja clics en el área del historial de movimientos.
        
        Args:
            pos: Posición (x, y) del clic.
        """
        # En una implementación completa, este método calcularía qué movimiento
        # se clicó y saltaría a esa posición en el historial.
        
        # Para esta implementación básica, simplemente registramos que se detectó un clic
        logger.debug(f"Clic detectado en historial de movimientos en posición {pos}")
        
        # Aquí iría la lógica para:
        # 1. Determinar qué movimiento del historial se clicó
        # 2. Obtener la representación de tablero correspondiente a ese movimiento
        # 3. Cargar esa representación en el tablero actual
        
        # Esto requeriría que cada movimiento en el historial tenga asociada
        # una representación del estado del tablero, o la capacidad de recrear
        # el estado del tablero hasta ese movimiento.
        
        # Ejemplo conceptual (no implementado):
        # indice_movimiento = self._calcular_indice_movimiento_desde_pos(pos)
        # if indice_movimiento is not None:
        #     self.controlador.saltar_a_movimiento(indice_movimiento) 

    def _dibujar_boton_desarrollo(self):
        """
        Dibuja un botón de desarrollo en la esquina inferior derecha de la pantalla.
        Este botón permite activar rápidamente diferentes escenarios de fin de juego.
        """
        # Definir posición y tamaño del botón
        ancho, alto = 120, 30
        x = self.DIMENSIONES['ventana'][0] - ancho - 10  # 10px desde el borde derecho
        y = self.DIMENSIONES['ventana'][1] - alto - 10   # 10px desde el borde inferior
        
        # Dibujar botón (con un color distintivo para desarrollo)
        boton_rect = pygame.Rect(x, y, ancho, alto)
        pygame.draw.rect(self.ventana, (255, 100, 100), boton_rect)  # Rojo claro
        pygame.draw.rect(self.ventana, self.COLORES['negro'], boton_rect, 2)  # Borde negro
        
        # Texto del botón
        texto = self.fuente_normal.render("DEV: FIN JUEGO", True, self.COLORES['negro'])
        texto_rect = texto.get_rect(center=boton_rect.center)
        self.ventana.blit(texto, texto_rect)
        
        # Guardar referencia al rectángulo para detectar clics
        self.botones_desarrollo['fin_juego'] = boton_rect
    
    def _es_clic_en_boton_desarrollo(self, pos):
        """
        Verifica si se hizo clic en el botón de desarrollo.
        
        Args:
            pos: Posición (x, y) del clic.
            
        Returns:
            bool: True si el clic fue en el botón de desarrollo.
        """
        return 'fin_juego' in self.botones_desarrollo and self.botones_desarrollo['fin_juego'].collidepoint(pos)
    
    def _dibujar_menu_desarrollo(self):
        """
        Dibuja un menú con opciones para simular diferentes escenarios de fin de juego.
        """
        # Definir posición y tamaño del menú (justo encima del botón de desarrollo)
        ancho_menu = 180
        alto_opcion = 30
        num_opciones = 7  # Aumentado de 5 a 7 para incluir las nuevas opciones
        alto_menu = alto_opcion * num_opciones + 10  # 5px de padding arriba y abajo
        
        x = self.DIMENSIONES['ventana'][0] - ancho_menu - 10  # 10px desde el borde derecho
        y = self.DIMENSIONES['ventana'][1] - alto_menu - 50   # 10px + altura del botón desde el borde inferior
        
        # Dibujar fondo del menú
        menu_rect = pygame.Rect(x, y, ancho_menu, alto_menu)
        pygame.draw.rect(self.ventana, self.COLORES['blanco'], menu_rect)
        pygame.draw.rect(self.ventana, self.COLORES['negro'], menu_rect, 2)  # Borde negro
        
        # Opciones del menú
        opciones = [
            "Victoria Blancas", 
            "Victoria Negras", 
            "Tablas (Ahogado)", 
            "Tablas (Insuficiente)",
            "Tablas (Repetición)",
            "Tablas (50 Movimientos)",
            "Cerrar Menú"
        ]
        
        # Dibujar cada opción
        self.botones_desarrollo['opciones'] = []
        for i, opcion in enumerate(opciones):
            opcion_y = y + 5 + i * alto_opcion
            opcion_rect = pygame.Rect(x + 5, opcion_y, ancho_menu - 10, alto_opcion - 5)
            
            # Color de fondo diferente para la última opción (Cerrar)
            if i == len(opciones) - 1:
                pygame.draw.rect(self.ventana, self.COLORES['gris_claro'], opcion_rect)
            else:
                pygame.draw.rect(self.ventana, self.COLORES['blanco'], opcion_rect)
            
            # Texto de la opción
            texto = self.fuente_normal.render(opcion, True, self.COLORES['negro'])
            texto_rect = texto.get_rect(midleft=(opcion_rect.left + 5, opcion_rect.centery))
            self.ventana.blit(texto, texto_rect)
            
            # Guardar referencia al rectángulo para detectar clics
            self.botones_desarrollo['opciones'].append((opcion, opcion_rect))
    
    def _manejar_clic_menu_desarrollo(self, pos):
        """
        Maneja los clics en las opciones del menú de desarrollo.
        
        Args:
            pos: Posición (x, y) del clic.
        """
        # Verificar clic en las opciones del menú
        if 'opciones' in self.botones_desarrollo:
            for opcion, rect in self.botones_desarrollo['opciones']:
                if rect.collidepoint(pos):
                    self._activar_opcion_desarrollo(opcion)
                    return
        
        # Si se hizo clic fuera del menú, cerrarlo
        self.mostrar_menu_dev = False
    
    def _activar_opcion_desarrollo(self, opcion):
        """
        Activa la opción de desarrollo seleccionada.
        
        Args:
            opcion: Texto de la opción seleccionada.
        """
        # Cerrar el menú en cualquier caso
        self.mostrar_menu_dev = False
        
        # Activar la opción correspondiente
        if opcion == "Victoria Blancas":
            self.controlador.dev_test_victoria_blancas()
        elif opcion == "Victoria Negras":
            self.controlador.dev_test_victoria_negras()
        elif opcion == "Tablas (Ahogado)":
            self.controlador.dev_test_tablas_ahogado()
        elif opcion == "Tablas (Insuficiente)":
            self.controlador.dev_test_tablas_insuficiente()
        elif opcion == "Tablas (Repetición)":
            self.controlador.dev_test_tablas_repeticion()
        elif opcion == "Tablas (50 Movimientos)":
            self.controlador.dev_test_tablas_50_movimientos()
        # "Cerrar Menú" no requiere acción adicional 