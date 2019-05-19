import cv2
import numpy as np
import glob
import matplotlib.pyplot as plt
font = cv2.FONT_HERSHEY_COMPLEX


def nothing(x):
    pass  
def create_Trackbar():
    cv2.namedWindow("lower")
    cv2.namedWindow("upper")
    # 93,89,0
    cv2.createTrackbar('lowH','lower',0,179,nothing)
    cv2.createTrackbar('highH','upper',179,179,nothing)

    cv2.createTrackbar('lowS','lower',73,255,nothing)
    cv2.createTrackbar('highS','upper',255,255,nothing)

    cv2.createTrackbar('lowV','lower',0,255,nothing)
    cv2.createTrackbar('highV','upper',255,255,nothing)
create_Trackbar()
def get_threshold():
    ilowH = cv2.getTrackbarPos('lowH', 'lower')
    ihighH = cv2.getTrackbarPos('highH', 'upper')
    ilowS = cv2.getTrackbarPos('lowS', 'lower')
    ihighS = cv2.getTrackbarPos('highS', 'upper')
    ilowV = cv2.getTrackbarPos('lowV', 'lower')
    ihighV = cv2.getTrackbarPos('highV', 'upper')
    return np.array([ilowH,ilowS,ilowV]),np.array([ihighH,ihighS,ihighV])
def main():
    while True:
        # fig, axis = plt.subplots(3, sharex=True)
        # img_org = cv2.imread(image)
        img = cv2.imread("image.jpg")
        img = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
        #_, threshold = cv2.threshold(img, lt, ht, cv2.THRESH_BINARY)
        # lower, upper = get_threshold()
        # [105,145,50]
        lower1,upper1 = np.array([97,98,67]), np.array([134,207,175])#red
        lower2,upper2 = np.array([10,147,156]), np.array([34,200,227])#blue
        red = cv2.inRange(img, lower1, upper1)
        blue = cv2.inRange(img, lower2, upper2)
        threshold = cv2.bitwise_or(blue,red)
        cv2.imshow("binary",threshold)
        kernel = np.ones((3,3),np.uint8)
        mask_b = cv2.morphologyEx(threshold, cv2.MORPH_OPEN, kernel)
        threshold = cv2.Canny(mask_b,0,255)
        _,contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        print("contours",len(contours))
        for cnt in contours:
            approx = cv2.approxPolyDP(cnt, 0.1*cv2.arcLength(cnt, True), True)
            cv2.drawContours(img, [approx], 0, (0), 5)
            x = approx.ravel()[0]
            y = approx.ravel()[1]

            if len(approx) >7:
                cv2.putText(img, "Octagonal", (x, y), font, 1, (0))
            # elif len(approx) >32:
            #     cv2.putText(img, "Circle", (x, y), font, 1, (0))
        # axis[0].imshow(img_org)
        # axis[1].imshow(img)
        # axis[2].imshow(threshold)
        # plt.show()
        cv2.imshow("shapes", img)
        cv2.imshow("Threshold", threshold)
        cv2.waitKey(1)


if __name__ == "__main__":
    main()