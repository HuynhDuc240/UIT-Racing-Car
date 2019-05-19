from traffic_sign_lib import *
ts = TRAFFIC_SIGN()
# def nothing(x):
#     pass  
# def create_Trackbar():
#     cv2.namedWindow("lower")
#     cv2.namedWindow("upper")
#     cv2.createTrackbar('lowH','lower',0,179,nothing)
#     cv2.createTrackbar('highH','upper',179,179,nothing)

#     cv2.createTrackbar('lowS','lower',0,255,nothing)
#     cv2.createTrackbar('highS','upper',255,255,nothing)

#     cv2.createTrackbar('lowV','lower',0,255,nothing)
#     cv2.createTrackbar('highV','upper',255,255,nothing)
# create_Trackbar()
image = cv2.imread("/home/huynhduc/Desktop/new_lane_detect/videos/56.jpg")
while True:
    cv2.imshow("image",image)
    ts.detect_ts(image)
    # cv2.imshow("ts",ts.image)
    ts.predict()
    print(ts.prediction)
    cv2.waitKey(1)