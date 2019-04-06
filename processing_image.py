import numpy as np
import cv2
import math

def rgb_select(img, thresh=(0, 255)):
    R = img[:,:,2] 
    G = img[:,:,1]
    B = img[:,:,0]
    binary_output = np.zeros_like(R)
    binary_output[(R >= thresh[0]) & (R <= thresh[1]) & (G >= thresh[0]) & (G <= thresh[1]) & (B >= thresh[0]) & (B <= thresh[1])] = 1
    return binary_output

def line_in_shadow(img, thresh1=(0,255),thresh2=(0,255),thresh3=(0,255)):
    R = img[:,:,2] 
    G = img[:,:,1]
    B = img[:,:,0]
    # Return a binary image of threshold result
    binary_output = np.zeros_like(R)
    binary_output[(R >= thresh1[0]) & (R <= thresh1[1]) & (G >= thresh2[0]) & (G <= thresh2[1]) & (B >= thresh3[0]) & (B <= thresh3[1])] = 1
    return binary_output

def binary_pipeline(img):
    img_copy = cv2.GaussianBlur(img, (3, 3), 0)
    red_binary = rgb_select(img_copy, thresh=(200,255))
    line_shadow = line_in_shadow(img_copy,thresh1=(50,90),thresh2=(60,120),thresh3=(120,150))
    binary =  cv2.bitwise_or(line_shadow,red_binary)
    return binary

def warp_image(img):
    
    image_size = (img.shape[1], img.shape[0])
    x = img.shape[1]
    y = img.shape[0]

    #the "order" of points in the polygon you are defining does not matter
    #but they need to match the corresponding points in destination_points!
    ## my source
    source_points = np.float32([
    [0, y],
    [0, (7/9)*y],
    [x, (7/9)*y],
    [x, y]
    ])
    
    destination_points = np.float32([
    [0.25 * x, y],
    [0.25 * x, 0],
    [x - (0.25 * x), 0],
    [x - (0.25 * x), y]
    ])
    
    perspective_transform = cv2.getPerspectiveTransform(source_points, destination_points)
    inverse_perspective_transform = cv2.getPerspectiveTransform( destination_points, source_points)
    
    warped_img = cv2.warpPerspective(img, perspective_transform, image_size, flags=cv2.INTER_LINEAR)

    return warped_img, inverse_perspective_transform

def get_val(y,poly_coeff):
    return poly_coeff[0]*y**2+poly_coeff[1]*y+poly_coeff[2]


def check_lane_inds(left_lane_inds, right_lane_inds):
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
    if countleft > 7:
        return [], right_lane_inds
    if countright > 7:
        return left_lane_inds, []
    return left_lane_inds,right_lane_inds

def track_lanes_initialize(binary_warped):   
    histogram = np.sum(binary_warped[int(binary_warped.shape[0]/2):,:], axis=0)
    out_img = np.dstack((binary_warped, binary_warped, binary_warped))*255
    midpoint = np.int(histogram.shape[0]/2)
    leftx_base = np.argmax(histogram[:midpoint])
    rightx_base = np.argmax(histogram[midpoint:]) + midpoint
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
        cv2.imshow('out_img',out_img)
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
        
    # print('left_lane_inds:',len(left_lane_inds))
    # print('right_lane_inds',len(right_lane_inds))
    # Concatenate the arrays of indices
    # left_lane_inds = 
    left_lane_inds,right_lane_inds = check_lane_inds(left_lane_inds,right_lane_inds)
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


    return left_fit, right_fit
def check_missing_line(binary_warped,left_fit, right_fit, current_missing_line):
    x = binary_warped.shape[1] - 1
    y = binary_warped.shape[0] - 1
    # if len(left_fit) == 0 or len(right_fit) == 0:
    #     if current_missing_line[0]:
    #         return True, False
    #     if current_missing_line[1]:
    #         return False, True
    if len(left_fit) == 0 and not(current_missing_line[1]):
        print("line left missing_in_missing_line")
        return True, False    
    if len(right_fit) == 0 and not(current_missing_line[0]):
        print("line right missing_in_missing_line")
        return False, True
    if len(left_fit) != 0 and len(right_fit) != 0:
        
        if (left_fit == right_fit).all():
            if current_missing_line[0]:
                return True, False
            if current_missing_line[1]:
                return False,True
            print("line right or left missing")
            check_point =  get_val(y,left_fit)
            if check_point < x/2: # left line avaiable
                return False, True
            else:
                return True, False
    return False,False

def lane_fill_poly(binary_warped,undist,left_fit,right_fit, inverse_perspective_transform):
    ploty = np.linspace(0, binary_warped.shape[0]-1, binary_warped.shape[0])
    x = binary_warped.shape[1] - 1
    y = binary_warped.shape[0] - 1
    if len(left_fit) == 0:
        print("line left missing")
        left_fit = np.array([0,0,1])
    if len(right_fit) == 0:
        print("line right missing")
        right_fit = np.array([0,0,x])
    if len(left_fit) != 0 and len(right_fit) != 0:
        if (left_fit ==  right_fit).all():
            print("line right or left missing")
            check_point =  get_val(y,left_fit)
            if check_point < x/2+1:
                right_fit = np.array([0,0,x])
            else:
                left_fit = np.array([0,0,1])
    left_fitx = get_val(ploty,left_fit)
    right_fitx = get_val(ploty,right_fit)
    len_center = len(left_fitx)
    if len(left_fitx) > len(right_fitx):
        len_center = len(right_fitx)
    center_x = (left_fitx[:len_center]+right_fitx[:len_center])/2
    # center_y = (lefty[:len(righty)]+righty)/2
    # print(center_x)
    # Create an image to draw the lines on
    warp_zero = np.zeros_like(binary_warped).astype(np.uint8)
    color_warp = np.dstack((warp_zero, warp_zero, warp_zero))
    center_color_warp = np.dstack((warp_zero, warp_zero, warp_zero))
    # Recast x and y for cv2.fillPoly()
    pts_left = np.array([np.transpose(np.vstack([left_fitx, ploty]))])
    pts_right = np.array([np.flipud(np.transpose(np.vstack([right_fitx, ploty])))])
    pts_center = np.array([np.transpose(np.vstack([center_x, ploty]))])
    pts = np.hstack((pts_left, pts_right))
    # print(pts)
    # Draw the lane 
    cv2.fillPoly(color_warp, np.int_([pts]), (0,255, 0))
    cv2.fillPoly(center_color_warp, np.int_([pts_center]),(0,0,255))
    # Warp using inverse perspective transform
    newwarp = cv2.warpPerspective(color_warp, inverse_perspective_transform, (binary_warped.shape[1], binary_warped.shape[0])) 
    center_line = cv2.warpPerspective(center_color_warp, inverse_perspective_transform, (binary_warped.shape[1], binary_warped.shape[0])) 
   
    result = cv2.addWeighted(undist, 1, newwarp, 0.7, 0.3)
    result = cv2.addWeighted(result,1,center_line,0.7,0.3)
    return result, center_line

def find_point_center(center_line):
    roi = int(center_line.shape[0]*(7/9))
    for y in range(roi,center_line.shape[0]):
        for x in range(center_line.shape[1]):
            if center_line[y][x][2] == 255:
                cv2.circle(center_line,(x,y),1,(255,0,0),7)
                # cv2.imshow('center_point',center_line)
                return x,y
    return 0,0

    
def errorAngle(dst, carPosx , carPosy):
    dstx = dst[1]
    dsty = dst[0]
    # print(carPosx,carPosy)
    if dstx == carPosx:
        return 0
    if dsty == carPosy:
        if dstx < carPosx:
            return -90
        else:
            return 90
    pi = math.acos(-1.0)
    dx = dstx - carPosx
    dy = carPosy - dsty
    # print(dx,dy)
    # print(dx,dy) 
    if dx < 0: 
        return math.atan(-dx / dy) * -180 / pi
    return (math.atan(dx / dy) * 180 / pi)

def calcul_speed(steer_angle):
    max_speed = 60
    max_angle = 40
    if steer_angle >= 20 or steer_angle <= -20:
        if steer_angle > 0:
            return 25 - (25/max_angle)*steer_angle
        else:
            return 25 + (25/max_angle)*steer_angle
    elif steer_angle >= 15 or steer_angle <= -15:
        if steer_angle > 0:
            return 40 - (40/max_angle)*steer_angle
        else:
            return 40 + (30/max_angle)*steer_angle
    elif steer_angle >= 10 or steer_angle <= -10:
        if steer_angle > 0:
            return 50 - (50/max_angle)*steer_angle
        else:
            return 50 + (50/max_angle)*steer_angle 
    elif steer_angle >=0:
        return max_speed - (max_speed/max_angle)*steer_angle

    return max_speed + (max_speed/max_angle)*steer_angle