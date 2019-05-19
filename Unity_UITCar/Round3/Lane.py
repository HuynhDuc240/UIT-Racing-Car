import cv2
import numpy as np
def nothing(x):
    pass  
def create_Trackbar():
    cv2.namedWindow("lower")
    cv2.namedWindow("upper")
    cv2.createTrackbar('lowH','lower',0,179,nothing)
    cv2.createTrackbar('highH','upper',179,179,nothing)
    cv2.createTrackbar('lowS','lower',0,255,nothing)
    cv2.createTrackbar('highS','upper',255,255,nothing)
    cv2.createTrackbar('lowV','lower',0,255,nothing)
    cv2.createTrackbar('highV','upper',255,255,nothing)
class Lane:
    def __init__(self, image):
        self.__image = image
        self.__left_line = None
        self.__right_line = None

############### covert image #################################
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
        # lower, upper = [],[]
        hsv_image = cv2.cvtColor(self.__image,cv2.COLOR_RGB2HSV)
        binary_image = cv2.inRange(hsv_image,lower,upper)
        self.binary_image = binary_image # public for debug
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
            if len(left) == 0:
                countleft+=1
            if len(right) == 0:
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
        out_img = np.dstack((binary_warped, binary_warped, binary_warped))
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
        margin = 100
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
            cv2.rectangle(out_img,(win_xleft_low,win_y_low),(win_xleft_high,win_y_high),(0,255,0), 3) 
            cv2.rectangle(out_img,(win_xright_low,win_y_low),(win_xright_high,win_y_high),(0,255,0), 3) 
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

    def get_Lines(self):
        self.__cvt_binary()
        self.__warp()
        self.__track_lanes_initialize(self.__warped_image)
    def draw_lane(self):
        self.__lane_fill_poly()
        cv2.imshow("lane", self.__lane_image)
