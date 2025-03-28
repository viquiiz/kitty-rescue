import os
import math
import random
import pygame

from os import listdir
from os.path import isfile, join

import constants as c
from background import Background

pygame.init()

pygame.display.set_caption("Kitty Rescue")

window = pygame.display.set_mode((c.WIDTH, c.HEIGHT))

def flip(sprites):
        return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path,f))]

    all_sprites = {}

    grouped_sprites = {}

    for image in images:  
        prefix = image.split("_")[0]  

        if prefix not in grouped_sprites:
            grouped_sprites[prefix] = []

        sprite = pygame.image.load(join(path, image)).convert_alpha()
        sprite = pygame.transform.scale(sprite, (width * 2, height * 2))

        grouped_sprites[prefix].append(sprite)

    for prefix, sprites in grouped_sprites.items():
        if direction:
            all_sprites[prefix + "_right"] = flip(sprites)  # Inverte a direção
            all_sprites[prefix + "_left"] = sprites
        else:
            all_sprites[prefix] = sprites

    return all_sprites

def get_block(size, img_path):

    image = pygame.image.load(img_path).convert_alpha()
    image = pygame.transform.scale(image, (size, size))  # Redimensiona corretamente
    return image 

class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.heigh = height
        self.name = name

    def draw(self, win, offset_x, offset_y):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y - offset_y))

class Block(Object):
    def __init__(self, x, y, size, block_img):
        super().__init__(x, y, size, size)
        block = get_block(size, block_img)
        self.image.blit(block, (0,0))
        self.mask = pygame.mask.from_surface(self.image)

class Cat(pygame.sprite.Sprite):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 48  # Defina conforme necessário
        self.height = 48
        self.sprites = load_sprite_sheets("img", "cats", self.width, self.height, True)
        spritesheet = random.choice(["idle_right", "idle_left"])
        self.current_sprite = self.sprites[spritesheet]  # Usa o primeiro frame da animação Idle
        self.frame_index = 0
        self.image = self.current_sprite[self.frame_index]  # Começa com a primeira imagem
        self.animation_speed = 0.1  # Ajuste a velocidade da animação

    def update(self):
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.current_sprite):
            self.frame_index = 0  

        self.image = self.current_sprite[int(self.frame_index)]  

    def draw(self, win, offset_x, offset_y):
        window.blit(self.image, (self.x - offset_x, self.y - offset_y))

class Game:
    def __init__(self):
        self.score = 0  # Pontuação inicial
        self.time_left = 30  # Tempo de jogo (em segundos)
        self.timer_event = pygame.USEREVENT + 1  # Definir um evento para o temporizador
        pygame.time.set_timer(self.timer_event, 1000)  # Evento de temporizador a cada 1 segundo
        self.font = pygame.font.SysFont('Roboto', 30)  # Fonte para o temporizador e pontuação
        self.cats_rescued = 0  # Contagem dos gatos resgatados

    def update_timer(self):
        if self.time_left > 0:
            self.time_left -= 1

    def draw(self, window):
        # Exibir o temporizador no canto superior esquerdo
        timer_text = self.font.render(f"Tempo: {self.time_left}s", True, (255, 255, 255))
        window.blit(timer_text, (10, 10))

        # Exibir a pontuação no canto superior direito
        score_text = self.font.render(f"Pontos: {self.score}", True, (255, 255, 255))
        window.blit(score_text, (c.WIDTH - 150, 10))

    def handle_cat_collision(self, player, cats):
        # Verifica se o jogador colidiu com algum gato
        for cat in cats[:]:
            if pygame.sprite.collide_mask(player, cat):  # Se houve colisão com o gato
                self.score += 10  # Aumenta a pontuação por resgatar um gato
                self.cats_rescued += 1  # Incrementa o número de gatos resgatados
                cats.remove(cat)  # Remove o gato da lista
                break

class Player(pygame.sprite.Sprite):
    COLOR = c.PLAYER_COLOR
    GRAVITY = c.GRAVITY
    SPRITES = load_sprite_sheets("img", "main_char", 64, 64, True)
    ANITMATION_DELAY = 5

    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0

    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0
    
    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self):
        sprite_sheet = 'idle'
        if self.y_vel < 0:
            if self.jump_count > 0:
                sprite_sheet = 'jump'
        elif self.y_vel  > self.GRAVITY * 2:
                sprite_sheet = 'fall'
        elif self.x_vel != 0:
            sprite_sheet = 'run'

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANITMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        # self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        
        self.rect = pygame.Rect(self.rect.x, self.rect.y, 109, 109)

        self.mask = pygame.mask.from_surface(self.sprite)
    
    def draw(self, win, offset_x, offset_y):
        # PARA VISUALIZAR O RECT DO PERSONAGEM
        # border_color = (255, 0, 0)  # Cor da borda (vermelha, por exemplo)
        # border_width = 2  # Largura da borda
        # pygame.draw.rect(win, border_color, self.rect, border_width)  # Desenha a borda

        # Desenha o sprite do personagem
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y - offset_y))

def draw(window, cats, background, player, objects, game, offset_x, offset_y):
    for tile_image, x, y in background["sky4"]:
        window.blit(tile_image, (x, y))

    for tile_image, x, y in background["sky3"]:
        window.blit(tile_image, (x, y))

    for tile_image, x, y in background["sky2"]:
        window.blit(tile_image, (x, y))

    for tile_image, x, y in background["sky1"]:
        window.blit(tile_image, (x, y))

    for obj in objects:
        obj.draw(window, offset_x, offset_y)

    for cat in cats:
        cat.draw(window, offset_x, offset_y)

    player.draw(window, offset_x, offset_y)

    game.draw(window)

    pygame.display.update()

def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()

        collided_objects.append(obj)

    return collided_objects

def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break
    
    player.move(-dx, 0)
    player.update()
    return collided_object

def handle_move(player, objects):
    keys = pygame.key.get_pressed()

    player.x_vel = 0
    collide_left = collide(player, objects, - c.PLAYER_VEL * 2)
    collide_right = collide(player, objects, c.PLAYER_VEL * 2)

    player.x_vel = 0
    if keys[pygame.K_LEFT] and not collide_left: 
        player.move_left(c.PLAYER_VEL)
    if keys[pygame.K_RIGHT] and not collide_right: 
        player.move_right(c.PLAYER_VEL)

    handle_vertical_collision(player, objects, player.y_vel)

def main(window):
    clock = pygame.time.Clock()
    game = Game()

    # Carregar todos os tiles e escolher as imagens
    tiles_folder = os.path.join("assets", "img", "terrain", "PNG", "Tiles")
    sky_tiles_1, sky_tiles_2, sky_tiles_3, sky_tiles_4 = Background.get_background(tiles_folder)

    block_size = 96 

    background = Background.generate_bg(sky_tiles_1, sky_tiles_2, sky_tiles_3, sky_tiles_4)

    player = Player(800, 600, 50, 50)
    cats = [
        Cat(600,520)
        , Cat(450,50)
        , Cat(2100,520)
        , Cat(1700,520)
        , Cat(800,-50)

    ]

    ground_path = join("assets", "img", "terrain", "PNG", "Tiles")
    
    objects = [
        # Chão camada -1
            Block(0, c.HEIGHT, block_size, f"{ground_path}/tile75.png")
            , Block(block_size, c.HEIGHT, block_size, f"{ground_path}/blank.png")
            , Block(block_size *2, c.HEIGHT, block_size, f"{ground_path}/blank.png") 
            , Block(block_size *3, c.HEIGHT, block_size, f"{ground_path}/blank.png")
            , Block(block_size *4, c.HEIGHT, block_size, f"{ground_path}/blank.png")
            , Block(block_size *5, c.HEIGHT, block_size, f"{ground_path}/blank.png")
            , Block(block_size *6, c.HEIGHT, block_size, f"{ground_path}/blank.png")
            , Block(block_size *7, c.HEIGHT, block_size, f"{ground_path}/blank.png")
            , Block(block_size *8, c.HEIGHT, block_size, f"{ground_path}/blank.png")
            , Block(block_size *9, c.HEIGHT, block_size, f"{ground_path}/blank.png")
            , Block(block_size *10, c.HEIGHT, block_size, f"{ground_path}/blank.png")
            , Block(block_size *11, c.HEIGHT, block_size, f"{ground_path}/blank.png")
            , Block(block_size *12, c.HEIGHT, block_size, f"{ground_path}/blank.png")
            , Block(block_size *13, c.HEIGHT, block_size, f"{ground_path}/blank.png")
            , Block(block_size *14, c.HEIGHT, block_size, f"{ground_path}/blank.png")
            , Block(block_size *15, c.HEIGHT, block_size, f"{ground_path}/blank.png")
            , Block(block_size *16, c.HEIGHT, block_size, f"{ground_path}/blank.png")
            , Block(block_size *17, c.HEIGHT, block_size, f"{ground_path}/blank.png")
            , Block(block_size *18, c.HEIGHT, block_size, f"{ground_path}/tile53.png")
            , Block(block_size *20, c.HEIGHT, block_size, f"{ground_path}/tile55.png")
            , Block(block_size *21, c.HEIGHT, block_size, f"{ground_path}/blank.png")
            , Block(block_size *22, c.HEIGHT, block_size, f"{ground_path}/blank.png")
            , Block(block_size *23, c.HEIGHT, block_size, f"{ground_path}/blank.png")
            , Block(block_size *24, c.HEIGHT, block_size, f"{ground_path}/blank.png")
            , Block(block_size *25, c.HEIGHT, block_size, f"{ground_path}/blank.png")
            , Block(block_size *26, c.HEIGHT, block_size, f"{ground_path}/blank.png")
            , Block(block_size *27, c.HEIGHT, block_size, f"{ground_path}/blank.png")
            , Block(block_size *28, c.HEIGHT, block_size, f"{ground_path}/blank.png")
            , Block(block_size *29, c.HEIGHT, block_size, f"{ground_path}/blank.png")
            , Block(block_size *30, c.HEIGHT, block_size, f"{ground_path}/blank.png")
            , Block(block_size *31, c.HEIGHT, block_size, f"{ground_path}/blank.png")
            , Block(block_size *32, c.HEIGHT, block_size, f"{ground_path}/blank.png")

        # Chão camada 1
            , Block(0, c.HEIGHT - block_size, block_size, f"{ground_path}/tile55.png")
            , Block(block_size, c.HEIGHT - block_size, block_size, f"{ground_path}/blank.png")
            , Block(block_size *2, c.HEIGHT - block_size, block_size, f"{ground_path}/blank.png") 
            , Block(block_size *3, c.HEIGHT - block_size, block_size, f"{ground_path}/blank.png")
            , Block(block_size *4, c.HEIGHT - block_size, block_size, f"{ground_path}/blank.png")
            , Block(block_size *5, c.HEIGHT - block_size, block_size, f"{ground_path}/blank.png")
            , Block(block_size *6, c.HEIGHT - block_size, block_size, f"{ground_path}/blank.png")
            , Block(block_size *7, c.HEIGHT - block_size, block_size, f"{ground_path}/blank.png")
            , Block(block_size *8, c.HEIGHT - block_size, block_size, f"{ground_path}/blank.png")
            , Block(block_size *9, c.HEIGHT - block_size, block_size, f"{ground_path}/blank.png")
            , Block(block_size *10, c.HEIGHT - block_size, block_size, f"{ground_path}/blank.png")
            , Block(block_size *11, c.HEIGHT - block_size, block_size, f"{ground_path}/blank.png")
            , Block(block_size *12, c.HEIGHT - block_size, block_size, f"{ground_path}/blank.png")
            , Block(block_size *13, c.HEIGHT - block_size, block_size, f"{ground_path}/blank.png")
            , Block(block_size *14, c.HEIGHT - block_size, block_size, f"{ground_path}/blank.png")
            , Block(block_size *15, c.HEIGHT - block_size, block_size, f"{ground_path}/blank.png")
            , Block(block_size *16, c.HEIGHT - block_size, block_size, f"{ground_path}/blank.png")
            , Block(block_size *17, c.HEIGHT - block_size, block_size, f"{ground_path}/blank.png")
            , Block(block_size *18, c.HEIGHT - block_size, block_size, f"{ground_path}/tile53.png")
            , Block(block_size *20, c.HEIGHT - block_size, block_size, f"{ground_path}/tile55.png")
            , Block(block_size *21, c.HEIGHT - block_size, block_size, f"{ground_path}/blank.png")
            , Block(block_size *22, c.HEIGHT - block_size, block_size, f"{ground_path}/blank.png")
            , Block(block_size *23, c.HEIGHT - block_size, block_size, f"{ground_path}/blank.png")
            , Block(block_size *24, c.HEIGHT - block_size, block_size, f"{ground_path}/blank.png")
            , Block(block_size *25, c.HEIGHT - block_size, block_size, f"{ground_path}/blank.png")
            , Block(block_size *26, c.HEIGHT - block_size, block_size, f"{ground_path}/blank.png")
            , Block(block_size *27, c.HEIGHT - block_size, block_size, f"{ground_path}/blank.png")
            , Block(block_size *28, c.HEIGHT - block_size, block_size, f"{ground_path}/blank.png")
            , Block(block_size *29, c.HEIGHT - block_size, block_size, f"{ground_path}/blank.png")
            , Block(block_size *30, c.HEIGHT - block_size, block_size, f"{ground_path}/blank.png")
            , Block(block_size *31, c.HEIGHT - block_size, block_size, f"{ground_path}/blank.png")
            , Block(block_size *32, c.HEIGHT - block_size, block_size, f"{ground_path}/blank.png")

        # Chão camada 2
            , Block(0, c.HEIGHT - block_size *2, block_size, f"{ground_path}/tile55.png")
            , Block(block_size, c.HEIGHT - block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *2, c.HEIGHT - block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *3, c.HEIGHT - block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *4, c.HEIGHT - block_size *2, block_size, f"{ground_path}/tile39.png")
            , Block(block_size *5, c.HEIGHT - block_size *2, block_size, f"{ground_path}/tile40.png")
            , Block(block_size *6, c.HEIGHT - block_size *2, block_size, f"{ground_path}/tile37.png")
            , Block(block_size *7, c.HEIGHT - block_size *2, block_size, f"{ground_path}/tile47.png")
            , Block(block_size *8, c.HEIGHT - block_size *2, block_size, f"{ground_path}/chao_g.png")
            , Block(block_size *9, c.HEIGHT - block_size *2, block_size, f"{ground_path}/tile72.png")
            , Block(block_size *10, c.HEIGHT - block_size *2, block_size, f"{ground_path}/tile29.png")
            , Block(block_size *11, c.HEIGHT - block_size *2, block_size, f"{ground_path}/tile51.png")
            , Block(block_size *12, c.HEIGHT - block_size *2, block_size, f"{ground_path}/tile49.png")
            , Block(block_size *13, c.HEIGHT - block_size *2, block_size, f"{ground_path}/tile95.png")
            , Block(block_size *14, c.HEIGHT - block_size *2, block_size, f"{ground_path}/tile45.png")
            , Block(block_size *15, c.HEIGHT - block_size *2, block_size, f"{ground_path}/tile32.png")
            , Block(block_size *16, c.HEIGHT - block_size *2, block_size, f"{ground_path}/tile47.png")
            , Block(block_size *17, c.HEIGHT - block_size *2, block_size, f"{ground_path}/tile98.png")
            , Block(block_size *18, c.HEIGHT - block_size *2, block_size, f"{ground_path}/tile30.png")
            , Block(block_size *20, c.HEIGHT - block_size *2, block_size, f"{ground_path}/tile31.png")
            , Block(block_size *21, c.HEIGHT - block_size *2, block_size, f"{ground_path}/tile45.png")
            , Block(block_size *22, c.HEIGHT - block_size *2, block_size, f"{ground_path}/tile32.png")
            , Block(block_size *23, c.HEIGHT - block_size *2, block_size, f"{ground_path}/tile47.png")
            , Block(block_size *24, c.HEIGHT - block_size *2, block_size, f"{ground_path}/tile95.png")
            , Block(block_size *25, c.HEIGHT - block_size *2, block_size, f"{ground_path}/tile91.png")
            , Block(block_size *26, c.HEIGHT - block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *27, c.HEIGHT - block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *28, c.HEIGHT - block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *29, c.HEIGHT - block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *30, c.HEIGHT - block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *31, c.HEIGHT - block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *32, c.HEIGHT - block_size *2, block_size, f"{ground_path}/blank.png")

        # Chão camada 3
            , Block(0, c.HEIGHT - block_size *3, block_size, f"{ground_path}/tile31.png")
            , Block(block_size, c.HEIGHT - block_size *3, block_size, f"{ground_path}/tile98.png")
            , Block(block_size *2, c.HEIGHT - block_size *3, block_size, f"{ground_path}/tile32.png")
            , Block(block_size *3, c.HEIGHT - block_size *3, block_size, f"{ground_path}/tile72.png")
            , Block(block_size *4, c.HEIGHT - block_size *3, block_size, f"{ground_path}/tile19.png")
            , Block(block_size *5, c.HEIGHT - block_size *3, block_size, f"{ground_path}/tile16.png")
            , Block(block_size *6, c.HEIGHT - block_size *3, block_size, f"{ground_path}/tile17.png")
            , Block(block_size *25, c.HEIGHT - block_size *3, block_size, f"{ground_path}/tile103.png")
            , Block(block_size *26, c.HEIGHT - block_size *3, block_size, f"{ground_path}/tile104.png")
            , Block(block_size *27, c.HEIGHT - block_size *3, block_size, f"{ground_path}/tile104.png")
            , Block(block_size *28, c.HEIGHT - block_size *3, block_size, f"{ground_path}/tile104.png")
            , Block(block_size *29, c.HEIGHT - block_size *3, block_size, f"{ground_path}/tile104.png")
            , Block(block_size *30, c.HEIGHT - block_size *3, block_size, f"{ground_path}/tile104.png")
            , Block(block_size *31, c.HEIGHT - block_size *3, block_size, f"{ground_path}/tile104.png")
            , Block(block_size *32, c.HEIGHT - block_size *3, block_size, f"{ground_path}/tile104.png")
            , Block(block_size *23, c.HEIGHT - block_size *3, block_size, f"{ground_path}/tile87.png")
            , Block(block_size *24, c.HEIGHT - block_size *3, block_size, f"{ground_path}/tile88.png")

        # Chão camada 4
            , Block(0, c.HEIGHT - block_size *4, block_size, f"{ground_path}/tile103.png")
            , Block(block_size, c.HEIGHT - block_size *4, block_size, f"{ground_path}/tile101.png")
            , Block(block_size *2, c.HEIGHT - block_size *4, block_size, f"{ground_path}/tile87.png")
            , Block(block_size *3, c.HEIGHT - block_size *4, block_size, f"{ground_path}/tile88.png")

            , Block(block_size *15, c.HEIGHT - block_size *3.5, block_size, f"{ground_path}/tile31.png")
            , Block(block_size *16, c.HEIGHT - block_size *3.5, block_size, f"{ground_path}/tile30.png")

            , Block(block_size *23, c.HEIGHT - block_size *4, block_size, f"{ground_path}/tile87.png")
            , Block(block_size *24, c.HEIGHT - block_size *4, block_size, f"{ground_path}/tile88.png")

        # Chão camada 5
            , Block(block_size *2, c.HEIGHT - block_size *5, block_size, f"{ground_path}/tile87.png")
            , Block(block_size *3, c.HEIGHT - block_size *5, block_size, f"{ground_path}/tile88.png")

            , Block(block_size *18, c.HEIGHT - block_size *5, block_size, f"{ground_path}/tile31.png")
            , Block(block_size *19, c.HEIGHT - block_size *5, block_size, f"{ground_path}/tile72.png")
            , Block(block_size *20, c.HEIGHT - block_size *5, block_size, f"{ground_path}/tile30.png")

            , Block(block_size *23, c.HEIGHT - block_size *5, block_size, f"{ground_path}/tile87.png")
            , Block(block_size *24, c.HEIGHT - block_size *5, block_size, f"{ground_path}/tile88.png")

        # Chão camada 6
            , Block(block_size *2, c.HEIGHT - block_size *6, block_size, f"{ground_path}/tile87.png")
            , Block(block_size *3, c.HEIGHT - block_size *6, block_size, f"{ground_path}/tile88.png")
            , Block(block_size *23, c.HEIGHT - block_size *6, block_size, f"{ground_path}/tile87.png")
            , Block(block_size *24, c.HEIGHT - block_size *6, block_size, f"{ground_path}/tile88.png")

        # Chão camada 7
            , Block(block_size *2, c.HEIGHT - block_size *7, block_size, f"{ground_path}/tile87.png")
            , Block(block_size *3, c.HEIGHT - block_size *7, block_size, f"{ground_path}/tile88.png")
            , Block(block_size *4, c.HEIGHT - block_size *7, block_size, f"{ground_path}/tile72.png")
            , Block(block_size *5, c.HEIGHT - block_size *7, block_size, f"{ground_path}/tile30.png")

            , Block(block_size *13, c.HEIGHT - block_size *7, block_size, f"{ground_path}/tile31.png")
            , Block(block_size *14, c.HEIGHT - block_size *7, block_size, f"{ground_path}/tile72.png")
            , Block(block_size *15, c.HEIGHT - block_size *7, block_size, f"{ground_path}/tile72.png")
            , Block(block_size *16, c.HEIGHT - block_size *7, block_size, f"{ground_path}/tile30.png")

            , Block(block_size *23, c.HEIGHT - block_size *7, block_size, f"{ground_path}/tile87.png")
            , Block(block_size *24, c.HEIGHT - block_size *7, block_size, f"{ground_path}/tile88.png")

        # Chão camada 8
            , Block(0, c.HEIGHT - block_size *8, block_size, f"{ground_path}/tile112.png")
            , Block(block_size, c.HEIGHT - block_size *8, block_size, f"{ground_path}/tile10.png")
            , Block(block_size *2, c.HEIGHT - block_size *8, block_size, f"{ground_path}/tile68.png")
            , Block(block_size *3, c.HEIGHT - block_size *8, block_size, f"{ground_path}/tile62.png")

            , Block(block_size *8, c.HEIGHT - block_size *8, block_size, f"{ground_path}/tile31.png")
            , Block(block_size *9, c.HEIGHT - block_size *8, block_size, f"{ground_path}/tile72.png")
            , Block(block_size *10, c.HEIGHT - block_size *8, block_size, f"{ground_path}/tile72.png")
            , Block(block_size *11, c.HEIGHT - block_size *8, block_size, f"{ground_path}/tile30.png")

            , Block(block_size *23, c.HEIGHT - block_size *8, block_size, f"{ground_path}/tile87.png")
            , Block(block_size *24, c.HEIGHT - block_size *8, block_size, f"{ground_path}/tile88.png")

        # Chão camada 9
            , Block(0, c.HEIGHT - block_size *9, block_size, f"{ground_path}/tile87.png")
            , Block(block_size, c.HEIGHT - block_size *9, block_size, f"{ground_path}/tile127.png")
            , Block(block_size *2, c.HEIGHT - block_size *9, block_size, f"{ground_path}/tile10.png")

            , Block(block_size *23, c.HEIGHT - block_size *9, block_size, f"{ground_path}/tile69.png")
            , Block(block_size *24, c.HEIGHT - block_size *9, block_size, f"{ground_path}/tile63.png")

        # Chão camada 10
            , Block(0, c.HEIGHT - block_size *10, block_size, f"{ground_path}/tile87.png")
            , Block(block_size, c.HEIGHT - block_size *10, block_size, f"{ground_path}/blank.png")
            , Block(block_size *2, c.HEIGHT - block_size *10, block_size, f"{ground_path}/tile127.png")
            , Block(block_size *3, c.HEIGHT - block_size *10, block_size, f"{ground_path}/tile81.png")
            , Block(block_size *4, c.HEIGHT - block_size *10, block_size, f"{ground_path}/tile111.png")

            , Block(block_size *23, c.HEIGHT - block_size *10, block_size, f"{ground_path}/tile2.png")
            , Block(block_size *24, c.HEIGHT - block_size *10, block_size, f"{ground_path}/tile3.png")
            , Block(block_size *25, c.HEIGHT - block_size *10, block_size, f"{ground_path}/tile1111.png")
            , Block(block_size *26, c.HEIGHT - block_size *10, block_size, f"{ground_path}/tile81.png")
            , Block(block_size *27, c.HEIGHT - block_size *10, block_size, f"{ground_path}/tile81.png")
            , Block(block_size *28, c.HEIGHT - block_size *10, block_size, f"{ground_path}/tile111.png")
        
        # Chão camada 11
            , Block(0, c.HEIGHT - block_size *11, block_size, f"{ground_path}/tile87.png")
            , Block(block_size, c.HEIGHT - block_size *11, block_size, f"{ground_path}/blank.png")
            , Block(block_size *2, c.HEIGHT - block_size *11, block_size, f"{ground_path}/blank.png")
            , Block(block_size *3, c.HEIGHT - block_size *11, block_size, f"{ground_path}/blank.png")
            , Block(block_size *4, c.HEIGHT - block_size *11, block_size, f"{ground_path}/tile88.png")

            , Block(block_size *20, c.HEIGHT - block_size *11, block_size, f"{ground_path}/tile113.png")
            , Block(block_size *21, c.HEIGHT - block_size *11, block_size, f"{ground_path}/tile81.png")
            , Block(block_size *22, c.HEIGHT - block_size *11, block_size, f"{ground_path}/tile81.png")
            , Block(block_size *23, c.HEIGHT - block_size *11, block_size, f"{ground_path}/tile128.png")
            , Block(block_size *24, c.HEIGHT - block_size *11, block_size, f"{ground_path}/tile118.png")
            , Block(block_size *25, c.HEIGHT - block_size *11, block_size, f"{ground_path}/blank.png")
            , Block(block_size *26, c.HEIGHT - block_size *11, block_size, f"{ground_path}/blank.png")
            , Block(block_size *27, c.HEIGHT - block_size *11, block_size, f"{ground_path}/blank.png")

        # Chão camada 12
            , Block(0, c.HEIGHT - block_size *12, block_size, f"{ground_path}/tile87.png")
            , Block(block_size, c.HEIGHT - block_size *12, block_size, f"{ground_path}/blank.png")
            , Block(block_size *2, c.HEIGHT - block_size *12, block_size, f"{ground_path}/blank.png")
            , Block(block_size *3, c.HEIGHT - block_size *12, block_size, f"{ground_path}/blank.png")
            , Block(block_size *4, c.HEIGHT - block_size *12, block_size, f"{ground_path}/tile88.png")

            , Block(block_size *20, c.HEIGHT - block_size *12, block_size, f"{ground_path}/blank.png")
            , Block(block_size *21, c.HEIGHT - block_size *12, block_size, f"{ground_path}/blank.png")
            , Block(block_size *22, c.HEIGHT - block_size *12, block_size, f"{ground_path}/blank.png")
            , Block(block_size *23, c.HEIGHT - block_size *12, block_size, f"{ground_path}/blank.png")
            , Block(block_size *24, c.HEIGHT - block_size *12, block_size, f"{ground_path}/blank.png")
            , Block(block_size *25, c.HEIGHT - block_size *12, block_size, f"{ground_path}/blank.png")
            , Block(block_size *26, c.HEIGHT - block_size *12, block_size, f"{ground_path}/blank.png")
            , Block(block_size *27, c.HEIGHT - block_size *12, block_size, f"{ground_path}/blank.png")
            , Block(block_size *28, c.HEIGHT - block_size *12, block_size, f"{ground_path}/blank.png")

        # Chão camada 13
            , Block(0, c.HEIGHT - block_size *13, block_size, f"{ground_path}/tile68.png")
            , Block(block_size, c.HEIGHT - block_size *13, block_size, f"{ground_path}/tile72.png")
            , Block(block_size *2, c.HEIGHT - block_size *13, block_size, f"{ground_path}/tile72.png")
            , Block(block_size *3, c.HEIGHT - block_size *13, block_size, f"{ground_path}/tile72.png")
            , Block(block_size *4, c.HEIGHT - block_size *13, block_size, f"{ground_path}/tile63.png")
        ]

    offset_x = 0
    offset_y = 0
    scroll_area_width = 200
    scroll_area_hight = 300

    run = True
    while run:
        clock.tick(c.FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
                
            if event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_SPACE or event.key == pygame.K_UP)and player.jump_count <2:
                    player.jump()
            
            if event.type == game.timer_event:  # Atualiza o tempo a cada segundo
                game.update_timer()
                    
        player.loop(c.FPS)
        handle_move(player, objects)

        for cat in cats:
            cat.update()  # Atualiza a animação de cada gato

        game.handle_cat_collision(player, cats)

        draw(window, cats, background, player, objects, game, offset_x, offset_y)

        if (player.rect.right - offset_x >= c.WIDTH - scroll_area_width and player.x_vel > 0) or (
                player.rect.left - offset_x <= c.WIDTH - scroll_area_width and player.x_vel < 0):
            offset_x += player.x_vel

        if (player.rect.top - offset_y >= c.HEIGHT - scroll_area_hight and player.y_vel > 0) or (
                player.rect.bottom- offset_y <= c.HEIGHT - scroll_area_hight and player.y_vel < 0):
            offset_y += player.y_vel

    pygame.quit()
    quit()


if __name__ == "__main__":
    main(window)