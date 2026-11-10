import math
import wave
import numpy as np

def generate_hoodie_showroom_audio(duration_sec=18.0, sample_rate=44100, output_wav='hoodie_beat.wav'):
    bpm = 115.0 # slightly slower, heavier, more cinematic
    beat_sec = 60.0 / bpm
    total_samples = int(duration_sec * sample_rate)
    
    left = np.zeros(total_samples, dtype=np.float32)
    right = np.zeros(total_samples, dtype=np.float32)
    
    # 1. Deep 808 Sub Kick (heavy cinematic impact)
    kick_len = int(0.55 * sample_rate)
    kick_t = np.linspace(0, 0.55, kick_len, False)
    kick_freq = 42.0 + 130.0 * np.exp(-kick_t * 18.0)
    kick_phase = np.cumsum(2.0 * np.pi * kick_freq / sample_rate)
    kick_env = np.exp(-kick_t * 5.0)
    kick_wave = np.sin(kick_phase) * kick_env
    kick_wave = np.tanh(kick_wave * 1.8) * 0.90
    
    # 2. Crisp Layered Snare / Rimshot
    snare_len = int(0.25 * sample_rate)
    snare_t = np.linspace(0, 0.25, snare_len, False)
    snare_noise = np.random.uniform(-1, 1, snare_len) * np.exp(-snare_t * 16.0)
    snare_tone = np.sin(2.0 * np.pi * 175.0 * snare_t) * np.exp(-snare_t * 22.0)
    snare_wave = (snare_noise * 0.7 + snare_tone * 0.4) * 0.8
    
    # 3. Metallic Hi-hat / Shaker
    hat_len = int(0.05 * sample_rate)
    hat_t = np.linspace(0, 0.05, hat_len, False)
    hat_noise = np.random.uniform(-1, 1, hat_len) * np.exp(-hat_t * 60.0)
    hat_wave = np.diff(hat_noise, prepend=0) * 0.32
    
    # 4. Cinematic Dark Drone / Pad (in background)
    t_all = np.linspace(0, duration_sec, total_samples, False)
    drone_f1 = 55.0 # A1
    drone_f2 = 110.0 # A2
    drone = (np.sin(2 * np.pi * drone_f1 * t_all) * 0.25 + 
             np.sin(2 * np.pi * drone_f2 * t_all) * 0.12 + 
             np.sin(2 * np.pi * (drone_f1 * 1.5) * t_all) * 0.08) # fifth
    # Add slow subtle LFO breathing to drone
    drone_lfo = 0.6 + 0.4 * np.sin(2 * np.pi * 0.25 * t_all)
    drone = drone * drone_lfo * 0.5
    left += drone
    right += drone
    
    # Place beat hits
    num_beats = int(duration_sec / beat_sec)
    for b in range(num_beats):
        beat_time = b * beat_sec
        start_idx = int(beat_time * sample_rate)
        if start_idx >= total_samples:
            break
            
        beat_in_measure = b % 4
        
        # Heavy Kick on beat 0 and beat 2.5
        if beat_in_measure == 0 or (beat_in_measure == 2 and (b // 4) % 2 == 1):
            k_end = min(start_idx + kick_len, total_samples)
            actual_k = k_end - start_idx
            left[start_idx:k_end] += kick_wave[:actual_k]
            right[start_idx:k_end] += kick_wave[:actual_k]
            
        # Snare on beat 2 (half-time heavy snare)
        if beat_in_measure == 2:
            s_end = min(start_idx + snare_len, total_samples)
            actual_s = s_end - start_idx
            left[start_idx:s_end] += snare_wave[:actual_s]
            right[start_idx:s_end] += snare_wave[:actual_s]
            
        # Hi-hat on 8th notes
        for h in range(2):
            h_time = beat_time + h * (beat_sec / 2.0)
            h_idx = int(h_time * sample_rate)
            if h_idx < total_samples:
                h_end = min(h_idx + hat_len, total_samples)
                actual_h = h_end - h_idx
                vol = 0.7 if h == 0 else 0.4
                left[h_idx:h_end] += hat_wave[:actual_h] * vol * 0.8
                right[h_idx:h_end] += hat_wave[:actual_h] * vol * 1.1

    # Smooth fades
    fade_in = int(0.3 * sample_rate)
    fade_out = int(1.2 * sample_rate)
    left[:fade_in] *= np.linspace(0, 1, fade_in)
    right[:fade_in] *= np.linspace(0, 1, fade_in)
    left[-fade_out:] *= np.linspace(1, 0, fade_out)
    right[-fade_out:] *= np.linspace(1, 0, fade_out)

    # Limiter / normalize
    max_val = max(np.max(np.abs(left)), np.max(np.abs(right)), 1e-4)
    left = (left / max_val) * 0.92
    right = (right / max_val) * 0.92
    
    # Fast vectorized conversion to 16-bit PCM
    stereo = np.column_stack((np.clip(left, -1.0, 1.0), np.clip(right, -1.0, 1.0)))
    pcm_bytes = (stereo * 32767.0).astype(np.int16).tobytes()
    
    with wave.open(output_wav, 'wb') as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_bytes)
        
    print(f"Showroom audio created: {output_wav}")

if __name__ == '__main__':
    generate_hoodie_showroom_audio(duration_sec=18.0, output_wav='scratch/hoodie_beat.wav')
