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

# y = ax + b
def cal(x1, y1, x2, y2):
    if(x2-x1 == 0):
        return math.inf, math.inf
    
    a = (y2- y1)/(x2-x1)
    b = (x2*y1-x1*y2)/(x2-x1)
    return a,b

image=cv2.imread("image1.jpg") 
image=cv2.resize(image,(1300,800)) #resizing
h, w = image.shape[:2]
orig=image.copy()

gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY) 

gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 5,5) #맨 뒤 주변부 보는 영역, 임계값
blurred = cv2.bilateralFilter(gray, -1,10,5)
# blurred=cv2.GaussianBlur(gray,(3,3),0)  #(5,5) is the kernel size and 0 is sigma that determines the amount of blur


edged=cv2.Canny(blurred,800,800)  # 선으로 표현하기... threshold 둘다 값이 클수록 엣지 검출 어려움
cv2.imshow("Blur",edged)
edging = edged.copy()

# cv2.HoughLinesP(찾을 이미지, 거리측정 해상도 1, 각도, 직선판단정확도, None, 최소길이,최대간격)
lines = cv2.HoughLinesP(edged, 1, np.pi/180, 10, None, 10, 2) #확률적 변환



# 라인 병합 알고리즘
chk = 0

while(True):
          
    if(chk == len(lines)):
        break
    
    x1, y1, x2, y2 = lines[chk][0]
#     #################### 연장하기 
    a1,b1 = cal(x1,y1, x2, y2)
    if( a1 == math.inf or a1 == -math.inf):
        #cv2.line(image, (x1,0),(x1, h),(255,0,0),1)
        intercept_x1, intercept_y1 = x1,0
        intercept_x2, intercept_y2 = x1, h
    else :
        #cv2.line(image, (0,int(b)),(int(w), int(a*w+b)),(255,0,0),1)  
        intercept_x1, intercept_y1 = 0,int(b1)
        intercept_x2, intercept_y2 = int(w), int(a1*w+b1)

    # print(rad)
    lines2 = lines[:chk+1,:,:].copy()

    for idx in range(chk+1, len(lines)):
        
        xx1, yy1, xx2, yy2 = lines[idx][0]
        if(abs(xx1-xx2)<5 and abs(yy1-yy2)<5):  # 너무 짧은 직선은 제외시킴
            continue
     #################### 연장하기 
        a2,b2 = cal(xx1,yy1, xx2, yy2)
        if( a2 == math.inf or a2 == -math.inf):
            #cv2.line(image, (x1,0),(x1, h),(255,0,0),1)
            intercept_xx1, intercept_yy1 = xx1,0
            intercept_xx2, intercept_yy2 = xx1, h
        else :
            #cv2.line(image, (0,int(b)),(int(w), int(a*w+b)),(255,0,0),1)  
            intercept_xx1, intercept_yy1 = 0,int(b2)
            intercept_xx2, intercept_yy2 = int(w), int(a2*w+b2)
 
        if(a1==a2 and abs(intercept_xx1-intercept_x1)<20 and abs(intercept_xx2-intercept_x2)<20 and abs(intercept_yy1-intercept_y1)<20 and abs(intercept_yy2-intercept_y2)<20):
            # 병합하기
            # 일단 그냥 뒤에 드롭
            continue
        else:
            lines2 = np.append(lines2, np.reshape(lines[idx],(1,1,4)), 0)
            
    lines = lines2
    chk+=1
 
       
   
               
for line in lines:
    # 검출된 선 그리기 ---
    # print(line[0])
    x1, y1, x2, y2 = line[0]
#     a,b = cal(x1,y1, x2, y2)
#     if( a == math.inf or a == -math.inf):
#         cv2.line(image, (x1,0),(x1, h),(255,0,0),1)

#     else :
        
#         cv2.line(image, (0,int(b)),(int(w), int(a*w+b)),(255,0,0),1)  

    cv2.line(image, (x1,y1), (x2, y2), (0,255,0), 1) #연장 안하고 그리기
    

    
# lines = cv2.HoughLines(edged, 1, np.pi/180,150) 

# for line in lines: # 검출된 모든 선 순회
#     print(line[0])
#     r,theta = line[0] # 거리와 각도
    
#     tx, ty = np.cos(theta), np.sin(theta) # x, y축에 대한 삼각비
#     x0, y0 = tx*r, ty*r  #x, y 기준(절편) 좌표
#     # 기준 좌표에 빨강색 점 그리기
#     #cv2.circle(image, (abs(x0), abs(y0)), 3, (0,0,255), -1)
#     # 직선 방정식으로 그리기 위한 시작점, 끝점 계산
#     x1, y1 = int(x0 + w*(-ty)), int(y0 + h * tx)
#     x2, y2 = int(x0 - w*(-ty)), int(y0 - h * tx)
#     # 선그리기
#     cv2.line(image, (x1, y1), (x2, y2), (0,255,0), 1)

cv2.imshow("Canny",image)

# approx=transfer.transfer(target) # 점 4개의 좌표 가져감 


# press q or Esc to close
cv2.waitKey(0)
cv2.destroyAllWindows()