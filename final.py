#!/usr/bin/env python3 
#General
import RPi.GPIO as GPIO
import time
#LCD
import busio
import digitalio
import board
import adafruit_pcd8544
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
#Multiprocessing
from multiprocessing import Process
import sys
rocket = 0
#Ubeac
import requests
#Webserver
import os.path

GPIO.setmode(GPIO.BCM)
ULTR_TRIG_PORT = 5      #Ultrasonische trigger poort
ULTR_ECHO_PORT = 6      #Ultrasonische echo poort

RELAY_PORT_1 = 26       #Relay port 1 = LAMP
RELAY_PORT_2 = 19       #Relay port 2 = POMP

MOTOR_PORT_IN1 = 21     #Motor poorten in
MOTOR_PORT_IN2 = 20
MOTOR_PORT_IN3 = 16
MOTOR_PORT_IN4 = 12

BUTTON_1 = 14      #Button ports van links naar rechts op het breadboard
BUTTON_2 = 15
BUTTON_3 = 18
BUTTON_4 = 4

url = "UBEAC_URL"
uid = "USER_ID"


GPIO.setup(ULTR_TRIG_PORT,GPIO.OUT)     #Trigger port moet outputten -> sturen van geluid
GPIO.setup(ULTR_ECHO_PORT,GPIO.IN)      #Echo port moet inputten -> ontvangen van geluid

GPIO.setup(RELAY_PORT_1,GPIO.OUT)       #Relay port 1 moet outputten -> sturen van aan/uit signaal
GPIO.setup(RELAY_PORT_2,GPIO.OUT)       #Relay port 2 moet outputten -> sturen van aan/uit signaal

GPIO.setup( MOTOR_PORT_IN1, GPIO.OUT )  #Alle pinnen van de motor als output instellen
GPIO.setup( MOTOR_PORT_IN2, GPIO.OUT )
GPIO.setup( MOTOR_PORT_IN3, GPIO.OUT )
GPIO.setup( MOTOR_PORT_IN4, GPIO.OUT )

GPIO.setup( BUTTON_1, GPIO.IN )  #Alle pinnen van de buttons als input instellen
GPIO.setup( BUTTON_2, GPIO.IN )
GPIO.setup( BUTTON_3, GPIO.IN )
GPIO.setup( BUTTON_4, GPIO.IN )




#SETUP LCD ---------------------------------------------------------------------------------------------------
# Initialize SPI bus
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

# Initialize display - overgenomen...
dc = digitalio.DigitalInOut(board.D23)  # data/command
cs1 = digitalio.DigitalInOut(board.CE1)  # chip select CE1 for display
reset = digitalio.DigitalInOut(board.D24)  # reset
display = adafruit_pcd8544.PCD8544(spi, dc, cs1, reset, baudrate= 1000000)
display.bias = 4
display.contrast = 60
display.invert = True

#  Display "legen"
display.fill(0)
display.show()

# Tekenobject aanmaken voor schrijven op display
image = Image.new('1', (display.width, display.height)) 
draw = ImageDraw.Draw(image)
 	

#tekstgrootte definieren en symbolattf voor emoji support toevoegen
font_size = 12
unicode_font = ImageFont.truetype("Symbola.ttf", font_size)


#Scherm leegmaken -> anders alles zwart
draw.rectangle((0, 0, display.width, display.height), outline=255, fill=255)

#END SETUP LCD ---------------------------------------------------------------------------------------------------
#START SETUP MOTOR
motor_step_delay = 0.002
motor_steps_total = 4096
motor_forward = True
#http://www.4tronix.co.uk/arduino/Stepper-Motors.php
motor_seq = [[1,0,0,1],
                [1,0,0,0],
                [1,1,0,0],
                [0,1,0,0],
                [0,1,1,0],
                [0,0,1,0],
                [0,0,1,1],
                [0,0,0,1]]
motor_ports = [MOTOR_PORT_IN1,MOTOR_PORT_IN2,MOTOR_PORT_IN3,MOTOR_PORT_IN4]
motor_step_counter = 0

GPIO.output( MOTOR_PORT_IN1, GPIO.LOW )
GPIO.output( MOTOR_PORT_IN2, GPIO.LOW )
GPIO.output( MOTOR_PORT_IN3, GPIO.LOW )
GPIO.output( MOTOR_PORT_IN4, GPIO.LOW )
    





ct = u"\U0001f567" + ": " #Current time emoji
nextfeed = u"\U0001f6ce" + ": " #Timer sort of emoji
water = u"\U0001f30a" + ": " #Water emoji
lampstate = u"\U0001f4a1" + ": " #Lamp state emoji



draw.text((1,0), ct, font=unicode_font)
draw.text((1,font_size), nextfeed, font=unicode_font)
draw.text((1,2*font_size), water, font=unicode_font)
draw.text((1,3*font_size+1), lampstate, font=unicode_font)

display.image(image)

display.show()

# getekende image weghalen (=rij leegmaken) & nieuwe lijn tekenen
def drawRow(row,value):
    draw.rectangle((1, row*font_size, display.width, (row + 1)*font_size), outline=255, fill=255)
    draw.text((1,row*font_size), value, font=unicode_font)
    display.image(image)
    display.show()


def getCurrentTime():
    time_current = time.time()
    current_time = time.localtime(time_current)
    drawRow(0,ct + str(current_time.tm_hour) + ":" + str(current_time.tm_min))
    #print("Current time :",str(current_time.tm_hour) + ":" + str(current_time.tm_min))



#Ultrasonische sensor lezing
def getUltrasonicReadings():
    GPIO.output(ULTR_TRIG_PORT,0)
    time.sleep(1)
    
    echohigh = 0
    echolow = 0

    GPIO.output(ULTR_TRIG_PORT,1)
    time.sleep(0.00001)
    GPIO.output(ULTR_TRIG_PORT,0)

    while(GPIO.input(ULTR_ECHO_PORT) == 0):
        echohigh = time.time()
    while(GPIO.input(ULTR_ECHO_PORT) == 1):
        echolow = time.time()
    echopassed = echolow - echohigh
    distance = round(echopassed * 17000,2)
    drawRow(2,water + str(distance) + " CM")
    print("Distance :",str(distance),"cm")

    data = {
    "id": uid,
    "sensors":[{
    'id': 'water height',
    'data': distance
    }]
    }
    r = requests.post(url, verify = False, json = data)



    time.sleep(2)

LAMP_ON = False
PREV_LAMP_ON = False


def getLampState(button_pressed = False,force_refresh = False):
    lamp_timer = False
    if(os.path.isfile("./webserver/time")):
        lamp_timer = True
        f = open("./webserver/time","r")
        timeout = int(f.readlines()[0])
        if timeout - time.time() < 0:
            lamp_timer = False
            #Toggle light off
            GPIO.output(RELAY_PORT_1,GPIO.HIGH)
            os.remove("./webserver/time")
        else:
            GPIO.output(RELAY_PORT_1,GPIO.LOW)


    global LAMP_ON
    if GPIO.input(RELAY_PORT_1) == GPIO.LOW:
        LAMP_ON = True
    else:
        LAMP_ON = False

    global PREV_LAMP_ON
    if LAMP_ON is not PREV_LAMP_ON:
        PREV_LAMP_ON = LAMP_ON
        if not button_pressed and not lamp_timer:
            drawRow(3,lampstate + "OFF" if GPIO.input(RELAY_PORT_1) == 1 else lampstate + "ON"  )
        elif lamp_timer:
            time_remaining = time.localtime(timeout - time.time())
            drawRow(3,lampstate + str(time_remaining.tm_min) + "min")
        print("Lamp state:",str(LAMP_ON))  
        data = {
        "id": uid,
        "sensors":[{
        'id': 'lamp state',
        'data': 1 if LAMP_ON else 0
        }]
        }
        r = requests.post(url, verify = False, json = data)
    elif force_refresh:
        if not lamp_timer:
            drawRow(3,lampstate + "OFF" if GPIO.input(RELAY_PORT_1) == 1 else lampstate + "ON"  )
        elif lamp_timer:
            time_remaining = time.localtime(timeout - time.time())
            drawRow(3,lampstate + str(time_remaining.tm_min) + "min")



    

def toggleLamp(button_pressed = False):
    GPIO.output(RELAY_PORT_1,0) if GPIO.input(RELAY_PORT_1) == 1 else GPIO.output(RELAY_PORT_1,1)
    getLampState(button_pressed)
        

def motorMove(steps = motor_steps_total,forward = motor_forward):
    steps = int(steps)
    global motor_step_counter
    for i in range(steps):
        for port in range(0, len(motor_ports)):
            GPIO.output( motor_ports[port], motor_seq[motor_step_counter][port] )
        if forward:
            motor_step_counter = (motor_step_counter - 1) % 8
        else:
            motor_step_counter = (motor_step_counter + 1) % 8
        time.sleep(motor_step_delay)

def getButtonPresses():
    BUTTON_1_EXECUTING = False
    BUTTON_3_EXECUTING = False
    BUTTON_4_EXECUTING = False
    PUMP_ON = False
    PREV_PUMP_STATE = False
    
    while True:
        #Check of knop is ingedrukt
        if GPIO.input(BUTTON_1) == 0:
            #Als knop nog niet is aan het uitvoeren voer uit, anders niet
            if BUTTON_1_EXECUTING == False:
                toggleLamp(True)
                BUTTON_1_EXECUTING = True
        else:
            BUTTON_1_EXECUTING = False


        PREV_PUMP_STATE = PUMP_ON
        if GPIO.input(BUTTON_2) == 0:
            #zet pomp aan
            PUMP_ON = True
            GPIO.output(19,GPIO.LOW)
        else:
            #zet pomp uit
            PUMP_ON = False
            GPIO.output(19,GPIO.HIGH)
            

        if PUMP_ON is not PREV_PUMP_STATE:
            data = {
            "id": uid,
            "sensors":[{
            'id': 'pump state',
            'data': 1 if PUMP_ON else 0
            }]
            }
            r = requests.post(url, verify = False, json = data)
            print("Pump state: " + str(PUMP_ON))


        if GPIO.input(BUTTON_3) == 0:
            #Als knop nog niet is aan het uitvoeren voer uit, anders niet
            if BUTTON_3_EXECUTING == False:
                motorMove(motor_steps_total * 1/4,True)
                BUTTON_3_EXECUTING = True
        else:
            BUTTON_3_EXECUTING = False


        if GPIO.input(BUTTON_4) == 0:
            #Als knop nog niet is aan het uitvoeren voer uit, anders niet
            if BUTTON_4_EXECUTING == False:
                motorMove(motor_steps_total * 1/4,False)
                BUTTON_4_EXECUTING = True
        else:
            BUTTON_4_EXECUTING = False
        
        time.sleep(0.5)










try:
    ps_checkbuttons = Process(target = getButtonPresses)
    ps_checkbuttons.start()

    #Om de hoeveel seconden de motor aangaat
    motor_timeout = 60 * 60 * 12
    motor_now = ""

    while True:
        getCurrentTime()
        getUltrasonicReadings()
        getLampState(False,True)
        if not motor_now or time.time() - motor_now > motor_timeout:
            motorMove(motor_steps_total * 1/4,True)
            motor_now = time.time()
            motor_next_feed = time.localtime(motor_now + motor_timeout)
            drawRow(1,nextfeed + str(motor_next_feed.tm_hour) + ":" + str(motor_next_feed.tm_min))
        

        

except KeyboardInterrupt:
    GPIO.cleanup()