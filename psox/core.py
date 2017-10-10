# -*- encoding: utf-8 -*-

import os, sys
import subprocess
from threading import Thread
from queue import Queue, Empty

from .types import *

__all__ = [ 'SoxObject', 'SoxSource', 'SoxSink' ]


SOX_EXE = 'D:/Local/Tools/sox-14.4.2/sox.exe'
os.environ['AUDIODRIVER'] = 'waveaudio'

ON_POSIX = 'posix' in sys.builtin_module_names

def enqueue_output(out, queue) :
    for line in iter(out.readline, b'') :
        queue.put(line)
    out.close()

class SoxObject(object) :
    '''
    SoxObject(inputs=None, output=None, effects=None)
    '''
    def __init__(self, *, inputs=None, output=None, effects=None) :
        self._psox = None
        self.threadStdout = None
        self.queueStdout = Queue()
        self.threadStderr = None
        self.queueStderr = Queue()
        self.flush()
        self.flush_errors()

        self.inputs = inputs
        self.output = output
        self.effects = effects

    @property
    def config(self) :
        return (self.inputs, self.output, self.effects)

    @property
    def inputs(self) :
        return self._inputs

    @inputs.setter
    def inputs(self, inputs) :
        self._inputs = Sox(inputs)

    @property
    def output(self) :
        return self._output

    @output.setter
    def output(self, output) :
        self._output = Sox(output)
    
    @property
    def effects(self) :
        return self._effects
    
    @effects.setter
    def effects(self, effects) :
        self._effects = Sox(effects)

    def get_stdout(self) :
        if self.threadStdout :
            more_data = b''.join(iter(self.read, None))
            self._data = b''.join((self._data, more_data))
            if not self.threadStdout.isAlive() :
                self.close()
        return self._data

    def get_stderr(self) :
        if self.threadStderr :
            more_errors = b''.join(iter(self.read_errors, None))
            self._errors = b''.join((self._errors, more_errors))
            if not self.threadStderr.isAlive() :
                self.close()
        return self._errors

    def capture(self) :
        if self.ready :
            self.get_stdout()
            self.get_stderr()

        return self.ready

    def flush(self) :
        self._data = b''

    def flush_errors(self) :
        self._errors = b''

    def flush_all(self) :
        self._data, self._errors = b'', b''
        
    @property
    def args(self) :
        if self.running :
            return self._psox.args

    @property
    def returncode(self) :
        if self.running :
            return self._psox.returncode

    @property
    def bytes(self) :
        return self._data

    @property
    def text(self) :
        return self._data.decode()

    @property
    def errors(self) :
        return self._errors.decode()

    def run(self) :
        # Terminer toute instance précédente
        self.close()

        # Démarrage d'une nouvelle instance
        self._psox = subprocess.Popen(
            Sox(SOX_EXE) + self.inputs + self.output + self.effects,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=1,
            close_fds=ON_POSIX
        )

        # thread de capture de STDOUT
        self.threadStdout = Thread(target=enqueue_output, args=(self._psox.stdout, self.queueStdout))
        self.threadStdout.daemon = True
        self.threadStdout.start()

        # thread de capture de STDERR
        self.threadStderr = Thread(target=enqueue_output, args=(self._psox.stderr, self.queueStderr))
        self.threadStderr.daemon = True
        self.threadStderr.start()

    @property
    def running(self) :
        return self._psox is not None and self._psox.poll() is None        

    @property
    def ready(self) :
        ready = False
        if self.threadStdout and self.threadStderr :
            ready = not(self.threadStdout.isAlive() or self.threadStderr.isAlive())
            
        return ready

    def write(self, data) :
        if self.running :
            self._psox.stdin.write(data)

    def read(self) :
        try :
            line = self.queueStdout.get_nowait()
        except Empty :
            line = None
        return line

    def read_errors(self) :
        try :
            line = self.queueStderr.get_nowait()
        except Empty :
            line = None
        return line

    def close(self) :
        if self.running :
            try :
                self._psox.terminate()
                self._psox.wait()
            except :
                pass
        self._psox = None


class SoxSource(SoxObject) :
    '''
    SoxSource(inputs=Null(), output=RawPipe(), effects=None)
    '''
    def __init__(self, *, inputs=Null(), output=RawPipe(), effects=None) :
        SoxObject.__init__(self, inputs=inputs, output=output, effects=effects)
        
class Soxi(SoxObject) :
    ''' Soxi(inputs, options=None)
    '''
    def __init__(self, *, inputs, options=None) :
        SoxObject.__init__(self, inputs=Sox('--info'), output=options, effects=inputs)
        self.run()

class SoxSink(SoxObject) :
    '''
    SoxSink(inputs=RawPipe(), output=Device(), effects=None)
    '''
    def __init__(self, *, inputs=RawPipe(), output=Device(), effects=None) :
        SoxObject.__init__(self, inputs=inputs, output=output, effects=effects)

def synth(accords, type='pluck') :
    dicoPlucks = dict()
    for chord, notes in accords.items() :
        dicoPlucks[chord] = sum([(type, note) for note in notes],())

    return dicoPlucks


    
    

