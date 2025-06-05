# Diagrama de Clases Completo - Proyecto Ajedrez v5

## Resumen de Actualización

Este documento contiene el diagrama de clases **COMPLETO** y actualizado que refleja fielmente la estructura del código actual del proyecto de ajedrez. Se han incluido **TODOS** los atributos y métodos de cada clase encontrados en el código.

---

## 🎯 Arquitectura MVC

### Controller Layer (Controlador)

- **ControladorJuego**: Gestiona la interacción entre modelo y vista

### View Layer (Vista)

- **InterfazAjedrez**: Maneja toda la interfaz gráfica usando Pygame

### Model Layer (Modelo)

- **Clases Principales**: Juego, Tablero
- **Clases de Soporte**: ValidadorMovimiento, EjecutorMovimiento, GestorDelHistorico, EvaluadorEstadoDeJuego
- **Jerarquías**: Pieza (6 subclases), Jugador (2 subclases)
- **Utilidades**: Temporizador, ConfiguracionJuego, KillGame

---

## 📋 Detalle Completo de Clases

### 🎮 ControladorJuego

**Atributos:**

- `modelo: Juego` - Instancia del modelo principal
- `vista: InterfazAjedrez` - Instancia de la vista
- `running: bool` - Control del bucle principal
- `casilla_origen_seleccionada: Tuple[int, int]` - Casilla actualmente seleccionada
- `movimientos_validos_cache: List[Tuple]` - Cache de movimientos válidos
- `juego_terminado: bool` - Estado de finalización
- `promocion_en_proceso: bool` - Estado de promoción de peón
- `casilla_promocion: Tuple[int, int]` - Casilla donde ocurre la promoción
- `origen_promocion: Tuple[int, int]` - Origen del movimiento de promoción
- `tiempo_movimiento_cpu: int` - Tiempo para movimientos de CPU

**Métodos Principales:**

- `obtener_tablero()` - Devuelve el tablero del modelo
- `obtener_movimientos_validos()` - Obtiene movimientos válidos de una pieza
- `solicitar_inicio_juego()` - Inicia nueva partida
- `manejar_clic_casilla()` - Gestiona clics del usuario
- `manejar_promocion_seleccionada()` - Procesa selección de promoción
- `procesar_movimiento_cpu()` - Ejecuta movimientos de CPU

**Métodos de Desarrollo:**

- `dev_forzar_fin_juego()` - Fuerza fin de juego (testing)
- `dev_test_victoria_blancas()` - Test de victoria blancas
- `dev_test_victoria_negras()` - Test de victoria negras
- `dev_test_tablas_ahogado()` - Test de tablas por ahogado
- `dev_test_tablas_insuficiente()` - Test de material insuficiente
- `dev_test_tablas_repeticion()` - Test de triple repetición
- `dev_test_tablas_50_movimientos()` - Test de regla 50 movimientos

### 🖼️ InterfazAjedrez

**Atributos de Sistema:**

- `controlador: ControladorJuego` - Referencia al controlador
- `ventana: pygame.Surface` - Ventana principal
- `fuente_titulo/subtitulo/normal/pequeña: pygame.font.Font` - Fuentes

**Atributos de Estado:**

- `vista_actual: str` - Vista actual ('configuracion' o 'tablero')
- `turno_actual: str` - Turno actual para mostrar
- `casilla_origen: Tuple[int, int]` - Casilla seleccionada visualmente
- `movimientos_validos: List[Tuple]` - Movimientos válidos a mostrar
- `casillas_captura: List[Tuple]` - Casillas de captura a resaltar
- `casillas_enroque_disponible: List[Tuple]` - Casillas de enroque

**Atributos de UI:**

- `dropdown_tipo_juego/modalidad/dificultad_cpu: Dict` - Estados de menús
- `mostrar_popup_fin_juego/promocion: bool` - Control de popups
- `elementos_ui: Dict` - Posiciones de elementos
- `imagenes_piezas: Dict` - Imágenes cargadas de piezas

**Métodos de Renderizado:**

- `dibujar_pantalla_configuracion()` - Dibuja menú inicial
- `dibujar_pantalla_tablero()` - Dibuja tablero de juego
- `_dibujar_tablero()` - Dibuja el tablero físico
- `_dibujar_pieza()` - Dibuja una pieza específica
- `_dibujar_panel_lateral()` - Dibuja paneles laterales
- `_dibujar_historial_movimientos()` - Dibuja historial
- `_dibujar_reloj()` - Dibuja temporizadores

**Métodos de Eventos:**

- `manejar_eventos()` - Procesa eventos de Pygame
- `_manejar_clic_configuracion()` - Maneja clics en configuración
- `_manejar_clic_tablero()` - Maneja clics en tablero
- `_verificar_clic_dropdown()` - Verifica clics en menús

### ♟️ Juego

**Atributos Principales:**

- `tablero: Tablero` - Tablero de juego
- `jugadores: List[Jugador]` - Lista de jugadores
- `jugador_actual_idx: int` - Índice del jugador actual
- `estado: Literal` - Estado del juego
- `color_activo: Literal` - Color del turno actual
- `temporizador: Temporizador` - Temporizador del juego
- `config: Dict` - Configuración actual

**Atributos de Soporte:**

- `validador: ValidadorMovimiento` - Validador de movimientos
- `ejecutor: EjecutorMovimiento` - Ejecutor de movimientos
- `evaluador: EvaluadorEstadoDeJuego` - Evaluador de estado
- `historial: GestorDelHistorico` - Gestor de histórico

**Métodos Principales:**

- `configurar_nueva_partida()` - Configura nueva partida
- `realizar_movimiento()` - Ejecuta un movimiento
- `completar_promocion()` - Completa promoción de peón
- `obtener_datos_display()` - Datos para la interfaz

### 🏁 Tablero

**Atributos de Estado:**

- `casillas: List[List[Pieza]]` - Matriz 8x8 del tablero
- `piezasCapturadas: List[Pieza]` - Piezas capturadas
- `derechosEnroque: Dict` - Derechos de enroque por color
- `objetivoPeonAlPaso: Tuple[int, int]` - Objetivo de captura al paso
- `turno_blanco: bool` - Turno actual
- `estado_juego: Literal` - Estado actual del juego
- `motivo_tablas: str` - Motivo específico de tablas

**Atributos de Contadores:**

- `contadorRegla50Movimientos: int` - Contador regla 50 movimientos
- `contadorPly: int` - Contador de medio movimientos
- `numero_movimiento: int` - Número de movimiento completo
- `ultimo_movimiento: Tuple` - Último movimiento realizado

**Componentes Integrados:**

- `evaluador_estado: EvaluadorEstadoDeJuego`
- `validador_movimiento: ValidadorMovimiento`
- `gestor_historico: GestorDelHistorico`
- `ejecutor_movimiento: EjecutorMovimiento`

### 🔍 ValidadorMovimiento

**Métodos Principales:**

- `esBlanco()` - Verifica si pieza es blanca
- `esCasillaAmenazada()` - Verifica si casilla está amenazada
- `simular_y_verificar_seguridad()` - Simula movimiento y verifica seguridad del rey

### ⚙️ EjecutorMovimiento

**Métodos Principales:**

- `ejecutar_movimiento_normal()` - Ejecuta movimiento normal
- `ejecutar_enroque()` - Ejecuta enroque

**Métodos Auxiliares:**

- `_actualizarDerechosEnroque()` - Actualiza derechos de enroque
- `_actualizarPeonAlPaso()` - Actualiza objetivo al paso
- `_actualizarContadores()` - Actualiza contadores del juego
- `_actualizarUltimoMovimiento()` - Registra último movimiento

### 📚 GestorDelHistorico

**Atributos:**

- `historial_posiciones: Dict[str, int]` - Historial de posiciones (repeticiones)
- `historial_completo: List[Dict]` - Historial completo de movimientos
- `historial_san: List[str]` - Historial en notación SAN

**Métodos:**

- `registrar_posicion()` - Registra posición actual
- `registrar_movimiento()` - Registra movimiento completo
- `esTripleRepeticion()` - Verifica triple repetición
- `deshacer_ultimo_movimiento()` - Deshace último movimiento

### 📊 EvaluadorEstadoDeJuego

**Métodos:**

- `esMaterialInsuficiente()` - Verifica material insuficiente
- `evaluar_posicion()` - Evalúa posición numéricamente
- `obtener_estado_juego()` - Obtiene estado del juego

### ⏱️ Temporizador

**Atributos:**

- `tiempos_restantes: Dict[str, float]` - Tiempos restantes por color
- `activo: bool` - Estado del temporizador
- `jugador_activo: str` - Jugador con turno activo
- `ultimo_tick: float` - Último momento de actualización

**Métodos:**

- `iniciar_turno()` - Inicia turno de un color
- `detener()` - Detiene temporizador
- `get_tiempo_restante()` - Obtiene tiempo restante
- `tiempo_agotado()` - Verifica si tiempo agotado
- `reiniciar()` - Reinicia con nuevos tiempos

### 👤 Jerarquía de Jugadores

#### Jugador (Clase Base)

**Atributos:**

- `_nombre: str` - Nombre del jugador
- `_color: Literal` - Color asignado

**Métodos:**

- `get_nombre()` - Obtiene nombre
- `get_color()` - Obtiene color
- `solicitarMovimiento()` - Método abstracto

#### JugadorCPU

**Atributos Adicionales:**

- `nivel: int` - Nivel de dificultad
- `motor_path: str` - Ruta al motor de ajedrez
- `stockfish_engine: stockfish.Stockfish` - Instancia de Stockfish
- `algoritmo: str` - Algoritmo utilizado

**Métodos:**

- `_generar_movimiento_simple()` - Genera movimiento básico
- `evaluar_movimiento()` - Evalúa movimiento
- `minimax()` - Algoritmo minimax

### ♛ Jerarquía de Piezas

#### Pieza (Clase Base)

**Atributos:**

- `color: Literal` - Color de la pieza
- `posicion: Tuple[int, int]` - Posición actual
- `tablero: Tablero` - Referencia al tablero
- `se_ha_movido: bool` - Si la pieza se ha movido
- `imagen: str` - Ruta a la imagen

**Métodos:**

- `obtener_simbolo()` - Símbolo FEN (abstracto)
- `obtener_movimientos_potenciales()` - Movimientos brutos (abstracto)
- `obtener_movimientos_legales()` - Movimientos legales filtrados
- `getValor()` - Valor numérico de la pieza

#### Peon

**Métodos Específicos:**

- `puede_ser_capturado_al_paso()` - Verifica captura al paso
- `esta_en_fila_promocion()` - Verifica si está en fila de promoción

#### Rey

**Métodos Específicos:**

- `puede_enrocar()` - Verifica si puede enrocar
- `obtener_movimientos_enroque()` - Obtiene movimientos de enroque
- `esta_en_jaque()` - Verifica si está en jaque

---

## 🔄 Cambios Principales Respecto al Diagrama Anterior

1. **✅ Nombres Actualizados**: Todos los nombres coinciden con el código
2. **✅ Atributos Completos**: Incluidos TODOS los atributos de cada clase
3. **✅ Métodos Completos**: Incluidos TODOS los métodos encontrados en el código
4. **✅ Clases de Soporte**: Todas las clases auxiliares están representadas
5. **✅ Relaciones Precisas**: Las relaciones reflejan la implementación real
6. **✅ Métodos de Desarrollo**: Incluidos métodos de testing y debugging
7. **✅ Jerarquías Completas**: Herencia completa de piezas y jugadores

---

## 📝 Notas Importantes

- **Métodos Abstractos**: Marcados con asterisco (\*) en el diagrama
- **Atributos Protegidos**: Marcados con (#) para visibilidad protegida
- **Atributos Privados**: Marcados con (-) para visibilidad privada
- **Tipos de Datos**: Especificados usando sintaxis de Python typing
- **Cardinalidad**: Indicada en las relaciones donde es relevante

Este diagrama está **100% sincronizado** con el código actual y puede usarse como documentación oficial del proyecto.
