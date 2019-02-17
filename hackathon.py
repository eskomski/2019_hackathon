import cv2
import numpy as np
import librosa
import soundfile as sf
import math


def uniformity(clip):
	pass

def smooth(tone, time, freq):
	window = np.arange(0, time) * freq
	window = tone*window

	const = (time-1) * freq
	
	for i, value in enumerate(window):
		if 1/const < value and value < (const - 1/const):
			window[i] = 1
		elif value > (const - 1/const):
			window[i] = (-1)*(const)*value+const*const

	window = np.multiply(window, tone)

	return window

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
	
	rgbAvg = [0,0,0]
	#maxBrightness = 0

	#bias = 1
	count  = 0

	#for pixel in image:
		#if brightness(pixel) > maxBrightness:
			#brightestPixel = image[count]

		#count += 1

	for pixel in image:
		rgbAvg[0] += pixel[0]
		rgbAvg[1] += pixel[1]
		rgbAvg[2] += pixel[2]
		count += 1

	rgbAvg[0] = rgbAvg[0]/count #bias*brightestPixel[0]+(1-bias)*rgbAvg[0]/count
	rgbAvg[1] = rgbAvg[1]/count #bias*brightestPixel[1]+(1-bias)*rgbAvg[1]/count
	rgbAvg[2] = rgbAvg[2]/count #bias*brightestPixel[2]+(1-bias)*rgbAvg[2]/count

	return rgbAvg

def intensity(pixel):
	maximum  = 0
	minimum = 255
	
	for value in pixel:
		if value > maximum:
			maximum = value

		if value < minimum:
			minimum = value

	intensity = max(abs(175-minimum),abs(maximum-0))

	return intensity/255
			
		

def main():
	clip = []
	clipAudio = []

	cap = cv2.VideoCapture('sunrise.mp4')
	success, frame = cap.read()

	rate = 44100
	framerate = cap.get(cv2.CAP_PROP_FPS)
	second = rate/framerate

	while success:
		clip.append(frame)
		success, frame = cap.read()

	
	for image in clip:
		
		height, width, depth = image.shape
		imgScale = 64/width
		newX, newY = image.shape[1]*imgScale, image.shape[0]*imgScale

		image = cv2.resize(image,(int(newX), int(newY)))
		image = image.reshape(-1,image.shape[2])

		avg = rgbAvg(image)
		freq = brightness(avg)
		amplitude = intensity(avg)

		tone = np.arange(0, second) * freq
		tone = np.sin(tone) * amplitude
		tone = smooth(tone, second, freq)

		clipAudio.append(tone)

	clipAudio = np.concatenate(clipAudio)

	#print(framerate)
	librosa.output.write_wav('file.wav', clipAudio, rate)


main()
	
