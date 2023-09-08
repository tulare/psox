from .helpers import is_iterable, get_short_path_name

__all__ = [ 'Sox', 'File', 'NewFile', 'RawFile', 'Null', 'Device', 'Pipe', 'RawPipe' ]


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
        elif is_iterable(elems[0]) :
            t = Sox(*elems[0])

        # head autre => conversion en chaîne
        else :
            t = str(elems[0]).split()

        return tuple.__new__(cls, tuple(t))

    def __repr__(self) :
        return self.__class__.__name__ + '(' + ','.join(self) + ')'

    def __str__(self) :
        return ' '.join(str(e) for e in self)

class Device(Sox) :
    ''' Device(fmt='waveaudio')
    '''
    def __new__(cls, fmt=None) :
        dev_fmt = Sox('-t', fmt) if fmt else Sox('-d')
        return Sox.__new__(cls, dev_fmt)

class File(Sox) :
    ''' File(file, fmt=None, options=None)
    '''
    def __new__(cls, file, fmt=None, options=None) :
        sox_fmt = Sox() if fmt is None else Sox('-t', fmt)
        if file not in ('-','-n') :
            try :
                fd = open(file, 'r')
                fd.close()
                file = get_short_path_name(file)
            except PermissionError as e :
                print(e)
                file = '-n'
            except FileNotFoundError as e :
                print(e)
                file = '-n'
        return Sox.__new__(cls, options, sox_fmt, file)

class NewFile(File) :
    ''' NewFile(file, overwrite=False, fmt=None, options=None)
    '''
    def __new__(cls, file, overwrite=False, fmt=None, options=None) :
        if file not in ('-', '-n') :            
            mode = 'w' if overwrite else 'x'
            try :
                fd = open(file, mode)
                fd.close()
            except PermissionError as e :
                print(e)
                file = '-n'
            except FileExistsError as e :
                print(e)
                file = '-n'
        return File.__new__(cls, file=file, fmt=fmt, options=options)
        

class RawFile(File) :
    ''' RawFile(file, channels=2, rate=44100, bits=16, encoding='signed')
    '''
    def __new__(cls, file, channels=2, rate=44100, bits=16, encoding='signed') :
        opts = Sox(
            '-c', channels,
            '-b', bits,
            '-r', rate,
            '-e', encoding
        )
        return File.__new__(cls, file=file, fmt='raw', options=opts)

class Null(File) :
    ''' Null(options=None)
    '''
    def __new__(cls, options=None) :
        return File.__new__(cls, file='-n', fmt=None, options=options)

class Pipe(File) :
    ''' Pipe(fmt='sox', options=None)
    '''
    def __new__(cls, fmt='sox', options=None) :
        return File.__new__(cls, file='-', fmt=fmt, options=options)


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
        return Pipe.__new__(cls, fmt='raw', options=opts)
