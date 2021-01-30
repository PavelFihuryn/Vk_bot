from io import BytesIO

import requests
from PIL import Image, ImageDraw, ImageFont

TEMPLATE_PATH = "files/ticket_base.jpg"
FONT_PATH = "files/MandysSketchExtended-3zRo8.ttf"
FONT_SIZE = 25

BLACK = (0, 0, 0, 255)
NAME_OFFSET = (260, 180)
EMAIL_OFFSET = (260, 230)

AVATAR_OFFSET = (100, 190)


def create_avatar(email):
    # import code for encoding urls and generating md5 hashes
    import hashlib
    size = 40
    # construct the url
    gravatar_url = "https://www.gravatar.com/avatar/" + hashlib.md5(email.lower().encode('utf-8')).hexdigest() + f"?s{size}"
    gravatar_url += "s=100&d=robohash&r=x"
    return gravatar_url


def draw_ticket(name, email):
    base = Image.open(TEMPLATE_PATH).convert("RGBA")
    fnt = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    d = ImageDraw.Draw(base)
    d.text(NAME_OFFSET, name, font=fnt, fill=BLACK)
    d.text(EMAIL_OFFSET, email, font=fnt, fill=BLACK)

    response = requests.get(url=create_avatar(email=email))
    avatar_like_file = BytesIO(response.content)
    avatar = Image.open(avatar_like_file)
    base.paste(avatar, AVATAR_OFFSET)
    temp_file = BytesIO()
    base.save(temp_file, 'png')
    temp_file.seek(0)

    return temp_file
