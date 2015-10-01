
from epsonprinter import EpsonPrinter
from PIL import Image
from PIL import ImageEnhance
import RPi.GPIO as GPIO
import os, sys
import time
import datetime
import exceptions

import subprocess
import shlex
import shutil
from optparse import OptionParser
import wget
import re 

command = 'mount -t tmpfs none tmp_images/'

GPIO.setmode(GPIO.BOARD) #pin-nummern
GPIO.setwarnings(False)

GPIO.setup(18, GPIO.IN, pull_up_down = GPIO.PUD_UP) #Taster
        
        
def print_image(file):
    printer = EpsonPrinter(0x04b8, 0x0202)
    printer.set_print_speed(1)
    
    start = time.time()
        
    im = Image.open(file)
    im = im.transpose(Image.ROTATE_270)
    basewidth = 512
    wpercent = (basewidth / float(im.size[0]))
    hsize = int((float(im.size[1]) * float(wpercent)))
    im = im.resize((basewidth, hsize), Image.BICUBIC)
     
    printer.print_image(im)
    printer.linefeed(5)
    printer.cut()
    end = time.time()
    print end - start

def load_and_print():
    for file in os.listdir('/home/pi/bonbooth/tmp_images'):
        os.remove(file)
        
    os.chdir('/home/pi/bonbooth/tmp_images')
    for a in range(0,10):
        url = 'http://taz.de/scripts/tom/tomshuffle.php'
        command = "wget  "+url+' --referer="http://taz.de"'    
        os.system(command)
        #file = wget.download('http://taz.de/scripts/tom/tomshuffle.php',"taz.html")
        tom = open('tomshuffle.php')
        for line in tom:
            line = line.rstrip()
            if re.search('alt="TOM"', line) :
                line = line[130:140]
                id = line.replace('\"', "")
                break     
        os.remove('tomshuffle.php')
        
        url = 'http://m.taz.de/digitaz/.tom/gif.t,tom.d,'+id+'.gif'
        command = "wget  "+url+' --referer="http://taz.de"'    
        os.system(command)      
        
        for file in os.listdir('/home/pi/bonbooth/tmp_images'):
            im = Image.open(file).convert("RGB")
            im.save("tmp.jpg")     
            os.remove(file)            
            print_image("tmp.jpg")
            os.remove("tmp.jpg")
        
        
def run(channel):
    global num_images
    print "taste"
    try: 
        load_and_print()
    except KeyboardInterrupt:
        GPIO.cleanup()

        

run(0)


"""        
GPIO.add_event_detect(18, GPIO.FALLING, callback = run, bouncetime = 15000)  


    
while 1:
    time.sleep(1)

"""    

