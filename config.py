import pygame
import json
import os

# Archivo de configuración
CONFIG_FILE = "config.json"

# Resolución base de referencia (16:9)
BASE_WIDTH = 1920
BASE_HEIGHT = 1080
BASE_ASPECT_RATIO = BASE_WIDTH / BASE_HEIGHT

# Detectar resolución actual de la pantalla
pygame.init()
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h
SCREEN_ASPECT_RATIO = SCREEN_WIDTH / SCREEN_HEIGHT

# Calcular la proporción de escala
SCALE_X = SCREEN_WIDTH / BASE_WIDTH
SCALE_Y = SCREEN_HEIGHT / BASE_HEIGHT
SCALE_FACTOR = min(SCALE_X, SCALE_Y)  # Usamos el menor para evitar distorsión

# Calcular el área de juego efectiva
EFFECTIVE_WIDTH = int(BASE_WIDTH * SCALE_FACTOR)
EFFECTIVE_HEIGHT = int(BASE_HEIGHT * SCALE_FACTOR)

# Calcular offsets para centrar el contenido
OFFSET_X = (SCREEN_WIDTH - EFFECTIVE_WIDTH) // 2
OFFSET_Y = (SCREEN_HEIGHT - EFFECTIVE_HEIGHT) // 2

# Adaptar resoluciones y posiciones
def scale_value(value):
    return int(value * SCALE_FACTOR)

def scale_position_x(x):
    return OFFSET_X + int(x * SCALE_FACTOR)

def scale_position_y(y):
    return OFFSET_Y + int(y * SCALE_FACTOR)

def scale_size(width, height):
    return (int(width * SCALE_FACTOR), int(height * SCALE_FACTOR))

# Valores base sin escalar
GAME_WIDTH_BASE = 800
GAME_HEIGHT_BASE = 600
GAME2_WIDTH_BASE = 1000
GAME2_HEIGHT_BASE = 800
GAME3_WIDTH_BASE = 1000
GAME3_HEIGHT_BASE = 800
MENU_WIDTH_BASE = 800
MENU_HEIGHT_BASE = 600
INICIO_WIDTH_BASE = 532
INICIO_HEIGHT_BASE = 800
BLOCKERS_POSITION_BASE = 450
ENEMY_DEFAULT_POSITION_BASE = 65
ENEMY_MOVE_DOWN_BASE = 35

# Valores por defecto
DEFAULT_CONFIG = {
    "izquierda": pygame.K_LEFT,
    "derecha": pygame.K_RIGHT,
    "muteado": False,
    "screen_width": SCREEN_WIDTH,
    "screen_height": SCREEN_HEIGHT,
    # Nuevos controles para multijugador
    "izquierda2": pygame.K_a,
    "derecha2": pygame.K_d,
    "izquierda3": pygame.K_j,
    "derecha3": pygame.K_l
}

# Variables en memoria
Izquierda1 = DEFAULT_CONFIG["izquierda"]
Derecha1 = DEFAULT_CONFIG["derecha"]
MUTEADO = DEFAULT_CONFIG["muteado"]
# Nuevas variables para multijugador
Izquierda2 = DEFAULT_CONFIG["izquierda2"]
Derecha2 = DEFAULT_CONFIG["derecha2"]
Izquierda3 = DEFAULT_CONFIG["izquierda3"]
Derecha3 = DEFAULT_CONFIG["derecha3"]

def guardar_configuracion():
    try:
        config_data = {
            "izquierda": Izquierda1,
            "derecha": Derecha1,
            "muteado": MUTEADO,
            "screen_width": SCREEN_WIDTH,
            "screen_height": SCREEN_HEIGHT,
            # Guardar configuración de multijugador
            "izquierda2": Izquierda2,
            "derecha2": Derecha2,
            "izquierda3": Izquierda3,
            "derecha3": Derecha3
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config_data, f)
        print("✔ Configuración guardada")
    except Exception as e:
        print(f"❌ Error al guardar configuración: {e}")

def cargar_configuracion():
    global Izquierda1, Derecha1, MUTEADO, Izquierda2, Derecha2, Izquierda3, Derecha3
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config_data = json.load(f)
            Izquierda1 = config_data.get("izquierda", DEFAULT_CONFIG["izquierda"])
            Derecha1 = config_data.get("derecha", DEFAULT_CONFIG["derecha"])
            MUTEADO = config_data.get("muteado", DEFAULT_CONFIG["muteado"])
            # Cargar configuración de multijugador
            Izquierda2 = config_data.get("izquierda2", DEFAULT_CONFIG["izquierda2"])
            Derecha2 = config_data.get("derecha2", DEFAULT_CONFIG["derecha2"])
            Izquierda3 = config_data.get("izquierda3", DEFAULT_CONFIG["izquierda3"])
            Derecha3 = config_data.get("derecha3", DEFAULT_CONFIG["derecha3"])
            print("✔ Configuración cargada")
        else:
            print("ℹ No se encontró config.json, usando valores por defecto")
    except Exception as e:
        print(f"❌ Error al cargar configuración: {e}")

# Getters - Configuración jugador 1
def get_izquierda(): return Izquierda1
def get_derecha(): return Derecha1
def get_muteado(): return MUTEADO

# Getters - Configuración jugador 2
def get_izquierda2(): return Izquierda2
def get_derecha2(): return Derecha2

# Getters - Configuración jugador 3
def get_izquierda3(): return Izquierda3
def get_derecha3(): return Derecha3

# Getters - Resolución escalada
def get_game_width(): return scale_value(GAME_WIDTH_BASE)
def get_game_height(): return scale_value(GAME_HEIGHT_BASE)
def get_game2_width(): return scale_value(GAME2_WIDTH_BASE)
def get_game2_height(): return scale_value(GAME2_HEIGHT_BASE)
def get_game3_width(): return scale_value(GAME3_WIDTH_BASE)
def get_game3_height(): return scale_value(GAME3_HEIGHT_BASE)
def get_menu_width(): return scale_value(MENU_WIDTH_BASE)
def get_menu_height(): return scale_value(MENU_HEIGHT_BASE)
def get_inicio_width(): return scale_value(INICIO_WIDTH_BASE)
def get_inicio_height(): return scale_value(INICIO_HEIGHT_BASE)
def get_blockers_position(): return scale_value(BLOCKERS_POSITION_BASE)
def get_enemy_default_position(): return scale_value(ENEMY_DEFAULT_POSITION_BASE)
def get_enemy_move_down(): return scale_value(ENEMY_MOVE_DOWN_BASE)
def get_scale_factor(): return SCALE_FACTOR
def get_offset_x(): return OFFSET_X
def get_offset_y(): return OFFSET_Y

# Setters - Jugador 1
def set_izquierda(tecla):
    global Izquierda1
    Izquierda1 = tecla
    guardar_configuracion()

def set_derecha(tecla):
    global Derecha1
    Derecha1 = tecla
    guardar_configuracion()

# Setters - Jugador 2
def set_izquierda2(tecla):
    global Izquierda2
    Izquierda2 = tecla
    guardar_configuracion()

def set_derecha2(tecla):
    global Derecha2
    Derecha2 = tecla
    guardar_configuracion()

# Setters - Jugador 3
def set_izquierda3(tecla):
    global Izquierda3
    Izquierda3 = tecla
    guardar_configuracion()

def set_derecha3(tecla):
    global Derecha3
    Derecha3 = tecla
    guardar_configuracion()

def set_muteado(valor):
    global MUTEADO
    MUTEADO = valor
    guardar_configuracion()

def toggle_muteado():
    global MUTEADO
    MUTEADO = not MUTEADO
    guardar_configuracion()
    return MUTEADO

# Getters de tamaños escalados (pares ancho, alto)
def get_scaled_game_size():
    return scale_value(GAME_WIDTH_BASE), scale_value(GAME_HEIGHT_BASE)

def get_scaled_game2_size():
    return scale_value(GAME2_WIDTH_BASE), scale_value(GAME2_HEIGHT_BASE)

def get_scaled_game3_size():
    return scale_value(GAME3_WIDTH_BASE), scale_value(GAME3_HEIGHT_BASE)

def get_scaled_menu_size():
    return scale_value(MENU_WIDTH_BASE), scale_value(MENU_HEIGHT_BASE)

def get_scaled_inicio_size():
    return scale_value(INICIO_WIDTH_BASE), scale_value(INICIO_HEIGHT_BASE)

def get_game_area():
    return pygame.Rect(OFFSET_X, OFFSET_Y, EFFECTIVE_WIDTH, EFFECTIVE_HEIGHT)

# Cargar configuración al inicio
cargar_configuracion()