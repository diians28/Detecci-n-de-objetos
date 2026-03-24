import time
import cv2
from collections import defaultdict, deque
from ultralytics import YOLO
from distancia import CalcularDistancia
from alerta import alerta

# Carga el modelo YOLO que se usa para detectar objetos en cada frame.
model = YOLO("yolo11n.pt")

# Limita el procesamiento a las clases relevantes para la aplicacion.
objetos_filtrados = ["person", "chair", "cup", "dining table"]

# Abre el stream de video IP.
camara = cv2.VideoCapture("http://192.168.1.134:4747/video")

# Guarda un historial corto por objeto para suavizar la distancia estimada.
historial_distancias = defaultdict(lambda: deque(maxlen=3))
# Conserva el ultimo estado valido de cada objeto para mostrarlo por persistencia.
EstadoObjetos = {}

# Tiempo maximo en segundos durante el cual se mantiene visible un objeto si deja de detectarse.
PERSISTENCIA = 1.2
# Margen en pixeles para considerar que una caja esta pegada al borde del frame.
BORDEPX = 8


def DibujarObjeto(frame, bbox, etiqueta, color):
    # Dibuja la caja y la etiqueta del objeto sobre el frame.
    x1, y1, x2, y2 = bbox

    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
    cv2.putText(
        frame,
        etiqueta,
        (x1, max(20, y1 - 10)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        color,
        2,
    )


def ColorDistancia(distancia):
    # Devuelve un color segun el nivel de cercania del objeto.
    if distancia < 1.0:
        return (0, 0, 255)
    if distancia < 1.5:
        return (0, 200, 255)
    return (0, 200, 0)


def TamañoReferencia(objeto, bbox):
    # Elige la dimension mas estable segun el tipo de objeto.
    x1, y1, x2, y2 = bbox
    #Primero se calcula el ancho y alto en pixeles de la caja delimitadora del objeto detectado.
    ancho_pixels = x2 - x1
    alto_pixels = y2 - y1

    if objeto == "person":
        return alto_pixels
    if objeto in ["chair", "dining table","cup"]:
        return ancho_pixels
    return max(ancho_pixels, alto_pixels)


def MejoresDetecciones(results):
    # Conserva solo la deteccion mas confiable por cada objeto filtrado.
    detecciones_por_objeto = {}

    for resultado in results:
        for box in resultado.boxes:
            clase = int(box.cls[0])
            objeto = model.names[clase]

            if objeto not in objetos_filtrados:
                continue

            bbox = tuple(map(int, box.xyxy[0]))
            tamaño_pixels = TamañoReferencia(objeto, bbox)

            # Ignora cajas demasiado pequenas porque degradan la estimacion.
            if tamaño_pixels <= 5:
                continue

            confianza = float(box.conf[0])

            if objeto not in detecciones_por_objeto or confianza > detecciones_por_objeto[objeto]["confianza"]:
                detecciones_por_objeto[objeto] = {
                    "bbox": bbox,
                    "tamaño": tamaño_pixels,
                    "confianza": confianza,
                }

    return detecciones_por_objeto


def BordeFrame(bbox, ancho_frame, alto_frame):
    # Detecta si la caja esta recortada por alguno de los bordes del frame,esto sirve para que la distancia se calcule bien.
    x1, y1, x2, y2 = bbox
    return (
        x1 <= BORDEPX
        or y1 <= BORDEPX
        or x2 >= (ancho_frame - BORDEPX)
        or y2 >= (alto_frame - BORDEPX)
    )


def suavizar_distancia(objeto, distancia_raw, bbox, ancho_frame, alto_frame):
    # Estabiliza la lectura usando persistencia previa o un promedio corto.
    estado_previo = EstadoObjetos.get(objeto)

    if BordeFrame(bbox, ancho_frame, alto_frame) and estado_previo is not None:
        return min(distancia_raw, estado_previo["distancia"])

    historial_distancias[objeto].append(distancia_raw)
    return sum(historial_distancias[objeto]) / len(historial_distancias[objeto])


def ProcesarDeteccion(objeto, data, frame, ancho_frame, alto_frame, ahora):
    # Calcula distancia, actualiza estado, dispara alerta y dibuja la deteccion.
    bbox = data["bbox"]
    tamaño_px = data["tamaño"]
    distancia_raw = CalcularDistancia(objeto, tamaño_px)

    if distancia_raw is None:
        return

    distancia_suavizada = suavizar_distancia(objeto, distancia_raw, bbox, ancho_frame, alto_frame)

    EstadoObjetos[objeto] = {
        "distancia": distancia_suavizada,
        "bbox": bbox,
        "last_seen": ahora,
    }

    alerta(distancia_suavizada, objeto)

    color = ColorDistancia(distancia_suavizada)
    etiqueta = f"{objeto}: {distancia_suavizada:.2f} m"
    DibujarObjeto(frame, bbox, etiqueta, color)


def ObjetosPersistentes(frame, detecciones_por_objeto, ahora):
    # Mantiene visibles por poco tiempo los objetos recientemente perdidos.
    for objeto in objetos_filtrados:
        if objeto in detecciones_por_objeto:
            continue

        estado = EstadoObjetos.get(objeto)

        if estado is None:
            continue

        if ahora - estado["last_seen"] > PERSISTENCIA:
            continue

        etiqueta = f"{objeto}: {estado['distancia']:.2f} m"
        DibujarObjeto(frame, estado["bbox"], etiqueta, (0, 120, 255))


def main():
    while True:
        # Lee el siguiente frame de la camara.
        ret, frame = camara.read()

        if not ret:
            print("No se encontro camara")
            break

        # Obtiene las dimensiones del frame para validar cajas recortadas.
        alto_frame, ancho_frame = frame.shape[:2]

        # Ejecuta la deteccion de objetos sobre el frame actual.
        results = model(frame, conf=0.40, iou=0.45, verbose=False)
        DeteccionesObjeto = MejoresDetecciones(results)

        # Registra el instante actual para control de persistencia.
        ahora = time.time()

        for objeto, data in DeteccionesObjeto.items():
            ProcesarDeteccion(objeto, data, frame, ancho_frame, alto_frame, ahora)

        ObjetosPersistentes(frame, DeteccionesObjeto, ahora)

        # Muestra el resultado procesado en pantalla.
        cv2.imshow("Detector", frame)

        # Sale del programa si se presiona la tecla "f".
        if cv2.waitKey(1) & 0xFF == ord("f"):
            break


try:
    main()
finally:
    # Libera la camara y cierra las ventanas de OpenCV.
    camara.release()
    cv2.destroyAllWindows()
