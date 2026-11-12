import numpy as np
from PyQt6.QtWidgets import QProgressBar, QHBoxLayout, QWidget, QLabel
from PyQt6.QtCore import Qt
from array import array
from PIL import Image
import numpy as np
import math

class FrequencyEffect(QHBoxLayout):
    @staticmethod
    def get_values_for_frame(frame: array):
        f = 2
        vals = abs(np.fft.fft(frame))
        intervals = [60, 120, 240, 480, 960, 1920, 3840, 7680, 15360]
        values = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        maxim = 0

        for index in range(len(intervals)):
            interval = intervals[index]
            if index == 0:
                last = 0
            else:
                last = intervals[index-1]

            for i in range(last//f, interval//f):
                values[index] += vals[i]
                if values[index] > maxim:
                    maxim = values[index]
            values[index] = np.round(values[index])

        for i in range(len(intervals)):
            values[i] /= maxim
            values[i] *= 100
            values[i] = round(values[i])
        return values
    
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.progress_bars: list[QProgressBar] = []

        for _ in range(9):
            self.progress_bars.append(QProgressBar())
            self.progress_bars[-1].setTextVisible(False)
            self.progress_bars[-1].setOrientation(Qt.Orientation.Vertical)
            self.addWidget(self.progress_bars[-1])
    
    def refresh(self, frame: array):
        v = self.get_values_for_frame(frame)
        for i in range(9):
            self.progress_bars[i].setValue(int(v[i]))

class PreciseFrequencyEffect(QHBoxLayout):
    @staticmethod
    def get_values_for_frame(frame: array):
        vals = abs(np.fft.fft(frame))
        values = []
        img = Image.new('RGBA', (400, 200), (255, 255, 255, 255))
        maxim = 0
        for x in range(400):
            val = 0
            for i in range(x*40, x*40+40):
                val += vals[i]
                if val > maxim:
                    maxim = val
            values.append(val)

        for x in range(400):
            img.putpixel((x, int(199 * values[x]/maxim)), (0, 0, 0, 255))

        return img
    
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.imgl = QLabel()
        self.imgl.setPixmap(Image.new('RGBA', (400, 200), (255, 255, 255, 255)).toqpixmap())
        self.addWidget(self.imgl)
    
    def refresh(self, frame: array):
        img = self.get_values_for_frame(frame)
        self.imgl.setPixmap(img.toqpixmap())