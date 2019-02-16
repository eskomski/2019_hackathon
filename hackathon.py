import cv2
import numpy as np
import librosa
import soundfile as sf
import math


def uniformity(clip):
	pass

def smooth(clip):
	pass

def brightness(pixel):
	#pitch

	brightness = 0

	for value in pixel:
		brightness =+ value

	brightness = brightness/768
	
	return brightness

def rgbAvg(image):
	#maybe weight center
	#volume
	
	count  = 0
	rgbAvg = [0,0,0]

	for pixel in image:
		count =+ 1
		rgbAvg[0] =+ pixel[0]
		rgbAvg[1] =+ pixel[1]
		rgbAvg[2] =+ pixel[2]

	rgbAvg[0] = rgbAvg[0]/count
	rgbAvg[1] = rgbAvg[1]/count
	rgbAvg[2]  = rgbAvg[2]/count
	

	return rgbAvg

def intensity(pixel):
	maximum  = 0
	minimum = 255
	
	for value in pixel:
		if value > maximum:
			maximum = value

		if value < minimum:
			minimum = value

	#intensity = max()

	return maximum/255
			
		

def main():
	clip = []
	clipAudio = []

	cap = cv2.VideoCapture('sunrise.mp4')
	success, frame = cap.read()	

	framerate = cap.get(cv2.CAP_PROP_FPS)

	while success:
		clip.append(frame)
		success, frame = cap.read()

	rate = 44100

	for image in clip:
		image = image.reshape(-1,image.shape[2])

		avg = rgbAvg(image)
		freq = brightness(avg)
		amplitude = intensity(avg)

		tone = np.arange(0, rate/framerate) * 2 * freq
		tone = np.sin(tone) * 2 * amplitude

		clipAudio.append(tone)

	clipAudio = np.concatenate(clipAudio)

	#print(framerate)
	librosa.output.write_wav('file.wav', clipAudio, rate)


main()
