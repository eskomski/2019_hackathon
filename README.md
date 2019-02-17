# 2019_hackathon
alright so im really tired and i intend to update this later but the code you're looking for is in videosynth.py.

videosynth.pde is our original processing implementation, which got ditched because envelope gen with pyo was easier and we managed to get it working.

pwm.py is part of the pyo-tools library by belangeo, author of pyo. it powers the pwm oscillators used in the chords and lead. we threw it in here instead of installing the whole library—we never got around to messing with duty cycle, so you could get away with using a square typed LFO (but you should find a feature and set the duty cycle and see how it sounds!)
