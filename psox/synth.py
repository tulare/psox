# -*- encoding: utf-8 -*-

import math
from struct import pack, unpack

def sign(x) :
    return (x > 0) - (x < 0)

def synth(accords, type='pluck') :
    dicoPlucks = dict()
    for chord, notes in accords.items() :
        dicoPlucks[chord] = sum([(type, note) for note in notes],())

    return dicoPlucks

class AudioFunction(object) :
    def __init__(self, fn, *, channels=2, rate=44100, bits=16, encoding='signed') :

        self._fn = fn

        self.channels = channels
        self.rate = rate
        self.bits = bits
        self.encoding = encoding

        self.base = int( math.pow(2, bits - 1) )
        self.size = channels * bits >> 3
        self.t = 0
        self.i = 0
        self._ticks = 0

    def getsample(self, nbytes=4096) :

        buf = bytearray(nbytes)

        for i in range(0, len(buf), self.size) :
            t = self.t + math.floor(i / self.size) / self.rate
            counter = self.i + math.floor(i / self.size)

            sample = self._fn(t, counter)
            if math.isnan(sample) :
                signed = 0
            elif sample > 0 :
                signed = min(int(self.base - 1), math.floor((self.base * sample) - 1))
            else :
                signed = max(int(-self.base), math.ceil((self.base * sample) - 1))

            mono = pack('q', signed)[:(self.bits >> 3)]
            buf[i:i+self.size] = mono * self.channels

        self.i += len(buf) / self.size
        self.t += len(buf) / self.size / self.rate

        self._ticks += 1

        return buf
    
