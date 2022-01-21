from xmlrpc.server import SimpleXMLRPCServer
import logging
from typing import Dict, List

import click
import yaml
from nidaqmx.system import System

from ..counter import PulseCounter
from ..generator import PulseTimeGenerator
from ..positioncapture import CapturePosition
from ..helpers import get_pfi, get_human, get_encoder_type, \
    get_encoder_z_index, get_encoder_angle_units

# TODO Implement logs
ChannelsList = List[str]
ChannelData = List[float]
ChannelsData = Dict[str, ChannelData]


class CountingApp:
    """
    Application to implement the acquisition on the beamline. It has
    multiples channels and one timer. The channels can be counter and/or
    encoder capture. The timer generate a periodic gate according to the
    acquisition parameters: high, low and delay.
    """

    def __init__(self, yaml_file: str):
        with open(yaml_file) as f:
            self.config = yaml.full_load(f)

        # Do connections
        self.system = System.local()
        if 'connections' in self.config:
            term_from = get_pfi(self.config['connections']['from'])
            terms_to = self.config['connections']['to']
            for term_to in terms_to:
                term_to = get_pfi(term_to)
                self.system.connect_terms(term_from, term_to)
                msg = f'Connect {get_human(term_from)} ({term_from}) to ' \
                      f'{get_human(term_to)} ({term_to})'
                print(msg)

        self._timer = PulseTimeGenerator(self.config['timer']['channel'])
        self._channels = {}
        if 'counters' in self.config:
            for name, config in self.config['counters'].items():
                self._channels[name] = PulseCounter(
                    config['channel'], name, get_pfi(config['gate']),
                    get_pfi(config['source']))

        if 'position_capture' in self.config:
            for name, config in self.config['position_capture'].items():
                channel = config['channel']
                trigger = get_pfi(config['trigger'])
                encoder = config['encoder']
                enc_type = get_encoder_type(encoder['type'])
                enc_z_index_phase = get_encoder_z_index(encoder['zindexphase'])
                enc_angle_unit = get_encoder_angle_units(encoder['angleunit'])
                enc_pulse_per_revolution = encoder['pulseperrevolution']
                self._channels[name] = CapturePosition(
                    channel, name, trigger, enc_type, enc_z_index_phase,
                    enc_angle_unit, enc_pulse_per_revolution)

    def __del__(self):
        term_from = get_pfi(self.config['connections']['from'])
        terms_to = self.config['connections']['to']
        for term_to in terms_to:
            term_to = get_pfi(term_to)
            self.system.disconnect_terms(term_from, term_to)
            print('Disconnect', term_from, 'to', term_to)

    def start_channels(self, names: ChannelsList, samples: int,
                       high_time: float):
        """ Method to start only the counters and encoders"""
        for name in names:
            channel = self._channels[name]
            channel.start(samples, high_time)

    def start_timer(self, samples: int, high_time: float, low_time: float,
                    initial_delay: float = 0):
        """ Method to start only the generator"""
        self._timer.start(samples, high_time, low_time, initial_delay)

    def start_all(self, samples: int, high_time: float, low_time: float,
                  initial_delay: float = 0):
        """ Method to start first the channels and after the timer
        :param samples: number of sample to acquire
        :type int
        :param high_time: pulse high time in seconds
        :type float
        :param low_time: pulse low time in seconds
        :type float
        :param initial_delay: pulse initial delay in seconds
        :type float
        """
        self.start_channels(self._channels.keys(), samples, high_time)
        self.start_timer(samples, high_time, low_time, initial_delay)

    def stop_all(self):
        self.stop_channels()
        self.stop_timer()

    def stop_timer(self):
        try:
            self._timer.stop()
        except Exception:
            pass

    def stop_channels(self, channels=[]):
        if not channels:
            channels = self._channels.values()
        for channel in channels:
            try:
                channel.stop()
            except Exception:
                pass

    def get_names(self) -> ChannelsList:
        """
        Return names for all counters and encoders
        :return: [str]
        """
        return list(self._channels.keys())

    def get_channel_data(self, name: str, start: int = 0,
                         end: int = None) -> ChannelData:
        """
        Return channel (counter or encoder) data
        :param name: counter or encoder name
        :type str
        :param start: int start index position
        :type int
        :param end: int end index position
        :type int
        :return: [float]
        """
        if end is None:
            data = self._channels[name].data[start:]
        else:
            data = self._channels[name].data[start:end]

        return data.tolist()

    def set_channels_enabled(self, names: ChannelsList = [],
                             enabled: bool = True):
        """
        Set the enabled attribute of each channel. If the channel is
        enabled it will acquire data.
        :param names: Channels names
        :type [str,]
        :param enabled: bool Enabled state for the channels
        :type bool
        :return:
        """
        if len(names) == 0:
            names = self._channels.keys()

        for name in names:
            self._channels[name].enabled = enabled

    def get_channels_enabled(self) -> Dict[str, bool]:
        """
        Return a dictionary with the value of enabled attribute for each
        channel

        :return: {str: bool}
        """
        status = {}
        for name, channel in self._channels.items():
            status[name] = channel.enabled
        return status

    def get_samples_readies(self, name: str) -> int:
        return self._channels[name].sample_readies

    def get_start_src(self) -> str:
        """
        Return start source if it is empty the external start is disabled
        """
        if self._timer.start_src is None:
            value = self._timer.start_src
        else:
            value = get_human(self._timer.start_src)
        return value

    def set_start_src(self, value: str):
        if not value or value.lower() == 'none':
            self._timer.start_src = None
            return
        self._timer.start_src = get_pfi(value)

    def set_retriggable(self, value: bool):
        self._timer.retriggable = value

    def get_retriggable(self):
        return self._timer.retriggable

    def is_done(self) -> bool:
        return self._timer.done



@click.command()
@click.option('-p', '--port', default=9000, type=click.INT)
@click.option('--log-level', 'log_level', default=logging.INFO)
@click.argument('config', type=click.STRING)
def main(port, log_level, config):
    app = CountingApp(config)
    server = SimpleXMLRPCServer(('0', port), logRequests=True,
                                allow_none=True)
    server.register_introspection_functions()
    server.register_instance(app)

    try:
        print('Use Control-C to exit')
        server.serve_forever()
    except KeyboardInterrupt:
        # TODO Improve the close
        print('Exiting...')
