#!/usr/bin/env python
#
# Scanning script for the Noisebridge book scanner.

import sys
import subprocess
import re
import time
import os


GPHOTO = 'gphoto2'
VIEW_FILE = 'view.html'
TMP_FILE = 'view_tmp.html'
IMG_FORMAT = 'img%05d.jpg'
TMP_FORMAT = 'tmp%05d.jpg'

import cv2
import numpy as np
import transfer
import math
import adaptive

def distance(x1,y1,x2,y2):
    return math.sqrt((x2-x1)**2 + (y2-y1)**2)

# y = ax + b
def get_crosspt(x11,y11, x12,y12, x21,y21, x22,y22):
    if x12==x11 or x22==x21:
        if x12==x11:
            cx = x12
            m2 = (y22 - y21) / (x22 - x21)
            cy = m2 * (cx - x21) + y21
            result = np.array([[cx, cy]])

            return result
        if x22==x21:
            cx = x22
            m1 = (y12 - y11) / (x12 - x11)
            cy = m1 * (cx - x11) + y11
            result = np.array([[cx, cy]])
            return result

    m1 = (y12 - y11) / (x12 - x11)
    m2 = (y22 - y21) / (x22 - x21)
    if m1==m2:
        print('parallel')
        return None
    cx = (x11 * m1 - y11 - x21 * m2 + y21) / (m1 - m2)
    cy = m1 * (cx - x11) + y11
    result = np.array([[cx, cy]])
    
    
    return result


image=cv2.imread("image1.jpg") 
image=cv2.resize(image,(1300,800)) #resizing
h, w = image.shape[:2]
orig=image.copy()

gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY) 
# gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 5,5) #맨 뒤 주변부 보는 영역, 임계값
blurred=cv2.GaussianBlur(gray,(15,15),0)  #(5,5) is the kernel size and 0 is sigma that determines the amount of blur

blurred = cv2.bilateralFilter(blurred, -1,10,5) #에지가 아닌 부분만 blurring 
# cv2.imshow("blur2", blurred)


edged=cv2.Canny(blurred,50,50)  # 선으로 표현하기... threshold 둘다 값이 클수록 엣지 검출 어려움
# cv2.imshow("Blur",edged)


#### 모폴로지 연산
k = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
# mor = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, k)
mor = cv2.dilate(edged, k)
mor = cv2.erode(mor, k)

# cv2.imshow("mor", mor)


edging = edged.copy()

# cv2.HoughLinesP(찾을 이미지, 거리측정 해상도 1, 각도, 직선판단정확도, None, 최소길이,최대간격)
lines = cv2.HoughLinesP(mor, 1, np.pi/1800, 50, None, 100, 10) #확률적 변환


##################사각형 네 직선 검출
Max =0
max_set = [[]]



for index in range(0, len(lines)):
    ### 평행한 한 직선과 수직한 두 직선이 존재해야함....
    x1, y1, x2, y2 = lines[index][0]
    rad = math.atan2(x2-x1, y2-y1)
    rad = math.degrees(rad)

    
    vertical = np.empty((0,4))
    horizontal = np.empty((0,4))
    

    for idx in range(index+1, len(lines)):
        xx1, yy1, xx2, yy2 = lines[idx][0]
        rad2 = math.atan2(xx2-xx1, yy2-yy1)
        rad2 = math.degrees(rad2)
        
        if(abs(rad2 - rad)<100 and abs(rad2 - rad) > 80): # 수직 선분 
            if(len(vertical) <2 ):
                vertical = np.append(vertical,lines[idx], 0)
                
        elif(abs(rad2 - rad)<7 or abs(rad2 - rad) >173): # 평행 선분 
            if(len(horizontal) ==0 ):
                horizontal = np.append(horizontal,lines[idx], 0)
        
        point = np.empty((0,2))
        if(len(vertical) == 2 and len(horizontal) == 1):
            point = np.append(point,get_crosspt(x1,y1,x2,y2,vertical[0][0],vertical[0][1],vertical[0][2],vertical[0][3]),0)
            point = np.append(point,get_crosspt(vertical[0][0],vertical[0][1],vertical[0][2],vertical[0][3],horizontal[0][0],horizontal[0][1],horizontal[0][2],horizontal[0][3]),0)
            point = np.append(point,get_crosspt(horizontal[0][0],horizontal[0][1],horizontal[0][2],horizontal[0][3],vertical[1][0],vertical[1][1],vertical[1][2],vertical[1][3]),0)
            point = np.append(point,get_crosspt(x1,y1,x2,y2,vertical[1][0],vertical[1][1],vertical[1][2],vertical[1][3]),0) 
            if(len(point) == 4):
                
                if(distance(point[0][0],point[0][1],point[1][0],point[1][0]) * distance(point[1][0],point[1][1],point[2][0],point[2][0]) > Max):
                    Max = distance(point[0][0],point[0][1],point[1][0],point[1][0]) * distance(point[1][0],point[1][1],point[2][0],point[2][0])
                    max_set = point
                    
                   


    cv2.line(image, (x1,y1), (x2, y2), (0,255,0), 1) #연장 안하고 그리기
    
cv2.imshow("line", image)    
approx=transfer.transfer(max_set) # 점 4개의 좌표 가져감 
print(max_set)
pts=np.float32([[0,0],[800,0],[800,800],[0,800]])  #map to 800*800 target window

op=cv2.getPerspectiveTransform(approx,pts)  #get the top or bird eye view effect
dst=cv2.warpPerspective(orig,op,(800,800))
cv2.imshow("Scan",dst)
dst_gray=cv2.cvtColor(dst,cv2.COLOR_BGR2GRAY) 
dst_gray = adaptive.adaptive(dst_gray)
cv2.imshow("Scanned",dst_gray)
###
       
    
    
               
for line in lines:
    # 검출된 선 그리기 ---
    # print(line[0])
    x1, y1, x2, y2 = line[0]
#     if( a == math.inf or a == -math.inf):
#         cv2.line(image, (x1,0),(x1, h),(255,0,0),1)

#     else :
        
#         cv2.line(image, (0,int(b)),(int(w), int(a*w+b)),(255,0,0),1)  

    cv2.line(image, (x1,y1), (x2, y2), (0,255,0), 1) #연장 안하고 그리기
    



cv2.imshow("Canny",image)


cv2.waitKey(0)
cv2.destroyAllWindows()