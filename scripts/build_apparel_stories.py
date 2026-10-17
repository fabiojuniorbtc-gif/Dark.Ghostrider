# -*- coding: utf-8 -*-
"""
Dedicated Batch Video Generator for all 9 Apparel Items (T-Shirts and Sweats)
Outputs vertical 9:16 (720x1280 @ 30fps) videos optimized for Instagram Stories, Reels, and TikTok.
Includes:
- Dynamic multi-slide animation (Front view, A3 Back print view, Yellow Fluo variant & CTA)
- Subtle Ken Burns smooth zoom
- Official Dark Ghostrider branding, verified Instagram UI, pulsating sticker and link
- Official pricing, Portugal shipping notice (4.85 € / 4-6 dias úteis)
- Dynamically synthesized high-energy Biker Synth/Phonk soundtrack
"""

import os, sys, math, time, subprocess, wave, shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import imageio_ffmpeg

WIDTH = 720
HEIGHT = 1280
FPS = 30

STORIES_DIR = os.path.abspath("assets/videos/stories")
POSTERS_DIR = os.path.abspath("assets/images/stories_posters")
os.makedirs(STORIES_DIR, exist_ok=True)
os.makedirs(POSTERS_DIR, exist_ok=True)

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

def get_font(name="arialbd.ttf", size=32):
    try:
        return ImageFont.truetype(name, size)
    except Exception:
        try:
            return ImageFont.truetype("arial.ttf", size)
        except Exception:
            return ImageFont.load_default()

FONT_TITLE = get_font("impact.ttf", 50)
FONT_SUB = get_font("arialbd.ttf", 25)
FONT_BODY = get_font("arialbd.ttf", 21)
FONT_SMALL = get_font("arialbd.ttf", 16)
FONT_BADGE = get_font("impact.ttf", 22)
FONT_SHIPPING = get_font("arialbd.ttf", 17)

# -------------------------------------------------------------
# VECTOR GRAPHIC HELPERS (No missing Unicode / Tofu glyphs)
# -------------------------------------------------------------
def draw_vector_link_chain(draw, cx, cy, size=22, color=(12, 14, 18, 255)):
    draw.rounded_rectangle([cx - size + 2, cy - size//2, cx + 2, cy + size//2], radius=size//3, outline=color, width=3)
    draw.rounded_rectangle([cx - 2, cy - size//2, cx + size - 2, cy + size//2], radius=size//3, outline=color, width=3)

def draw_vector_arrow(draw, cx, cy, size=16, color=(12, 14, 18, 255)):
    draw.line([cx - size//2, cy + size//2, cx + size//2, cy - size//2], fill=color, width=3)
    draw.line([cx + size//2 - 6, cy - size//2, cx + size//2, cy - size//2], fill=color, width=3)
    draw.line([cx + size//2, cy - size//2 + 6, cx + size//2, cy - size//2], fill=color, width=3)

def draw_vector_heart(draw, cx, cy, size=18, color=(255, 255, 255, 240)):
    pts = [
        (cx, cy + size//2),
        (cx - size//2, cy),
        (cx - size//3, cy - size//2),
        (cx, cy - size//4),
        (cx + size//3, cy - size//2),
        (cx + size//2, cy),
        (cx, cy + size//2)
    ]
    draw.polygon(pts, fill=color)

def draw_vector_plane(draw, cx, cy, size=18, color=(255, 255, 255, 240)):
    pts = [
        (cx + size//2, cy - size//2),
        (cx - size//2, cy - size//5),
        (cx - size//4, cy + size//3),
        (cx - size//10, cy + size//8),
        (cx + size//2, cy - size//2)
    ]
    draw.polygon(pts, fill=color)

def draw_story_header(draw, progress, current_slide, total_slides):
    bar_top = 22
    bar_h = 3
    spacing = 6
    margin = 20
    avail_w = WIDTH - (margin * 2) - (spacing * (total_slides - 1))
    seg_w = avail_w / total_slides
    
    for i in range(total_slides):
        sx = margin + i * (seg_w + spacing)
        ex = sx + seg_w
        draw.rounded_rectangle([sx, bar_top, ex, bar_top + bar_h], radius=2, fill=(255, 255, 255, 75))
        if i < current_slide:
            draw.rounded_rectangle([sx, bar_top, ex, bar_top + bar_h], radius=2, fill=(255, 255, 255, 250))
        elif i == current_slide:
            fill_w = seg_w * progress
            if fill_w > 1:
                draw.rounded_rectangle([sx, bar_top, sx + fill_w, bar_top + bar_h], radius=2, fill=(255, 255, 255, 250))
                
    header_y = 42
    av_size = 40
    av_x = margin
    name_x = av_x + av_size + 12
    draw.text((name_x, header_y + 4), "dark.ghostrider", fill=(255, 255, 255, 255), font=FONT_SMALL)
    
    # Verified badge
    badge_x = name_x + 114
    badge_y = header_y + 5
    draw.ellipse([badge_x, badge_y, badge_x + 14, badge_y + 14], fill=(59, 130, 246, 255))
    draw.line([badge_x + 3, badge_y + 7, badge_x + 6, badge_y + 10], fill=(255, 255, 255, 255), width=2)
    draw.line([badge_x + 6, badge_y + 10, badge_x + 11, badge_y + 4], fill=(255, 255, 255, 255), width=2)
    
    draw.text((badge_x + 22, header_y + 5), "2 h", fill=(190, 190, 200, 200), font=FONT_SMALL)
    
    # Close icon
    draw.line([WIDTH - margin - 14, header_y + 8, WIDTH - margin - 2, header_y + 20], fill=(255, 255, 255, 220), width=2)
    draw.line([WIDTH - margin - 2, header_y + 8, WIDTH - margin - 14, header_y + 20], fill=(255, 255, 255, 220), width=2)

def draw_story_footer(draw):
    pill_h = 44
    pill_y = HEIGHT - 68
    pill_w = WIDTH - 120
    pill_x = 20
    draw.rounded_rectangle([pill_x, pill_y, pill_x + pill_w, pill_y + pill_h], radius=22, outline=(255, 255, 255, 70), width=1, fill=(20, 20, 26, 180))
    draw.text((pill_x + 20, pill_y + 12), "Enviar mensagem...", fill=(180, 180, 190, 200), font=FONT_SMALL)
    
    heart_cx = pill_x + pill_w + 30
    draw_vector_heart(draw, heart_cx, pill_y + 22, size=20)
    plane_cx = heart_cx + 40
    draw_vector_plane(draw, plane_cx, pill_y + 22, size=20)

def draw_story_link_sticker(canvas, text, center_x, center_y, scale=1.0):
    w = int(370 * scale)
    h = int(58 * scale)
    bx = int(center_x - w / 2)
    by = int(center_y - h / 2)
    
    sticker = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(sticker)
    
    # Yellow neon halo
    for offset, alpha in [(8, 40), (4, 90), (2, 160)]:
        sdraw.rounded_rectangle([20 - offset, 20 - offset, 20 + w + offset, 20 + h + offset], radius=int(26 * scale), fill=(246, 255, 0, alpha))
        
    # White background
    sdraw.rounded_rectangle([20, 20, 20 + w, 20 + h], radius=int(26 * scale), fill=(255, 255, 255, 255))
    
    chain_x = 20 + int(24 * scale)
    chain_y = 20 + int(h / 2)
    draw_vector_link_chain(sdraw, chain_x, chain_y, size=int(18 * scale))
    
    arrow_x = 20 + w - int(24 * scale)
    arrow_y = chain_y
    draw_vector_arrow(sdraw, arrow_x, arrow_y, size=int(16 * scale))

    font_s = get_font("arialbd.ttf", int(17 * scale))
    tb = sdraw.textbbox((0, 0), text, font=font_s)
    tw = tb[2] - tb[0]
    th = tb[3] - tb[1]
    
    # Centered horizontally inside the white pill
    tx = 20 + (w - tw) // 2
    ty = 20 + (h - th) // 2 - 2
    sdraw.text((tx, ty), text, fill=(12, 14, 18, 255), font=font_s)
    
    canvas.alpha_composite(sticker, (bx - 20, by - 20))

def create_circular_logo_badge(img, size=135, border_color=(246, 255, 0, 255)):
    thumb = ImageOps.fit(img, (size, size), Image.Resampling.LANCZOS)
    badge = Image.new("RGBA", (size + 40, size + 40), (0, 0, 0, 0))
    bdraw = ImageDraw.Draw(badge)
    cx = (size + 40) // 2
    cy = (size + 40) // 2
    r = size // 2
    
    for off, alpha in [(8, 40), (4, 90), (2, 160)]:
        bdraw.ellipse([cx - r - off, cy - r - off, cx + r + off, cy + r + off], fill=(border_color[0], border_color[1], border_color[2], alpha))
        
    bdraw.ellipse([cx - r - 4, cy - r - 4, cx + r + 4, cy + r + 4], fill=(255, 255, 255, 255))
    
    mask = Image.new("L", (size, size), 0)
    mdraw = ImageDraw.Draw(mask)
    mdraw.ellipse([0, 0, size, size], fill=255)
    badge.paste(thumb, (cx - r, cy - r), mask)
    return badge

# -------------------------------------------------------------
# AUDIO SYNTHESIZER FOR HIGH ENERGY BIKER VIBES
# -------------------------------------------------------------
def generate_story_audio(duration, variant_idx=0, out_wav_path="temp_audio.wav"):
    sr = 44100
    total_samples = int(sr * duration)
    bpm = 130.0 + (variant_idx % 5) * 2.5
    spb = 60.0 / bpm
    
    left = np.zeros(total_samples, dtype=np.float32)
    right = np.zeros(total_samples, dtype=np.float32)
    
    # Punchy Kick
    kick_len = int(0.32 * sr)
    t_k = np.arange(kick_len) / sr
    f_k = 50 + 140 * np.exp(-t_k * 34)
    phase_k = np.cumsum(f_k * 2 * np.pi / sr)
    env_k = np.exp(-t_k * 9.0)
    click = np.sin(2 * np.pi * 2000 * t_k) * np.exp(-t_k * 150) * 0.4
    kick = np.tanh((np.sin(phase_k) * env_k + click) * 1.7) * 0.95
    
    # Sharp Snare
    snare_len = int(0.26 * sr)
    t_s = np.arange(snare_len) / sr
    noise = np.random.uniform(-1, 1, snare_len)
    body = np.sin(2 * np.pi * 220 * t_s) * np.exp(-t_s * 25) * 0.5
    snare = (noise * np.exp(-t_s * 16) * 0.70 + body) * 0.80
    
    # Hi-hats
    hat_len = int(0.06 * sr)
    t_h = np.arange(hat_len) / sr
    hat = np.random.uniform(-1, 1, hat_len) * np.exp(-t_h * 60) * 0.30
    
    # Crash
    crash_len = int(2.2 * sr)
    t_c = np.arange(crash_len) / sr
    crash = np.random.uniform(-1, 1, crash_len) * np.exp(-t_c * 2.0) * 0.55
    
    total_beats = int(duration / spb)
    for b in range(total_beats):
        pos = int(b * spb * sr)
        if b % 2 == 0 or (b % 4 == 3 and b > 3):
            en = min(total_samples, pos + kick_len)
            left[pos:en] += kick[:en - pos] * 0.92
            right[pos:en] += kick[:en - pos] * 0.92
        if b % 2 == 1:
            en = min(total_samples, pos + snare_len)
            left[pos:en] += snare[:en - pos] * 0.78
            right[pos:en] += snare[:en - pos] * 0.78
        for h in range(4):
            h_pos = int((b + h * 0.25) * spb * sr)
            if h_pos + hat_len < total_samples:
                vol = 0.85 if h == 0 else 0.52
                left[h_pos:h_pos + hat_len] += hat * vol
                right[h_pos:h_pos + hat_len] += hat * vol * 0.9
                
    # Rolling Bassline
    bass_roots = [
        [43.7, 43.7, 51.9, 43.7, 58.3, 58.3, 51.9, 43.7],
        [41.2, 41.2, 49.0, 41.2, 55.0, 55.0, 49.0, 41.2],
        [46.2, 46.2, 55.0, 46.2, 61.7, 61.7, 55.0, 46.2],
        [38.9, 38.9, 46.2, 38.9, 51.9, 51.9, 46.2, 38.9],
        [49.0, 49.0, 58.3, 49.0, 65.4, 65.4, 58.3, 49.0]
    ]
    notes = bass_roots[variant_idx % len(bass_roots)]
    note_dur = spb * 2
    for i in range(int(duration / note_dur) + 1):
        st = int(i * note_dur * sr)
        if st >= total_samples: break
        freq = notes[i % len(notes)]
        en = min(total_samples, int((i + 1) * note_dur * sr))
        t_n = np.arange(en - st) / sr
        sub = np.sin(2 * np.pi * freq * t_n)
        sub += 0.40 * np.sin(2 * np.pi * freq * 2 * t_n)
        sub = np.tanh(sub * 2.4) * 0.45
        sub *= np.minimum(1.0, t_n * 25.0)
        sub *= np.maximum(0.2, np.exp(-t_n * 0.5))
        left[st:en] += sub
        right[st:en] += sub

    # Dark Synth Arpeggio
    arp_scales = [
        [174.6, 207.7, 261.6, 311.1, 349.2],
        [164.8, 196.0, 246.9, 293.7, 329.6],
        [185.0, 220.0, 277.2, 329.6, 370.0],
        [155.6, 185.0, 233.1, 277.2, 311.1],
        [196.0, 233.1, 293.7, 349.2, 392.0]
    ]
    scale = arp_scales[variant_idx % len(arp_scales)]
    arp_step = spb / 4
    for step in range(int(duration / arp_step)):
        st = int(step * arp_step * sr)
        if st >= total_samples: break
        freq = scale[(step * 2 + variant_idx) % len(scale)]
        n_len = min(int(0.20 * sr), total_samples - st)
        t_l = np.arange(n_len) / sr
        saw = 2 * (t_l * freq - np.floor(t_l * freq + 0.5))
        lead = saw * np.exp(-t_l * 11) * 0.17
        pan = 0.5 + 0.3 * np.sin(step * 0.75)
        left[st:st + n_len] += lead * (1 - pan)
        right[st:st + n_len] += lead * pan

    # Crash hits
    crashes = [0.0, duration * 0.34, duration * 0.67]
    for c_t in crashes:
        pos = int(c_t * sr)
        if pos < total_samples:
            en = min(total_samples, pos + crash_len)
            left[pos:en] += crash[:en - pos] * 0.7
            right[pos:en] += crash[:en - pos] * 0.7
            
    peak = max(np.max(np.abs(left)), np.max(np.abs(right)), 1.0)
    left = np.tanh((left / peak) * 1.3) * 0.94
    right = np.tanh((right / peak) * 1.3) * 0.94
    
    left_i16 = (left * 32767).astype(np.int16)
    right_i16 = (right * 32767).astype(np.int16)
    stereo = np.empty((total_samples * 2,), dtype=np.int16)
    stereo[0::2] = left_i16
    stereo[1::2] = right_i16
    
    with wave.open(out_wav_path, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(stereo.tobytes())
        
    return out_wav_path

# -------------------------------------------------------------
# IMAGE CACHE & BADGES
# -------------------------------------------------------------
IMAGE_CACHE = {}

def get_cached_image(rel_path):
    if rel_path in IMAGE_CACHE:
        return IMAGE_CACHE[rel_path]
    abs_p = os.path.abspath(rel_path)
    if os.path.exists(abs_p):
        try:
            im = Image.open(abs_p).convert("RGBA")
            IMAGE_CACHE[rel_path] = im
            return im
        except Exception as e:
            print(f"Error loading {abs_p}: {e}")
    fb = Image.new("RGBA", (800, 800), (20, 20, 26, 255))
    IMAGE_CACHE[rel_path] = fb
    return fb

AVATAR_IMG = get_cached_image("assets/images/logo_opt1_profile.jpg")
SKULL_IMG = get_cached_image("assets/images/apparel/estampa_costas.jpg")

LOGO_BADGE_PROFILE = create_circular_logo_badge(AVATAR_IMG, size=135, border_color=(246, 255, 0, 255))
LOGO_BADGE_SKULL = create_circular_logo_badge(SKULL_IMG, size=135, border_color=(255, 42, 59, 255))

# -------------------------------------------------------------
# APPAREL PRODUCTS CONFIGURATION (9 ITEMS)
# -------------------------------------------------------------
APPAREL_STORIES = [
    {
        "id": "story_apparel_01_hoodie_oficial",
        "product_id": "hoodie-dark-ghostrider-oficial",
        "title": "SWEATSHIRT COM CAPUZ OFICIAL",
        "item_type": "Sweatshirt / Hoodie",
        "price": "59,90 €",
        "duration": 8.0,
        "link_text": "COMPRAR HOODIE OFICIAL",
        "slides": [
            {
                "image": "assets/images/apparel/hoodie_oficial_preto_front.jpg",
                "tag": "DROP 01 • OFICIAL",
                "title_line1": "SWEATSHIRT CAPUZ",
                "title_line2": "DARK GHOSTRIDER",
                "sub": "59,90 € • PRETO STEALTH & CYBER AMARELO",
                "badge_type": "skull",
                "show_shipping": False
            },
            {
                "image": "assets/images/apparel/hoodie_oficial_preto_back.jpg",
                "tag": "MEGA ESTAMPA A3 COSTAS",
                "title_line1": "ESTAMPA COSTAS A3",
                "title_line2": "ALTA DEFINIÇÃO DTF",
                "sub": "380G HEAVYWEIGHT • ALGODÃO PENTEADO ULTRA MACIO",
                "badge_type": "none",
                "show_shipping": False
            },
            {
                "image": "assets/images/apparel/hoodie_oficial_amarelo_back.jpg",
                "tag": "ENVIO RÁPIDO PORTUGAL",
                "title_line1": "GARANTE O TEU",
                "title_line2": "PRETO OU AMARELO",
                "sub": "DISPONÍVEL AGORA NA LOJA OFICIAL",
                "badge_type": "skull",
                "show_shipping": True
            }
        ]
    },
    {
        "id": "story_apparel_02_tshirt_oversized",
        "product_id": "tshirt-oversized-dark-ghostrider",
        "title": "T-SHIRT STREETWEAR OVERSIZED BOXY FIT",
        "item_type": "T-Shirt Oversized",
        "price": "39,90 €",
        "duration": 8.0,
        "link_text": "COMPRAR T-SHIRT OVERSIZED",
        "slides": [
            {
                "image": "assets/images/apparel/tshirt_preto_front.jpg",
                "tag": "STREET DIVISION • BOXY FIT",
                "title_line1": "T-SHIRT OVERSIZED",
                "title_line2": "STREET DIVISION",
                "sub": "39,90 € • ALGODÃO PESADO ESTRUTURADO",
                "badge_type": "skull",
                "show_shipping": False
            },
            {
                "image": "assets/images/apparel/tshirt_oversized_preto.jpg",
                "tag": "MEGA ESTAMPA A3 COSTAS",
                "title_line1": "ESTAMPA COSTAS A3",
                "title_line2": "DARK RIDER DIVISION",
                "sub": "CORTE RETRO MOTARD • OMBROS CAÍDOS",
                "badge_type": "profile",
                "show_shipping": False
            },
            {
                "image": "assets/images/apparel/tshirt_oversized_amarelo.jpg",
                "tag": "ENVIO RÁPIDO PORTUGAL",
                "title_line1": "PRETO OU AMARELO",
                "title_line2": "CLICA NO LINK",
                "sub": "DISPONÍVEL DO S AO XXL NA LOJA",
                "badge_type": "skull",
                "show_shipping": True
            }
        ]
    },
    {
        "id": "story_apparel_03_tshirt_classic_bio190",
        "product_id": "tshirt-classic-bio190-dark-ghostrider",
        "title": "T-SHIRT CLASSIC RIDER BIO190 IC",
        "item_type": "T-Shirt Classic",
        "price": "29,90 €",
        "duration": 8.0,
        "link_text": "COMPRAR T-SHIRT CLASSIC",
        "slides": [
            {
                "image": "assets/images/apparel/tshirt_preto_front.jpg",
                "tag": "100% ALGODÃO ORGÂNICO",
                "title_line1": "T-SHIRT CLASSIC",
                "title_line2": "BIO190 STREET",
                "sub": "29,90 € • TOQUE ULTRA SUAVE E RESISTENTE",
                "badge_type": "skull",
                "show_shipping": False
            },
            {
                "image": "assets/images/apparel/tshirt_classic_preto.jpg",
                "tag": "MEGA ESTAMPA A3 COSTAS",
                "title_line1": "ESTAMPA COSTAS A3",
                "title_line2": "GHOSTRIDER ORIGINAL",
                "sub": "CORTE REGULAR CLÁSSICO • CONFORTO TOTAL NA MOTO",
                "badge_type": "profile",
                "show_shipping": False
            },
            {
                "image": "assets/images/apparel/tshirt_classic_amarelo.jpg",
                "tag": "ENVIO RÁPIDO PORTUGAL",
                "title_line1": "DISPONÍVEL NO SITE",
                "title_line2": "PRETO & AMARELO",
                "sub": "ESSENCIAL PARA O TEU DIA A DIA BIKER",
                "badge_type": "skull",
                "show_shipping": True
            }
        ]
    },
    {
        "id": "story_apparel_04_hoodie_lentos",
        "product_id": "hoodie-veiculos-lentos-dark-ghostrider",
        "title": "SWEAT CAPUZ • VEÍCULOS LENTOS À DIREITA",
        "item_type": "Sweatshirt / Hoodie",
        "price": "59,90 €",
        "duration": 8.0,
        "link_text": "COMPRAR SWEAT LENTOS",
        "slides": [
            {
                "image": "assets/images/apparel/hoodie_lentos_preto_front.jpg",
                "tag": "EDIÇÃO BIKER HUMOR",
                "title_line1": "SWEAT COM CAPUZ",
                "title_line2": "VEÍCULOS LENTOS",
                "sub": "59,90 € • FRENTE MINIMALISTA COM LOGO PEITO",
                "badge_type": "skull",
                "show_shipping": False
            },
            {
                "image": "assets/images/apparel/hoodie_lentos_preto_back.jpg",
                "tag": "MENSAGEM NAS COSTAS",
                "title_line1": "VEÍCULOS LENTOS",
                "title_line2": "À DIREITA",
                "sub": "380G HEAVYWEIGHT • ULTRAPASSAGEM COM ESTILO",
                "badge_type": "profile",
                "show_shipping": False
            },
            {
                "image": "assets/images/apparel/hoodie_lentos_amarelo_back.jpg",
                "tag": "ENVIO RÁPIDO PORTUGAL",
                "title_line1": "PRETO OU AMARELO",
                "title_line2": "CLICA NO LINK",
                "sub": "A REGRA DA ESTRADA COM MÁXIMA ATITUDE",
                "badge_type": "skull",
                "show_shipping": True
            }
        ]
    },
    {
        "id": "story_apparel_05_tshirt_lentos",
        "product_id": "tshirt-veiculos-lentos-dark-ghostrider",
        "title": "T-SHIRT OVERSIZED • VEÍCULOS LENTOS À DIREITA",
        "item_type": "T-Shirt Oversized",
        "price": "39,90 €",
        "duration": 8.0,
        "link_text": "COMPRAR T-SHIRT LENTOS",
        "slides": [
            {
                "image": "assets/images/apparel/tshirt_lentos_preto_front.jpg",
                "tag": "BIKER HUMOR • BOX FIT",
                "title_line1": "T-SHIRT OVERSIZED",
                "title_line2": "VEÍCULOS LENTOS",
                "sub": "39,90 € • CORTE RETRO BOXY FIT EM ALGODÃO PESADO",
                "badge_type": "skull",
                "show_shipping": False
            },
            {
                "image": "assets/images/apparel/tshirt_lentos_preto_back.jpg",
                "tag": "ESTAMPA COSTAS A3",
                "title_line1": "VEÍCULOS LENTOS",
                "title_line2": "À DIREITA",
                "sub": "ALTA DENSIDADE DTF • IMPOSSÍVEL NÃO REPARAREM",
                "badge_type": "profile",
                "show_shipping": False
            },
            {
                "image": "assets/images/apparel/tshirt_lentos_amarelo_back.jpg",
                "tag": "ENVIO RÁPIDO PORTUGAL",
                "title_line1": "PRETO & AMARELO FLUO",
                "title_line2": "GARANTE A TUA",
                "sub": "EDIÇÃO ESPECIAL LIMITADA NO SITE",
                "badge_type": "skull",
                "show_shipping": True
            }
        ]
    },
    {
        "id": "story_apparel_06_hoodie_faixa_esquerda",
        "product_id": "hoodie-faixa-esquerda-dark-ghostrider",
        "title": "SWEAT CAPUZ • A FAIXA DA ESQUERDA NÃO É TUA",
        "item_type": "Sweatshirt / Hoodie",
        "price": "59,90 €",
        "duration": 8.0,
        "link_text": "COMPRAR SWEAT FAIXA ESQ.",
        "slides": [
            {
                "image": "assets/images/apparel/hoodie_faixa_preto_front.jpg",
                "tag": "EDIÇÃO BIKER HUMOR",
                "title_line1": "SWEAT COM CAPUZ",
                "title_line2": "FAIXA DA ESQUERDA",
                "sub": "59,90 € • FRENTE CLEAN E DISCRETA NO PEITO",
                "badge_type": "skull",
                "show_shipping": False
            },
            {
                "image": "assets/images/apparel/hoodie_faixa_preto_back.jpg",
                "tag": "MENSAGEM NAS COSTAS",
                "title_line1": "A FAIXA DA ESQUERDA",
                "title_line2": "NÃO É TUA!",
                "sub": "380G HEAVYWEIGHT • CORTE BIKER CONFORTÁVEL",
                "badge_type": "profile",
                "show_shipping": False
            },
            {
                "image": "assets/images/apparel/hoodie_faixa_amarelo_back.jpg",
                "tag": "ENVIO RÁPIDO PORTUGAL",
                "title_line1": "PEDE JÁ A TUA",
                "title_line2": "STOCK LIMITADO",
                "sub": "DISPONÍVEL NAS DUAS CORES OFICIAIS",
                "badge_type": "skull",
                "show_shipping": True
            }
        ]
    },
    {
        "id": "story_apparel_07_tshirt_faixa_esquerda",
        "product_id": "tshirt-faixa-esquerda-dark-ghostrider",
        "title": "T-SHIRT OVERSIZED • A FAIXA DA ESQUERDA NÃO É TUA",
        "item_type": "T-Shirt Oversized",
        "price": "39,90 €",
        "duration": 8.0,
        "link_text": "COMPRAR T-SHIRT FAIXA ESQ.",
        "slides": [
            {
                "image": "assets/images/apparel/tshirt_faixa_preto_front.jpg",
                "tag": "BIKER HUMOR • BOX FIT",
                "title_line1": "T-SHIRT OVERSIZED",
                "title_line2": "FAIXA DA ESQUERDA",
                "sub": "39,90 € • ALGODÃO ENCORPADO DE ALTA QUALIDADE",
                "badge_type": "skull",
                "show_shipping": False
            },
            {
                "image": "assets/images/apparel/tshirt_faixa_preto_back.jpg",
                "tag": "ESTAMPA COSTAS A3",
                "title_line1": "A FAIXA DA ESQUERDA",
                "title_line2": "NÃO É TUA!",
                "sub": "MÁXIMA ATITUDE E PERSONALIDADE NA ESTRADA",
                "badge_type": "profile",
                "show_shipping": False
            },
            {
                "image": "assets/images/apparel/tshirt_faixa_amarelo_back.jpg",
                "tag": "ENVIO RÁPIDO PORTUGAL",
                "title_line1": "PRETO OU AMARELO",
                "title_line2": "CLICA NO LINK",
                "sub": "ENVIO SEGURO COM TRACKING CTT",
                "badge_type": "skull",
                "show_shipping": True
            }
        ]
    },
    {
        "id": "story_apparel_08_hoodie_lentos_porfavor",
        "product_id": "hoodie-veiculos-lentos-porfavor-dark-ghostrider",
        "title": "SWEAT CAPUZ • VEÍCULOS LENTOS À DIREITA, POR FAVOR",
        "item_type": "Sweatshirt / Hoodie",
        "price": "59,90 €",
        "duration": 8.0,
        "link_text": "COMPRAR SWEAT POR FAVOR",
        "slides": [
            {
                "image": "assets/images/apparel/hoodie_porfavor_preto_front.jpg",
                "tag": "BIKER HUMOR POLITE",
                "title_line1": "SWEAT COM CAPUZ",
                "title_line2": "POR FAVOR, À DIREITA",
                "sub": "59,90 € • EDUCAÇÃO E VELOCIDADE JUNTAS",
                "badge_type": "skull",
                "show_shipping": False
            },
            {
                "image": "assets/images/apparel/hoodie_porfavor_preto_back.jpg",
                "tag": "MENSAGEM NAS COSTAS",
                "title_line1": "VEÍCULOS LENTOS",
                "title_line2": "À DIREITA, POR FAVOR",
                "sub": "380G HEAVYWEIGHT • INTERIOR TÉRMICO FLANELADO",
                "badge_type": "profile",
                "show_shipping": False
            },
            {
                "image": "assets/images/apparel/hoodie_porfavor_amarelo_back.jpg",
                "tag": "ENVIO RÁPIDO PORTUGAL",
                "title_line1": "PRETO & AMARELO FLUO",
                "title_line2": "GARANTE JÁ",
                "sub": "A MENSAGEM PERFEITA COM CORDIALIDADE",
                "badge_type": "skull",
                "show_shipping": True
            }
        ]
    },
    {
        "id": "story_apparel_09_tshirt_lentos_porfavor",
        "product_id": "tshirt-veiculos-lentos-porfavor-dark-ghostrider",
        "title": "T-SHIRT OVERSIZED • VEÍCULOS LENTOS À DIREITA, POR FAVOR",
        "item_type": "T-Shirt Oversized",
        "price": "39,90 €",
        "duration": 8.0,
        "link_text": "COMPRAR T-SHIRT POR FAVOR",
        "slides": [
            {
                "image": "assets/images/apparel/tshirt_porfavor_preto_front.jpg",
                "tag": "BIKER HUMOR POLITE",
                "title_line1": "T-SHIRT OVERSIZED",
                "title_line2": "POR FAVOR, À DIREITA",
                "sub": "39,90 € • CORTE BOXY FIT DESCONTRAÍDO E MODERNO",
                "badge_type": "skull",
                "show_shipping": False
            },
            {
                "image": "assets/images/apparel/tshirt_porfavor_preto_back.jpg",
                "tag": "ESTAMPA COSTAS A3",
                "title_line1": "VEÍCULOS LENTOS",
                "title_line2": "À DIREITA, POR FAVOR",
                "sub": "ESTAMPAGEM A3 DE ALTA DEFINIÇÃO RESISTENTE A LAVAGENS",
                "badge_type": "profile",
                "show_shipping": False
            },
            {
                "image": "assets/images/apparel/tshirt_porfavor_amarelo_back.jpg",
                "tag": "ENVIO RÁPIDO PORTUGAL",
                "title_line1": "COMPRA ONLINE",
                "title_line2": "PRETO OU AMARELO",
                "sub": "ENVIO PARA PORTUGAL CONTINENTAL",
                "badge_type": "skull",
                "show_shipping": True
            }
        ]
    }
]

# -------------------------------------------------------------
# RENDER STORY VIDEO FUNCTION
# -------------------------------------------------------------
def render_apparel_story(cfg, story_idx):
    story_id = cfg["id"]
    duration = cfg["duration"]
    total_frames = int(duration * FPS)
    slides = cfg["slides"]
    num_slides = len(slides)
    slide_dur = duration / num_slides
    
    out_video_path = os.path.join(STORIES_DIR, f"{story_id}.mp4")
    out_poster_path = os.path.join(POSTERS_DIR, f"{story_id}_poster.jpg")
    temp_wav = os.path.join(STORIES_DIR, f"temp_{story_id}.wav")
    
    print(f"\n[{story_idx+1}/9] Rendering {story_id} ({duration}s, {total_frames} frames)...")
    t0 = time.time()
    
    generate_story_audio(duration, variant_idx=story_idx, out_wav_path=temp_wav)
    
    cmd = [
        FFMPEG_EXE,
        "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{WIDTH}x{HEIGHT}",
        "-pix_fmt", "rgb24",
        "-r", str(FPS),
        "-i", "-",
        "-i", temp_wav,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "faster",
        "-crf", "20",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        "-movflags", "+faststart",
        out_video_path
    ]
    
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    poster_saved = False
    
    for frame_idx in range(total_frames):
        t = frame_idx / float(FPS)
        slide_idx = min(int(t / slide_dur), num_slides - 1)
        cur_slide = slides[slide_idx]
        slide_t = t - (slide_idx * slide_dur)
        slide_prog = min(1.0, max(0.0, slide_t / slide_dur))
        
        # Deep dark cyber biker background
        canvas = Image.new("RGBA", (WIDTH, HEIGHT), (10, 11, 16, 255))
        src_img = get_cached_image(cur_slide["image"])
        
        # Subtle Ken Burns smooth zoom (2% max to keep product framing pristine)
        zoom = 1.0 + 0.02 * slide_prog
        card_w, card_h = 580, 580
        cx = WIDTH // 2
        cy = 465
        
        target_w = int(card_w * zoom)
        target_h = int(card_h * zoom)
        thumb = ImageOps.fit(src_img, (target_w, target_h), Image.Resampling.LANCZOS)
        left_c = (target_w - card_w) // 2
        top_c = (target_h - card_h) // 2
        thumb_cropped = thumb.crop((left_c, top_c, left_c + card_w, top_c + card_h))
        
        card_mask = Image.new("L", (card_w, card_h), 0)
        ImageDraw.Draw(card_mask).rounded_rectangle([0, 0, card_w, card_h], radius=24, fill=255)
        
        # Shadow
        shadow_box = Image.new("RGBA", (card_w + 40, card_h + 40), (0, 0, 0, 0))
        ImageDraw.Draw(shadow_box).rounded_rectangle([15, 15, card_w + 25, card_h + 25], radius=28, fill=(0, 0, 0, 160))
        canvas.alpha_composite(shadow_box, (cx - card_w // 2 - 20, cy - card_h // 2 - 20))
        
        # Product Card
        card_composite = Image.new("RGBA", (card_w, card_h), (18, 20, 28, 255))
        card_composite.paste(thumb_cropped, (0, 0), card_mask)
        outline_color = (246, 255, 0, 130) if slide_idx % 2 == 0 else (255, 255, 255, 80)
        ImageDraw.Draw(card_composite).rounded_rectangle([0, 0, card_w - 1, card_h - 1], radius=24, outline=outline_color, width=2)
        canvas.alpha_composite(card_composite, (cx - card_w // 2, cy - card_h // 2))
        
        draw = ImageDraw.Draw(canvas)
        
        # Top Tag Pill
        tag_text = cur_slide["tag"]
        t_box = draw.textbbox((0, 0), tag_text, font=FONT_BADGE)
        tw = t_box[2] - t_box[0] + 32
        tx = cx - tw // 2
        ty = 135
        draw.rounded_rectangle([tx, ty, tx + tw, ty + 38], radius=19, fill=(246, 255, 0, 255))
        draw.text((tx + 16, ty + 6), tag_text, fill=(10, 10, 10, 255), font=FONT_BADGE)
        
        # Headline Texts
        l1 = cur_slide["title_line1"]
        l2 = cur_slide["title_line2"]
        sub_text = cur_slide["sub"]
        
        b1 = draw.textbbox((0, 0), l1, font=FONT_TITLE)
        b2 = draw.textbbox((0, 0), l2, font=FONT_TITLE)
        w1 = b1[2] - b1[0]
        w2 = b2[2] - b2[0]
        
        y_text = 795
        # Shadow + text line 1
        draw.text((cx - w1 // 2 + 2, y_text + 2), l1, fill=(0, 0, 0, 230), font=FONT_TITLE)
        draw.text((cx - w1 // 2, y_text), l1, fill=(255, 255, 255, 255), font=FONT_TITLE)
        
        # Shadow + text line 2 (in neon yellow)
        draw.text((cx - w2 // 2 + 2, y_text + 54), l2, fill=(0, 0, 0, 230), font=FONT_TITLE)
        draw.text((cx - w2 // 2, y_text + 52), l2, fill=(246, 255, 0, 255), font=FONT_TITLE)
        
        # Subtitle
        bsub = draw.textbbox((0, 0), sub_text, font=FONT_BODY)
        wsub = bsub[2] - bsub[0]
        draw.text((cx - wsub // 2, y_text + 112), sub_text, fill=(210, 215, 230, 240), font=FONT_BODY)
        
        # Shipping Notice on Slide 3 or when enabled
        if cur_slide.get("show_shipping", False):
            ship_text = "Envio 4,85 € Portugal Continental • 4 a 6 dias úteis"
            b_ship = draw.textbbox((0, 0), ship_text, font=FONT_SHIPPING)
            w_ship = b_ship[2] - b_ship[0] + 28
            h_ship = 32
            x_ship = cx - w_ship // 2
            y_ship = 948
            draw.rounded_rectangle([x_ship, y_ship, x_ship + w_ship, y_ship + h_ship], radius=16, fill=(20, 25, 38, 220), outline=(246, 255, 0, 100), width=1)
            draw.text((x_ship + 14, y_ship + 6), ship_text, fill=(246, 255, 0, 255), font=FONT_SHIPPING)
        else:
            # Price Tag pill in earlier slides
            price_text = f"PREÇO OFICIAL: {cfg['price']}"
            b_p = draw.textbbox((0, 0), price_text, font=FONT_SHIPPING)
            w_p = b_p[2] - b_p[0] + 24
            x_p = cx - w_p // 2
            y_p = 948
            draw.rounded_rectangle([x_p, y_p, x_p + w_p, y_p + 32], radius=16, fill=(25, 27, 36, 210), outline=(255, 255, 255, 60), width=1)
            draw.text((x_p + 12, y_p + 6), price_text, fill=(255, 255, 255, 240), font=FONT_SHIPPING)
        
        # Center pulsating badge (only when badge_type is not "none")
        badge_type = cur_slide.get("badge_type", "skull")
        if badge_type and badge_type != "none":
            badge_scale = 1.0 + 0.05 * math.sin(t * 5.0)
            badge_img = LOGO_BADGE_PROFILE if badge_type == "profile" else LOGO_BADGE_SKULL
            bw = int(140 * badge_scale)
            bh = int(140 * badge_scale)
            badge_resized = badge_img.resize((bw, bh), Image.Resampling.BILINEAR)
            canvas.alpha_composite(badge_resized, (cx - bw // 2, 730 - bh // 2))
        
        # Link Sticker
        link_bounce = 1.0 + 0.03 * math.sin(t * 4.0)
        draw_story_link_sticker(canvas, cfg["link_text"], cx, 1040, scale=link_bounce)
        
        # Stories Header
        draw_story_header(draw, slide_prog, slide_idx, num_slides)
        
        av_small = AVATAR_IMG.resize((40, 40), Image.Resampling.BILINEAR)
        av_mask = Image.new("L", (40, 40), 0)
        ImageDraw.Draw(av_mask).ellipse([0, 0, 40, 40], fill=255)
        canvas.paste(av_small, (20, 42), av_mask)
        
        # Stories Footer
        draw_story_footer(draw)
        
        rgb = canvas.convert("RGB")
        
        # Save poster on frame of second slide (A3 back print)
        if not poster_saved and frame_idx == int(3.5 * FPS):
            rgb.save(out_poster_path, quality=94)
            poster_saved = True
            
        proc.stdin.write(rgb.tobytes())
        
    proc.stdin.close()
    proc.wait()
    
    if os.path.exists(temp_wav):
        try: os.remove(temp_wav)
        except: pass
        
    if not poster_saved and os.path.exists(out_video_path):
        rgb.save(out_poster_path, quality=94)
        
    elapsed = time.time() - t0
    size_mb = os.path.getsize(out_video_path) / (1024 * 1024)
    print(f"-> Done {story_id}.mp4: {size_mb:.2f} MB in {elapsed:.1f}s")
    return out_video_path

def main():
    target_id = sys.argv[1] if len(sys.argv) > 1 else None
    print("================================================================")
    print("BATCH RENDERING APPAREL INSTAGRAM STORIES VIDEOS (9:16)")
    if target_id:
        print(f"Targeting single story: {target_id}")
    else:
        print("Dedicated video for each T-shirt and Sweatshirt on the site")
    print("================================================================")
    total_t0 = time.time()
    
    count = 0
    for idx, cfg in enumerate(APPAREL_STORIES):
        if target_id and cfg["id"] != target_id and cfg["product_id"] != target_id:
            continue
        render_apparel_story(cfg, idx)
        count += 1
        
    print("\n================================================================")
    print(f"COMPLETED {count} APPAREL VIDEO(S) IN {time.time() - total_t0:.1f}s!")
    print(f"Videos saved to: {STORIES_DIR}")
    print(f"Posters saved to: {POSTERS_DIR}")
    print("================================================================")

if __name__ == "__main__":
    main()
