# -*- encoding: utf-8 -*-
import time
from psox import *
from psox.synth import build_chord
from psox.ukulele import CHORDS as ukuleleChords

if __name__ == '__main__' :

    def makeChord(chord, up=False, scale=20, length=1) :

        sin = SoxSource(
            effects = build_chord(ukuleleChords, chord, up, scale, length)
        )

        sin.communicate()
        
        return sin.stdout

    # préparation des accords
    scale = 32
    length = .3

    chords = dict()
    for chord in ukuleleChords :
        print('make', chord)
        chords[(chord, 'Down')] = makeChord(chord, scale=scale, length=length)
        chords[(chord , 'Up')] = makeChord(chord, up=True, scale=scale, length=length)
    
    sout = SoxSink()

    for n in range(2) :
        sout.stdin.write(chords[('C', 'Down')])
        sout.stdin.write(chords[('C', 'Up')])

    for n in range(2) :
        sout.stdin.write(chords[('Am', 'Down')])
        sout.stdin.write(chords[('Am', 'Up')])

    for n in range(2) :
        sout.stdin.write(chords[('F', 'Down')])
        sout.stdin.write(chords[('F', 'Up')])

    for n in range(2) :
        sout.stdin.write(chords[('G', 'Down')])
        sout.stdin.write(chords[('G', 'Up')])

    for c in chords :
        print(c)
        sout.stdin.write(chords[c])

    sout.terminate()
