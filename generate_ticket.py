import random
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
import os

TEMPLATE_PATH = os.path.normpath('files/ticket_template.jpg')
FONT_PATH = os.path.normpath('files/Roboto-Regular.ttf')
FONT_SIZE = 30
FONT_SIZE_2 = 50

BLACK = (0, 0, 0, 255)
NAME_OFFSET = (90, 195)
EMAIL_OFFSET = (90, 278)
DEPARTURE_CITY_OFFSET = (110, 420)
ARRIVE_CITY_OFFSET = (465, 420)
DATE_OFFSET = (210, 580)

AVATAR_SIZE = 100
AVATAR_OFFSET = (515, 130)


def generate_ticket(name, email, departure, arrive, date, random_avatars=True):
    base = Image.open(TEMPLATE_PATH).convert('RGBA')
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    font_bigger = ImageFont.truetype(FONT_PATH, FONT_SIZE_2)

    draw = ImageDraw.Draw(base)
    draw.text(NAME_OFFSET, name, font=font, fill=BLACK)
    draw.text(EMAIL_OFFSET, email, font=font, fill=BLACK)
    draw.text(DEPARTURE_CITY_OFFSET, departure, font=font_bigger, fill=BLACK)
    draw.text(ARRIVE_CITY_OFFSET, arrive, font=font_bigger, fill=BLACK)
    draw.text(DATE_OFFSET, date, font=font_bigger, fill=BLACK)

    random_choice = random.randint(1, 7) if random_avatars is True else 7
    avatar_file = os.path.normpath(f'files/avatars/{random_choice}.png')
    avatar = Image.open(avatar_file)
    avatar = avatar.resize((200, 200))

    base.paste(avatar, AVATAR_OFFSET)

    temp_file = BytesIO()
    base.save(temp_file, 'png')
    temp_file.seek(0)

    return temp_file
