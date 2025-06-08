import pygame
import sys
import os
from Space_Invaders_Main import pantalla_inicio, menu_principal
from Space_Invaders import SpaceInvaders
import Space_Invaders_2 as nm
import config

# Configurar ventana centrada
os.environ['SDL_VIDEO_CENTERED'] = '1'

# Inicializar pygame
pygame.init()

def main():
    # Mostrar pantalla de inicio primero
    pantalla_inicio()
    
    # Comenzar con el menú principal
    estado = 'menu'
    
    while True:
        if estado == 'menu':
            # Llamar al menú principal y esperar su resultado
            resultado = menu_principal()
            
            # Procesar el resultado del menú
            if resultado == '1player':
                # Juego de un jugador
                juego = SpaceInvaders()
                estado = juego.main()  # Devuelve 'menu' si se quiere volver
            elif resultado == '1vs1':
                # Modo 1 vs 1 (por implementar)
                # Aquí iría el código para el modo 1vs1
                pass
            elif resultado == '2vsCpu':
                # Modo 2 vs CPU
                SCREEN = pygame.display.set_mode((config.GAME2_WIDTH_BASE, config.GAME2_HEIGHT_BASE))
                juego2 = nm.SpaceInvaders2()
                estado = juego2.main2()  # Devuelve 'menu' si se quiere volver
            elif resultado == 'salir':
                break
        elif estado == 'salir':
            break

    # Cerrar juego correctamente
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()