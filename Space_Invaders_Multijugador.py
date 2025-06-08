from pygame import *
import sys
from os.path import abspath, dirname
from random import choice
import config

# Archivos
BASE_PATH = abspath(dirname(__file__))
FONT_PATH = BASE_PATH + '/Letras/'
IMAGE_PATH = BASE_PATH + '/Images/'
SOUND_PATH = BASE_PATH + '/Sounds/'

# Colores (R, G, B)
WHITE = (255, 255, 255)
GREEN = (78, 255, 87)
YELLOW = (241, 255, 0)
BLUE = (80, 255, 239)
PURPLE = (203, 0, 255)
RED = (237, 28, 36)

# Cargado de Imagenes y Pantalla
GAME2_WIDTH = config.get_game2_width()
GAME2_HEIGTH = config.get_game2_height()
SCREEN = display.set_mode((GAME2_WIDTH, GAME2_HEIGTH))
FONT = FONT_PATH + 'space_invaders.ttf'
IMG_NAMES = ['ship', 'mystery',
             'enemy1_1', 'enemy1_2',
             'enemy2_1', 'enemy2_2',
             'enemy3_1', 'enemy3_2',
             'explosionblue', 'explosiongreen', 'explosionpurple',
             'laser', 'enemylaser']
IMAGES = {name: image.load(IMAGE_PATH + '{}.png'.format(name)).convert_alpha()
          for name in IMG_NAMES} # Cargado Automatico de Imagenes en un diccionario

BLOCKERS_POSITION = 550
ENEMY_DEFAULT_POSITION = 65 
ENEMY_MOVE_DOWN = 35


class Ship(sprite.Sprite): # Hereda la clase Sprite de Pygame (Util para objetos con hitbox)
    def __init__(self, player_num=1):
        sprite.Sprite.__init__(self)
        self.image = IMAGES['ship']
        # Configura posición según el jugador
        if player_num == 1:
            self.rect = self.image.get_rect(topleft=(465, 735)) # Posición jugador 1
            self.controls = {"left": K_LEFT, "right": K_RIGHT} # Controles para jugador 1
        else:
            self.rect = self.image.get_rect(topleft=(465, 675)) # Posición jugador 2 
            self.controls = {"left": K_a, "right": K_d} # Controles para jugador 2
        self.invulnerable = True # Nueva nave es invulnerable al principio
        self.tiempoDeCreacion = time.get_ticks() # Tiempo de creación
        self.speed = 5
        self.player_num = player_num # Guardamos qué jugador es para referencia
        
        # Atributos para el disparo
        self.bullet = None # Bala actual (si existe)
        self.canShoot = True # Bandera para permitir disparo
        self.lastShot = 0 # Tiempo del último disparo

    def update(self, screen, keys, currentTime, *args): # Para reescribir la posicion del objeto
        if self.invulnerable and (currentTime - self.tiempoDeCreacion > 1000):
            self.invulnerable = False
        if keys[self.controls["left"]] and self.rect.x > 10:
            self.rect.x -= self.speed # Mover a la izquierda
        if keys[self.controls["right"]] and self.rect.x < 940:
            self.rect.x += self.speed # Mover a la derecha
        screen.blit(self.image, self.rect) # Dibuja el objeto

class Bullet(sprite.Sprite): # Definiendo las balas
    def __init__(self, xpos, ypos, direction, speed, filename, side):
        sprite.Sprite.__init__(self)
        self.image = IMAGES[filename]
        self.rect = self.image.get_rect(topleft=(xpos, ypos)) # Cargar la imagen
        self.speed = speed
        self.direction = direction
        self.side = side # Tirador
        self.filename = filename # Nombre de la imagen

    def update(self, screen, keys, *args): # Para reescribir la posicion del objeto (Keys - Teclas, *Args - Agrupar argumentos)
        screen.blit(self.image, self.rect)
        self.rect.y += self.speed * self.direction
        if self.rect.y < 20 or self.rect.y > 987:
            self.kill() # Eliminar la bala en caso que exceda los limites

class Enemy(sprite.Sprite): # Definiendo a los enemigos
    def __init__(self, row, column): # Para ubicar al enemigo dentro de una matriz de posiciones
        sprite.Sprite.__init__(self)
        self.row = row
        self.column = column
        self.images = [] # Una lista con las dos imagenes para alternar en la animacion
        self.load_images()
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect() # Crea la hitbox

    def toggle_image(self):
        self.index += 1 # Agraga una imagen
        if self.index >= len(self.images): # Si la cantidad de imagenes es igual o mayor a la cantidad de imagenes animables (2)
            self.index = 0 # Empezar con las imagenes de vuelta
        self.image = self.images[self.index]

    def update(self, screen, *args):
        screen.blit(self.image, self.rect) # Solo lo dibuja

    def load_images(self): 
        images = {0: ['1_2', '1_1'],
                  1: ['2_2', '2_1'],
                  2: ['2_2', '2_1'],
                  3: ['3_1', '3_2'],
                  4: ['3_1', '3_2'],
                  } # Asigna un tipo de enemigo a cada fila
        img1, img2 = (IMAGES['enemy{}'.format(img_num)] for img_num in
                      images[self.row]) # Generador de imagenes
        self.images.append(transform.scale(img1, (40, 35)))
        self.images.append(transform.scale(img2, (40, 35))) # Asigna un tamaño a la imagen y la guarda dentro de la lista

class EnemiesGroup(sprite.Group): # Extiende la clase Enemies para trabajar en conjunto con cada uno de ellos
    def __init__(self, columns, rows, enemyPosition):
        sprite.Group.__init__(self)
        self.enemies = [[None] * columns for _ in range(rows)] # Crea una matriz vacia para la formacion de enemigos
        self.columns = columns
        self.rows = rows
        self.leftAddMove = 0 # Agregan movimientos si los enemigos se mueren cerca del lado del limite
        self.rightAddMove = 0
        self.moveTime = 600 # Cuantos milisegundo tarda en moverse el grupo
        self.direction = 1 # 1 = Derecha - -1 = Izquierda
        self.rightMoves = 28 
        self.leftMoves = 28 # Cantidad de paso para poder bajar a la siguiente columna
        self.moveNumber = 12
        self.timer = time.get_ticks() # Ultimo momento en el que se movieron
        self.bottom = enemyPosition + ((rows - 1) * 45) + 35 # Bottom = la ilera de abajo
        self._aliveColumns = list(range(columns))
        self._leftAliveColumn = 0
        self._rightAliveColumn = columns - 1

    def update(self, current_time): # Actualizar al grupo
        if current_time - self.timer > self.moveTime:
            velocidad = 10 if self.direction == 1 else -10
            anchoPantalla = 1000  # Ancho de tu pantalla
            margen = 15  # Margen para que no lleguen pegados al borde

            # Verificar si algún enemigo se pasa del borde
            seVaAPasar = any(
                (enemy.rect.right + velocidad >= anchoPantalla - margen and self.direction == 1) or
                (enemy.rect.left + velocidad < margen and self.direction == -1)
                for enemy in self
            )

            if seVaAPasar: # Si alguno se pasa, cambiar dirección y bajar
                self.direction *= -1
                self.moveNumber = 0
                self.leftMoves = 30 + self.rightAddMove
                self.rightMoves = 30 + self.leftAddMove
                self.bottom = 0
                for enemy in self:
                    enemy.rect.y += ENEMY_MOVE_DOWN
                    enemy.toggle_image()
                    if self.bottom < enemy.rect.y + 35:
                        self.bottom = enemy.rect.y + 35
            else: # Si no se pasa, seguir moviéndose
                for enemy in self:
                    enemy.rect.x += velocidad
                    enemy.toggle_image()
                self.moveNumber += 1

            self.timer += self.moveTime
            
    def add_internal(self, *sprites): # Agrega el sprite a la matriz de enemigos
        super(EnemiesGroup, self).add_internal(*sprites)
        for s in sprites:
            self.enemies[s.row][s.column] = s

    def remove_internal(self, *sprites): # Elimina de la matriz a los muertos y actualiza la velocidad
        super(EnemiesGroup, self).remove_internal(*sprites)
        for s in sprites:
            self.kill(s)
        self.update_speed()

    def is_column_dead(self, column):
        return not any(self.enemies[row][column]
                       for row in range(self.rows))

    def random_bottom(self):
        col = choice(self._aliveColumns) # Elige una de las columnas vivas al azar
        col_enemies = (self.enemies[row - 1][col] # De vuelve el enemigo de mas abajo para poder disparar
                       for row in range(self.rows, 0, -1))
        return next((en for en in col_enemies if en is not None), None)

    def update_speed(self):
        if len(self) == 1:
            self.moveTime = 200 # Si solo queda un enemigo triplica la velocidad
        elif len(self) <= 10:
            self.moveTime = 400 # Si quedan entre 10 y 2 enemigos duplica la velocidad

    def kill(self, enemy):
        self.enemies[enemy.row][enemy.column] = None # Elemina al enemigo de la matriz
        is_column_dead = self.is_column_dead(enemy.column) 
        if is_column_dead: # Verifica 
            self._aliveColumns.remove(enemy.column) # Lo elimina de la lista de los vivos

        if enemy.column == self._rightAliveColumn: # Si era el borde
            while self._rightAliveColumn > 0 and is_column_dead:
                self._rightAliveColumn -= 1 # Reduce el borde
                self.rightAddMove += 5 # Agrega movimientos en esa direccion
                is_column_dead = self.is_column_dead(self._rightAliveColumn)

        elif enemy.column == self._leftAliveColumn: # Lo mismo pero con el lado izquierdo
            while self._leftAliveColumn < self.columns and is_column_dead:
                self._leftAliveColumn += 1
                self.leftAddMove += 5
                is_column_dead = self.is_column_dead(self._leftAliveColumn)

class Blocker(sprite.Sprite): # Definir los bloques de proteccion
    def __init__(self, size, color, row, column):
        sprite.Sprite.__init__(self)
        self.height = size # Alto
        self.width = size # Ancho
        self.color = color
        self.image = Surface((self.width, self.height)) # Se crea un rectangulo
        self.image.fill(self.color) # Se le coloca el color
        self.rect = self.image.get_rect() # Para manejar las coliciones
        self.row = row
        self.column = column

    def update(self, screen, keys, *args):
        screen.blit(self.image, self.rect) # Dibujar el objeto

class Mystery(sprite.Sprite):  # Nave misteriosa
    def __init__(self):
        sprite.Sprite.__init__(self)
        self.image = IMAGES['mystery']
        self.image = transform.scale(self.image, (75, 35))
        self.rect = self.image.get_rect(topleft=(-80, 45))  # Posición inicial
        self.row = 5
        self.moveTime = 25000  # Aparece cada 25 segundos
        self.direction = 1
        self.timer = time.get_ticks()
        
        # Cargar el sonido con volumen según esté muteado o no
        self.mysteryEntered = mixer.Sound(SOUND_PATH + 'mysteryentered.wav')
        self.mysteryEntered.set_volume(0.0 if config.MUTEADO else 0.3)
        
        self.playSound = True  # Controla si el sonido debe reproducirse nuevamente

    def update(self, screen, keys, currentTime, *args):
        resetTimer = False
        passed = currentTime - self.timer  # Asegúrate de que currentTime es un entero con milisegundos
        if passed > self.moveTime:  # Solo si han pasado el tiempo adecuado
            if (self.rect.x < 0 or self.rect.x > 800) and self.playSound:
                self.mysteryEntered.play()  # Reproduce el sonido de la nave
                self.playSound = False  # Apaga el sonido de la nave
            if self.rect.x < 1040 and self.direction == 1:
                self.mysteryEntered.fadeout(4000)  # Reduce suavemente el sonido
                self.rect.x += 2
                screen.blit(self.image, self.rect)  # Lo mueve para la derecha
            if self.rect.x > -100 and self.direction == -1:
                self.mysteryEntered.fadeout(4000)  # Reduce suavemente el sonido
                self.rect.x -= 2
                screen.blit(self.image, self.rect)  # Lo mueve para la izquierda


        if self.rect.x > 1030: # Si salio por la derecha
            self.playSound = True
            self.direction = -1 # Setea el movimiento para la izquierda
            resetTimer = True 
        if self.rect.x < -90: # Si salio por la izquierda
            self.playSound = True
            self.direction = 1 # Setea el movimiento para la derecha
            resetTimer = True
        if passed > self.moveTime and resetTimer:
            self.timer = currentTime # Resetea el reloj de 25 segundos

class EnemyExplosion(sprite.Sprite): # Definir la explosion de los enemigos tras su muerte
    def __init__(self, enemy, *groups):
        super(EnemyExplosion, self).__init__(*groups)
        self.image = transform.scale(self.get_image(enemy.row), (40, 35)) # Asigna un tamaño de imagen inicial
        self.image2 = transform.scale(self.get_image(enemy.row), (50, 45)) # Asigna un tamaño a la imagen mas grande
        self.rect = self.image.get_rect(topleft=(enemy.rect.x, enemy.rect.y)) # La coloca en la posicion del enemigo
        self.timer = time.get_ticks() # Guarda el momento de la explosion

    @staticmethod
    def get_image(row):
        img_colors = ['purple', 'blue', 'blue', 'green', 'green']
        return IMAGES['explosion{}'.format(img_colors[row])] # Generador de imagenes

    def update(self, screen, current_time, *args):
        passed = current_time - self.timer
        if passed <= 100:
            screen.blit(self.image, self.rect) # Dibuja una imagen luego de 100 milisegundos
        elif passed <= 200:
            screen.blit(self.image2, (self.rect.x - 6, self.rect.y - 6)) # Dibuja la segunda luego de 200 milisegundos
        elif 400 < passed:
            self.kill() # Luego de 400 milisegundo las elimina

class MysteryExplosion(sprite.Sprite): # Explosion de la nave misteriosa
    def __init__(self, mystery, score, *groups):
        super(MysteryExplosion, self).__init__(*groups)
        self.text = Text(FONT, 20, str(score), WHITE, # Define un tipo de texto en la fuente, 20 de grande y color blanco
                         mystery.rect.x + 20, mystery.rect.y + 6)
        self.timer = time.get_ticks() # Guarda el tiempo de la explosion

    def update(self, screen, current_time, *args):
        passed = current_time - self.timer
        if passed <= 200 or 400 < passed <= 600:
            self.text.draw(screen) # Muestra el texto en 2 intervalos; 0 - 200 , 400 - 600 milesegundos
        elif 600 < passed:
            self.kill() # Luego de 600 milisegundo elimina el texto

class ShipExplosion(sprite.Sprite): # Explosion de la nave propia
    def __init__(self, ship, *groups):
        super(ShipExplosion, self).__init__(*groups)
        self.image = IMAGES['ship']
        self.rect = self.image.get_rect(topleft=(ship.rect.x, ship.rect.y))
        self.timer = time.get_ticks() # Guarda el tiempo de la explosion

    def update(self, screen, current_time, *args):
        passed = current_time - self.timer
        if 300 < passed <= 600:
            screen.blit(self.image, self.rect) # Durante 300 milisegundo dibuja de nuevo la nave
        elif 900 < passed:
            self.kill() # Luego de 900 milisegundo la elimina

class Life(sprite.Sprite): 
    def __init__(self, xpos, ypos):
        sprite.Sprite.__init__(self)
        self.image = IMAGES['ship']
        self.image = transform.scale(self.image, (23, 23)) # Carga la imagen pero la dimensiona mas pequeña
        self.rect = self.image.get_rect(topleft=(xpos, ypos)) # Define la posicion inicial en pantalla

    def update(self, screen, *args):
        screen.blit(self.image, self.rect) # Dibuja la imagen cada vez que se actualiza el juego

class Text(object):
    def __init__(self, textFont, size, message, color, xpos, ypos):
        self.font = font.Font(textFont, size)
        self.surface = self.font.render(message, True, color)
        self.rect = self.surface.get_rect(topleft=(xpos, ypos))

    def draw(self, surface):
        surface.blit(self.surface, self.rect) # Dibuja el texto sobre la superficie

class SpaceInvaders2(object): # Codigo del Juego
    def __init__(self):
        mixer.pre_init(44100, -16, 1, 4096) # Es recomendado para las persona que usan Linux
        init()
        self.clock = time.Clock() # Timer
        self.caption = display.set_caption('Space Invaders Multiplayer') # Título actualizado
        self.screen = SCREEN # Pantalla
        self.menu = image.load(IMAGE_PATH + 'image_second.webp') # Cargar fondo
        self.menu = transform.scale(self.menu, (1000, 800))
        self.background = image.load(IMAGE_PATH + 'background.jpg').convert() # Cargar fondo
        self.background = transform.scale(self.background, (1000, 800))
        self.startGame = False # Iniciar el juego
        self.mainScreen = True # El menu principal
        self.gameOver = False # Controla si el juego termino
        self.gameOverTime = 0  # Tiempo para contar desde que inicia el game over
        self.enemyPosition = ENEMY_DEFAULT_POSITION # Llama a la funcion para poder colocar a los enemigos
        """self.titleText = Text(FONT, 50, 'Space Invaders', WHITE, 274, 205)  # Centrado más arriba"""
        self.titleText2 = Text(FONT, 25, 'Press any key to continue', WHITE, 285, 715)
        self.titleText3 = Text(FONT, 20, '2 Player Mode: P1-Arrows/Space, P2-WASD/W', WHITE, 240, 755)
        self.gameOverText = Text(FONT, 50, 'Game Over', WHITE, 350, 360)  # Ajustado para centrar
        self.nextRoundText = Text(FONT, 50, 'Next Round', WHITE, 330, 360)  # Ajustado para centrar
        """self.enemy1Text = Text(FONT, 25, '   =   10 pts', GREEN, 468, 370)
        self.enemy2Text = Text(FONT, 25, '   =  20 pts', BLUE, 468, 420)
        self.enemy3Text = Text(FONT, 25, '   =  30 pts', PURPLE, 468, 470)
        self.enemy4Text = Text(FONT, 25, '   =  ?????', RED, 468, 520)"""
        self.scoreText = Text(FONT, 20, 'Score', WHITE, 5, 5)
        self.livesText = Text(FONT, 20, 'P1 Lives', WHITE, 780, 5)  # Ajustado para P1
        self.livesText2 = Text(FONT, 20, 'P2 Lives', WHITE, 780, 30)  # Vidas para P2

        self.life1 = Life(894, 3)  
        self.life2 = Life(928, 3)
        self.life3 = Life(961, 3)
        self.life1_p2 = Life(894, 28)
        self.life2_p2 = Life(928, 28)
        self.life3_p2 = Life(961, 28)
        self.livesGroup = sprite.Group(self.life1, self.life2, self.life3)
        self.livesGroup2 = sprite.Group(self.life1_p2, self.life2_p2, self.life3_p2)
        self.livesRecoveredP1 = 0  # Contador de vidas recuperadas para el jugador 1
        self.livesRecoveredP2 = 0  # Contador de vidas recuperadas para el jugador 2
        self.gameTimer = 0
        self.gameOverTime = 0
        self.mainScreen = True
        self.startGame = False

    def reset(self, score): # Reinicia cada grupo (Para cuando termina o pasa de nivel)
        self.player = Ship(player_num=1) # Jugador 1 con controles de flechas
        self.player2 = Ship(player_num=2) # Jugador 2 con controles WASD
        self.shipAlive = True
        self.ship2Alive = True
        self.playerGroup = sprite.Group(self.player)
        self.player2Group = sprite.Group(self.player2)
        self.explosionsGroup = sprite.Group()
        self.bullets = sprite.Group()
        self.bullets2 = sprite.Group() # Grupo para las balas del segundo jugador
        self.mysteryShip = Mystery()
        self.mysteryGroup = sprite.Group(self.mysteryShip)
        self.enemyBullets = sprite.Group()
        self.make_enemies()
        self.allSprites = sprite.Group(self.player, self.player2, self.enemies,
                                    self.livesGroup, self.livesGroup2, self.mysteryShip)
        self.keys = key.get_pressed()

        self.timer = time.get_ticks()
        self.noteTimer = time.get_ticks()
        self.shipTimer = time.get_ticks()
        self.ship2Timer = time.get_ticks()
        self.gameTimer = time.get_ticks() # Añadido para solucionar el problema del game over
        self.score = score
        self.create_audio()
        self.makeNewShip = False
        self.makeNewShip2 = False
        self.shipAlive = True
        self.ship2Alive = True
    
        # Restaurar vidas del jugador 1 si están todas muertas y no se revivieron previamente
        if all(not life.alive() for life in [self.life1, self.life2, self.life3]):
            if len(self.livesGroup) == 0:
                self.life1 = Life(894, 3)
                self.life2 = Life(928, 3)
                self.life3 = Life(961, 3)
                self.livesGroup.add(self.life1, self.life2, self.life3)
                self.shipAlive = True
            else:
                # Solo volver a agregar las que están vivas y no están en el grupo
                for life in [self.life1, self.life2, self.life3]:
                    if life.alive() and life not in self.livesGroup:
                        self.livesGroup.add(life)

        # Restaurar vidas del jugador 2 si están todas muertas y no se revivieron previamente
        if all(not life.alive() for life in [self.life1_p2, self.life2_p2, self.life3_p2]):
            if len(self.livesGroup2) == 0:
                self.life1_p2 = Life(894, 28)
                self.life2_p2 = Life(928, 28)
                self.life3_p2 = Life(961, 28)
                self.livesGroup2.add(self.life1_p2, self.life2_p2, self.life3_p2)
                self.ship2Alive = True
            else:
                for life in [self.life1_p2, self.life2_p2, self.life3_p2]:
                    if life.alive() and life not in self.livesGroup2:
                        self.livesGroup2.add(life)


    def make_blockers(self, number): # Crea los bloques de defensa
        blockerGroup = sprite.Group()
        for row in range(4): # Cada bloque tendra 4 * 9 secciones
            for column in range(9):
                blocker = Blocker(10, RED, row, column)
                blocker.rect.x = 50 + (200 * number) + (column * blocker.width)
                blocker.rect.y = BLOCKERS_POSITION + (row * blocker.height)
                blockerGroup.add(blocker)
        return blockerGroup

    def create_audio(self):  # Guarda los sonidos de cada actualización
        self.sounds = {}  # Diccionario para acceder a los sonidos fácilmente

        for SoundName in ['shoot', 'shoot2', 'invaderkilled', 'mysterykilled', 'shipexplosion']:
            self.sounds[SoundName] = mixer.Sound(SOUND_PATH + '{}.wav'.format(SoundName))
            # Si está muteado, volumen en 0; si no, en 0.2
            self.sounds[SoundName].set_volume(0.0 if config.MUTEADO else 0.2)

        self.musicNotes = [mixer.Sound(SOUND_PATH + '{}.wav'.format(i)) for i in range(4)]
        for Sound in self.musicNotes:
            # Si está muteado, volumen en 0; si no, en 0.5
            Sound.set_volume(0.0 if config.MUTEADO else 0.5)

        self.noteIndex = 0  # Índice de nota para la secuencia

    def play_main_music(self, currentTime): # Reproductor de musica
        if currentTime - self.noteTimer > self.enemies.moveTime: # Suena con el mismo intervalo que los enemigos se mueven
            self.note = self.musicNotes[self.noteIndex]
            if self.noteIndex < 3: # Si no excede el maximo de notas
                self.noteIndex += 1 # Pasa a la siguiente nota
            else: # Si lo excedio
                self.noteIndex = 0 # Se reinician las notas

            self.note.play() 
            self.noteTimer += self.enemies.moveTime # Actualiza el tiempo de ultimo tocado

    @staticmethod # Funcion estatica
    def should_exit(evt): # Evalua el evento
        return evt.type == QUIT or (evt.type == KEYUP and evt.key == K_ESCAPE)
        # Si es la accion de tocar la cruz o la tecla escape se cierra el juego

    def check_input(self): 
        self.keys = key.get_pressed() 
        if hasattr(self, 'player') and self.player is not None:
            for e in event.get():
                if e.type == QUIT:
                    return 'exit'
                if e.type == KEYUP:
                    if e.key == K_ESCAPE:
                        return 'menu'
                if e.type == KEYDOWN: 
                    # Disparo para el jugador 1 con SPACE
                    if e.key == K_SPACE: 
                        # Verificar que el jugador tenga vidas antes de permitirle disparar
                        can_shoot1 = self.shipAlive 
                        if can_shoot1:
                            # Verificar si no hay balas activas antes de permitir disparar
                            if len(self.bullets) == 0:  # Solo dispara si no hay balas en pantalla
                                if self.score < 2000: 
                                    bullet = Bullet(self.player.rect.x + 23,
                                                    self.player.rect.y + 5, -1,
                                                    15, 'laser', 'center') 
                                    self.bullets.add(bullet) 
                                    self.allSprites.add(self.bullets) 
                                    self.sounds['shoot'].play() 
                                else: 
                                    # Disparo doble (izquierda y derecha) solo si el puntaje es mayor a 2000
                                    leftbullet = Bullet(self.player.rect.x + 8,
                                                        self.player.rect.y + 5, -1,
                                                        15, 'laser', 'left')
                                    rightbullet = Bullet(self.player.rect.x + 38,
                                                        self.player.rect.y + 5, -1,
                                                        15, 'laser', 'right') 
                                    self.bullets.add(leftbullet) 
                                    self.bullets.add(rightbullet) 
                                    self.allSprites.add(self.bullets)
                                    self.sounds['shoot2'].play()

                    # Disparo para el jugador 2 con W
                    if e.key == K_w:
                        # Verificar que el jugador 2 tenga vidas antes de permitirle disparar
                        can_shoot2 = self.ship2Alive 
                        if can_shoot2:
                            # Verificar si no hay balas activas antes de permitir disparar
                            if len(self.bullets2) == 0:  # Solo dispara si no hay balas en pantalla
                                if self.score < 2000:
                                    bullet = Bullet(self.player2.rect.x + 23,
                                                    self.player2.rect.y + 5, -1,
                                                    15, 'laser', 'center')
                                    self.bullets2.add(bullet)
                                    self.allSprites.add(self.bullets2)
                                    self.sounds['shoot'].play()
                                else:
                                    # Disparo doble (izquierda y derecha) solo si el puntaje es mayor a 2000
                                    leftbullet = Bullet(self.player2.rect.x + 8,
                                                        self.player2.rect.y + 5, -1,
                                                        15, 'laser', 'left')
                                    rightbullet = Bullet(self.player2.rect.x + 38,
                                                        self.player2.rect.y + 5, -1,
                                                        15, 'laser', 'right')
                                    self.bullets2.add(leftbullet)
                                    self.bullets2.add(rightbullet)
                                    self.allSprites.add(self.bullets2)
                                    self.sounds['shoot2'].play()

        return None


    def make_enemies(self): # Crear los enemigos
        enemies = EnemiesGroup(15, 5, self.enemyPosition) # Se agregan los anemigos a los grupos de enemigos 
        for row in range(5):
            for column in range(15):
                enemy = Enemy(row, column)
                enemy.rect.x = 120 + (column * 50)
                enemy.rect.y = self.enemyPosition + (row * 45)
                enemies.add(enemy) # Se agrega al grupo de los enemigos existenes

        self.enemies = enemies

    def make_enemies_shoot(self): # Crea los disparos de los enemigos
        if (time.get_ticks() - self.timer) > 700 and self.enemies: # Solo si ya pasaron 700 milisegundos
            enemy = self.enemies.random_bottom()
            self.enemyBullets.add(
                Bullet(enemy.rect.x + 14, enemy.rect.y + 20, 1, 5,
                       'enemylaser', 'center')) # Se genera una bala para el enemigo elegido por el random
            self.allSprites.add(self.enemyBullets)
            self.timer = time.get_ticks() # Se guarda el tiempo de disparo

    def calculate_score(self, row): # Calcular el puntaje
        scores = {0: 30,
                  1: 20,
                  2: 20,
                  3: 10,
                  4: 10,
                  5: choice([50, 100, 150, 300])
                  } # Asigna un valor a cada fila de enemigos

        score = scores[row] # Calcula la posicion del enemigo destruido para saber cuantos puntos asignar
        self.score += score
        return score

    def create_main_menu(self): # Crea el menu principal
        """self.enemy1 = IMAGES['enemy3_1'] # Coloca un enemigo en cada posicion asignada
        self.enemy1 = transform.scale(self.enemy1, (40, 40)) # Crea la escala de la imagen
        self.enemy2 = IMAGES['enemy2_2']
        self.enemy2 = transform.scale(self.enemy2, (40, 40))
        self.enemy3 = IMAGES['enemy1_2']
        self.enemy3 = transform.scale(self.enemy3, (40, 40))
        self.enemy4 = IMAGES['mystery']
        self.enemy4 = transform.scale(self.enemy4, (80, 40))
        self.screen.blit(self.enemy1, (418, 370))
        self.screen.blit(self.enemy2, (418, 420))
        self.screen.blit(self.enemy3, (418, 470))
        self.screen.blit(self.enemy4, (399, 520))"""

    def check_collisions(self): # Checkear las coliciones de hitbox's
        # Colisiones entre balas
        sprite.groupcollide(self.bullets, self.enemyBullets, True, True) # Considera ambos tipos de balas
        sprite.groupcollide(self.bullets2, self.enemyBullets, True, True) # Lo mismo pero para balas del jugador 2

        # Colisiones entre balas del jugador 1 y enemigos
        for enemy in sprite.groupcollide(self.enemies, self.bullets,True, True).keys(): # Considera enemigos y balas propias
            self.sounds['invaderkilled'].play() # Suena el sonido de muerte
            self.calculate_score(enemy.row) # Calcula el puntaje
            EnemyExplosion(enemy, self.explosionsGroup) # Llama a la funcion de grafico de explosiones
            self.gameTimer = time.get_ticks() # Guarda el tiempo de la muerte
            
        # Colisiones entre balas del jugador 2 y enemigos
        for enemy in sprite.groupcollide(self.enemies, self.bullets2,True, True).keys():
            self.sounds['invaderkilled'].play()
            self.calculate_score(enemy.row)
            EnemyExplosion(enemy, self.explosionsGroup)
            self.gameTimer = time.get_ticks()

        # Colisiones entre balas del jugador 1 y naves misteriosas
        for mystery in sprite.groupcollide(self.mysteryGroup, self.bullets, True, True).keys(): # Para las naves misteriosas y balas propias
            mystery.mysteryEntered.stop() # Se detiene el sonido de la nave recorriendo el juego
            self.sounds['mysterykilled'].play() # Se inserta el sonido de la nave destruida
            score = self.calculate_score(mystery.row) # Se calcula el puntaje
            MysteryExplosion(mystery, score, self.explosionsGroup) 
            newShip = Mystery() # Se crea una nueva nave
            self.allSprites.add(newShip) # Se agrega al grupo
            self.mysteryGroup.add(newShip)
            
        # Colisiones entre balas del jugador 2 y naves misteriosas
        for mystery in sprite.groupcollide(self.mysteryGroup, self.bullets2, True, True).keys():
            mystery.mysteryEntered.stop()
            self.sounds['mysterykilled'].play()
            score = self.calculate_score(mystery.row)
            MysteryExplosion(mystery, score, self.explosionsGroup)
            newShip = Mystery()
            self.allSprites.add(newShip)
            self.mysteryGroup.add(newShip)

        # Colisiones entre balas enemigas y jugador 1
        for player in sprite.groupcollide(self.playerGroup, self.enemyBullets, True, True).keys():  
            if self.life3.alive(): 
                self.life3.kill()
                self.livesRecoveredP1 -= 1 
            elif self.life2.alive():
                self.life2.kill() 
                self.livesRecoveredP1 -= 1
            elif self.life1.alive():
                self.life1.kill() 
                self.livesRecoveredP1 -= 1
            self.sounds['shipexplosion'].play() 
            ShipExplosion(player, self.explosionsGroup)

            # Verificar si aún tiene vidas
            if self.life1.alive() or self.life2.alive() or self.life3.alive():
                self.makeNewShip = True
                self.shipTimer = time.get_ticks()
                self.shipAlive = False
            else:
                self.makeNewShip = False
                self.shipAlive = False  # Aseguramos que no pueda disparar
        
        # Colisiones entre balas enemigas y jugador 2
        for player2 in sprite.groupcollide(self.player2Group, self.enemyBullets, True, True).keys():
            if self.life3_p2.alive():
                self.life3_p2.kill()
                self.livesRecoveredP2 -= 1
            elif self.life2_p2.alive():
                self.life2_p2.kill()
                self.livesRecoveredP2 -= 1
            elif self.life1_p2.alive():
                self.life1_p2.kill()
                self.livesRecoveredP2 -= 1
            self.sounds['shipexplosion'].play()
            ShipExplosion(player2, self.explosionsGroup)
                
            # Verificar si aún tiene vidas
            if self.life1_p2.alive() or self.life2_p2.alive() or self.life3_p2.alive():
                self.makeNewShip2 = True
                self.ship2Timer = time.get_ticks()
                self.ship2Alive = False
            else:
                self.makeNewShip2 = False
                self.ship2Alive = False  # Aseguramos que no pueda disparar

        # Comprobar si ambos jugadores perdieron todas sus vidas (forma dinámica y segura)
        if not any(life.alive() for life in self.livesGroup) and not any(life.alive() for life in self.livesGroup2):
            self.gameOver = True
            self.startGame = False
            self.gameTimer = time.get_ticks()

        # También modificar esta condición:
        if self.enemies and self.enemies.bottom >= 718:
            sprite.groupcollide(self.enemies, self.playerGroup, True, True)
            sprite.groupcollide(self.enemies, self.player2Group, True, True)
            # Si los enemigos tocan el suelo, terminar el juego
            self.gameOver = True
            self.startGame = False
            self.gameTimer = time.get_ticks()

        # Colisiones con bloques
        sprite.groupcollide(self.bullets, self.allBlockers, True, True) # Considera balas aliadas y los bloques
        sprite.groupcollide(self.bullets2, self.allBlockers, True, True) # Lo mismo para balas del jugador 2
        sprite.groupcollide(self.enemyBullets, self.allBlockers, True, True) # Considera balas enemigas y los bloques
        if self.enemies.bottom >= BLOCKERS_POSITION: # Si los enemigos se encuentran en la misma posicion que los bloques
            sprite.groupcollide(self.enemies, self.allBlockers, False, True) # Considera a los enemigos y los bloques

    def create_new_ship(self, currentTime):
        # Recrear nave del jugador 1 si es necesario
        if self.makeNewShip and (currentTime - self.shipTimer > 900):
            if self.life1.alive() or self.life2.alive() or self.life3.alive():
                self.player = Ship(player_num=1)
                self.player.bullet = None
                self.player.canShoot = True  # Solo si tu clase Ship lo usa
                self.player.lastShot = 0  # Si usás cooldown por tiempo
                self.allSprites.add(self.player)
                self.playerGroup.add(self.player)
                self.makeNewShip = False
                self.shipAlive = True

        # Recrear nave del jugador 2 si es necesario
        if self.makeNewShip2 and (currentTime - self.ship2Timer > 900):
            if self.life1_p2.alive() or self.life2_p2.alive() or self.life3_p2.alive():
                self.player2 = Ship(player_num=2)
                self.player2.bullet = None
                self.player2.canShoot = True
                self.player2.lastShot = 0
                self.allSprites.add(self.player2)
                self.player2Group.add(self.player2)
                self.makeNewShip2 = False
                self.ship2Alive = True


    def create_game_over(self, currentTime): 
        self.screen.blit(self.background, (0, 0)) 
        passed = currentTime - self.gameTimer
        if passed < 750: 
            self.gameOverText.draw(self.screen) 
        elif 750 < passed < 1500:
            self.screen.blit(self.background, (0, 0))
        elif 1500 < passed < 2250:
            self.gameOverText.draw(self.screen)
        elif 2250 < passed < 2750:
            self.screen.blit(self.background, (0, 0))
        elif passed > 3000:
            self.mainScreen = True 
            self.gameOver = False 
            self.gameOverTime = 0  # Resetea el tiempo de game over
            # Resetear completamente el estado del juego
            self.enemyPosition = ENEMY_DEFAULT_POSITION

    def revisar_y_revivir_jugador(self, playerLives, teammateLives, playerTag, livesGroup, xCoordinates, yCoordinate):
        # Verifica si el jugador está completamente eliminado y su compañero sigue vivo
        if all(not life.alive() for life in playerLives) and any(life.alive() for life in teammateLives):
            # Verifica si el jugador todavía puede recuperar vidas (máximo 3)
            if getattr(self, playerTag) < 3:
                for i in range(3):
                    if not playerLives[i].alive():
                        # Crea una nueva vida en la posición correspondiente
                        playerLives[i] = Life(xCoordinates[i], yCoordinate)
                        livesGroup.add(playerLives[i])
                        setattr(self, playerTag, getattr(self, playerTag) + 1)
                        # Activar nuevamente al jugador según el tag
                        if playerTag == 'livesRecoveredP1':
                            self.shipAlive = True
                            # Recrear el jugador 1 si no existe
                            if not self.playerGroup:
                                self.player = Ship(player_num=1)
                                self.allSprites.add(self.player)
                                self.playerGroup.add(self.player)
                        elif playerTag == 'livesRecoveredP2':
                            self.ship2Alive = True
                            # Recrear el jugador 2 si no existe
                            if not self.player2Group:
                                self.player2 = Ship(player_num=2)
                                self.allSprites.add(self.player2)
                                self.player2Group.add(self.player2)
                        break


    def actualizar_vidas(self):
        # Asegúrate de que las vidas siempre se actualicen correctamente
        self.livesGroup.update(self.screen)
        self.livesGroup2.update(self.screen)

    def main2(self):  # Definiendo el menú principal
        self.screen = display.set_mode((1000, 800))  # Define el tamaño de la pantalla

        while True:
            salir = self.check_input()  # Verifica si se debe salir (al menú)
            if salir:
                return 'menu'

            if self.mainScreen:  # Si se encuentra en la pantalla del menú
                self.screen.blit(self.background, (0, 0))  # Cargar fondo
                self.screen.blit(self.menu, (0, 0))  # Mostrar el fondo del menú
                self.titleText2.draw(self.screen)  # Muestra el texto del título
                self.titleText3.draw(self.screen)  # Instrucciones para 2 jugadores
                self.create_main_menu()  # Crear el menú principal
                for e in event.get():
                    if self.should_exit(e):
                        return 'menu'  # Volver al menú en vez de salir del juego

                    if e.type == KEYUP:  # Si es de dejar de presionar una tecla
                        self.allBlockers = sprite.Group(self.make_blockers(0), 
                                                        self.make_blockers(1),
                                                        self.make_blockers(2),
                                                        self.make_blockers(3),
                                                        self.make_blockers(4))  # Crear los bloques
                        self.livesGroup.add(self.life1, self.life2, self.life3)  # Añadir vidas del jugador 1
                        self.livesGroup2.add(self.life1_p2, self.life2_p2, self.life3_p2)  # Añadir vidas del jugador 2
                        self.reset(0)  # Resetear el estado del juego
                        self.startGame = True
                        self.mainScreen = False  # Salir del menú

            elif self.startGame:  # Cuando se ejecuta el juego
                if not self.enemies and not self.explosionsGroup:  # Si no hay enemigos ni colisiones
                    currentTime = time.get_ticks()  # Guardar el tiempo
                    if currentTime - self.gameTimer < 3000:  # Durante los primeros 3 segundos
                        self.screen.blit(self.background, (0, 0))  # Mostrar fondo
                        self.scoreText2 = Text(FONT, 20, str(self.score), GREEN, 85, 5)  # Mostrar el puntaje
                        self.scoreText.draw(self.screen)
                        self.scoreText2.draw(self.screen)
                        self.nextRoundText.draw(self.screen)
                        self.livesText.draw(self.screen)
                        self.livesText2.draw(self.screen)  # Mostrar las vidas del jugador 2
                        self.livesGroup.update(self.screen)
                        self.livesGroup2.update(self.screen)  # Actualizar las vidas del jugador 2
                        self.check_input()  # Verificar el input
                        # Revisar si se revive el jugador 1
                        self.revisar_y_revivir_jugador(
                            playerLives = [self.life1, self.life2, self.life3],
                            teammateLives = [self.life1_p2, self.life2_p2, self.life3_p2],
                            playerTag = 'livesRecoveredP1',
                            livesGroup = self.livesGroup,
                            xCoordinates = [894, 928, 961],
                            yCoordinate = 3
                        )

                        # Revisar si se revive el jugador 2
                        self.revisar_y_revivir_jugador(
                            playerLives = [self.life1_p2, self.life2_p2, self.life3_p2],
                            teammateLives = [self.life1, self.life2, self.life3],
                            playerTag = 'livesRecoveredP2',
                            livesGroup = self.livesGroup2,
                            xCoordinates = [894, 928, 961],
                            yCoordinate = 28
                        )

                        self.actualizar_vidas()

                    if currentTime - self.gameTimer > 3000:  # Después de 3 segundos
                        self.enemyPosition += ENEMY_MOVE_DOWN  # Mover enemigos hacia abajo
                        self.reset(self.score)
                        self.gameTimer += 3000
                        
                    self.allSprites.update(self.screen, self.keys, currentTime)
                else:  # Si el juego está en curso normalmente
                    currentTime = time.get_ticks()  # Guardar el tiempo
                    self.play_main_music(currentTime)  # Ejecutar música
                    self.screen.blit(self.background, (0, 0))  # Mostrar fondo
                    self.allBlockers.update(self.screen, self.keys)  # Actualizar los bloques
                    self.scoreText2 = Text(FONT, 20, str(self.score), GREEN, 85, 5)  # Mostrar el puntaje
                    self.scoreText.draw(self.screen)
                    self.scoreText2.draw(self.screen)
                    self.livesText.draw(self.screen)
                    self.livesText2.draw(self.screen)  # Mostrar vidas del jugador 2
                    self.check_input()  # Verificar input del jugador
                    self.enemies.update(currentTime)  # Actualizar enemigos
                    self.allSprites.update(self.screen, self.keys, currentTime)
                    self.explosionsGroup.update(self.screen, currentTime)  # Actualizar las explosiones
                    self.check_collisions()  # Revisar colisiones
                    self.create_new_ship(currentTime)
                    self.make_enemies_shoot()  # Los enemigos comienzan a disparar

            elif self.gameOver:  # Si se pierde el juego
                currentTime = time.get_ticks()
                if self.gameOverTime == 0:  # Si no se ha iniciado el contador de game over
                    self.gameOverTime = currentTime
                    self.gameTimer = currentTime

                self.create_game_over(currentTime)  # Mostrar la pantalla de game over
                # Asegúrate de que los jugadores no puedan disparar
                self.shipAlive = False
                self.ship2Alive = False

            display.update()  # Actualizar la pantalla
            self.clock.tick(60)  # Limitar a 60 FPS


if __name__ == '__main__':
    game2 = SpaceInvaders2()
    game2.main2()
