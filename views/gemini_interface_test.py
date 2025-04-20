import pygame
import sys

# --- Constantes ---
WIDTH, HEIGHT = 640, 640  # Dimensiones de la ventana (múltiplo de 8)
DIMENSION = 8             # Dimensiones del tablero (8x8)
SQ_SIZE = HEIGHT // DIMENSION # Tamaño de cada casilla

# Colores RGB
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_SQUARE = (238, 238, 210) # Color casilla clara
DARK_SQUARE = (118, 150, 86)   # Color casilla oscura
HIGHLIGHT_COLOR = (255, 255, 0, 150) # Amarillo semitransparente para resaltar

# --- Carga de Imágenes (Requiere archivos de imagen) ---
# Crea un diccionario para almacenar las imágenes de las piezas.
# Las claves serán 'wP', 'wR', 'wN', 'wB', 'wQ', 'wK' para blancas
# y 'bP', 'bR', 'bN', 'bB', 'bQ', 'bK' para negras.
# ¡¡IMPORTANTE!! Necesitas tener archivos de imagen para las piezas
# en una carpeta llamada 'images' (o cambiar la ruta).
# Los nombres de archivo deben coincidir (p.ej., 'wP.png', 'bR.png').
# Si no tienes imágenes, se mostrará texto como placeholder.
IMAGES = {}
PIECE_NAMES = ['Peon blanco', 'Torre blanca', 'Caballo blanco', 'Alfil blanco', 'Reina blanca', 'Rey blanco', 'Peon Negro', 'Torre negra', 'Caballo negro', 'Alfil negro', 'Reina negra', 'Rey negro']
IMAGE_PATH = 'assets/imagenes_piezas/' # Cambia si tus imágenes están en otro lugar

def load_images():
    """Carga las imágenes de las piezas desde los archivos."""
    print("Cargando imágenes...")
    images_found = True
    for piece in PIECE_NAMES:
        try:
            # Intenta cargar la imagen y escalarla al tamaño de la casilla
            image = pygame.image.load(f"{IMAGE_PATH}{piece}.png")
            IMAGES[piece] = pygame.transform.scale(image, (SQ_SIZE, SQ_SIZE))
            print(f"  - Cargada: {piece}.png")
        except pygame.error as e:
            print(f"  - Error cargando {piece}.png: {e}")
            IMAGES[piece] = None # Marcar como no encontrada
            images_found = False
    if not images_found:
        print("\n¡Advertencia! No se encontraron todas las imágenes.")
        print("Se mostrarán letras en lugar de las imágenes faltantes.")
        print(f"Asegúrate de tener las imágenes en la carpeta: '{IMAGE_PATH}'")
        print("Nombres esperados: wP.png, wR.png, ..., bK.png\n")
    else:
        print("¡Imágenes cargadas correctamente!\n")


# --- Tablero Lógico ---
# Representación interna del tablero. Las minúsculas son negras, mayúsculas blancas.
# 'P' peón, 'R' torre, 'N' caballo, 'B' alfil, 'Q' reina, 'K' rey, '--' vacío
initial_board_setup = [
    ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
    ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
    ["--", "--", "--", "--", "--", "--", "--", "--"],
    ["--", "--", "--", "--", "--", "--", "--", "--"],
    ["--", "--", "--", "--", "--", "--", "--", "--"],
    ["--", "--", "--", "--", "--", "--", "--", "--"],
    ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
    ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
]

# --- Funciones de Dibujo ---
def draw_board(screen):
    """Dibuja las casillas del tablero."""
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            # Determina el color de la casilla
            color = LIGHT_SQUARE if (r + c) % 2 == 0 else DARK_SQUARE
            # Dibuja el rectángulo para la casilla
            pygame.draw.rect(screen, color, pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def draw_pieces(screen, board, font):
    """Dibuja las piezas en el tablero."""
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":  # Si no es una casilla vacía
                image = IMAGES.get(piece) # Intenta obtener la imagen cargada
                if image:
                    # Dibuja la imagen de la pieza centrada en la casilla
                    screen.blit(image, pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
                else:
                    # Si no hay imagen, dibuja el texto de la pieza
                    piece_text = font.render(piece, True, BLACK if piece.startswith('b') else WHITE)
                    text_rect = piece_text.get_rect(center=(c * SQ_SIZE + SQ_SIZE // 2, r * SQ_SIZE + SQ_SIZE // 2))
                    screen.blit(piece_text, text_rect)

def highlight_square(screen, row, col):
    """Dibuja un resaltado en la casilla seleccionada."""
    # Crea una superficie semitransparente para el resaltado
    highlight_surface = pygame.Surface((SQ_SIZE, SQ_SIZE), pygame.SRCALPHA)
    highlight_surface.fill(HIGHLIGHT_COLOR)
    screen.blit(highlight_surface, (col * SQ_SIZE, row * SQ_SIZE))


# --- Función Principal ---
def main():
    """Función principal que ejecuta el juego."""
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Interfaz de Ajedrez Simple")
    clock = pygame.time.Clock()

    # Carga las imágenes (o prepara para mostrar texto si fallan)
    load_images()
    font = pygame.font.SysFont('monospace', 30, bold=True) # Fuente para texto si no hay imagen

    # Estado del juego
    board = [row[:] for row in initial_board_setup] # Copia profunda del tablero inicial
    selected_square = None  # Tupla (fila, columna) de la casilla seleccionada
    selected_piece = None   # Pieza en la casilla seleccionada ('wP', 'bR', etc.)
    player_clicks = []      # Almacena los clics del jugador (máximo 2: origen, destino)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Manejo de clics del ratón
            elif event.type == pygame.MOUSEBUTTONDOWN:
                location = pygame.mouse.get_pos()  # (x, y) posición del ratón
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE

                # Lógica de selección/movimiento simple
                if selected_square == (row, col): # Clic en la misma casilla seleccionada
                    selected_square = None # Deseleccionar
                    selected_piece = None
                    player_clicks = []
                else:
                    piece_clicked = board[row][col]
                    if piece_clicked != "--": # Si hay una pieza en la casilla clicada
                        # Si ya había una pieza seleccionada, esto podría ser una captura
                        # (pero por ahora, simplemente seleccionamos la nueva)
                        selected_square = (row, col)
                        selected_piece = piece_clicked
                        player_clicks = [selected_square] # Primer clic (origen)
                        print(f"Seleccionada: {selected_piece} en ({row}, {col})")
                    elif selected_piece: # Si no hay pieza pero ya teníamos una seleccionada (segundo clic)
                        player_clicks.append((row, col)) # Segundo clic (destino)
                        print(f"Moviendo {selected_piece} de {player_clicks[0]} a {player_clicks[1]}")

                        # --- Lógica de Movimiento (Muy Básica - SIN VALIDACIÓN) ---
                        start_row, start_col = player_clicks[0]
                        end_row, end_col = player_clicks[1]

                        # Mover la pieza en el tablero lógico
                        board[end_row][end_col] = selected_piece
                        board[start_row][start_col] = "--" # Vaciar casilla de origen

                        # Resetear selección
                        selected_square = None
                        selected_piece = None
                        player_clicks = []

        # --- Dibujo ---
        screen.fill(BLACK) # Limpia la pantalla (opcional si siempre dibujas el tablero completo)
        draw_board(screen)

        # Resaltar casilla seleccionada (si hay alguna)
        if selected_square:
            highlight_square(screen, selected_square[0], selected_square[1])

        draw_pieces(screen, board, font) # Dibuja las piezas encima del tablero

        # --- Actualizar Pantalla ---
        pygame.display.flip()
        clock.tick(60)  # Limita los FPS a 60

    pygame.quit()
    sys.exit()

# --- Punto de Entrada ---
if __name__ == "__main__":
    main()