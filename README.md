# Estetoscopio Digital: Procesamiento DSP
Proyecto de adquisición y filtrado de audio cardíaco (PCG).

## Estructura del Proyecto
- `grabador.py`: Captura de audio I2S (4kHz).
- `procesar_campana.py`: Pipeline de limpieza (Filtro Butterworth, Puerta de Ruido, Ganancia).
- `CMakeLists.txt`: Configuración para migración a entorno C++.

## Instalación
1. Clonar el repo: `git clone [URL]`
2. Instalar dependencias: `pip install numpy scipy`
