import math
import wave
import struct
import numpy as np

def generate_promo_beat(duration_sec=20.0, sample_rate=44100, output_wav='promo_beat.wav'):
    bpm = 125.0
    beat_sec = 60.0 / bpm
    total_samples = int(duration_sec * sample_rate)
    
    # Left and right audio buffers (float32)
    left = np.zeros(total_samples, dtype=np.float32)
    right = np.zeros(total_samples, dtype=np.float32)
    
    # Generate 808 Kick
    # Pitch drops from ~160Hz to ~45Hz with exponential decay
    kick_len = int(0.45 * sample_rate)
    kick_t = np.linspace(0, 0.45, kick_len, False)
    kick_freq = 45.0 + 120.0 * np.exp(-kick_t * 22.0)
    kick_phase = np.cumsum(2.0 * np.pi * kick_freq / sample_rate)
    kick_env = np.exp(-kick_t * 6.5)
    kick_wave = np.sin(kick_phase) * kick_env
    # Add subtle drive/saturation
    kick_wave = np.tanh(kick_wave * 1.6) * 0.85
    
    # Generate Crisp Snare / Clap
    snare_len = int(0.22 * sample_rate)
    snare_t = np.linspace(0, 0.22, snare_len, False)
    snare_noise = np.random.uniform(-1, 1, snare_len) * np.exp(-snare_t * 18.0)
    snare_tone = np.sin(2.0 * np.pi * 190.0 * snare_t) * np.exp(-snare_t * 25.0)
    snare_wave = (snare_noise * 0.75 + snare_tone * 0.35) * 0.75
    
    # Generate Hi-hat
    hat_len = int(0.06 * sample_rate)
    hat_t = np.linspace(0, 0.06, hat_len, False)
    hat_noise = np.random.uniform(-1, 1, hat_len) * np.exp(-hat_t * 55.0)
    # High-pass filter simulated by differencing
    hat_wave = np.diff(hat_noise, prepend=0) * 0.35
    
    # Sub Bass notes (A1=55Hz, F1=43.65Hz, D1=36.7Hz, E1=41.2Hz)
    chord_freqs = [55.0, 43.65, 36.7, 41.2]
    
    # Place drums and bass across the 20 seconds
    num_beats = int(duration_sec / beat_sec)
    
    for b in range(num_beats):
        beat_time = b * beat_sec
        start_idx = int(beat_time * sample_rate)
        if start_idx >= total_samples:
            break
            
        measure = (b // 4)
        beat_in_measure = b % 4
        
        # Chord progression every 4 beats (1 measure per chord)
        chord_idx = measure % 4
        bass_freq = chord_freqs[chord_idx]
        
        # Kick on beat 0, 2 (or 0, 1.5, 2.5 syncopated)
        has_kick = (beat_in_measure == 0 or beat_in_measure == 2 or (beat_in_measure == 1 and measure % 2 == 1))
        if has_kick:
            k_end = min(start_idx + kick_len, total_samples)
            actual_len = k_end - start_idx
            left[start_idx:k_end] += kick_wave[:actual_len]
            right[start_idx:k_end] += kick_wave[:actual_len]
            
        # Snare on beats 1 and 3 (2nd and 4th beats of the bar)
        if beat_in_measure == 1 or beat_in_measure == 3:
            s_end = min(start_idx + snare_len, total_samples)
            actual_len = s_end - start_idx
            left[start_idx:s_end] += snare_wave[:actual_len] * 0.9
            right[start_idx:s_end] += snare_wave[:actual_len] * 0.9
            
        # 16th note hi-hats (4 hats per beat)
        sub_len = beat_sec / 4.0
        for h in range(4):
            h_time = beat_time + h * sub_len
            h_idx = int(h_time * sample_rate)
            if h_idx < total_samples:
                h_end = min(h_idx + hat_len, total_samples)
                actual_h = h_end - h_idx
                vol = 0.8 if h == 0 else (0.5 if h == 2 else 0.35)
                # Slight stereo panning for hi-hats
                left[h_idx:h_end] += hat_wave[:actual_h] * vol * 0.7
                right[h_idx:h_end] += hat_wave[:actual_h] * vol * 1.1
                
        # Bass synthesizer tone across the beat
        note_len = int(beat_sec * sample_rate)
        note_end = min(start_idx + note_len, total_samples)
        act_note_len = note_end - start_idx
        t_note = np.linspace(0, act_note_len / sample_rate, act_note_len, False)
        # Rich sawtooth-like bass (fundamental + harmonics)
        saw = (np.sin(2 * np.pi * bass_freq * t_note) * 0.5 +
               np.sin(2 * np.pi * bass_freq * 2 * t_note) * 0.25 +
               np.sin(2 * np.pi * bass_freq * 3 * t_note) * 0.12)
        # Envelope: punchy pluck with sustain
        env = np.exp(-t_note * 2.8) * 0.45 + 0.15
        bass_note = saw * env
        # Lowpass filter effect
        bass_note = np.tanh(bass_note * 1.3) * 0.4
        
        left[start_idx:note_end] += bass_note
        right[start_idx:note_end] += bass_note
        
        # High synth pluck arp on off-beats for musical atmosphere
        if b >= 4 and b < num_beats - 2:
            arp_note = bass_freq * 8.0 # higher octave
            arp_t = np.linspace(0, len(t_note) / sample_rate, len(t_note), False)
            arp_wave = np.sin(2 * np.pi * arp_note * arp_t) * np.exp(-arp_t * 8.0) * 0.08
            pan_l = 0.5 + 0.3 * np.sin(b * 0.8)
            pan_r = 1.0 - pan_l
            left[start_idx:note_end] += arp_wave * pan_l
            right[start_idx:note_end] += arp_wave * pan_r

    # Smooth fade in (0.3s) and fade out (1.2s)
    fade_in_len = int(0.3 * sample_rate)
    fade_out_len = int(1.2 * sample_rate)
    left[:fade_in_len] *= np.linspace(0, 1, fade_in_len)
    right[:fade_in_len] *= np.linspace(0, 1, fade_in_len)
    left[-fade_out_len:] *= np.linspace(1, 0, fade_out_len)
    right[-fade_out_len:] *= np.linspace(1, 0, fade_out_len)

    # Master limiter / normalization
    max_val = max(np.max(np.abs(left)), np.max(np.abs(right)), 1e-4)
    target_peak = 0.92
    left = (left / max_val) * target_peak
    right = (right / max_val) * target_peak
    
    # Interleave to 16-bit PCM
    audio_data = bytearray()
    for i in range(total_samples):
        sl = int(np.clip(left[i], -1.0, 1.0) * 32767.0)
        sr = int(np.clip(right[i], -1.0, 1.0) * 32767.0)
        audio_data.extend(struct.pack('<hh', sl, sr))
        
    with wave.open(output_wav, 'wb') as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_data)
        
    print(f"Beat generated successfully: {output_wav} ({duration_sec}s, {total_samples} samples)")

if __name__ == '__main__':
    generate_promo_beat(duration_sec=20.0, output_wav='scratch_promo_beat.wav')
