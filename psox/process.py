# -*- encoding: utf-8 -*-

import sys
import subprocess
import inspect
from threading import Thread
from queue import Queue, Empty

__all__ = [ 'QueuedPopen' ]

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


def docstring(ref) :
    def decorated(func) :
        func.__doc__ = inspect.getdoc(ref)
        return func
    return decorated

    
class Proxy(type) :
    """Proxy Abstract Metaclass"""
    
    def __new__(metacls, clsname, bases, namespace) :
        # get proxy parameter from namespace
        proxy = namespace['_proxy_class']

        # inventory proxy methods
        dict_proxy = dict(inspect.getmembers(proxy, inspect.isfunction))
        # print(clsname, 'dict_proxy', set(dict_proxy))

        # inventory bases methods and clean proxy dict
        for basecls in bases :
            for name, attr in inspect.getmembers(basecls, inspect.isroutine) :
                if dict_proxy.get(name) :
                    if dict_proxy[name].__qualname__ != attr.__qualname__ :
                        del dict_proxy[name]
            
        # filter proxy methods that aren't already in namespace
        proxied_methods = set(dict_proxy) - (set(dict_proxy) & set(namespace))
        # print('proxied_methods', proxied_methods)

        # merge namespace into proxy (namespace takes precedence over proxy)
        dict_proxy.update(namespace)

        # create the modified class
        cls = super().__new__(metacls, clsname, bases, dict_proxy)
        cls.__methods = proxied_methods
        cls.__getattribute__ = metacls.getattribute
        return cls

    @staticmethod
    def getattribute(instance, name) :
        """get direct or proxied attributes"""
        
        # avoid recursion to get proxy methods
        if name == '_Proxy__methods' :
            return object.__getattribute__(instance, name)

        # attribute directly defined in the instance ?
        if name not in instance._Proxy__methods :
            try :
                # print('direct :\t', name)
                return object.__getattribute__(instance, name)
            except AttributeError :
                pass

        # attribute defined in the proxy object ?
        # print('proxied :\t', name)
        return object.__getattribute__(instance._proxy, name)


class PopenProxy(Proxy) :
    """Proxy Metaclass for subprocess.Popen"""

    @classmethod
    def __prepare__(metacls, clsname, bases, **kwargs) :
        return { '_proxy_class' : subprocess.Popen }

    
class QueuedPopen(metaclass=PopenProxy) :

    def __init__(self, args, *, encoding=None, hidewindow=False) :
        # used to convert bytes to str
        self.encoding = encoding
        
        # set the flags to hide the process window if manded
        self.startupinfo = subprocess.STARTUPINFO()
        if hidewindow :
            self.startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        # subprocess creation
        self._proxy = self._proxy_class(
            args,
            bufsize=1,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            startupinfo=self.startupinfo,
            close_fds=ON_POSIX
        )

        # thread for queueing STDOUT
        self.__stdout = b''
        self.__queueStdOut = Queue()
        self.__threadStdOut = Thread(
            target=enqueue_output,
            args=(self._proxy.stdout, self.__queueStdOut)
        )
        self.__threadStdOut.daemon = True
        self.__threadStdOut.start()

        # thread for queueing STDERR
        self.__stderr = b''
        self.__queueStdErr = Queue()
        self.__threadStdErr = Thread(
            target=enqueue_output,
            args=(self._proxy.stderr, self.__queueStdErr)
        )
        self.__threadStdErr.daemon = True
        self.__threadStdErr.start()

    @property
    def stdout(self) :
        """get cached stdout of the subprocess as bytes"""
        # get STDOUT data from the queue and add it to cache
        more_data = b''.join(list(iter(lambda : dequeue_output(self.__queueStdOut), None)))
        self.__stdout = b''.join((self.__stdout, more_data))

        # return cached data as is if there is no encoding, else return it decoded.
        return self.__stdout

    @property
    def stderr(self) :
        """get cached stderr of the subprocess as bytes"""
        # get STDERR data from the queue and add it to cache
        more_data = b''.join(list(iter(lambda : dequeue_output(self.__queueStdErr), None)))
        self.__stderr = b''.join((self.__stderr, more_data))

        # return cached data as is if there is no encoding, else return it decoded.
        return self.__stderr

    @property
    def output(self) :
        """get output from stdout as text (use encoding)"""
        if self.encoding :
            return self.stdout.decode(self.encoding)
        return self.stdout.decode()

    @property
    def errors(self) :
        """get errors from stderr as text (use encoding)"""
        if self.encoding :
            return self.stderr.decode(self.encoding)
        return self.stderr.decode()

    @docstring(subprocess.Popen.communicate)
    def communicate(self, input=None, timeout=None) :
        # if there is input, send it if the process is alive
        if input is not None :
            self.write(input)

        # wait for process end with possibly a timeout, then return
        self.wait(timeout)
        return (self.stdout, self.stderr)

    def write(self, data) :
        """Send data to standard input of the process and flush it"""
        if self.poll() is not None :
            return 0     
        nbytes = self.stdin.write(data)
        self.stdin.flush()
        return nbytes
