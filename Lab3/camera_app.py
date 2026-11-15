from datetime import datetime

from guizero import App, PushButton, Text
from picamera2 import Picamera2, Preview
from picamera2.encoders import H264Encoder

picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration())
picam2.start_preview(Preview.QTGL)
picam2.start()

encoder = H264Encoder()
recording = False


def timestamp():
    return datetime.now().strftime("%H%M%S")


def take_photo():
    filename = f"photo_{timestamp()}.jpg"
    picam2.capture_file(filename)
    status.value = f"Zapisano {filename}"


def toggle_recording():
    global recording
    if recording:
        picam2.stop_encoder()
        video_button.text = "Nagraj wideo"
        status.value = "Nagranie zapisane"
    else:
        filename = f"video_{timestamp()}.h264"
        picam2.start_encoder(encoder, filename)
        video_button.text = "Zatrzymaj wideo"
        status.value = f"Nagrywam {filename}"
    recording = not recording


app = App(title="Kamera", width=320, height=200)
photo_button = PushButton(app, text="Zrób zdjęcie", command=take_photo)
video_button = PushButton(app, text="Nagraj wideo", command=toggle_recording)
status = Text(app, text="Gotowe", size=14)
app.display()
