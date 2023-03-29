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
# gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 5,5) #맨 뒤 주변부 보는 영역, 임계값
blurred=cv2.GaussianBlur(gray,(15,15),0)  #(5,5) is the kernel size and 0 is sigma that determines the amount of blur

blurred = cv2.bilateralFilter(blurred, -1,10,5) #에지가 아닌 부분만 blurring 
cv2.imshow("blur2", blurred)


edged=cv2.Canny(blurred,50,50)  # 선으로 표현하기... threshold 둘다 값이 클수록 엣지 검출 어려움
cv2.imshow("Blur",edged)


#### 모폴로지 연산
k = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
# mor = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, k)
mor = cv2.dilate(edged, k)
mor = cv2.erode(mor, k)

cv2.imshow("mor", mor)


edging = edged.copy()

# cv2.HoughLinesP(찾을 이미지, 거리측정 해상도 1, 각도, 직선판단정확도, None, 최소길이,최대간격)
lines = cv2.HoughLinesP(mor, 1, np.pi/1800, 50, None, 100, 10) #확률적 변환


 
       
print(lines.shape)
               
for line in lines:
    # 검출된 선 그리기 ---
    # print(line[0])
    x1, y1, x2, y2 = line[0]
    a,b = cal(x1,y1, x2, y2)
#     if( a == math.inf or a == -math.inf):
#         cv2.line(image, (x1,0),(x1, h),(255,0,0),1)

#     else :
        
#         cv2.line(image, (0,int(b)),(int(w), int(a*w+b)),(255,0,0),1)  

    cv2.line(image, (x1,y1), (x2, y2), (0,255,0), 1) #연장 안하고 그리기
    



cv2.imshow("Canny",image)


cv2.waitKey(0)
cv2.destroyAllWindows()