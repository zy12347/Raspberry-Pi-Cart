import time
import cv2 
import numpy as np
import RPi.GPIO as GPIO
from move import CarMove

GPIO.setwarnings(False)  # Disable warning
GPIO.setmode(GPIO.BCM)  # BCM coding
#定义摄像头
cap = cv2.VideoCapture(0)

car = CarMove()

total_error,error,error_1=0,0,0
Kp,Ki,Kd=0.7,0,0.2

try:
    while (1):
        #读取摄像头画面图像尺寸480*640
        ret, frame = cap.read()
        #降采样为120*160
        frame = cv2.resize(frame,(0,0),fx = 0.25, fy = 0.25, interpolation= cv2.INTER_NEAREST)
        #高斯模糊 平滑图像
        frame1=cv2.GaussianBlur(frame,(5,5),0)
        #转化为灰度图
        gray_ = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        #大津法二值化
        retval, dst = cv2.threshold(gray_,50,255,cv2.THRESH_OTSU)
        #腐蚀
        dst = cv2.erode(dst, None, iterations=2)
        #膨胀
        dst = cv2.dilate(dst, None, iterations=1)
        rows,cols= dst.shape
        center=80
        count=[]
        location1,location2=0,0
        
        temp1,temp2=dst[90],dst[50]
        error=0
        '''
        if temp1[0]==0:
            for j in range(len(temp1)-1):
                if temp1[len(temp1)-1-j]!=temp1[len(temp1)-1-(j+1)]:
                    location1=len(temp1)-1-j
                    break
                if location1==0:
                    location1=159
                
            
            for k in range(len(temp2)-1):
                if temp2[len(temp2)-1-k]!=temp2[len(temp2)-1-(k+1)]:
                    location2=len(temp2)-1-k
                    break
            error=location1-location2
            
            
        elif temp1[len(temp1)-1]==0:
            for j in range(len(temp1)-1):
                if temp1[j]!=temp1[j+1]:
                    location1=j
                    break
                if(location1==159):
                        location1=0
            
            for k in range(len(temp2)-1):
                if temp2[k]!=temp2[k+1]:
                    location2=k
                    break
            error=location1-location2
            '''
        
        for j in range(160-1):
            if temp1[j]!=temp1[j+1]:
                #error=-j
                location1=j
                count.append(j)
                
        if len(count)==0:
            if temp2[0]==0:
                location1=159
            elif temp2[159]==0:
                location1=0
        elif len(count)==1:
            if temp2[0]==0 and temp1[0]==0:
                location1=159
            elif temp2[159]==0 and temp1[159]==0:
                location1=0
        elif len(count)==2:
            location1=int((count[0]+count[1])/2)
        elif len(count)==3:
            if(temp1[0]==0):
                location1=int((count[1]+count[2])/2)
            else:
                location1=int((count[0]+count[1])/2)       
        elif len(count)==4:
            a=(count[0]+count[1])/2
            b=(count[2]+count[3])/2
            if abs(80-a)<abs(80-b):
                location1=int(a)
            else:
                location1=int(b)
                    
            '''
            for k in range(80):
                if temp2[center-k]==0:
                    #error=-j
                    location2=center-k
                    break
                elif temp2[center+k]==0:
                    #error=j
                    location2=center+k
                    break
            '''
        location2=location1
            #error=location1-location2
        #errors.append(error)
        #cv2.circle(dst,(location1,85), 5, (255,255,255), -1)
        cv2.circle(dst,(location1,90), 5, (255,255,255), -1)
        #error=int(sum(errors)/5)
        error=location1-center
        #print(error)
        #error=int(0.6*abs(error))
        #print(error)
        #car.go(error)
        #pid
        print(error)
        total_error=error+total_error
        output=Kp*error+Ki*total_error+Kd*(error-error_1)
        print(output)
        error_1=error
        left_speed=min((20+0.5*output),60)
        right_speed=min((20-0.5*output),60)
        
        if left_speed<0:
            left_speed=0
        if right_speed<0:
            right_speed=0
        
        #car.go(40,40)
        car.go(left_speed,right_speed)
        '''
        if abs(error)<8:
            speed=int(40+error)
            print("forward")
            print(error)
            car.forward(speed)
        
        elif error>8:
            print("right")
            print(error)
            speed=int(20+0.4*error)
            car.right(speed)
        
        elif error<-8:
            print("left")
            print(error)
            speed=int(20-0.4*error)
            car.left(speed)
        '''
        cv2.imshow('gaussian',dst)
        cv2.waitKey(1)
        
except KeyboardInterrupt :
    # 释放清理
    print("Measurement stopped by User")
    car.MotorStop()
    cap.release()
    cv2.destroyAllWindows()
    GPIO.cleanup()