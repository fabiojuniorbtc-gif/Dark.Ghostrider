# -*- coding: utf-8 -*-
"""
Production Batch Generator for 10 Instagram Stories / Reels Videos (9:16 - 720x1280)
Tailored for Dark Ghostrider Store Instagram Stories promotion.
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

FONT_TITLE = get_font("impact.ttf", 52)
FONT_SUB = get_font("arialbd.ttf", 26)
FONT_BODY = get_font("arialbd.ttf", 22)
FONT_SMALL = get_font("arialbd.ttf", 16)
FONT_BADGE = get_font("impact.ttf", 22)

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
    w = int(340 * scale)
    h = int(58 * scale)
    bx = int(center_x - w / 2)
    by = int(center_y - h / 2)
    
    sticker = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(sticker)
    
    # Yellow neon halo
    for offset, alpha in [(8, 40), (4, 90), (2, 150)]:
        sdraw.rounded_rectangle([20 - offset, 20 - offset, 20 + w + offset, 20 + h + offset], radius=int(26 * scale), fill=(246, 255, 0, alpha))
        
    # White background
    sdraw.rounded_rectangle([20, 20, 20 + w, 20 + h], radius=int(26 * scale), fill=(255, 255, 255, 255))
    
    chain_x = 20 + int(24 * scale)
    chain_y = 20 + int(h / 2)
    draw_vector_link_chain(sdraw, chain_x, chain_y, size=int(18 * scale))
    
    font_s = get_font("arialbd.ttf", int(19 * scale))
    sdraw.text((chain_x + int(24 * scale), 20 + int(17 * scale)), text, fill=(12, 14, 18, 255), font=font_s)
    
    arrow_x = 20 + w - int(24 * scale)
    arrow_y = chain_y
    draw_vector_arrow(sdraw, arrow_x, arrow_y, size=int(16 * scale))
    
    canvas.alpha_composite(sticker, (bx - 20, by - 20))

def create_circular_logo_badge(img, size=140, border_color=(246, 255, 0, 255)):
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
# AUDIO SYNTHESIZER
# -------------------------------------------------------------
def generate_story_audio(duration, variant_idx=0, out_wav_path="temp_audio.wav"):
    sr = 44100
    total_samples = int(sr * duration)
    bpm = 128.0 + (variant_idx % 4) * 2.0
    spb = 60.0 / bpm
    
    left = np.zeros(total_samples, dtype=np.float32)
    right = np.zeros(total_samples, dtype=np.float32)
    
    kick_len = int(0.32 * sr)
    t_k = np.arange(kick_len) / sr
    f_k = 48 + 130 * np.exp(-t_k * 32)
    phase_k = np.cumsum(f_k * 2 * np.pi / sr)
    env_k = np.exp(-t_k * 8.5)
    click = np.sin(2 * np.pi * 1800 * t_k) * np.exp(-t_k * 140) * 0.4
    kick = np.tanh((np.sin(phase_k) * env_k + click) * 1.6) * 0.95
    
    snare_len = int(0.26 * sr)
    t_s = np.arange(snare_len) / sr
    noise = np.random.uniform(-1, 1, snare_len)
    body = np.sin(2 * np.pi * 215 * t_s) * np.exp(-t_s * 25) * 0.5
    snare = (noise * np.exp(-t_s * 15) * 0.65 + body) * 0.75
    
    hat_len = int(0.07 * sr)
    t_h = np.arange(hat_len) / sr
    hat = np.random.uniform(-1, 1, hat_len) * np.exp(-t_h * 55) * 0.28
    
    crash_len = int(2.0 * sr)
    t_c = np.arange(crash_len) / sr
    crash = np.random.uniform(-1, 1, crash_len) * np.exp(-t_c * 2.2) * 0.5
    
    total_beats = int(duration / spb)
    for b in range(total_beats):
        pos = int(b * spb * sr)
        if b % 2 == 0 or (b % 4 == 3 and b > 3):
            en = min(total_samples, pos + kick_len)
            left[pos:en] += kick[:en - pos] * 0.9
            right[pos:en] += kick[:en - pos] * 0.9
        if b % 2 == 1:
            en = min(total_samples, pos + snare_len)
            left[pos:en] += snare[:en - pos] * 0.75
            right[pos:en] += snare[:en - pos] * 0.75
        for h in range(4):
            h_pos = int((b + h * 0.25) * spb * sr)
            if h_pos + hat_len < total_samples:
                vol = 0.85 if h == 0 else 0.5
                left[h_pos:h_pos + hat_len] += hat * vol
                right[h_pos:h_pos + hat_len] += hat * vol * 0.9
                
    bass_roots = [
        [41.2, 41.2, 49.0, 41.2, 55.0, 55.0, 49.0, 41.2],
        [43.7, 43.7, 51.9, 43.7, 58.3, 58.3, 51.9, 43.7],
        [38.9, 38.9, 46.2, 38.9, 51.9, 51.9, 46.2, 38.9],
        [46.2, 46.2, 55.0, 46.2, 61.7, 61.7, 55.0, 46.2],
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
        sub += 0.35 * np.sin(2 * np.pi * freq * 2 * t_n)
        sub = np.tanh(sub * 2.2) * 0.42
        sub *= np.minimum(1.0, t_n * 25.0)
        sub *= np.maximum(0.2, np.exp(-t_n * 0.5))
        left[st:en] += sub
        right[st:en] += sub

    arp_scales = [
        [164.8, 196.0, 246.9, 293.7, 329.6],
        [174.6, 207.7, 261.6, 311.1, 349.2],
        [155.6, 185.0, 233.1, 277.2, 311.1],
        [185.0, 220.0, 277.2, 329.6, 370.0],
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
        lead = saw * np.exp(-t_l * 12) * 0.16
        pan = 0.5 + 0.3 * np.sin(step * 0.75)
        left[st:st + n_len] += lead * (1 - pan)
        right[st:st + n_len] += lead * pan

    crashes = [0.0, duration * 0.33, duration * 0.66]
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
# IMAGE CACHE & PRE-LOADER
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
# CONFIGURATION FOR 10 STORIES VIDEOS
# -------------------------------------------------------------
STORIES_CONFIG = [
    {
        "id": "story_01_colecao_streetwear",
        "title": "DROP 01 • COLEÇÃO COMPLETA",
        "category": "VESTUÁRIO",
        "duration": 12.0,
        "link_text": "DARKGHOSTRIDER.COM",
        "slides": [
            {
                "image": "assets/images/hero-rider-mt07.jpg",
                "tag": "DROP OFICIAL 01",
                "title_line1": "STREETWEAR",
                "title_line2": "DARK RIDER",
                "sub": "COLEÇÃO EXCLUSIVA NO AR",
                "badge_type": "profile",
            },
            {
                "image": "assets/images/apparel/hoodie_preto.jpg",
                "tag": "HOODIE HEAVYWEIGHT",
                "title_line1": "PRETO STEALTH",
                "title_line2": "380G PREMIUM",
                "sub": "ALGODÃO PENTEADO & BORDADO",
                "badge_type": "skull",
            },
            {
                "image": "assets/images/apparel/hoodie_amarelo.jpg",
                "tag": "CYBER YELLOW",
                "title_line1": "HOODIE AMARELO",
                "title_line2": "EDICÃO LIMITADA",
                "sub": "COR EXCLUSIVA DA MARCA",
                "badge_type": "profile",
            },
            {
                "image": "assets/images/apparel/tshirt_classic_preto.jpg",
                "tag": "T-SHIRTS & PACKS",
                "title_line1": "OVERSIZED RAW",
                "title_line2": "LINK NA BIO",
                "sub": "GARANTE ANTES QUE ESGOTE!",
                "badge_type": "skull",
            }
        ]
    },
    {
        "id": "story_02_hoodie_heavyweight",
        "title": "HOODIE HEAVYWEIGHT 380G",
        "category": "HOODIE",
        "duration": 10.0,
        "link_text": "VER HOODIES",
        "slides": [
            {
                "image": "assets/images/apparel/hoodie_preto.jpg",
                "tag": "TOP SELLER",
                "title_line1": "HOODIE DARK",
                "title_line2": "HEAVYWEIGHT",
                "sub": "380G DE PURO CONFORTO",
                "badge_type": "profile",
            },
            {
                "image": "assets/images/apparel/emblema_peito.jpg",
                "tag": "DETALHES BORDADOS",
                "title_line1": "BORDADO FRONTAL",
                "title_line2": "ALTA PRECISÃO",
                "sub": "LOGÓTIPO OFICIAL DARK RIDER",
                "badge_type": "skull",
            },
            {
                "image": "assets/images/apparel/estampa_costas.jpg",
                "tag": "ESTAMPA COSTAS",
                "title_line1": "CAVEIRA NEON",
                "title_line2": "HIGH DEFINITION",
                "sub": "NÃO RACHA NEM DESBOTA",
                "badge_type": "profile",
            },
            {
                "image": "assets/images/apparel/hoodie_amarelo.jpg",
                "tag": "ESCOLHE A TUA COR",
                "title_line1": "PRETO OU AMARELO",
                "title_line2": "CLICA NO LINK",
                "sub": "ENVIO 24/48H VIA CTT EXPRESSO",
                "badge_type": "skull",
            }
        ]
    },
    {
        "id": "story_03_tshirts_oversized",
        "title": "T-SHIRTS STREETWEAR & OVERSIZED",
        "category": "T-SHIRTS",
        "duration": 10.0,
        "link_text": "VER T-SHIRTS",
        "slides": [
            {
                "image": "assets/images/apparel/tshirt_classic_preto.jpg",
                "tag": "100% ALGODÃO PENTEADO",
                "title_line1": "T-SHIRT CLASSIC",
                "title_line2": "PRETO STEALTH",
                "sub": "TOQUE MACIO E RESPIRÁVEL",
                "badge_type": "profile",
            },
            {
                "image": "assets/images/apparel/tshirt_preto_back.jpg",
                "tag": "VISÃO TRASEIRA",
                "title_line1": "ESTAMPA GIGANTE",
                "title_line2": "NAS COSTAS",
                "sub": "ARTE OFICIAL EXCLUSIVA",
                "badge_type": "skull",
            },
            {
                "image": "assets/images/apparel/tshirt_oversized_amarelo.jpg",
                "tag": "CORTE OVERSIZED",
                "title_line1": "CYBER YELLOW",
                "title_line2": "STREETWEAR RAW",
                "sub": "CAIMENTO PERFEITO NO CORPO",
                "badge_type": "profile",
            },
            {
                "image": "assets/images/apparel/mockup_tshirt.jpg",
                "tag": "STOCK LIMITADO",
                "title_line1": "GARANTE A TUA",
                "title_line2": "LINK NA BIO",
                "sub": "ENVIOS PARA PORTUGAL E EUROPA",
                "badge_type": "skull",
            }
        ]
    },
    {
        "id": "story_04_pack_economico",
        "title": "PACK ECONÓMICO HOODIE + T-SHIRT",
        "category": "OFERTA PACK",
        "duration": 11.0,
        "link_text": "GARANTIR O PACK",
        "slides": [
            {
                "image": "assets/images/apparel/hoodie_duo_full.jpg",
                "tag": "COMBO EXCLUSIVO",
                "title_line1": "PACK ECONÓMICO",
                "title_line2": "HOODIE + T-SHIRT",
                "sub": "O CONJUNTO COMPLETO DARK",
                "badge_type": "profile",
            },
            {
                "image": "assets/images/apparel/hoodie_preto.jpg",
                "tag": "DESCONTO DIRETO",
                "title_line1": "POUPA ATÉ 20€",
                "title_line2": "NO CARRINHO",
                "sub": "LEVA AMBAS AS PEÇAS COM DESCONTO",
                "badge_type": "skull",
            },
            {
                "image": "assets/images/apparel/tshirt_classic_preto.jpg",
                "tag": "ESCOLHE AS CORES",
                "title_line1": "COMBINA AO TEU",
                "title_line2": "GOSTO PESSOAL",
                "sub": "PRETO, AMARELO OU MISTO",
                "badge_type": "profile",
            },
            {
                "image": "assets/images/apparel/estampa_costas.jpg",
                "tag": "APROVEITA AGORA",
                "title_line1": "CLICA NO LINK",
                "title_line2": "POUPA JÁ",
                "sub": "PROMOÇÃO POR TEMPO LIMITADO",
                "badge_type": "skull",
            }
        ]
    },
    {
        "id": "story_05_raiox_mt07",
        "title": "RAIO-X MT-07 • SETUP DO DARK",
        "category": "RAIO-X MOTO",
        "duration": 12.0,
        "link_text": "VER SETUP MT-07",
        "slides": [
            {
                "image": "assets/images/hero-rider-mt07.jpg",
                "tag": "O QUE O DARK USA",
                "title_line1": "SETUP MT-07",
                "title_line2": "DO DARK",
                "sub": "TODAS AS PEÇAS REVELADAS",
                "badge_type": "profile",
            },
            {
                "image": "assets/images/products/retrovisores_stealth_main.jpg",
                "tag": "COCKPIT & PERFORMANCE",
                "title_line1": "RETROVISORES",
                "title_line2": "STEALTH WING",
                "sub": "ALUMÍNIO CNC AERODINÂMICO",
                "badge_type": "skull",
            },
            {
                "image": "assets/images/products/escape_r77_main.jpg",
                "tag": "SOM & POTÊNCIA",
                "title_line1": "YOSHIMURA R77",
                "title_line2": "FULL CARBON",
                "sub": "O RONCO BRUTO DA MT-07",
                "badge_type": "profile",
            },
            {
                "image": "assets/images/hero-mt07.jpg",
                "tag": "PÁGINA INTERATIVA",
                "title_line1": "CLICA NO LINK",
                "title_line2": "RAIO-X NO SITE",
                "sub": "TODAS AS PEÇAS COM LINK DIRETO",
                "badge_type": "skull",
            }
        ]
    },
    {
        "id": "story_06_escape_yoshimura_r77",
        "title": "ESCAPE YOSHIMURA R77 FULL CARBON",
        "category": "ESCAPES",
        "duration": 10.0,
        "link_text": "VER ESCAPE R77",
        "slides": [
            {
                "image": "assets/images/products/escape_r77_main.jpg",
                "tag": "FULL SYSTEM",
                "title_line1": "ESCAPE R77",
                "title_line2": "YOSHIMURA",
                "sub": "COLETORES EM INOX + CARBONO",
                "badge_type": "profile",
            },
            {
                "image": "assets/images/products/1005007342817819.jpg",
                "tag": "CARBONO REAL",
                "title_line1": "PONTEIRA FIBRA",
                "title_line2": "DE CARBONO",
                "sub": "LEVE, RESISTENTE E ELEGANTE",
                "badge_type": "skull",
            },
            {
                "image": "assets/images/hero-rider-mt07.jpg",
                "tag": "RONCO INCONFUNDÍVEL",
                "title_line1": "O SOM QUE A",
                "title_line2": "MT-07 MERECE",
                "sub": "TESTADO E APROVADO PELO DARK",
                "badge_type": "profile",
            },
            {
                "image": "assets/images/products/escape_r77_main.jpg",
                "tag": "DISPONÍVEL NO SITE",
                "title_line1": "UPGRADE TOTAL",
                "title_line2": "CLICA NO LINK",
                "sub": "ENVIO DIRETO COM RASTREIO",
                "badge_type": "skull",
            }
        ]
    },
    {
        "id": "story_07_retrovisores_stealth",
        "title": "RETROVISORES STEALTH WING",
        "category": "COCKPIT",
        "duration": 10.0,
        "link_text": "VER ESPELHOS STEALTH",
        "slides": [
            {
                "image": "assets/images/products/retrovisores_stealth_main.jpg",
                "tag": "DESIGN AERODINÂMICO",
                "title_line1": "RETROVISORES",
                "title_line2": "STEALTH WING",
                "sub": "ALUMÍNIO CNC DE ALTA QUALIDADE",
                "badge_type": "profile",
            },
            {
                "image": "assets/images/products/variants/tampa_ouro.jpg",
                "tag": "UPGRADE COCKPIT",
                "title_line1": "TAMPAS FLUIDO",
                "title_line2": "CNC ANODIZADO",
                "sub": "CORES OURO, PRETO E AZUL",
                "badge_type": "skull",
            },
            {
                "image": "assets/images/products/parafusos_vedacao_cnc_main.jpg",
                "tag": "ACABAMENTO IMPECÁVEL",
                "title_line1": "PARAFUSOS CNC",
                "title_line2": "DE VEDAÇÃO",
                "sub": "ELIMINA FUROS ORIGINAIS",
                "badge_type": "profile",
            },
            {
                "image": "assets/images/products/retrovisores_stealth_main.jpg",
                "tag": "TRANSFORMA A MOTO",
                "title_line1": "VISUAL DARK",
                "title_line2": "LINK NA BIO",
                "sub": "COMPATÍVEL COM MT-07 E OUTRAS",
                "badge_type": "skull",
            }
        ]
    },
    {
        "id": "story_08_luvas_kashvelo",
        "title": "LUVAS TÁTICAS KASHVELO",
        "category": "ACESSÓRIOS",
        "duration": 10.0,
        "link_text": "VER LUVAS KASHVELO",
        "slides": [
            {
                "image": "assets/images/products/kashvelo_studio_pair.jpg",
                "tag": "EQUIPAMENTO OFICIAL",
                "title_line1": "LUVAS TÁTICAS",
                "title_line2": "KASHVELO",
                "sub": "AS LUVAS USADAS NOS VÍDEOS",
                "badge_type": "profile",
            },
            {
                "image": "assets/images/products/kashvelo-glove-palm.jpg",
                "tag": "MÁXIMA ADERÊNCIA",
                "title_line1": "PALMA COM GRIP",
                "title_line2": "ANTI-ABRASÃO",
                "sub": "CONTROLO TOTAL DO ACELERADOR",
                "badge_type": "skull",
            },
            {
                "image": "assets/images/products/kashvelo-glove-top.jpg",
                "tag": "PROTEÇÃO DE IMPACTO",
                "title_line1": "NÓS DOS DEDOS",
                "title_line2": "REFORÇADOS",
                "sub": "RESPIRÁVEL E RESISTENTE",
                "badge_type": "profile",
            },
            {
                "image": "assets/images/products/kashvelo_real_enhanced.jpg",
                "tag": "PEDE O TEU TAMANHO",
                "title_line1": "S, M, L, XL",
                "title_line2": "CLICA NO LINK",
                "sub": "GARANTE JÁ AS TUAS LUVAS",
                "badge_type": "skull",
            }
        ]
    },
    {
        "id": "story_09_sliders_protecao",
        "title": "PROTEÇÃO TOTAL: SLIDERS & KOMINE",
        "category": "PROTEÇÃO",
        "duration": 11.0,
        "link_text": "VER PROTEÇÃO",
        "slides": [
            {
                "image": "assets/images/products/sliders_coolpad_main.jpg",
                "tag": "SEGURANÇA NA ESTRADA",
                "title_line1": "SLIDERS MOTOR",
                "title_line2": "COOLPAD CNC",
                "sub": "PROTEGE O MOTOR E O CHASSI",
                "badge_type": "profile",
            },
            {
                "image": "assets/images/products/komine_slider_main_1.jpg",
                "tag": "PISTA E CURVAS",
                "title_line1": "KOMINE KNEE",
                "title_line2": "SLIDERS",
                "sub": "ALTA DENSIDADE DE RASPAGEM",
                "badge_type": "skull",
            },
            {
                "image": "assets/images/products/adesivo_tracao_main_1.jpg",
                "tag": "CONTROLO NAS PERNAS",
                "title_line1": "PADS DE TRAÇÃO",
                "title_line2": "NO TANQUE",
                "sub": "CONFORTO E GRIP EM CURVAS",
                "badge_type": "profile",
            },
            {
                "image": "assets/images/products/lanterna_led_fume_main.jpg",
                "tag": "SETUP DE RESPEITO",
                "title_line1": "EQUIPA A TUA",
                "title_line2": "MÁQUINA HOJE",
                "sub": "LINK NA BIO // CTT EXPRESSO",
                "badge_type": "skull",
            }
        ]
    },
    {
        "id": "story_10_store_launch_bio",
        "title": "LOJA OFICIAL DARK • LINK NA BIO",
        "category": "OFICIAL",
        "duration": 12.0,
        "link_text": "DARKGHOSTRIDER.COM",
        "slides": [
            {
                "image": "assets/images/hero-rider-mt07.jpg",
                "tag": "LOJA OFICIAL NO AR",
                "title_line1": "DARK GHOSTRIDER",
                "title_line2": "STORE ONLINE",
                "sub": "O UNIVERSO DARK NA PALMA DA MÃO",
                "badge_type": "profile",
            },
            {
                "image": "assets/images/apparel/hoodie_preto.jpg",
                "tag": "STREETWEAR EXCLUSIVO",
                "title_line1": "DROP 01 VESTUÁRIO",
                "title_line2": "HOODIES & TSHIRTS",
                "sub": "QUALIDADE HEAVYWEIGHT DE TOPO",
                "badge_type": "skull",
            },
            {
                "image": "assets/images/products/retrovisores_stealth_main.jpg",
                "tag": "PEÇAS E RAIO-X MT-07",
                "title_line1": "TUDO O QUE O",
                "title_line2": "DARK USA",
                "sub": "MB WAY • CARTÃO • CTT EXPRESSO",
                "badge_type": "profile",
            },
            {
                "image": "assets/images/apparel/estampa_costas.jpg",
                "tag": "TOCA NO LINK DA BIO",
                "title_line1": "ENTRA JÁ",
                "title_line2": "DARK STORE",
                "sub": "WWW.DARKGHOSTRIDER.COM",
                "badge_type": "skull",
            }
        ]
    }
]

# -------------------------------------------------------------
# RENDER STORY VIDEO FUNCTION
# -------------------------------------------------------------
def render_single_story(cfg, story_idx):
    story_id = cfg["id"]
    duration = cfg["duration"]
    total_frames = int(duration * FPS)
    slides = cfg["slides"]
    num_slides = len(slides)
    slide_dur = duration / num_slides
    
    out_video_path = os.path.join(STORIES_DIR, f"{story_id}.mp4")
    out_poster_path = os.path.join(POSTERS_DIR, f"{story_id}_poster.jpg")
    temp_wav = os.path.join(STORIES_DIR, f"temp_{story_id}.wav")
    
    print(f"\n[{story_idx+1}/10] Rendering {story_id} ({duration}s, {total_frames} frames)...")
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
        
        canvas = Image.new("RGBA", (WIDTH, HEIGHT), (10, 11, 16, 255))
        src_img = get_cached_image(cur_slide["image"])
        
        # Ken Burns zoom on product image
        zoom = 1.0 + 0.12 * slide_prog
        card_w, card_h = 580, 580
        cx = WIDTH // 2
        cy = 470
        
        target_w = int(card_w * zoom)
        target_h = int(card_h * zoom)
        thumb = src_img.resize((target_w, target_h), Image.Resampling.BILINEAR)
        left_c = (target_w - card_w) // 2
        top_c = (target_h - card_h) // 2
        thumb_cropped = thumb.crop((left_c, top_c, left_c + card_w, top_c + card_h))
        
        card_mask = Image.new("L", (card_w, card_h), 0)
        ImageDraw.Draw(card_mask).rounded_rectangle([0, 0, card_w, card_h], radius=24, fill=255)
        
        # Shadow
        shadow_box = Image.new("RGBA", (card_w + 40, card_h + 40), (0, 0, 0, 0))
        ImageDraw.Draw(shadow_box).rounded_rectangle([15, 15, card_w + 25, card_h + 25], radius=28, fill=(0, 0, 0, 160))
        canvas.alpha_composite(shadow_box, (cx - card_w // 2 - 20, cy - card_h // 2 - 20))
        
        card_composite = Image.new("RGBA", (card_w, card_h), (18, 20, 28, 255))
        card_composite.paste(thumb_cropped, (0, 0), card_mask)
        ImageDraw.Draw(card_composite).rounded_rectangle([0, 0, card_w - 1, card_h - 1], radius=24, outline=(246, 255, 0, 90) if slide_idx % 2 == 0 else (255, 255, 255, 60), width=2)
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
        
        y_text = 800
        draw.text((cx - w1 // 2 + 2, y_text + 2), l1, fill=(0, 0, 0, 220), font=FONT_TITLE)
        draw.text((cx - w1 // 2, y_text), l1, fill=(255, 255, 255, 255), font=FONT_TITLE)
        
        draw.text((cx - w2 // 2 + 2, y_text + 56), l2, fill=(0, 0, 0, 220), font=FONT_TITLE)
        draw.text((cx - w2 // 2, y_text + 54), l2, fill=(246, 255, 0, 255), font=FONT_TITLE)
        
        bsub = draw.textbbox((0, 0), sub_text, font=FONT_BODY)
        wsub = bsub[2] - bsub[0]
        draw.text((cx - wsub // 2, y_text + 115), sub_text, fill=(200, 205, 220, 240), font=FONT_BODY)
        
        # CENTER LOGO STICKER: Right in the middle at the bottom edge of the photo card
        badge_type = cur_slide["badge_type"]
        badge_scale = 1.0 + 0.05 * math.sin(t * 5.0)
        badge_img = LOGO_BADGE_PROFILE if badge_type == "profile" else LOGO_BADGE_SKULL
        bw = int(140 * badge_scale)
        bh = int(140 * badge_scale)
        badge_resized = badge_img.resize((bw, bh), Image.Resampling.BILINEAR)
        
        # Position centered at (cx, 730)
        canvas.alpha_composite(badge_resized, (cx - bw // 2, 730 - bh // 2))
        
        # Link Sticker
        link_bounce = 1.0 + 0.03 * math.sin(t * 4.0)
        draw_story_link_sticker(canvas, cfg["link_text"], cx, 1030, scale=link_bounce)
        
        # Stories Header
        draw_story_header(draw, slide_prog, slide_idx, num_slides)
        
        av_small = AVATAR_IMG.resize((40, 40), Image.Resampling.BILINEAR)
        av_mask = Image.new("L", (40, 40), 0)
        ImageDraw.Draw(av_mask).ellipse([0, 0, 40, 40], fill=255)
        canvas.paste(av_small, (20, 42), av_mask)
        
        # Stories Footer
        draw_story_footer(draw)
        
        rgb = canvas.convert("RGB")
        
        if not poster_saved and frame_idx == int(2.5 * FPS):
            rgb.save(out_poster_path, quality=92)
            poster_saved = True
            
        proc.stdin.write(rgb.tobytes())
        
    proc.stdin.close()
    proc.wait()
    
    if os.path.exists(temp_wav):
        try: os.remove(temp_wav)
        except: pass
        
    if not poster_saved and os.path.exists(out_video_path):
        rgb.save(out_poster_path, quality=92)
        
    elapsed = time.time() - t0
    size_mb = os.path.getsize(out_video_path) / (1024 * 1024)
    print(f"-> Done {story_id}.mp4: {size_mb:.2f} MB in {elapsed:.1f}s")
    return out_video_path

def main():
    print("==================================================")
    print("BATCH RENDERING 10 INSTAGRAM STORIES VIDEOS (9:16)")
    print("==================================================")
    total_t0 = time.time()
    
    for idx, cfg in enumerate(STORIES_CONFIG):
        render_single_story(cfg, idx)
        
    print("\n==================================================")
    print(f"ALL 10 VIDEOS RENDERED IN {time.time() - total_t0:.1f}s!")
    print(f"Output folder: {STORIES_DIR}")
    print("==================================================")

if __name__ == "__main__":
    main()
