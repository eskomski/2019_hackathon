from pyo import *
from pyotools import PWM
from time import time, sleep
from random import randint, choice
import cv2
import numpy as np
from utils import *
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-m', type=str, default=None)
parser.add_argument('-d', type=int, default=4)
parser.add_argument('-s', type=int, default=30)
parser.add_argument('-k', type=str, default='B')
args = parser.parse_args()

key = args.k
NUM_VOICES = 2
CHORD_DUR = args.d
IMG_DIFF_THRESHOLD = 10

s = Server(audio='jack')
s.boot()

chorus = [dict(), dict()]
cur_chorus = 0

# here is a description of what hell looks like:
for i in range(2):
    notes = [Sig(440.0) for _ in range(NUM_VOICES)]

    env = Adsr(2, 0, 1, 2, CHORD_DUR+3)

    freq = [SigTo(notes[j]) for j in range(NUM_VOICES)]

    osc = []
    for j in range(NUM_VOICES):
        osc += [PWM(freq[j], mul=env), LFO(freq[j], type=3, mul=env)]

    chorus[i] = {'notes' : notes, 'env' : env, 'freq' : freq, 'osc' : osc}

bass_amp = SigTo(0.3)
bass_freq = SigTo(440.0)
bass_osc = Sine(bass_freq, bass_amp, mul=0.2).out()

lead_amp = SigTo(0.2)
lead_freq = SigTo(440.0)
lead_osc = PWM(lead_freq, mul=lead_amp)

lead_lpf_cutoff = SigTo(1000.0, time=0.1)
lead_lpf = Biquad(lead_osc, lead_lpf_cutoff, mul=0.2)
lead = SmoothDelay(lead_lpf, CHORD_DUR / 9.0, 0.7).out()

noise_amp = SigTo(1.0)
noise = Noise(mul=noise_amp)

lfo_amp = SigTo(1.0)
lfo = Sine(0.5, add=0.5, mul=lfo_amp)

lpf_cutoff = SigTo(1000.0, time=0.1)
lpf_reso = SigTo(1.0, time=0.1)
lpf = Biquad(chorus[0]['osc'] + chorus[1]['osc'] + [noise], lpf_cutoff + lfo * 10, lpf_reso, mul=0.1).out()

# VIDEO
if args.m is not None:
    cap = cv2.VideoCapture(args.m)
else:
    cap = cv2.VideoCapture(0)
    cap.set(3, 320)
    cap.set(4, 180)

chord_start = time()
lead_start = chord_start

ret, frame = cap.read()
prev_frame = cv2.resize(frame, (320, 180))

def to_us(delta):
    return delta * 10**6

def to_ms(delta):
    return delta * 10**3

def play_chord(chord, chorus):
    for i in range(len(chord)):
        chorus['notes'][i].setValue(chord[i])
    chorus['env'].play()

# set initial lead
chord = get_chord(None, key=key)
note = midify([chord[1]], key=key)[0]
lead_freq.setValue(note)

# set initial chord
fifth = midify(chord[::2], key=key)
prev_chord = chord
play_chord(fifth, chorus[cur_chorus])
bass_freq.setValue(fifth[0] / 2)

s.start()

# MAIN LOOP
while(True):
    frame_start = time()
    ret, frame = cap.read()

    if not ret: break

    sframe = cv2.resize(frame, (320, 180))
    gframe = cv2.cvtColor(sframe, cv2.COLOR_BGR2GRAY)

    # IMAGE GRADIENT
    sobel = cv2.Sobel(gframe, cv2.CV_8U, 1, 1, ksize=5)
    grad_variance = np.var(sobel)
    filter_val = (grad_variance / 255.0) * 200.0 + 300.0

    lpf_cutoff.setValue(float(filter_val))
    lfo_amp.setValue(float(grad_variance / 255.0))

    # BRIGHTNESS
    brightness = (float(np.sum(sframe) / sframe.size) / 255.0)
    lpf_reso.setValue(brightness * 5)
    lead_amp.setValue(brightness * 0.7 + 0.05)
    lead_lpf_cutoff.setValue(brightness * 2000.0 + 2800.0)
    bass_amp.setValue(brightness * 0.3)
    noise_amp.setValue(brightness * 0.3)

    # MOVEMENT
    diff = np.abs(np.float32(sframe) - np.float32(prev_frame))
    diff = np.uint8(cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY))
    perc_changed = float(np.mean(diff > IMG_DIFF_THRESHOLD))

    lead_freq.setValue(note - 25 * perc_changed)

    # DETERMINE TIME DELTA
    end = time()
    chord_delta = to_us(end - chord_start)
    lead_delta = to_us(end - lead_start)

    # DIVIDE MEASURES INTO NOTES FOR LEAD
    exp = 2 ** int((np.log((perc_changed / 0.35) + 1) / np.log(2)) * 5)
    if lead_delta > (CHORD_DUR * 10**6 / exp):
        note = midify([choice(chord)], key=key, octave=[-1, 0][perc_changed > 0.3 and randint(0, 1)])[0]
        lead_start = time()
        lead_freq.setValue(note)

        if chord_delta > CHORD_DUR * 10**6:
            cur_chorus = int(not cur_chorus)
            chord = get_chord(prev_chord, key=key)
            fifth = midify(chord[::2], key=key)
            prev_chord = chord
            chord_start = time()
            play_chord(fifth, chorus[cur_chorus])
            bass_freq.setValue(fifth[0] / 2)

    cv2.imshow('sobel', sobel)
    cv2.imshow('diff', diff)
    cv2.imshow('image', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    prev_frame = sframe

    if args.m is not None:
        wait_time = (1./args.s) - (time() - frame_start)
        if wait_time > 0: sleep(wait_time)


s.stop()
cap.release()
cv2.destroyAllWindows()

