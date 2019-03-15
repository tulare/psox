# -*- encoding: utf-8 -*-

__all__ = [ 'Sox', 'File', 'Null', 'Device', 'Pipe', 'RawPipe' ]

def iterable(obj) :
    try :
        iter(obj)
        return True
    except :
        return False


class Sox(tuple) :
    ''' Sox(*elems)
    '''
    def __new__(cls, *elems) :
        
        # vacuité
        if len(elems) == 0 :
            t = ()

        # réccurence : head + *tail
        elif len(elems) > 1 :
            t = Sox(elems[0]) + Sox(*elems[1:])

        # head chaîne => split en mots
        elif isinstance(elems[0], str) :
            t = elems[0].split()

        # head None => ()
        elif elems[0] is None :
            t = ()

        # head sous-séquence => récurrence *head
        elif iterable(elems[0]) :
            t = Sox(*elems[0])

        # head autre => conversion en chaîne
        else :
            t = str(elems[0]).split()

        return tuple.__new__(cls, tuple(t))

    def __repr__(self) :
        return self.__class__.__name__ + '(' + ','.join(self) + ')'

    def __str__(self) :
        return ' '.join(str(e) for e in self)


class File(Sox) :
    ''' File(file, fmt=None, options=None)
    '''
    def __new__(cls, file, fmt=None, options=None) :
        sox_fmt = Sox() if fmt is None else Sox('-t', fmt)
        return Sox.__new__(cls, options, sox_fmt, file)


class Null(File) :
    ''' Null(options=None)
    '''
    def __new__(cls, options=None) :
        return File.__new__(cls, '-n', None, options)


class Device(File) :
    ''' Device(fmt='waveaudio', options=None)
    '''
    def __new__(cls, fmt='waveaudio', options=None) :
        return File.__new__(cls, '-d', fmt, options)


class Pipe(File) :
    ''' Pipe(fmt='sox', options=None)
    '''
    def __new__(cls, fmt='sox', options=None) :
        return File.__new__(cls, '-', fmt, options)


class RawPipe(Pipe) :
    ''' RawPipe(channels=2, rate='44100', bits=16, encoding='signed')
    '''
    def __new__(cls, channels=2, rate=44100, bits=16, encoding='signed') :
        opts = Sox(
            '-c', channels,
            '-r', rate,
            '-b', bits,
            '-e', encoding
            )
        return Pipe.__new__(cls, 'raw', opts)
