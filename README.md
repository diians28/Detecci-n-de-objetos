# Vision Assist

Este proyecto detecta objetos en tiempo real con YOLO, estima su distancia aproximada y emite una alerta sonora cuando un objeto se encuentra demasiado cerca.

## Requisitos

- Windows
- Python 3.11 o superior
- Cámara IP accesible desde la misma red
- Conexión a internet la primera vez, en caso de que `ultralytics` necesite preparar dependencias

## Objetos detectados

El programa está configurado para detectar:

- `person`
- `chair`
- `cup`
- `dining table`

## Archivos principales

- `main.py`: ejecuta la detección en tiempo real
- `distancia.py`: calcula la distancia estimada del objeto
- `alerta.py`: reproduce un sonido cuando un objeto está muy cerca
- `yolo11n.pt`: modelo de detección usado por el programa

## Instalación

Abre una terminal dentro de la carpeta `vision-assist` y ejecuta:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -U pip
pip install numpy opencv-python ultralytics
```

## Configuración de la cámara

Antes de ejecutar el programa, revisa esta línea en `main.py`:

```python
camara = cv2.VideoCapture("http://192.168.1.134:4747/video")
```

Debes cambiar la dirección si tu cámara IP usa otra URL.

## Ejecución

Desde la carpeta `vision-assist`, ejecuta:

```powershell
python main.py
```

## Funcionamiento

1. El programa abre la cámara IP.
2. Detecta objetos en cada frame.
3. Calcula una distancia aproximada en metros.
4. Dibuja el nombre del objeto y su distancia en pantalla.
5. Si un objeto está a menos de `1.0 m`, se reproduce una alerta sonora.

## Cómo cerrar el programa

Con la ventana de OpenCV activa, presiona la tecla `f`.

## Notas importantes

- El sonido de alerta usa `winsound`, por lo que esta versión está pensada para Windows.
- La distancia es una estimación y depende del tamaño de referencia configurado en `distancia.py`.
- Si la cámara no responde, el programa mostrará `No se encontro camara`.
- Si quieres detectar otros objetos, debes modificar la lista `objetos_filtrados` en `main.py`.
