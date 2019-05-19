import cv2
import numpy as np 
from keras.models import load_model
import tensorflow as tf
model = load_model('model_autocar.h5')
graph = tf.get_default_graph()
# def get_threshold():
#     ilowH = cv2.getTrackbarPos('lowH', 'lower')
#     ihighH = cv2.getTrackbarPos('highH', 'upper')
#     ilowS = cv2.getTrackbarPos('lowS', 'lower')
#     ihighS = cv2.getTrackbarPos('highS', 'upper')
#     ilowV = cv2.getTrackbarPos('lowV', 'lower')
#     ihighV = cv2.getTrackbarPos('highV', 'upper')
#     return np.array([ilowH,ilowS,ilowV]),np.array([ihighH,ihighS,ihighV])
class TRAFFIC_SIGN():

    def __init__(self):
        self.image = None
        self.prediction = -1
    
    def detect_ts(self,image):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lower1, upper1 = np.array([78,102,43]), np.array([125,255,255])
        lower2, upper2 = np.array([74,105,103]), np.array([182,213,195])
        mask_1 = cv2.inRange(hsv, lower1,upper1) # lower range red
        mask_2 = cv2.inRange(hsv, lower2, upper2) # upper range blue
        mask_r = cv2.bitwise_or(mask_1,mask_2)
        blur = cv2.GaussianBlur(mask_r, (9,9), 0)
        edge_img = cv2.Canny(blur, 200, 255)    
        _,cnts,_ = cv2.findContours(edge_img.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # img2 = img.copy()
        # cv2.drawContours(img2,cnts, -1, (0,255,0), 2)
        x_min, y_min, h_max,w_max = 1000,1000,0,0
        if len(cnts)==0:
            return 
        for cnt in cnts:
            area = cv2.contourArea(cnt) # define area contour
            if area < 100:
                continue
            # elip = cv2.fitEllipse(cnt)
            # cv2.ellipse(img2, elip, (0, 255, 0), 2)
            x,y,w,h = cv2.boundingRect(cnt)
            if x < x_min:
                x_min = x
            if y < y_min:
                y_min = y
            if h_max < h:
                h_max = h
            if w_max < w:
                w_max = w
            # h_max+=h
            # w_max+=w
            # cv2.rectangle(img2,(x,y),(x+w,y+h),(0,255,0),3)
        # h_max = h_max / len(cnts) * 2
        # w_max = w_max / len(cnts) * 2
        if x_min == 1000 and y_min == 1000 and h_max == 0 and w_max ==0:
            return None
        if h_max < 32 and w_max < 32:
            return
        self.image = image[y_min:y_min+h_max,x_min:x_min+w_max,:]
            # cv2.imwrite("image.jpg",self.image)
        cv2.imshow('traffic sign', self.image)

    def predict(self):
        if self.image is None:
            self.prediction = -1
            return
        traffic_sign = np.asarray(self.image)
        traffic_sign = cv2.resize(traffic_sign, (32,32))
        # convert to Gray
        traffic_sign = cv2.cvtColor(traffic_sign, cv2.COLOR_BGR2GRAY)
        traffic_sign = cv2.equalizeHist(traffic_sign)
        traffic_sign = traffic_sign/225
        traffic_sign = traffic_sign.reshape(1,32,32,1)
        #perdict
        ### add code here
        with graph.as_default():
            prediction = model.predict_classes(traffic_sign)
        self.prediction = prediction[0]

        


