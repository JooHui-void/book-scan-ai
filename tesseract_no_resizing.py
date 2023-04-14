#!/usr/bin/env python
#
# Scanning script for the Noisebridge book scanner.

import sys
import subprocess
import re
import time
import os
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfFileReader, PdfWriter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
pdfmetrics.registerFont(UnicodeCIDFont('HYGothic-Medium'))

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
from pytesseract import Output
from pytesseract import *
from PIL import Image
from rotation import rotate

pytesseract.tesseract_cmd = R'C:\Program Files\Tesseract-OCR\tesseract'

from pathlib import Path
from typing import Union, Literal, List

from PyPDF2 import PdfWriter, PdfReader


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


image=cv2.imread("test2.jpg") 
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
    #print(x1,y1,x2,y2)

    for idx in range(index+1, len(lines)):
        xx1, yy1, xx2, yy2 = lines[idx][0]
        rad2 = math.atan2(xx2-xx1, yy2-yy1)
        rad2 = math.degrees(rad2)
        # print("---",xx1,yy1,xx2,yy1,"=>",abs(rad2-rad))
        if(abs(rad2 - rad)<115 and abs(rad2 - rad) > 65): # 수직 선분 
            if(len(vertical) <2 ):
                vertical = np.append(vertical,lines[idx], 0)
               
        elif(abs(rad2 - rad)<15 or abs(rad2 - rad) >165): # 평행 선분 
            if(len(horizontal) ==0 ):
                horizontal = np.append(horizontal,lines[idx], 0)
            else:  # 이미 들어온 선분과 비교
                gap1 = abs(x1 - horizontal[0][0])
                gap2 = abs(x1 - xx1)
                if(gap2 > gap1):
                    horizontal[0] = lines[idx][0]
        point = np.empty((0,2))
        if(len(vertical) == 2 and len(horizontal) == 1):
            point = np.append(point,get_crosspt(x1,y1,x2,y2,vertical[0][0],vertical[0][1],vertical[0][2],vertical[0][3]),0)
            point = np.append(point,get_crosspt(vertical[0][0],vertical[0][1],vertical[0][2],vertical[0][3],horizontal[0][0],horizontal[0][1],horizontal[0][2],horizontal[0][3]),0)
            point = np.append(point,get_crosspt(horizontal[0][0],horizontal[0][1],horizontal[0][2],horizontal[0][3],vertical[1][0],vertical[1][1],vertical[1][2],vertical[1][3]),0)
            point = np.append(point,get_crosspt(x1,y1,x2,y2,vertical[1][0],vertical[1][1],vertical[1][2],vertical[1][3]),0) 
            if(len(point) == 4):
                
                if(distance(point[0][0],point[0][1],point[1][0],point[1][1]) * distance(point[1][0],point[1][1],point[2][0],point[2][1]) > Max):
                    Max = distance(point[0][0],point[0][1],point[1][0],point[1][1]) * distance(point[1][0],point[1][1],point[2][0],point[2][1])
                    max_set = point
                    
                   


    cv2.line(image, (x1,y1), (x2, y2), (255,0,0), 5) #연장 안하고 그리기

image2 = image.copy()

for dot in max_set:
    x = int(dot[0])
    y = int(dot[1])
    cv2.line(image2, (x,y), (x,y), (0,255,0), 10)
    
    
# cv2.imshow("line", image2)    
approx=transfer.transfer(max_set) # 점 4개의 좌표 가져감 
# print(max_set)
# pts=np.float32([[0,0],[800,0],[800,800],[0,800]])  #map to 800*800 target window

# op=cv2.getPerspectiveTransform(approx,pts)  #get the top or bird eye view effect
# dst=cv2.warpPerspective(orig,op,(800,800))
# cv2.imshow("Scan",dst)

print(dst)
dst_gray=cv2.cvtColor(dst,cv2.COLOR_BGR2GRAY) 
dst_gray = adaptive.adaptive(dst_gray)
# dst_gray = 255-dst_gray
cv2.imshow("Scanned",dst_gray)
cv2.imwrite("test.jpg", dst_gray)
# rotate(dst_gray)
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
    
save_path = './maked/terreract.pdf'


# cv2.imshow("Canny",image)

# rgb_img = cv2.cvtColor(dst, cv2.COLOR_BGR2RGB)
# cv2.imshow('result',rgb_img)
text = pytesseract.image_to_data(dst_gray, lang = 'kor+eng',output_type = Output.DICT)
text_real = pytesseract.image_to_string(dst_gray, lang = 'kor+eng')
print(text)
# print(text['level'][0])

########################## pdf 에 글자 삽입하기 

pdf_writer = PdfWriter() # 빈 pdf 만들기
pdf_writer.add_blank_page(800,800) # PageObject 리턴

# pdf_writer.pages[0].add_named_destination_array("hello")
pdf_writer.add_outline_item(text_real,0)
## 저장
with open(save_path, 'wb') as f:
    pdf_writer.write(f)
    
packet = io.BytesIO()
can = canvas.Canvas(packet, pagesize=(800,800))
tmp_y = 0
tmp_h = 0
for i in range(0, len(text['level'])):
    if text['conf'][i] > 20:
        x = text['left'][i]
        y = text['top'][i]
        w = text['width'][i]
        h = text['height'][i]
        print(y,h,text['text'][i])
        ver_pos = 800-y-h
        # #### ver_pos와 바로 앞글자의 ver_pos 차가 h/2보다 작다면 같은 라인, 같은 사이즈 
        # #### 저장해놓은 tmp_y와 tmp_h를 사용한다
        # if(i != 0 and abs(ver_pos -(800- text['top'][i-1]-text['height'][i-1])) < 4 and abs(text['height'][i-1]-h)<h/2):
        #     print("a")
        # else:
        #     tmp_y = ver_pos
        #     tmp_h = h
        tmp_y = ver_pos
        tmp_h = h
        can.setFont('HYGothic-Medium', tmp_h)
        can.drawString(x, tmp_y, text['text'][i])
        
can.save()

#move to the beginning of the StringIO buffer
packet.seek(0)

# create a new PDF with Reportlab
new_pdf = PdfReader(packet)
# read your existing PDF
existing_pdf = PdfReader(open(save_path, "rb"))
output = PdfWriter()
# add the "watermark" (which is the new pdf) on the existing page
page = existing_pdf.pages[0]
page.merge_page(new_pdf.pages[0])
output.add_page(page)
# finally, write "output" to a real file
output_stream = open("./maked/destination1.pdf", "wb")
output.write(output_stream)
output_stream.close()
##########################
cv2.waitKey(0)
cv2.destroyAllWindows()