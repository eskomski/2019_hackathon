from pyo import *
import cv2
import numpy as np

from time import time
from random import randint

from pwm import PWM

NUM_VOICES = 3
TONIC = 69
SCALE = [0, 2, 4, 5, 7, 9, 11, 12]

IMG_DIFF_THRESHOLD = 10

BIN = [0, 1]

s = Server(audio='jack')
s.boot()
s.start()

lead_freq = SigTo(440.0)
lead_osc = LFO(lead_freq)
freq = [SigTo(440.0) for _ in range(NUM_VOICES)]
osc = [{'pwm' : PWM(freq[i]), 'tri' : LFO(freq[i], type=3)} for i in range(NUM_VOICES)]

lpf_cutoff = SigTo(1000.0, time=0.1)
lead_lpf_cutoff = SigTo(1000.0, time=0.1)

lead_lpf = Biquad(lead_osc, lead_lpf_cutoff, mul=0.4).out()

# TODO: don't do this
osclist = []
for o in osc:
    osclist += [o['pwm'], o['tri']]

lpf = Biquad(osclist, lpf_cutoff, mul=0.1).out()

# VIDEO
cap = cv2.VideoCapture(0)
cap.set(3, 320)
cap.set(4, 180)

def midi_to_hz(note):
    return np.square((note - 69.0)/12.0) * 440.0

def gen_note(octave=1):
    return midiToHz((TONIC + (12 * octave)) + SCALE[randint(0, 7)])

def gen_chord(octave=1, mode='rand'):
    chord = []

    if mode == 'rand':
        for i in range(NUM_VOICES):
            chord += [gen_note(octave)]
    else:
        print('not implemented')

    return chord

def play_chord(chord):
    for i in range(NUM_VOICES):
        freq[i].setValue(chord[i])

chord_start = time()
lead_start = chord_start

ret, frame = cap.read()
#frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
prev_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)

def to_us(delta):
    return delta * 10**6

while(True):
    ret, frame = cap.read()
    gframe = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # IMAGE GRADIENT
    sobel = cv2.Sobel(gframe, cv2.CV_8U, 1, 1, ksize=5)

    grad_variance = np.var(sobel)
    filter_val = (grad_variance / 255.0) * 300.0 + 300.0

    lpf_cutoff.setValue(float(filter_val))

    # MOVEMENT
    diff = np.abs(np.float32(cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)) - np.float32(prev_frame))
    diff = np.uint8(cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY))

    perc_changed = np.mean(diff > IMG_DIFF_THRESHOLD)

    # DETERMINE TIME DELTA
    end = time()
    chord_delta = to_us(end - chord_start)
    lead_delta = to_us(end - lead_start)

    if lead_delta > (3000000 / int(2**(perc_changed * 100))):
        note = gen_note(1)
        lead_start = time()
        lead_freq.setValue(note)

        if chord_delta > 3000000:
            chord = gen_chord(-1)
            chord_start = time()
            play_chord(chord)

    cv2.imshow('frame', cv2.resize(sobel, (0,0), fx=2, fy=2))
    cv2.imshow('diff', diff)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    prev_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)

cap.release()
cv2.destroyAllWindows()
