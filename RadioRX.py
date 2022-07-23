#!/bin/python3/Radio

#RadioProject
#Remote Sensor
#Marcus Dechant (c)
#RadioRX.py
#v3.0.1

#verbose
script = 'RadioRX.py'
v = 'v3.0.1'
author = 'Marcus Dechant (c)'
verbose =('\n'+script+' - ('+v+') - '+author+'\n')
print(verbose)

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

cnct = sql.connect
database = ('radio.db')
db = cnct(database)
xcte = db.execute
save = db.commit
clse = db.close

xcte('''
CREATE TABLE IF NOT EXISTS RADIO (
LID     INT     NOT NULL    PRIMARY KEY,
RLID    INT     NOT NULL,
DELAY   INT     NULL,
CODE    TEXT    NOT NULL,
TEMP    REAL    NULL,
HUMI    REAL    NULL,
BTEMP   REAL    NULL,
RSSI    REAL    NOT NULL,
SNR     REAL    NOT NULL);''')

xcte('''
CREATE TABLE IF NOT EXISTS ERROR (
LID     INT     NOT NULL    PRIMARY KEY,
EID     INT     NOT NULL,
CODE    TEXT    NOT NULL,
RSSI    REAL    NOT NULL,
SNR     REAL    NOT NULL);''')

if path(database):
    last = xcte('''SELECT LID FROM RADIO''')
    for row in last:
        LID = int(row[0])

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
        LID += 1
        packet = radio.receive(timeout=90)
        RSSI = radio.rssi
        SNR = radio.snr
        rxData = (str(RSSI) +c+ str(SNR))
        try:
            data = str(packet, 'ascii')
            #data = LID,RLID/EID,Delay,Code,Temp,Humi,bTemp,RSSI,SNR
            part = data.split(',')
            loop = int(part[0])
            delay = int(part[1])
            code = str(part[2])
            temp = float(part[3])
            humi = float(part[4])
            bTemp = float(part[5])
            
            data = (str(LID)+c+data+c+rxData)
            
            xcte('''
            INSERT INTO RADIO (LID,RLID,DELAY,CODE,TEMP,HUMI,BTEMP,RSSI,SNR)
                       VALUES (?,?,?,?,?,?,?,?,?)''',
                              (LID,loop,delay,code,temp,humi,bTemp,RSSI,SNR))
            
        except ValueError:
            print('\n' + str(packet))
            EID1 += 1
            data = (str(LID)+c+str(EID1)+',,Err1,,,,'+rxData)
            ERR1 = 'Err1'
            
            xcte('''
            INSERT INTO ERROR (LID,EID,CODE,RSSI,SNR)
                       VALUES (?,?,?,?,?)''',
                              (LID,EID1,ERR1,RSSI,SNR))
            
            radio.reset()
            radio = rfm9x(SPI, CS, RST, RF)
                        
        except TypeError:
            print('\n' + str(packet))
            EID2 += 1
            data = (str(LID)+c+str(EID2)+',,Err2,,,,'+rxData)
            ERR2 = 'Err2'            
            
            xcte('''
            INSERT INTO ERROR (LID,EID,CODE,RSSI,SNR)
                       VALUES (?,?,?,?,?)''',
                              (LID,EID2,ERR2,RSSI,SNR))
            
            radio.reset()
            radio = rfm9x(SPI, CS, RST, RF)
        save()
        print('\n' + data)
        with open(r'RadioLogs/radioTest.%s.csv' %LogID, 'a') as log:
            log.write(data + '\n')
        
except KeyboardInterrupt:
    clse()
    exit(0)
