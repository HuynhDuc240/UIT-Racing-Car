from keras.models import load_model
import tensorflow as tf
from processing_image import *
model = load_model('model_autocar.h5')
graph = tf.get_default_graph()
def predict_obj(image): # 0 is not turn left, 1 is not turn right, 2 is straight
    traffic_sign = np.asarray(image)
    traffic_sign = cv2.resize(traffic_sign, (32,32))
    # convert to Gray
    traffic_sign = cv2.cvtColor(traffic_sign, cv2.COLOR_BGR2GRAY)
    traffic_sign = cv2.equalizeHist(traffic_sign)
    traffic_sign = traffic_sign/225
    traffic_sign = traffic_sign.reshape(1,32,32,1)
    #perdict
    with graph.as_default():
        prediction = model.predict_classes(traffic_sign)
    return prediction[0]

def binary_cvt(image):
    # Blue
    lower_b = np.array([0,140,200])
    upper_b = np.array([2,150,255])
    # lower_b = np.array([0,50,200])
    # upper_b = np.array([20,70,255])
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
    roi = image[:int(image.shape[0]/2)-20,:]  
    binary_image = binary_cvt(roi)
    if not np.any(binary_image):
        return None
    nonzero = binary_image.nonzero()
    nonzeroy = np.array(nonzero[0])
    nonzerox = np.array(nonzero[1])
    nwindows = 9
    window_width = np.int(binary_image.shape[1]/nwindows)
    win_y_low = 0
    win_y_high = binary_image.shape[0]
    minpix = 200
    good_window = []
    for window in range(nwindows):
        win_x_low = int(binary_image.shape[1] - (window+1)*window_width)
        win_x_high = int(binary_image.shape[1] - window*window_width)
        good_ts_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) & (nonzerox >= win_x_low) & (nonzerox < win_x_high)).nonzero()[0]
        if len(good_ts_inds) > minpix:
            good_window.append(window)
    if len(good_window) == 0:
        return None
    x_low = int(binary_image.shape[1] - (good_window[len(good_window)-1]+1)*window_width)
    x_high = int(binary_image.shape[1] - good_window[0]*window_width)
    binary_image[:,0:x_low] = 0
    binary_image[:,x_high:binary_image.shape[1]-1] = 0
    # with opencv version >= 4.0
    contours,_ = cv2.findContours(binary_image,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    # other opencv version
    # _,contours,_ = cv2.findContours(binary_image,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
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
    if abs(dst_x - dst_y) > 10:
        return None  
    # cv2.rectangle(image,(min_x_index,min_y_index),(max_x_index,max_y_index),(0,255,0),3)
    traffic_sign = image[min_y_index:max_y_index, min_x_index: max_x_index,:]
    if traffic_sign.shape[0] < 32 or traffic_sign.shape[1] < 32:
        return None
    return traffic_sign
def check_for_time_steer(image):
    image_copy = image[int(image.shape[0]*(7/9)):,:,:]
    print('mode checking steer for have traffic sign is turning on')
    point_left = (0,image_copy.shape[0]-50)
    point_right = (image_copy.shape[1]-1,image_copy.shape[0]-50)
    lane_image = hsv_select(image_copy)
    lane_shadow = lane_in_shadow(image_copy)
    lane = cv2.bitwise_or(lane_image,lane_shadow)
    lane = cv2.GaussianBlur(lane,(7,7),0)
    # cv2.imshow('a',lane)
    # cv2.circle(image_copy,point_left,1,(0,0,255),8)
    # cv2.circle(image_copy,point_right,1,(0,0,255),8)
    if lane[point_left[1],point_left[0]] == 255 and lane[point_right[1],point_right[0]] == 255:
        return True
    return False
    
# def traffic_sign_processing(image):
#    traffic_sign = dectect_obj(image)
#    if traffic_sign is None:
#       return -1
#    cv2.imshow('traffic_sign_image',traffic_sign)
#    predict = predict_obj(traffic_sign)
#    return predict
# if __name__ == "__main__":
#     image = cv2.imread('camretrai.jpg')
#     # image = cv2.imread('turnright.jpg')
#     # image = cv2.imread('turnleft.jpg')
#     traffic_sign = dectect_obj(image)
#     cv2.imshow('image',traffic_sign)
#     print(predict_obj(traffic_sign))
#     cv2.waitKey()
#     pass