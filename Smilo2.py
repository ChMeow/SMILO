#2: HoG based face detection

from imutils.video import VideoStream
from imutils import face_utils

import dlib,time,cv2,os
import requests
import threading
from threading import Lock, Thread
from neopixel import *
import argparse

#UPLOAD CONFIGURATION
URLFinal = ' '
token='A1E-pfijQduZcLc8fQhwQFAlBEaGBWJc3N'
URL1 = 'https://io.adafruit.com/api/groups/Default/send.json?x-aio-key=faea54aca5d64c069827e0b3e6b0417e&smilometer='
URL2 = '&faced='
URLToken = 'http://translate.ubidots.com/api/postvalue/?token=' + token;
URLVar = '&variable='
URLValue = '&value='
ID01 = '5b97267fc03f974874188a76' # this is smile variable ID
ID02 = '5b972346c03f9744eb829866' # this is number of face ID
UploadTimer = UploadConst= 30 #how many frame to collect before upload

# LED strip configuration:
LED_COUNT      = 1      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STAY       = 3       # How long it takes to set the color back to IDLE
LED_UPLOAD     = 0       # Just for timing
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

#UPLOADING DATA
def send_url(URLFinal):
    global LED_UPLOAD
    LED_UPLOAD = 1
    colorWipe(strip, Color(255, 0, 0)) #Uploading
    try:
        r = requests.get(URLFinal)   # to adafruit
        print ('UPLOADED')
    except requests.exceptions.RequestException as e:
        print ('OFFLINE !!')
        colorWipe(strip, Color(0, 255, 0))  # Offline (G,R,B)
        # Save to text here?

#MAIN PROGRAM
colorWipe(strip, Color(255, 255, 0))  # IDLE wipe (G,R,B)
shape_predictor="shape_predictor_68_face_landmarks.dat" 
print("Loading...")
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(shape_predictor)

print("Warming up...")
#vs = VideoStream(usePiCamera=args["picamera"] > 0).start()
vs = VideoStream(src=0).start()

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
pid=0
count_smile=0
count_eact,count_re,count_le,count_be=0,0,0,0
count_an,count_neu=0,0
ratingcount,rating,ratingsum,ratinghappysum = 0,0,0,0

# loop over the frames from the video stream
while True:
        if(LED_UPLOAD == 1):
            LED_STAY = LED_STAY + 1
            if(LED_STAY == 6):
                LED_UPLOAD = 0
                LED_STAU = 2
        else:
            LED_STAY = LED_STAY - 1
        if(UploadTimer == -1):
            UploadTimer = UploadConst
        UploadTimer = UploadTimer - 1
        frame = vs.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

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
        cv2.imshow("Frame", frame)
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
        print ('H(S): ',count_smile,'H(EB): ',count_eact,'H(LE): ',count_le,'H(RE): ',count_re,'H(BE): ',count_be,'A: ',count_an,'N: ',count_neu, 'R: ',int(rating), 'T: ',UploadTimer)
        #print ('Happy(Smile): ',count_smile,'Happy(EyeBrown): ',count_eact,'Happy(leftEye): ',count_le,'Happy(rightEye): ',count_re,'Happy(BothEye): ',count_be,'Angry: ',count_an,'Neutral: ',count_neu, 'Rating: ',rating)
        rating,e,s,le,re,be,an,neu=0,0,0,0,0,0,0,0
        for rect in rects:
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
                        if(LED_UPLOAD == 0):
                            colorWipe(strip, Color(153, 153, 255))  # Detect wipe (G,R,B)
                            LED_STAY = 3
                        cv2.circle(frame, (x, y), 1, (0, 0, 255), -1)
                        if(i):
                                cv2.putText(frame, str(i), (x, y),cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 255), 1)
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
                                if diff_smile>10 and diff_smile<50 and j!=1:
                                        #print('Smile (Mouth)') #smile based on mouth shape
                                        s=1
                                if diff_up>3:
                                        #print('Eyebrown Up') #Eyebrown motion up?
                                        e=1
                                if diff_leye>2.5 and diff_leye<5:
                                        #print('Happy (right eye)') #eye lifting up during smile
                                        le=1
                                if diff_reye>2.5 and diff_reye<5:
                                        #print('Happy (Left Eye)') #eye lifting up during smile
                                        re=1
                                if diff_eye==1: #2.5<diff_reye<5 and 2.5<diff_leye<5:
                                        #print('Happy (Botheye)')
                                        be=1
                                if diff_ang>4 and j!=1:
                                        #print('Anger')
                                        an=1
                        else:
                                #print('Neutral')
                                neu=1                                
                             
                        i=i+1

        if s:
                count_smile=count_smile+1
                ratingcount = ratingcount + 1
        if e:               
                count_eact=count_eact+1
                ratingcount = ratingcount + 1
        if le:
                count_le=count_le+1
                #ratingcount = ratingcount + 1
        if re:
                count_re=count_re+1
                #ratingcount = ratingcount + 1
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
                rating = (10*count_smile + 8*count_eact + 0*count_le + 0*count_re + 8*count_be + 0.2*count_an + 5*count_neu)/ratingcount*10
                #cv2.putText(frame,'Rating: ' + str(rating), (50, 50),cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)
                if(UploadTimer == 0):
                    URLFinal = URLToken + URLVar + ID01 + URLValue + str(rating) + URLVar + ID02 + URLValue + str(0)
                    UploadTimer = UploadConst
                    count_smile=0
                    count_eact,count_re,count_le,count_be=0,0,0,0
                    count_an,count_neu=0,0
                    ratingcount,rating,ratingsum,ratinghappysum = 0,0,0,0
                    threading.Thread(target=send_url, args=(URLFinal,)).start()       
        
        cv2.imshow("Frame", frame)
        if (LED_STAY == 0):
            colorWipe(strip, Color(255, 255, 0))  # IDLE wipe (G,R,B)

        k = cv2.waitKey(10) & 0xff # ESC to exit
        if k == 27:
            break
 
# Exit
VideoStream(src=0).stop()
cv2.destroyAllWindows()


