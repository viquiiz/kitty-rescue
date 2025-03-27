import os
import math
import random
import pygame

from os import listdir
from os.path import isfile, join

import constants as c

pygame.init()

pygame.display.set_caption("Kitty Rescue")

window = pygame.display.set_mode((c.WIDTH, c.HEIGHT))

def get_background(tiles_folder):
    tile_files = [f for f in os.listdir(tiles_folder) if f.endswith('.png')]

    sky_tiles_1 = []
    sky_tiles_2 = []
    sky_tiles_3 = []
    sky_tiles_4 = []

    ground_tiles = []

    for tile_file in tile_files:
        image = pygame.image.load(os.path.join(tiles_folder, tile_file))
        _, _, width, height = image.get_rect()

        if "ceu1" in tile_file:
            sky_tiles_1.append((image, width, height, tile_file))
        elif "ceu2" in tile_file:
            if tile_file == "ceu2.png":
                sky_tiles_2.extend([(image, width, height, tile_file)] * 20)  
            else:
                sky_tiles_2.append((image, width, height, tile_file))  
        elif "ceu3" in tile_file:
            sky_tiles_3.append((image, width, height, tile_file))
        elif "ceu4" in tile_file:
            sky_tiles_4.append((image, width, height, tile_file))
        elif "chao" in tile_file:
            ground_tiles.append((image, width, height, tile_file))

    ground_tiles.sort(key=lambda x: x[3])

    return sky_tiles_1, sky_tiles_2, sky_tiles_3, sky_tiles_4, ground_tiles

def generate_bg(sky_tiles_1, sky_tiles_2, sky_tiles_3, sky_tiles_4, ground_tiles):
    background = {
        "sky1": [],
        "sky2": [],
        "sky3": [],
        "sky4": [],
        "ground": []
    }
    
    # Adicionar tiles de céu
    for i in range(c.WIDTH // sky_tiles_4[0][1] + 1):
        for j in range(c.HEIGHT // sky_tiles_4[0][2] + 1):
            tile = random.choice(sky_tiles_4)  # Escolher um tile aleatório para o céu
            background["sky4"].append((tile[0], i * tile[1], j * tile[2]))

    for i in range(c.WIDTH // sky_tiles_3[0][1] + 1):
        for j in range(c.HEIGHT // sky_tiles_3[0][2] + 1):
            tile = random.choice(sky_tiles_3) 
            background["sky3"].append((tile[0], i * tile[1], (c.HEIGHT // 4) + j * tile[2]))  # Deslocar no eixo Y para baixo

    for i in range(c.WIDTH // sky_tiles_2[0][1] + 1):
        for j in range(c.HEIGHT // sky_tiles_2[0][2] + 1):
            tile = random.choice(sky_tiles_2)  
            background["sky2"].append((tile[0], i * tile[1], (c.HEIGHT // 4) * 2 + j * tile[2]))  

    for i in range(c.WIDTH // sky_tiles_1[0][1] + 1):
        for j in range(c.HEIGHT // sky_tiles_1[0][2] + 1):
            tile = random.choice(sky_tiles_1)  
            background["sky1"].append((tile[0], i * tile[1], (c.HEIGHT // 4) * 3 + j * tile[2])) 

    x = 0
    for i in range(c.WIDTH // ground_tiles[0][1] + 1):
        tile = ground_tiles[x]
        print(tile[3])
        x = (x + 1) if x < (len(ground_tiles) -1) else 0
        background["ground"].append((tile[0], i * tile[1], (c.HEIGHT // 4) * 2 + 7 * tile[2]))  # Adicionando no fundo

    print(background['ground'])

    return background

def draw(window, background):
    for tile_image, x, y in background["sky4"]:
        window.blit(tile_image, (x, y))

    for tile_image, x, y in background["sky3"]:
        window.blit(tile_image, (x, y))

    for tile_image, x, y in background["sky2"]:
        window.blit(tile_image, (x, y))

    for tile_image, x, y in background["sky1"]:
        window.blit(tile_image, (x, y))
    
    for tile_image, x, y in background["ground"]:
        window.blit(tile_image, (x, y))

    pygame.display.update()

def main(window):
    clock = pygame.time.Clock()

    # Carregar todos os tiles e escolher as imagens
    tiles_folder = os.path.join("assets", "img", "craftpix-net-156752-nature-pixel-art-environment", "PNG", "Tiles")
    sky_tiles_1, sky_tiles_2, sky_tiles_3, sky_tiles_4, ground_tiles = get_background(tiles_folder)

    background = generate_bg(sky_tiles_1, sky_tiles_2, sky_tiles_3, sky_tiles_4, ground_tiles)

    run = True
    while run:
        clock.tick(c.FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        draw(window, background)
    
    pygame.quit()
    quit()


if __name__ == "__main__":
    main(window)