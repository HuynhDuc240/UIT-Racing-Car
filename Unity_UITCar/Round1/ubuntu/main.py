import cv2
import socket
import sys
import json
import threading
import queue
import time
from detect_traffic_sign import *
from Lane import *
rspeed = 0
speed = 0
Max_speed = 100
angle = 0
path = 'theFxUITCar_Data/Snapshots/fx_UIT_Car.png'
port = 9999
ip = str(sys.argv[1])
# flag for traffic sign
pass_loop_time = 0
flag_ts = False
status_ts = [0,0,""]
perdict = -1
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

# def processing(image):
#    global flag_ts
#    global status_ts
#    global pass_loop_time
#    global predict
#    while pass_loop_time > 0:
#       pass_loop_time -= 1
#       print(status_ts[2])
#       cv2.imshow('lane', image)
#       return status_ts[0], status_ts[1]
#    ########### TRAFFIC SIGN ###########
#    image_cp_ts = np.copy(image)
#    traffic_sign = dectect_obj(image_cp_ts)
#    if traffic_sign is not None:
#       predict = predict_obj(traffic_sign)
#       flag_ts = True
#       cv2.imshow('traffic_sign',traffic_sign)
#    if flag_ts:
#       # 0 is not turn left, 1 is not turn right, 2 is straight, -1 is None
#       if predict == 0:
#          status_ts = [0,45,"TURN RIGHT"]
#       elif predict == 1:
#          status_ts = [0,-45,"TURN LEFT"]
#       else:
#          status_ts = [70,0,"GO STRAIGHT"]
#       if check_for_time_steer(image_cp_ts):
#          flag_ts = False
#          pass_loop_time = 65
#          return status_ts[0],status_ts[1]
#    ############# LINES ####################
#    binary_image =  binary_pipeline(image)
#    bird_view, inverse_perspective_transform =  warp_image(binary_image)
#    left_fit, right_fit = track_lanes_initialize(bird_view)
#    left_fit, right_fit = check_fit_duplication(left_fit,right_fit)
#    center_fit, left_fit, right_fit = find_center_line_and_update_fit(image,left_fit,right_fit) # update left, right line
#    colored_lane, center_line = lane_fill_poly(bird_view,image,center_fit,left_fit,right_fit, inverse_perspective_transform)
#    cv2.imshow("lane",colored_lane)
#    # cv2.imshow("image_cp_ts",image_cp_ts)
#    speed_current, steer_angle = get_speed_angle(center_line)
#    if traffic_sign is None and flag_ts and (steer_angle >= 20 or steer_angle <= -20):
#       return status_ts[0], status_ts[1]
#    return int(speed_current), int(steer_angle)

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
            img = cv2.imread(path,1)
            # print('speed now is : {0}', rspeed)
            if img is not None:
               lane = Lane(img)
               lane.get_Lines()
               lane.get_center_line_unwarped()
               # lane.draw_lane()
               lane.draw_center_line()
               # print(lane.center_line)
               angle = int(errorAngle(lane.center_line))
               speed = int(calcul_speed(angle))
               # speed, angle = processing(img)
               # angle,speed = 0 ,0
               cv2.waitKey(1)
               if rspeed < 2:
                  speed = 70
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