import os
import sys
import math
import wave
import struct
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import imageio_ffmpeg

W, H = 720, 1280
FPS = 30
DURATION = 20.0
TOTAL_FRAMES = int(DURATION * FPS) # 600 frames

# Font setup
font_bold_path = r'C:\Windows\Fonts\bahnschrift.ttf'
font_segoe_path = r'C:\Windows\Fonts\segoeuib.ttf'

def get_font(size, bold=True):
    path = font_bold_path if bold else font_segoe_path
    try:
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()

# Asset directories
base_dir = os.getcwd()
img_dir = os.path.join(base_dir, 'assets', 'images')
apparel_dir = os.path.join(img_dir, 'apparel')
video_dir = os.path.join(base_dir, 'assets', 'videos')
os.makedirs(video_dir, exist_ok=True)

# Load media assets
logo_img = Image.open(os.path.join(img_dir, 'logo.png')).convert("RGBA")
tshirt_oversized = Image.open(os.path.join(apparel_dir, 'tshirt_oversized_preto.jpg')).convert("RGB")
tshirt_lentos_back = Image.open(os.path.join(apparel_dir, 'tshirt_lentos_preto_back.jpg')).convert("RGB")
tshirt_lentos_front = Image.open(os.path.join(apparel_dir, 'tshirt_lentos_preto_front.jpg')).convert("RGB")
hoodie_oficial_back = Image.open(os.path.join(apparel_dir, 'hoodie_oficial_preto_back.jpg')).convert("RGB")
hoodie_oficial_front = Image.open(os.path.join(apparel_dir, 'hoodie_oficial_preto_front.jpg')).convert("RGB")
hoodie_lentos_back = Image.open(os.path.join(apparel_dir, 'hoodie_lentos_preto_back.jpg')).convert("RGB")
hoodie_lentos_front = Image.open(os.path.join(apparel_dir, 'hoodie_lentos_preto_front.jpg')).convert("RGB")

def draw_gradient_bg(im, color_top=(14, 16, 24), color_bot=(4, 4, 6)):
    draw = ImageDraw.Draw(im)
    for y in range(H):
        t = y / float(H)
        r = int(color_top[0] * (1 - t) + color_bot[0] * t)
        g = int(color_top[1] * (1 - t) + color_bot[1] * t)
        b = int(color_top[2] * (1 - t) + color_bot[2] * t)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

def draw_header_pill(draw, text, y=42, color=(255, 230, 0)):
    font = get_font(19, bold=True)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    px, py = 18, 9
    rx = (W - tw - px * 2) // 2
    ry = y
    draw.rounded_rectangle([rx, ry, rx + tw + px * 2, ry + th + py * 2], radius=16, fill=(18, 20, 30), outline=color, width=2)
    draw.text((rx + px, ry + py - 2), text, font=font, fill=color)

def draw_progress_bar(draw, frame_idx):
    progress = frame_idx / float(TOTAL_FRAMES)
    bar_w = int(W * progress)
    # Background subtle track
    draw.rectangle([0, 0, W, 4], fill=(30, 32, 45))
    # Active track with gold glow
    draw.rectangle([0, 0, bar_w, 4], fill=(255, 230, 0))

# 1. SCENE 1: Brand Hook & Drop Intro (0.0s - 3.0s, frames 0-89)
def render_frame_scene_1(frame_idx, rel_t):
    im = Image.new("RGB", (W, H))
    draw_gradient_bg(im, (16, 18, 28), (5, 5, 8))
    draw = ImageDraw.Draw(im)
    draw_progress_bar(draw, frame_idx)
    
    draw_header_pill(draw, "DROP 01 STREETWEAR • EDIÇÃO LIMITADA", y=48)
    
    # Pulsing scale on logo
    pulse = 1.0 + 0.03 * math.sin(rel_t * math.pi * 3.0)
    lw = int(270 * pulse)
    lh = int(logo_img.height * (lw / logo_img.width))
    logo_res = logo_img.resize((lw, lh), Image.Resampling.LANCZOS)
    im.paste(logo_res, ((W - lw) // 2, 210 - (lh - int(logo_img.height * 270 / logo_img.width)) // 2), logo_res)
    
    draw.text((W // 2, 530), "DARK GHOSTRIDER", font=get_font(44, True), fill=(255, 255, 255), anchor="mm")
    draw.text((W // 2, 585), "STREETWEAR & RIDER APPAREL", font=get_font(23, True), fill=(255, 230, 0), anchor="mm")
    
    # Feature box
    card_box = [55, 660, W - 55, 940]
    draw.rounded_rectangle(card_box, radius=24, fill=(17, 19, 29), outline=(255, 230, 0), width=2)
    
    draw.text((W // 2, 710), "COLEÇÃO 100% PRETO STEALTH", font=get_font(25, True), fill=(255, 255, 255), anchor="mm")
    
    f_body = get_font(20, False)
    draw.text((W // 2, 765), "• T-Shirts Pesadas 220g (Corte Boxy)", font=f_body, fill=(205, 210, 225), anchor="mm")
    draw.text((W // 2, 810), "• Sweatshirts com Capuz Heavyweight 280g", font=f_body, fill=(205, 210, 225), anchor="mm")
    draw.text((W // 2, 855), "• Produção Oficial Lisboa / Margem Sul", font=f_body, fill=(205, 210, 225), anchor="mm")
    draw.text((W // 2, 900), "• Estampa DTF Ultra HD Peito & Costas", font=f_body, fill=(255, 230, 0), anchor="mm")
    
    # Red Instagram promo banner
    banner_y = 995
    draw.rounded_rectangle([80, banner_y, W - 80, banner_y + 80], radius=18, fill=(230, 20, 38))
    draw.text((W // 2, banner_y + 40), "PROMOÇÃO EXCLUSIVA INSTAGRAM", font=get_font(22, True), fill=(255, 255, 255), anchor="mm")
    
    draw.text((W // 2, 1130), "Ativa o cupão no carrinho:", font=get_font(18, False), fill=(180, 185, 200), anchor="mm")
    draw.text((W // 2, 1170), "DARKINSTA  (-25% OFF)", font=get_font(28, True), fill=(255, 230, 0), anchor="mm")
    
    return im

# 2. SCENE 2A: T-Shirt Oversized Heavyweight (3.0s - 5.8s, frames 90-174)
def render_frame_scene_2a(frame_idx, rel_t):
    im = Image.new("RGB", (W, H))
    draw_gradient_bg(im, (14, 15, 22), (4, 4, 6))
    draw = ImageDraw.Draw(im)
    draw_progress_bar(draw, frame_idx)
    
    draw_header_pill(draw, "[ 1 ] COLEÇÃO T-SHIRTS • ALGODÃO PESADO", y=48, color=(255, 230, 0))
    
    # Photo display with subtle zoom
    photo_box = [55, 125, W - 55, 735]
    pw = photo_box[2] - photo_box[0]
    ph = photo_box[3] - photo_box[1]
    
    zoom = 1.0 + 0.04 * rel_t
    zw, zh = int(pw * zoom), int(pw * zoom)
    t_crop = tshirt_oversized.resize((zw, zh), Image.Resampling.LANCZOS)
    # Center crop
    cx = (zw - pw) // 2
    cy = (zh - ph) // 2
    t_crop = t_crop.crop((cx, cy, cx + pw, cy + ph))
    im.paste(t_crop, (photo_box[0], photo_box[1]))
    
    # Border
    draw.rounded_rectangle([photo_box[0]-3, photo_box[1]-3, photo_box[2]+3, photo_box[3]+3], radius=22, outline=(50, 52, 70), width=2)
    
    # Badge
    draw.rounded_rectangle([photo_box[0]+15, photo_box[1]+15, photo_box[0]+250, photo_box[1]+55], radius=10, fill=(230, 20, 38))
    draw.text((photo_box[0]+132, photo_box[1]+35), "OVERSIZED HEAVYWEIGHT", font=get_font(14, True), fill=(255, 255, 255), anchor="mm")
    
    # Bottom Card
    card_y = 765
    draw.rounded_rectangle([45, card_y, W - 45, 1220], radius=24, fill=(16, 18, 28), outline=(45, 48, 66), width=2)
    
    draw.text((W // 2, card_y + 38), "T-SHIRT OVERSIZED HEAVYWEIGHT 220G", font=get_font(24, True), fill=(255, 255, 255), anchor="mm")
    
    f_sub = get_font(18, False)
    draw.text((W // 2, card_y + 78), "100% Algodão Ring Spun 220g/m² • Corte Boxy Drop", font=f_sub, fill=(185, 190, 205), anchor="mm")
    draw.text((W // 2, card_y + 112), "Edição Oficial Preto Stealth All Black (XS ao 4XL)", font=f_sub, fill=(185, 190, 205), anchor="mm")
    
    # Pricing Box
    price_box_y = card_y + 150
    draw.rounded_rectangle([75, price_box_y, W - 75, price_box_y + 110], radius=16, fill=(10, 11, 16), outline=(255, 230, 0), width=2)
    
    draw.text((W // 2, price_box_y + 30), "PREÇO NORMAL: 39,90 €", font=get_font(17, True), fill=(140, 145, 160), anchor="mm")
    
    f_promo_price = get_font(30, True)
    draw.text((W // 2, price_box_y + 75), "COM CUPÃO DARKINSTA: 29,90 €", font=f_promo_price, fill=(255, 230, 0), anchor="mm")
    
    # Green discount banner
    draw.rounded_rectangle([90, card_y + 285, W - 90, card_y + 340], radius=14, fill=(25, 135, 84))
    draw.text((W // 2, card_y + 312), "POUPAS 10,00 € (-25% DE DESCONTO)", font=get_font(18, True), fill=(255, 255, 255), anchor="mm")
    
    draw.text((W // 2, card_y + 380), "+ Oferta de Pack de Autocolantes Oficiais", font=get_font(16, True), fill=(255, 230, 0), anchor="mm")
    draw.text((W // 2, card_y + 412), "Entrega em mão Lisboa / Margem Sul disponível", font=get_font(14, False), fill=(160, 165, 180), anchor="mm")
    
    return im

# 3. SCENE 2B: T-Shirt Veículos Lentos (5.8s - 8.6s, frames 175-259)
def render_frame_scene_2b(frame_idx, rel_t):
    im = Image.new("RGB", (W, H))
    draw_gradient_bg(im, (14, 15, 22), (4, 4, 6))
    draw = ImageDraw.Draw(im)
    draw_progress_bar(draw, frame_idx)
    
    draw_header_pill(draw, "[ 1 ] COLEÇÃO T-SHIRTS • BIKER HUMOR", y=48, color=(255, 230, 0))
    
    photo_box = [55, 125, W - 55, 735]
    pw = photo_box[2] - photo_box[0]
    ph = photo_box[3] - photo_box[1]
    
    zoom = 1.0 + 0.04 * rel_t
    zw, zh = int(pw * zoom), int(pw * zoom)
    t_crop = tshirt_lentos_back.resize((zw, zh), Image.Resampling.LANCZOS)
    cx = (zw - pw) // 2
    cy = (zh - ph) // 2
    t_crop = t_crop.crop((cx, cy, cx + pw, cy + ph))
    im.paste(t_crop, (photo_box[0], photo_box[1]))
    
    # Inset photo of front
    inset_w, inset_h = 160, 160
    t_front_inset = tshirt_lentos_front.resize((inset_w, inset_h), Image.Resampling.LANCZOS)
    ix, iy = photo_box[2] - inset_w - 15, photo_box[3] - inset_h - 15
    draw.rectangle([ix-2, iy-2, ix+inset_w+2, iy+inset_h+2], fill=(255, 230, 0))
    im.paste(t_front_inset, (ix, iy))
    draw.rectangle([ix, iy+inset_h-22, ix+inset_w, iy+inset_h], fill=(0, 0, 0))
    draw.text((ix + inset_w // 2, iy + inset_h - 11), "FRENTE", font=get_font(12, True), fill=(255, 255, 255), anchor="mm")
    
    draw.rounded_rectangle([photo_box[0]-3, photo_box[1]-3, photo_box[2]+3, photo_box[3]+3], radius=22, outline=(50, 52, 70), width=2)
    
    draw.rounded_rectangle([photo_box[0]+15, photo_box[1]+15, photo_box[0]+240, photo_box[1]+55], radius=10, fill=(230, 20, 38))
    draw.text((photo_box[0]+127, photo_box[1]+35), "BIKER HUMOR BESTSELLER", font=get_font(13, True), fill=(255, 255, 255), anchor="mm")
    
    # Bottom Card
    card_y = 765
    draw.rounded_rectangle([45, card_y, W - 45, 1220], radius=24, fill=(16, 18, 28), outline=(45, 48, 66), width=2)
    
    draw.text((W // 2, card_y + 38), 'T-SHIRT "VEÍCULOS LENTOS À DIREITA"', font=get_font(24, True), fill=(255, 255, 255), anchor="mm")
    
    f_sub = get_font(18, False)
    draw.text((W // 2, card_y + 78), "Frente Peito Minimalista + Costas A3 de Alto Contraste", font=f_sub, fill=(185, 190, 205), anchor="mm")
    draw.text((W // 2, card_y + 112), "Edição Preto Stealth All Black • Malha Premium DTF HD", font=f_sub, fill=(185, 190, 205), anchor="mm")
    
    # Pricing Box
    price_box_y = card_y + 150
    draw.rounded_rectangle([75, price_box_y, W - 75, price_box_y + 110], radius=16, fill=(10, 11, 16), outline=(255, 230, 0), width=2)
    
    draw.text((W // 2, price_box_y + 30), "T-SHIRT CLASSIC BIO190: 29,90 €", font=get_font(16, True), fill=(140, 145, 160), anchor="mm")
    
    f_promo_price = get_font(30, True)
    draw.text((W // 2, price_box_y + 75), "COM DARKINSTA: 22,40 €", font=f_promo_price, fill=(255, 230, 0), anchor="mm")
    
    draw.rounded_rectangle([90, card_y + 285, W - 90, card_y + 340], radius=14, fill=(25, 135, 84))
    draw.text((W // 2, card_y + 312), "-25% EM TODOS OS MODELOS", font=get_font(18, True), fill=(255, 255, 255), anchor="mm")
    
    draw.text((W // 2, card_y + 380), "Versão Oversized Heavyweight por 29,90 €", font=get_font(16, True), fill=(255, 230, 0), anchor="mm")
    draw.text((W // 2, card_y + 412), "Produzido em Lisboa / Margem Sul", font=get_font(14, False), fill=(160, 165, 180), anchor="mm")
    
    return im

# 4. SCENE 3A: Sweatshirt com Capuz Oficial (8.6s - 11.4s, frames 260-344)
def render_frame_scene_3a(frame_idx, rel_t):
    im = Image.new("RGB", (W, H))
    draw_gradient_bg(im, (14, 15, 22), (4, 4, 6))
    draw = ImageDraw.Draw(im)
    draw_progress_bar(draw, frame_idx)
    
    draw_header_pill(draw, "[ 2 ] SWEATSHIRTS COM CAPUZ • HEAVYWEIGHT", y=48, color=(255, 230, 0))
    
    photo_box = [55, 125, W - 55, 735]
    pw = photo_box[2] - photo_box[0]
    ph = photo_box[3] - photo_box[1]
    
    zoom = 1.0 + 0.04 * rel_t
    zw, zh = int(pw * zoom), int(pw * zoom)
    h_crop = hoodie_oficial_back.resize((zw, zh), Image.Resampling.LANCZOS)
    cx = (zw - pw) // 2
    cy = (zh - ph) // 2
    h_crop = h_crop.crop((cx, cy, cx + pw, cy + ph))
    im.paste(h_crop, (photo_box[0], photo_box[1]))
    
    # Inset photo of front
    inset_w, inset_h = 160, 160
    h_front_inset = hoodie_oficial_front.resize((inset_w, inset_h), Image.Resampling.LANCZOS)
    ix, iy = photo_box[2] - inset_w - 15, photo_box[3] - inset_h - 15
    draw.rectangle([ix-2, iy-2, ix+inset_w+2, iy+inset_h+2], fill=(255, 230, 0))
    im.paste(h_front_inset, (ix, iy))
    draw.rectangle([ix, iy+inset_h-22, ix+inset_w, iy+inset_h], fill=(0, 0, 0))
    draw.text((ix + inset_w // 2, iy + inset_h - 11), "FRENTE", font=get_font(12, True), fill=(255, 255, 255), anchor="mm")
    
    draw.rounded_rectangle([photo_box[0]-3, photo_box[1]-3, photo_box[2]+3, photo_box[3]+3], radius=22, outline=(50, 52, 70), width=2)
    
    draw.rounded_rectangle([photo_box[0]+15, photo_box[1]+15, photo_box[0]+240, photo_box[1]+55], radius=10, fill=(230, 20, 38))
    draw.text((photo_box[0]+127, photo_box[1]+35), "SWEATSHIRT OFICIAL 280G", font=get_font(13, True), fill=(255, 255, 255), anchor="mm")
    
    # Bottom Card
    card_y = 765
    draw.rounded_rectangle([45, card_y, W - 45, 1220], radius=24, fill=(16, 18, 28), outline=(45, 48, 66), width=2)
    
    draw.text((W // 2, card_y + 38), "SWEATSHIRT COM CAPUZ OFICIAL", font=get_font(24, True), fill=(255, 255, 255), anchor="mm")
    
    f_sub = get_font(18, False)
    draw.text((W // 2, card_y + 78), "50/50 Ring Spun 280g/m² • Capuz Duplo Forrado & Bolso", font=f_sub, fill=(185, 190, 205), anchor="mm")
    draw.text((W // 2, card_y + 112), "Dupla Estampa DTF Ultra HD Peito + Costas 30x30", font=f_sub, fill=(185, 190, 205), anchor="mm")
    
    # Pricing Box
    price_box_y = card_y + 150
    draw.rounded_rectangle([75, price_box_y, W - 75, price_box_y + 110], radius=16, fill=(10, 11, 16), outline=(255, 230, 0), width=2)
    
    draw.text((W // 2, price_box_y + 30), "PREÇO NORMAL: 59,90 €", font=get_font(17, True), fill=(140, 145, 160), anchor="mm")
    
    f_promo_price = get_font(30, True)
    draw.text((W // 2, price_box_y + 75), "COM CUPÃO DARKINSTA: 44,90 €", font=f_promo_price, fill=(255, 230, 0), anchor="mm")
    
    draw.rounded_rectangle([90, card_y + 285, W - 90, card_y + 340], radius=14, fill=(25, 135, 84))
    draw.text((W // 2, card_y + 312), "POUPAS 15,00 € (-25% DE DESCONTO)", font=get_font(18, True), fill=(255, 255, 255), anchor="mm")
    
    draw.text((W // 2, card_y + 380), "+ Oferta de Pack de Autocolantes Oficiais", font=get_font(16, True), fill=(255, 230, 0), anchor="mm")
    draw.text((W // 2, card_y + 412), "Entrega em mão Lisboa / Margem Sul disponível", font=get_font(14, False), fill=(160, 165, 180), anchor="mm")
    
    return im

# 5. SCENE 3B: Sweatshirt Veículos Lentos (11.4s - 14.2s, frames 345-429)
def render_frame_scene_3b(frame_idx, rel_t):
    im = Image.new("RGB", (W, H))
    draw_gradient_bg(im, (14, 15, 22), (4, 4, 6))
    draw = ImageDraw.Draw(im)
    draw_progress_bar(draw, frame_idx)
    
    draw_header_pill(draw, "[ 2 ] SWEATSHIRTS COM CAPUZ • BIKER HUMOR", y=48, color=(255, 230, 0))
    
    photo_box = [55, 125, W - 55, 735]
    pw = photo_box[2] - photo_box[0]
    ph = photo_box[3] - photo_box[1]
    
    zoom = 1.0 + 0.04 * rel_t
    zw, zh = int(pw * zoom), int(pw * zoom)
    h_crop = hoodie_lentos_back.resize((zw, zh), Image.Resampling.LANCZOS)
    cx = (zw - pw) // 2
    cy = (zh - ph) // 2
    h_crop = h_crop.crop((cx, cy, cx + pw, cy + ph))
    im.paste(h_crop, (photo_box[0], photo_box[1]))
    
    # Inset photo of front
    inset_w, inset_h = 160, 160
    h_front_inset = hoodie_lentos_front.resize((inset_w, inset_h), Image.Resampling.LANCZOS)
    ix, iy = photo_box[2] - inset_w - 15, photo_box[3] - inset_h - 15
    draw.rectangle([ix-2, iy-2, ix+inset_w+2, iy+inset_h+2], fill=(255, 230, 0))
    im.paste(h_front_inset, (ix, iy))
    draw.rectangle([ix, iy+inset_h-22, ix+inset_w, iy+inset_h], fill=(0, 0, 0))
    draw.text((ix + inset_w // 2, iy + inset_h - 11), "FRENTE", font=get_font(12, True), fill=(255, 255, 255), anchor="mm")
    
    draw.rounded_rectangle([photo_box[0]-3, photo_box[1]-3, photo_box[2]+3, photo_box[3]+3], radius=22, outline=(50, 52, 70), width=2)
    
    draw.rounded_rectangle([photo_box[0]+15, photo_box[1]+15, photo_box[0]+240, photo_box[1]+55], radius=10, fill=(230, 20, 38))
    draw.text((photo_box[0]+127, photo_box[1]+35), "SWEAT BIKER HUMOR", font=get_font(13, True), fill=(255, 255, 255), anchor="mm")
    
    # Bottom Card
    card_y = 765
    draw.rounded_rectangle([45, card_y, W - 45, 1220], radius=24, fill=(16, 18, 28), outline=(45, 48, 66), width=2)
    
    draw.text((W // 2, card_y + 38), 'SWEAT "VEÍCULOS LENTOS À DIREITA"', font=get_font(24, True), fill=(255, 255, 255), anchor="mm")
    
    f_sub = get_font(18, False)
    draw.text((W // 2, card_y + 78), "Peito Minimalista + Mega Costas A3 em DTF de Alta Densidade", font=f_sub, fill=(185, 190, 205), anchor="mm")
    draw.text((W // 2, card_y + 112), "Edição Preto Stealth All Black • Malha Ring Spun 280g", font=f_sub, fill=(185, 190, 205), anchor="mm")
    
    # Pricing Box
    price_box_y = card_y + 150
    draw.rounded_rectangle([75, price_box_y, W - 75, price_box_y + 110], radius=16, fill=(10, 11, 16), outline=(255, 230, 0), width=2)
    
    draw.text((W // 2, price_box_y + 30), "PREÇO NORMAL: 59,90 €", font=get_font(17, True), fill=(140, 145, 160), anchor="mm")
    
    f_promo_price = get_font(30, True)
    draw.text((W // 2, price_box_y + 75), "COM CUPÃO DARKINSTA: 44,90 €", font=f_promo_price, fill=(255, 230, 0), anchor="mm")
    
    draw.rounded_rectangle([90, card_y + 285, W - 90, card_y + 340], radius=14, fill=(25, 135, 84))
    draw.text((W // 2, card_y + 312), "POUPAS 15,00 € (-25% DE DESCONTO)", font=get_font(18, True), fill=(255, 255, 255), anchor="mm")
    
    draw.text((W // 2, card_y + 380), "+ Oferta de Pack de Autocolantes Oficiais", font=get_font(16, True), fill=(255, 230, 0), anchor="mm")
    draw.text((W // 2, card_y + 412), "Produção Oficial Portuguesa (Margem Sul / Lisboa)", font=get_font(14, False), fill=(160, 165, 180), anchor="mm")
    
    return im

# 6. SCENE 4: Promo Coupon Card & Value Stack (14.2s - 17.4s, frames 430-524)
def render_frame_scene_4(frame_idx, rel_t):
    im = Image.new("RGB", (W, H))
    draw_gradient_bg(im, (20, 15, 25), (6, 5, 10))
    draw = ImageDraw.Draw(im)
    draw_progress_bar(draw, frame_idx)
    
    draw_header_pill(draw, "OFERTA EXCLUSIVA DO INSTAGRAM", y=48, color=(255, 230, 0))
    
    # Pulse coupon outline
    pulse_w = int(2 + 1 * math.sin(rel_t * math.pi * 4.0))
    card_box = [45, 130, W - 45, 650]
    draw.rounded_rectangle(card_box, radius=28, fill=(16, 18, 28), outline=(255, 230, 0), width=pulse_w)
    
    draw.text((W // 2, 185), "CÓDIGO DE CUPÃO OFICIAL:", font=get_font(23, True), fill=(200, 205, 220), anchor="mm")
    
    # Glowing Coupon code pill
    draw.rounded_rectangle([85, 230, W - 85, 340], radius=20, fill=(10, 11, 16), outline=(255, 230, 0), width=3)
    draw.text((W // 2, 285), "DARKINSTA", font=get_font(54, True), fill=(255, 230, 0), anchor="mm")
    
    draw.text((W // 2, 390), "-25% DE DESCONTO IMEDIATO", font=get_font(28, True), fill=(255, 255, 255), anchor="mm")
    draw.text((W // 2, 435), "Válido em toda a coleção oficial de vestuário", font=get_font(19, False), fill=(180, 185, 200), anchor="mm")
    
    draw.line([(80, 480), (W - 80, 480)], fill=(40, 44, 60), width=2)
    draw.text((W // 2, 525), "• T-Shirts a partir de 22,40 € (Classic) / 29,90 € (Oversized)", font=get_font(18, True), fill=(255, 230, 0), anchor="mm")
    draw.text((W // 2, 575), "• Sweatshirts com Capuz por apenas 44,90 €", font=get_font(18, True), fill=(255, 230, 0), anchor="mm")
    
    # Perks
    perks_y = 690
    perks = [
        ("+ PACK DE AUTOCOLANTES GRÁTIS", "Incluído de oferta em todas as encomendas de vestuário"),
        ("+ ENTREGA EM MÃO NA MARGEM SUL & LISBOA", "Opção de levantamento ou entrega local sem portes"),
        ("+ ENVIO EXPRESSO CTT 24/48H", "Entrega rápida e segura em todo o território nacional")
    ]
    
    for i, (title, desc) in enumerate(perks):
        py = perks_y + i * 135
        draw.rounded_rectangle([45, py, W - 45, py + 115], radius=18, fill=(15, 17, 24), outline=(35, 38, 55), width=2)
        draw.text((W // 2, py + 38), title, font=get_font(20, True), fill=(255, 255, 255), anchor="mm")
        draw.text((W // 2, py + 75), desc, font=get_font(15, False), fill=(160, 165, 180), anchor="mm")
        
    draw.text((W // 2, 1190), "PROMOÇÃO TEMPORÁRIA • STOCK LIMITADO", font=get_font(21, True), fill=(230, 20, 38), anchor="mm")
    
    return im

# 7. SCENE 5: Outro & Call to Action (17.4s - 20.0s, frames 525-599)
def render_frame_scene_5(frame_idx, rel_t):
    im = Image.new("RGB", (W, H))
    draw_gradient_bg(im, (16, 18, 28), (5, 5, 8))
    draw = ImageDraw.Draw(im)
    draw_progress_bar(draw, frame_idx)
    
    # Logo
    lw = 240
    lh = int(logo_img.height * (lw / logo_img.width))
    logo_res = logo_img.resize((lw, lh), Image.Resampling.LANCZOS)
    im.paste(logo_res, ((W - lw) // 2, 130), logo_res)
    
    draw.text((W // 2, 390), "DARK GHOSTRIDER", font=get_font(40, True), fill=(255, 255, 255), anchor="mm")
    draw.text((W // 2, 440), "STREET DIVISION • LISBOA", font=get_font(20, True), fill=(255, 230, 0), anchor="mm")
    
    # Main CTA Box
    box_y = 520
    draw.rounded_rectangle([45, box_y, W - 45, box_y + 360], radius=28, fill=(18, 20, 30), outline=(255, 230, 0), width=3)
    
    draw.text((W // 2, box_y + 50), "COMPRA DIRETAMENTE NO SITE:", font=get_font(22, True), fill=(200, 205, 220), anchor="mm")
    
    # Yellow Website Button
    draw.rounded_rectangle([75, box_y + 90, W - 75, box_y + 175], radius=18, fill=(255, 230, 0))
    draw.text((W // 2, box_y + 132), "DARKGHOSTRIDER.COM", font=get_font(30, True), fill=(0, 0, 0), anchor="mm")
    
    draw.text((W // 2, box_y + 225), "LINK DIRETO NA BIO DO INSTAGRAM", font=get_font(22, True), fill=(255, 255, 255), anchor="mm")
    draw.text((W // 2, box_y + 270), "@DARK.GHOSTRIDER", font=get_font(27, True), fill=(255, 230, 0), anchor="mm")
    
    draw.text((W // 2, box_y + 315), "Usa o cupão DARKINSTA no carrinho", font=get_font(18, False), fill=(180, 185, 200), anchor="mm")
    
    # Urgency footer
    draw.rounded_rectangle([55, 960, W - 55, 1080], radius=18, fill=(230, 20, 38))
    draw.text((W // 2, 1005), "GARANTE A TUA PEÇA AGORA", font=get_font(26, True), fill=(255, 255, 255), anchor="mm")
    draw.text((W // 2, 1045), "ENQUANTO HÁ DISPONIBILIDADE DE TAMANHO", font=get_font(16, True), fill=(255, 255, 255), anchor="mm")
    
    draw.text((W // 2, 1160), "Marca Oficial Biker Portuguesa", font=get_font(18, True), fill=(160, 165, 180), anchor="mm")

    return im

def render_frame(f):
    if f < 90:
        return render_frame_scene_1(f, f / 90.0)
    elif f < 175:
        return render_frame_scene_2a(f, (f - 90) / 85.0)
    elif f < 260:
        return render_frame_scene_2b(f, (f - 175) / 85.0)
    elif f < 345:
        return render_frame_scene_3a(f, (f - 260) / 85.0)
    elif f < 430:
        return render_frame_scene_3b(f, (f - 345) / 85.0)
    elif f < 525:
        return render_frame_scene_4(f, (f - 430) / 95.0)
    else:
        return render_frame_scene_5(f, (f - 525) / 75.0)

# Build Audio Beat
def build_audio(audio_path):
    print("Generating soundtrack beat...")
    from generate_audio_beat import generate_promo_beat
    # Use existing scratch_promo_beat.wav or re-generate
    if os.path.exists('scratch_promo_beat.wav'):
        import shutil
        shutil.copy('scratch_promo_beat.wav', audio_path)
    else:
        generate_promo_beat(duration_sec=DURATION, output_wav=audio_path)
    print("Audio ready:", audio_path)

def build_video():
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    audio_path = os.path.join(video_dir, 'promo_beat.wav')
    build_audio(audio_path)
    
    output_video = os.path.join(video_dir, 'promo_darkinsta_reels.mp4')
    
    cmd = [
        ffmpeg_exe,
        '-y',
        '-f', 'rawvideo',
        '-vcodec', 'rawvideo',
        '-s', f'{W}x{H}',
        '-pix_fmt', 'rgb24',
        '-r', str(FPS),
        '-i', '-',
        '-i', audio_path,
        '-c:v', 'libx264',
        '-preset', 'fast',
        '-crf', '19',
        '-pix_fmt', 'yuv420p',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-shortest',
        output_video
    ]
    
    print(f"Launching FFmpeg encoder to {output_video}...")
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    for f in range(TOTAL_FRAMES):
        if f % 60 == 0:
            print(f"Rendering frame {f}/{TOTAL_FRAMES} ({(f/TOTAL_FRAMES)*100:.1f}%)...")
        frame_img = render_frame(f)
        proc.stdin.write(frame_img.tobytes())
        
    proc.stdin.close()
    proc.wait()
    
    size_mb = os.path.getsize(output_video) / (1024 * 1024)
    print(f"SUCCESS! Video created: {output_video} ({size_mb:.2f} MB, {DURATION}s, {FPS}fps)")

if __name__ == '__main__':
    build_video()
