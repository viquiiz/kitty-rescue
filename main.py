import os
import math
import random
import pygame

from os import listdir
from os.path import isfile, join

import constants as c
from background import Background

pygame.init()
pygame.mixer.init()

window = pygame.display.set_mode((c.WIDTH, c.HEIGHT))
rescued_cats = []

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
        super().__init__()  # Chama o construtor da classe Sprite
        self.x = x
        self.y = y
        self.width = 48  # Defina conforme necessário
        self.height = 48
        self.sprites = load_sprite_sheets("img", "cats", self.width, self.height, True)
        self.spritesheet = random.choice(["idle_right", "idle_left"])
        self.current_sprite = self.sprites[self.spritesheet]  # Usa o primeiro frame da animação Idle
        self.frame_index = 0
        self.image = self.current_sprite[self.frame_index]  # Começa com a primeira imagem
        self.animation_speed = 0.1  # Ajuste a velocidade da animação
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.rescued = False
        self.is_jumping = False
        self.jump_height = 0
        self.max_jump_height = 100  # Altura máxima do pulo
        self.fall_speed = 5  # Velocidade de queda do gato

    def update(self):
        if self.rescued:
            self.jump_animation()

        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.current_sprite):
            self.frame_index = 0  

        self.image = self.current_sprite[int(self.frame_index)]  
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def jump_animation(self):
        if 'right' in self.spritesheet:
            self.current_sprite = self.sprites["jump_right"]
        else:
            self.current_sprite = self.sprites["jump_left"]

        # O gato sobe até atingir a altura máxima do pulo
        if self.jump_height < self.max_jump_height:
            self.y -= 1  # Movimenta o gato para cima
            self.jump_height += 3
        # O gato começa a cair após atingir a altura máxima
        elif self.jump_height >= self.max_jump_height:  # Certifique-se de que o gato caia até o chão
            if self.y < 999999:  # Certifique-se de que o gato caia até o chão (ajuste o valor para o chão do seu jogo)
                self.y += self.fall_speed

    def draw(self, window, offset_x, offset_y):
        window.blit(self.image, (self.x - offset_x, self.y - offset_y))

class Game:
    def __init__(self):
        self.score = 0  # Pontuação inicial
        self.time_left = 30  # Tempo de jogo (em segundos)
        self.timer_event = pygame.USEREVENT + 1  # Definir um evento para o temporizador
        pygame.time.set_timer(self.timer_event, 1000)  # Evento de temporizador a cada 1 segundo
        self.font = pygame.font.SysFont('Roboto', 30)  # Fonte para o temporizador e pontuação
        self.cats_rescued = 0  # Contagem dos gatos resgatados
        self.total_cats = 5

    def update_timer(self):
        if self.time_left > 0:
            self.time_left -= 1

    def draw(self, window):
        # Exibir o temporizador no canto superior esquerdo
        timer_text = self.font.render(f"Tempo: {self.time_left}s", True, (255, 255, 255))
        window.blit(timer_text, (10, 10))

        # Exibir a pontuação no canto superior direito
        score_text = self.font.render(f"Gatos resgatados: {self.cats_rescued}", True, (255, 255, 255))
        window.blit(score_text, (c.WIDTH - 300, 10))

    def handle_cat_collision(self, player, cats):
        # Verifica se o jogador colidiu com algum gato
        global rescued_cats
        for cat in cats:
            if pygame.sprite.collide_mask(player, cat):  # Se houve colisão com o gato
                if cat not in rescued_cats:
                    cat.rescued = True
                    rescued_cats.append(cat)

                    if 'right' in cat.spritesheet:
                        self.current_sprite = cat.sprites["jump_right"]
                    else:
                        self.current_sprite = cat.sprites["jump_left"]

                    pygame.mixer.Sound("assets/sound/retro_game_sound_effects_-_all_sounds/SoundStartLevel.wav").play()
                    cat.jump_animation()

                    self.score += 1  # Aumenta a pontuação por resgatar um gato
                    self.cats_rescued += 1  # Incrementa o número de gatos resgatados
                break

    def show_end_screen(self, window, player_dead=False):
        pygame.mixer.music.stop()

        # Definir as mensagens de vitória e derrota
        if player_dead:
            pygame.mixer.music.load("assets\sound\mp3_8bit Action Jingle & Mini Loop\GameOver (Jingle).mp3") 
            pygame.mixer.music.play(0, 0.0) 
            background_image = pygame.image.load('assets/img/telas_final/1.png')
            final_msg_font = pygame.font.SysFont("Open Sans", 30)
            final_msg_text = final_msg_font.render("Precione ENTER para tentar novamente ou ESC para sair", True, (255, 255, 255))
            final_msg_text_rect = final_msg_text.get_rect(center=(500, 230))
            message = ""
        elif self.cats_rescued == self.total_cats:
            pygame.mixer.music.load("assets\sound\mp3_8bit Action Jingle & Mini Loop\Stage Clear Long (Jingle).mp3") 
            pygame.mixer.music.play(0, 0.0) 
            background_image = pygame.image.load('assets/img/telas_final/3.png')
            final_msg_font = pygame.font.SysFont("Open Sans", 30)
            final_msg_text = final_msg_font.render("Precione ENTER para jogar novamente ou ESC para sair", True, (255, 255, 255))
            final_msg_text_rect = final_msg_text.get_rect(center=(500, 550))
            message = "Parabéns! Você conseguiu resgatar todos os gatos!"
        elif self.cats_rescued > 0:
            pygame.mixer.music.load("assets\sound\mp3_8bit Action Jingle & Mini Loop\Stage Clear Long (Jingle).mp3") 
            pygame.mixer.music.play(0, 0.0) 
            background_image = pygame.image.load('assets/img/telas_final/3.png')
            final_msg_font = pygame.font.SysFont("Open Sans", 30)
            final_msg_text = final_msg_font.render("Precione ENTER para jogar novamente ou ESC para sair", True, (255, 255, 255))
            final_msg_text_rect = final_msg_text.get_rect(center=(500, 550))
            message = f"Você resgatou {self.cats_rescued} gatos! Boa tentativa!"
        else:
            pygame.mixer.music.load("assets\sound\mp3_8bit Action Jingle & Mini Loop\GameOver (Jingle).mp3") 
            pygame.mixer.music.play(0, 0.0) 
            background_image = pygame.image.load('assets/img/telas_final/2.png')
            final_msg_font = pygame.font.SysFont("Open Sans", 30)
            final_msg_text = final_msg_font.render("Precione ENTER para tentar novamente ou ESC para sair", True, (255, 255, 255))
            final_msg_text_rect = final_msg_text.get_rect(center=(500, 230))
            message = ""

        background_image = pygame.transform.scale(background_image, (c.WIDTH, c.HEIGHT))
        window.blit(background_image, (0, 0))

        font = pygame.font.SysFont("Open Sans", 40)
        text = font.render(message, True, (255, 255, 255))

        text_rect = text.get_rect(center=(500, 450))
        window.blit(text, text_rect)

        # Exibir a tela
        pygame.display.update()
        pygame.time.delay(3000)

        window.blit(final_msg_text, final_msg_text_rect)

        pygame.display.update()

        # Loop para esperar a interação do usuário
        waiting_for_key = True
        while waiting_for_key:
            for event in pygame.event.get():                
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:  # Verifica se o jogador apertou Enter
                        main(window)  # Reinicia o jogo
                        waiting_for_key = False
                    elif event.key == pygame.K_ESCAPE:  # Verifica se o jogador apertou Escape
                        pygame.quit()
                        quit()


    def check_end_game(self, window):
        # Verifica se o tempo acabou ou se todos os gatos foram resgatados
        if self.time_left <= 0 or self.cats_rescued == self.total_cats:
            self.show_end_screen(window)  # Exibe a tela de fim de jogo
            return True
        return False

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
        self.lives = 3
        self.is_dead = False    

    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            pygame.mixer.Sound("assets/sound/retro_game_sound_effects_-_all_sounds/SoundJumpHah.wav").play()
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
        pygame.mixer.Sound("assets/sound/retro_game_sound_effects_-_all_sounds/SoundLand2.wav").play()
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
        if self.rect.y > c.HEIGHT + 300:  # Se o jogador ultrapassar a altura da tela
            self.die(3)

        self.rect = pygame.Rect(self.rect.x, self.rect.y, 109, 109)

        self.mask = pygame.mask.from_surface(self.sprite)

    def die(self, lives):
        self.lives -= lives  # Subtrai uma vida
        if self.lives <= 0:
            self.is_dead = True  # Marca o jogador como morto

            # Aqui você pode reiniciar o jogo ou executar alguma outra ação

        else:
            self.x = 800  # Coloque a posição inicial do jogador de volta
            self.y = 600
            self.is_dead = False
            print(f"Você tem {self.lives} vidas restantes.")

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

def initial_state():
    pygame.display.set_caption("Kitty Rescue")
    pygame.mixer.music.load("assets\sound\mp3_8bit Action Jingle & Mini Loop\Invincible (Loop)_BPM155.mp3")
    pygame.mixer.music.play(-1, 0.0)

    game = Game()  # Criar uma nova instância do jogo
    player = Player(800, 600, 50, 50)  # Posição inicial do personagem

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

    objects =[
        # Chão camada -2
            Block(0, c.HEIGHT + block_size *2, block_size, f"{ground_path}/tile75.png")
            , Block(block_size, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *2, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png") 
            , Block(block_size *3, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *4, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *5, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *6, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *7, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *8, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *9, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *10, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *11, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *12, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *13, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *14, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *15, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *16, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *17, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *18, c.HEIGHT + block_size *2, block_size, f"{ground_path}/tile53.png")
            , Block(block_size *20, c.HEIGHT + block_size *2, block_size, f"{ground_path}/tile55.png")
            , Block(block_size *21, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *22, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *23, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *24, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *25, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *26, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *27, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *28, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *29, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *30, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *31, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *32, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png")

        # Chão camada -3
            , Block(0, c.HEIGHT + block_size *3, block_size, f"{ground_path}/tile75.png")
            , Block(block_size, c.HEIGHT + block_size *3, block_size, f"{ground_path}/blank.png")
            , Block(block_size *2, c.HEIGHT + block_size *3, block_size, f"{ground_path}/blank.png") 
            , Block(block_size *3, c.HEIGHT + block_size *3, block_size, f"{ground_path}/blank.png")
            , Block(block_size *4, c.HEIGHT + block_size *3, block_size, f"{ground_path}/blank.png")
            , Block(block_size *5, c.HEIGHT + block_size *3, block_size, f"{ground_path}/blank.png")
            , Block(block_size *6, c.HEIGHT + block_size *3, block_size, f"{ground_path}/blank.png")
            , Block(block_size *7, c.HEIGHT + block_size *3, block_size, f"{ground_path}/blank.png")
            , Block(block_size *8, c.HEIGHT + block_size *3, block_size, f"{ground_path}/blank.png")
            , Block(block_size *9, c.HEIGHT + block_size *3, block_size, f"{ground_path}/blank.png")
            , Block(block_size *10, c.HEIGHT + block_size *3, block_size, f"{ground_path}/blank.png")
            , Block(block_size *11, c.HEIGHT + block_size *3, block_size, f"{ground_path}/blank.png")
            , Block(block_size *12, c.HEIGHT + block_size *3, block_size, f"{ground_path}/blank.png")
            , Block(block_size *13, c.HEIGHT + block_size *3, block_size, f"{ground_path}/blank.png")
            , Block(block_size *14, c.HEIGHT + block_size *3, block_size, f"{ground_path}/blank.png")
            , Block(block_size *15, c.HEIGHT + block_size *3, block_size, f"{ground_path}/blank.png")
            , Block(block_size *16, c.HEIGHT + block_size *3, block_size, f"{ground_path}/blank.png")
            , Block(block_size *17, c.HEIGHT + block_size *3, block_size, f"{ground_path}/blank.png")
            , Block(block_size *18, c.HEIGHT + block_size *3, block_size, f"{ground_path}/tile53.png")
            , Block(block_size *20, c.HEIGHT + block_size *3, block_size, f"{ground_path}/tile55.png")
            , Block(block_size *21, c.HEIGHT + block_size *3, block_size, f"{ground_path}/blank.png")
            , Block(block_size *22, c.HEIGHT + block_size *3, block_size, f"{ground_path}/blank.png")
            , Block(block_size *23, c.HEIGHT + block_size *3, block_size, f"{ground_path}/blank.png")
            , Block(block_size *24, c.HEIGHT + block_size *3, block_size, f"{ground_path}/blank.png")
            , Block(block_size *25, c.HEIGHT + block_size *3, block_size, f"{ground_path}/blank.png")
            , Block(block_size *26, c.HEIGHT + block_size *3, block_size, f"{ground_path}/blank.png")
            , Block(block_size *27, c.HEIGHT + block_size *3, block_size, f"{ground_path}/blank.png")
            , Block(block_size *28, c.HEIGHT + block_size *3, block_size, f"{ground_path}/blank.png")
            , Block(block_size *29, c.HEIGHT + block_size *3, block_size, f"{ground_path}/blank.png")
            , Block(block_size *30, c.HEIGHT + block_size *3, block_size, f"{ground_path}/blank.png")
            , Block(block_size *31, c.HEIGHT + block_size *3, block_size, f"{ground_path}/blank.png")
            , Block(block_size *32, c.HEIGHT + block_size *3, block_size, f"{ground_path}/blank.png")

        # Chão camada -2
            , Block(0, c.HEIGHT + block_size *2, block_size, f"{ground_path}/tile75.png")
            , Block(block_size, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *2, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png") 
            , Block(block_size *3, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *4, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *5, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *6, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *7, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *8, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *9, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *10, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *11, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *12, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *13, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *14, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *15, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *16, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *17, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *18, c.HEIGHT + block_size *2, block_size, f"{ground_path}/tile53.png")
            , Block(block_size *20, c.HEIGHT + block_size *2, block_size, f"{ground_path}/tile55.png")
            , Block(block_size *21, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *22, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *23, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *24, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *25, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *26, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *27, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *28, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *29, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *30, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *31, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png")
            , Block(block_size *32, c.HEIGHT + block_size *2, block_size, f"{ground_path}/blank.png")

        # Chão camada -1
            , Block(0, c.HEIGHT + block_size, block_size, f"{ground_path}/tile75.png")
            , Block(block_size, c.HEIGHT + block_size, block_size, f"{ground_path}/blank.png")
            , Block(block_size *2, c.HEIGHT + block_size, block_size, f"{ground_path}/blank.png") 
            , Block(block_size *3, c.HEIGHT + block_size, block_size, f"{ground_path}/blank.png")
            , Block(block_size *4, c.HEIGHT + block_size, block_size, f"{ground_path}/blank.png")
            , Block(block_size *5, c.HEIGHT + block_size, block_size, f"{ground_path}/blank.png")
            , Block(block_size *6, c.HEIGHT + block_size, block_size, f"{ground_path}/blank.png")
            , Block(block_size *7, c.HEIGHT + block_size, block_size, f"{ground_path}/blank.png")
            , Block(block_size *8, c.HEIGHT + block_size, block_size, f"{ground_path}/blank.png")
            , Block(block_size *9, c.HEIGHT + block_size, block_size, f"{ground_path}/blank.png")
            , Block(block_size *10, c.HEIGHT + block_size, block_size, f"{ground_path}/blank.png")
            , Block(block_size *11, c.HEIGHT + block_size, block_size, f"{ground_path}/blank.png")
            , Block(block_size *12, c.HEIGHT + block_size, block_size, f"{ground_path}/blank.png")
            , Block(block_size *13, c.HEIGHT + block_size, block_size, f"{ground_path}/blank.png")
            , Block(block_size *14, c.HEIGHT + block_size, block_size, f"{ground_path}/blank.png")
            , Block(block_size *15, c.HEIGHT + block_size, block_size, f"{ground_path}/blank.png")
            , Block(block_size *16, c.HEIGHT + block_size, block_size, f"{ground_path}/blank.png")
            , Block(block_size *17, c.HEIGHT + block_size, block_size, f"{ground_path}/blank.png")
            , Block(block_size *18, c.HEIGHT + block_size, block_size, f"{ground_path}/tile53.png")
            , Block(block_size *20, c.HEIGHT + block_size, block_size, f"{ground_path}/tile55.png")
            , Block(block_size *21, c.HEIGHT + block_size, block_size, f"{ground_path}/blank.png")
            , Block(block_size *22, c.HEIGHT + block_size, block_size, f"{ground_path}/blank.png")
            , Block(block_size *23, c.HEIGHT + block_size, block_size, f"{ground_path}/blank.png")
            , Block(block_size *24, c.HEIGHT + block_size, block_size, f"{ground_path}/blank.png")
            , Block(block_size *25, c.HEIGHT + block_size, block_size, f"{ground_path}/blank.png")
            , Block(block_size *26, c.HEIGHT + block_size, block_size, f"{ground_path}/blank.png")
            , Block(block_size *27, c.HEIGHT + block_size, block_size, f"{ground_path}/blank.png")
            , Block(block_size *28, c.HEIGHT + block_size, block_size, f"{ground_path}/blank.png")
            , Block(block_size *29, c.HEIGHT + block_size, block_size, f"{ground_path}/blank.png")
            , Block(block_size *30, c.HEIGHT + block_size, block_size, f"{ground_path}/blank.png")
            , Block(block_size *31, c.HEIGHT + block_size, block_size, f"{ground_path}/blank.png")
            , Block(block_size *32, c.HEIGHT + block_size, block_size, f"{ground_path}/blank.png")

        # Chão camada 0
            , Block(0, c.HEIGHT , block_size, f"{ground_path}/tile75.png")
            , Block(block_size, c.HEIGHT , block_size, f"{ground_path}/blank.png")
            , Block(block_size *2, c.HEIGHT , block_size, f"{ground_path}/blank.png") 
            , Block(block_size *3, c.HEIGHT , block_size, f"{ground_path}/blank.png")
            , Block(block_size *4, c.HEIGHT , block_size, f"{ground_path}/blank.png")
            , Block(block_size *5, c.HEIGHT , block_size, f"{ground_path}/blank.png")
            , Block(block_size *6, c.HEIGHT , block_size, f"{ground_path}/blank.png")
            , Block(block_size *7, c.HEIGHT , block_size, f"{ground_path}/blank.png")
            , Block(block_size *8, c.HEIGHT , block_size, f"{ground_path}/blank.png")
            , Block(block_size *9, c.HEIGHT , block_size, f"{ground_path}/blank.png")
            , Block(block_size *10, c.HEIGHT , block_size, f"{ground_path}/blank.png")
            , Block(block_size *11, c.HEIGHT , block_size, f"{ground_path}/blank.png")
            , Block(block_size *12, c.HEIGHT , block_size, f"{ground_path}/blank.png")
            , Block(block_size *13, c.HEIGHT , block_size, f"{ground_path}/blank.png")
            , Block(block_size *14, c.HEIGHT , block_size, f"{ground_path}/blank.png")
            , Block(block_size *15, c.HEIGHT , block_size, f"{ground_path}/blank.png")
            , Block(block_size *16, c.HEIGHT , block_size, f"{ground_path}/blank.png")
            , Block(block_size *17, c.HEIGHT , block_size, f"{ground_path}/blank.png")
            , Block(block_size *18, c.HEIGHT , block_size, f"{ground_path}/tile53.png")
            , Block(block_size *20, c.HEIGHT , block_size, f"{ground_path}/tile55.png")
            , Block(block_size *21, c.HEIGHT , block_size, f"{ground_path}/blank.png")
            , Block(block_size *22, c.HEIGHT , block_size, f"{ground_path}/blank.png")
            , Block(block_size *23, c.HEIGHT , block_size, f"{ground_path}/blank.png")
            , Block(block_size *24, c.HEIGHT , block_size, f"{ground_path}/blank.png")
            , Block(block_size *25, c.HEIGHT , block_size, f"{ground_path}/blank.png")
            , Block(block_size *26, c.HEIGHT , block_size, f"{ground_path}/blank.png")
            , Block(block_size *27, c.HEIGHT , block_size, f"{ground_path}/blank.png")
            , Block(block_size *28, c.HEIGHT , block_size, f"{ground_path}/blank.png")
            , Block(block_size *29, c.HEIGHT , block_size, f"{ground_path}/blank.png")
            , Block(block_size *30, c.HEIGHT , block_size, f"{ground_path}/blank.png")
            , Block(block_size *31, c.HEIGHT , block_size, f"{ground_path}/blank.png")
            , Block(block_size *32, c.HEIGHT , block_size, f"{ground_path}/blank.png")

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


    # Colocando os gatos de volta nas suas posições iniciais
    cats = [
        Cat(600, 520),
        Cat(450, 50),
        Cat(2100, 520),
        Cat(1700, 520),
        Cat(800, -50)
    ]

    # Resetando o deslocamento da tela
    offset_x = 0
    offset_y = 0

    return game, player, cats, objects, background, offset_x, offset_y

def main(window):
    clock = pygame.time.Clock()

    game, player, cats, objects, background, offset_x, offset_y = initial_state()

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

        
        if player.is_dead:
            game.show_end_screen(window, True)  
                    
        player.loop(c.FPS)
        handle_move(player, objects)
        game.handle_cat_collision(player, cats)

        for cat in cats:
            cat.update() 

        draw(window, cats, background, player, objects, game, offset_x, offset_y)

        if game.check_end_game(window):  # Se o jogo acabou, exibe a tela de fim de jogo
            break

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