from nidaqmx import Task
from nidaqmx.stream_readers import CounterReader
import numpy as np
import threading

MAX_TIMEOUT = 0.1
MIN_TIMEOUT = 0.01


class BaseChannel:
    """
    Base class to implement a channel
    """
    def __init__(self, channel, channel_name):
        self._thread = None
        self._stop = False
        self._channel = channel
        self._data = np.zeros(0)
        self.sample_readies = 0
        self.enabled = True
        self._timeout = 0
        self._reading = False
        # Create the task
        self._task = Task('task' + channel_name)

        # Configure reader.
        self._task.in_stream.read_all_avail_samp = True
        self._reader = CounterReader(self._task.in_stream)

        # Configure timing

    def __del__(self):
        self._task.close()

    def start(self, samples, high_time):
        self._task.stop()
        self._data = np.zeros(samples)
        self.sample_readies = 0
        if high_time > MAX_TIMEOUT:
            high_time = MAX_TIMEOUT
        elif high_time < MIN_TIMEOUT:
            high_time = MIN_TIMEOUT
        self._timeout = high_time
        if not self.enabled:
            return
        if samples == 1:
            self._task.timing.samp_quant_samp_per_chan = 2
        else:
            self._task.timing.samp_quant_samp_per_chan = samples
        self._stop = False
        self._thread = threading.Thread(target=self._read, args=[samples])
        self._task.start()
        self._thread.start()
        self._reading = True

    @property
    def data(self):
        return self._data[:self.sample_readies]

    @property
    def done(self):
        if self._reading:
            return False
        else:
            return self._task.is_task_done()

    def stop(self):
        self._task.stop()
        self._stop = True
        self._reading = False
        self._thread.join()

    def _read(self, samples):
        i = 0
        while not self._stop and samples != 0:
            try:
                self._data[i] = \
                    self._reader.read_one_sample_double(timeout=self._timeout)
            except Exception:
                continue

            i += 1
            samples -= 1
            self.sample_readies += 1
        self._reading = False
        self._task.stop()
