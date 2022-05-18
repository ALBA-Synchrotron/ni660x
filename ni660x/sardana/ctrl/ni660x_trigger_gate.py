from xmlrpc.client import ServerProxy

from sardana import State
from sardana.pool.pooldefs import SynchDomain, SynchParam
from sardana.pool.controller import TriggerGateController, Type, \
    Description, DefaultValue, Access, DataAccess
from ni660x.rpc.client import get_ni_client


class NI660XRPCTriggerGateCtrl(TriggerGateController):
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
        }
    }

    axis_attributes = {
        'start_src': {
            Type: str,
            Description: 'Start trigger source',
            Access: DataAccess.ReadWrite,
        },

    }

    def __init__(self, inst, props, *args, **kwargs):
        TriggerGateController.__init__(self, inst, props, *args, **kwargs)
        try:
            self._addr = 'http://{}:{}'.format(self.host, self.port)
            self._proxy = get_ni_client(self._addr)
            self._log.debug('Connected to  %s', self._addr)
        except Exception as e:
            self._log.error('Can not connect to %s: %s', self._addr, e)
            raise RuntimeError(e)

    def StateOne(self, axis):
        if not self._proxy.is_timer_done():
            state = State.Moving
            status = 'The card(s) are acquiring'
        else:
            state = State.On
            status = 'The system is ready to acquire'
        return state, status

    def SynchOne(self, axis, configuration):
        """
        Set axis configuration.
        """

        group = configuration[0]
        delay = group[SynchParam.Delay][SynchDomain.Time]
        active = group[SynchParam.Active][SynchDomain.Time]
        total = group[SynchParam.Total][SynchDomain.Time]
        passive = total - active
        repeats = group[SynchParam.Repeats]

        self._proxy.stop_timer()

        # Check if the axis trigger generator needs a master trigger to start
        if self._proxy.get_start_src():
            # If the trigger is manage by external trigger the delay time
            # should be 0
            delay = 0
            # TODO implement the configuration of the external start

        self.high_time = active
        if passive < 1e-7:
            if repeats == 1:
                self._log.warning(
                    "using minimal passive time (1e-7 s) while requested was {}".format(passive)
                )
                passive = 1e-7
            else:
                raise ValueError(
                    "requested passive time {} s is below limit (1e7 s)".format(passive)
                )
        self.low_time = passive
        self.initial_delay = delay
        self.samples = repeats

    def PreStartOne(self, axis, value=None):
        """
        Prepare axis for generation.
        """
        self._log.debug('PreStartOne(%d): entering...' % axis)

        self._log.debug('PreStartOne(%d): leaving...' % axis)
        return True

    def StartOne(self, axis):
        """
        Start generation - start the specified channel.
        """
        self._log.debug('StartOne(%d): entering...' % axis)
        self._proxy.start_timer(self.samples, self.high_time, self.low_time,
                                self.initial_delay)
        self._log.debug('StartOne(%d): leaving...' % axis)

    def AbortOne(self, axis):
        """
        Abort generation - stop the specified channel
        """
        self._proxy.stop_timer()

    def GetAxisExtraPar(self, axis, name):
        name = name.lower()
        if name == 'start_src':
           return self._proxy.get_start_src()

    def SetAxisExtraPar(self, axis, name, value):
        self._log.debug("SetAxisExtraPar(%d, %s, %s) entering..." %
                        (axis, name, value))
        name = name.lower()
        if name == 'start_src':
            self._proxy.set_start_src(value)

    def StopOne(self, axis):
        self.AbortOne(axis)