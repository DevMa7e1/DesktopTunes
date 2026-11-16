from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QPushButton, \
QVBoxLayout, QHBoxLayout, QFileDialog, QMenuBar, QMenu, QLayout
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QIcon
import miniaudio
from mutagen import flac, id3
import sys
from pathlib import Path
from PIL import Image
from io import BytesIO
import effects
import backend
from functools import partial
from array import array

app = QApplication(sys.argv)

class MainWindow(QMainWindow):
    def __init__(self, /, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle('DesktopTunes')
        self.setWindowIcon(QIcon(str(Path(__file__).parent.absolute().joinpath(f'icon.png'))))
        
        mainbox = QHBoxLayout()
        mainbox.setContentsMargins(8, 4, 4, 4)
        mainbox.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.mb = mainbox
        maincontainer = QWidget()
        maincontainer.setLayout(mainbox)

        menu: QMenuBar = self.menuBar() #type: ignore
        menu.setNativeMenuBar(False)

        file_menu: QMenu = menu.addMenu('File') #type: ignore

        openf: QAction = file_menu.addAction('Open audio file(s)') #type: ignore
        openf.triggered.connect(self.open)

        close: QAction = file_menu.addAction('Exit') #type: ignore
        close.triggered.connect(self.close)
        
        audio_menu: QMenu = menu.addMenu('Media') #type: ignore

        playpause: QAction = audio_menu.addAction('Play / Pause') #type: ignore
        playpause.triggered.connect(self.play)
        audio_menu.addAction(playpause)

        stop: QAction = audio_menu.addAction('Stop') #type: ignore
        stop.triggered.connect(self.stop)
        audio_menu.addAction(stop)

        effect_menu: QMenu = menu.addMenu('Visuals') #type: ignore

        freqeffb: QAction = effect_menu.addAction('Frequency responsive (bars)') #type: ignore
        freqeffb.triggered.connect(partial(self.switch_effect, effects.FrequencyEffect))

        freqeff: QAction = effect_menu.addAction('Frequency responsive (full)') #type: ignore
        freqeff.triggered.connect(partial(self.switch_effect, effects.PreciseFrequencyEffect))

        ampleffb: QAction = effect_menu.addAction('Amplitude responsive (bars)') #type: ignore
        ampleffb.triggered.connect(partial(self.switch_effect, effects.AmplitudeEffect))

        ampleff: QAction = effect_menu.addAction('Amplitude responsive (full)') #type: ignore
        ampleff.triggered.connect(partial(self.switch_effect, effects.PreciseAmplitudeEffect))

        fade_menu: QMenu = menu.addMenu('Fading') #type: ignore
        fadetoggle: QAction = fade_menu.addAction('Enable gapless playback') #type: ignore
        tmp: QAction = fade_menu.addAction('(takes effect after opening files)') #type: ignore
        tmp.setEnabled(False)
        fadetoggle.triggered.connect(self.toggle_fade)
        self.fd = fadetoggle

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
        self.coverl.setPixmap(Image.new('RGBA', (100, 100), (0, 0, 0, 0)).toqpixmap())
        self.coverl.setFixedSize(100, 100)
        buttons.addWidget(self.coverl)

        self.hole_where_effect_goes = QHBoxLayout()
        self.hole_where_effect_goes.setContentsMargins(0, 0, 0, 0)
        self.parent_of_the_hole = QWidget()
        self.parent_of_the_hole.setLayout(self.hole_where_effect_goes)
        mainbox.addWidget(self.parent_of_the_hole)

        self.current_effect: QHBoxLayout = effects.PreciseFrequencyEffect(self)
        self.current_effect.setContentsMargins(0, 0, 0, 0)
        self.effect_container = QWidget()
        self.effect_container.setLayout(self.current_effect)
        self.hole_where_effect_goes.addWidget(self.effect_container, alignment=Qt.AlignmentFlag.AlignCenter)

        button_container = QWidget()
        button_container.setLayout(buttons)
        mainbox.addWidget(button_container)

        self.setCentralWidget(maincontainer)

        self.playing = False
        self.ended = False
        self.fade_between = True
        self.data_stream = BytesIO()
        self.files = []
        self.filei = 0

        self.event_updater = backend.EventUpdater(self)

        mainbox.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)

    def toggle_fade(self):
        if self.fade_between:
            self.fade_between = False
            self.fd.setText('Disable gapless playback')
        else:
            self.fade_between = True
            self.fd.setText('Enable gapless playback')

    def switch_effect(self, effect: type):
        self.effect_container.deleteLater()
        self.current_effect = effect()
        self.effect_container = QWidget()
        self.effect_container.setLayout(self.current_effect)
        self.current_effect.setContentsMargins(0, 0, 0, 0)
        self.hole_where_effect_goes.addWidget(self.effect_container)
        self.setFixedSize(QSize(0, 0))

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
                    self.coverl.setPixmap(Image.new('RGBA', (100, 100), (255, 255, 255, 0)).toqpixmap())
            case 'MP3':
                self.information = id3.ID3(self.files[self.filei][0])
                if 'APIC:' in self.information.keys():
                    mp3pic = self.information['APIC:']
                    img = Image.open(BytesIO(mp3pic.data))
                    img = img.resize([100, int(100 / img.width * img.height)])
                    self.coverl.setPixmap(img.toqpixmap())
                else:
                    self.coverl.setPixmap(Image.new('RGBA', (100, 100), (255, 255, 255, 0)).toqpixmap())
            case _:
                self.coverl.setPixmap(Image.new('RGBA', (100, 100), (255, 255, 255, 0)).toqpixmap())
    
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
                    if len(self.files) > 1:
                        if self.fade_between and (self.data_stream.seek(0, 1) - self.files[-2][1]) > 48000:
                            self.data_stream.seek(-48000, 2)
                            to_fade_out = array('h', self.data_stream.read())
                            for i in range(len(to_fade_out)):
                                f = 1 - i / len(to_fade_out)
                                to_fade_out[i] = int(to_fade_out[i] * f)
                            self.data_stream.seek(-48000, 2)
                            self.data_stream.write(to_fade_out.tobytes())
                    else:
                        if self.fade_between and self.data_stream.seek(0, 1) > 48000:
                            self.data_stream.seek(-48000, 2)
                            to_fade_out = array('h', self.data_stream.read())
                            for i in range(len(to_fade_out)):
                                f = 1 - i / len(to_fade_out)
                                to_fade_out[i] = int(to_fade_out[i] * f)
                            self.data_stream.seek(-48000, 2)
                            self.data_stream.write(to_fade_out.tobytes())

            self.data_stream.seek(0)
            self.setWindowTitle(Path(self.files[0][0]).name + ' - DesktopTunes')
            self.show_cover()
            
            self.init()


window = MainWindow()
window.show()

app.exec()