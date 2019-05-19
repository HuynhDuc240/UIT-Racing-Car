import cv2
import numpy as np
import matplotlib.pyplot as plt
import random
# from skimage import io

img = cv2.imread("3.jpg")

def imshowx(img):
    size = plt.rcParams["figure.figsize"]
    size[0] = 12
    size[1] = 4
    plt.rcParams["figure.figsize"] = size

    plt.axis("off")
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    plt.show()

def imshowgray(img):
    plt.axis("off")
    plt.imshow(img, plt.get_cmap("gray"))
    plt.show()

#imshowx(outimg)
def nothing(x):
    pass                
def create_Trackbar():
    cv2.namedWindow("lower")
    cv2.namedWindow("upper")
    cv2.createTrackbar('lowH','lower',0,360,nothing)
    cv2.createTrackbar('highH','upper',360,360,nothing)

    cv2.createTrackbar('lowS','lower',0,255,nothing)
    cv2.createTrackbar('highS','upper',255,255,nothing)

    cv2.createTrackbar('lowV','lower',0,255,nothing)
    cv2.createTrackbar('highV','upper',255,255,nothing)


def get_threshold():
    ilowH = cv2.getTrackbarPos('lowH', 'lower')
    ihighH = cv2.getTrackbarPos('highH', 'upper')
    ilowS = cv2.getTrackbarPos('lowS', 'lower')
    ihighS = cv2.getTrackbarPos('highS', 'upper')
    ilowV = cv2.getTrackbarPos('lowV', 'lower')
    ihighV = cv2.getTrackbarPos('highV', 'upper')
    return np.array([ilowH,ilowS,ilowV]),np.array([ihighH,ihighS,ihighV])

#create_Trackbar()

# while(1):
#     hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
#     cv2.imshow("hsv", hsv)
#     lower1, upper1 = get_threshold()
#     lower2, upper2 = get_threshold()
#     mask_1 = cv2.inRange(hsv, lower1,upper1) # lower range blue
#     mask_2 = cv2.inRange(hsv, lower2, upper2) # upper range blue
#     mask_r = cv2.bitwise_or(mask_1,mask_2)
#     cv2.imshow("mask1", mask_1)
#     cv2.imshow("mask2", mask_2)
#     cv2.imshow("mask", mask_r)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
lower1, upper1 = np.array([78,102,43]), np.array([125,255,255])
lower2, upper2 = np.array([74,105,103]), np.array([182,213,195])
mask_1 = cv2.inRange(hsv, lower1,upper1) # lower range red
imshowgray(mask_1)
mask_2 = cv2.inRange(hsv, lower2, upper2) # upper range blue
imshowgray(mask_2)

mask_r = cv2.bitwise_or(mask_1,mask_2)
imshowgray(mask_r)
blur = cv2.GaussianBlur(mask_r, (9,9), 0)
edge_img = cv2.Canny(blur, 200, 255)
#imshowgray(edge_img)

img2 = img.copy()
# find contours in edge image: object found should be white on black backgroud
# function have three argument: src image, contour retrieval mode, contour approximation method
im ,cnts,_ = cv2.findContours(edge_img.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cv2.drawContours(img2,cnts, -1, (0,255,0), 2)
imshowx(img2)

img2 = img.copy()
for cnt in cnts:
    area = cv2.contourArea(cnt) # define area contour
    if area < 100:
         continue
    # elip = cv2.fitEllipse(cnt)
    # cv2.ellipse(img2, elip, (0, 255, 0), 2)
    x,y,w,h = cv2.boundingRect(cnt)
    cv2.rectangle(img2,(x,y),(x+w,y+h),(0,255,0),3)

imshowx(img2)

