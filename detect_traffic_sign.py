import numpy as np 
import cv2
from keras.models import load_model
model = load_model('model.h5')

def predict_obj(image):
    traffic_sign = cv2.resize(image, (32,32))
    # convert to Gray
    traffic_sign = cv2.cvtColor(traffic_sign, cv2.COLOR_BGR2GRAY)
    traffic_sign = cv2.equalizeHist(traffic_sign)
    traffic_sign = traffic_sign/225
    cv2.imshow('traffic_sign', traffic_sign)
    traffic_sign = traffic_sign.reshape(1, 32, 32, 1)
    prediction = model.predict_classes(traffic_sign)
    return prediction[0]
def dectect_obj(image):
    # Blue
    lower = np.array([0,0,190])
    upper = np.array([20,70,255])
    # Red
    # lower = np.array([200,0,0])
    # upper = np.array([255,40,40])
    R  = image[:,:,2]
    G  = image[:,:,1]
    B  = image[:,:,0]
    binary_output = np.zeros_like(R)
    binary_output[(R >= lower[0]) & (R <= upper[0]) & (G >= lower[1]) & (G <= upper[1]) & (B >= lower[2]) & (B <= upper[2])] = 255
    if not np.any(binary_output):
        return None
    contours,_ = cv2.findContours(binary_output,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    cnt = np.asarray(contours)
    list_corner = np.array([[-1,-1]])
    for i in range(len(cnt)):
        max_x_index = np.argmax(cnt[i], axis=0)[0][0]
        max_y_index = np.argmax(cnt[i], axis=0)[0][1]
        min_x_index = np.argmin(cnt[i], axis=0)[0][0]
        min_y_index = np.argmin(cnt[i], axis=0)[0][1]
        # print(ct[i][max_x_index])
        list_corner = np.append(list_corner,cnt[i][max_x_index],axis=0)
        list_corner = np.append(list_corner,cnt[i][max_y_index],axis=0)
        list_corner = np.append(list_corner,cnt[i][min_x_index],axis=0)
        list_corner = np.append(list_corner,cnt[i][min_y_index],axis=0)

    list_corner = np.delete(list_corner, 0, 0)
    max_index = np.argmax(list_corner,axis=0)
    min_index = np.argmin(list_corner,axis=0)
    max_x_index = list_corner[max_index[0]][0]
    max_y_index = list_corner[max_index[1]][1]
    min_x_index = list_corner[min_index[0]][0]
    min_y_index = list_corner[min_index[1]][1]
    point_1 = (min_x_index,min_y_index)
    point_2 = (max_x_index,max_y_index)
    cv2.rectangle(image,point_1,point_2,(0,255,0),3)
    cv2.imshow('image',image)
    # print(max_x)
    traffic_sign = image[min_y_index:max_y_index, min_x_index: max_x_index,:]
    return traffic_sign
if __name__ == "__main__":
    image = cv2.imread('image_testing/turnleft.jpg')
    traffic_sign_image = dectect_obj(image)
    if traffic_sign_image is None:
        print("None")
    else:
        val = predict_obj(traffic_sign_image) # 1 is left, 0 is right
        if val == 1:
            print("TURN LEFT")
        else:
            print("TURN RIGHT")
    cv2.waitKey()
    pass
