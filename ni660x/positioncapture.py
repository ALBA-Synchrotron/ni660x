import nidaqmx
from nidaqmx.constants import EncoderType, EncoderZIndexPhase, AngleUnits
from nidaqmx.stream_readers import CounterReader
import threading
import numpy as np
import time


class CapturePosition:

    # Builder
    def __init__(self, counter, source_trigger):
        print("Hola")
        self._task = None
        self._counter = counter
        self._source_trigger = source_trigger
        self._reader = None
        self._data = np.zeros(0)
        self._thread = None
        self._stop = False

    # Destructor
    def __del__(self):
        print("Adeu")
        self.stop()

    # Private method
    def _read(self, samples):
        print("Soy el hijo")
        i = 0
        while not self._stop and i < samples:
            print("Entro")
            # self._data[i] = self._reader.read_one_sample_double(timeout=-1)
            time.sleep(20)
            i += 1

        self._task.stop()
        self._thread = None
        self._stop = True
        print("Acabo el hijo")

    # start and stop methods
    def start(self, samples, encoder_type, encoder_zindex, angle_units):
        print("Start")
        if self._task is not None:
            self._task.close()

        self._task = nidaqmx.Task('timer')
        self._data = np.zeros(samples)
        self._task.ci_channels.add_ci_ang_encoder_chan(self._counter, "",
                                                       encoder_type, False,
                                                       0, encoder_zindex,
                                                       angle_units, 24,
                                                       0.0, "")

        self._task.timing.cfg_samp_clk_timing(1000.0, self._source_trigger,
                                              samps_per_chan=samples)
        self._reader = CounterReader(self._task.in_stream)

        self._task.start()

        self._stop = False
        self._thread = threading.Thread(target=self._read, args=[samples],
                                        daemon=True)
        self._thread.start()

    def stop(self):
        print("Stop")
        self._stop = True
        if self._task is not None:
            self._task.stop()

        if self._thread is not None:
            self._thread.kill()

    # Another methods
    @property
    def done(self):
        if self._task is not None:
            result = self._task.is_task_done()
        else:
            result = True
        return result

    @property
    def data(self):
        return self._data
