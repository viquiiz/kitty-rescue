import os
import random
import pygame

import constants as c

class Background:
    def get_background(tiles_folder):
        tile_files = [f for f in os.listdir(tiles_folder) if f.endswith('.png')]

        sky_tiles_1 = []
        sky_tiles_2 = []
        sky_tiles_3 = []
        sky_tiles_4 = []


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
                if tile_file == "ceu3.png":
                    sky_tiles_3.extend([(image, width, height, tile_file)] * 15)  
                else:
                    sky_tiles_3.append((image, width, height, tile_file))
            elif "ceu4" in tile_file:
                if tile_file == "ceu4.png":
                    sky_tiles_4.extend([(image, width, height, tile_file)] * 10)  
                else:
                    sky_tiles_4.append((image, width, height, tile_file))

        return sky_tiles_1, sky_tiles_2, sky_tiles_3, sky_tiles_4

    def generate_bg(sky_tiles_1, sky_tiles_2, sky_tiles_3, sky_tiles_4):
        background = {
            "sky1": [],
            "sky2": [],
            "sky3": [],
            "sky4": [],
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

        return background