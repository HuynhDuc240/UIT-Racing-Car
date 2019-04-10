import numpy as np 
import cv2

image  = cv2.imread('traffic_sign.png')
# imgray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
lower = np.array([240,0,0])
upper = np.array([255,40,40])
R  = image[:,:,2]
G  = image[:,:,1]
B  = image[:,:,0]
binary_output = np.zeros_like(R)
binary_output[(R >= lower[0]) & (R <= upper[0]) & (G >= lower[1]) & (G <= upper[1]) & (B >= lower[2]) & (B <= upper[2])] = 255
    
# ret,thresh = cv2.threshold(image,250,255,0)
# cnt = contours[4]
# cv2.RETR_TREE

contours,hierachy = cv2.findContours(binary_output,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
# cnt = contours[4]
ct = np.asarray(contours)
# min = np.argmax(ct[1], axis=0)
list_corner = np.array([[-1,-1]])
for i in range(len(ct)):
    max_x_index = np.argmax(ct[i], axis=0)[0][0]
    max_y_index = np.argmax(ct[i], axis=0)[0][1]
    min_x_index = np.argmin(ct[i], axis=0)[0][0]
    min_y_index = np.argmin(ct[i], axis=0)[0][1]
    # print(ct[i][max_x_index])
    list_corner = np.append(list_corner,ct[i][max_x_index],axis=0)
    list_corner = np.append(list_corner,ct[i][max_y_index],axis=0)
    list_corner = np.append(list_corner,ct[i][min_x_index],axis=0)
    list_corner = np.append(list_corner,ct[i][min_y_index],axis=0)
    # list_corner = arr.append([list_corner],[ct[i][max_x_index],ct[i][max_y_index],ct[i][min_x_index],ct[i][min_y_index]], axis=0)
# print(ct[1])
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
# print(max_x)

# cv2.drawContours(image,contours, -1, (0,255,0), 3)
cv2.imshow('image', image)
cv2.waitKey()