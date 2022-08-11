#RadioProject
#Remote Sensor Data Logger
#Marcus Dechant (c)
#pico beta
#main.py
#v1.1.2

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
out=DIO.Direction.OUTPUT
rfm=RFM.RFM9x

#SPI Object
spi=bu.SPI(bo.GP10, MOSI=bo.GP11, MISO=bo.GP12)
cs=dio(bo.GP13)
rst=dio(bo.GP15)

#RF Frequency (MHz)
rf=915.0

#High Power Toggle (+20dB)
hp=(high_power=True)
pwr=20

#Radio Object
radio=rfm(spi, cs, rst, rf, hp)

#Board Led
led=digIO(bo.LED)
led.direction=out
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

def mct(): #board temp function
    mct=mc.cpu.temperature
    bt=('{0:0.2f}'.format(mct))
    return(bt)

while(True): #Main Loop
    LID+=1 #Loop Local Variables
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
            data=(str(LID)+c+str(delay)+c+"HighTemp"+c+str(temp)+c+str(humi)+c+str(bt))
        elif(temp<tempLo): #If Temperature is lower than the defined min. Data has a LowTemp Code.
            data=(str(LID)+c+str(delay)+c+"LowTemp"+c+str(temp)+c+str(humi)+c+str(bt))
        elif(humi>humiHi): #If Humidity is higher than the definded max. Data has HighTemp Code.
            data=(str(LID)+c+str(delay)+c+"HighHumi"+c+str(temp)+c+str(humi)+c+str(bt))
        elif(humi<humiLo): #If Humidity is Lower than the definded min. Data has LowHumi code.
            data=(str(LID)+c+str(delay)+c+"LowHumi"+c+str(temp)+c+str(humi)+c+str(bt))
        else: #Good Readings are indicated by a Good Code.
            data=(str(LID)+c+str(delay)+c+"Good"+c+str(temp)+c+str(humi)+c+ str(bt))
            
    #set radio power level
    radio.tx_power=pwr
    #Send Data to RXRadio
    radio.send(data)
    #Led Indicates Data is Sent
    if(radio.tx_done is True):
        led.value=False
        sl(ledel)
        led.value=True
    #print data to user
    print(data)
    #reading delay
    sl(delay)
#led off before exit
led.value=False
exit(0)