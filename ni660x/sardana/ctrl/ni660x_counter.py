from xmlrpc.client import ServerProxy

import numpy
from sardana.pool.controller import CounterTimerController, Type, \
    Description, DefaultValue, Access, DataAccess, AcqSynch
from sardana import State


ALLOWED_SYNC = {AcqSynch.HardwareGate, AcqSynch.HardwareStart,
                AcqSynch.HardwareTrigger}


class NI660XRPCCounterCtrl(CounterTimerController):
    """

    """
    ctrl_properties = {
        'host': {
            Type: str, Description: 'RPC Host name'
        },
        'port': {
            Type: int,
            Description: 'RPC Port',
            DefaultValue: 9000
        },
        'channelsNames': {
            Type: str,
            Description: 'Comma separated list names from the config yaml'
        },
        'latencyTime': {
            Type: float,
            Description: 'Controller latency time',
            DefaultValue: 25e-7
        }
    }

    axis_attributes = {
        'position_capture': {
            Type: bool,
            Description: 'Attribute to define channels as Position Capture',
            DefaultValue: False,
            Access: DataAccess.ReadWrite,
        },
        'position_start': {
            Type: float,
            Description: 'Value to add to each position capture',
            Access: DataAccess.ReadWrite,
        },
        'position_formula': {
            Type: str,
            Description: 'Equation to calculate the position: keywords'
                         'pos: position captured [steps]'
                         'start: Start position attribute [user units]',
            DefaultValue: 'start + pos',
            Access: DataAccess.ReadWrite,
        }
    }

    def __init__(self, inst, props, *args, **kwargs):
        CounterTimerController.__init__(self, inst, props, *args, **kwargs)
        self.channels_names = self.channelsNames.split(",")
        self.used_channels = []
        self._latency_time = self.latencyTime
        self._channel_config = {}
        self._last_index_read = {}
        self._new_index_ready = -1
        self._first_encoder = {}
        self._start_pos = {}
        self._shape = (1,)
        self._samples = 0
        self._sscan = False
        self._high_time = 0

        try:
            self._addr = 'http://{}:{}'.format(self.host, self.port)
            self._proxy = ServerProxy(self._addr)
            self._log.debug('Connected to  %s', self._addr)
        except Exception as e:
            self._log.error('Can not connect to %s: %s', self._addr, e)
            raise RuntimeError(e)

    def AddDevice(self, axis):
        name = self.channels_names[axis-1]
        self._channel_config[name] = {
            'position_capture': False,
            'position_start': 0,
            'position_formula': 'start + pos'
        }

    def StateOne(self, axis):
        if not self._proxy.is_done():
            state = State.Moving
            status = 'The card(s) are acquiring'
        elif not self._sscan and self._samples > 1 and not self._sscan and \
            any([last_index+1 < self._samples for last_index in
                     self._last_index_read.values()]):
            state = State.Moving
            status = 'The card(s) are acquiring'
        else:
            state = State.On
            status = 'The system is ready to acquire'
        return state, status

    def PrepareOne(self, axis, value, repetitions, latency, nb_starts):
        self.used_channels.clear()
        self._last_index_read.clear()
        self._first_encoder.clear()
        self._proxy.stop_channels()
        self._high_time = value

        if self._synchronization not in ALLOWED_SYNC:
            raise ValueError('This controller only works with Hardware'
                             'syncrhonization')
        self._samples = repetitions * nb_starts
        self._sscan = False
        if nb_starts > 1:
            self._sscan = True
        self._proxy.set_channels_enabled([], False)
        self._first_start = False

    def LoadOne(self, axis, value, repetitions, latency):
        pass

    def PreStartOne(self, axis, value):
        if not self._first_start:
            name = self.channels_names[axis-1]
            self.used_channels.append(name)
            self._last_index_read[name] = -1
        return True

    def StartAll(self):
        if not self._first_start:
            self._proxy.set_channels_enabled(self.used_channels, True)
            self._first_start = True
            self._proxy.start_channels(self._samples, self._high_time)

    def ReadAll(self):
        self._new_index_ready = self._proxy.get_samples_readies() - 1

    def ReadOne(self, axis):
        name = self.channels_names[axis-1]
        last_index_read = self._last_index_read[name]
        self._log.debug('ReadOne %s new: %s, last %s', axis,
                        self._new_index_ready,
                        last_index_read)
        if self._new_index_ready <= last_index_read:
            return []

        data = numpy.array(self._proxy.get_channel_data(
            name, last_index_read + 1, self._new_index_ready+1))

        # Position Calculation
        if self._channel_config[name]['position_capture']:
            if self._last_index_read[name] == -1:
                self._first_encoder[name] = data[0]
            first_encode = self._first_encoder[name]
            data -= first_encode
            formula = self._channel_config[name]['position_formula']
            start_pos = self._channel_config[name]['position_start']
            try:
                data = eval(formula, {'pos': data, 'start': start_pos})
            except Exception as e:
                self._log.error('ReadOne(%s) Can not apply the formula: %s'
                                'Error: %s', axis, formula, e)
        if self._samples != 1:
            self._last_index_read[name] += len(data)
        self._log.debug('ReadOne %s data: %s', axis, data)
        return data.tolist()

    # Axis attributes
    def GetAxisExtraPar(self, axis, parameter):
        name = self.channels_names[axis - 1]
        parameter = parameter.lower()
        self._log.debug('GetAxisExtraPar %s %s', axis, parameter)
        if parameter in self._channel_config[name]:
            return self._channel_config[name][parameter]

    def SetAxisExtraPar(self, axis, parameter, value):
        name = self.channels_names[axis - 1]
        parameter = parameter.lower()
        if parameter in self._channel_config[name]:
            self._channel_config[name][parameter] = value

    def AbortOne(self, axis):
        self._log.debug('abort ni660x %s', axis)
        pass

