import config
from epsonprinter import EpsonPrinter
from PIL import Image
from PIL import ImageEnhance
import RPi.GPIO as GPIO
import os, sys
import time
import datetime
import picamera
import exceptions

import subprocess
import shlex
import shutil
from optparse import OptionParser


num_images = config.num_images
save_images = config.save_images
text = config.text 

ready = True

GPIO.setmode(GPIO.BOARD) #pin-nummern
GPIO.setwarnings(False)

GPIO.setup(18, GPIO.IN, pull_up_down = GPIO.PUD_UP) #Taster

GPIO.setup(22, GPIO.OUT) #Lampe Blitz
GPIO.output(22, GPIO.LOW)

GPIO.setup(12, GPIO.OUT) #LED Gruen
GPIO.output(12, GPIO.HIGH)

GPIO.setup(16, GPIO.OUT) #LED Rot
GPIO.output(16, GPIO.LOW)

command = 'mount -t tmpfs none tmp_images/'
subprocess.call(shlex.split(command))

os.chdir('/home/pi/bonbooth/tmp_images')

camera = picamera.PiCamera()


    
def capture_image(num):
    print "capture"
    #camera = picamera.PiCamera()
    try:
        camera.resolution = (1296, 972)
        #camera.rotation = 0
        camera.awb_mode = 'tungsten'
        camera.brightness = 78
        camera.contrast = 85
        camera.iso = 1600
        camera.capture(str(num)+ ".jpg", quality = 90, thumbnail = None, resize = (682, 512))
        camera.stop_preview()
        camera.start_preview()

        print "finished"
        pass
    finally:
        #camera.close()
        print "finished"
        
        
  
def countdown():
    print ("countdown start")
    try:
        for i in range(3):
            GPIO.output(12, GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(12, GPIO.LOW)
            time.sleep(0.5)
        for i in range(6):
            GPIO.output(12, GPIO.HIGH)
            time.sleep(0.1)
            GPIO.output(12, GPIO.LOW)
            time.sleep(0.1)
    except KeyboardInterrupt:
		GPIO.cleanup()
    print ("countdown end")


        
def flashlight(on):
    print ("flash")
    try:
        if on:
            GPIO.output(22, GPIO.HIGH)
            time.sleep(0.2)
        else:
            GPIO.output(22, GPIO.LOW)
    except KeyboardInterrupt:
        GPIO.cleanup()       

        
        
def print_images(num_images):
    printer = EpsonPrinter(0x04b8, 0x0202)
    printer.set_print_speed(1)
    for i in range(num_images):
        start = time.time()
        print "PRINT"
        im = Image.open(str(i)+ ".jpg")

        #brighter = ImageEnhance.Brightness(im)
        #im = brighter.enhance(1.2)
        #contrast = ImageEnhance.Contrast(im)
        #im = contrast.enhance(1.0)

        #verkleinern
        #im = im.resize((682, 512))
        #drehen
        im = im.transpose(Image.ROTATE_90)
                
        #printer.print_file(str(i)+ ".png")
        printer.print_image(im)
        
        if text['show']:
            printer.print_text("\n")
            printer.center()
            if text['row1'] != "":
               printer.print_text(text['row1'])
               printer.print_text("\n")
            if text['row2'] != "":
               printer.print_text(text['row2'])
               printer.print_text("\n")
            if text['row3'] != "":
               printer.print_text(text['row3'])
            if text['date']:
               printer.print_text("\n")
               printer.print_text(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
               
        printer.linefeed(7)
        printer.cut()
        end = time.time()
        print end - start


        
def copy_images(num_images):
    for i in range(num_images):
        #im = Image.open(str(i)+".png")
        #im.save("/home/pi/thermobooth/images/"+ (str(datetime.datetime.utcnow()))+ ".jpg", "JPEG")
        shutil.copy(str(i)+".jpg","/home/pi/bonbooth/images/"+ (str(datetime.datetime.utcnow()))+ ".jpg")
        print "COPY"

        
        
def run(channel):
    global ready
    global num_images
    print "taste"
    try:
        if ready:
            #GPIO.remove_event_detect(18)        
            ready = False
            GPIO.output(12, GPIO.LOW)
            time.sleep(0.05)
            for i in range(num_images):
                countdown()
                flashlight(True)
                capture_image(i)
                flashlight(False)
            print_images(num_images)
            if save_images:
                copy_images(num_images)
                time.sleep(0.1)
            ready = True
            GPIO.output(12, GPIO.HIGH)
            #GPIO.add_event_detect(18, GPIO.FALLING, callback = run, bouncetime = 1000)
            time.sleep(0.01)
    except KeyboardInterrupt:
        GPIO.cleanup()

        

GPIO.add_event_detect(18, GPIO.FALLING, callback = run, bouncetime = 15000* num_images)    

#camera = picamera.PiCamera()
camera.start_preview()

while 1:
    time.sleep(1)

    