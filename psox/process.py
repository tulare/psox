# -*- encoding: utf-8 -*-

import sys
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


def docstring_from(base) :
    def set_docstring(f) :
        f.__doc__ = getattr(base, f.__name__).__doc__
        return f
    return set_docstring


class QueuedProcess(object) :
    def __init__(self, args, *, encoding=None) :
        self.encoding = encoding
        self.__proc = Popen(
            args,
            bufsize=1,
            stdin=PIPE, stdout=PIPE, stderr=PIPE,
            close_fds=ON_POSIX
        )

        # thread for STDOUT capture
        self.__stdout = b''
        self.__queueStdOut = Queue()
        self.__threadStdOut = Thread(target=enqueue_output, args=(self.__proc.stdout, self.__queueStdOut))
        self.__threadStdOut.daemon = True
        self.__threadStdOut.start()

        # thread for STDERR capture
        self.__stderr = b''
        self.__queueStdErr = Queue()
        self.__threadStdErr = Thread(target=enqueue_output, args=(self.__proc.stderr, self.__queueStdErr))
        self.__threadStdErr.daemon = True
        self.__threadStdErr.start()

    @property
    def stdin(self) :
        return self.__proc.stdin
            
    @property
    def stdout(self) :
        # get STDOUT data from the queue and add it to cache
        more_data = b''.join(list(iter(lambda : dequeue_output(self.__queueStdOut), None)))
        self.__stdout = b''.join((self.__stdout, more_data))

        # return cached data as is if there is no encoding, else return it decoded.
        return self.__stdout

    @property
    def stderr(self) :
        # get STDERR data from the queue and add it to cache
        more_data = b''.join(list(iter(lambda : dequeue_output(self.__queueStdErr), None)))
        self.__stderr = b''.join((self.__stderr, more_data))

        # return cached data as is if there is no encoding, else return it decoded.
        return self.__stderr

    @property
    def bytes(self) :
        return self.stdout

    @property
    def text(self) :
        if self.encoding :
            return self.stdout.decode(self.encoding)
        return self.stdout.decode()

    @property
    def errors(self) :
        if self.encoding :
            return self.stderr.decode(self.encoding)
        return self.stderr.decode()

    @property
    def pid(self) :
        return self.__proc.pid

    @property
    def returncode(self) :
        return self.__proc.returncode

    @property
    def args(self) :
        return self.__proc.args

    @docstring_from(Popen)
    def communicate(self, input=None, timeout=None) :
        # if there is input, send it if the process is alive
        if input is not None :
            self.write(input)

        # wait for process end with possibly a timeout, then return
        self.wait(timeout)
        return (self.stdout, self.stderr)

    @docstring_from(Popen)
    def kill(self) :
        return self.__proc.kill()

    @docstring_from(Popen)
    def poll(self) :
        return self.__proc.poll()

    @docstring_from(Popen)
    def send_signal(self, sig) :
        return self.__proc.send_signal(sig)

    @docstring_from(Popen)
    def terminate(self) :
        return self.__proc.terminate()

    @docstring_from(Popen)    
    def wait(self, timeout=None, endtime=None) :
        return self.__proc.wait(timeout, endtime)

    def write(self, data) :
        if self.poll() is not None :
            return 0
        
        nbytes = self.stdin.write(data)
        self.stdin.flush()

        return nbytes
    
