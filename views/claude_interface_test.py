import pygame
import sys

# Inicialización de pygame
pygame.init()

# Constantes
ANCHO, ALTO = 640, 640
DIMENSION = 8  # Dimensiones del tablero 8x8
TAMAÑO_CASILLA = ANCHO // DIMENSION
FPS = 60
IMAGENES = {}  # Diccionario para almacenar imágenes de piezas

# Colores
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
GRIS = (128, 128, 128)
AZUL_CLARO = (100, 149, 237)
VERDE_CLARO = (144, 238, 144)

# Configuración de la pantalla
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption('Ajedrez')
reloj = pygame.time.Clock()


def cargar_imagenes():
    """Carga las imágenes de las piezas y las almacena en el diccionario IMAGENES."""
    piezas = ['bR', 'bN', 'bB', 'bQ', 'bK', 'bP', 'wR', 'wN', 'wB', 'wQ', 'wK', 'wP']
    for pieza in piezas:
        # Nota: Este código asume que tienes imágenes en una carpeta 'imagenes'
        # Las imágenes deben ser nombradas como 'bR.png', 'wK.png', etc.
        try:
            IMAGENES[pieza] = pygame.transform.scale(
                pygame.image.load(f"imagenes/{pieza}.png"), (TAMAÑO_CASILLA, TAMAÑO_CASILLA)
            )
        except:
            print(f"No se pudo cargar la imagen {pieza}.png")
            # Utilizar rectángulos coloreados como respaldo si no hay imágenes
            color = NEGRO if pieza[0] == 'b' else BLANCO
            IMAGENES[pieza] = pygame.Surface((TAMAÑO_CASILLA, TAMAÑO_CASILLA))
            IMAGENES[pieza].fill(GRIS)
            font = pygame.font.SysFont('Arial', 32)
            text = font.render(pieza[1], True, color)
            text_rect = text.get_rect(center=(TAMAÑO_CASILLA//2, TAMAÑO_CASILLA//2))
            IMAGENES[pieza].blit(text, text_rect)


class EstadoJuego:
    """Almacena toda la información sobre el estado actual del juego de ajedrez."""
    
    def __init__(self):
        # Tablero es una lista 8x8, donde cada elemento es una pieza o '--'
        # El primer caracter representa el color ('b' o 'w')
        # El segundo caracter representa el tipo de pieza (R, N, B, Q, K, P)
        self.tablero = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.turno_blanco = True
        self.movimientos_validos = self.generar_movimientos_validos()
        self.pieza_seleccionada = None  # (fila, columna)
        self.jaque_mate = False
        self.tablas = False
        self.historial_movimientos = []
    
    def hacer_movimiento(self, movimiento):
        """Ejecuta un movimiento en el tablero."""
        self.tablero[movimiento.fila_inicio][movimiento.col_inicio] = "--"
        self.tablero[movimiento.fila_fin][movimiento.col_fin] = movimiento.pieza_movida
        self.historial_movimientos.append(movimiento)
        self.turno_blanco = not self.turno_blanco
        self.movimientos_validos = self.generar_movimientos_validos()
    
    def deshacer_movimiento(self):
        """Deshace el último movimiento."""
        if len(self.historial_movimientos) > 0:
            movimiento = self.historial_movimientos.pop()
            self.tablero[movimiento.fila_inicio][movimiento.col_inicio] = movimiento.pieza_movida
            self.tablero[movimiento.fila_fin][movimiento.col_fin] = movimiento.pieza_capturada
            self.turno_blanco = not self.turno_blanco
            self.movimientos_validos = self.generar_movimientos_validos()
    
    def generar_movimientos_validos(self):
        """Genera todos los movimientos válidos para la posición actual."""
        movimientos = []
        for f in range(8):
            for c in range(8):
                color = self.tablero[f][c][0]
                if (color == 'w' and self.turno_blanco) or (color == 'b' and not self.turno_blanco):
                    pieza = self.tablero[f][c][1]
                    if pieza == 'P':
                        self.generar_movimientos_peon(f, c, movimientos)
                    elif pieza == 'R':
                        self.generar_movimientos_torre(f, c, movimientos)
                    elif pieza == 'N':
                        self.generar_movimientos_caballo(f, c, movimientos)
                    elif pieza == 'B':
                        self.generar_movimientos_alfil(f, c, movimientos)
                    elif pieza == 'Q':
                        self.generar_movimientos_reina(f, c, movimientos)
                    elif pieza == 'K':
                        self.generar_movimientos_rey(f, c, movimientos)
        return movimientos
    
    def generar_movimientos_peon(self, f, c, movimientos):
        """Genera todos los movimientos válidos para un peón en la posición (f, c)."""
        if self.turno_blanco:  # Peón blanco (se mueve hacia arriba)
            if f > 0 and self.tablero[f-1][c] == "--":  # Avance simple
                movimientos.append(Movimiento((f, c), (f-1, c), self.tablero))
                if f == 6 and self.tablero[f-2][c] == "--":  # Avance doble (solo desde posición inicial)
                    movimientos.append(Movimiento((f, c), (f-2, c), self.tablero))
            
            # Capturas
            if f > 0 and c > 0:  # Captura a la izquierda
                if self.tablero[f-1][c-1][0] == 'b':  # Hay una pieza negra para capturar
                    movimientos.append(Movimiento((f, c), (f-1, c-1), self.tablero))
            
            if f > 0 and c < 7:  # Captura a la derecha
                if self.tablero[f-1][c+1][0] == 'b':  # Hay una pieza negra para capturar
                    movimientos.append(Movimiento((f, c), (f-1, c+1), self.tablero))
        
        else:  # Peón negro (se mueve hacia abajo)
            if f < 7 and self.tablero[f+1][c] == "--":  # Avance simple
                movimientos.append(Movimiento((f, c), (f+1, c), self.tablero))
                if f == 1 and self.tablero[f+2][c] == "--":  # Avance doble (solo desde posición inicial)
                    movimientos.append(Movimiento((f, c), (f+2, c), self.tablero))
            
            # Capturas
            if f < 7 and c > 0:  # Captura a la izquierda
                if self.tablero[f+1][c-1][0] == 'w':  # Hay una pieza blanca para capturar
                    movimientos.append(Movimiento((f, c), (f+1, c-1), self.tablero))
            
            if f < 7 and c < 7:  # Captura a la derecha
                if self.tablero[f+1][c+1][0] == 'w':  # Hay una pieza blanca para capturar
                    movimientos.append(Movimiento((f, c), (f+1, c+1), self.tablero))
    
    def generar_movimientos_torre(self, f, c, movimientos):
        """Genera todos los movimientos válidos para una torre en la posición (f, c)."""
        direcciones = [(1, 0), (-1, 0), (0, 1), (0, -1)]  # Abajo, arriba, derecha, izquierda
        color_enemigo = 'b' if self.turno_blanco else 'w'
        
        for df, dc in direcciones:
            for i in range(1, 8):
                fila_final = f + i * df
                col_final = c + i * dc
                
                # Verificar si la posición está dentro del tablero
                if 0 <= fila_final < 8 and 0 <= col_final < 8:
                    pieza_final = self.tablero[fila_final][col_final]
                    
                    if pieza_final == "--":  # Casilla vacía
                        movimientos.append(Movimiento((f, c), (fila_final, col_final), self.tablero))
                    elif pieza_final[0] == color_enemigo:  # Pieza enemiga
                        movimientos.append(Movimiento((f, c), (fila_final, col_final), self.tablero))
                        break
                    else:  # Pieza propia
                        break
                else:  # Fuera del tablero
                    break
    
    def generar_movimientos_caballo(self, f, c, movimientos):
        """Genera todos los movimientos válidos para un caballo en la posición (f, c)."""
        saltos = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (-1, 2), (1, -2), (-1, -2)]
        color_aliado = 'w' if self.turno_blanco else 'b'
        
        for df, dc in saltos:
            fila_final = f + df
            col_final = c + dc
            
            # Verificar si la posición está dentro del tablero
            if 0 <= fila_final < 8 and 0 <= col_final < 8:
                pieza_final = self.tablero[fila_final][col_final]
                
                if pieza_final[0] != color_aliado:  # Casilla vacía o pieza enemiga
                    movimientos.append(Movimiento((f, c), (fila_final, col_final), self.tablero))
    
    def generar_movimientos_alfil(self, f, c, movimientos):
        """Genera todos los movimientos válidos para un alfil en la posición (f, c)."""
        direcciones = [(1, 1), (1, -1), (-1, 1), (-1, -1)]  # Diagonales
        color_enemigo = 'b' if self.turno_blanco else 'w'
        
        for df, dc in direcciones:
            for i in range(1, 8):
                fila_final = f + i * df
                col_final = c + i * dc
                
                # Verificar si la posición está dentro del tablero
                if 0 <= fila_final < 8 and 0 <= col_final < 8:
                    pieza_final = self.tablero[fila_final][col_final]
                    
                    if pieza_final == "--":  # Casilla vacía
                        movimientos.append(Movimiento((f, c), (fila_final, col_final), self.tablero))
                    elif pieza_final[0] == color_enemigo:  # Pieza enemiga
                        movimientos.append(Movimiento((f, c), (fila_final, col_final), self.tablero))
                        break
                    else:  # Pieza propia
                        break
                else:  # Fuera del tablero
                    break
    
    def generar_movimientos_reina(self, f, c, movimientos):
        """Genera todos los movimientos válidos para una reina en la posición (f, c)."""
        # La reina combina los movimientos de la torre y el alfil
        self.generar_movimientos_torre(f, c, movimientos)
        self.generar_movimientos_alfil(f, c, movimientos)
    
    def generar_movimientos_rey(self, f, c, movimientos):
        """Genera todos los movimientos válidos para un rey en la posición (f, c)."""
        direcciones = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        color_aliado = 'w' if self.turno_blanco else 'b'
        
        for df, dc in direcciones:
            fila_final = f + df
            col_final = c + dc
            
            # Verificar si la posición está dentro del tablero
            if 0 <= fila_final < 8 and 0 <= col_final < 8:
                pieza_final = self.tablero[fila_final][col_final]
                
                if pieza_final[0] != color_aliado:  # Casilla vacía o pieza enemiga
                    movimientos.append(Movimiento((f, c), (fila_final, col_final), self.tablero))


class Movimiento:
    """
    Clase para representar un movimiento de ajedrez.
    Mapea las coordenadas del tablero (fila, columna) a notación algebraica (e.g., e4)
    """
    
    # Mapeo de columnas a letras de notación algebraica
    filas_a_rangos = {0: "8", 1: "7", 2: "6", 3: "5", 4: "4", 5: "3", 6: "2", 7: "1"}
    cols_a_filas = {0: "a", 1: "b", 2: "c", 3: "d", 4: "e", 5: "f", 6: "g", 7: "h"}
    
    # Mapeo inverso para convertir de notación algebraica a coordenadas
    rangos_a_filas = {v: k for k, v in filas_a_rangos.items()}
    filas_a_cols = {v: k for k, v in cols_a_filas.items()}
    
    def __init__(self, posicion_inicio, posicion_fin, tablero):
        self.fila_inicio = posicion_inicio[0]
        self.col_inicio = posicion_inicio[1]
        self.fila_fin = posicion_fin[0]
        self.col_fin = posicion_fin[1]
        
        self.pieza_movida = tablero[self.fila_inicio][self.col_inicio]
        self.pieza_capturada = tablero[self.fila_fin][self.col_fin]
        
        self.id_movimiento = self.fila_inicio * 1000 + self.col_inicio * 100 + self.fila_fin * 10 + self.col_fin
    
    def __eq__(self, otro):
        """Método para comparar dos objetos Movimiento."""
        if isinstance(otro, Movimiento):
            return self.id_movimiento == otro.id_movimiento
        return False
    
    def get_notacion_algebraica(self):
        """Devuelve la notación algebraica del movimiento (e.g., e2e4)."""
        return self.cols_a_filas[self.col_inicio] + self.filas_a_rangos[self.fila_inicio] + \
               self.cols_a_filas[self.col_fin] + self.filas_a_rangos[self.fila_fin]


def dibujar_estado_juego(pantalla, estado, cuadros_validos):
    """Dibuja todos los elementos del juego actual."""
    dibujar_tablero(pantalla)
    resaltar_cuadros(pantalla, estado, cuadros_validos)
    dibujar_piezas(pantalla, estado.tablero)


def dibujar_tablero(pantalla):
    """Dibuja los cuadros del tablero de ajedrez."""
    colores = [pygame.Color(240, 217, 181), pygame.Color(181, 136, 99)]  # Colores claros y oscuros del tablero
    for f in range(DIMENSION):
        for c in range(DIMENSION):
            color = colores[(f + c) % 2]
            pygame.draw.rect(pantalla, color, pygame.Rect(c * TAMAÑO_CASILLA, f * TAMAÑO_CASILLA, TAMAÑO_CASILLA, TAMAÑO_CASILLA))


def resaltar_cuadros(pantalla, estado, cuadros_validos):
    """Resalta el cuadro seleccionado y los movimientos posibles."""
    if estado.pieza_seleccionada:
        f, c = estado.pieza_seleccionada
        
        # Resaltar cuadro seleccionado
        s = pygame.Surface((TAMAÑO_CASILLA, TAMAÑO_CASILLA))
        s.set_alpha(100)  # Transparencia
        s.fill(pygame.Color(AZUL_CLARO))
        pantalla.blit(s, (c * TAMAÑO_CASILLA, f * TAMAÑO_CASILLA))
        
        # Resaltar movimientos válidos
        s.fill(pygame.Color(VERDE_CLARO))
        for movimiento in cuadros_validos:
            pantalla.blit(s, (movimiento.col_fin * TAMAÑO_CASILLA, movimiento.fila_fin * TAMAÑO_CASILLA))


def dibujar_piezas(pantalla, tablero):
    """Dibuja las piezas en el tablero según el estado actual."""
    for f in range(DIMENSION):
        for c in range(DIMENSION):
            pieza = tablero[f][c]
            if pieza != "--":  # No es un espacio vacío
                pantalla.blit(IMAGENES[pieza], pygame.Rect(c * TAMAÑO_CASILLA, f * TAMAÑO_CASILLA, TAMAÑO_CASILLA, TAMAÑO_CASILLA))


def main():
    """Función principal que maneja la entrada del usuario y actualiza los gráficos."""
    cargar_imagenes()
    ejecutando = True
    estado = EstadoJuego()
    cuadros_validos = []  # Lista para almacenar los movimientos válidos de la pieza seleccionada
    pieza_seleccionada = False  # Variable para rastrear si el jugador ha seleccionado una pieza
    animacion_jugada = False  # Variable para rastrear si hay una animación de movimiento en curso
    
    while ejecutando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False
            
            # Manejador de eventos del ratón
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if not animacion_jugada:  # No permitir clic durante la animación
                    ubicacion = pygame.mouse.get_pos()  # (x, y) ubicación del ratón
                    col = ubicacion[0] // TAMAÑO_CASILLA
                    fila = ubicacion[1] // TAMAÑO_CASILLA
                    
                    if estado.pieza_seleccionada == (fila, col):  # El usuario clicó la misma casilla dos veces
                        estado.pieza_seleccionada = None
                        pieza_seleccionada = False
                        cuadros_validos = []
                    else:
                        estado.pieza_seleccionada = (fila, col)
                        pieza_seleccionada = True
                        
                        # Obtener los movimientos válidos para la pieza seleccionada
                        cuadros_validos = []
                        for movimiento in estado.movimientos_validos:
                            if movimiento.fila_inicio == fila and movimiento.col_inicio == col:
                                cuadros_validos.append(movimiento)
                        
                        # Si no hay movimientos válidos, deseleccionar la pieza
                        if len(cuadros_validos) == 0 and estado.tablero[fila][col] == "--":
                            estado.pieza_seleccionada = None
                            pieza_seleccionada = False
            
            # Manejador de eventos del ratón para soltar el botón
            elif evento.type == pygame.MOUSEBUTTONUP:
                if pieza_seleccionada and not animacion_jugada:
                    ubicacion = pygame.mouse.get_pos()
                    col = ubicacion[0] // TAMAÑO_CASILLA
                    fila = ubicacion[1] // TAMAÑO_CASILLA
                    
                    # Verificar si el movimiento a la nueva ubicación es válido
                    movimiento_valido = None
                    for m in cuadros_validos:
                        if m.fila_fin == fila and m.col_fin == col:
                            movimiento_valido = m
                            break
                    
                    if movimiento_valido:
                        estado.hacer_movimiento(movimiento_valido)
                        pieza_seleccionada = False
                        estado.pieza_seleccionada = None
                        cuadros_validos = []
                    else:
                        # Si el movimiento no es válido, mantener la selección de la pieza
                        estado.pieza_seleccionada = (estado.pieza_seleccionada[0], estado.pieza_seleccionada[1])
            
            # Manejador de eventos del teclado
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_z:  # Deshacer movimiento al presionar 'z'
                    estado.deshacer_movimiento()
                    pieza_seleccionada = False
                    estado.pieza_seleccionada = None
                    cuadros_validos = []
                    animacion_jugada = False
                if evento.key == pygame.K_r:  # Reiniciar juego al presionar 'r'
                    estado = EstadoJuego()
                    cuadros_validos = []
                    pieza_seleccionada = False
                    estado.pieza_seleccionada = None
                    animacion_jugada = False
        
        # Dibujar el estado del juego
        dibujar_estado_juego(pantalla, estado, cuadros_validos)
        reloj.tick(FPS)
        pygame.display.flip()


if __name__ == "__main__":
    main()