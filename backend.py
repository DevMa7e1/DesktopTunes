from io import BytesIO
from array import array

class EventUpdater:
    def __init__(self, mainwindow) -> None:
        self.mw = mainwindow
        self.cursor = 0
    def update_event(self, delta: int, sample_rate: int):
        frame = array('h')
        if len(self.mw.rawdata.samples) >= self.cursor+(delta*2):
            window = self.mw.rawdata.samples[self.cursor : self.cursor+(delta*2)]
            for i in range(delta * 2):
                if i % 2 == 0:
                    frame.append(window[i])
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
        event_updater.update_event(required_frames, sample_rate)
        required_frames = yield sample_data