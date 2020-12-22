from ubidots import ApiClient
import os
import requests

api = ApiClient(token='A1E-pfijQduZcLc8fQhwQFAlBEaGBWJc3N')
isOffline = True
while isOffline:
    try:
        var = api.get_variable('5bf21ec4c03f977f5a4ed8d1')
        new = var.save_value({'value':1})
        isOffline = False
        print('Online')
    except requests.exceptions.RequestException as e:
        print ('offline')
##    except UbidotsForbiddenError as e:
##        print ('offline')
   
while True:
    try:
        switch = var.get_values(1)
        if (switch[0]['value'] == 1):
            print ('on')
        else:
            print('off')
            os.system("tmux kill-session -t smilo")
            os.system("sudo python3 /home/pi/Desktop/led.py")
            #os.system("sudo halt")
            time.sleep(30)
    except BaseException: 
        print ('error')

            
    
