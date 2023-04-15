import cv2
import numpy
kernel = numpy.array([[0, -1, 0],
                   [-1, 5, -1],
                   [0, -1, 0]])

def adaptive(image):
    image = cv2.bilateralFilter(image, -1,10,5) #에지가 아닌 부분만 blurring 
    dst = cv2.filter2D(image, -1, kernel)
    dst = image
    #dst = cv2.adaptiveThreshold(dst, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 39, 10) # 맨 뒤 두 숫자는 블록 크기, 임계값
    dst = 255- dst
    k = cv2.getStructuringElement(cv2.MORPH_RECT, (1,1))
    q = cv2.getStructuringElement(cv2.MORPH_RECT, (1,1))
    # mor = cv2.morphologyEx(dst, cv2.MORPH_CLOSE, q)
    # mor = cv2.morphologyEx(dst, cv2.MORPH_CLOSE, q)
    
    mor = cv2.dilate(dst, k)
    mor = cv2.erode(dst, q)
    return mor 