import cv2
import numpy as np
import librosa
import soundfile as sf
import math

image = cv2.imread("grad.jpg").astype(float)
image = image.reshape(-1,image.shape[2])
print(image.shape)

rate = 44100
data = np.arange(0, 2 * rate)
data = math.sin(data) * 20

print (data.shape)
librosa.output.write_wav('file.wav', data, rate)
