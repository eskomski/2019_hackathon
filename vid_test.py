import cv2

vid = cv2.VideoCapture('big_buck_bunny.mp4')
success, image = vid.read()

i = 0
while success and i < 200:
    cv2.imwrite("frames/{}.jpg".format(i), image)
    success, image = vid.read()
    i += 1
