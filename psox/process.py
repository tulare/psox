# -*- encoding: utf-8 -*-

import sys, os
import time
import inspect
from subprocess import Popen, PIPE
from threading import Thread
from queue import Queue, Empty

__all__ = [ 'QueuedProcess' ]

ON_POSIX = 'posix' in sys.builtin_module_names


def enqueue_output(out, queue) :
    for line in iter(out.readline, b'') :
        queue.put(line)
    out.close()


def dequeue_output(queue) :
    try :
        line = queue.get_nowait()
    except Empty :
        line = None
    return line


def wrap_methods(wrapper, target) :
    methods = inspect.getmembers(
        target,
        predicate = lambda bind : inspect.isroutine(bind) and not bind.__name__.startswith('_')
        )
    for method, bind in methods :
        if method not in wrapper.__class__.__dict__ :
            wrapper.__dict__[method] = bind
            

class QueuedProcess(object) :
    def __init__(self, args, *, encoding=None) :
        self.encoding = encoding
        self.__proc = Popen(
            args,
            bufsize=1,
            stdin=PIPE, stdout=PIPE, stderr=PIPE,
            close_fds=ON_POSIX
        )

        # thread de capture de STDOUT
        self.__stdout = b''
        self.__queueStdOut = Queue()
        self.__threadStdOut = Thread(target=enqueue_output, args=(self.__proc.stdout, self.__queueStdOut))
        self.__threadStdOut.daemon = True
        self.__threadStdOut.start()

        # thread de capture de STDERR
        self.__stderr = b''
        self.__queueStdErr = Queue()
        self.__threadStdErr = Thread(target=enqueue_output, args=(self.__proc.stderr, self.__queueStdErr))
        self.__threadStdErr.daemon = True
        self.__threadStdErr.start()

        # encapsulation des méthodes de Popen
        wrap_methods(self, self.__proc)

    @property
    def stdin(self) :
        return self.__proc.stdin
            
    @property
    def stdout(self) :
        more_data = b''.join(list(iter(lambda : dequeue_output(self.__queueStdOut), None)))
        self.__stdout = b''.join((self.__stdout, more_data))
        return self.__stdout if not self.encoding else self.__stdout.decode(self.encoding)

    @property
    def stderr(self) :
        more_data = b''.join(list(iter(lambda : dequeue_output(self.__queueStdErr), None)))
        self.__stderr = b''.join((self.__stderr, more_data))
        return self.__stderr if not self.encoding else self.__stderr.decode(self.encoding)

    @property
    def returncode(self) :
        return self.__proc.returncode

    @property
    def args(self) :
        return self.__proc.returncode

    def communicate(self, input=None, timeout=None) :
        # envoi des données
        if self.poll() is None and input is not None :
            self.stdin.write(input)
            self.stdin.flush()

        # attente avec timeout éventuel et retour
        self.wait(timeout)
        return (self.stdout, self.stderr)
