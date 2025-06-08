import pygame
import sys
import os
import config
from Space_Invaders import *  # Asegúrate de que este archivo esté en la misma carpeta
import Space_Invaders_2 as nm

# =============== CONFIGURAR VENTANA CENTRADA ==================
os.environ['SDL_VIDEO_CENTERED'] = '1'

# =============== INICIALIZAR PYGAME ============================
pygame.init()

# Cargar fuente personalizada desde la carpeta Letras
FUENTE = pygame.font.Font("Letras/space_invaders.ttf", int(20 * config.SCALE_FACTOR))
FUENTE_NEGRITA = pygame.font.Font("Letras/space_invaders.ttf", int(20 * config.SCALE_FACTOR))
FUENTE_NEGRITA.set_bold(True)

# =============== PRIMERA PANTALLA - IMAGEN INICIAL =============
INICIO_WIDTH = config.get_inicio_width()
INICIO_HEIGHT = config.get_inicio_height()
PANTALLA = pygame.display.set_mode((INICIO_WIDTH, INICIO_HEIGHT))
pygame.display.set_caption("Space Invaders - Inicio")

imagen_inicio = pygame.image.load("Images/image_init.jpeg")
imagen_inicio = pygame.transform.scale(imagen_inicio, (INICIO_WIDTH, INICIO_HEIGHT))

def pantalla_inicio():
    # ========== Crear los textos ==========
    texto_original = FUENTE.render("The Original Game".title(), True, (255, 238, 0))
    texto_produced = FUENTE_NEGRITA.render("Produced By Fuchs".title(), True, (255, 255, 255))
    texto_licencia = FUENTE_NEGRITA.render("Licenced By Huergo Inst.".title(), True, (255, 255, 255))
    texto_presionar = FUENTE.render("Push Start Button".title(), True, (255, 238, 0))

    # ========== Posicionar los textos ==========
    # Usamos las funciones de escala para adaptar las posiciones
    rect_original = texto_original.get_rect(center=(scale_value(INICIO_WIDTH // 2), scale_value(222)))
    rect_produced = texto_produced.get_rect(center=(scale_value(INICIO_WIDTH // 2), scale_value(685)))
    rect_licencia = texto_licencia.get_rect(center=(scale_value(INICIO_WIDTH // 2), scale_value(715)))
    rect_presionar = texto_presionar.get_rect(center=(scale_value(INICIO_WIDTH // 2), scale_value(300)))

    esperando = True
    while esperando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                esperando = False

        PANTALLA.blit(imagen_inicio, (0, 0))
        PANTALLA.blit(texto_original, rect_original)
        PANTALLA.blit(texto_presionar, rect_presionar)
        PANTALLA.blit(texto_produced, rect_produced)
        PANTALLA.blit(texto_licencia, rect_licencia)
        pygame.display.flip()

# =============== MENÚ PRINCIPAL ===============================
ANCHO_MENU = config.get_menu_width()
ALTO_MENU = config.get_menu_height()

# Colores
BLANCO = (255, 255, 255)
VERDE = (0, 255, 0)
AZUL = (0, 0, 255)
ROJO = (255, 0, 0)
AMARILLO = (255, 255, 0)

# Fondo de la segunda pantalla
imagen_menu = pygame.image.load("Images/image_second.webp")
imagen_menu = pygame.transform.scale(imagen_menu, (ANCHO_MENU, ALTO_MENU))

def dibujar_boton(texto, x, y, ancho, alto, color_base, color_hover, pos_mouse):
    # Escalar las posiciones y dimensiones
    x = scale_value(x)
    y = scale_value(y)
    ancho = scale_value(ancho)
    alto = scale_value(alto)
    
    rect = pygame.Rect(x, y, ancho, alto)
    color = color_hover if rect.collidepoint(pos_mouse) else color_base
    pygame.draw.rect(PANTALLA, color, rect, border_radius=10)
    
    texto_render = FUENTE.render(texto, True, BLANCO)
    texto_rect = texto_render.get_rect(center=rect.center)
    PANTALLA.blit(texto_render, texto_rect)
    
    return rect

def abrir_menu_settings(): 
    corriendo = True
    cambiando_tecla = None
    
    # Escalado de botones y elementos
    x_boton = scale_position_x(300)
    w_boton = scale_value(250)  # Aumentado para que quepa el texto
    h_boton = scale_value(40)
    spacing = scale_value(60)  # Espacio entre botones
    
    # Título
    fuente_titulo = pygame.font.SysFont(None, scale_value(48))
    fuente = pygame.font.SysFont(None, scale_value(36))
    
    # Crear rectángulos para todos los botones
    mute_rect = pygame.Rect(x_boton, scale_position_y(50), w_boton, h_boton)
    
    # Jugador 1
    p1_titulo_rect = pygame.Rect(x_boton, scale_position_y(110), w_boton, h_boton)
    p1_izquierda_rect = pygame.Rect(x_boton, scale_position_y(150), w_boton, h_boton)
    p1_derecha_rect = pygame.Rect(x_boton, scale_position_y(190), w_boton, h_boton)
    
    # Jugador 2
    p2_titulo_rect = pygame.Rect(x_boton, scale_position_y(250), w_boton, h_boton)
    p2_izquierda_rect = pygame.Rect(x_boton, scale_position_y(290), w_boton, h_boton)
    p2_derecha_rect = pygame.Rect(x_boton, scale_position_y(330), w_boton, h_boton)
    
    # Jugador 3
    p3_titulo_rect = pygame.Rect(x_boton, scale_position_y(390), w_boton, h_boton)
    p3_izquierda_rect = pygame.Rect(x_boton, scale_position_y(430), w_boton, h_boton)
    p3_derecha_rect = pygame.Rect(x_boton, scale_position_y(470), w_boton, h_boton)
    
    # Botón volver
    volver_rect = pygame.Rect(x_boton, scale_position_y(530), w_boton, h_boton)

    while corriendo:
        PANTALLA.fill((30, 30, 30))
        pos_mouse = pygame.mouse.get_pos()

        # Obtener nombres de teclas
        mute_texto = f"Mute: {'ON' if config.get_muteado() else 'OFF'}"
        p1_tecla_izq = pygame.key.name(config.get_izquierda()).upper()
        p1_tecla_der = pygame.key.name(config.get_derecha()).upper()
        p2_tecla_izq = pygame.key.name(config.get_izquierda2()).upper()
        p2_tecla_der = pygame.key.name(config.get_derecha2()).upper()
        p3_tecla_izq = pygame.key.name(config.get_izquierda3()).upper()
        p3_tecla_der = pygame.key.name(config.get_derecha3()).upper()

        # Colores para los distintos botones
        mute_color = (200, 0, 0) if mute_rect.collidepoint(pos_mouse) else (150, 0, 0)
        
        # Colores de jugador 1 (Azul)
        p1_titulo_color = (0, 100, 200)
        p1_izq_color = (0, 150, 200) if p1_izquierda_rect.collidepoint(pos_mouse) else (0, 100, 150)
        p1_der_color = (0, 150, 200) if p1_derecha_rect.collidepoint(pos_mouse) else (0, 100, 150)
        
        # Colores de jugador 2 (Verde)
        p2_titulo_color = (0, 150, 0)
        p2_izq_color = (0, 200, 0) if p2_izquierda_rect.collidepoint(pos_mouse) else (0, 150, 0)
        p2_der_color = (0, 200, 0) if p2_derecha_rect.collidepoint(pos_mouse) else (0, 150, 0)
        
        # Colores de jugador 3 (Rojo)
        p3_titulo_color = (150, 0, 0)
        p3_izq_color = (200, 0, 0) if p3_izquierda_rect.collidepoint(pos_mouse) else (150, 0, 0)
        p3_der_color = (200, 0, 0) if p3_derecha_rect.collidepoint(pos_mouse) else (150, 0, 0)
        
        # Color botón volver
        volver_color = (150, 150, 255) if volver_rect.collidepoint(pos_mouse) else (100, 100, 255)

        # Resaltar el botón activo durante la asignación de teclas
        if cambiando_tecla == "p1_izq":
            p1_izq_color = (255, 255, 0)
        elif cambiando_tecla == "p1_der":
            p1_der_color = (255, 255, 0)
        elif cambiando_tecla == "p2_izq":
            p2_izq_color = (255, 255, 0)
        elif cambiando_tecla == "p2_der":
            p2_der_color = (255, 255, 0)
        elif cambiando_tecla == "p3_izq":
            p3_izq_color = (255, 255, 0)
        elif cambiando_tecla == "p3_der":
            p3_der_color = (255, 255, 0)

        # Título de la pantalla
        titulo = fuente_titulo.render("CONFIGURACIÓN", True, (255, 255, 255))
        PANTALLA.blit(titulo, (scale_position_x(280), scale_position_y(6)))

        # Dibujar botón mute
        pygame.draw.rect(PANTALLA, mute_color, mute_rect)
        PANTALLA.blit(fuente.render(mute_texto, True, (255, 255, 255)), (mute_rect.x + scale_value(10), mute_rect.y + scale_value(5)))

        # Dibujar sección Jugador 1
        pygame.draw.rect(PANTALLA, p1_titulo_color, p1_titulo_rect)
        PANTALLA.blit(fuente.render("JUGADOR 1", True, (255, 255, 255)), (p1_titulo_rect.x + scale_value(10), p1_titulo_rect.y + scale_value(5)))
        
        pygame.draw.rect(PANTALLA, p1_izq_color, p1_izquierda_rect)
        PANTALLA.blit(fuente.render(f"Izquierda: {p1_tecla_izq}", True, (255, 255, 255)), (p1_izquierda_rect.x + scale_value(10), p1_izquierda_rect.y + scale_value(5)))
        
        pygame.draw.rect(PANTALLA, p1_der_color, p1_derecha_rect)
        PANTALLA.blit(fuente.render(f"Derecha: {p1_tecla_der}", True, (255, 255, 255)), (p1_derecha_rect.x + scale_value(10), p1_derecha_rect.y + scale_value(5)))

        # Dibujar sección Jugador 2
        pygame.draw.rect(PANTALLA, p2_titulo_color, p2_titulo_rect)
        PANTALLA.blit(fuente.render("JUGADOR 1", True, (255, 255, 255)), (p2_titulo_rect.x + scale_value(10), p2_titulo_rect.y + scale_value(5)))
        
        pygame.draw.rect(PANTALLA, p2_izq_color, p2_izquierda_rect)
        PANTALLA.blit(fuente.render(f"Izquierda: {p2_tecla_izq}", True, (255, 255, 255)), (p2_izquierda_rect.x + scale_value(10), p2_izquierda_rect.y + scale_value(5)))
        
        pygame.draw.rect(PANTALLA, p2_der_color, p2_derecha_rect)
        PANTALLA.blit(fuente.render(f"Derecha: {p2_tecla_der}", True, (255, 255, 255)), (p2_derecha_rect.x + scale_value(10), p2_derecha_rect.y + scale_value(5)))

        # Dibujar sección Jugador 3
        pygame.draw.rect(PANTALLA, p3_titulo_color, p3_titulo_rect)
        PANTALLA.blit(fuente.render("JUGADOR 2", True, (255, 255, 255)), (p3_titulo_rect.x + scale_value(10), p3_titulo_rect.y + scale_value(5)))
        
        pygame.draw.rect(PANTALLA, p3_izq_color, p3_izquierda_rect)
        PANTALLA.blit(fuente.render(f"Izquierda: {p3_tecla_izq}", True, (255, 255, 255)), (p3_izquierda_rect.x + scale_value(10), p3_izquierda_rect.y + scale_value(5)))
        
        pygame.draw.rect(PANTALLA, p3_der_color, p3_derecha_rect)
        PANTALLA.blit(fuente.render(f"Derecha: {p3_tecla_der}", True, (255, 255, 255)), (p3_derecha_rect.x + scale_value(10), p3_derecha_rect.y + scale_value(5)))

        # Botón volver
        pygame.draw.rect(PANTALLA, volver_color, volver_rect)
        PANTALLA.blit(fuente.render("Volver", True, (255, 255, 255)), (volver_rect.x + scale_value(80), volver_rect.y + scale_value(5)))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if mute_rect.collidepoint(event.pos):
                    config.toggle_muteado()
                # Jugador 1
                elif p1_izquierda_rect.collidepoint(event.pos):
                    cambiando_tecla = "p1_izq"
                elif p1_derecha_rect.collidepoint(event.pos):
                    cambiando_tecla = "p1_der"
                # Jugador 2
                elif p2_izquierda_rect.collidepoint(event.pos):
                    cambiando_tecla = "p2_izq"
                elif p2_derecha_rect.collidepoint(event.pos):
                    cambiando_tecla = "p2_der"
                # Jugador 3
                elif p3_izquierda_rect.collidepoint(event.pos):
                    cambiando_tecla = "p3_izq"
                elif p3_derecha_rect.collidepoint(event.pos):
                    cambiando_tecla = "p3_der"
                # Botón volver
                elif volver_rect.collidepoint(event.pos):
                    corriendo = False
            elif event.type == pygame.KEYDOWN:
                if cambiando_tecla == "p1_izq":
                    config.set_izquierda(event.key)
                    cambiando_tecla = None
                elif cambiando_tecla == "p1_der":
                    config.set_derecha(event.key)
                    cambiando_tecla = None
                elif cambiando_tecla == "p2_izq":
                    config.set_izquierda2(event.key)
                    cambiando_tecla = None
                elif cambiando_tecla == "p2_der":
                    config.set_derecha2(event.key)
                    cambiando_tecla = None
                elif cambiando_tecla == "p3_izq":
                    config.set_izquierda3(event.key)
                    cambiando_tecla = None
                elif cambiando_tecla == "p3_der":
                    config.set_derecha3(event.key)
                    cambiando_tecla = None
                elif event.key == pygame.K_ESCAPE:
                    if cambiando_tecla:
                        cambiando_tecla = None
                    else:
                        corriendo = False

def menu_principal():
    global PANTALLA
    PANTALLA = pygame.display.set_mode((ANCHO_MENU, ALTO_MENU))
    pygame.display.set_caption("Space Invaders - Menú Principal")
    
    ejecutando = True
    mostrar_submenu_multi = False

    while ejecutando:
        pos_mouse = pygame.mouse.get_pos()
        PANTALLA.blit(imagen_menu, (0, 0))

        # Botón de configuración escalado
        settings_button_rect = pygame.Rect(scale_position_x(650), scale_position_y(30), scale_value(125), scale_value(35))
        settings_color = (150, 150, 255) if settings_button_rect.collidepoint(pos_mouse) else (100, 100, 255)
        pygame.draw.rect(PANTALLA, settings_color, settings_button_rect)
        texto = FUENTE.render("Settings", True, (255, 255, 255))
        PANTALLA.blit(texto, (settings_button_rect.x + scale_value(5), settings_button_rect.y + scale_value(5)))

        y_botones = ALTO_MENU - scale_value(100)

        if not mostrar_submenu_multi:
            boton_1_jugador = dibujar_boton("1 Jugador", scale_position_x(140), y_botones, scale_position_y(200), scale_value(60), AZUL, VERDE, pos_mouse)
            boton_multijugador = dibujar_boton("Multijugador", scale_position_x(460), y_botones, scale_position_y(200), scale_value(60), AZUL, VERDE, pos_mouse)
        else:
            """boton_1vs1 = dibujar_boton("1 vs 1", ANCHO_MENU // 2 - scale_position_x(260), y_botones, scale_position_y(200), scale_value(60), AZUL, VERDE, pos_mouse)
            boton_2vsCpu = dibujar_boton("2 vs Cpu", ANCHO_MENU // 2 + scale_position_x(60), y_botones, scale_position_y(200), scale_value(60), AZUL, VERDE, pos_mouse)"""

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.MOUSEBUTTONDOWN:
                if settings_button_rect.collidepoint(evento.pos):
                    abrir_menu_settings()

                if not mostrar_submenu_multi:
                    if boton_1_jugador.collidepoint(evento.pos):
                        return '1player'
                    if boton_multijugador.collidepoint(evento.pos):
                        return '2vsCpu'
                        """mostrar_submenu_multi = True
                else:
                    return 
                    
                    if boton_1vs1.collidepoint(evento.pos):
                        return '1vs1'
                    if boton_2vsCpu.collidepoint(evento.pos):"""

            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                if mostrar_submenu_multi:
                    mostrar_submenu_multi = False
                else:
                    return 'salir'

        pygame.display.flip()

# =============== EJECUCIÓN GENERAL ===========================
if __name__ == "__main__":
    pantalla_inicio()
    menu_principal()