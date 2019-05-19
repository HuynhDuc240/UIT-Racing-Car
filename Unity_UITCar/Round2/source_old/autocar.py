import cv2
import socket
import sys
import json
import threading
import queue
import numpy as np
import time
from processing_image import *

rspeed = 0
speed = 0
angle = 0
path = 'theFxUITCar_Data/Snapshots/fx_UIT_Car.png'
missing_left_before = -1 # 0 is left, 1 is right
port = 9999
ip = str(sys.argv[1])

## Function Parse to Json String
def jsonToString(speed, angle):
   jsonObject = {
      'speed': speed,
      'angle': angle,
      'request': 'SPEED',
   }
   jsonString = json.dumps(jsonObject)
   # print(jsonString)
   return jsonString



def Processing_image(img):
   global missing_left_before
   car_posx = int(img.shape[1]/2)
	# car_posy = image.shape[0] - int(0.025*image.shape[0])
   car_posy = img.shape[0] - 10
   image = np.copy(img)
   binary_image =  binary_pipeline(image)
   bird_view, inverse_perspective_transform =  warp_image(binary_image)
   left_fit, right_fit = track_lanes_initialize(bird_view)
   # print(left_fit,right_fit)
   warp, inverse = warp_image(image)
   lane_image = hsv_select(warp)
   # cv2.imshow('lane_image',lane_image)
   lane_point = get_point_in_lane(lane_image)
   # print(lane_point)
   missing_left_line_current, missing_right_line_current = check_missing_line(left_fit, right_fit,lane_point)
   center_line = []
   if missing_left_line_current:
      center_line = center_lane_in_missing_line(bird_view, right_fit,inverse_perspective_transform,missing_left_before,1)
      missing_left_before = 0
      cv2.imshow('bird', center_line)
   elif missing_right_line_current:
      center_line = center_lane_in_missing_line(bird_view, left_fit,inverse_perspective_transform,missing_left_before,0)
      missing_left_before = 1
      cv2.imshow('bird', center_line)
   else:
      colored_lane, center_line = lane_fill_poly(bird_view, image, left_fit, right_fit,inverse_perspective_transform, lane_point)
      cv2.imshow("lane",colored_lane)
      missing_left_before = -1
   x,y = find_point_center(center_line)
   center_point = []
   center_point.append(y)
   center_point.append(x)
   steer_angle = errorAngle(center_point,car_posx,car_posy)/2.5
   if steer_angle >= 23 or steer_angle <= -23: # maybe turn angle 90
      if steer_angle > 0:
         cv2.waitKey(1)
         return 0,45
      else:
         cv2.waitKey(1)
         return 0,-45
   speed_current = calcul_speed(steer_angle)
   cv2.waitKey(1)
   return int(speed_current), int(steer_angle)


## Thread for Socket communication
class socketThread (threading.Thread):
   def __init__(self, threadID, sock):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.sock = sock
   def run(self):
      global speed
      global angle
      global rspeed
      while(True):
         try:
            message = jsonToString(speed, angle)
            sock.sendall(message.encode())
            data = sock.recv(100).decode('ascii')
            rspeed = int(data)
            # print(rspeed)
         except Exception as e:
            print(e)
            sys.exit(1)

         # time.sleep(2)

## Thread for Processing Image
class processThread (threading.Thread):
   def __init__(self, threadID):
      threading.Thread.__init__(self)
      self.threadID = threadID
   def run(self):
      global speed
      global angle
      while True:
         try:
            img = cv2.imread(path)
            # print('speed now is : {0}', rspeed)
            if img is not None:
               speed,angle = Processing_image(img)
               print(speed, angle)
         except Exception as e:
            print(e)
      cv2.destroyAllWindows()

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip , port))
    print("Connected to ", ip, ":", port)

    ## image processing here
except Exception as ex:
    print('error', ex)
    sys.exit()

threadSendRecv = socketThread(1, sock)
threadProcess = processThread(2)

threadSendRecv.start()
threadProcess.start()

threadProcess.join()
threadSendRecv.join()
