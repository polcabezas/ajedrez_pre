import tkinter as tk

class ChessGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Juego de Ajedrez")
        self.canvas_size = 640  # Tamaño total del canvas (640x640 píxeles)
        self.square_size = self.canvas_size // 8  # Tamaño de cada casilla
        self.canvas = tk.Canvas(self.root, width=self.canvas_size, height=self.canvas_size)
        self.canvas.pack()

        self.draw_board()   # Dibuja el tablero
        self.add_pieces()   # Coloca las piezas en el tablero

    def draw_board(self):
        # Dibuja 8 filas y 8 columnas de cuadrados, alternando colores
        for row in range(8):
            for col in range(8):
                x1 = col * self.square_size
                y1 = row * self.square_size
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size
                # Alterna colores: blanco para casilla clara y marrón para oscura
                fill_color = "white" if (row + col) % 2 == 0 else "sienna"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline="black")

    def add_pieces(self):
        # Representación de las piezas usando caracteres Unicode
        # Piezas blancas (en la parte inferior)
        white_back_row = ["♖", "♘", "♗", "♕", "♔", "♗", "♘", "♖"]
        # Piezas negras (en la parte superior)
        black_back_row = ["♜", "♞", "♝", "♛", "♚", "♝", "♞", "♜"]

        # Fuente utilizada para las piezas. Se recomienda usar una fuente que soporte caracteres Unicode.
        font = ("Arial", 36)

        for col in range(8):
            x = col * self.square_size + self.square_size / 2

            # Piezas negras
            # Fila superior (fila 0) con piezas principales
            self.canvas.create_text(x, self.square_size / 2, text=black_back_row[col], font=font)
            # Segunda fila (fila 1) con peones
            self.canvas.create_text(x, self.square_size + self.square_size / 2, text="♟︎", font=font)

            # Piezas blancas
            # Fila penúltima (fila 6) con peones
            self.canvas.create_text(x, 6 * self.square_size + self.square_size / 2, text="♙", font=font)
            # Fila inferior (fila 7) con piezas principales
            self.canvas.create_text(x, 7 * self.square_size + self.square_size / 2, text=white_back_row[col], font=font)

def main():
    root = tk.Tk()
    app = ChessGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
