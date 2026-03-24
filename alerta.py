import time
import winsound  # ocupare esta libreria para poner un sonido de alerta

ULTIMA_ALERTA = {}
COOLDOWN_SEGUNDOS = 1.5


def alerta(distancia, objeto):
    if distancia is None:
        return

    if distancia < 1.0:
        ahora = time.time()
        ultima = ULTIMA_ALERTA.get(objeto, 0)
        if ahora - ultima < COOLDOWN_SEGUNDOS:
            return

        ULTIMA_ALERTA[objeto] = ahora
        print(f"ALERTA: {objeto} esta muy cerca ({distancia:.2f} m)")
        winsound.Beep(1000, 300)  # Frecuencia de 1000 Hz durante 300 ms
