#main.py
#remote sensor prototype
#Import List
from sht import t, h
import lib.RFM.adafruit_rfm9x as RFM
import digitalio as DIO
import board as BO
import busio as BU
import time as TI

import microcontroller

#Constructors
sleep=TI.sleep
digIO=DIO.DigitalInOut
rfm9x=RFM.RFM9x
#Relay Object
#SPI Object
spi=BU.SPI(BO.GP10, MOSI=BO.GP11, MISO=BO.GP12)
cs=digIO(BO.GP13)
rst=digIO(BO.GP15)
#RF Frequency (MHz)
rf=915.0
#Radio Object
radio=rfm9x(spi, cs, rst, rf)
#Board Led
led=digIO(BO.LED)
led.direction=DIO.Direction.OUTPUT
led.value=True #On when Pico is powered and running
#common variables
loopID=0
LID=str(loopID)
com=','
mainDelay=60
ofrDelay=30 #Out-oF-Range
leDel=0.5
#Range. Minimum and Maximum Values. See Below
#https://www.grainscanada.gc.ca/en/grain-quality/manage/manage-storage-prevent-infestations/prevent-spoilage.html
#https://pami.ca/wp-content/uploads/2021/10/Equilibrium-Moisture-Content-Charts-for-Grain-Storage-Management_rev2.pdf
#Currently Unset
tempMax=25.99
tempMin=19.99
humiMax=100.99
humiMin=30
#Main Loop
while True:
    #Loop Local Variables
    loopID += 1
    LID=str(loopID)
    temp=float(t())
    humi=float(h())
    bt = microcontroller.cpu.temperature
    boT = ('{0:0.2f}'.format(bt))
    #If Sensor is returning None. 
    if temp is None or humi is None:
        A=1
        #attempt 30 times
        while (A == 30):
            A += 1
            temp=t()
            if temp is not None and humi is not None:
                break
            else:
                #If unsucessful after 30 tries pico will blink led to indicate an Error State
                while True:
                    sleep(leDel)
                    led.value=False
                    sleep(leDel)
                    led.value=True
    #Sensor Returns a Value
    #If the Value is Out-oF-Range the time between the readings (Delay) will be reduced. If readings are nominal, Delay is increased.
    else:
        #If Temperature is higher than the definded max. Data has a HighTemp Code. Fan is On heater is Off.
        if temp > tempMax:
            Delay=ofrDelay
            readDelay=str(Delay)
            data=(LID + com + readDelay + com + "HighTemp" + com + str(temp) + com + str(humi) + com + str(boT))
        #If Temperature is lower than the defined min. Data has a LowTemp Code. Fan and Heater are On.
        elif temp < tempMin:
            Delay=ofrDelay
            readDelay=str(Delay)
            data=(LID + com + readDelay + com + "LowTemp" + com + str(temp) + com + str(humi) + com + str(boT))
        #If Humidity is higher than the definded max. Data has HighTemp Code. Fan and Heater are On.
        elif (humi > humiMax):
            Delay=ofrDelay
            readDelay=str(Delay)
            data=(LID + com + readDelay + com + "HighHumi" + com + str(temp) + com + str(humi) + com + str(boT))
        #If Humidity is Lower than the definded min. Data has LowHumi code. Fan is On Heater is Off.
        elif (humi < humiMin):
            Delay=ofrDelay
            readDelay=str(Delay)
            data=(LID + com + readDelay + com + "LowHumi" + com + str(temp) + com + str(humi) + com + str(boT))
        #Good Readings are indicated by a Good Code. Both fan and heater and turned off. Delay is increased.
        else:
            Delay=mainDelay
            readDelay=str(Delay)
            data=(LID + com + readDelay + com + "Good" + com + str(temp) + com + str(humi) + com + str(boT))
            #Send Data to Radio1        
    radio.send(data)
    #Led Indicates Data is Sent
    led.value=False
    sleep(leDel)
    led.value=True
    print(data) #uncomment to test
    sleep(Delay)
led.value=False
exit(0)
#(c) Marcus Dechant 2022