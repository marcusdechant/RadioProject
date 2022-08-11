#RadioProject
#Remote Sensor Data Logger
#Marcus Dechant (c)
#pico beta
#main.py
#v1.1.3

#import list
from sht import t
from sht import h
import lib.RFM.adafruit_rfm9x as RFM
import digitalio as DIO
import board as bo
import busio as bu
import time as ti
import microcontroller as mc

#Constructors
sl=ti.sleep
dio=DIO.DigitalInOut
rfm=RFM.RFM9x

#SPI Object
spi=bu.SPI(bo.GP10, MOSI=bo.GP11, MISO=bo.GP12)
cs=dio(bo.GP13)
rst=dio(bo.GP15)

#RF Frequency (MHz)
rf=915.0

#High Power Level (max=19dB, min=5dB)
pwr=5

#Radio Object
radio=rfm(spi, cs, rst, rf, high_power=True)

#Board Led
led=dio(bo.LED)
led.direction=DIO.Direction.OUTPUT
led.value=True #On when Pico is powered and running

#common variables
lid=0
delay=30
ledel=0.5

#Delimiter
c=','

#reading range triggers
tempHi=25.01
tempLo=20
humiHi=85
humiLo=30

#dynamic power change trigger
a=120 #loops (120*30s=3600s=1h@30s)

def mct(): #board temp function
    bt=('{0:0.2f}'.format(mc.cpu.temperature))
    return(bt)

while(True): #Main Loop
    lid+=1 #Loop Local Variables
    temp=float(t())
    humi=float(h())
    bt=float(mct())
    
    #If Sensor is returning None. 
    if(temp is None)or(humi is None):
        nid=1
        #attempt 30 times
        while(nid==30):
            nid+=1
            temp=t()
            humi=h()
            if(temp is not None)and(humi is not None):
                break
        while(True): #After 30 tries led will blink indicating an error
            led.value=False
            sl(ledel)
            led.value=True
            sl(ledel)
    
    else: #Sensor Returns a Value
        if(temp>tempHi): #If Temperature is higher than the definded max. Data has a HighTemp Code.
            data=(str(lid)+c+str(delay)+c+"HighTemp"+c+str(temp)+c+str(humi)+c+str(bt))
        elif(temp<tempLo): #If Temperature is lower than the defined min. Data has a LowTemp Code.
            data=(str(lid)+c+str(delay)+c+"LowTemp"+c+str(temp)+c+str(humi)+c+str(bt))
        elif(humi>humiHi): #If Humidity is higher than the definded max. Data has HighTemp Code.
            data=(str(lid)+c+str(delay)+c+"HighHumi"+c+str(temp)+c+str(humi)+c+str(bt))
        elif(humi<humiLo): #If Humidity is Lower than the definded min. Data has LowHumi code.
            data=(str(lid)+c+str(delay)+c+"LowHumi"+c+str(temp)+c+str(humi)+c+str(bt))
        else: #Good Readings are indicated by a Good Code.
            data=(str(lid)+c+str(delay)+c+"Good"+c+str(temp)+c+str(humi)+c+str(bt))
         
    #EXPERIMENTAL
    #Dynamic TX Power Test
    #pwr in dB
    if(lid==a): #if lid = a (120 base)
        a+=a #when triggered a will become thee next hour, ((120+120=240)*30=7200=2h@30s)
        if(pwr>19): #if power level = +19 it is reverted to 5 (lowest)
            pwr=5
        else: #pwr increases by 1 every 120 loops (1 hour)
            pwr+=1
    radio.tx_power=pwr
    
    #Send Data to RXRadio
    radio.send(data)
    #print data to user
    print(data+c+str(pwr))
    #Led Indicates Data is Sent
    led.value=False
    sl(ledel)
    led.value=True
    #reading delay
    sl(delay)
#led off before exit
led.value=False
exit(0)