# -*- coding: utf-8 -*-
import os, sys, math, time, subprocess, wave, shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
import imageio
import imageio_ffmpeg

print("=== BUILDING DARK GHOSTRIDER REELS VIDEO (9:16) ===")

WIDTH = 720
HEIGHT = 1280
FPS = 30
DURATION = 22.0
TOTAL_FRAMES = int(DURATION * FPS) # 660

OUT_DIR = os.path.abspath("assets/videos")
OUT_VIDEO = os.path.join(OUT_DIR, "reels_dark_ghostrider_store.mp4")
OUT_AUDIO = os.path.join(OUT_DIR, "reels_audio.wav")
ALT_DIR = os.path.abspath("assets/video")
ALT_VIDEO = os.path.join(ALT_DIR, "reels_dark_ghostrider_store.mp4")
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(ALT_DIR, exist_ok=True)

# -------------------------------------------------------------
# 1. AUDIO SYNTHESIS
# -------------------------------------------------------------
def make_audio():
    sr = 44100
    duration = DURATION
    total_samples = int(sr * duration)
    bpm = 128.0
    spb = 60.0 / bpm
    
    left = np.zeros(total_samples, dtype=np.float32)
    right = np.zeros(total_samples, dtype=np.float32)
    
    # 808 Kick
    kick_len = int(0.35 * sr)
    t_k = np.arange(kick_len) / sr
    f_k = 48 + 120 * np.exp(-t_k * 30)
    phase_k = np.cumsum(f_k * 2 * np.pi / sr)
    env_k = np.exp(-t_k * 8.5)
    click = np.sin(2 * np.pi * 1700 * t_k) * np.exp(-t_k * 140) * 0.45
    kick = np.tanh((np.sin(phase_k) * env_k + click) * 1.6) * 0.95
    
    # Snare
    snare_len = int(0.28 * sr)
    t_s = np.arange(snare_len) / sr
    noise = np.random.uniform(-1, 1, snare_len)
    body = np.sin(2 * np.pi * 210 * t_s) * np.exp(-t_s * 25) * 0.5
    snare = (noise * np.exp(-t_s * 15) * 0.65 + body) * 0.75
    
    # Hi-hat
    hat_len = int(0.08 * sr)
    t_h = np.arange(hat_len) / sr
    hat = np.random.uniform(-1, 1, hat_len) * np.exp(-t_h * 55) * 0.28
    
    # Crash
    crash_len = int(2.5 * sr)
    t_c = np.arange(crash_len) / sr
    crash = np.random.uniform(-1, 1, crash_len) * np.exp(-t_c * 2.2) * 0.55
    
    # Place drums
    total_beats = int(duration / spb)
    for b in range(total_beats):
        pos = int(b * spb * sr)
        if b % 2 == 0 or (b % 4 == 3 and b > 4):
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
                
    # Bass (E minor)
    bass_notes = [41.2, 41.2, 49.0, 41.2, 55.0, 55.0, 49.0, 41.2, 65.4, 61.7, 55.0, 41.2]
    note_dur = spb * 2
    for i, freq in enumerate(bass_notes):
        st = int(i * note_dur * sr)
        if st >= total_samples: break
        en = min(total_samples, int((i + 1) * note_dur * sr))
        t_n = np.arange(en - st) / sr
        sub = np.sin(2 * np.pi * freq * t_n)
        sub += 0.35 * np.sin(2 * np.pi * freq * 2 * t_n)
        sub += 0.15 * np.sin(2 * np.pi * freq * 3 * t_n)
        sub = np.tanh(sub * 2.2) * 0.42
        sub *= np.minimum(1.0, t_n * 25.0)
        sub *= np.maximum(0.2, np.exp(-t_n * 0.5))
        left[st:en] += sub
        right[st:en] += sub

    # Arpeggio
    arp_notes = [164.8, 196.0, 246.9, 293.7, 329.6, 392.0, 493.9, 587.3]
    arp_step = spb / 4
    for step in range(int(duration / arp_step)):
        st = int(step * arp_step * sr)
        if st >= total_samples: break
        freq = arp_notes[(step * 3) % len(arp_notes)]
        n_len = min(int(0.22 * sr), total_samples - st)
        t_l = np.arange(n_len) / sr
        saw = 2 * (t_l * freq - np.floor(t_l * freq + 0.5))
        lead = saw * np.exp(-t_l * 12) * 0.18
        pan = 0.5 + 0.3 * np.sin(step * 0.75)
        left[st:st + n_len] += lead * (1 - pan)
        right[st:st + n_len] += lead * pan

    # Cuts transitions
    cuts = [0.0, 3.6, 8.2, 12.8, 17.4]
    for cut_t in cuts:
        pos = int(cut_t * sr)
        if pos < total_samples:
            en = min(total_samples, pos + crash_len)
            left[pos:en] += crash[:en - pos] * 0.8
            right[pos:en] += crash[:en - pos] * 0.8
        if cut_t > 0:
            r_len = int(1.2 * sr)
            r_st = max(0, pos - r_len)
            t_r = np.arange(pos - r_st) / sr
            riser = np.random.uniform(-1, 1, len(t_r)) * (t_r / (len(t_r) / sr)) ** 2 * 0.38
            left[r_st:pos] += riser * 0.75
            right[r_st:pos] += riser * 0.85

    peak = max(np.max(np.abs(left)), np.max(np.abs(right)), 0.001)
    scale = 0.94 / peak
    left = np.clip(left * scale, -0.99, 0.99)
    right = np.clip(right * scale, -0.99, 0.99)
    
    stereo = np.empty((total_samples * 2,), dtype=np.int16)
    stereo[0::2] = (left * 32767).astype(np.int16)
    stereo[1::2] = (right * 32767).astype(np.int16)
    
    with wave.open(OUT_AUDIO, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(stereo.tobytes())
    print("[AUDIO] Generated audio:", OUT_AUDIO)

make_audio()

# -------------------------------------------------------------
# 2. LOAD FONTS
# -------------------------------------------------------------
def get_font(name, size):
    font_path = os.path.join(r"C:\Windows\Fonts", name)
    if os.path.exists(font_path):
        return ImageFont.truetype(font_path, size)
    return ImageFont.load_default()

font_title_lg = get_font("impact.ttf", 54)
font_title_md = get_font("impact.ttf", 40)
font_title_sm = get_font("impact.ttf", 30)
font_bold_lg  = get_font("arialbd.ttf", 32)
font_bold_md  = get_font("arialbd.ttf", 25)
font_bold_sm  = get_font("arialbd.ttf", 20)
font_text_md  = get_font("segoeuib.ttf", 21)
font_text_sm  = get_font("segoeuib.ttf", 17)
font_badge    = get_font("arialbd.ttf", 16)

# -------------------------------------------------------------
# 3. PRELOAD & CACHE IMAGES
# -------------------------------------------------------------
print("[ASSETS] Preloading images...")
def load_img(path):
    if os.path.exists(path):
        return Image.open(path).convert("RGBA")
    return Image.new("RGBA", (100, 100), (40, 40, 40, 255))

logo_raw = load_img("assets/images/logo_profile_hd.png")
hero_rider_raw = load_img("assets/images/hero-rider-mt07.jpg")

# Apparel
h_preto_front = load_img("assets/images/apparel/hoodie_preto_front.jpg")
h_preto_back  = load_img("assets/images/apparel/hoodie_preto_back.jpg")
h_amarelo_front = load_img("assets/images/apparel/hoodie_amarelo_front.jpg")
h_amarelo_back  = load_img("assets/images/apparel/hoodie_amarelo_back.jpg")
t_preto_front = load_img("assets/images/apparel/tshirt_preto_front.jpg")
t_preto_back  = load_img("assets/images/apparel/tshirt_preto_back.jpg")
t_amarelo_front = load_img("assets/images/apparel/tshirt_amarelo_front.jpg")
t_amarelo_back  = load_img("assets/images/apparel/tshirt_amarelo_back.jpg")

# Parts
p_retrovisores = load_img("assets/images/products/retrovisores_stealth_main.jpg")
p_escape = load_img("assets/images/products/escape_r77_main.jpg")
p_lanterna = load_img("assets/images/products/lanterna_led_fume_main.jpg")

# Video background reader
video_reader = imageio.get_reader("assets/videos/hero_dark_rider.mp4")
print("[ASSETS] Video reader initialized!")

def fit_image(img, target_w, target_h):
    w, h = img.size
    scale = max(target_w / w, target_h / h)
    nw, nh = int(w * scale), int(h * scale)
    res = img.resize((nw, nh), Image.Resampling.BILINEAR)
    left = (nw - target_w) // 2
    top = (nh - target_h) // 2
    return res.crop((left, top, left + target_w, top + target_h))

def draw_card(canvas, box, bg=(20, 22, 30, 240), border=(60, 65, 80, 255), radius=16, border_w=2):
    x0, y0, x1, y1 = box
    card = Image.new("RGBA", (x1 - x0, y1 - y0), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle([(0, 0), (x1 - x0 - 1, y1 - y0 - 1)], radius=radius, fill=bg, outline=border, width=border_w)
    canvas.paste(card, (x0, y0), card)

def draw_badge(draw, text, xy, bg=(246, 255, 0), fg=(0, 0, 0), font=font_badge, pad=(12, 5), radius=8):
    x, y = xy
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    bx0 = x - pad[0]
    by0 = y - pad[1]
    bx1 = x + tw + pad[0]
    by1 = y + th + pad[1] + 2
    draw.rounded_rectangle([(bx0, by0), (bx1, by1)], radius=radius, fill=bg)
    draw.text((x, y), text, font=font, fill=fg)
    return bx1, by1

def get_rider_bg(frame_idx, darken=0.5):
    try:
        raw_f = video_reader.get_data(frame_idx % 800)
        im = Image.fromarray(raw_f).convert("RGBA")
    except Exception:
        im = hero_rider_raw
    bg = fit_image(im, WIDTH, HEIGHT)
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (10, 10, 14, int(255 * darken)))
    bg = Image.alpha_composite(bg, overlay)
    return bg

def get_tech_bg(frame_idx):
    bg = Image.new("RGBA", (WIDTH, HEIGHT), (12, 13, 18, 255))
    d = ImageDraw.Draw(bg)
    grid_spacing = 40
    offset = int((frame_idx * 2) % grid_spacing)
    for y in range(0, HEIGHT, grid_spacing):
        d.line([(0, y + offset), (WIDTH, y + offset)], fill=(22, 24, 34, 255), width=1)
    for x in range(0, WIDTH, grid_spacing):
        d.line([(x, 0), (x, HEIGHT)], fill=(22, 24, 34, 255), width=1)
    glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([(-100, -150), (WIDTH + 100, 300)], fill=(246, 255, 0, 20))
    gd.ellipse([(100, HEIGHT - 350), (WIDTH + 200, HEIGHT + 100)], fill=(246, 255, 0, 15))
    bg = Image.alpha_composite(bg, glow)
    return bg

def draw_reels_header(canvas, frame_idx):
    d = ImageDraw.Draw(canvas)
    seg_w = (WIDTH - 40 - 16) // 5
    y = 12
    cuts = [0, 108, 246, 384, 522, TOTAL_FRAMES]
    for i in range(5):
        sx0 = 20 + i * (seg_w + 4)
        sx1 = sx0 + seg_w
        d.rounded_rectangle([(sx0, y), (sx1, y + 4)], radius=2, fill=(60, 62, 75, 200))
        if frame_idx >= cuts[i + 1]:
            d.rounded_rectangle([(sx0, y), (sx1, y + 4)], radius=2, fill=(246, 255, 0, 255))
        elif frame_idx >= cuts[i]:
            pct = (frame_idx - cuts[i]) / (cuts[i + 1] - cuts[i])
            fill_x = sx0 + int(seg_w * pct)
            d.rounded_rectangle([(sx0, y), (fill_x, y + 4)], radius=2, fill=(246, 255, 0, 255))
            
    d.rounded_rectangle([(24, 28), (280, 68)], radius=20, fill=(18, 20, 28, 230), outline=(50, 52, 68), width=1)
    d.ellipse([(34, 38), (54, 58)], fill=(246, 255, 0))
    d.text((62, 38), "DARK GHOSTRIDER", font=font_badge, fill=(255, 255, 255))
    draw_badge(d, "● LOJA OFICIAL", (WIDTH - 150, 39), bg=(30, 32, 44), fg=(246, 255, 0), font=font_badge, radius=12)

def draw_reels_footer(canvas, frame_idx):
    d = ImageDraw.Draw(canvas)
    pulse = 1.0 + 0.03 * math.sin(frame_idx * 0.25)
    bw = int(660 * pulse)
    bh = 60
    bx0 = (WIDTH - bw) // 2
    by0 = 1175
    bx1 = bx0 + bw
    by1 = by0 + bh
    
    d.rounded_rectangle([(bx0, by0), (bx1, by1)], radius=30, fill=(246, 255, 0), outline=(255, 255, 255), width=2)
    txt = "🛒 WWW.DARKGHOSTRIDER.COM ⚡"
    bbox = d.textbbox((0, 0), txt, font=font_bold_md)
    tw = bbox[2] - bbox[0]
    d.text(((WIDTH - tw) // 2, by0 + 16), txt, font=font_bold_md, fill=(0, 0, 0))
    
    sub = "CLICA NO LINK DA BIO • ENVIO PORTUGAL & EUROPA"
    sbbox = d.textbbox((0, 0), sub, font=font_badge)
    stw = sbbox[2] - sbbox[0]
    d.text(((WIDTH - stw) // 2, by1 + 10), sub, font=font_badge, fill=(180, 185, 200))

# -------------------------------------------------------------
# 4. SCENE RENDERERS
# -------------------------------------------------------------

def render_scene_0(frame_idx):
    bg = get_rider_bg(frame_idx, darken=0.55)
    d = ImageDraw.Draw(bg)
    
    scan_y = int((frame_idx * 14) % HEIGHT)
    d.line([(0, scan_y), (WIDTH, scan_y)], fill=(246, 255, 0, 180), width=3)
    
    pulse = 1.0 + 0.05 * math.sin(frame_idx * 0.3)
    lw = int(230 * pulse)
    lx = (WIDTH - lw) // 2
    ly = 240 - int(pulse * 8)
    
    ring_r = lw // 2 + 12
    d.ellipse([(WIDTH // 2 - ring_r, ly + lw // 2 - ring_r), 
               (WIDTH // 2 + ring_r, ly + lw // 2 + ring_r)], 
              outline=(246, 255, 0, 220), width=4)
    
    logo_scaled = logo_raw.resize((lw, lw), Image.Resampling.LANCZOS)
    bg.paste(logo_scaled, (lx, ly), logo_scaled)
    
    t1 = "DARK GHOSTRIDER"
    bb1 = d.textbbox((0, 0), t1, font=font_title_lg)
    tw1 = bb1[2] - bb1[0]
    d.text(((WIDTH - tw1) // 2 + 3, 523), t1, font=font_title_lg, fill=(0, 0, 0))
    d.text(((WIDTH - tw1) // 2, 520), t1, font=font_title_lg, fill=(255, 255, 255))
    
    t2 = "★ LOJA OFICIAL ONLINE ★"
    bb2 = d.textbbox((0, 0), t2, font=font_title_sm)
    tw2 = bb2[2] - bb2[0]
    pw = tw2 + 40
    px = (WIDTH - pw) // 2
    d.rounded_rectangle([(px, 595), (px + pw, 645)], radius=25, fill=(246, 255, 0))
    d.text(((WIDTH - tw2) // 2, 606), t2, font=font_title_sm, fill=(0, 0, 0))
    
    t3 = "TUDO O QUE O DARK USA NA SUA MOTO ESTÁ AQUI"
    bb3 = d.textbbox((0, 0), t3, font=font_bold_sm)
    tw3 = bb3[2] - bb3[0]
    d.text(((WIDTH - tw3) // 2, 675), t3, font=font_bold_sm, fill=(246, 255, 0))
    
    t4 = "DROP 01 VESTUÁRIO  •  SETUP MT-07  •  ACESSÓRIOS"
    bb4 = d.textbbox((0, 0), t4, font=font_text_md)
    tw4 = bb4[2] - bb4[0]
    d.text(((WIDTH - tw4) // 2, 720), t4, font=font_text_md, fill=(255, 255, 255))
    
    pills = [("🔥 DROP 01 NO AR", (246, 255, 0), (0, 0, 0)),
             ("🏍️ SETUP MT-07", (35, 38, 52), (255, 255, 255)),
             ("🇵🇹 MB WAY & CTT", (35, 38, 52), (246, 255, 0))]
    total_pw = 180 * 3 + 20
    st_px = (WIDTH - total_pw) // 2
    for idx, (p_txt, p_bg, p_fg) in enumerate(pills):
        cur_x = st_px + idx * 190
        d.rounded_rectangle([(cur_x, 790), (cur_x + 180, 836)], radius=23, fill=p_bg, outline=(60, 65, 80), width=1)
        pbb = d.textbbox((0, 0), p_txt, font=font_badge)
        ptw = pbb[2] - pbb[0]
        d.text((cur_x + (180 - ptw) // 2, 804), p_txt, font=font_badge, fill=p_fg)
        
    url_box = (60, 880, WIDTH - 60, 960)
    draw_card(bg, url_box, bg=(15, 17, 24, 240), border=(246, 255, 0), radius=20, border_w=2)
    url_d = ImageDraw.Draw(bg)
    url_txt = "WWW.DARKGHOSTRIDER.COM"
    ubb = url_d.textbbox((0, 0), url_txt, font=font_title_md)
    utw = ubb[2] - ubb[0]
    url_d.text(((WIDTH - utw) // 2, 898), url_txt, font=font_title_md, fill=(246, 255, 0))
    
    draw_reels_header(bg, frame_idx)
    draw_reels_footer(bg, frame_idx)
    return bg

def render_scene_1(frame_idx):
    bg = get_tech_bg(frame_idx)
    d = ImageDraw.Draw(bg)
    
    is_hoodie = (frame_idx < 177)
    
    d.text((30, 80), "🔥 DROP 01 EXCLUSIVO", font=font_title_md, fill=(246, 255, 0))
    sub_title = "SWEATSHIRTS COM CAPUZ OVERSIZED" if is_hoodie else "T-SHIRTS OVERSIZED STREETWEAR"
    d.text((30, 130), sub_title, font=font_bold_sm, fill=(255, 255, 255))
    
    card_box = (24, 175, WIDTH - 24, 1140)
    draw_card(bg, card_box, bg=(18, 20, 28, 245), border=(60, 64, 82), radius=22, border_w=2)
    
    cd = ImageDraw.Draw(bg)
    sub_frame = (frame_idx - 108) if is_hoodie else (frame_idx - 177)
    show_back = (sub_frame >= 35)
    
    if is_hoodie:
        img_left = h_preto_back if show_back else h_preto_front
        img_right = h_amarelo_back if show_back else h_amarelo_front
        lbl_left = "PRETO STEALTH" + (" (COSTAS)" if show_back else " (FRENTE)")
        lbl_right = "CYBER AMARELO" + (" (COSTAS)" if show_back else " (FRENTE)")
        price_tag = "39,90€"
    else:
        img_left = t_preto_back if show_back else t_preto_front
        img_right = t_amarelo_back if show_back else t_amarelo_front
        lbl_left = "PRETO OVERSIZED" + (" (COSTAS)" if show_back else " (FRENTE)")
        lbl_right = "CYBER AMARELO" + (" (COSTAS)" if show_back else " (FRENTE)")
        price_tag = "24,90€"
        
    top_badge_txt = "NOVA ESTAMPA COSTAS & FRENTE HD" if show_back else "CORTE OVERSIZED STREETWEAR"
    cd.rounded_rectangle([(44, 195), (WIDTH - 44, 235)], radius=12, fill=(30, 34, 48))
    tbb = cd.textbbox((0, 0), top_badge_txt, font=font_badge)
    cd.text(((WIDTH - (tbb[2] - tbb[0])) // 2, 205), top_badge_txt, font=font_badge, fill=(246, 255, 0))
    
    img_w, img_h = 310, 420
    im1 = fit_image(img_left, img_w, img_h)
    im2 = fit_image(img_right, img_w, img_h)
    
    bg.paste(im1, (42, 255))
    cd.rectangle([(42, 255), (42 + img_w, 255 + img_h)], outline=(60, 65, 85), width=2)
    bg.paste(im2, (WIDTH - 42 - img_w, 255))
    cd.rectangle([(WIDTH - 42 - img_w, 255), (WIDTH - 42, 255 + img_h)], outline=(60, 65, 85), width=2)
    
    cd.rounded_rectangle([(42, 685), (42 + img_w, 720)], radius=8, fill=(25, 28, 38))
    bb_l = cd.textbbox((0, 0), lbl_left, font=font_badge)
    cd.text((42 + (img_w - (bb_l[2] - bb_l[0])) // 2, 693), lbl_left, font=font_badge, fill=(255, 255, 255))
    
    cd.rounded_rectangle([(WIDTH - 42 - img_w, 685), (WIDTH - 42, 720)], radius=8, fill=(25, 28, 38))
    bb_r = cd.textbbox((0, 0), lbl_right, font=font_badge)
    cd.text((WIDTH - 42 - img_w + (img_w - (bb_r[2] - bb_r[0])) // 2, 693), lbl_right, font=font_badge, fill=(246, 255, 0))
    
    specs_y = 745
    specs = [
        ("✔ ALGODÃO PREMIUM 320g" if is_hoodie else "✔ 100% ALGODÃO PENTEADO CONFORTÁVEL"),
        ("✔ LOGO COSTAS EM ALTA DEFINIÇÃO (MESMA LOGO NA PRETA & AMARELA)"),
        ("✔ DISPONÍVEL DO TAMANHO S AO XXL COM GUIA DE MEDIDAS")
    ]
    for sp in specs:
        cd.text((50, specs_y), sp, font=font_text_sm, fill=(230, 235, 245))
        specs_y += 34
        
    price_box = (42, 875, WIDTH - 42, 965)
    cd.rounded_rectangle([price_box[0:2], price_box[2:4]], radius=18, fill=(246, 255, 0))
    p_txt1 = f"A PARTIR DE {price_tag}"
    pbb1 = cd.textbbox((0, 0), p_txt1, font=font_title_md)
    cd.text(((WIDTH - (pbb1[2] - pbb1[0])) // 2, 888), p_txt1, font=font_title_md, fill=(0, 0, 0))
    p_txt2 = "★ OPÇÃO DE PACKS ECONÓMICOS COM DESCONTO NA LOJA ★"
    pbb2 = cd.textbbox((0, 0), p_txt2, font=font_badge)
    cd.text(((WIDTH - (pbb2[2] - pbb2[0])) // 2, 936), p_txt2, font=font_badge, fill=(20, 20, 20))
    
    cd.rounded_rectangle([(50, 995), (WIDTH - 50, 1045)], radius=14, fill=(35, 38, 52), outline=(246, 255, 0), width=1)
    al_txt = "⚡ STOCK LIMITADO DO DROP 01 — GARANTE O TEU ANTES QUE ESGOTE!"
    albb = cd.textbbox((0, 0), al_txt, font=font_badge)
    cd.text(((WIDTH - (albb[2] - albb[0])) // 2, 1012), al_txt, font=font_badge, fill=(246, 255, 0))
    
    draw_reels_header(bg, frame_idx)
    draw_reels_footer(bg, frame_idx)
    return bg

def render_scene_2(frame_idx):
    bg = get_tech_bg(frame_idx)
    d = ImageDraw.Draw(bg)
    
    d.text((30, 80), "🏍️ SETUP MT-07 DO DARK", font=font_title_md, fill=(246, 255, 0))
    d.text((30, 130), "TUDO O QUE O DARK USA NA MOTO ESTÁ AQUI", font=font_bold_sm, fill=(255, 255, 255))
    
    cards_data = [
        (p_retrovisores, "RETROVISORES STEALTH WING", "Asas Aerodinâmicas Alumínio CNC", "• Rotação 360° • Plug & Play MT-07", "28,90€", 175),
        (p_escape, "ESCAPE FULL SYSTEM R77", "Linha Completa Carbono + Inox", "• Ronco Grave Potente • Ganho de Torque", "219,00€", 495),
        (p_lanterna, "LANTERNA LED FUMÊ TRASEIRA", "Com Piscas Sequenciais Integrados", "• Lente Escurecida • Encaixe Direto OEM", "39,90€", 815),
    ]
    
    for img, title, subtitle, bullets, price, y_pos in cards_data:
        card_box = (24, y_pos, WIDTH - 24, y_pos + 295)
        draw_card(bg, card_box, bg=(18, 20, 28, 245), border=(55, 60, 78), radius=18, border_w=2)
        cd = ImageDraw.Draw(bg)
        
        p_img = fit_image(img, 245, 245)
        bg.paste(p_img, (44, y_pos + 25))
        cd.rectangle([(44, y_pos + 25), (44 + 245, y_pos + 270)], outline=(60, 65, 85), width=2)
        
        rx = 310
        cd.text((rx, y_pos + 28), title, font=font_bold_md, fill=(246, 255, 0))
        cd.text((rx, y_pos + 68), subtitle, font=font_text_sm, fill=(255, 255, 255))
        
        by = y_pos + 115
        for b_line in bullets.split("•"):
            b_line = b_line.strip()
            if not b_line: continue
            cd.text((rx, by), "• " + b_line, font=font_badge, fill=(180, 185, 200))
            by += 30
            
        pw = 140
        cd.rounded_rectangle([(rx, y_pos + 205), (rx + pw, y_pos + 255)], radius=12, fill=(246, 255, 0))
        pbb = cd.textbbox((0, 0), price, font=font_title_sm)
        cd.text((rx + (pw - (pbb[2] - pbb[0])) // 2, y_pos + 215), price, font=font_title_sm, fill=(0, 0, 0))
        
        draw_badge(cd, "COMPATÍVEL MT-07", (rx + 155, y_pos + 220), bg=(32, 36, 48), fg=(246, 255, 0), font=font_badge, radius=8)
        
    draw_reels_header(bg, frame_idx)
    draw_reels_footer(bg, frame_idx)
    return bg

def render_scene_3(frame_idx):
    bg = get_tech_bg(frame_idx)
    d = ImageDraw.Draw(bg)
    
    d.text((30, 80), "⚡ EXPERIÊNCIA DA LOJA", font=font_title_md, fill=(246, 255, 0))
    d.text((30, 130), "COMPRA RÁPIDA, SEGURA & SEM COMPLICAÇÕES", font=font_bold_sm, fill=(255, 255, 255))
    
    features = [
        ("🔍", "NOVA VISTA DETALHADA TIPO MOTOCARD", 
         "Página dedicada para cada item com fotos gigantes em alta definição, zoom e especificações completas.",
         "EXPERIÊNCIA PREMIUM", 180),
        ("📦", "PACKS ECONÓMICOS COM DESCONTO", 
         "Adiciona packs de sweatshirt + t-shirt ou kits de peças com descontos automáticos no carrinho.",
         "POUPA ATÉ 20%", 410),
        ("📏", "GUIA DE TAMANHOS & MEDIDAS", 
         "Tabela de medidas exata para não errares no tamanho da tua peça do Drop 01.",
         "DO S AO XXL", 640),
        ("🇵🇹", "MB WAY & ENVIO CTT EXPRESSO 24/48H", 
         "Pagamentos nacionais seguros e envio rápido com tracking em tempo real no site.",
         "MÁXIMA CONFIANÇA", 870)
    ]
    
    for icon, title, desc, tag, y_pos in features:
        card_box = (24, y_pos, WIDTH - 24, y_pos + 205)
        draw_card(bg, card_box, bg=(18, 20, 28, 245), border=(55, 60, 78), radius=18, border_w=2)
        cd = ImageDraw.Draw(bg)
        
        cd.ellipse([(44, y_pos + 35), (104, y_pos + 95)], fill=(30, 34, 48), outline=(246, 255, 0), width=2)
        ibb = cd.textbbox((0, 0), icon, font=font_bold_md)
        cd.text((74 - (ibb[2] - ibb[0]) // 2, y_pos + 48), icon, font=font_bold_md, fill=(246, 255, 0))
        
        cd.text((125, y_pos + 35), title, font=font_bold_md, fill=(246, 255, 0))
        draw_badge(cd, tag, (125, y_pos + 75), bg=(32, 36, 50), fg=(255, 255, 255), font=font_badge, radius=8)
        
        words = desc.split(" ")
        lines = []
        cur_line = ""
        for w in words:
            test_l = (cur_line + " " + w).strip()
            if len(test_l) > 42:
                lines.append(cur_line)
                cur_line = w
            else:
                cur_line = test_l
        if cur_line: lines.append(cur_line)
        
        ly = y_pos + 120
        for l in lines[:2]:
            cd.text((45, ly), l, font=font_text_sm, fill=(200, 205, 220))
            ly += 28
            
    cd = ImageDraw.Draw(bg)
    cd.rounded_rectangle([(40, 1095), (WIDTH - 40, 1145)], radius=14, fill=(25, 28, 38), outline=(246, 255, 0), width=1)
    inf_txt = "✨ TUDO TESTADO & SELECIONADO PELO DARK GHOSTRIDER"
    inbb = cd.textbbox((0, 0), inf_txt, font=font_badge)
    cd.text(((WIDTH - (inbb[2] - inbb[0])) // 2, 1112), inf_txt, font=font_badge, fill=(246, 255, 0))
    
    draw_reels_header(bg, frame_idx)
    draw_reels_footer(bg, frame_idx)
    return bg

def render_scene_4(frame_idx):
    bg = get_rider_bg(frame_idx, darken=0.6)
    d = ImageDraw.Draw(bg)
    
    fade = 1.0
    if frame_idx >= 640:
        fade = max(0.0, (TOTAL_FRAMES - frame_idx) / 20.0)
        
    pulse = 1.0 + 0.06 * math.sin(frame_idx * 0.35)
    lw = int(240 * pulse)
    lx = (WIDTH - lw) // 2
    ly = 200
    
    ring_r = lw // 2 + 16
    d.ellipse([(WIDTH // 2 - ring_r, ly + lw // 2 - ring_r), 
               (WIDTH // 2 + ring_r, ly + lw // 2 + ring_r)], 
              outline=(246, 255, 0), width=5)
    
    logo_scaled = logo_raw.resize((lw, lw), Image.Resampling.LANCZOS)
    bg.paste(logo_scaled, (lx, ly), logo_scaled)
    
    motto = "“Tudo o que o Dark usa na sua moto está aqui.”"
    mbb = d.textbbox((0, 0), motto, font=font_bold_sm)
    d.text(((WIDTH - (mbb[2] - mbb[0])) // 2, 490), motto, font=font_bold_sm, fill=(255, 255, 255))
    
    cta_box = (36, 560, WIDTH - 36, 760)
    d.rounded_rectangle([cta_box[0:2], cta_box[2:4]], radius=28, fill=(246, 255, 0), outline=(255, 255, 255), width=3)
    
    c_txt1 = "👉 VISITA JÁ O SITE OFICIAL 👈"
    cbb1 = d.textbbox((0, 0), c_txt1, font=font_bold_md)
    d.text(((WIDTH - (cbb1[2] - cbb1[0])) // 2, 580), c_txt1, font=font_bold_md, fill=(0, 0, 0))
    
    c_txt2 = "WWW.DARKGHOSTRIDER.COM"
    cbb2 = d.textbbox((0, 0), c_txt2, font=font_title_lg)
    d.text(((WIDTH - (cbb2[2] - cbb2[0])) // 2, 630), c_txt2, font=font_title_lg, fill=(0, 0, 0))
    
    c_txt3 = "CLICA NO LINK DA BIO DO INSTAGRAM"
    cbb3 = d.textbbox((0, 0), c_txt3, font=font_badge)
    d.text(((WIDTH - (cbb3[2] - cbb3[0])) // 2, 705), c_txt3, font=font_badge, fill=(20, 20, 20))
    
    d.rounded_rectangle([(140, 790), (WIDTH - 140, 860)], radius=22, fill=(18, 20, 28, 240), outline=(246, 255, 0), width=2)
    ig_txt = "📲 @dark.ghostrider"
    igbb = d.textbbox((0, 0), ig_txt, font=font_title_md)
    d.text(((WIDTH - (igbb[2] - igbb[0])) // 2, 804), ig_txt, font=font_title_md, fill=(255, 255, 255))
    
    d.text(((WIDTH - 360) // 2, 900), "🇵🇹 PORTUGAL & EUROPA  •  CTT EXPRESSO", font=font_text_sm, fill=(246, 255, 0))
    d.text(((WIDTH - 310) // 2, 940), "PAGAMENTOS MB WAY & CARTÃO 100% SEGURO", font=font_badge, fill=(200, 205, 220))
    
    d.rounded_rectangle([(50, 1000), (WIDTH - 50, 1070)], radius=16, fill=(35, 38, 52), outline=(60, 65, 80), width=1)
    al2 = "GARANTE AS TUAS PEÇAS DO DROP 01 ANTES DE ESGOTAR!"
    al2bb = d.textbbox((0, 0), al2, font=font_badge)
    d.text(((WIDTH - (al2bb[2] - al2bb[0])) // 2, 1025), al2, font=font_badge, fill=(246, 255, 0))
    
    if fade < 1.0:
        black_overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, int(255 * (1.0 - fade))))
        bg = Image.alpha_composite(bg, black_overlay)
        
    draw_reels_header(bg, frame_idx)
    draw_reels_footer(bg, frame_idx)
    return bg

# -------------------------------------------------------------
# 5. FFmpeg PIPELINE EXECUTION
# -------------------------------------------------------------
print("[FFMPEG] Starting pipeline...")
ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()

cmd = [
    ffmpeg_bin,
    "-y",
    "-f", "rawvideo",
    "-vcodec", "rawvideo",
    "-s", f"{WIDTH}x{HEIGHT}",
    "-pix_fmt", "rgb24",
    "-r", str(FPS),
    "-i", "-",
    "-i", OUT_AUDIO,
    "-c:v", "libx264",
    "-pix_fmt", "yuv420p",
    "-preset", "veryfast",
    "-crf", "20",
    "-c:a", "aac",
    "-b:a", "192k",
    "-shortest",
    OUT_VIDEO
]

proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

t0 = time.time()
print(f"[RENDER] Generating {TOTAL_FRAMES} frames ({DURATION}s @ {FPS}fps)...")

for i in range(TOTAL_FRAMES):
    if i < 108:
        frame = render_scene_0(i)
    elif i < 246:
        frame = render_scene_1(i)
    elif i < 384:
        frame = render_scene_2(i)
    elif i < 522:
        frame = render_scene_3(i)
    else:
        frame = render_scene_4(i)
        
    rgb = frame.convert("RGB").tobytes()
    proc.stdin.write(rgb)
    
    if (i + 1) % 60 == 0 or i == TOTAL_FRAMES - 1:
        elapsed = time.time() - t0
        fps_speed = (i + 1) / max(elapsed, 0.01)
        pct = int(((i + 1) / TOTAL_FRAMES) * 100)
        print(f"Progress: {pct}% ({i + 1}/{TOTAL_FRAMES}) | Speed: {fps_speed:.1f} fps | Elapsed: {elapsed:.1f}s")

proc.stdin.close()
stderr_out = proc.stderr.read().decode("utf-8", errors="ignore")
proc.wait()

print("[FFMPEG] Finished with return code:", proc.returncode)
if proc.returncode != 0:
    print("[FFMPEG ERROR]", stderr_out[-1000:])
else:
    print("[SUCCESS] Video saved to:", OUT_VIDEO)
    shutil.copyfile(OUT_VIDEO, ALT_VIDEO)
    print("[SUCCESS] Video copied to:", ALT_VIDEO)
    sz = os.path.getsize(OUT_VIDEO) / (1024 * 1024)
    print(f"[SUCCESS] File size: {sz:.2f} MB")

try:
    video_reader.close()
except Exception:
    pass

print("=== REELS GENERATION COMPLETE ===")
