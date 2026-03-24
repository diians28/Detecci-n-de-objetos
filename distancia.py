#Los anchos  estan en cm
FOCAL_PX = 1110

ANCHO = {
    "person": 60.0,
    "chair": 54.0,
    "cup": 9.0,
    "dining table": 80.0
}

def CalcularDistancia(objeto, ancho_pixel, focal_px=FOCAL_PX):

    if ancho_pixel <= 0:
        return None
#
    AnchoReal = ANCHO.get(objeto)

    if AnchoReal is None:
        return None

    Distancia = (focal_px * AnchoReal) / ancho_pixel

    if Distancia <= 0:
        return None
#Para convertit a metros
    return Distancia / 100