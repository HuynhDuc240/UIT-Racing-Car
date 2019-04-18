import cv2
import socket
import sys
import json
import threading
import queue
import numpy as np
import time
from processing_image import *
from detect_traffic_sign import *
rspeed = 0
speed = 0
Max_speed = 100
angle = 0
path = 'theFxUITCar_Data/Snapshots/fx_UIT_Car.png'
missing_left_before = -1 # 0 is left, 1 is right
port = 9999
ip = str(sys.argv[1])
flag_for_steer = False
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

def processing(image):
   global flag_for_steer
   # detect traffic sign
   traffic_sign_image = dectect_obj(image)
   if traffic_sign_image is None:
      if flag_for_steer:
         flag_for_steer = False   
   else:
      cv2.imshow('traffic_sign_image',traffic_sign_image)
      predict = predict_obj(traffic_sign_image)
      print(predict)
      flag_for_steer = True
   #detect line
   image_copy = np.copy(image)
   binary_image =  binary_pipeline(image_copy)
   bird_view, inverse_perspective_transform =  warp_image(binary_image)
   left_fit, right_fit = track_lanes_initialize(bird_view)
   left_fit, right_fit = check_fit_duplication(left_fit,right_fit)
   center_fit, left_fit, right_fit = find_center_line_and_update_fit(image_copy,left_fit,right_fit) # update left, right line
   colored_lane, center_line = lane_fill_poly(bird_view,image_copy,center_fit,left_fit,right_fit, inverse_perspective_transform)
   cv2.imshow("lane",colored_lane)
   # calculate speed and angle
   steer_angle =  errorAngle(center_line)
   speed_current = calcul_speed(steer_angle)
   cv2.waitKey(1)
   return int(speed_current), int(steer_angle)
   


class socketThread (threading.Thread):
   def __init__(self, threadID, sock):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.sock = sock
   def run(self):
      global speed
      global angle
      global rspeed
      global Max_speed
      while(True):
         try:
            message = jsonToString(speed, angle)
            sock.sendall(message.encode())
            data = sock.recv(100).decode('ascii')
            rspeed = int(data)
            if rspeed >= 30:
               Max_speed = 0
            else:
               Max_speed = 100
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
               speed, angle = processing(img)
               if speed > Max_speed:
                  speed = Max_speed
               print(speed, angle,rspeed)
               
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