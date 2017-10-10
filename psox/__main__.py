# -*- encoding: utf-8 -*-
import time
import psox

if __name__ == '__main__' :

    ukuleleChords = {
        'C' :   ('G4','C4','E4','C5'),
        'Am':   ('A4','C4','E4','A4'),
        'F' :   ('A4','C4','F4','A4'),
        'G' :   ('G4','D4','G4','B4'),
    }

    def makeChord(chord, up=False, scale=20, length=1) :
        print('#', end='', flush=True)
        notes = psox.core.synth(ukuleleChords,'pluck')[chord]

        if not up :
            _scale = [i/scale for i in range(4)]
        else :
            _scale = [i/scale for i in reversed(range(4))]

        delay = psox.Sox('delay', _scale)

        remix = psox.Sox('remix - -')
        fade = psox.Sox('fade 0', length)
        norm = psox.Sox('gain -n -1')
            
        sin = psox.SoxSource()
        sin.effects = psox.types.Sox('synth', notes, delay, remix, fade, norm)
        sin.run()

        while True :
            time.sleep(1/100)
            if sin.ready :
                break

        sin.capture()
        
        return sin.bytes

    # préparation des accords
    scale = 16
    length = .6
    
    chord_C_Down = makeChord('C', scale=scale, length=length)
    chord_C_Up = makeChord('C', up=True, scale=scale, length=length)
    chord_Am_Down = makeChord('Am', scale=scale, length=length)
    chord_Am_Up = makeChord('Am', up=True, scale=scale, length=length)
    chord_F_Down = makeChord('F', scale=scale, length=length)
    chord_F_Up = makeChord('F', up=True, scale=scale, length=length)
    chord_G_Down = makeChord('G', scale=scale, length=length)
    chord_G_Up = makeChord('G', up=True, scale=scale, length=length)

    sout = psox.SoxSink()
    sout.run()

    while True :
        if sout.running :
            break

    for n in range(2) :
        sout.write(chord_C_Down)
        sout.write(chord_C_Up)

    for n in range(2) :
        sout.write(chord_Am_Down)
        sout.write(chord_Am_Up)

    for n in range(2) :
        sout.write(chord_F_Down)
        sout.write(chord_F_Up)

    for n in range(2) :
        sout.write(chord_G_Down)
        sout.write(chord_G_Up)

    sout.close()
