import numpy as np 
import cv2
# from keras.models import load_model
# model = load_model('model.h5')
# def predict_obj(image):
#     traffic_sign = cv2.resize(image, (32,32))
#     # convert to Gray
#     traffic_sign = cv2.cvtColor(traffic_sign, cv2.COLOR_BGR2GRAY)
#     traffic_sign = cv2.equalizeHist(traffic_sign)
#     traffic_sign = traffic_sign/225
#     # cv2.imshow('traffic_sign', traffic_sign)
#     traffic_sign = traffic_sign.reshape(1, 32, 32, 1)
#     prediction = model.predict_classes(traffic_sign)
#     return prediction[0]

def binary_cvt(image):
    # Blue
    lower_b = np.array([0,140,200])
    upper_b = np.array([2,150,255])
    # Red
    lower_r = np.array([190,15,15])
    upper_r = np.array([210,40,40])
    R  = image[:,:,2]
    G  = image[:,:,1]
    B  = image[:,:,0]
    binary_output1 = np.zeros_like(R)
    binary_output2 = np.zeros_like(R)
    binary_output1[(R >= lower_r[0]) & (R <= upper_r[0]) & (G >= lower_r[1]) & (G <= upper_r[1]) & (B >= lower_r[2]) & (B <= upper_r[2])] = 1
    binary_output2[(R >= lower_b[0]) & (R <= upper_b[0]) & (G >= lower_b[1]) & (G <= upper_b[1]) & (B >= lower_b[2]) & (B <= upper_b[2])] = 1
    binary = cv2.bitwise_or(binary_output1,binary_output2) 
    return binary


def dectect_obj(image):
    binary_image = binary_cvt(image)
    roi = binary_image[:int(binary_image.shape[0]/2)-20,:]   
    if not np.any(roi):
        return None
    histogram_x = np.sum(roi[:,:], axis=0)
    histogram_y = np.sum(roi[:,:], axis=1)
    x_mid = np.argmax(histogram_x)
    y_mid = np.argmax(histogram_y)
    nonzero = roi.nonzero()
    nonzeroy = np.array(nonzero[0])
    nonzerox = np.array(nonzero[1])
    nwindows = 3
    window_width = np.int(roi.shape[1]/nwindows)
    win_y_low = 0
    win_y_high = roi.shape[0]
    minpix = 1000
    ts_inds = []
    good_window = []
    for window in range(nwindows):
        win_x_low = int(roi.shape[1] - (window+1)*window_width)
        win_x_high = int(roi.shape[1] - window*window_width)
        good_ts_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) & (nonzerox >= win_x_low) & (nonzerox < win_x_high)).nonzero()[0]
        if len(good_ts_inds) > 500:
            good_window.append(window)
    if len(good_window) == 0:
        return None
    x_low = int(roi.shape[1] - (good_window[len(good_window)-1]+1)*window_width)
    x_high = int(roi.shape[1] - good_window[0]*window_width)
    roi[:,0:x_low] = 0
    roi[:,x_high:roi.shape[1]-1] = 0
    #with opencv version >= 4.0
    contours,_ = cv2.findContours(roi,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    # other opencv version
    # _,contours,_ = cv2.findContours(roi,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    # cv2.drawContours(image, contours, -1, (0,255,0), 3)
    list_corner = np.array([[-1,-1]])
    for i in range(len(contours)):
        max_x_index = np.argmax(contours[i], axis=0)[0][0]
        max_y_index = np.argmax(contours[i], axis=0)[0][1]
        min_x_index = np.argmin(contours[i], axis=0)[0][0]
        min_y_index = np.argmin(contours[i], axis=0)[0][1]
        list_corner = np.append(list_corner,contours[i][max_x_index],axis=0)
        list_corner = np.append(list_corner,contours[i][max_y_index],axis=0)
        list_corner = np.append(list_corner,contours[i][min_x_index],axis=0)
        list_corner = np.append(list_corner,contours[i][min_y_index],axis=0)
    #get max and min with x,y
    list_corner = np.delete(list_corner, 0, 0)
    max_index = np.argmax(list_corner,axis=0)
    min_index = np.argmin(list_corner,axis=0)
    max_x_index = list_corner[max_index[0]][0]
    max_y_index = list_corner[max_index[1]][1]
    min_x_index = list_corner[min_index[0]][0]
    min_y_index = list_corner[min_index[1]][1] 
    dst_x  = max_x_index - min_x_index
    dst_y = max_y_index - min_y_index
    print(dst_x,dst_y)
    if abs(dst_x - dst_y) > 10:
        return None 
    point_1 = (min_x_index,min_y_index)
    point_2 = (max_x_index,max_y_index)
    cv2.rectangle(image,point_1,point_2,(0,255,0),3)
    # cv2.imshow('image',image)
    # print(max_x)
    traffic_sign = image[min_y_index:max_y_index, min_x_index: max_x_index,:]
    return traffic_sign
