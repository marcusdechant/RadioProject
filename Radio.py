#!/bin/python3/Test

import board as BO
import busio as BU
import digitalio as DIO
import adafruit_rfm9x as RFM
import os
import sqlite3 as sql
path = os.path.exists
mkDir = os.mkdir
digIO = DIO.DigitalInOut

rfm9x = RFM.RFM9x
SPI = BU.SPI(BO.SCK, MOSI=BO.MOSI, MISO=BO.MISO)
CS = digIO(BO.CE1)
RST = digIO(BO.D25)
RF = 915.0
radio = rfm9x(SPI, CS, RST, RF)

EID1 = 0
EID2 = 0
LID = 0
c = ','

logs = (r'RadioLogs')
if not path(logs):
    mkDir(logs)
    
LogID = 0
while path (r'RadioLogs/radioTest.%s.csv' %LogID):
    LogID += 1
    
with open(r'RadioLogs/radioTest.%s.csv' %LogID, 'w') as log:
    log.write('LID,ID,Delay,Code,TempC,Humi,BoTempC,RSSI,SNR\n')

try:
    while True:
        packet = radio.receive(timeout=90)
        RSSI = radio.rssi
        SNR = radio.snr
        rxData = (str(RSSI) + ',' + str(SNR))
        try:
            data = str(packet, 'ascii')
            part = data.split(',')
            ID = int(part[0])
            DLY = int(part[1])
            CODE = str(part[2])
            Temp = float(part[3])
            Humi = float(part[4])
            bTemp = float(part[5])
            
        except ValueError:
            print('\n' + str(packet))
            EID1 += 1
            data = ('!!!,Err1,' + str(EID1) + ',,,')
            #radio.reset()
            
        except TypeError:
            print('\n' + str(packet))
            EID2 += 1
            data = ('!!!,Err2,' + str(EID2) + ',,,')
            #radio.reset()

        LID += 1
        data = (str(LID) + c + data + c + rxData)
        print('\n' + data)
        
        with open(r'RadioLogs/radioTest.%s.csv' %LogID, 'a') as log:
            log.write(data + '\n')
        radio.reset()
        radio = rfm9x(SPI, CS, RST, RF)
        
except KeyboardInterrupt:
    exit(0)