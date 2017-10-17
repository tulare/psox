# -*- encoding: utf-8 -*-

import os, sys

from .types import *
from .process import QueuedProcess
from subprocess import TimeoutExpired


__all__ = [ 'SoxProcess', 'Soxi', 'Play', 'Rec', 'SoxSource', 'SoxSink' ]

SOXPATH = os.environ.get('SOXPATH', '.')

ON_POSIX = 'posix' in sys.builtin_module_names

def enqueue_output(out, queue) :
    for line in iter(out.readline, b'') :
        queue.put(line)
    out.close()


class SoxProcess(QueuedProcess) :
    def __init__(self, *, inputs=None, output=None, effects=None,
                 encoding=None, hidewindow=True) :
        self.exe = (SOXPATH+'/sox',)
        self.inputs = inputs
        self.output = output
        self.effects = effects
        sox_cmd = self.exe + self.inputs + self.output + self.effects
        super().__init__(sox_cmd, encoding=encoding, hidewindow=hidewindow)

        # let a little time for the process to start
        try :
            self.communicate(timeout=.1)
        except TimeoutExpired :
            pass

    @property
    def config(self) :
        return (self.inputs, self.output, self.effects)

    @property
    def inputs(self) :
        return self.__inputs

    @inputs.setter
    def inputs(self, inputs) :
        self.__inputs = Sox(inputs)

    @property
    def output(self) :
        return self.__output

    @output.setter
    def output(self, output) :
        self.__output = Sox(output)

    @property
    def effects(self) :
        return self.__effects

    @effects.setter
    def effects(self, effects) :
        self.__effects = Sox(effects)


class Soxi(SoxProcess) :
    '''
    Soxi
    '''
    def __init__(self, *, inputs=None, options=None, encoding=None) :
        super().__init__(
            inputs=Sox('--info'),
            output=options,
            effects=inputs,
            encoding=encoding
            )


class Play(SoxProcess) :
    '''
    Play
    '''
    def __init__(self, *, inputs, device=Device() ,effects=None, encoding=None) :
        super().__init__(
            inputs=inputs,
            output=device,
            effects=effects,
            encoding=encoding
            )


class Rec(SoxProcess) :
    '''
    Rec
    '''
    def __init__(self, *, output, device=Device(), effects=None, encoding=None) :
        super().__init__(
            inputs=device,
            output=output,
            effects=effects,
            encoding=encoding
            )


class SoxSource(SoxProcess) :
    '''
    SoxSource
    '''
    def __init__(self, *, inputs=Null(), output=RawPipe(), effects=None, encoding=None) :
        super().__init__(
            inputs=inputs,
            output=output,
            effects=effects,
            encoding=encoding
            )
        

class SoxSink(SoxProcess) :
    '''
    SoxSink
    '''
    def __init__(self, *, inputs=RawPipe(), output=Device(), effects=None, encoding=None) :
        super().__init__(
            inputs=inputs,
            output=output,
            effects=effects,
            encoding=encoding
        )
