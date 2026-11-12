from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout, QFileDialog
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QFontDatabase, QPixmap
import miniaudio
import mutagen.flac
import sys
from pathlib import Path
from PIL import Image
from io import BytesIO

app = QApplication(sys.argv)

class MainWindow(QMainWindow):
    def __init__(self, /, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle('DesktopTunes')

        self.playing = False
        self.file = 'file.flac'
        self.init()
        
        mainbox = QVBoxLayout()
        mainbox.setAlignment(Qt.AlignmentFlag.AlignTop)
        maincontainer = QWidget()
        maincontainer.setLayout(mainbox)

        self.namel = QLabel()
        self.namel.setText('Audio file.flac')
        mainbox.addWidget(self.namel)

        self.coverl = QLabel()
        mainbox.addWidget(self.coverl)

        self.playbtn = QPushButton()
        self.playbtn.setText('Play')
        self.playbtn.pressed.connect(self.play)
        mainbox.addWidget(self.playbtn)

        self.stopbtn = QPushButton()
        self.stopbtn.setText('Stop')
        self.stopbtn.pressed.connect(self.stop)
        mainbox.addWidget(self.stopbtn)

        pickbtn = QPushButton()
        pickbtn.setText('Open an audio file')
        pickbtn.pressed.connect(self.open)
        mainbox.addWidget(pickbtn)

        self.setCentralWidget(maincontainer)

    def init(self):
        self.playing = False
        self.audio_device = miniaudio.PlaybackDevice()
        self.stream = miniaudio.stream_file(self.file)
        self.information = mutagen.flac.FLAC(self.file)
        
    def play(self):
        if not self.playing:
            self.playbtn.setText('Pause')
            self.playing = True
            self.audio_device.start(self.stream)
        else:
            self.playbtn.setText('Play')
            self.playing = False
            self.audio_device.stop()

    def stop(self):
        self.playing = False
        self.playbtn.setText('Play')
        self.audio_device.close()
        self.init()

    def open(self):
        fd = QFileDialog()
        names = fd.getOpenFileNames(self, 'Open an audio file', filter='Audio files (*.wav *.flac *.mp3)')
        if names[0] != '':
            self.stop()
            self.file = names[0][0]
            self.namel.setText(Path(self.file).name)
            self.init()


window = MainWindow()
window.show()

app.exec()