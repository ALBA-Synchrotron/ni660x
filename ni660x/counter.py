from nidaqmx import Task
from nidaqmx.constants import TimeUnits, Edge,\
    DataTransferActiveTransferMode, SampleTimingType
from nidaqmx.stream_readers import CounterReader
import numpy as np
import threading


class PulseCounter:
    """
    Class to implement a pulse counter
    """
    def __init__(self, channel, channel_name, gate_src, timebase_src,
                 edge=Edge.RISING):
        self._thread = None
        self._stop = False
        self._channel = channel
        self._data = np.zeros(0)
        self.sample_readies = 0
        self.enabled = True
        # Create the task
        self._task = Task('task' + channel_name)

        # Add pulse width channel
        self._counter = self._task.ci_channels.add_ci_pulse_width_chan(
            channel, channel_name, units=TimeUnits.TICKS, starting_edge=edge)

        # Configure timing and data transfer mechanims
        self._task.timing.samp_timing_type = SampleTimingType.IMPLICIT
        self._counter.ci_data_xfer_mech = \
            DataTransferActiveTransferMode.INTERRUPT

        # Configure the source and the gate
        self._counter.ci_ctr_timebase_src = timebase_src
        self._counter.ci_pulse_width_term = gate_src

        # Configure reader.
        self._task.in_stream.read_all_avail_samp = True
        self._reader = CounterReader(self._task.in_stream)

    def __del__(self):
        self._task.close()

    def start(self, samples):
        self._task.stop()
        self._data = np.zeros(samples)
        self.sample_readies = 0
        if not self.enabled:
            return

        self._task.timing.samp_quant_samp_per_chan = samples
        self._stop = False
        self._thread = threading.Thread(target=self._read, args=[samples])
        self._task.start()
        self._thread.start()

    @property
    def data(self):
        return self._data[:self.sample_readies]

    @property
    def done(self):
        return self._task.is_task_done()

    def stop(self):
        self._stop = True
        self._task.stop()

    def _read(self, samples):
        i = 0
        while not self._stop and samples != 0:
            self._data[i] = self._reader.read_one_sample_double(timeout=-1)
            i += 1
            samples -= 1
            self.sample_readies += 1

        self._task.stop()
