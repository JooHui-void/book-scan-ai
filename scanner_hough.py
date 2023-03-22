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


    

image=cv2.imread("image1.jpg") 
image=cv2.resize(image,(1300,800)) #resizing
h, w = image.shape[:2]
orig=image.copy()

gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY) 

gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 5,5) #맨 뒤 주변부 보는 영역, 임계값
blurred = cv2.bilateralFilter(gray, -1,10,5)
# blurred=cv2.GaussianBlur(gray,(3,3),0)  #(5,5) is the kernel size and 0 is sigma that determines the amount of blur


edged=cv2.Canny(blurred,10,100)  # 선으로 표현하기...
cv2.imshow("Blur",edged)
edging = edged.copy()

# cv2.HoughLinesP(찾을 이미지, 거리측정 해상도 1, 각도, 직선판단정확도, None, 최소길이,최대간격)
lines = cv2.HoughLinesP(edged, 1, np.pi/180, 10, None, 10, 2) #확률적 변환

# 라인 병합 알고리즘
print(len(lines))
for line in lines:
    # 검출된 선 그리기 ---
    x1, y1, x2, y2 = line[0]
    cv2.line(image, (x1,y1), (x2, y2), (0,255,0), 1)
    
# lines = cv2.HoughLines(edged, 1, np.pi/180,150) 

# for line in lines: # 검출된 모든 선 순회
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