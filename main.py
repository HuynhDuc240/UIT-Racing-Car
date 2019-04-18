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
port = 9999
ip = str(sys.argv[1])

# flag for turn left or right
flag_for_steer = [False,-1] 
pass_loop_time = 0
old_status = [0,0]
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
   global old_status
   global pass_loop_time
   global flag_for_steer
   global Max_speed
   if flag_for_steer[0]:
      print("Traffic Sign avaiable")
      if flag_for_steer[1] == 0 or flag_for_steer[1] == 1:
         Max_speed = 10
   else:
      Max_speed = 100
   while pass_loop_time > 0:
      pass_loop_time -= 1
      cv2.imshow('lane',image)
      cv2.waitKey(1)
      return old_status[0], old_status[1]
   image_copy = np.copy(image)
   ##### predic traffic sign avaiable 
   # 0 is not turn left, 1 is not turn right, 2 is straight, -1 is None
   predict = traffic_sign_processing(image_copy)
   if predict == 0: # Turn Right
      flag_for_steer = [True, 0]
      old_status = [0, 45]
   elif predict == 1: # Turn Left
      flag_for_steer = [True, 1]
      old_status = [0,-45]
   elif predict == 2:
      flag_for_steer = [True, 2]
      old_status = [70, 0]
   left_fit, right_fit, bird_view, ipt = line_processing(image_copy)
   if len(left_fit) == 0 or len(right_fit) == 0: # missing 2 line
      if flag_for_steer[0]: # before have traffic sign avaiable after that
         if flag_for_steer[1] == 0:
            print("Turn RIGHT with traffic sign aviable")
             ############ change for testing old value[0,45]
         elif flag_for_steer[1] == 1:
            print("Turn LEFT  with traffic sign aviable")
         elif flag_for_steer[1] == 2:
            print("GO STRAIGHT")
         flag_for_steer[0] = False
         print("Traffic Sign unavaiable")
         pass_loop_time = 70
         cv2.imshow('lane',image_copy)
         return old_status[0], old_status[1]
   center_line = draw_lane(image_copy,bird_view,left_fit,right_fit,ipt)
   speed_current, steer_angle = get_speed_angle(center_line)
   ######## bug ####################
   if steer_angle == 45 or steer_angle == -45:
      if flag_for_steer[0]: # before have traffic sign avaiable after that
         return old_status[0], old_status[1]
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
            # if rspeed >= 30:
            #    Max_speed = 0
            # else:
            #    Max_speed = 100
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