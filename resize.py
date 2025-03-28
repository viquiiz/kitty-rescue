from PIL import Image
import os

for x in os.listdir('assets\img\main_char'):
    image = Image.open(f'assets\img\main_char\{x}')
    print(f"Original size : {image.size}") # 5464x3640

    sunset_resized = image.resize((128, 128))
    sunset_resized.save(f'assets\img\main_char\{x}')