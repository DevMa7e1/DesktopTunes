import numpy as np
from PyQt6.QtWidgets import QProgressBar, QHBoxLayout, QWidget, QLabel
from PyQt6.QtCore import Qt
from array import array
from PIL import Image, ImageDraw
import numpy as np
from miniaudio import convert_frames, SampleFormat

class FrequencyEffect(QHBoxLayout):
    @staticmethod
    def get_values_for_frame(frame: array, sample_rate: int):
        f = sample_rate//len(frame)*2
        result = convert_frames(SampleFormat.SIGNED16, 1, 48000, frame.tobytes(), SampleFormat.SIGNED16, 1, 96000)

        vals = abs(np.fft.fft(array('h', result)))
        intervals = [60, 120, 240, 480, 960, 1920, 3840, 7680, 15360]
        values = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        average = 0

        for index in range(len(intervals)):
            interval = intervals[index]
            if index == 0:
                last = 0
            else:
                last = intervals[index-1]

            for i in range(last//f, interval//f):
                values[index] += vals[i]
            values[index] = np.round(values[index])
            average += np.round(values[index])

        average /= len(values)

        for i in range(len(intervals)):
            values[i] /= average
            values[i] *= 100
            values[i] = min(values[i], 100)
            values[i] = safe_int(values[i])
        return values
    
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.progress_bars: list[QProgressBar] = []

        for _ in range(9):
            self.progress_bars.append(QProgressBar())
            self.progress_bars[-1].setTextVisible(False)
            self.progress_bars[-1].setOrientation(Qt.Orientation.Vertical)
            self.addWidget(self.progress_bars[-1])
    
    def refresh(self, frame: array, sample_rate: int):
        v = self.get_values_for_frame(frame, sample_rate)
        for i in range(9):
            self.progress_bars[i].setValue(int(v[i]))

def safe_int(input):
    try:
        return int(input)
    except:
        return 0

class PreciseFrequencyEffect(QHBoxLayout):
    @staticmethod
    def get_values_for_frame(frame: array):
        result = convert_frames(SampleFormat.SIGNED16, 1, 48000, frame.tobytes(), SampleFormat.SIGNED16, 1, 96000)

        vals = abs(np.fft.fft(array('h', result)))
        values = []
        img = Image.new('RGBA', (400, 200), (0, 0, 0, 255))
        imgdraw = ImageDraw.ImageDraw(img)
        average = 0
        f = len(vals)//1600
        for x in range(1600):
            val = 0
            for i in range(x*f, x*f+f):
                val += vals[i]
            values.append(val)

        for i in range(200):
            average += values[i]
        for i in range(1400, 1600):
            average += values[i]

        average /= 200
            
        for x in range(400):
            if x <= 200:
                index = x
            else:
                index = 1200 + x
            if x < 200:
                v = x
            else:
                v = 200 - (x % 200)
            v /= 200
            color = [0.6*v, 0.18 + (0.16 * v), 0.9 - (0.22 * v)]
            imgdraw.line(((x, 199-min(safe_int(199 * values[index] / (average+1)), 199)), (x, 199)), fill=(int(color[0] * 255), int(color[1] * 255), int(color[2] * 255), 255))

        return img
    
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.imgl = QLabel()
        self.imgl.setPixmap(Image.new('RGBA', (400, 200), (0, 0, 0, 255)).toqpixmap())
        self.imgl.setStyleSheet('border-style: solid; border-width: 4px; border-color: #AAAAAA;')
        self.addWidget(self.imgl)
    
    def refresh(self, frame: array, sample_rate: int):
        img = self.get_values_for_frame(frame)
        self.imgl.setPixmap(img.toqpixmap())

class AmplitudeEffect(QHBoxLayout):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.progress_bars: list[QProgressBar] = []

        for _ in range(9):
            self.progress_bars.append(QProgressBar())
            self.progress_bars[-1].setTextVisible(False)
            self.progress_bars[-1].setOrientation(Qt.Orientation.Vertical)
            self.addWidget(self.progress_bars[-1])

    def get_values_for_frame(self, frame: array):
        values = []
        maxim = 8732500
        f = len(frame) // 9
        for i in range(9):
            frm = i * f
            to = i * f + f
            val = 0
            for j in range(frm, to):
                val += abs(frame[j])
            values.append(val)
        for i in range(9):
            values[i] /= maxim
            values[i] *= 100
            values[i] = min(round(values[i]), 100)
        return values
    
    def refresh(self, frame: array, sample_rate: int):
        v = self.get_values_for_frame(frame)
        for i in range(9):
            self.progress_bars[i].setValue(int(v[i]))

class PreciseAmplitudeEffect(QHBoxLayout):
    @staticmethod
    def get_values_for_frame(frame: array):
        values = []
        img = Image.new('RGBA', (400, 200), (0, 0, 0, 255))
        imgdraw = ImageDraw.ImageDraw(img)
        maxim = 196700
        f = len(frame) // 400
        for x in range(400):
            val = 0
            for i in range(x*f, x*f+f):
                val += frame[i]
            values.append(val)
            
        for x in range(400):
            v = x / 400
            color = [0.6*v, 0.18 + (0.16 * v), 0.9 - (0.22 * v)]
            imgdraw.line(((x, 199-min(int(199 * values[x] / maxim), 199)), (x, 199)), fill=(int(color[0]*255), int(color[1]*255), int(color[2]*255), 255))

        return img
    
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.imgl = QLabel()
        self.imgl.setPixmap(Image.new('RGBA', (400, 200), (0, 0, 0, 255)).toqpixmap())
        self.imgl.setStyleSheet('border-style: solid; border-width: 4px; border-color: #AAAAAA;')
        self.addWidget(self.imgl)
    
    def refresh(self, frame: array, sample_rate: int):
        img = self.get_values_for_frame(frame)
        self.imgl.setPixmap(img.toqpixmap())