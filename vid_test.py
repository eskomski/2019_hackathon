import cv2
import numpy as np
import librosa
# import soundfile as sf


def main():
    vid = cv2.VideoCapture('big_buck_bunny.mp4')
    success, img = vid.read()
    frames = []

    i = 0
    while success:
        #cv2.imwrite("frames/{}.jpg".format(i), img)
        frames.append(generate_tone(1/24, 44100, img))

        success, img = vid.read()
        i += 1

    samples = np.concatenate(frames)
    librosa.output.write_wav('file.wav', samples, 44100)

# generate a tone of audio, returns the samples
def generate_tone(duration, rate, img):
    r = np.arange(0, duration * rate) 
    g = np.arange(0, duration * rate) 
    b = np.arange(0, duration * rate) 

    average = img.mean(axis=0).mean(axis=0) 

    r = np.sin(r * average[0])
    g = np.sin(g * average[1])
    b = np.sin(b * average[2])

    data = (r + b + g)  / 3

    return data

    # pixels = np.float32(img.reshape(-1, 3))

    # n_colors = 5
    # criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, .1)
    # flags = cv2.KMEANS_RANDOM_CENTERS

    # _, labels, palette = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)
    # _, counts = np.unique(labels, return_counts=True)

    # dominant = palette[np.argmax(counts)]

main()
