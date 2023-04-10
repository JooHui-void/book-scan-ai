import numpy as np
import cv2

def rotate(image):
    image=cv2.GaussianBlur(image,(15,15),0) 
    image=cv2.cvtColor(image,cv2.COLOR_RGB2GRAY) 
   
    cv2.imshow("image", image)
    
    
    return blurred
    