from nidaqmx import Task
from nidaqmx.constants import SampleTimingType


class PulseTimeGenerator:
    def __init__(self, channel, start_src=None, retriggable=False):
        self._task = None
        self._channel = channel
        self.start_src = start_src
        self.retriggable = retriggable

    def __del__(self):
        if self._task is not None:
            self._task.close()

    def start(self,  samples, high_time, low_time, initial_delay=0):
        if self._task is not None:
            self._task.close()
        self._task = Task('timer')
        # TODO investigate how to use the retriggable
        # if self.start_src and self.retriggable:
        #     samples = 1
        #     low_time = 0

        self._timer = self._task.co_channels.add_co_pulse_chan_time(
            self._channel, high_time=high_time, low_time=low_time,
            initial_delay=initial_delay)
        self._task.timing.samp_quant_samp_per_chan = samples
        self._task.timing.samp_timing_type = SampleTimingType.IMPLICIT
        # TODO implement external start
        if self.start_src is not None:
            self._task.triggers.start_trigger.cfg_dig_edge_start_trig(
                self.start_src)
            # self._task.triggers.start_trigger.retriggerable = self.retriggable
        else:
            self._task.triggers.start_trigger.disable_start_trig()

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

