# -*- encoding: utf-8 -*-

import os, sys

from .soxtypes import *
from .process import QueuedPopen
from subprocess import TimeoutExpired


__all__ = [ 'SoxProcess', 'Soxi', 'Play', 'Rec', 'SoxSource', 'SoxSink' ]


SOXPATH = os.environ.get('SOXPATH', '.')


class SoxProcess(QueuedPopen) :
    exe = (SOXPATH+'/sox',)
    
    def __init__(self, *, sources=None, dest=None, effects=None,
                 encoding=None, hidewindow=True) :
        self.sources = sources
        self.dest = dest
        self.effects = effects
        sox_cmd = self.exe + self.sources + self.dest + self.effects
        super().__init__(sox_cmd, encoding=encoding, hidewindow=hidewindow)

        # let a little time for the process to start
        try :
            self.wait(timeout=.1)
        except TimeoutExpired :
            pass

    @property
    def config(self) :
        return (self.sources, self.dest, self.effects)

    @property
    def sources(self) :
        return self.__sources

    @sources.setter
    def sources(self, sources) :
        self.__sources = Sox(sources)

    @property
    def dest(self) :
        return self.__dest

    @dest.setter
    def dest(self, dest) :
        self.__dest = Sox(dest)

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
    def __init__(self, *, sources=None, options=None, encoding=None) :
        super().__init__(
            sources=Sox('--info'),
            dest=options,
            effects=sources,
            encoding=encoding
            )


class Play(SoxProcess) :
    '''
    Play
    '''
    def __init__(self, *, sources, device=Device(), effects=None, encoding=None) :
        super().__init__(
            sources=sources,
            dest=device,
            effects=effects,
            encoding=encoding
            )


class Rec(SoxProcess) :
    '''
    Rec
    '''
    def __init__(self, *, dest, device=Device(), effects=None, encoding=None) :
        super().__init__(
            sources=device,
            dest=dest,
            effects=effects,
            encoding=encoding
            )


class SoxSource(SoxProcess) :
    '''
    SoxSource
    '''
    def __init__(self, *, sources=Null(), dest=RawPipe(), effects=None, encoding=None) :
        super().__init__(
            sources=sources,
            dest=dest,
            effects=effects,
            encoding=encoding
            )
        

class SoxSink(SoxProcess) :
    '''
    SoxSink
    '''
    def __init__(self, *, sources=RawPipe(), dest=Device(), effects=None, encoding=None) :
        super().__init__(
            sources=sources,
            dest=dest,
            effects=effects,
            encoding=encoding
        )
