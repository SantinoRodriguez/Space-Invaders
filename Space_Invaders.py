from pygame import *
import sys
from os.path import abspath, dirname
from random import choice
from config import get_izquierda, get_derecha, get_muteado, get_game_width, get_game_height, scale_size, scale_value, scale_position_x, scale_position_y, get_offset_x, get_offset_y, get_blockers_position, get_enemy_default_position, get_enemy_move_down

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
GAME_WIDTH = get_game_width()
GAME_HEIGHT = get_game_height()
SCREEN = display.set_mode((GAME_WIDTH, GAME_HEIGHT))
FONT = FONT_PATH + 'space_invaders.ttf'
IMG_NAMES = ['ship', 'mystery',
             'enemy1_1', 'enemy1_2',
             'enemy2_1', 'enemy2_2',
             'enemy3_1', 'enemy3_2',
             'explosionblue', 'explosiongreen', 'explosionpurple',
             'laser', 'enemylaser']
IMAGES = {name: image.load(IMAGE_PATH + '{}.png'.format(name)).convert_alpha()
          for name in IMG_NAMES} # Cargado Automatico de Imagenes en un diccionario

# Valores escalados de posiciones
ENEMY_DEFAULT_POSITION = get_enemy_default_position()
BLOCKERS_POSITION = get_blockers_position()
ENEMY_MOVE_DOWN = get_enemy_move_down()

class Ship(sprite.Sprite):
    def __init__(self):
        sprite.Sprite.__init__(self)
        self.image = IMAGES['ship']
        self.original_width, self.original_height = self.image.get_rect().size
        self.image = transform.scale(self.image, scale_size(self.original_width, self.original_height))
        
        # Posición correctamente escalada con scale_position_x/y
        self.rect = self.image.get_rect(topleft=(scale_position_x(375), scale_position_y(540)))
        self.invulnerable = True
        self.tiempoDeCreacion = time.get_ticks()
        self.speed = scale_value(5)

    def update(self, keys, currentTime, pantalla):
        if self.invulnerable and (currentTime - self.tiempoDeCreacion > 1000):
            self.invulnerable = False
        
        # Corregir los límites para que sean relativos a la zona de juego
        if keys[get_izquierda()] and self.rect.x > scale_position_x(10):
            self.rect.x -= self.speed
        
        if keys[get_derecha()] and self.rect.x < scale_position_x(740):
            self.rect.x += self.speed
        
        pantalla.blit(self.image, self.rect)

class Bullet(sprite.Sprite):
    def __init__(self, xpos, ypos, direction, speed, filename, side):
        sprite.Sprite.__init__(self)
        self.image = IMAGES[filename]
        self.original_width, self.original_height = self.image.get_rect().size
        self.image = transform.scale(self.image, scale_size(self.original_width, self.original_height))
        
        # Escalar la posición inicial de la bala con los nuevos métodos de posición
        self.rect = self.image.get_rect(topleft=(scale_position_x(xpos), scale_position_y(ypos)))
        self.speed = scale_value(speed)
        self.direction = direction
        self.side = side
        self.filename = filename

    def update(self, keys, *args):
        if args and hasattr(args[-1], "blit"):
            pantalla = args[-1]
            pantalla.blit(self.image, self.rect)
        else:
            print("Advertencia: No se pasó pantalla correctamente a update()")
        
        self.rect.y += self.speed * self.direction
        if self.rect.y < scale_position_y(15) or self.rect.y > scale_position_y(GAME_HEIGHT):
            self.kill()

class Enemy(sprite.Sprite):
    def __init__(self, row, column):
        sprite.Sprite.__init__(self)
        self.row = row
        self.column = column
        self.images = []
        self.load_images()
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()

    def toggle_image(self):
        self.index += 1
        if self.index >= len(self.images):
            self.index = 0
        self.image = self.images[self.index]

    def update(self, *args):
        if args:
            pantalla = args[-1]
            pantalla.blit(self.image, self.rect)

    def load_images(self):
        images = {0: ['1_2', '1_1'],
                  1: ['2_2', '2_1'],
                  2: ['2_2', '2_1'],
                  3: ['3_1', '3_2'],
                  4: ['3_1', '3_2'],
                  }
        
        img1, img2 = (IMAGES['enemy{}'.format(img_num)] for img_num in images[self.row])
        # Escalar con la nueva función de escalado
        escala = scale_size(40, 35)

        self.images.append(transform.scale(img1, escala))
        self.images.append(transform.scale(img2, escala))

class EnemiesGroup(sprite.Group):
    def __init__(self, columns, rows, enemyPosition):
        sprite.Group.__init__(self)
        self.enemies = [[None] * columns for _ in range(rows)]
        self.columns = columns
        self.rows = rows
        self.leftAddMove = 0
        self.rightAddMove = 0
        self.moveTime = 600
        self.direction = 1
        self.rightMoves = 30
        self.leftMoves = 30
        self.moveNumber = 15
        self.timer = time.get_ticks()
        # Usar scale_position_y para la posición del fondo
        self.bottom = scale_position_y(enemyPosition + ((rows - 1) * 45) + 35)
        self._aliveColumns = list(range(columns))
        self._leftAliveColumn = 0
        self._rightAliveColumn = columns - 1

    def update(self, current_time):
        if current_time - self.timer > self.moveTime:
            if self.direction == 1:
                max_move = self.rightMoves + self.rightAddMove
            else:
                max_move = self.leftMoves + self.leftAddMove

            if self.moveNumber >= max_move:
                self.leftMoves = 30 + self.rightAddMove
                self.rightMoves = 30 + self.leftAddMove
                self.direction *= -1
                self.moveNumber = 0
                self.bottom = 0
                for enemy in self:
                    # Desplazamiento vertical adecuadamente escalado
                    enemy.rect.y += scale_value(ENEMY_MOVE_DOWN)
                    enemy.toggle_image()
                    if self.bottom < enemy.rect.y + scale_value(35): 
                        self.bottom = enemy.rect.y + scale_value(35)
            else:
                # Velocidad horizontal adecuadamente escalada
                velocity = scale_value(10) if self.direction == 1 else -scale_value(10)
                for enemy in self:
                    enemy.rect.x += velocity
                    enemy.toggle_image()
                self.moveNumber += 1

            self.timer += self.moveTime

    def add_internal(self, *sprites):
        super(EnemiesGroup, self).add_internal(*sprites)
        for s in sprites:
            self.enemies[s.row][s.column] = s

    def remove_internal(self, *sprites):
        super(EnemiesGroup, self).remove_internal(*sprites)
        for s in sprites:
            self.kill(s)
        self.update_speed()

    def is_column_dead(self, column):
        return not any(self.enemies[row][column] for row in range(self.rows))

    def random_bottom(self):
        col = choice(self._aliveColumns)
        col_enemies = (self.enemies[row - 1][col]
                       for row in range(self.rows, 0, -1))
        return next((en for en in col_enemies if en is not None), None)

    def update_speed(self):
        if len(self) == 1:
            self.moveTime = 200
        elif len(self) <= 10:
            self.moveTime = 400

    def kill(self, enemy):
        self.enemies[enemy.row][enemy.column] = None
        is_column_dead = self.is_column_dead(enemy.column)
        if is_column_dead:
            self._aliveColumns.remove(enemy.column)

        if enemy.column == self._rightAliveColumn:
            while self._rightAliveColumn > 0 and is_column_dead:
                self._rightAliveColumn -= 1
                self.rightAddMove += 5
                is_column_dead = self.is_column_dead(self._rightAliveColumn)

        elif enemy.column == self._leftAliveColumn:
            while self._leftAliveColumn < self.columns and is_column_dead:
                self._leftAliveColumn += 1
                self.leftAddMove += 5
                is_column_dead = self.is_column_dead(self._leftAliveColumn)

class Blocker(sprite.Sprite):
    def __init__(self, size, color, row, column):
        sprite.Sprite.__init__(self)
        self.height = scale_value(size)
        self.width = scale_value(size)
        self.color = color
        self.image = Surface((self.width, self.height))
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.row = row
        self.column = column

    def update(self, pantalla):
        pantalla.blit(self.image, self.rect)

class Mystery(sprite.Sprite):
    def __init__(self):
        sprite.Sprite.__init__(self)
        self.image = IMAGES['mystery']
        self.image = transform.scale(self.image, scale_size(75, 35))
        # Posición inicial correctamente escalada
        self.rect = self.image.get_rect(topleft=(scale_position_x(-80), scale_position_y(45)))
        self.row = 5
        self.moveTime = 25000
        self.direction = 1
        self.timer = time.get_ticks()
        
        self.mysteryEntered = mixer.Sound(SOUND_PATH + 'mysteryentered.wav')
        self.mysteryEntered.set_volume(0.0 if get_muteado() else 0.3)
        
        self.playSound = True

    def update(self, keys, currentTime, *args):
        if args:
            pantalla = args[-1]
            resetTimer = False
            passed = currentTime - self.timer

            if passed > self.moveTime:
                # Verificar correctamente los límites de la pantalla
                if (self.rect.x < get_offset_x() or self.rect.x > scale_position_x(840)) and self.playSound:
                    self.mysteryEntered.play()
                    self.playSound = False
                if self.rect.x < scale_position_x(840) and self.direction == 1:
                    self.mysteryEntered.fadeout(4000)
                    self.rect.x += scale_value(2)
                    pantalla.blit(self.image, self.rect)
                if self.rect.x > scale_position_x(-100) and self.direction == -1:
                    self.mysteryEntered.fadeout(4000)
                    self.rect.x -= scale_value(2)
                    pantalla.blit(self.image, self.rect)

            # Verificar límites correctamente escalados
            if self.rect.x > scale_position_x(830):
                self.playSound = True
                self.direction = -1
                resetTimer = True 
            if self.rect.x < scale_position_x(-90):
                self.playSound = True
                self.direction = 1
                resetTimer = True
            if passed > self.moveTime and resetTimer:
                self.timer = currentTime

class EnemyExplosion(sprite.Sprite):
    def __init__(self, enemy, *groups):
        super(EnemyExplosion, self).__init__(*groups)
        self.image = transform.scale(self.get_image(enemy.row), scale_size(40, 35))
        self.image2 = transform.scale(self.get_image(enemy.row), scale_size(50, 45))
        self.rect = self.image.get_rect(topleft=(enemy.rect.x, enemy.rect.y))
        self.timer = time.get_ticks()

    @staticmethod
    def get_image(row):
        img_colors = ['purple', 'blue', 'blue', 'green', 'green']
        return IMAGES['explosion{}'.format(img_colors[row])]

    def update(self, current_time, *args):
        if args:
            pantalla = args[-1]
            passed = current_time - self.timer
            if passed <= 100:
                pantalla.blit(self.image, self.rect)
            elif passed <= 200:
                offset_x = scale_value(6)
                offset_y = scale_value(6)
                pantalla.blit(self.image2, (self.rect.x - offset_x, self.rect.y - offset_y))
        if current_time - self.timer > 400:
            self.kill()

class MysteryExplosion(sprite.Sprite): # Explosion de la nave misteriosa
    def __init__(self, mystery, score, *groups):
        super(MysteryExplosion, self).__init__(*groups)
        self.text = Text(FONT, 20, str(score), WHITE, # Define un tipo de texto en la fuente, 20 de grande y color blanco
                         mystery.rect.x + 20, mystery.rect.y + 6)
        self.timer = time.get_ticks() # Guarda el tiempo de la explosion

    def update(self, current_time):
        passed = current_time - self.timer
        if passed <= 200 or 400 < passed <= 600:
            self.text.draw(display.get_surface())
        elif 600 < passed:
            self.kill()


class ShipExplosion(sprite.Sprite):
    def __init__(self, ship, *groups):
        super(ShipExplosion, self).__init__(*groups)
        self.image = IMAGES['ship']
        self.image = transform.scale(self.image, scale_size(50, 50))
        self.rect = self.image.get_rect(topleft=(ship.rect.x, ship.rect.y))
        self.timer = time.get_ticks()

    def update(self, current_time, *args):
        if args:
            pantalla = args[-1]
            passed = current_time - self.timer
            if 300 < passed <= 600:
                pantalla.blit(self.image, self.rect)
        if current_time - self.timer > 900:
            self.kill()

class Life(sprite.Sprite): 
    def __init__(self, xpos, ypos):
        sprite.Sprite.__init__(self)
        self.image = IMAGES['ship']
        self.image = transform.scale(self.image, scale_size(23, 23))
        # Usar scale_position_x y scale_position_y para posicionar correctamente
        self.rect = self.image.get_rect(topleft=(scale_position_x(xpos), scale_position_y(ypos)))

    def update(self, *args):
        if args and hasattr(args[-1], "blit"):
            pantalla = args[-1]
            pantalla.blit(self.image, self.rect)

class Text(object):
    def __init__(self, textFont, size, message, color, xpos, ypos):
        self.font = font.Font(textFont, scale_value(size))
        self.surface = self.font.render(message, True, color)
        # Usar scale_position_x y scale_position_y para posicionar correctamente
        self.rect = self.surface.get_rect(topleft=(scale_position_x(xpos), scale_position_y(ypos)))

    def draw(self, surface):
        surface.blit(self.surface, self.rect)

class SpaceInvaders(object):
    def __init__(self):
        mixer.pre_init(44100, -16, 1, 4096)
        init()
        self.bullets = sprite.Group()
        self.allSprites = sprite.Group()
        self.shipAlive = True
        self.score = 0
        self.player = Ship()
        self.sounds = {
            'shoot': mixer.Sound('Sounds\shoot.wav'),
            'shoot2': mixer.Sound('Sounds\shoot2.wav')
        }
        self.allSprites.add(self.player)
        self.clock = time.Clock()
        self.caption = display.set_caption('Space Invaders')
        self.screen = SCREEN
        
        # Cargar y escalar fondos
        self.menu = image.load(IMAGE_PATH + 'image_second.webp')
        self.menu = transform.scale(self.menu, (GAME_WIDTH, GAME_HEIGHT))
        self.background = image.load(IMAGE_PATH + 'background.jpg')
        self.background = transform.scale(self.background, (GAME_WIDTH, GAME_HEIGHT))
        
        self.startGame = False
        self.mainScreen = True
        self.gameOver = False
        self.enemyPosition = ENEMY_DEFAULT_POSITION
        
        # Textos con posiciones escaladas
        self.titleText2 = Text(FONT, 25, 'Press any key to continue', WHITE, 201, 540)
        self.gameOverText = Text(FONT, 50, 'Game Over', WHITE, 250, 270)
        self.nextRoundText = Text(FONT, 50, 'Next Round', WHITE, 240, 270)
        self.scoreText = Text(FONT, 20, 'Score', WHITE, 5, 5)
        self.livesText = Text(FONT, 20, 'Lives ', WHITE, 640, 5)

        # Vidas con posiciones escaladas
        self.life1 = Life(715, 3)
        self.life2 = Life(742, 3)
        self.life3 = Life(769, 3)
        self.livesGroup = sprite.Group(self.life1, self.life2, self.life3)

    def reset(self, score):
        self.player = Ship()
        self.playerGroup = sprite.Group(self.player)
        self.explosionsGroup = sprite.Group()
        self.bullets = sprite.Group()
        self.mysteryShip = Mystery()
        self.mysteryGroup = sprite.Group(self.mysteryShip)
        self.enemyBullets = sprite.Group()
        self.make_enemies()
        self.allSprites = sprite.Group(self.player, self.enemies,
                                       self.livesGroup, self.mysteryShip)
        self.keys = key.get_pressed()

        self.timer = time.get_ticks()
        self.noteTimer = time.get_ticks()
        self.shipTimer = time.get_ticks()
        self.score = score
        self.create_audio()
        self.makeNewShip = False
        self.shipAlive = True

    def make_blockers(self, number):
        blockerGroup = sprite.Group()
        for row in range(4):
            for column in range(9):
                blocker = Blocker(10, GREEN, row, column)
                # Usar scale_position_x y scale_position_y para posicionar correctamente
                blocker.rect.x = scale_position_x(50 + (200 * number) + (column * 10))
                blocker.rect.y = scale_position_y(BLOCKERS_POSITION + (row * 10))
                blockerGroup.add(blocker)
        return blockerGroup

    def create_audio(self):
        self.sounds = {}

        for SoundName in ['shoot', 'shoot2', 'invaderkilled', 'mysterykilled', 'shipexplosion']:
            self.sounds[SoundName] = mixer.Sound(SOUND_PATH + '{}.wav'.format(SoundName))
            # Usar get_muteado() para obtener el estado actual
            self.sounds[SoundName].set_volume(0.0 if get_muteado() else 0.2)

        self.musicNotes = [mixer.Sound(SOUND_PATH + '{}.wav'.format(i)) for i in range(4)]
        for Sound in self.musicNotes:
            Sound.set_volume(0.0 if get_muteado() else 0.5)

        self.noteIndex = 0

    def play_main_music(self, currentTime):
        if currentTime - self.noteTimer > self.enemies.moveTime:
            self.note = self.musicNotes[self.noteIndex]
            if self.noteIndex < 3:
                self.noteIndex += 1
            else:
                self.noteIndex = 0

            self.note.play()
            self.noteTimer += self.enemies.moveTime

    @staticmethod
    def should_exit(evt):
        return evt.type == QUIT or (evt.type == KEYUP and evt.key == K_ESCAPE)

    def check_input(self):
        self.keys = key.get_pressed()

        for e in event.get():
            if self.should_exit(e):
                return True

            if e.type == KEYUP and self.mainScreen:
                self.allBlockers = sprite.Group(self.make_blockers(0),
                                                self.make_blockers(1),
                                                self.make_blockers(2),
                                                self.make_blockers(3))
                self.livesGroup.add(self.life1, self.life2, self.life3)
                self.reset(0)
                self.startGame = True
                self.mainScreen = False

            if e.type == KEYDOWN and self.startGame:
                if e.key == K_SPACE:
                    if len(self.bullets) == 0 and self.shipAlive:  # Solo se puede disparar si la nave está viva
                        if self.score < 1000:
                            bullet = Bullet(self.player.rect.x + scale_value(23), self.player.rect.y + scale_value(5), -1, 15, 'laser', 'center')
                            self.bullets.add(bullet)
                            self.allSprites.add(self.bullets)
                            self.sounds['shoot'].play()
                        else:
                            leftbullet = Bullet(self.player.rect.x + scale_value(8), self.player.rect.y + scale_value(5), -1, 15, 'laser', 'left')
                            rightbullet = Bullet(self.player.rect.x + scale_value(38), self.player.rect.y + scale_value(5), -1, 15, 'laser', 'right')
                            self.bullets.add(leftbullet)
                            self.bullets.add(rightbullet)
                            self.allSprites.add(self.bullets)
                            self.sounds['shoot2'].play()

        return False

    def make_enemies(self):
        enemies = EnemiesGroup(10, 5, self.enemyPosition)
        for row in range(5):
            for column in range(10):
                enemy = Enemy(row, column)
                # Usar scale_position_x y scale_position_y para posicionar correctamente
                enemy.rect.x = scale_position_x(157 + (column * 50))
                enemy.rect.y = scale_position_y(self.enemyPosition + (row * 45))
                enemies.add(enemy)

        self.enemies = enemies

    def make_enemies_shoot(self):
        if (time.get_ticks() - self.timer) > 700 and self.enemies:
            enemy = self.enemies.random_bottom()
            if enemy:
                # Posiciones correctamente escaladas para el disparo del enemigo
                self.enemyBullets.add(
                    Bullet(enemy.rect.x + scale_value(14), 
                        enemy.rect.y + scale_value(20), 1, 5,
                        'enemylaser', 'center'))
                self.allSprites.add(self.enemyBullets)
                self.timer = time.get_ticks()

    def calculate_score(self, row):
        scores = {0: 30,
                  1: 20,
                  2: 20,
                  3: 10,
                  4: 10,
                  5: choice([50, 100, 150, 300])
                  }

        score = scores[row]
        self.score += score
        return score

    def create_main_menu(self):
        # Este método se mantiene vacío ya que los comentarios indican que este código
        # ya no se está usando en la versión actual
        pass

    def check_collisions(self):
        sprite.groupcollide(self.bullets, self.enemyBullets, True, True)

        for enemy in sprite.groupcollide(self.enemies, self.bullets, True, True).keys():
            self.sounds['invaderkilled'].play()
            self.calculate_score(enemy.row)
            EnemyExplosion(enemy, self.explosionsGroup)
            self.gameTimer = time.get_ticks()

        for player in sprite.groupcollide(self.playerGroup, self.enemyBullets, True, True).keys():
            if self.life3.alive():
                self.life3.kill()
            elif self.life2.alive():
                self.life2.kill()
            elif self.life1.alive():
                self.life1.kill()
            else:
                self.gameOver = True
                self.startGame = False
                self.sounds['shipexplosion'].play()
            ShipExplosion(player, self.explosionsGroup)
            self.makeNewShip = True
            self.shipTimer = time.get_ticks()
            self.shipAlive = False

        # Usar un valor escalado correctamente para el límite inferior
        if self.enemies.bottom >= scale_position_y(540):
            sprite.groupcollide(self.enemies, self.playerGroup, True, True)
            if not self.player.alive() or self.enemies.bottom >= scale_position_y(GAME_HEIGHT):
                self.gameOver = True
                self.startGame = False



        for mystery in sprite.groupcollide(self.mysteryGroup, self.bullets,
                                        True, True).keys():
            mystery.mysteryEntered.stop()
            self.sounds['mysterykilled'].play()
            score = self.calculate_score(mystery.row)
            MysteryExplosion(mystery, score, self.explosionsGroup)
            newShip = Mystery()
            self.allSprites.add(newShip)
            self.mysteryGroup.add(newShip)

        # Usar un valor escalado correctamente para el límite inferior
        if self.enemies.bottom >= scale_position_y(540):
            sprite.groupcollide(self.enemies, self.playerGroup, True, True)
            if not self.player.alive() or self.enemies.bottom >= scale_position_y(GAME_HEIGHT):
                self.gameOver = True
                self.startGame = False

        sprite.groupcollide(self.bullets, self.allBlockers, True, True)
        sprite.groupcollide(self.enemyBullets, self.allBlockers, True, True)
        
        # Usar un valor escalado para BLOCKERS_POSITION
        if self.enemies.bottom >= scale_position_y(BLOCKERS_POSITION):
            sprite.groupcollide(self.enemies, self.allBlockers, False, True)

    def create_new_ship(self, createShip, currentTime):
        if createShip and (currentTime - self.shipTimer > 900):
            self.player = Ship()  # Creación de la nueva nave
            self.allSprites.add(self.player)
            self.playerGroup.add(self.player)
            self.makeNewShip = False
            self.shipAlive = True  # La nave está viva
            self.bullets = sprite.Group()  # Reiniciamos las balas para evitar que queden del anterior juego
            self.allSprites.add(self.bullets)  # Aseguramos que las balas se añaden correctamente al grupo de sprites

    def create_game_over(self, currentTime):
        self.screen.blit(self.background, (0, 0))
        passed = currentTime - self.timer
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

        for e in event.get():
            if self.should_exit(e):
                sys.exit()

    def main(self):
        # Ya no es necesario redefinir el tamaño de la pantalla aquí,
        # ya que se configuró correctamente en el inicio
        
        while True:
            salir = self.check_input()
            if salir:
                return 'menu'
            
            if self.mainScreen:
                self.screen.blit(self.background, (0, 0))
                self.screen.blit(self.menu, (0, 0))
                self.titleText2.draw(self.screen)
                self.create_main_menu()

            elif self.startGame:
                currentTime = time.get_ticks()
                self.screen.blit(self.background, (0, 0))

                if not self.enemies and not self.explosionsGroup:
                    if currentTime - self.gameTimer < 3000:
                        self.screen.blit(self.background, (0, 0))
                        self.scoreText2 = Text(FONT, 20, str(self.score), GREEN, 85, 5)
                        self.scoreText.draw(self.screen)
                        self.scoreText2.draw(self.screen)
                        self.nextRoundText.draw(self.screen)
                        self.livesText.draw(self.screen)
                        self.livesGroup.update(self.screen)
                    elif currentTime - self.gameTimer > 3000:
                        self.enemyPosition += ENEMY_MOVE_DOWN
                        self.reset(self.score)
                        self.gameTimer += 3000
                    self.allSprites.update(self.keys, currentTime, self.screen)

                else:
                    self.play_main_music(currentTime)
                    self.screen.blit(self.background, (0, 0))
                    self.allBlockers.update(self.screen)
                    self.scoreText2 = Text(FONT, 20, str(self.score), GREEN, 85, 5)
                    self.scoreText.draw(self.screen)
                    self.scoreText2.draw(self.screen)
                    self.livesText.draw(self.screen)
                    self.enemies.update(currentTime) # Mueve enemigos
                    self.allSprites.update(self.keys, currentTime, self.screen) # Mueve jugador, balas, etc.
                    self.explosionsGroup.update(currentTime) # Actualiza explosiones
                    self.check_collisions() # Verifica colisiones entre elementos
                    self.create_new_ship(self.makeNewShip, currentTime) # Crea nave nueva si fue destruida
                    self.make_enemies_shoot() # Los enemigos disparan

            elif self.gameOver: # Si el juego terminó
                currentTime = time.get_ticks()
                self.enemyPosition = ENEMY_DEFAULT_POSITION # Reinicia la posición de enemigos
                self.create_game_over(currentTime) # Muestra pantalla de Game Over

            display.update() # Actualiza la pantalla
            self.clock.tick(60) # Limita la velocidad de fotogramas a 60 FPS

if __name__ == "__main__":
    game = SpaceInvaders()
    game.main()