#2: HoG based face detection

import RPi.GPIO as GPIO
from imutils.video import VideoStream
from imutils import face_utils
import dlib,time,cv2,os
import requests
import threading
from threading import Lock, Thread
from neopixel import *
import argparse
from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
import os
lock = Lock()

print("Loading... UNIT3", end="")

# LED strip configuration:
LED_COUNT      = 1      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STAY       = 0       
LED_STAYS      = 2       # How long it takes to set the color back to IDLE
LED_UPLOAD     = 0       # Just for timing
LED_HALT       = False
parser = argparse.ArgumentParser()
parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
args = parser.parse_args()
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()

#LED CONTROL
def colorWipe(strip, color, wait_ms=50):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
    
#RAINBOW LED
def rainbow(strip, wait_ms=10, iterations=1):
    #print('rainbow')
    i = 0
    global LOADING
    while LOADING:
        if (i < 84):
            colorWipe(strip, Color(i*3, 255-3*i, i))
        else:
            i = 0
        i = i + 1
        time.sleep(wait_ms/1000)
    colorWipe(strip, Color(255, 255, 0))

# LOADING
LOADING = 1
threading.Thread(target=rainbow, args=(strip,)).start()

#UPLOAD CONFIGURATION
URLFinal = ' '
token='A1E-pfijQduZcLc8fQhwQFAlBEaGBWJc3N'
URL1 = 'https://io.adafruit.com/api/groups/Default/send.json?x-aio-key=faea54aca5d64c069827e0b3e6b0417e&smilometer='
URL2 = '&faced='
URLToken = 'http://translate.ubidots.com/api/postvalue/?token=' + token;
URLVar = '&variable='
URLValue = '&value='
ID01 = '5bf21f8fc03f97014399f536' # this is smile variable ID
ID02 = '5bbc1a5bc03f97621d77062d' # this is number of face ID
UploadTimer = UploadConst= 30 #how many frame to collect before upload
OfflineSave = True #Accumulate data when offline
Offline = False #Don't change this, 0 is online, 1 is offline, 2 is waiting status
statusSkip = False #Cosmetic purpose
Eva = False

#UPLOADING DATA
def send_url(URLFinal):
    global LED_STAY
    global Offline
    global statusSkip
    lock.acquire
    LED_STAY = LED_STAYS
    statusSkip = True 
    lock.release
    colorWipe(strip, Color(255, 0, 0)) #Uploading
    try:
        r = requests.get(URLFinal)   # to adafruit
        print ("[ UPLOADED ]\n")
        lock.acquire
        Offline = False
        statusSkip = False 
        lock.release
    except requests.exceptions.RequestException as e:
        print ("[ OFFLINE ]\n")
        colorWipe(strip, Color(0, 255, 0))  # Offline (G,R,B)
        lock.acquire
        Offline = True
        statusSkip = False
        lock.release
        # Save to text here?
        
#GPIO Button
ShutdownGPIOPin = 21
ResetWifiPin = 20
GPIO.setmode(GPIO.BCM)
GPIO.setup(ShutdownGPIOPin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(ResetWifiPin, GPIO.IN, pull_up_down = GPIO.PUD_UP)

def Shutdown(channel):
    LED_HALT = True
    time.sleep(0.5)
    colorWipe(strip, Color(255, 255, 255))
    print ("Halt")
    os.system("sudo halt")
    
def ResetWifi(channel):
    #os.system("wpa_cli -i wlan0 reconfigure")
    colorWipe(strip, Color(51, 255, 255))
    colorWipe(strip, Color(51, 255, 255))
    colorWipe(strip, Color(51, 255, 255))
    colorWipe(strip, Color(51, 255, 255))
    colorWipe(strip, Color(51, 255, 255))
    print ("Alive")
    
GPIO.add_event_detect(ShutdownGPIOPin, GPIO.FALLING, callback = Shutdown, bouncetime = 2000)
GPIO.add_event_detect(ResetWifiPin, GPIO.FALLING, callback = ResetWifi, bouncetime = 2000)
#PiCamSetting
PiCam = True
if(PiCam):
    resolutionX = 1024  # High resolution capture can cover more face with significant performance impact. *use resize to reduce lag
    resolutionY = 768
    resizeFrame = True
    resizeX = 640     #resize to smaller resolution to improve performance
    resizeY = 480
    #time.sleep(2.0)
    camera = PiCamera()
    camera.resolution = (resolutionX, resolutionY)
    camera.framerate = 30 
    rawCapture = PiRGBArray(camera, size=(resolutionX, resolutionY))

# MAIN PROGRAM
#colorWipe(strip, Color(255, 255, 0))  # IDLE wipe (G,R,B)
shape_predictor="/home/pi/Desktop/Smilo2/shape_predictor_68_face_landmarks.dat" 

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(shape_predictor)
print('[ OK ]')
print("Warming up...", end="")

#vs = VideoStream(usePiCamera=args["picamera"] > 0).start()
if(PiCam):
    PiCam = PiCam

time.sleep(2.0)

j=0
p=[(0,0)]*68
p1=[(0,0)]*68
d=[(0,0)]*68
dist_smilo=0
dist_leyeo=0
dist_reyeo=0
dist_ango=0
dup1,dup2=0,0
diff_chx,diff_chy=0,0
count_smile=0
count_eact,count_re,count_le,count_be=0,0,0,0
count_an,count_neu=0,0
count_face,count_facebuffer = 0,0
ratingcount,rating,ratingsum,ratinghappysum,ratingbuffer = 0,0,0,0,0
offlinerating,offlinecount,offlinepeople,offlinefinalize = 0,0,0,0
TIME = 0
neutest = 0
savenow = 0
LOADING = 0
print('[ OK ]')

# loop over the frames from the video stream
for img in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        Eva = False
        start = time.time()
        if(UploadTimer == -1):
            UploadTimer = UploadConst
        UploadTimer = UploadTimer - 1
        if(statusSkip == False and UploadTimer!=0):
            print('Evaluating > ', end="")
            Eva = True
        frame = img.array
        if(resizeFrame == True):
            frame = cv2.resize(frame,(resizeX,resizeY))
            frame = cv2.flip(frame, -1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        img.truncate(0)
        
        # detect faces in the grayscale frame
        rects = detector(gray, 0)
        diff_smile=0
        diff_ang=0
        diff_leye=0
        diff_eye=0
        diff_reye=0
        diff_up=0
        diff_change=0
        if j%2==0:
                p=p1
                p1=[(0,0)]*68
                d=[(0,0)]*68
        # loop over the face detections
        x49=0
        y49=0
        x55=0
        y55=0
        x23=0
        y23=0
        x22=0
        y22=0
        x38=0
        y38=0
        x41=0
        y41=0
        x44=0
        y44=0
        x47=0
        y47=0
        #print ('H(S): ',count_smile,'H(EB): ',count_eact,'H(LE): ',count_le,'H(RE): ',count_re,'H(BE): ',count_be,'A: ',count_an,'N: ',count_neu, 'R: ',int(rating), 'F(R): ',len(rects), 'F(S): ',count_face, 'T: ',UploadTimer , 'FPS: ', '%.3f' % TIME)
        
        e,s,le,re,be,an,neu=0,0,0,0,0,0,0
        
        for rect in rects:
                colorWipe(strip, Color(153, 153, 255)) # Detect wipe (G,R,B)
                LED_STAY = LED_STAYS
                # determine the facial landmarks for the face region, then
                # convert the facial landmark (x, y)-coordinates to a NumPy
                # array
                
                shape = predictor(gray, rect)
                shape = face_utils.shape_to_np(shape)

                # loop over the (x, y)-coordinates for the facial landmarks
                # and draw them on the image
                i=1
                # print('iter'+str(j)) founded face or analyzed
                x1,y1,w,h=0,0,0,0
                j=j+1
                for (x, y) in shape:
                        if i==1:
                                x1=x
                                y1=y-40
                                
                                
                                if j%2!=0:
                                        dup1=x1
                                        dup2=y1
                                        diff_chx,diff_chy=0,0
                                else:
                                        diff_chx=dup1-x1
                                        diff_chy=dup2-y1
                                

                        elif i==9:
                                h=y-y1
                        elif i==17:
                                w=x-x1

                        elif i==20:
                                if j%2!=0:
                                        y_20=y-y1
                                else:
                                        y20=y-y1
                                        diff_up=y_20-y20
                                                                
                        elif(i==49):
                                x49=x
                                y49=y
                        elif(i==55):
                                x55=x
                                y55=y

                                dist_smile=((x49-x55)**2+(y49-y55)**2)**0.5
                                
                                diff_smile=(dist_smile)-dist_smilo
                                if diff_smile<0:
                                        diff_smile*=-1

                                if j==1 or diff_smile>15:
                                        dist_smilo=dist_smile
                                        
                                        
                                if diff_smile<6:
                                        dist_smilo=(dist_smilo+dist_smile)//2

                        elif(i==38):
                                x38=x
                                y38=y
                        elif(i==41):
                                x41=x
                                y41=y
                                dist_leye=((x38-x41)**2+(y38-y41)**2)**0.5
                                diff_leye=(dist_leye)-dist_leyeo

                                if diff_leye<0:
                                        diff_leye=diff_leye*-1

                                if j==1 or diff_leye>2:
                                        dist_leyeo=dist_leye
                                                                            
                                if diff_leye<1:
                                        dist_leyeo=(dist_leyeo+dist_leye)//2                                
                        elif(i==44):
                                x44=x
                                y44=y
                        elif(i==47):
                                x47=x
                                y47=y
                                dist_reye=((x44-x47)**2+(y44-y47)**2)**0.5
                                
                                diff_reye=(dist_reye)-dist_reyeo

                                if diff_reye<0:
                                        diff_reye=diff_reye*-1

                                if j==1 or diff_reye>2:
                                        dist_reyeo=dist_reye
                                        
                                diff=(dist_reye-dist_leye)-(dist_reyeo-dist_leyeo)
                                if diff<0:
                                        diff=diff*-1
                                if diff_leye+diff_reye>2 and diff_leye+diff_reye<4 and (diff<0.5):
                                        diff_eye=1
                                        
                                if diff_reye<1:
                                        dist_reyeo=(dist_reyeo+dist_reye)//2   
        
                        elif(i==22):
                                x22=x
                                y22=y
                        elif(i==23):
                                x23=x
                                y23=y
                                dist_ang=((x22-x23)**2+(y23-y23)**2)**0.5
                                diff_ang=(dist_ang)-dist_ango
                                if diff_ang<0:
                                        diff_ang*=-1

                                if j==1:
                                        dist_ango=dist_ang                                       
                                        
                                if diff_ang<=5:
                                        dist_ango=(dist_ango+dist_ang)//2

                        if diff_chx<10 and diff_chy<10:
                                neutest = 0
                                if diff_smile>10 and diff_smile<50 and j!=1:
                                        #print('Smile (Mouth)') #smile based on mouth shape
                                        s=1
                                        neutest = 1
                                if diff_up>3:
                                        #print('Eyebrown Up') #Eyebrown motion up?
                                        e=1
                                        neutest = 1
                                if diff_leye>2.5 and diff_leye<5:
                                        #print('Happy (right eye)') #eye lifting up during smile
                                        le=1
                                        neutest = 1
                                if diff_reye>2.5 and diff_reye<5:
                                        #print('Happy (Left Eye)') #eye lifting up during smile
                                        re=1
                                        neutest = 1
                                if diff_eye==1: #2.5<diff_reye<5 and 2.5<diff_leye<5:
                                        #print('Happy (Botheye)')
                                        be=1
                                        neutest = 1
                                if diff_ang>4 and j!=1:
                                        #print('Anger')
                                        an=1
                                        neutest = 1
                                if neutest == 0:
                                        neu=1
                        else:
                            #print('Neutral')
                            neu=1                                
                             
                        i=i+1

        if(len(rects) != count_facebuffer):
                count_face = count_face + len(rects)
                count_facebuffer = len(rects)
                savenow = 1

        if(savenow == 1):
                ratingbuffer = ratingbuffer + rating
                rating,count_smile,count_eact,count_le,count_re,count_be,count_an,count_neu,ratingcount=0,0,0,0,0,0,0,0,0
                savenow = 0                
        if s:
                count_smile=count_smile+1
                ratingcount = ratingcount + 1
        if e:               
                count_eact=count_eact+1
                ratingcount = ratingcount + 1
        if le:
                count_le=count_le+1
                ratingcount = ratingcount + 1
        if re:
                count_re=count_re+1
                ratingcount = ratingcount + 1
        if be:
                count_be=count_be+1
                ratingcount = ratingcount + 1
        if an:
                count_an=count_an+1
                ratingcount = ratingcount + 1
        if neu:
                count_neu=count_neu+1
                ratingcount = ratingcount + 1
            
        if(ratingcount != 0):                
                rating = (10*count_smile + 8*count_eact + 8*count_le + 8*count_re + 9*count_be + 0.5*count_an + 5.5*count_neu)/ratingcount*10
                
        if(UploadTimer == 0):
                ratingbuffer = rating + ratingbuffer
                    #rating = ratingbuffer/count_face
                    
                if(Offline == False):
                    offlinerating,offlinecount,offlinepeople = 0,0,0
                    
                if(OfflineSave == True and (offlinerating !=0 or ratingbuffer != 0)):
                    offlinerating = offlinerating + ratingbuffer
                    ratingbuffer = 0
                    #offlinecount = offlinecount + 1
                    offlinepeople = offlinepeople + count_face
                    offlinefinalize = offlinerating/offlinepeople
                    
                    URLFinal = URLToken + URLVar + ID01 + URLValue + str('%.3f' % offlinefinalize) + URLVar + ID02 + URLValue + str(offlinepeople)
                    print( "\nUPLOADING {R = " + str('%.3f' % offlinefinalize) + ', F = ',str(offlinepeople) + "} ... ", end ="")
                    UploadTimer = UploadConst
                    count_smile=0
                    count_eact,count_re,count_le,count_be=0,0,0,0
                    count_an,count_neu=0,0
                    count_face,count_facebuffer = 0,0
                    ratingcount,rating,ratingsum,ratinghappysum = 0,0,0,0                        
                    threading.Thread(target=send_url, args=(URLFinal,)).start()
                    
                    
##                else:    
##                    URLFinal = URLToken + URLVar + ID01 + URLValue + str(rating) + URLVar + ID02 + URLValue + str(count_face)
##                    UploadTimer = UploadConst
##                    count_smile=0
##                    count_eact,count_re,count_le,count_be=0,0,0,0
##                    count_an,count_neu=0,0
##                    count_face,count_facebuffer = 0,0
##                    ratingcount,rating,ratingsum,ratinghappysum = 0,0,0,0
##                    threading.Thread(target=send_url, args=(URLFinal,)).start()       
                
                    
                    
        if(LED_STAY == 0 and LED_HALT == False):
            colorWipe(strip, Color(255, 255, 0))  # IDLE wipe (G,R,B)
        else:
            LED_STAY = LED_STAY - 1
        end = time.time()
        TIME = end - start
        TIME = 1/TIME
        #print ('R: ',int(rating), ',F(R): ',len(rects), '(C): ',count_face, ',T: ',UploadTimer , ',FPS: ', '%.3f' % TIME, 'B: ', ratingbuffer)
        #print ('Realtime[R:',int(rating), ',F: ',len(rects), '], Cumulative[R: ', int(offlinerating + ratingbuffer + rating),' ,F: ',count_face + offlinepeople, '], T: ',UploadTimer , ',FPS: ', '%.3f' % TIME)
        if(statusSkip == False and Eva == True):
            print ('[R:',int(rating), '\tF:',len(rects), '\tT:',UploadTimer , '\tFPS:', '%.3f' % TIME, ']')
        k = cv2.waitKey(10) & 0xff # ESC to exit
        if k == 27:
            break
 
# Exit
cv2.destroyAllWindows()


