#!/bin/python3/Radio/dev

#RadioProject
#Remote Sensor
#Marcus Dechant (c)
#RadioRX.py
#v3.0.13

#verbose
script='RadioRX.dev.py'
v='v3.0.13'
author='Marcus Dechant (c)'
verbose=('\n'+script+' - ('+v+') - '+author+'\n')
print(verbose)

#Import List
import board as BO
import busio as BU
import digitalio as DIO
import adafruit_rfm9x as RFM
import os
import sqlite3 as sql
from datetime import datetime
path=os.path.exists
mkdir=os.mkdir
digIO=DIO.DigitalInOut

#Radio Object (SPI)
rfm9x=RFM.RFM9x
SPI=BU.SPI(BO.SCK,MOSI=BO.MOSI,MISO=BO.MISO)
CS=digIO(BO.CE1)
RST=digIO(BO.D25)
RF=915
radio=rfm9x(SPI,CS,RST,RF)

#local variables
EID=0
EID1=0
EID2=0
EID3=0
LID=0
LogID=0

rssiLow=(-120)
snr1=8.5
snr2=(-1)

#comma seperator
c=', '
d='-'
tc=' \u00b0'+'C'
hd=' %'
dbm=' dBm'
dec=' dB'

#database
cnct=sql.connect
database=('./database/radio.3.db')
logs=(r'./radiologs')
db=cnct(database)
xcte=db.execute
save=db.commit
clse=db.close

#reading database
#LID = Loop ID
#RLID = Remote Loop ID
#TYME = time of reading
#DELAY = time between readings
#CODE = status descriptor
#TEMP = SHT30 Temperature Reading
#HUMI = SHT30 Relative Humidity Reading
#BTEMP = Raspberry Pi Pico Board Temperature
#RSSI = RFM95W Return Signal Strenght Indication
#SNR = RFM95W Signal to Noise Ratio
#DATE = date of reading
#INFO = explains cause of error
xcte('''CREATE TABLE IF NOT EXISTS RADIO (
        LID     INT     NOT NULL    PRIMARY KEY,
        RLID    INT     NOT NULL,
        TIME    TEXT    NOT NULL,
        DELAY   INT     NULL,
        CODE    TEXT    NOT NULL,
        TEMP    REAL    NULL,
        HUMI    REAL    NULL,
        BTEMP   REAL    NULL,
        RSSI    REAL    NOT NULL,
        SNR     REAL    NOT NULL,
        DATE    TEXT    NOT NULL);''')

#error database
xcte('''CREATE TABLE IF NOT EXISTS ERROR (
        LID     INT     NOT NULL    PRIMARY KEY,
        EID     INT     NOT NULL,
        LEID    INT     NOT NULL,
        TIME    TEXT    NOT NULL,
        CODE    TEXT    NOT NULL,
        RSSI    REAL    NOT NULL,
        SNR     REAL    NOT NULL,
        DATE    TEXT    NOT NULL,
        INFO    TEXT    NOT NULL);''')

"""
#EXPERIMENTAL
#RSSI & SNR including errors
xcte('''CREATE TABLE IF NOT EXISTS RADIOSTATUS (
        LID     INT     NOT NULL    PRIMARY KEY,
        TIME    TEXT    NOT NULL,
        RSSI    REAL    NOT NULL,
        SNR     REAL    NOT NULL,
        DATE    TEXT    NOT NULL,
        INFO    TEXT    NULL);''')
"""

#error1 only
xcte('''CREATE TABLE IF NOT EXISTS ERROR1 (
        LID     INT     NOT NULL    PRIMARY KEY,
        EID     INT     NOT NULL,
        LEID     INT     NOT NULL,
        TIME    TEXT    NOT NULL,
        RSSI    REAL    NOT NULL,
        SNR     REAL    NOT NULL,
        DATE    TEXT    NOT NULL);''')

#error2 only
xcte('''CREATE TABLE IF NOT EXISTS ERROR2 (
        LID     INT     NOT NULL    PRIMARY KEY,
        EID     INT     NOT NULL,
        LEID     INT     NOT NULL,
        TIME    TEXT    NOT NULL,
        RSSI    REAL    NOT NULL,
        SNR     REAL    NOT NULL,
        DATE    TEXT    NOT NULL);''')

#error3 only
xcte('''CREATE TABLE IF NOT EXISTS ERROR3 (
        LID     INT     NOT NULL    PRIMARY KEY,
        EID     INT     NOT NULL,
        LEID     INT     NOT NULL,
        TIME    TEXT    NOT NULL,
        RSSI    REAL    NOT NULL,
        SNR     REAL    NOT NULL,
        DATE    TEXT    NOT NULL);''')

#database continuation
#gets last LID from 
if(path(database)):
    last=xcte('''SELECT LID FROM RADIO''')
    for row in last:
        LID=int(row[0])

if not(path(logs)):
    mkdir(logs)
    
while(path(r'radiologs/radio.%s.csv' %LogID)):
    LogID+=1
    
with(open(r'radiologs/radio.%s.csv' %LogID, 'w') as log):
    log.write('loop-id, remote-loop-id, reading-delay, code, temperatrue, humidity, board-temperature, rssi, snr, time, date\n')

with(open(r'radiologs/radio.err.pkt.csv', 'w') as err):
    err.write('LID-EID-LEID, Error Type')

#NEEDS UPDATE
print("loop-id, remote-loop-id, reading-delay, code, temperatrue, humidity, board-temperature, rssi, snr, time, date")

try:
    while(True):
        LID+=1
        packet=radio.receive(timeout=90)
        rssi=radio.rssi
        snr=radio.snr
        date=datetime.now().strftime('%d/%m/%Y')
        tyme=datetime.now().strftime('%H:%M:%S')
        datetyme=(tyme+c+date)
        rxData=(str(rssi)+dbm+c+str(snr)+dec)
        
        #-3 is less than -1
        # 3 is greater than 1
        #if RSSI is lower than -120 (LoRa min) will result in error 3
        if(rssi<rssiLow):
            EID+=1
            EID3+=1
            ERR3='Err3'
            info='LowRSSI'
            data=(str(LID)+d+str(EID)+d+str(EID3)+c+ERR3+c+info+c+c+c+rxData+c+datetyme)
            xcte('''INSERT INTO ERROR (LID,EID,LEID,TIME,CODE,RSSI,SNR,DATE,INFO)
                               VALUES (?,?,?,?,?,?,?,?,?)''',
                                      (LID,EID,EID3,tyme,ERR3,rssi,snr,date,info))
            xcte('''INSERT INTO ERROR3 (LID,EID,LEID,TIME,RSSI,SNR,DATE)
                                VALUES (?,?,?,?,?,?,?)''',
                                       (LID,EID,EID3,tyme,rssi,snr,date))               
            radio.reset()
            radio=rfm9x(SPI,CS,RST,RF)
            
        else:
            try:
                data=str(packet, 'ascii')
                part=data.split(',')
                loop=int(part[0])
                delay=int(part[1])
                code=str(part[2])
                temp=float(part[3])
                humi=float(part[4])
                btemp=float(part[5])
                data=(str(LID)+d+str(loop)+c+str(delay)+c+code+c+str(temp)+tc+c+str(humi)+hd+c+str(btemp)+tc+c+rxData+c+datetyme)
                xcte('''INSERT INTO RADIO (LID,RLID,TIME,DELAY,CODE,TEMP,HUMI,BTEMP,RSSI,SNR,DATE)
                                   VALUES (?,?,?,?,?,?,?,?,?,?,?)''',
                                          (LID,loop,tyme,delay,code,temp,humi,btemp,rssi,snr,date))
            except(ValueError):
                EID+=1
                EID1+=1
                ERR1='Err1'
                info='ValueError'
                data=(str(LID)+d+str(EID)+d+str(EID1)+c+ERR1+c+info+c+c+c+rxData+c+datetyme)
                xcte('''INSERT INTO ERROR (LID,EID,LEID,TIME,CODE,RSSI,SNR,DATE,INFO)
                                   VALUES (?,?,?,?,?,?,?,?,?)''',
                                          (LID,EID,EID1,tyme,ERR1,rssi,snr,date,info))
                xcte('''INSERT INTO ERROR1 (LID,EID,LEID,TIME,RSSI,SNR,DATE)
                                    VALUES (?,?,?,?,?,?,?)''',
                                           (LID,EID,EID1,tyme,rssi,snr,date))  
                radio.reset()
                radio=rfm9x(SPI,CS,RST,RF)           
            except(TypeError):
                EID+=1
                EID2+=1
                ERR2='Err2'
                info='TypeError'
                data=(str(LID)+d+str(EID)+d+str(EID2)+c+ERR2+c+info+c+c+c+rxData+c+datetyme)            
                xcte('''INSERT INTO ERROR (LID,EID,LEID,TIME,CODE,RSSI,SNR,DATE,INFO)
                                   VALUES (?,?,?,?,?,?,?,?,?)''',
                                          (LID,EID,EID2,tyme,ERR2,rssi,snr,date,info))
                xcte('''INSERT INTO ERROR2 (LID,EID,LEID,TIME,RSSI,SNR,DATE)
                                    VALUES (?,?,?,?,?,?,?)''',
                                           (LID,EID,EID2,tyme,rssi,snr,date))  
                radio.reset()
                radio=rfm9x(SPI,CS,RST,RF)
        save()
        print(data)
        with(open(r'radiologs/radio.%s.csv' %LogID, 'a') as log):
            log.write(data+'\n')
            
except(KeyboardInterrupt):
    clse()
    exit(0)