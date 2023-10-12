from pathlib import Path
import os
import secrets


# генератов случайного названия файла и замена оригинального
def random_name(file) -> str:
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(file.filename)
    return (random_hex + f_ext)


# функция сохранения обложки
def save_image(image) -> str:
    picture_name = random_name(image)
    picture_path = Path("../BotStorage", picture_name)
    with open(picture_path, 'wb') as f:
        f.write(image.file.read())
    return str(picture_path)
