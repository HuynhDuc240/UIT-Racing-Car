import cv2
import numpy as np
import math

def cal_Angle(center_point):
    carPosx , carPosy = 160, 240
    dstx, dsty = center_point
    if dstx == carPosx:
        return 0
    if dsty == carPosy:
        if dstx < carPosx:
            return -30
        else:
            return 30
    pi = math.acos(-1.0)
    dx = dstx - carPosx
    dy = carPosy - dsty
    if dx < 0: 
        angle = (math.atan(-dx / dy) * -180 / pi) / 2.5 * 2.3
        # if angle >= 25 or angle <= -25: # maybe must turn 90
        #     if angle > 0:
        #         return 30
        #     return -30
        return angle
    #################################################
    angle = (math.atan(dx / dy) * 180 / pi) / 2.5 * 2.3
    # if angle >= 25 or angle <= -25: # maybe must turn 90
    #     if angle > 0:
    #         return 30
    #     return -30
    return angle
#########################  convert image #################################
# def get_threshold():
#     ilowH = cv2.getTrackbarPos('lowH', 'lower')
#     ihighH = cv2.getTrackbarPos('highH', 'upper')
#     ilowS = cv2.getTrackbarPos('lowS', 'lower')
#     ihighS = cv2.getTrackbarPos('highS', 'upper')
#     ilowV = cv2.getTrackbarPos('lowV', 'lower')
#     ihighV = cv2.getTrackbarPos('highV', 'upper')
#     return np.array([ilowH,ilowS,ilowV]),np.array([ihighH,ihighS,ihighV])

def abs_sobel_thresh(image,orient,  thresh=(20, 100)):
    gray=cv2.cvtColor(image,cv2.COLOR_RGB2GRAY)
    
    if orient=='x':x, y=1,0
    else: x, y=0,1
        
    sobel=cv2.Sobel(gray,cv2.CV_64F,x,y)
    sobel=np.absolute(sobel)
    scaled_sobel=np.uint8(255*sobel/np.max(sobel))
    
    sx_binary=np.zeros_like(scaled_sobel)
    sx_binary[(scaled_sobel>=thresh[0]) & (scaled_sobel<=thresh[1])]=1
    binary_output=np.copy(sx_binary)
    return binary_output


def mag_thresh(img, mag_thresh=(20,150)):
    
    gray=cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
    
    sobelx=cv2.Sobel(gray,cv2.CV_64F,1,0)
    sobely=cv2.Sobel(gray,cv2.CV_64F,0,1)
    sobel=np.sqrt(np.square(sobelx)+np.square(sobely))
    scaled_sobel=np.uint8(255*sobel/np.max(sobel))
    
#     t=sum((i > 150) &(i<200)  for i in scaled_sobel)
    binary_sobel=np.zeros_like(scaled_sobel)
    binary_sobel[(scaled_sobel>=mag_thresh[0]) & (scaled_sobel<=mag_thresh[1])]=1
    return binary_sobel

def dir_threshold(img,  thresh=(0.7,1.3)):
    gray=cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
    sobelx=np.absolute(cv2.Sobel(gray,cv2.CV_64F,1,0))
    sobely=np.absolute(cv2.Sobel(gray,cv2.CV_64F,0,1))
    
    dir_=np.arctan2(sobely,sobelx)
    
    sx_binary = np.zeros_like(gray)
    sx_binary[(dir_>=thresh[0]) &(dir_<=thresh[1])]=1
    binary_output=sx_binary
    return binary_output

def color_space(image,thresh=(170,255)):
    hls=cv2.cvtColor(image,cv2.COLOR_RGB2HLS)
    l_channel=hls[:,:,1]
    s_channel=hls[:,:,2]
    s_binary=np.zeros_like(s_channel)
    
    s_binary[(s_channel>=thresh[0]) & (s_channel<=thresh[1])&(l_channel>=80)]=1
    color_output=np.copy(s_binary)
    return color_output

def segregate_white_line(image,thresh=(200,255)):
    hls=cv2.cvtColor(image,cv2.COLOR_RGB2HLS)
    l_channel=hls[:,:,1]
    l_binary=np.zeros_like(l_channel)
    l_binary[((l_channel>=200)&(l_channel<=255))]=1
    return l_binary

def gradient_color_thresh(image):
    # ksize=3
    gradx = abs_sobel_thresh(image, orient='x', thresh=(20, 200))
    grady = abs_sobel_thresh(image, orient='y', thresh=(20, 200))
    
    mag_binary = mag_thresh(image, mag_thresh=(20, 200))
    
    dir_binary = dir_threshold(image, thresh=(0.7, 1.3))
    
    color_binary=color_space(image,thresh=(100,255))
    
    combined = np.zeros_like(dir_binary)
    combined[(color_binary==1)|((gradx == 1)& (grady == 1)) |(mag_binary==1) &(dir_binary==1)] = 1
    
    kernel = np.ones((3,3),np.uint8)
    morph_image=combined
    morph_image = cv2.morphologyEx(morph_image, cv2.MORPH_OPEN, kernel)
    combined=morph_image
    
    white_line=segregate_white_line(image,thresh=(200,255))
    combined=(combined)|(white_line)
    
    return combined
#############################################################################
def get_val(y,poly_coeff):
    return poly_coeff[0]*y**2+poly_coeff[1]*y+poly_coeff[2]
class LINE():
    def __init__(self):
        self.first_frame=False
        self.curvature=0
        
        self.right_fit=[np.array([])]
        self.left_fit=[np.array([])]
        self.max_tolerance=0.01
        self.center_x = []
        self.img=None
        x = 320
        y = 240
        source_points = np.float32([
        [0, y],
        [0.08 * x, int((2/3)*y)],
        [x - (0.08  * x), int((2/3)*y)],
        [x, y]
        ])
            
        destination_points = np.float32([
        [0.1 * x, y],
        [0.1 * x, 0],
        [x - (0.1 * x), 0],
        [x - (0.1 * x), y]
        ])
        self.M = cv2.getPerspectiveTransform(source_points, destination_points)
        self.Minv = cv2.getPerspectiveTransform(destination_points, source_points)  
    
    def update_fit(self,left_fit,right_fit):
        self.right_fit=right_fit
        self.left_fit=left_fit
    
            

class LANE():
    def __init__(self,line,image):
        self.line = line
        self.image = image
        self.center_x = []
        self.center_point = 0
             

    def detect_lane(self,ts_flag):
        img = np.copy(self.image)
        img_size=(img.shape[1],img.shape[0])
        thresh_image=gradient_color_thresh(img)
        binary_warped = cv2.warpPerspective(thresh_image, self.line.M, img_size, flags=cv2.INTER_LINEAR)
        # cv2.imshow("binary_warped",binary_warped*255)
        out_img = np.dstack((binary_warped, binary_warped, binary_warped))*255
        nwindows = 9
        
        window_height = np.int(binary_warped.shape[0]/nwindows)
        
        margin = 75
        minpix = 50
        
        if not self.line.first_frame:
            histogram = np.sum(binary_warped[int(binary_warped.shape[0]/2):,:], axis=0)
            # Create an output image to draw on and  visualize the result
            midpoint = np.int(histogram.shape[0]/2)
            leftx_base = np.argmax(histogram[:midpoint])
            rightx_base = np.argmax(histogram[midpoint:]) + midpoint

            # Identify the x and y positions of all nonzero pixels in the image
            nonzero = binary_warped.nonzero()
            nonzeroy = np.array(nonzero[0])
            nonzerox = np.array(nonzero[1])
            # Current positions to be updated for each window
            leftx_current = leftx_base
            rightx_current = rightx_base
            # Create empty lists to receive left and right lane pixel indices
            left_lane_inds = []
            right_lane_inds = []

            # Step through the windows one by one
            for window in range(nwindows):
                # Identify window boundaries in x and y (and right and left)
                win_y_low = binary_warped.shape[0] - (window+1)*window_height
                win_y_high = binary_warped.shape[0] - window*window_height
                win_xleft_low = leftx_current - margin
                win_xleft_high = leftx_current + margin
                win_xright_low = rightx_current - margin
                win_xright_high = rightx_current + margin
                # Draw the windows on the visualization image
                cv2.rectangle(out_img,(win_xleft_low,win_y_low),(win_xleft_high,win_y_high),
                (0,255,0), 2) 
                cv2.rectangle(out_img,(win_xright_low,win_y_low),(win_xright_high,win_y_high),
                (0,255,0), 2) 
                # Identify the nonzero pixels in x and y within the window
                good_left_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) & 
                (nonzerox >= win_xleft_low) &  (nonzerox < win_xleft_high)).nonzero()[0]
                good_right_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) & 
                (nonzerox >= win_xright_low) &  (nonzerox < win_xright_high)).nonzero()[0]
                # Append these indices to the lists
                left_lane_inds.append(good_left_inds)
                right_lane_inds.append(good_right_inds)
                # If you found > minpix pixels, recenter next window on their mean position
                if len(good_left_inds) > minpix:
                    leftx_current = np.int(np.mean(nonzerox[good_left_inds]))
                if len(good_right_inds) > minpix:        
                    rightx_current = np.int(np.mean(nonzerox[good_right_inds]))

            # Concatenate the arrays of indices
            left_lane_inds = np.concatenate(left_lane_inds)
            right_lane_inds = np.concatenate(right_lane_inds)

            # Extract left and right line pixel positions
            leftx = nonzerox[left_lane_inds]
            lefty = nonzeroy[left_lane_inds] 
            rightx = nonzerox[right_lane_inds]
            righty = nonzeroy[right_lane_inds] 

            # Fit a second order polynomial to each
            left_fit = np.array([0,0,0])
            right_fit = np.array([0,0,img.shape[1]-1])
            if len(leftx) > 1200:
                left_fit = np.polyfit(lefty, leftx, 2)
            if len(rightx) > 1200:
                right_fit = np.polyfit(righty, rightx, 2)
            self.line.update_fit(left_fit,right_fit)
            self.line.first_frame=True
            
        else:
            nonzero = binary_warped.nonzero()
            nonzeroy = np.array(nonzero[0])
            nonzerox = np.array(nonzero[1])
            
            left_fit=self.line.left_fit
            right_fit=self.line.right_fit
            
            left_lane_inds = ((nonzerox > (left_fit[0]*(nonzeroy**2) + left_fit[1]*nonzeroy + 
            left_fit[2] - margin)) & (nonzerox < (left_fit[0]*(nonzeroy**2) + 
            left_fit[1]*nonzeroy + left_fit[2] + margin))) 
            
            right_lane_inds = ((nonzerox > (right_fit[0]*(nonzeroy**2) + right_fit[1]*nonzeroy + 
            right_fit[2] - margin)) & (nonzerox < (right_fit[0]*(nonzeroy**2) + 
            right_fit[1]*nonzeroy + right_fit[2] + margin)))  

            # Again, extract left and right line pixel positions
            leftx = nonzerox[left_lane_inds]
            lefty = nonzeroy[left_lane_inds] 
            rightx = nonzerox[right_lane_inds]
            righty = nonzeroy[right_lane_inds]
            # Fit a second order polynomial to each
            left_fit = np.array([0,0,0])
            right_fit = np.array([0,0,img.shape[1]-1])
            if len(leftx) > 1200:
                left_fit = np.polyfit(lefty, leftx, 2)
            if len(rightx) > 1200:
                right_fit = np.polyfit(righty, rightx, 2)
            self.line.update_fit(left_fit,right_fit)
            left_fit=self.line.left_fit
            right_fit=self.line.right_fit
        ploty = np.linspace(0, binary_warped.shape[0]-1, binary_warped.shape[0] )
        self.update_center_x(ts_flag)
        # left_fitx = get_val(ploty,left_fit)
        # right_fitx = get_val(ploty,right_fit)
        center_x = self.center_x
        warp_zero = np.zeros_like(binary_warped).astype(np.uint8)
        color_warp = np.dstack((warp_zero, warp_zero, warp_zero))
        
        # pts_left = np.array([np.transpose(np.vstack([left_fitx, ploty]))])
        # pts_right = np.array([np.flipud(np.transpose(np.vstack([right_fitx, ploty])))])
        pts_center = np.array([np.flipud(np.transpose(np.vstack([center_x, ploty])))])
        # pts = np.hstack((pts_left, pts_right))
        
        # cv2.fillPoly(color_warp, np.int_([pts]), (0,255, 0))
        cv2.fillPoly(color_warp, np.int_([pts_center]),(0,0,255))
        newwarp = cv2.warpPerspective(color_warp, self.line.Minv, (img.shape[1], img.shape[0]))
        
        line_get_point = newwarp[int((2/3)*240),:,2]
        center = np.nonzero(line_get_point)
        if len(center[0]) ==0 :
            for i in range(int((2/3)*240),239):
                line_get_point = newwarp[i,:,2]
                center = np.nonzero(line_get_point)
                if len(center[0]) != 0:
                    break
        # print(center)
        if len(center[0]) != 0:
            self.center_point = (center[0][0],int((2/3)*240))
        else:
            self.center_point = (160,int((2/3)*240))
        # cv2.circle(newwarp,self.center_point,1,(0,255,0),8)
        result = cv2.addWeighted(img, 1, newwarp, 0.3, 0)
        cv2.imshow("lane",result)

    def update_center_x(self,ts_flag):
        delta = 70
        ######################### have ts_flag #########################
        """
        [[0, 'left'], [1, 'right'], [2, 'stop']]
        if ts_flag is turn left:
            center will be calculated by left_left
        if ts_flag is turn right:
            center will be calculated by right left
        if ts_flag is go straight:
            center is posCar
        if ts_flag is stop:
            driver.setSpeed = 0
        """
        if ts_flag != -1:
            if ts_flag == 1: #turn right
                ploty = np.linspace(0, 239, 240)
                right_x = get_val(ploty,self.line.right_fit)
                self.center_x = np.clip(right_x-delta,320*0.1-1,320-320*0.1-1) 
            elif ts_flag == 0: #turn left
                ploty = np.linspace(0, 239, 240)
                left_x = get_val(ploty,self.line.left_fit)
                self.center_x = np.clip(left_x+delta,320*0.1-1,320-320*0.1-1)
            # elif ts_flag == 2: # stop
            #     ploty = np.linspace(0, 239, 240)
            #     center_fit = [0,0,160]
            #     self.center_x = get_val(ploty,center_fit)
        ######################### have not ts_flag ##########################
        else:
            flag = -1 # 0 is missing left, 1 is missing right, 2 is missing both
            if np.array_equal(self.line.right_fit, np.array([0,0,319])):
                print("missing right line")
                flag = 1
            if np.array_equal(self.line.left_fit,np.array([0,0,0])):
                print("missing left line")
                if flag == 1: #### after that avaiable missing right
                    flag = 2
                else:
                    flag = 0
            if flag == 2:
                ploty = np.linspace(0, 239, 240)
                right_x = get_val(ploty,self.line.right_fit)
                self.center_x = np.clip(right_x-delta,320*0.1-1,320-320*0.1-1)
            elif flag == -1 :
                ploty = np.linspace(0, 239, 240)
                left_x = get_val(ploty,self.line.left_fit)
                right_x = get_val(ploty,self.line.right_fit)
                self.center_x = (left_x + right_x) / 2
            elif flag == 1: # left is avaiable
                ploty = np.linspace(0, 239, 240)
                left_x = get_val(ploty,self.line.left_fit)
                self.center_x = np.clip(left_x+delta,320*0.1-1,320-320*0.1-1)
                # print(self.center_x)
                # self.center_x = left_x + 200
            elif flag == 0: # right is avaiable
                ploty = np.linspace(0, 239, 240)
                right_x = get_val(ploty,self.line.right_fit)
                self.center_x = np.clip(right_x-delta,320*0.1-1,320-320*0.1-1)
                # print(self.center_x)
