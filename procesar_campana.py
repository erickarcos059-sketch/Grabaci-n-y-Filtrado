import wave
import numpy as np
import os
from scipy.signal import butter, filtfilt

ARCHIVO_ENTRADA = "captura_cruda_4khz.wav"  
ARCHIVO_SALIDA = "resultado.wav"

def filtro_fase_cero(data, lowcut=20, highcut=150, fs=4000, order=2):
    nyq = 0.5 * fs
    b, a = butter(order, [lowcut/nyq, highcut/nyq], btype='band')
    return filtfilt(b, a, data)

def procesar_ordenado():
    if not os.path.exists(ARCHIVO_ENTRADA):
        print(f"ERROR: No se encontró '{ARCHIVO_ENTRADA}'")
        return

    try:
        with wave.open(ARCHIVO_ENTRADA, 'rb') as w:
            fs = w.getframerate()
            data_raw = w.readframes(w.getnframes())
            audio_np = np.frombuffer(data_raw, dtype=np.int16).astype(np.float64)
            if w.getnchannels() == 2: audio_np = audio_np[0::2]

        audio_centrado = audio_np - np.mean(audio_np)

        # 1. FILTRADO GRUESO: Eliminamos la basura que causa el siseo inicial
        audio_pre_filtrado = filtro_fase_cero(audio_centrado, 30, 140, fs)

        # 2. PUERTA DE RUIDO: Limpiamos el aire ANTES de tocar el volumen
        # Usamos una envolvente más rápida para que no sea tan sensible al ruido
        rectificado = np.abs(audio_pre_filtrado)
        b, a = butter(2, 5.0 / (0.5 * fs), btype='low')
        perfil = filtfilt(b, a, rectificado)
        umbral = np.percentile(perfil, 30.0)
        atenuacion = np.clip((perfil - umbral * 0.5) / (umbral * 0.5), 0.05, 1.0)
        audio_sin_aire = audio_pre_filtrado * atenuacion

        # 3. FILTRADO FINO
        audio_fino = filtro_fase_cero(audio_sin_aire, 20, 150, fs)

        # 4. AMPLIFICACIÓN
        pico_final = np.max(np.abs(audio_fino))
        BOOST = 20.5
        if pico_final > 0:
            audio_final = audio_fino * ((25000.0 / pico_final) * (BOOST / 10.0))
        else:
            audio_final = audio_fino

        # 5. LIMITADOR SUAVE FINAL
        data_final = np.clip(np.tanh(audio_final / 25000.0) * 31000.0, -32768, 32767).astype(np.int16)

        with wave.open(ARCHIVO_SALIDA, 'w') as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(fs)
            f.writeframes(data_final.tobytes())

        print(f" audio limpio en: '{ARCHIVO_SALIDA}'")

    except Exception as e:
        print(f" Error: {e}")

if __name__ == "__main__":
    procesar_ordenado()