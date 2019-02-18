from pyo import *
from random import randint, choice

from mingus.core import chords, progressions, notes

def gen_note(octave=1, TONIC=60, SCALE=[0, 2, 4, 5, 7, 9, 11, 12]):
    return midiToHz((TONIC + (12 * octave)) + SCALE[randint(0, 7)])

def gen_chord(octave=1, mode='rand', NUM_VOICES=3):
    chord = []

    if mode == 'rand':
        for i in range(NUM_VOICES):
            chord += [gen_note(octave)]
    else:
        print('not implemented')

    return chord

def gen_fifth(octave=1, prev_chord=None, TONIC=60, SCALE=[0, 2, 4, 5, 7, 9, 11, 12]):
    note = (TONIC + (12 * octave)) + SCALE[randint(0, 7)]
    if prev_chord is not None:
        prev_chord = [hzToMidi(x) for x in prev_chord]
        while note == prev_chord[0] or note == prev_chord[0] - 1:
            note = (TONIC + (12 * octave)) + SCALE[randint(0, 7)]
    fifth = note + 7
    return [midiToHz(note), midiToHz(fifth)]

def get_chord(prev_chord=None, key='A'):
    if prev_chord is None:
        return chords.tonic(key)

    hfunc = progressions.determine(prev_chord, key, True)[0]

    if hfunc == 'I':
        return choice([chords.ii(key), chords.iii(key), chords.IV(key), chords.IV7(key), chords.V(key), chords.V7(key)])
    elif hfunc == 'ii':
        return choice([chords.iii(key), chords.V(key)])
    elif hfunc == 'iii':
        return choice([chords.ii(key), chords.IV(key), chords.IV7(key), chords.vi(key)])
    elif hfunc == 'IV':
        return choice([chords.I(key), chords.ii(key), chords.iii(key), chords.V(key), chords.V7(key)])
    elif hfunc == 'V':
        return choice([chords.I(key), chords.vi(key)])
    elif hfunc == 'vi':
        return choice([chords.ii(key), chords.IV(key)])
    else:
        return chords.I(key)

def midify(chord, key='A', octave=-2):
    tonic = (60 + (12 * octave)) + notes.note_to_int(key)
    return [midiToHz(tonic + notes.note_to_int(x)) for x in chord]

