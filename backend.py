from io import BytesIO
from array import array
from pathlib import Path

class EventUpdater:
    def __init__(self, mainwindow) -> None:
        self.mw = mainwindow
        self.cursor = 0
    def update_event(self, data: bytes, sample_rate: int):
        frame = array('h')
        rawdata = array('h', data)
        delta = len(rawdata)
        for i in range(delta):
            if i % 2 == 0:
                frame.append(rawdata[i])
        self.mw.current_effect.refresh(frame, sample_rate)
        self.cursor += delta*2

def stream(data: BytesIO, event_updater: EventUpdater, sample_rate: int):
    required_frames = yield b""
    while True:
        required_bytes = required_frames * 2 * 2
        sample_data = data.read(required_bytes)
        if not sample_data:
            event_updater.mw.end()
            break
        if data.seek(0, 1) > event_updater.mw.files[event_updater.mw.filei][1]:
            event_updater.mw.filei += 1
            event_updater.mw.setWindowTitle(Path(event_updater.mw.files[event_updater.mw.filei][0]).name + ' - DesktopTunes')
            event_updater.mw.show_cover()
        event_updater.update_event(sample_data, sample_rate)
        required_frames = yield sample_data