import random
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from django.core.files.base import ContentFile


def generate_avatar_placeholder(user):
    size = (400, 400)
    colors = ['#f44336', '#e91e63', '#9c27b0', '#3f51b5', '#00abc9', '#4caf50', '#ff9800']
    bg_color = random.choice(colors)
    
    image = Image.new('RGBA', size, color=bg_color)
    draw = ImageDraw.Draw(image)
    
    if user and getattr(user, 'first_name', None):
        letter = user.first_name[0].upper()
    elif user and getattr(user, 'username', None):
        letter = user.username[0].upper()
    else:
        letter = "U"

    try:
        font = ImageFont.truetype("arial.ttf", 200)
    except IOError:
        font = ImageFont.load_default()

    left, top, right, bottom = draw.textbbox((0, 0), letter, font=font)
    text_width = right - left
    text_height = bottom - top
    position = ((size[0] - text_width) / 2, (size[1] - text_height) / 2 - top)
    
    draw.text(position, letter, fill="white", font=font)

    mask = Image.new('L', size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0, size[0], size[1]), fill=255)
    
    round_image = Image.new('RGBA', size, (0, 0, 0, 0))
    round_image.paste(image, (0, 0), mask=mask)

    buffer = BytesIO()
    round_image.save(buffer, format='PNG')
    
    username_str = getattr(user, 'username', 'default')
    filename = f"{username_str}_default.png"
    return filename, ContentFile(buffer.getvalue())


def process_uploaded_avatar(image_field_file):
    img = Image.open(image_field_file)
    
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
        
    width, height = img.size
    min_edge = min(width, height)
    
    left = (width - min_edge) / 2
    top = (height - min_edge) / 2
    right = (width + min_edge) / 2
    bottom = (height + min_edge) / 2
    
    img = img.crop((left, top, right, bottom))
    
    target_size = (400, 400)
    img = img.resize(target_size, Image.Resampling.LANCZOS)
    
    mask = Image.new('L', target_size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0, target_size, target_size), fill=255)
    
    round_image = Image.new('RGBA', target_size, (0, 0, 0, 0))
    round_image.paste(img, (0, 0), mask=mask)
    
    buffer = BytesIO()
    round_image.save(buffer, format='PNG', optimize=True)
    
    return ContentFile(buffer.getvalue())
