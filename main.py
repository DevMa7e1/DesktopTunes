from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog
from PyQt6.QtCore import QTimerEvent, Qt, QTimer
from PyQt6.QtGui import QFont, QFontDatabase
import miniaudio
from mutagen import flac, id3
import sys
from pathlib import Path
from PIL import Image
from io import BytesIO
import effects

app = QApplication(sys.argv)

class EffectRefreshTimer(QTimer):
    def __init__(self, /, parent: MainWindow) -> None:
        super().__init__(parent)
        self.mw = parent
        self.selftime = 0
    def timerEvent(self, a0: QTimerEvent | None) -> None:
        self.mw.current_effect.refresh(self.mw.rawdata.samples[self.selftime*48000 : self.selftime*48000+4800])
        self.selftime += 1
        if type(a0) == QTimerEvent:
            return a0.accept()
        else:
            return None

class MainWindow(QMainWindow):
    def __init__(self, /, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle('DesktopTunes')
        
        mainbox = QVBoxLayout()
        mainbox.setAlignment(Qt.AlignmentFlag.AlignTop)
        maincontainer = QWidget()
        maincontainer.setLayout(mainbox)

        self.coverl = QLabel()
        mainbox.addWidget(self.coverl)

        buttons = QHBoxLayout()
        buttons.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.playbtn = QPushButton()
        self.playbtn.setText('Play')
        self.playbtn.pressed.connect(self.play)
        buttons.addWidget(self.playbtn)

        self.stopbtn = QPushButton()
        self.stopbtn.setText('Stop')
        self.stopbtn.pressed.connect(self.stop)
        buttons.addWidget(self.stopbtn)

        mainbox.addLayout(buttons)

        pickbtn = QPushButton()
        pickbtn.setText('Open an audio file')
        pickbtn.pressed.connect(self.open)
        mainbox.addWidget(pickbtn)

        self.current_effect = effects.FrequencyEffect(self)
        mainbox.addLayout(self.current_effect)

        self.setCentralWidget(maincontainer)

        self.playing = False
        self.file: str = None #type: ignore
        self.rawdata: miniaudio.DecodedSoundFile = None #type: ignore

        self.refresh_timer = EffectRefreshTimer(self)

    def init(self):
        self.refresh_timer.selftime = 0
        self.playing = False
        self.audio_device = miniaudio.PlaybackDevice()
        self.stream = miniaudio.stream_file(self.file)
        match miniaudio.get_file_info(self.file).file_format.name:
            case 'FLAC':
                self.information = flac.FLAC(self.file)
                if len(self.information.pictures) > 0:
                    flacpic: flac.Picture = self.information.pictures[0]
                    img = Image.open(BytesIO(flacpic.data))
                    img = img.resize([100, int(100 / img.width * img.height)])
                    self.coverl.setPixmap(img.toqpixmap())
            case 'MP3':
                self.information = id3.ID3(self.file)
                if 'APIC:' in self.information.keys():
                    mp3pic = self.information['APIC:']
                    img = Image.open(BytesIO(mp3pic.data))
                    img = img.resize([100, int(100 / img.width * img.height)])
                    self.coverl.setPixmap(img.toqpixmap())
        self.rawdata = miniaudio.decode_file(self.file, sample_rate=48000)
        
    def play(self):
        if not self.playing and self.file != None:
            self.playbtn.setText('Pause')
            self.playing = True
            self.audio_device.start(self.stream)
            self.refresh_timer.startTimer(1000, Qt.TimerType.CoarseTimer)
        elif self.file != None:
            self.refresh_timer.stop()
            self.playbtn.setText('Play')
            self.playing = False
            self.audio_device.stop()

    def stop(self):
        if self.file != None:
            self.refresh_timer.stop()
            self.playing = False
            self.playbtn.setText('Play')
            self.audio_device.close()
            self.init()

    def open(self):
        fd = QFileDialog()
        names = fd.getOpenFileNames(self, 'Open an audio file', filter='Audio files (*.wav *.flac *.mp3 *.ogg)')
        if names[0] != '':
            self.stop()
            self.file = names[0][0]
            self.setWindowTitle(Path(self.file).name + ' - DesktopTunes')
            self.init()


window = MainWindow()
window.show()

app.exec()