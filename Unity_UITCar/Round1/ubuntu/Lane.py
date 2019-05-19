import cv2
import numpy as np
import math
############################## calcul steer angle #############################
def find_point_center(center_line):
    roi = int(center_line.shape[0]*(7/9))+10
    for y in range(roi,center_line.shape[0]):
        for x in range(center_line.shape[1]):
            if center_line[y][x] == 255:
                # cv2.circle(center_line,(x,y),1,(255,0,0),7)
                # cv2.imshow('center_point',center_line)
                return x,y
    return 0,0

def errorAngle(center_line):
    carPosx , carPosy = 320, 480
    dstx, dsty = find_point_center(center_line)
    print(dstx,dsty)
    if dstx == carPosx:
        return 0
    if dsty == carPosy:
        if dstx < carPosx:
            return -45
        else:
            return 45
    pi = math.acos(-1.0)
    dx = dstx - carPosx
    dy = carPosy - dsty
    if dx < 0: 
        angle = (math.atan(-dx / dy) * -180 / pi)/2.5
        if angle >= 28 or angle <= -28: # maybe must turn 90
            if angle > 0:
                return 45
            return -45
        return angle
    #################################################
    angle = (math.atan(dx / dy) * 180 / pi)/2.5
    if angle >= 25 or angle <= -25: # maybe must turn 90
        if angle > 0:
            return 45
        return -45
    return angle

def calcul_speed(steer_angle):
    max_speed = 70
    max_angle = 40
    if steer_angle == -45 or steer_angle == 45:
        return 0
    if steer_angle >= 4 or steer_angle <= -4:
        if steer_angle > 0:
            return max_speed - (max_speed/max_angle)*steer_angle
        else:
            return max_speed + (max_speed/max_angle)*steer_angle 
    elif steer_angle >= 15 or steer_angle <= -15:
        if steer_angle > 0:
            return 40 - (40/max_angle)*steer_angle
        else:
            return 40 + (30/max_angle)*steer_angle
    # elif steer_angle >= 10 or steer_angle <= -10:
    #     if steer_angle > 0:
    #         return max_speed - (max_speed/max_angle)*steer_angle
    #     else:
    #         return max_speed + (max_speed/max_angle)*steer_angle 
    # if steer_angle >=0:
    #     return max_speed - (max_speed/max_angle)*steer_angle
    return max_speed 

class Lane:
    def __init__(self, image):
        self.__image = image
        self.binary_image = None
        self.left_line = None
        self.right_line = None

############### covert image #################################
    def __nothing(self,x):
        pass  
    def create_Trackbar(self):
        cv2.namedWindow("lower")
        cv2.namedWindow("upper")
        cv2.createTrackbar('lowH','lower',0,179,self.__nothing)
        cv2.createTrackbar('highH','upper',179,179,self.__nothing)

        cv2.createTrackbar('lowS','lower',0,255,self.__nothing)
        cv2.createTrackbar('highS','upper',255,255,self.__nothing)

        cv2.createTrackbar('lowV','lower',0,255,self.__nothing)
        cv2.createTrackbar('highV','upper',255,255,self.__nothing)
    def __get_threshold(self):
        ilowH = cv2.getTrackbarPos('lowH', 'lower')
        ihighH = cv2.getTrackbarPos('highH', 'upper')
        ilowS = cv2.getTrackbarPos('lowS', 'lower')
        ihighS = cv2.getTrackbarPos('highS', 'upper')
        ilowV = cv2.getTrackbarPos('lowV', 'lower')
        ihighV = cv2.getTrackbarPos('highV', 'upper')
        return np.array([ilowH,ilowS,ilowV]),np.array([ihighH,ihighS,ihighV])
    def __cvt_binary(self):
        lower, upper = self.__get_threshold()
        # lower, upper = np.array([0,0,0]), np.array([179,22,255])
        hsv_image = cv2.cvtColor(self.__image,cv2.COLOR_RGB2HSV)
        binary_image = cv2.inRange(hsv_image,lower,upper)
        self.binary_image = binary_image # public for debug
    def __cvt_binary_rgb(self, thresh=(0, 255)):
        R = self.__image[:,:,2] 
        G = self.__image[:,:,1]
        B = self.__image[:,:,0]
        binary_output = np.zeros_like(R)
        binary_output[(R >= thresh[0]) & (R <= thresh[1]) & (G >= thresh[0]) & (G <= thresh[1]) & (B >= thresh[0]) & (B <= thresh[1])] = 1
        self.binary_image = binary_output
############################Processing Line#############################
    def __warp(self):
        image_size = (self.__image.shape[1], self.__image.shape[0])
        x = self.__image.shape[1]
        y = self.__image.shape[0]
        #the "order" of points in the polygon you are defining does not matter
        #but they need to match the corresponding points in destination_points!
        ## my source
        source_points = np.float32([
        [0, y],
        [0, (7/9)*y+10],
        [x, (7/9)*y+10],
        [x, y]
        ])
        
        destination_points = np.float32([
        [0.25 * x, y],
        [0.25 * x, 0],
        [x - (0.25 * x), 0],
        [x - (0.25 * x), y]
        ])
        
        perspective_transform = cv2.getPerspectiveTransform(source_points, destination_points)
        self.__inverse_perspective_transform = cv2.getPerspectiveTransform( destination_points, source_points)
        self.__warped_image = cv2.warpPerspective(self.binary_image, perspective_transform, image_size, flags=cv2.INTER_LINEAR)
    
    def __get_val(self,y,poly_coeff):
        return poly_coeff[0]*y**2+poly_coeff[1]*y+poly_coeff[2]

    def __check_lane_inds(self,left_lane_inds, right_lane_inds):
        countleft = 0
        countright = 0
        missing_one_line = False
        for x in range(9):
            left = np.asarray(left_lane_inds[x])
            right = np.asarray(right_lane_inds[x])
            if len(left) < 30:
                countleft+=1
            if len(right) < 30:
                countright+=1
            if len(left) == len(right) and len(left) !=0 and len(right) != 0:
                if (left == right).all():
                    missing_one_line = True
        if missing_one_line:
            if countleft == countright:
                return left_lane_inds, right_lane_inds
            if countleft < countright:
                return left_lane_inds, []
            return [], right_lane_inds
        if countleft >= 6:
            return [], right_lane_inds
        if countright >= 6:
            return left_lane_inds, []
        return left_lane_inds,right_lane_inds

    def __check_fit_duplication(self,left_fit, right_fit):
        if len(left_fit) == 0 or len(right_fit) == 0:
            return left_fit, right_fit
        # print(left_fit[2], right_fit[2])
        if abs(left_fit[0] - right_fit[0]) < 0.1:
            if abs(left_fit[1] - right_fit[1]) < 0.4:
                if abs(left_fit[2] - right_fit[2]) < 30:
                    return left_fit, []
        return left_fit, right_fit

    def __track_lanes_initialize(self, binary_warped):   
        histogram = np.sum(binary_warped[int(binary_warped.shape[0]/2):,:], axis=0)
        # out_img = np.dstack((binary_warped, binary_warped, binary_warped))
        midpoint = np.int(histogram.shape[0]/2)
        leftx_base = np.argmax(histogram[:midpoint+100])
        rightx_base = np.argmax(histogram[midpoint+100:]) + midpoint+100
        nwindows = 9
        window_height = np.int(binary_warped.shape[0]/nwindows)
        nonzero = binary_warped.nonzero()
        nonzeroy = np.array(nonzero[0])
        nonzerox = np.array(nonzero[1])
        leftx_current = leftx_base
        rightx_current = rightx_base
        # Set the width of the windows +/- margin
        margin = 40
        # Set minimum number of pixels found to recenter window
        minpix = 60
        # Create empty lists to receive left and right lane pixel indices
        left_lane_inds = []
        right_lane_inds = []  
        for window in range(nwindows):
            # Identify window boundaries in x and y (and right and left)
            win_y_low = int(binary_warped.shape[0] - (window+1)*window_height)
            win_y_high = int(binary_warped.shape[0] - window*window_height)
            win_xleft_low = leftx_current - margin
            win_xleft_high = leftx_current + margin
            win_xright_low = rightx_current - margin
            win_xright_high = rightx_current + margin
            # Draw the windows on the visualization image
            # cv2.rectangle(out_img,(win_xleft_low,win_y_low),(win_xleft_high,win_y_high),(0,255,0), 3) 
            # cv2.rectangle(out_img,(win_xright_low,win_y_low),(win_xright_high,win_y_high),(0,255,0), 3) 
            # cv2.imshow('out_img',out_img)
            # Identify the nonzero pixels in x and y within the window
            good_left_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) & (nonzerox >= win_xleft_low) & (nonzerox < win_xleft_high)).nonzero()[0]
            good_right_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) & (nonzerox >= win_xright_low) & (nonzerox < win_xright_high)).nonzero()[0]
            # Append these indices to the lists
            left_lane_inds.append(good_left_inds)
            right_lane_inds.append(good_right_inds)
            # If you found > minpix pixels, recenter next window on their mean position
            if len(good_left_inds) > minpix:
                leftx_current = np.int(np.mean(nonzerox[good_left_inds]))
            if len(good_right_inds) > minpix:        
                rightx_current = np.int(np.mean(nonzerox[good_right_inds]))
        left_lane_inds,right_lane_inds = self.__check_lane_inds(left_lane_inds,right_lane_inds)
        if len(left_lane_inds) != 0:
            left_lane_inds = np.concatenate(left_lane_inds)
        if len(right_lane_inds) !=0:
            right_lane_inds = np.concatenate(right_lane_inds)
        leftx = nonzerox[left_lane_inds]
        lefty = nonzeroy[left_lane_inds] 
        rightx = nonzerox[right_lane_inds]
        righty = nonzeroy[right_lane_inds] 
        left_fit = np.array([])
        right_fit = np.array([])
        if len(leftx) != 0:
            left_fit  = np.polyfit(lefty, leftx, 2)
        if len(rightx) != 0:
            right_fit  = np.polyfit(righty, rightx, 2)
        self.left_line, self.right_line = self.__check_fit_duplication(left_fit,right_fit)

    def __lane_fill_poly(self):
        ploty = np.linspace(0, self.binary_image.shape[0]-1, self.binary_image.shape[0])
        if len(self.left_line) == 0:
            self.left_line = np.array([0,0,1])
        if len(self.right_line) == 0:
            self.right_line = np.array([0,0,self.binary_image.shape[1]-1])
        left_fitx = self.__get_val(ploty,self.left_line)
        right_fitx =self.__get_val(ploty,self.right_line)
        # Create an image to draw the lines on
        warp_zero = np.zeros_like(self.binary_image).astype(np.uint8)
        color_warp = np.dstack((warp_zero, warp_zero, warp_zero))
        # Recast x and y for cv2.fillPoly()
        pts_left = np.array([np.transpose(np.vstack([left_fitx, ploty]))])
        pts_right = np.array([np.flipud(np.transpose(np.vstack([right_fitx, ploty])))])
        pts = np.hstack((pts_left, pts_right))
        # Draw the lane 
        cv2.fillPoly(color_warp, np.int_([pts]), (0,255, 0))
        # Warp using inverse perspective transform
        newwarp = cv2.warpPerspective(color_warp, self.__inverse_perspective_transform, (self.binary_image.shape[1], self.binary_image.shape[0])) 
        self.__lane_image = cv2.addWeighted(self.__image, 1, newwarp, 0.7, 0.3)

    def __checking_missing_line(self): # focus to missing 1 line
        # flag is old status missing before
        if len(self.left_line) == 0 or len(self.right_line) == 0:
            avaiable_fit = self.left_line
            if len(avaiable_fit) == 0:
                avaiable_fit = self.right_line
            if len(avaiable_fit) == 0:
                return # missing 2 line
            #missing 1 line: not exact 100 percent, maybe exact 80 percent
            carPosx , carPosy = 320, 480
            value_check = int(carPosx - self.__get_val(carPosy,avaiable_fit))
            # print(value_check)
            if value_check > 0: # avaiable fit is left line
                print("missing right line")
                self.left_line = avaiable_fit
                self.right_line = []
            elif value_check <=0:
                print("missing left line")
                self.left_line = []
                self.right_line = avaiable_fit
    def get_Lines(self):
        ######## change hsv or rgb in here ##############
        # self.__cvt_binary()
        self.__cvt_binary_rgb(thresh=(200,255))
        #################################################
        self.__warp()
        self.__track_lanes_initialize(self.__warped_image)
        self.__checking_missing_line()

############# Processing_center ###########################
    def get_center_line_warped(self):
        ploty = np.linspace(0, self.__image.shape[0]-1, self.__image.shape[0])
        if len(self.left_line) == 0  and len(self.right_line) == 0: # missing 2 line:
            self.center_fit =  np.array([0,0,self.__image.shape[1]/2])
            return
        if len(self.left_line) == 0 or len(self.right_line) == 0: #missing 1 line
            center_x = np.array([])
            if len(self.left_line) != 0:
                left_fitx = self.__get_val(ploty, self.left_line)
                center_x = np.clip(left_fitx+150,self.__image.shape[1]*0.25+1,self.__image.shape[1]-self.__image.shape[1]*0.25-1)
            else:
                right_fitx = self.__get_val(ploty, self.right_line)
                center_x = np.clip(right_fitx-150,self.__image.shape[1]*0.25+1,self.__image.shape[1]-self.__image.shape[1]*0.25-1)
            self.center_fit = np.polyfit(ploty, center_x, 2)
            return
        # none missing line
        leftx = self.__get_val(ploty, self.left_line)
        rightx = self.__get_val(ploty, self.right_line)
        center_x = (leftx+rightx)/2
        self.center_fit = np.polyfit(ploty, center_x, 2)     
    def get_center_line_unwarped(self):
        self.get_center_line_warped()
        ploty = np.linspace(0, self.binary_image.shape[0]-1, self.binary_image.shape[0])
        warp_zero = np.zeros_like(self.binary_image)
        center_fitx = self.__get_val(ploty,self.center_fit)
        pts_center = np.array([np.transpose([center_fitx, ploty])])
        for element in pts_center[0]:
            x = int(element[0])
            y = int(element[1])
            if x > 0 and x < 640 and y > 0 and y < 480:
                warp_zero[y][x] = 255
        self.center_line = cv2.warpPerspective(warp_zero, self.__inverse_perspective_transform, (self.binary_image.shape[1], self.binary_image.shape[0]))
        # cv2.fillPoly(center_color_warp, np.int_([pts_center]),(255))
        # cv2.imshow("center_color_warp",center_color_warp)
    def draw_center_line(self):
        self.draw_lane()
        self.get_center_line_warped()
        warp_zero = np.zeros_like(self.binary_image).astype(np.uint8)
        center_color_warp = np.dstack((warp_zero, warp_zero, warp_zero))
        ploty = np.linspace(0, self.binary_image.shape[0]-1, self.binary_image.shape[0])
        center_fitx = self.__get_val(ploty,self.center_fit)
        pts_center = np.array([np.transpose(np.vstack([center_fitx, ploty]))])
        cv2.fillPoly(center_color_warp, np.int_([pts_center]),(0,0,255))
        center_line = cv2.warpPerspective(center_color_warp, self.__inverse_perspective_transform, (self.binary_image.shape[1], self.binary_image.shape[0])) 
        center = cv2.addWeighted(self.__lane_image,1,center_line,0.7,0.3)
        cv2.imshow("lane", center)
    def draw_lane(self):
        self.__lane_fill_poly()
        cv2.imshow("lane", self.__lane_image)