import cv2

def adaptive(image):
    
    dst = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 39, 10) # 맨 뒤 두 숫자는 블록 크기, 임계값
    return dst