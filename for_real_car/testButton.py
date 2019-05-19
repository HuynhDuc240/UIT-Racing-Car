from openni import openni2
from openni import _openni2 as c_api
from lane_lib import *
from driver import *
from traffic_sign_lib import *
import time
driver = DRIVER()
openni2.initialize()     # can also accept the path of the OpenNI redistribution
dev = openni2.Device.open_any()
rgb_stream = dev.create_color_stream()
rgb_stream.set_video_mode(c_api.OniVideoMode(pixelFormat=c_api.OniPixelFormat.ONI_PIXEL_FORMAT_RGB888, resolutionX=320, resolutionY=240, fps=30))
rgb_stream.start()
line = LINE()
ts_flag = -1
time_pass_loop = 0
angle = 0
speed = 0
start = 0

while True:
    value1  = (int)(driver.btn_start_stop.gpioGetValue())
    value2  = (int)(driver.btn_speed_plus.gpioGetValue())
    value3  = (int)(driver.btn_speed_minus.gpioGetValue())
    if value1 == 1:
        driver.led1.gpioSetValue(on)
        if start == 0:
            start = 1
        else:
            start = 0
        time.sleep(1)
    else:
        driver.led1.gpioSetValue(off)
    if value2 == 1:
        speed+=1
        print(speed)
        driver.led2.gpioSetValue(on)
        time.sleep(2)
    else:
        driver.led2.gpioSetValue(off)
    if value3 == 1:
        speed-=1
        print(speed)
        driver.led3.gpioSetValue(on)
        time.sleep(2)
    else: 
        driver.led3.gpioSetValue(off)

    if start == 1: 
        frame = rgb_stream.read_frame()
        frame_data = frame.get_buffer_as_uint16()
        bgr = np.fromstring(rgb_stream.read_frame().get_buffer_as_uint8(),dtype=np.uint8).reshape(240,320,3)
        image = cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)
        image = cv2.flip(image,1)
        ts = TRAFFIC_SIGN()
        ############ processing ##############
        if time_pass_loop == 0:
            ts_flag = -1
        if time_pass_loop > 0:
            lane = LANE(line,image)
            lane.detect_lane(ts_flag)
            angle = int(cal_Angle(lane.center_point))
            time_pass_loop -= 1
        else:
            ts.detect_ts(image)
            if ts.image is not None:
                print("Traffic Sign")
                driver.setSpeed(0)
                driver.setAngle(0)
                ts.predict()
                lane = LANE(line,image)
            ts_flag = ts.prediction
            if ts_flag != -1:
                print("ts",ts_flag)
                if ts_flag == 2: #STOP
                    break
                lane.detect_lane(ts_flag)
                angle = int(cal_Angle(lane.center_point))
                time_pass_loop = 60
            else:
                lane = LANE(line,image)
                lane.detect_lane(-1)
                angle = int(cal_Angle(lane.center_point))
        print(speed,angle)
        driver.setAngle(angle)
        driver.setSpeed(speed)
        cv2.waitKey(1)
    if start == 0:
        driver.pca9865.setPWM(4,0,306)
        # driver.setAngle(0)
        driver.pca9865.setPWM(0,0,412)
# cv2.destroyAllWindows()
openni2.unload()
