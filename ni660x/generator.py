from nidaqmx import Task
from nidaqmx.constants import SampleTimingType


class PulseTimeGenerator:
    def __init__(self, channel, start_src=None):
        self._task = None
        self._channel = channel
        self._start_src = start_src

    def __del__(self):
        if self._task is not None:
            self._task.close()

    def start(self,  samples, high_time, low_time, initial_delay=0):
        if self._task is not None:
            self._task.close()
        self._task = Task('timer')
        self._timer = self._task.co_channels.add_co_pulse_chan_time(
            self._channel, high_time=high_time, low_time=low_time,
            initial_delay=initial_delay)
        self._task.timing.samp_quant_samp_per_chan = samples
        self._task.timing.samp_timing_type = SampleTimingType.IMPLICIT
        # TODO implement external start

        self._task.start()

    def stop(self):
        if self._task is not None:
            self._task.stop()

    @property
    def done(self):
        if self._task is not None:
            result = self._task.is_task_done()
        else:
            result = True
        return result

