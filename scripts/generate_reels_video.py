# -*- coding: utf-8 -*-
import os, sys, math, time, subprocess, wave, shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
import imageio
import imageio_ffmpeg

print("=== REBUILDING ENHANCED REELS VIDEO (9:16) ===")

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
# 1. AUDIO SYNTHESIS: 128 BPM Phonk Beat
# -------------------------------------------------------------
def make_audio():
    sr = 44100
    duration = DURATION
    total_samples = int(sr * duration)
    bpm = 128.0
    spb = 60.0 / bpm
    
    left = np.zeros(total_samples, dtype=np.float32)
    right = np.zeros(total_samples, dtype=np.float32)
    
    kick_len = int(0.35 * sr)
    t_k = np.arange(kick_len) / sr
    f_k = 48 + 120 * np.exp(-t_k * 30)
    phase_k = np.cumsum(f_k * 2 * np.pi / sr)
    env_k = np.exp(-t_k * 8.5)
    click = np.sin(2 * np.pi * 1700 * t_k) * np.exp(-t_k * 140) * 0.45
    kick = np.tanh((np.sin(phase_k) * env_k + click) * 1.6) * 0.95
    
    snare_len = int(0.28 * sr)
    t_s = np.arange(snare_len) / sr
    noise = np.random.uniform(-1, 1, snare_len)
    body = np.sin(2 * np.pi * 210 * t_s) * np.exp(-t_s * 25) * 0.5
    snare = (noise * np.exp(-t_s * 15) * 0.65 + body) * 0.75
    
    hat_len = int(0.08 * sr)
    t_h = np.arange(hat_len) / sr
    hat = np.random.uniform(-1, 1, hat_len) * np.exp(-t_h * 55) * 0.28
    
    crash_len = int(2.5 * sr)
    t_c = np.arange(crash_len) / sr
    crash = np.random.uniform(-1, 1, crash_len) * np.exp(-t_c * 2.2) * 0.55
    
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

    cuts = [0.0, 3.8, 8.5, 13.0, 17.5]
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

font_title_lg = get_font("impact.ttf", 52)
font_title_md = get_font("impact.ttf", 38)
font_title_sm = get_font("impact.ttf", 28)
font_bold_lg  = get_font("arialbd.ttf", 32)
font_bold_md  = get_font("arialbd.ttf", 24)
font_bold_sm  = get_font("arialbd.ttf", 20)
font_text_md  = get_font("segoeuib.ttf", 21)
font_text_sm  = get_font("segoeuib.ttf", 17)
font_badge    = get_font("arialbd.ttf", 15)

# -------------------------------------------------------------
# 3. PRELOAD & CACHE IMAGES
# -------------------------------------------------------------
print("[ASSETS] Preloading images...")
def load_img(path):
    if os.path.exists(path):
        return Image.open(path).convert("RGBA")
    return Image.new("RGBA", (100, 100), (40, 40, 40, 255))

logo_raw = load_img("assets/images/logo_profile_hd.png")
logo_skull_raw = load_img("assets/images/apparel/estampa_costas.jpg")
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

# Instagram Story Header
def draw_story_header(canvas, frame_idx):
    d = ImageDraw.Draw(canvas)
    seg_w = (WIDTH - 40 - 16) // 5
    y = 14
    cuts = [0, 114, 255, 390, 525, TOTAL_FRAMES]
    for i in range(5):
        sx0 = 20 + i * (seg_w + 4)
        sx1 = sx0 + seg_w
        d.rounded_rectangle([(sx0, y), (sx1, y + 3)], radius=2, fill=(80, 82, 95, 200))
        if frame_idx >= cuts[i + 1]:
            d.rounded_rectangle([(sx0, y), (sx1, y + 3)], radius=2, fill=(255, 255, 255, 255))
        elif frame_idx >= cuts[i]:
            pct = (frame_idx - cuts[i]) / max(cuts[i + 1] - cuts[i], 1)
            fill_x = sx0 + int(seg_w * pct)
            d.rounded_rectangle([(sx0, y), (fill_x, y + 3)], radius=2, fill=(255, 255, 255, 255))
            
    avatar_size = 40
    ax, ay = 24, 28
    d.ellipse([(ax - 3, ay - 3), (ax + avatar_size + 3, ay + avatar_size + 3)], outline=(246, 255, 0), width=2)
    av_img = logo_raw.resize((avatar_size, avatar_size), Image.Resampling.LANCZOS)
    canvas.paste(av_img, (ax, ay), av_img)
    
    d.text((ax + avatar_size + 12, ay + 3), "dark.ghostrider", font=font_bold_sm, fill=(255, 255, 255))
    d.ellipse([(ax + avatar_size + 172, ay + 6), (ax + avatar_size + 186, ay + 20)], fill=(0, 150, 255))
    d.text((ax + avatar_size + 175, ay + 6), "✓", font=font_badge, fill=(255, 255, 255))
    d.text((ax + avatar_size + 12, ay + 23), "Loja Oficial • há 2 h", font=font_badge, fill=(180, 185, 200))
    d.text((WIDTH - 42, ay + 8), "✕", font=font_bold_md, fill=(220, 220, 220))

# CENTRAL STORY LOGO STICKER WITH WHITE CONTOUR + GLOW
def create_story_logo_sticker(raw_img, size, pulse=1.0, border_color=(255, 255, 255), outline_color=(246, 255, 0)):
    sz = int(size * pulse)
    img_scaled = raw_img.resize((sz, sz), Image.Resampling.LANCZOS)
    
    mask = Image.new("L", (sz, sz), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse([(0, 0), (sz, sz)], fill=255)
    
    pad = 18
    tot_sz = sz + pad * 2
    sticker = Image.new("RGBA", (tot_sz, tot_sz), (0, 0, 0, 0))
    
    sd = ImageDraw.Draw(sticker)
    sd.ellipse([(pad - 2, pad + 6), (pad + sz + 2, pad + sz + 10)], fill=(0, 0, 0, 160))
    sticker = sticker.filter(ImageFilter.GaussianBlur(6))
    
    bd = ImageDraw.Draw(sticker)
    bd.ellipse([(pad - 5, pad - 5), (pad + sz + 5, pad + sz + 5)], fill=border_color, outline=outline_color, width=3)
    sticker.paste(img_scaled, (pad, pad), mask)
    return sticker

# INSTAGRAM STORY LINK STICKER
def draw_story_link_sticker(canvas, text, center_xy, font=font_bold_md, bounce=0.0):
    cx, cy = center_xy
    cy += int(bounce)
    d = ImageDraw.Draw(canvas)
    
    bbox = d.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    
    pill_w = tw + 56
    pill_h = th + 28
    x0 = cx - pill_w // 2
    y0 = cy - pill_h // 2
    x1 = x0 + pill_w
    y1 = y0 + pill_h
    
    shadow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle([(x0, y0 + 5), (x1, y1 + 5)], radius=pill_h // 2, fill=(0, 0, 0, 150))
    shadow = shadow.filter(ImageFilter.GaussianBlur(5))
    canvas.paste(shadow, (0, 0), shadow)
    
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle([(x0, y0), (x1, y1)], radius=pill_h // 2, fill=(255, 255, 255), outline=(246, 255, 0), width=2)
    d.text((x0 + 28, y0 + 13), text, font=font, fill=(12, 14, 22))

# -------------------------------------------------------------
# 4. SCENE RENDERERS WITH STORY LOGO IN THE MIDDLE
# -------------------------------------------------------------

def render_scene_0(frame_idx):
    bg = get_rider_bg(frame_idx, darken=0.55)
    d = ImageDraw.Draw(bg)
    
    scan_y = int((frame_idx * 15) % HEIGHT)
    d.line([(0, scan_y), (WIDTH, scan_y)], fill=(246, 255, 0, 180), width=3)
    
    # ⭐ CENTRAL STORY LOGO STICKER
    pulse = 1.0 + 0.05 * math.sin(frame_idx * 0.35)
    bounce = 6.0 * math.sin(frame_idx * 0.25)
    stk = create_story_logo_sticker(logo_raw, size=210, pulse=pulse)
    sw, sh = stk.size
    sx = (WIDTH - sw) // 2
    sy = 270 + int(bounce)
    bg.paste(stk, (sx, sy), stk)
    
    draw_badge(d, "★ LOJA OFICIAL ONLINE ★", (WIDTH // 2 - 120, sy + sh - 8), bg=(246, 255, 0), fg=(0, 0, 0), font=font_badge, radius=12)
    
    t1 = "DARK GHOSTRIDER"
    bb1 = d.textbbox((0, 0), t1, font=font_title_lg)
    tw1 = bb1[2] - bb1[0]
    d.text(((WIDTH - tw1) // 2 + 2, 572), t1, font=font_title_lg, fill=(0, 0, 0))
    d.text(((WIDTH - tw1) // 2, 570), t1, font=font_title_lg, fill=(255, 255, 255))
    
    t2 = "TUDO O QUE O DARK USA NA MOTO ESTÁ AQUI"
    bb2 = d.textbbox((0, 0), t2, font=font_bold_sm)
    tw2 = bb2[2] - bb2[0]
    d.text(((WIDTH - tw2) // 2, 640), t2, font=font_bold_sm, fill=(246, 255, 0))
    
    pills = [("🔥 DROP 01 VESTUÁRIO", (246, 255, 0), (0, 0, 0)),
             ("🏍️ SETUP MT-07", (26, 28, 40), (255, 255, 255)),
             ("🇵🇹 MB WAY & CTT", (26, 28, 40), (246, 255, 0))]
    pw_tot = 185 * 3 + 20
    spx = (WIDTH - pw_tot) // 2
    for idx, (pt, pbg, pfg) in enumerate(pills):
        cx = spx + idx * 195
        d.rounded_rectangle([(cx, 715), (cx + 185, 762)], radius=23, fill=pbg, outline=(70, 75, 95), width=2)
        pbb = d.textbbox((0, 0), pt, font=font_badge)
        d.text((cx + (185 - (pbb[2] - pbb[0])) // 2, 730), pt, font=font_badge, fill=pfg)
        
    link_bounce = 4.0 * math.sin(frame_idx * 0.3)
    draw_story_link_sticker(bg, "🔗 WWW.DARKGHOSTRIDER.COM ↗", (WIDTH // 2, 850), font=font_bold_md, bounce=link_bounce)
    
    tap_txt = "👆 TOQUE NO LINK PARA VISITAR A LOJA"
    tbb = d.textbbox((0, 0), tap_txt, font=font_badge)
    d.text(((WIDTH - (tbb[2] - tbb[0])) // 2, 905), tap_txt, font=font_badge, fill=(200, 205, 220))
    
    draw_story_header(bg, frame_idx)
    return bg

def render_scene_1(frame_idx):
    bg = get_tech_bg(frame_idx)
    d = ImageDraw.Draw(bg)
    
    is_hoodie = (frame_idx < 185)
    sub_frame = (frame_idx - 114) if is_hoodie else (frame_idx - 185)
    show_back = (sub_frame >= 35)
    
    d.text((30, 80), "🔥 DROP 01 • VESTUÁRIO", font=font_title_md, fill=(246, 255, 0))
    sub_title = "SWEATSHIRTS COM CAPUZ 320g" if is_hoodie else "T-SHIRTS OVERSIZED 100% ALGODÃO"
    d.text((30, 130), sub_title, font=font_bold_sm, fill=(255, 255, 255))
    
    img_w, img_h = 300, 420
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
        
    im1 = fit_image(img_left, img_w, img_h)
    im2 = fit_image(img_right, img_w, img_h)
    
    bg.paste(im1, (40, 185))
    d.rectangle([(40, 185), (40 + img_w, 185 + img_h)], outline=(65, 70, 90), width=2)
    bg.paste(im2, (WIDTH - 40 - img_w, 185))
    d.rectangle([(WIDTH - 40 - img_w, 185), (WIDTH - 40, 185 + img_h)], outline=(65, 70, 90), width=2)
    
    d.rounded_rectangle([(40, 615), (40 + img_w, 650)], radius=8, fill=(24, 26, 36))
    bb_l = d.textbbox((0, 0), lbl_left, font=font_badge)
    d.text((40 + (img_w - (bb_l[2] - bb_l[0])) // 2, 624), lbl_left, font=font_badge, fill=(255, 255, 255))
    
    d.rounded_rectangle([(WIDTH - 40 - img_w, 615), (WIDTH - 40, 650)], radius=8, fill=(24, 26, 36))
    bb_r = d.textbbox((0, 0), lbl_right, font=font_badge)
    d.text((WIDTH - 40 - img_w + (img_w - (bb_r[2] - bb_r[0])) // 2, 624), lbl_right, font=font_badge, fill=(246, 255, 0))
    
    # ⭐ LOGO NO MEIO COMO DE UNS STORIES (BETWEEN CLOTHING)
    pulse = 1.0 + 0.06 * math.sin(frame_idx * 0.4)
    active_logo = logo_skull_raw if show_back else logo_raw
    stk = create_story_logo_sticker(active_logo, size=150, pulse=pulse, border_color=(255, 255, 255), outline_color=(246, 255, 0))
    sw, sh = stk.size
    sx = (WIDTH - sw) // 2
    sy = 340
    bg.paste(stk, (sx, sy), stk)
    
    mid_tag = "★ LOGO COSTAS HD ★" if show_back else "★ LOGO OFICIAL DROP 01 ★"
    draw_badge(d, mid_tag, (WIDTH // 2 - 95, sy + sh - 10), bg=(246, 255, 0), fg=(0, 0, 0), font=font_badge, radius=10)
    
    specs_y = 675
    specs = [
        ("✔ ALGODÃO PREMIUM 320g" if is_hoodie else "✔ 100% ALGODÃO PENTEADO CONFORTÁVEL"),
        ("✔ MESMA LOGO NA PRETA & NA AMARELA (FRENTE E COSTAS)"),
        ("✔ DISPONÍVEL DO TAMANHO S AO XXL COM GUIA DE MEDIDAS")
    ]
    for sp in specs:
        d.text((50, specs_y), sp, font=font_text_sm, fill=(230, 235, 245))
        specs_y += 32
        
    p_box = (40, 785, WIDTH - 40, 870)
    d.rounded_rectangle([p_box[0:2], p_box[2:4]], radius=18, fill=(246, 255, 0))
    p1 = f"A PARTIR DE {price_tag}"
    pbb1 = d.textbbox((0, 0), p1, font=font_title_md)
    d.text(((WIDTH - (pbb1[2] - pbb1[0])) // 2, 796), p1, font=font_title_md, fill=(0, 0, 0))
    p2 = "★ OPÇÃO DE PACKS ECONÓMICOS COM DESCONTO NA LOJA ★"
    pbb2 = d.textbbox((0, 0), p2, font=font_badge)
    d.text(((WIDTH - (pbb2[2] - pbb2[0])) // 2, 840), p2, font=font_badge, fill=(20, 20, 20))
    
    link_bounce = 3.0 * math.sin(frame_idx * 0.3)
    draw_story_link_sticker(bg, "🔗 VER VESTUÁRIO NA LOJA ↗", (WIDTH // 2, 930), font=font_bold_md, bounce=link_bounce)
    
    al_txt = "⚡ STOCK LIMITADO DO DROP 01 — GARANTE O TEU ANTES QUE ESGOTE!"
    albb = d.textbbox((0, 0), al_txt, font=font_badge)
    d.text(((WIDTH - (albb[2] - albb[0])) // 2, 990), al_txt, font=font_badge, fill=(246, 255, 0))
    
    draw_story_header(bg, frame_idx)
    return bg

def render_scene_2(frame_idx):
    bg = get_tech_bg(frame_idx)
    d = ImageDraw.Draw(bg)
    
    d.text((30, 80), "🏍️ SETUP MT-07 DO DARK", font=font_title_md, fill=(246, 255, 0))
    d.text((30, 130), "TUDO O QUE O DARK USA NA MOTO ESTÁ AQUI", font=font_bold_sm, fill=(255, 255, 255))
    
    cards_data = [
        (p_retrovisores, "RETROVISORES STEALTH WING", "Asas Aerodinâmicas Alumínio CNC", "• Rotação 360° • Plug & Play MT-07", "28,90€", 175),
        (p_escape, "ESCAPE FULL SYSTEM R77", "Linha Completa Carbono + Inox", "• Ronco Grave Potente • Ganho de Torque", "219,00€", 460),
        (p_lanterna, "LANTERNA LED FUMÊ TRASEIRA", "Com Piscas Sequenciais Integrados", "• Lente Escurecida • Encaixe Direto OEM", "39,90€", 745),
    ]
    
    for img, title, subtitle, bullets, price, y_pos in cards_data:
        card_box = (24, y_pos, WIDTH - 24, y_pos + 265)
        draw_card(bg, card_box, bg=(18, 20, 28, 245), border=(55, 60, 78), radius=18, border_w=2)
        cd = ImageDraw.Draw(bg)
        
        p_img = fit_image(img, 220, 220)
        bg.paste(p_img, (44, y_pos + 22))
        cd.rectangle([(44, y_pos + 22), (44 + 220, y_pos + 242)], outline=(60, 65, 85), width=2)
        
        rx = 285
        cd.text((rx, y_pos + 24), title, font=font_bold_md, fill=(246, 255, 0))
        cd.text((rx, y_pos + 60), subtitle, font=font_text_sm, fill=(255, 255, 255))
        
        by = y_pos + 102
        for b_line in bullets.split("•"):
            b_line = b_line.strip()
            if not b_line: continue
            cd.text((rx, by), "• " + b_line, font=font_badge, fill=(180, 185, 200))
            by += 28
            
        pw = 135
        cd.rounded_rectangle([(rx, y_pos + 185), (rx + pw, y_pos + 232)], radius=12, fill=(246, 255, 0))
        pbb = cd.textbbox((0, 0), price, font=font_title_sm)
        cd.text((rx + (pw - (pbb[2] - pbb[0])) // 2, y_pos + 195), price, font=font_title_sm, fill=(0, 0, 0))
        
        draw_badge(cd, "COMPATÍVEL MT-07", (rx + 150, y_pos + 198), bg=(32, 36, 48), fg=(246, 255, 0), font=font_badge, radius=8)
        
    # ⭐ LOGO NO MEIO COMO DE UNS STORIES (STORY SEAL)
    pulse = 1.0 + 0.05 * math.sin(frame_idx * 0.35)
    stk = create_story_logo_sticker(logo_raw, size=120, pulse=pulse)
    sw, sh = stk.size
    bg.paste(stk, (WIDTH - sw - 20, 410), stk)
    
    link_bounce = 3.0 * math.sin(frame_idx * 0.3)
    draw_story_link_sticker(bg, "🔗 VER PEÇAS DA MT-07 ↗", (WIDTH // 2, 1050), font=font_bold_md, bounce=link_bounce)
    
    draw_story_header(bg, frame_idx)
    return bg

def render_scene_3(frame_idx):
    bg = get_tech_bg(frame_idx)
    d = ImageDraw.Draw(bg)
    
    d.text((30, 80), "⚡ EXPERIÊNCIA DA LOJA", font=font_title_md, fill=(246, 255, 0))
    d.text((30, 130), "COMPRA RÁPIDA, SEGURA & SEM COMPLICAÇÕES", font=font_bold_sm, fill=(255, 255, 255))
    
    features = [
        ("🔍", "VISTA DETALHADA TIPO MOTOCARD", 
         "Página dedicada para cada item com fotos gigantes em alta resolução, zoom e especificações completas.",
         "EXPERIÊNCIA PREMIUM", 180),
        ("📦", "PACKS ECONÓMICOS COM DESCONTO", 
         "Conjuntos de sweatshirt + t-shirt ou kits de peças com descontos automáticos no carrinho.",
         "POUPA ATÉ 20%", 385),
        ("📏", "GUIA DE TAMANHOS & MEDIDAS", 
         "Tabela de medidas exata para não errares no tamanho da tua peça do Drop 01.",
         "DO S AO XXL", 590),
        ("🇵🇹", "MB WAY & CTT EXPRESSO 24/48H", 
         "Pagamentos nacionais seguros e envio rápido com tracking em tempo real no site.",
         "MÁXIMA CONFIANÇA", 795)
    ]
    
    for icon, title, desc, tag, y_pos in features:
        card_box = (24, y_pos, WIDTH - 24, y_pos + 185)
        draw_card(bg, card_box, bg=(18, 20, 28, 245), border=(55, 60, 78), radius=18, border_w=2)
        cd = ImageDraw.Draw(bg)
        
        cd.ellipse([(44, y_pos + 28), (98, y_pos + 82)], fill=(30, 34, 48), outline=(246, 255, 0), width=2)
        ibb = cd.textbbox((0, 0), icon, font=font_bold_md)
        cd.text((71 - (ibb[2] - ibb[0]) // 2, y_pos + 40), icon, font=font_bold_md, fill=(246, 255, 0))
        
        cd.text((115, y_pos + 28), title, font=font_bold_md, fill=(246, 255, 0))
        draw_badge(cd, tag, (115, y_pos + 65), bg=(32, 36, 50), fg=(255, 255, 255), font=font_badge, radius=8)
        
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
        
        ly = y_pos + 105
        for l in lines[:2]:
            cd.text((45, ly), l, font=font_text_sm, fill=(200, 205, 220))
            ly += 26
            
    # ⭐ LOGO NO MEIO COMO DE UNS STORIES (SEAL)
    pulse = 1.0 + 0.05 * math.sin(frame_idx * 0.35)
    stk = create_story_logo_sticker(logo_raw, size=115, pulse=pulse)
    bg.paste(stk, (WIDTH - 150, 560), stk)
    
    link_bounce = 3.0 * math.sin(frame_idx * 0.3)
    draw_story_link_sticker(bg, "🔗 WWW.DARKGHOSTRIDER.COM ↗", (WIDTH // 2, 1025), font=font_bold_md, bounce=link_bounce)
    
    draw_story_header(bg, frame_idx)
    return bg

def render_scene_4(frame_idx):
    bg = get_rider_bg(frame_idx, darken=0.6)
    d = ImageDraw.Draw(bg)
    
    fade = 1.0
    if frame_idx >= 640:
        fade = max(0.0, (TOTAL_FRAMES - frame_idx) / 20.0)
        
    # ⭐ LOGO GIGANTE NO MEIO DOS STORIES
    pulse = 1.0 + 0.06 * math.sin(frame_idx * 0.35)
    bounce = 6.0 * math.sin(frame_idx * 0.25)
    stk = create_story_logo_sticker(logo_raw, size=240, pulse=pulse)
    sw, sh = stk.size
    sx = (WIDTH - sw) // 2
    sy = 220 + int(bounce)
    bg.paste(stk, (sx, sy), stk)
    
    motto = "“Tudo o que o Dark usa na sua moto está aqui.”"
    mbb = d.textbbox((0, 0), motto, font=font_bold_sm)
    d.text(((WIDTH - (mbb[2] - mbb[0])) // 2, 510), motto, font=font_bold_sm, fill=(255, 255, 255))
    
    cta_box = (36, 565, WIDTH - 36, 750)
    d.rounded_rectangle([cta_box[0:2], cta_box[2:4]], radius=28, fill=(246, 255, 0), outline=(255, 255, 255), width=3)
    
    c_txt1 = "👉 VISITA JÁ A LOJA OFICIAL 👈"
    cbb1 = d.textbbox((0, 0), c_txt1, font=font_bold_md)
    d.text(((WIDTH - (cbb1[2] - cbb1[0])) // 2, 582), c_txt1, font=font_bold_md, fill=(0, 0, 0))
    
    c_txt2 = "WWW.DARKGHOSTRIDER.COM"
    cbb2 = d.textbbox((0, 0), c_txt2, font=font_title_lg)
    d.text(((WIDTH - (cbb2[2] - cbb2[0])) // 2, 630), c_txt2, font=font_title_lg, fill=(0, 0, 0))
    
    c_txt3 = "CLICA NO LINK DA BIO DO INSTAGRAM"
    cbb3 = d.textbbox((0, 0), c_txt3, font=font_badge)
    d.text(((WIDTH - (cbb3[2] - cbb3[0])) // 2, 700), c_txt3, font=font_badge, fill=(20, 20, 20))
    
    link_bounce = 4.0 * math.sin(frame_idx * 0.3)
    draw_story_link_sticker(bg, "🔗 DARKGHOSTRIDER.COM ↗", (WIDTH // 2, 820), font=font_bold_md, bounce=link_bounce)
    
    d.rounded_rectangle([(140, 885), (WIDTH - 140, 950)], radius=22, fill=(18, 20, 28, 240), outline=(246, 255, 0), width=2)
    ig_txt = "📲 @dark.ghostrider"
    igbb = d.textbbox((0, 0), ig_txt, font=font_title_md)
    d.text(((WIDTH - (igbb[2] - igbb[0])) // 2, 897), ig_txt, font=font_title_md, fill=(255, 255, 255))
    
    d.text(((WIDTH - 360) // 2, 985), "🇵🇹 PORTUGAL & EUROPA  •  CTT EXPRESSO", font=font_text_sm, fill=(246, 255, 0))
    d.text(((WIDTH - 310) // 2, 1025), "PAGAMENTOS MB WAY & CARTÃO 100% SEGURO", font=font_badge, fill=(200, 205, 220))
    
    if fade < 1.0:
        black_overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, int(255 * (1.0 - fade))))
        bg = Image.alpha_composite(bg, black_overlay)
        
    draw_story_header(bg, frame_idx)
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
    "-crf", "19",
    "-c:a", "aac",
    "-b:a", "192k",
    "-shortest",
    OUT_VIDEO
]

proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

t0 = time.time()
print(f"[RENDER] Generating {TOTAL_FRAMES} frames ({DURATION}s @ {FPS}fps)...")

for i in range(TOTAL_FRAMES):
    if i < 114:
        frame = render_scene_0(i)
    elif i < 255:
        frame = render_scene_1(i)
    elif i < 390:
        frame = render_scene_2(i)
    elif i < 525:
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

print("[POSTERS] Extracting updated poster frames...")
subprocess.run([ffmpeg_bin, "-y", "-ss", "00:00:02", "-i", OUT_VIDEO, "-frames:v", "1", "assets/images/reels_poster_intro.jpg"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
subprocess.run([ffmpeg_bin, "-y", "-ss", "00:00:06", "-i", OUT_VIDEO, "-frames:v", "1", "assets/images/reels_poster_drop01.jpg"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
subprocess.run([ffmpeg_bin, "-y", "-ss", "00:00:10", "-i", OUT_VIDEO, "-frames:v", "1", "assets/images/reels_poster_setup.jpg"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
subprocess.run([ffmpeg_bin, "-y", "-ss", "00:00:20", "-i", OUT_VIDEO, "-frames:v", "1", "assets/images/reels_poster_cta.jpg"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
shutil.copyfile("assets/images/reels_poster_intro.jpg", "assets/images/reels_poster.jpg")

shutil.copyfile("scripts/build_reels.py", "scripts/generate_reels_video.py")
print("=== REELS GENERATION COMPLETE ===")
