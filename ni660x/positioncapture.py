from .channel import BaseChannel
from nidaqmx.constants import AngleUnits
import math

class CapturePosition(BaseChannel):

    # Builder
    def __init__(self, channel, channel_name, source_trigger, encoder_type,
                 encoder_zindex, angle_units):
        super().__init__(channel, channel_name)
        self._source_trigger = source_trigger
        self._entype = encoder_type
        self._enzindex = encoder_zindex
        self._angunit = angle_units

        self._task.ci_channels.add_ci_ang_encoder_chan(self._channel, "",
                                                       self._entype, False,
                                                       0, self._enzindex,
                                                       self._angunit, 24,
                                                       0, "")

    def start(self, samples, high_time):
        self._task.timing.cfg_samp_clk_timing(10000.0, self._source_trigger,
                                              samps_per_chan=samples)

        super().start(samples, high_time)

    def translate(self, value):
        if self._angunit == AngleUnits.DEGREES:
            units_per_revolution = 360.0
        elif self._angunit == AngleUnits.RADIANS:
            units_per_revolution = 4 * math.acos(0.0)
        else:
            units_per_revolution = 1.0

        return value / 24 * units_per_revolution