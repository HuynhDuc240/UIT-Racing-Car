# from driver import *
import cv2
from Lane import *
import time
# driver = DRIVER()

# driver.pca9865.setPWM(4,0,400)
count = 1
while count <=106:
    image = cv2.imread("videos/"+str(count)+".jpg")
    count+=1
    cv2.imshow("image",image)
    key = cv2.waitKey(1000)
    if key == ord('q'):
        break