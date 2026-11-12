import numpy as np
from PyQt6.QtWidgets import QProgressBar, QHBoxLayout, QWidget
from PyQt6.QtCore import Qt
from array import array

class FrequencyEffect(QHBoxLayout):
    @staticmethod
    def get_values_for_frame(frame: array):
        f = 20
        vals = abs(np.fft.fft(frame))
        intervals = [200, 400, 600, 800, 1000, 2000, 4000]
        values = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
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

        for _ in range(7):
            self.progress_bars.append(QProgressBar())
            self.progress_bars[-1].setTextVisible(False)
            self.progress_bars[-1].setOrientation(Qt.Orientation.Vertical)
            self.addWidget(self.progress_bars[-1])
    
    def refresh(self, frame: array):
        v = self.get_values_for_frame(frame)
        for i in range(7):
            self.progress_bars[i].setValue(int(v[i]))