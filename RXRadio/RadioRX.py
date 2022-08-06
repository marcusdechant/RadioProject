#!/bin/python3/Radio/dev
#Marcus Dechant (c)
#v3.0.5
#See Dev files for documantation
script = 'RadioRX.dev.py'
v = 'v3.0.5'
author = 'Marcus Dechant (c)'
verbose =('\n'+script+' - ('+v+') - '+author+'\n')
print(verbose)
import board as BO
import busio as BU
import digitalio as DIO
import adafruit_rfm9x as RFM
import os
import sqlite3 as sql
from datetime import datetime
path=os.path.exists
mkDir=os.mkdir
digIO=DIO.DigitalInOut
rfm9x=RFM.RFM9x
SPI=BU.SPI(BO.SCK, MOSI=BO.MOSI, MISO=BO.MISO)
CS=digIO(BO.CE1)
RST=digIO(BO.D25)
RF=915.0
radio=rfm9x(SPI, CS, RST, RF)
EID1=0
EID2=0
LID=0
c=','
cnct=sql.connect
database=('radio.db')
db=cnct(database)
xcte=db.execute
save=db.commit
clse=db.close
xcte('''
CREATE TABLE IF NOT EXISTS RADIO (
LID     INT     NOT NULL    PRIMARY KEY,
RLID    INT     NOT NULL,
TYME    TEXT    NOT NULL,
DELAY   INT     NULL,
CODE    TEXT    NOT NULL,
TEMP    REAL    NULL,
HUMI    REAL    NULL,
BTEMP   REAL    NULL,
RSSI    REAL    NOT NULL,
SNR     REAL    NOT NULL,
DATE    TEXT    NOT NULL);''')
xcte('''
CREATE TABLE IF NOT EXISTS ERROR (
LID     INT     NOT NULL    PRIMARY KEY,
EID     INT     NOT NULL,
TYME    TEXT    NOT NULL,
CODE    TEXT    NOT NULL,
RSSI    REAL    NOT NULL,
SNR     REAL    NOT NULL,
DATE    TEXT    NOT NULL);''')
if path(database):
    last=xcte('''SELECT LID FROM RADIO''')
    for row in last:
        LID=int(row[0])
logs=(r'RadioLogs')
if not path(logs):
    mkDir(logs)
LogID=0
while path(r'RadioLogs/radioTest.%s.csv' %LogID):
    LogID+=1
with open(r'RadioLogs/radioTest.%s.csv' %LogID, 'w') as log:
    log.write('LID, ID, Delay, Code, TempC, Humi, BoTempC, RSSI, SNR, TIME, DATE\n')
print('LID, ID, Delay, Code, TempC, Humi, BoTempC, RSSI, SNR, TIME, DATE\n')
try:
    while(True):
        LID+=1
        packet=radio.receive(timeout=90)
        rssi=radio.rssi
        snr=radio.snr
        date=datetime.now().strftime('%d/%m/%Y')
        tyme=datetime.now().strftime('%H:%M:%S')
        datetyme=(tyme+c+date)
        rxData=(str(rssi)+c+str(snr))
        try:
            data=str(packet, 'ascii')
            #LID,RLID,TYME,DELAY,CODE,TEMP,HUMI,bTEMP,RSSI,SNR,DATE
            part=data.split(',')
            loop=int(part[0])
            delay=int(part[1])
            code=str(part[2])
            temp=float(part[3])
            humi=float(part[4])
            bTemp=float(part[5])            
            data=(str(LID)+c+data+c+rxData+c+datetyme)
            xcte('''INSERT INTO RADIO (LID,RLID,TYME,DELAY,CODE,TEMP,HUMI,BTEMP,RSSI,SNR,DATE)
                               VALUES (?,?,?,?,?,?,?,?,?,?,?)''',
                                      (LID,loop,tyme,delay,code,temp,humi,bTemp,rssi,snr,date))
        except ValueError:
            EID1+=1
            ERR1='Err1'
            data=(str(LID)+c+str(EID1)+c+c+ERR1+c+c+c+c+rxData+c+datetyme)
            xcte('''INSERT INTO ERROR (LID,EID,TYME,CODE,RSSI,SNR,DATE)
                               VALUES (?,?,?,?,?,?,?)''',
                                      (LID,EID1,tyme,ERR1,rssi,snr,date))
            radio.reset()
            radio=rfm9x(SPI, CS, RST, RF)       
        except TypeError:
            EID2+=1
            ERR2='Err2'
            data=(str(LID)+c+str(EID2)+c+c+ERR2+c+c+c+c+rxData+c+datetyme)            
            xcte('''INSERT INTO ERROR (LID,EID,TYME,CODE,RSSI,SNR,DATE)
                               VALUES (?,?,?,?,?,?,?)''',
                                      (LID,EID2,tyme,ERR2,rssi,snr,date))
            radio.reset()
            radio=rfm9x(SPI, CS, RST, RF)
        save()
        print(data+'\n')
        with open(r'RadioLogs/radioTest.%s.csv' %LogID, 'a') as log:
            log.write(data+'\n')
except KeyboardInterrupt:
    clse()
    exit(0)