import os
import sys
import math
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import imageio_ffmpeg

W, H = 720, 1280
FPS = 30
DURATION = 18.0
TOTAL_FRAMES = int(DURATION * FPS) # 540 frames

font_bold_path = r'C:\Windows\Fonts\bahnschrift.ttf'
font_segoe_path = r'C:\Windows\Fonts\segoeuib.ttf'

def get_font(size, bold=True):
    path = font_bold_path if bold else font_segoe_path
    try:
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()

base_dir = os.getcwd()
apparel_dir = os.path.join(base_dir, 'assets', 'images', 'apparel')
img_dir = os.path.join(base_dir, 'assets', 'images')
video_dir = os.path.join(base_dir, 'assets', 'videos')
os.makedirs(video_dir, exist_ok=True)

# Load master images
im_back_raw = Image.open(os.path.join(apparel_dir, 'hoodie_oficial_preto_back.jpg')).convert("RGB")
im_front_raw = Image.open(os.path.join(apparel_dir, 'hoodie_oficial_preto_front.jpg')).convert("RGB")
im_a3_raw = Image.open(os.path.join(apparel_dir, 'dark_side_rider_costas_a3_black.jpg')).convert("RGB")
logo_raw = Image.open(os.path.join(img_dir, 'logo.png')).convert("RGBA")

# Helper for fullbleed cropping with smooth zoom and pan
def get_fullbleed_crop(img, zoom=1.0, pan_x=0.0, pan_y=0.0):
    target_ratio = W / float(H) # 0.5625
    iw, ih = img.size
    img_ratio = iw / float(ih)
    
    if img_ratio > target_ratio:
        crop_h = ih / zoom
        crop_w = crop_h * target_ratio
    else:
        crop_w = iw / zoom
        crop_h = crop_w / target_ratio
        
    center_x = iw * (0.5 + pan_x)
    center_y = ih * (0.5 + pan_y)
    
    x1 = int(center_x - crop_w / 2.0)
    y1 = int(center_y - crop_h / 2.0)
    x2 = int(x1 + crop_w)
    y2 = int(y1 + crop_h)
    
    if x1 < 0:
        x2 -= x1
        x1 = 0
    if y1 < 0:
        y2 -= y1
        y1 = 0
    if x2 > iw:
        x1 -= (x2 - iw)
        x2 = iw
    if y2 > ih:
        y1 -= (y2 - ih)
        y2 = ih
        
    cropped = img.crop((max(0, x1), max(0, y1), min(iw, x2), min(ih, y2)))
    return cropped.resize((W, H), Image.Resampling.LANCZOS)

# Vectorized lighting sheen sweep
def apply_light_sheen(pil_img, sweep_t, intensity=38.0):
    arr = np.array(pil_img, dtype=np.float32)
    y_coords, x_coords = np.ogrid[:H, :W]
    diag = (x_coords + y_coords * 0.45) / (W + H * 0.45)
    dist = (diag - sweep_t) / 0.13
    sheen = np.exp(-dist * dist) * intensity
    
    arr[:, :, 0] += sheen * 0.95
    arr[:, :, 1] += sheen * 0.90
    arr[:, :, 2] += sheen * 0.70
    np.clip(arr, 0, 255, out=arr)
    return Image.fromarray(arr.astype(np.uint8))

def draw_progress_bar(draw, frame_idx):
    progress = frame_idx / float(TOTAL_FRAMES)
    bar_w = int(W * progress)
    draw.rectangle([0, 0, W, 4], fill=(30, 32, 45))
    draw.rectangle([0, 0, bar_w, 4], fill=(255, 230, 0))

def draw_studio_brackets(draw, tag_left="DARK GHOSTRIDER // SHOWROOM", tag_right="REF: DGR-SW-01 • 280 GSM"):
    bracket_len = 26
    bracket_dist = 22
    w_th = 2
    c = (210, 215, 230)
    
    # Top-Left
    draw.line([(bracket_dist, bracket_dist), (bracket_dist + bracket_len, bracket_dist)], fill=c, width=w_th)
    draw.line([(bracket_dist, bracket_dist), (bracket_dist, bracket_dist + bracket_len)], fill=c, width=w_th)
    # Top-Right
    draw.line([(W - bracket_dist, bracket_dist), (W - bracket_dist - bracket_len, bracket_dist)], fill=c, width=w_th)
    draw.line([(W - bracket_dist, bracket_dist), (W - bracket_dist, bracket_dist + bracket_len)], fill=c, width=w_th)
    # Bottom-Left
    draw.line([(bracket_dist, H - bracket_dist), (bracket_dist + bracket_len, H - bracket_dist)], fill=c, width=w_th)
    draw.line([(bracket_dist, H - bracket_dist), (bracket_dist, bracket_dist - bracket_len)], fill=c, width=w_th)
    # Bottom-Right
    draw.line([(W - bracket_dist, H - bracket_dist), (W - bracket_dist - bracket_len, H - bracket_dist)], fill=c, width=w_th)
    draw.line([(W - bracket_dist, H - bracket_dist), (W - bracket_dist, H - bracket_dist - bracket_len)], fill=c, width=w_th)
    
    # Minimal top bar
    draw.rectangle([bracket_dist + 36, bracket_dist - 4, W - bracket_dist - 36, bracket_dist + 22], fill=(12, 14, 20, 210))
    f_micro = get_font(12, True)
    draw.text((bracket_dist + 44, bracket_dist + 9), tag_left, font=f_micro, fill=(230, 235, 250), anchor="lm")
    draw.text((W - bracket_dist - 44, bracket_dist + 9), tag_right, font=f_micro, fill=(255, 230, 0), anchor="rm")

# Scene 1: Fullscreen Silhouette & Showroom Look (0.0s - 3.8s, frames 0-113)
def render_s1(f, t):
    zoom = 1.0 + 0.08 * t
    im = get_fullbleed_crop(im_back_raw, zoom=zoom, pan_y=0.0)
    sheen_t = -0.2 + 1.4 * t
    im = apply_light_sheen(im, sheen_t, intensity=42.0)
    
    draw = ImageDraw.Draw(im)
    draw_progress_bar(draw, f)
    draw_studio_brackets(draw, "DARK GHOSTRIDER // SHOWROOM", "HEAVYWEIGHT 280G")
    
    # Top floating badge
    cw, ch = 440, 52
    cx, cy = (W - cw) // 2, 75
    draw.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=16, fill=(12, 14, 20), outline=(255, 230, 0), width=2)
    draw.text((W // 2, cy + ch // 2), "SWEATSHIRT COM CAPUZ OFICIAL", font=get_font(18, True), fill=(255, 255, 255), anchor="mm")
    
    # Bottom specs teaser
    draw.rounded_rectangle([55, 1165, W - 55, 1225], radius=16, fill=(12, 14, 20), outline=(55, 58, 80), width=2)
    draw.text((W // 2, 1195), "EDITION 01 • 100% PRETO STEALTH ALL BLACK", font=get_font(16, True), fill=(255, 230, 0), anchor="mm")
    return im

# Scene 2: Deep Macro Zoom on the Big Logo (3.8s - 8.0s, frames 114-239)
def render_s2(f, t):
    # Zoom starts at 1.30 and pushes to 1.55, panning smoothly across helmet
    zoom = 1.30 + 0.25 * t
    pan_x = 0.02 * math.sin(t * math.pi)
    pan_y = 0.04 - 0.03 * t
    im = get_fullbleed_crop(im_a3_raw, zoom=zoom, pan_x=pan_x, pan_y=pan_y)
    
    # Glint sweep across metal & visor
    sheen_t = -0.2 + 1.4 * t
    im = apply_light_sheen(im, sheen_t, intensity=45.0)
    
    draw = ImageDraw.Draw(im)
    draw_progress_bar(draw, f)
    draw_studio_brackets(draw, "MACRO DETAIL // MASTER A3 PRINT", "300 DPI • DTF ULTRA HD")
    
    # Lower technical card
    card_y = 1010
    draw.rounded_rectangle([40, card_y, W - 40, 1220], radius=22, fill=(10, 12, 18), outline=(255, 230, 0), width=2)
    draw.text((W // 2, card_y + 35), "MEGA ESTAMPA A3 MASTER // 300 DPI", font=get_font(21, True), fill=(255, 255, 255), anchor="mm")
    draw.text((W // 2, card_y + 78), "• Estampa DTF em Alta Densidade com Toque Zero", font=get_font(16, False), fill=(205, 210, 225), anchor="mm")
    draw.text((W // 2, card_y + 118), "• Cores Ultra Vivas e Resistência a +60 Lavagens", font=get_font(16, False), fill=(205, 210, 225), anchor="mm")
    draw.text((W // 2, card_y + 160), "• Dimensão Gigante 30 × 30 cm nas Costas", font=get_font(16, True), fill=(255, 230, 0), anchor="mm")
    return im

# Scene 3: Front View & Construction Detail (8.0s - 11.5s, frames 240-344)
def render_s3(f, t):
    zoom = 1.0 + 0.08 * t
    im = get_fullbleed_crop(im_front_raw, zoom=zoom, pan_y=0.0)
    sheen_t = -0.2 + 1.4 * t
    im = apply_light_sheen(im, sheen_t, intensity=40.0)
    
    draw = ImageDraw.Draw(im)
    draw_progress_bar(draw, f)
    draw_studio_brackets(draw, "FRONT VIEW // HOOD & POCKET", "BOLSO CANGURU DUPLO")
    
    card_y = 1010
    draw.rounded_rectangle([40, card_y, W - 40, 1220], radius=22, fill=(10, 12, 18), outline=(50, 54, 75), width=2)
    draw.text((W // 2, card_y + 35), "CONSTRUÇÃO PREMIUM HEAVYWEIGHT 280G", font=get_font(21, True), fill=(255, 255, 255), anchor="mm")
    draw.text((W // 2, card_y + 78), "• 50% Algodão Ring Spun / 50% Poliéster Reciclado", font=get_font(16, False), fill=(205, 210, 225), anchor="mm")
    draw.text((W // 2, card_y + 118), "• Capuz Duplo Forrado com Cordões Tonais Reforçados", font=get_font(16, False), fill=(205, 210, 225), anchor="mm")
    draw.text((W // 2, card_y + 160), "• Emblema Oficial DTF no Peito Esquerdo", font=get_font(16, True), fill=(255, 230, 0), anchor="mm")
    return im

# Scene 4: Full Backprint Reveal & Promo Price (11.5s - 15.5s, frames 345-464)
def render_s4(f, t):
    # Gentle zoom from 1.05 down to 1.0 (revealing the whole piece)
    zoom = 1.05 - 0.04 * t
    im = get_fullbleed_crop(im_back_raw, zoom=zoom, pan_y=0.0)
    
    draw = ImageDraw.Draw(im)
    draw_progress_bar(draw, f)
    draw_studio_brackets(draw, "OFERTA EXCLUSIVA // INSTAGRAM", "PROMOÇÃO ATIVA")
    
    # Sleek bottom luxury offer card
    card_y = 740
    pulse_b = int(2 + 1 * math.sin(t * math.pi * 3.0))
    draw.rounded_rectangle([35, card_y, W - 35, 1225], radius=24, fill=(12, 14, 22), outline=(255, 230, 0), width=pulse_b)
    
    draw.text((W // 2, card_y + 38), "SWEATSHIRT COM CAPUZ OFICIAL", font=get_font(24, True), fill=(255, 255, 255), anchor="mm")
    draw.text((W // 2, card_y + 75), "Edição Limitada 100% Preto Stealth (XS ao 4XL)", font=get_font(16, False), fill=(185, 190, 205), anchor="mm")
    
    # Price box
    p_box_y = card_y + 105
    draw.rounded_rectangle([65, p_box_y, W - 65, p_box_y + 105], radius=16, fill=(8, 9, 14), outline=(255, 230, 0), width=2)
    draw.text((W // 2, p_box_y + 28), "PREÇO NORMAL: 59,90 €", font=get_font(16, True), fill=(140, 145, 160), anchor="mm")
    draw.text((W // 2, p_box_y + 72), "COM DARKINSTA: 44,90 €", font=get_font(30, True), fill=(255, 230, 0), anchor="mm")
    
    # Green discount pill
    draw.rounded_rectangle([75, card_y + 230, W - 75, card_y + 282], radius=12, fill=(25, 135, 84))
    draw.text((W // 2, card_y + 256), "POUPAS 15,00 € (-25% DE DESCONTO)", font=get_font(17, True), fill=(255, 255, 255), anchor="mm")
    
    # Perks
    draw.text((W // 2, card_y + 320), "+ OFERTA DE PACK DE AUTOCOLANTES OFICIAIS", font=get_font(16, True), fill=(255, 255, 255), anchor="mm")
    draw.text((W // 2, card_y + 360), "Entrega em Mão em Lisboa / Margem Sul ou CTT Expresso", font=get_font(14, False), fill=(170, 175, 190), anchor="mm")
    draw.text((W // 2, card_y + 415), "DARKGHOSTRIDER.COM • LINK NA BIO", font=get_font(21, True), fill=(255, 230, 0), anchor="mm")
    return im

# Scene 5: Outro & Final Call to Action (15.5s - 18.0s, frames 465-539)
def render_s5(f, t):
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)
    
    # Gradient backdrop
    for y in range(H):
        alpha = y / float(H)
        r = int(14 * (1 - alpha) + 4 * alpha)
        g = int(16 * (1 - alpha) + 4 * alpha)
        b = int(24 * (1 - alpha) + 6 * alpha)
        draw.line([(0, y), (W, y)], fill=(r, g, b))
        
    draw_progress_bar(draw, f)
    
    # Logo
    lw = 240
    lh = int(logo_raw.height * (lw / logo_raw.width))
    logo_res = logo_raw.resize((lw, lh), Image.Resampling.LANCZOS)
    im.paste(logo_res, ((W - lw) // 2, 140), logo_res)
    
    draw.text((W // 2, 400), "DARK GHOSTRIDER", font=get_font(40, True), fill=(255, 255, 255), anchor="mm")
    draw.text((W // 2, 450), "STREETWEAR & RIDER APPAREL", font=get_font(21, True), fill=(255, 230, 0), anchor="mm")
    
    # Main Box
    box_y = 530
    draw.rounded_rectangle([45, box_y, W - 45, box_y + 350], radius=26, fill=(16, 18, 28), outline=(255, 230, 0), width=3)
    
    draw.text((W // 2, box_y + 50), "COMPRA DIRETAMENTE NO SITE:", font=get_font(22, True), fill=(200, 205, 220), anchor="mm")
    
    # Website button
    draw.rounded_rectangle([75, box_y + 90, W - 75, box_y + 175], radius=18, fill=(255, 230, 0))
    draw.text((W // 2, box_y + 132), "DARKGHOSTRIDER.COM", font=get_font(30, True), fill=(0, 0, 0), anchor="mm")
    
    draw.text((W // 2, box_y + 225), "LINK DIRETO NA BIO DO INSTAGRAM", font=get_font(22, True), fill=(255, 255, 255), anchor="mm")
    draw.text((W // 2, box_y + 270), "@DARK.GHOSTRIDER", font=get_font(26, True), fill=(255, 230, 0), anchor="mm")
    
    draw.text((W // 2, box_y + 312), "Usa o cupão DARKINSTA (-25% OFF)", font=get_font(18, False), fill=(180, 185, 200), anchor="mm")
    
    # Bottom Urgency
    draw.rounded_rectangle([55, 960, W - 55, 1070], radius=18, fill=(230, 20, 38))
    draw.text((W // 2, 1000), "GARANTE A TUA PEÇA AGORA", font=get_font(25, True), fill=(255, 255, 255), anchor="mm")
    draw.text((W // 2, 1038), "ENQUANTO HÁ DISPONIBILIDADE DE TAMANHO", font=get_font(15, True), fill=(255, 255, 255), anchor="mm")
    
    draw.text((W // 2, 1160), "Marca Oficial Biker Portuguesa", font=get_font(18, True), fill=(160, 165, 180), anchor="mm")
    return im

def render_hoodie_frame(f):
    if f < 114:
        return render_s1(f, f / 114.0)
    elif f < 240:
        return render_s2(f, (f - 114) / 126.0)
    elif f < 345:
        return render_s3(f, (f - 240) / 105.0)
    elif f < 465:
        return render_s4(f, (f - 345) / 120.0)
    else:
        return render_s5(f, (f - 465) / 75.0)

def build_hoodie_video():
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    audio_path = os.path.join(video_dir, 'hoodie_showroom_beat.wav')
    
    sys.path.append(os.path.join(base_dir, 'scripts'))
    from generate_hoodie_audio import generate_hoodie_showroom_audio
    generate_hoodie_showroom_audio(duration_sec=DURATION, output_wav=audio_path)
    
    output_video = os.path.join(video_dir, 'promo_hoodie_big_logo_fullscreen.mp4')
    
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
    
    print(f"Encoding Fullscreen Hoodie Video to: {output_video}...")
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    for f in range(TOTAL_FRAMES):
        if f % 60 == 0:
            print(f"Rendering frame {f}/{TOTAL_FRAMES} ({(f/TOTAL_FRAMES)*100:.1f}%)...")
        frame_img = render_hoodie_frame(f)
        proc.stdin.write(frame_img.tobytes())
        
    proc.stdin.close()
    proc.wait()
    
    size_mb = os.path.getsize(output_video) / (1024 * 1024)
    print(f"SUCCESS! Hoodie Showroom Video created: {output_video} ({size_mb:.2f} MB, {DURATION}s, {FPS}fps)")

if __name__ == '__main__':
    build_hoodie_video()
