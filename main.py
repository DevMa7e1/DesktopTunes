from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QFontDatabase
import miniaudio
from mutagen import flac, id3
import sys
from pathlib import Path
from PIL import Image
from io import BytesIO
import effects
import backend

app = QApplication(sys.argv)

class MainWindow(QMainWindow):
    def __init__(self, /, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle('DesktopTunes')
        
        mainbox = QHBoxLayout()
        mainbox.setContentsMargins(8, 4, 4, 4)
        mainbox.setAlignment(Qt.AlignmentFlag.AlignTop)
        maincontainer = QWidget()
        maincontainer.setLayout(mainbox)

        buttons = QVBoxLayout()
        buttons.setContentsMargins(4, 8, 4, 8)
        buttons.setAlignment(Qt.AlignmentFlag.AlignLeft)

        pickbtn = QPushButton()
        pickbtn.setText('Open')
        pickbtn.pressed.connect(self.open)
        buttons.addWidget(pickbtn)

        self.playbtn = QPushButton()
        self.playbtn.setText('Play')
        self.playbtn.pressed.connect(self.play)
        buttons.addWidget(self.playbtn)

        self.stopbtn = QPushButton()
        self.stopbtn.setText('Stop')
        self.stopbtn.pressed.connect(self.stop)
        buttons.addWidget(self.stopbtn)

        self.coverl = QLabel()
        self.coverl.setPixmap(Image.new('RGBA', (100, 100), (255, 255, 255, 255)).toqpixmap())
        buttons.addWidget(self.coverl)

        self.current_effect = effects.PreciseFrequencyEffect(self)
        self.current_effect.setContentsMargins(0, 0, 0, 0)
        effect_container = QWidget()
        effect_container.setStyleSheet('border-style: solid; border-width: 4px; border-color: #AAAAAA;')
        effect_container.setLayout(self.current_effect)
        mainbox.addWidget(effect_container, alignment=Qt.AlignmentFlag.AlignCenter)

        mainbox.addLayout(buttons)

        self.setCentralWidget(maincontainer)

        self.playing = False
        self.ended = False
        self.data_stream = BytesIO()
        self.files = []
        self.filei = 0

        self.event_updater = backend.EventUpdater(self)

    def end(self):
        self.ended = True
        self.playing = False
        self.playbtn.setText('Play')

    def init(self):
        if self.ended:
            self.audio_device.stop()
            self.audio_device.close()
            self.ended = False
        self.event_updater.cursor = 0
        self.playing = False
        self.audio_device = miniaudio.PlaybackDevice(miniaudio.SampleFormat.SIGNED16, 2, 48000, buffersize_msec=100)
        self.stream = backend.stream(self.data_stream, self.event_updater, 48000)
        self.stream.send(None)
        
    def play(self):
        if not self.ended:
            if not self.playing:
                self.playbtn.setText('Pause')
                self.playing = True
                self.audio_device.start(self.stream)
            else:
                self.playbtn.setText('Play')
                self.playing = False
                self.audio_device.stop()

    def stop(self):
        if not self.ended:
            self.playing = False
            self.playbtn.setText('Play')
            self.audio_device.stop()
            self.audio_device.close()
            self.data_stream.seek(0)
            self.init()

    def show_cover(self):
        match miniaudio.get_file_info(self.files[self.filei][0]).file_format.name:
            case 'FLAC':
                self.information = flac.FLAC(self.files[self.filei][0])
                if len(self.information.pictures) > 0:
                    flacpic: flac.Picture = self.information.pictures[0]
                    img = Image.open(BytesIO(flacpic.data))
                    img = img.resize([100, int(100 / img.width * img.height)])
                    self.coverl.setPixmap(img.toqpixmap())
                else:
                    self.coverl.setPixmap(Image.new('RGBA', (100, 100), (255, 255, 255, 255)).toqpixmap())
            case 'MP3':
                self.information = id3.ID3(self.files[self.filei][0])
                if 'APIC:' in self.information.keys():
                    mp3pic = self.information['APIC:']
                    img = Image.open(BytesIO(mp3pic.data))
                    img = img.resize([100, int(100 / img.width * img.height)])
                    self.coverl.setPixmap(img.toqpixmap())
                else:
                    self.coverl.setPixmap(Image.new('RGBA', (100, 100), (255, 255, 255, 255)).toqpixmap())
            case _:
                self.coverl.setPixmap(Image.new('RGBA', (100, 100), (255, 255, 255, 255)).toqpixmap())
    
    def open(self):
        fd = QFileDialog()
        names = fd.getOpenFileNames(self, 'Open an audio file', filter='Audio files (*.wav *.flac *.mp3 *.ogg)')
        if len(names[0]) > 0:
            self.data_stream.close()
            self.data_stream = BytesIO()
            self.files.clear()
            self.filei = 0
            for name in names[0]:
                if name != '':
                    if not self.ended and self.playing:
                        self.stop()
                    self.setWindowTitle('DesktopTunes')
                    self.data_stream.write(miniaudio.decode_file(name, sample_rate=48000, output_format=miniaudio.SampleFormat.SIGNED16).samples.tobytes())
                    self.files.append((name, self.data_stream.seek(0, 1)))
            self.data_stream.seek(0)
            self.setWindowTitle(Path(self.files[0][0]).name + ' - DesktopTunes')
            self.show_cover()
            
            self.init()


window = MainWindow()
window.show()

app.exec()