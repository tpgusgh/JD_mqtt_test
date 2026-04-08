import cv2
import numpy as np

def freecam(cam, msg):
    cam.release()
    print('\nMain Thread Finished',msg)

def getImg(cam):
    ret, frame = cam.read()
    if not ret:
        freecam(cam, 'Failed to capture image')
        exit()
    return frame

vid = cv2.VideoCapture(1)
if not vid.isOpened():
    print('Error: Could not open video stream')
    exit()

else:
    print('Video stream opened successfully')

# image 가져오기

imgTemp = getImg(vid)
width = imgTemp.shape[1]; height = imgTemp.shape[0] 

row_vector = np.arange(1, width+1)
img_x = np.tile(row_vector, (height, 1))

column_vector = np.arange(1, height+1).reshape(-1, 1)
img_y = np.tile(column_vector, (1, width))

img_X = img_x.astype(np.uint16)
img_Y = img_y.astype(np.uint16)

frameBg = getImg(vid)
frameBg = cv2.cvtColor(frameBg.copy(), cv2.COLOR_BGR2GRAY)
meanX = round(width/2); meanY = round(height/2)

while True:
    frame = getImg(vid)
    frame = cv2.cvtColor(frame.copy(), cv2.COLOR_BGR2GRAY)
    imgDiff = cv2.absdiff(frame, frameBg)
    _, imgDiff = cv2.threshold(imgDiff,128,1,cv2.THRESH_BINARY)
    maskCp = cv2.multiply(imgDiff, 255)
    imgBin16 = imgDiff.astype(np.uint16)

    img_X2 = cv2.multiply(img_X, imgBin16)
    img_Y2 = cv2.multiply(img_Y, imgBin16)

    img_X2 = img_X2.astype(np.uint16)
    img_Y2 = img_Y2.astype(np.uint16)

    count = np.count_nonzero(img_X2)


