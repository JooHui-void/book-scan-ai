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
import adaptive

    

image=cv2.imread("image3.jpg") 
image=cv2.resize(image,(1300,800)) #resizing
h, w = image.shape[:2]
orig=image.copy()

gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY) 
# gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 5,5) #맨 뒤 주변부 보는 영역, 임계값
blurred=cv2.GaussianBlur(gray,(15,15),0)  #(5,5) is the kernel size and 0 is sigma that determines the amount of blur

blurred = cv2.bilateralFilter(blurred, -1,10,5) #에지가 아닌 부분만 blurring 


edged=cv2.Canny(blurred,30,30)  # 선으로 표현하기... threshold 둘다 값이 클수록 엣지 검출 어려움

#### 모폴로지 연산
k = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
# mor = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, k)
mor = cv2.dilate(edged, k)
mor = cv2.erode(mor, k)





contours,hierarchy=cv2.findContours(mor,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)  #컨투어 검출, 리스트화
contours=sorted(contours,key=cv2.contourArea,reverse=True)

for c in contours:
    
    #### 꼭지점 구하기 
    p=cv2.arcLength(c,True)
    approx=cv2.approxPolyDP(c,0.02*p,True)
########## 
    if len(approx)==4:
        cv2.drawContours(edged,[c],0,(255,0,0),3)
        target=approx
        break

cv2.imshow("Canny",edged)

approx=transfer.transfer(target) # 점 4개의 좌표 가져감 

pts=np.float32([[0,0],[800,0],[800,800],[0,800]])  #map to 800*800 target window

op=cv2.getPerspectiveTransform(approx,pts)  #get the top or bird eye view effect
dst=cv2.warpPerspective(orig,op,(800,800))
cv2.imshow("Scan",dst)
dst_gray=cv2.cvtColor(dst,cv2.COLOR_BGR2GRAY) 
dst_gray = adaptive.adaptive(dst_gray)
cv2.imshow("Scanned",dst_gray)
# press q or Esc to close
cv2.waitKey(0)
cv2.destroyAllWindows()