import serial
import numpy as np
import wave
import time

PUERTO = 'COM3'       # <--- Cambia por tu puerto real
BAUDIOS = 921600
TIEMPO_GRABACION = 20 # Segundos
SAMPLE_RATE = 4000    
ARCHIVO_SALIDA = "captura_cruda_4khz.wav"

def simular_recepcion_app():
    print(f"🔌 Conectando al ESP32 en {PUERTO} a {BAUDIOS} baudios...")
    try:
        ser = serial.Serial(PUERTO, BAUDIOS, timeout=1)
        ser.reset_input_buffer()
        
        print(f" Grabando {TIEMPO_GRABACION} segundos.")
        
        muestras_totales_requeridas = SAMPLE_RATE * TIEMPO_GRABACION
        audio_buffer = []
        
        # Parámetros del simulador BLE
        SYNC_WORD = b'\xAA\xBB'
        PACKET_SIZE = 246  # 2 Sync + 2 Seq + 242 Audio (121 muestras int16)
        
        buffer_temporal = bytearray()
        
        while len(audio_buffer) < muestras_totales_requeridas:
            # 1. Leer todo lo que haya en el puerto serial
            if ser.in_waiting > 0:
                buffer_temporal.extend(ser.read(ser.in_waiting))
                
            # 2. Buscar paquetes completos dentro del buffer temporal
            while len(buffer_temporal) >= PACKET_SIZE:
                sync_idx = buffer_temporal.find(SYNC_WORD)
                
                if sync_idx == -1:
                    # No se encontró cabecera, borramos basura pero dejamos el último byte por si es la mitad de un 0xAA
                    buffer_temporal = buffer_temporal[-1:]
                    break
                    
                if sync_idx > 0:
                    # Hay basura antes de la cabecera, la descartamos
                    del buffer_temporal[:sync_idx]
                    continue
                    
                # Si llegamos aquí, tenemos una cabecera en el índice 0
                if len(buffer_temporal) >= PACKET_SIZE:
                    # Extraer el paquete completo
                    paquete = buffer_temporal[:PACKET_SIZE]
                    del buffer_temporal[:PACKET_SIZE]
                    
                    # 3. Descartar los 4 primeros bytes (Sync 0xAA 0xBB + SeqNum) y quedarnos con el audio
                    audio_bytes = paquete[4:]
                    
                    # 4. Convertir a un array de enteros de 16 bits
                    muestras = np.frombuffer(audio_bytes, dtype=np.int16)
                    audio_buffer.extend(muestras)
                    
        ser.close()
        print("Recepción finalizada")

        # Recortar el buffer al tamaño exacto de segundos solicitados
        audio_final = np.array(audio_buffer[:muestras_totales_requeridas], dtype=np.int16)

        with wave.open(ARCHIVO_SALIDA, 'w') as f:
            f.setnchannels(1)
            f.setsampwidth(2) # 2 bytes = 16 bits
            f.setframerate(SAMPLE_RATE)
            f.writeframes(audio_final.tobytes())
            
        print(f"Señal cruda guardada como: '{ARCHIVO_SALIDA}'")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    simular_recepcion_app()
    
