from nidaqmx.constants import TimeUnits, Edge,\
    DataTransferActiveTransferMode, SampleTimingType
from .channel import BaseChannel


class PulseCounter(BaseChannel):
    """
    Class to implement a pulse counter
    """
    def __init__(self, channel, channel_name, gate_src, timebase_src,
                 edge=Edge.RISING):

        super().__init__(channel,channel_name)
        # Add pulse width channel
        self._counter = self._task.ci_channels.add_ci_pulse_width_chan(
            channel, channel_name, units=TimeUnits.TICKS, starting_edge=edge)

        # Configure timing and transfer mechanims
        self._task.timing.samp_timing_type = SampleTimingType.IMPLICIT
        self._counter.ci_data_xfer_mech = \
            DataTransferActiveTransferMode.INTERRUPT

        # Configure the source and the gate
        self._counter.ci_ctr_timebase_src = timebase_src
        self._counter.ci_pulse_width_term = gate_src


