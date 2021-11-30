from .channel import BaseChannel


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
