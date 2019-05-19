
from openni import openni2
from openni import _openni2 as c_api
from Lane import *
from traffic_sign import *
import numpy as np
import cv2
from driver import DRIVER
from driver import *
import time

driver = DRIVER()
driver.turnOnLed1()
driver.turnOnLed2()
driver.turnOnLed3()

openni2.initialize()     # can also accept the path of the OpenNI redistribution
dev = openni2.Device.open_any()
print(dev.get_device_info())

rgb_stream = dev.create_color_stream()

#depth_stream = dev.create_depth_stream()
#depth_stream.start()
print('The rgb video mode is', rgb_stream.get_video_mode()) # Checks rgb video configuration
rgb_stream.set_video_mode(c_api.OniVideoMode(pixelFormat=c_api.OniPixelFormat.ONI_PIXEL_FORMAT_RGB888, resolutionX=320, resolutionY=240, fps=30))
## Start the streams
rgb_stream.start()
# def nothing(x):
#         pass  
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
while True:
   frame = rgb_stream.read_frame()
   frame_data = frame.get_buffer_as_uint16()
   bgr = np.fromstring(rgb_stream.read_frame().get_buffer_as_uint8(),dtype=np.uint8).reshape(240,320,3)
   image = cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)
   image = cv2.flip(image,1)
   # ts = traffic_sign()
   # ts.detect(image)
   # print(image.shape)
    ###############Lane################
   binary_image =  binary_pipeline(image)
   bird_view, inverse_perspective_transform =  warp_image(binary_image)
   left_fit, right_fit = track_lanes_initialize(bird_view)
   left_fit, right_fit = check_fit_duplication(left_fit,right_fit)
   center_fit, left_fit, right_fit = find_center_line_and_update_fit(image,left_fit,right_fit) # update left, right line
   colored_lane, center_line = lane_fill_poly(bird_view,image,center_fit,left_fit,right_fit, inverse_perspective_transform)
   cv2.imshow("lane",colored_lane)
   angle = int(errorAngle(center_line))
   if angle < 10 and angle > 0:
      angle = 20
   if angle >-10 and angle <0:
      angle = 20
   driver.setSpeed(2)
   driver.setAngle(angle)
    # time.sleep(0.5)
   print(angle)
    # if ts.image is None:
    #     #print("None ts")
    #     pass
    # else:
    #     cv2.imshow('image', ts.image)
    #     driver.setAngle(0)
    #     driver.setSpeed(0)
    #     break
	#depth_stream.stop()
   key = cv2.waitKey(1) 
   if key == ord('q'):
      break

openni2.unload()
cv2.destroyAllWindows()
