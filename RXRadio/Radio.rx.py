#!/bin/python3/Radio/dev

#RadioProject
#Remote Sensor
#Marcus Dechant (c)
#RadioRX.py
#v3.1.7

#Change LEID to ESID
#Need UnicodeDecodeError handling
#Change Coding to UTF-8 over ASCII

name='Radio.rx.py'
v='v3.1.7'
cpyr=u'\u00A9'
year=' 2022'
author=' Marcus Dechant'
verbose=(name+' - '+v+' - '+cpyr+year+author)
print('\n'+verbose+'\n')

import board as BO
import busio as BU

import sqlite3 as sql #PostgreSQL integration coming

from datetime import datetime #import from dt.py

from digitalio import DigitalInOut as digiIO
digIO=digiIO

from os import mkdir
from os.path import exists as path

from adafruit_rfm9x import RFM9x as rfm9x

spi=BU.SPI(BO.SCK,MOSI=BO.MOSI,MISO=BO.MISO)
cs=digIO(BO.CE1)
rst=digIO(BO.D25)
rf=915 #MHz
radio=rfm9x(spi,cs,rst,rf)

def radio_rst():
    global radio
    radio.reset()
    radio=rfm9x(spi,cs,rst,rf)

EID=0 #Error ID
EID1=0 #Error 1 ID
EID2=0 #Error 2 ID
EID3=0 #Error 3 ID
LID=0 #Loop ID
LogID=0 #Obsolete

rssiLo=(-120)
snrLo=5.5
snrNeg=0
snrLoLo=(-10)

c=', '
d='-'
tc=('\u00b0'+'C')
hd='%'
dbm=' dBm'
dec=' dB'

cnct=sql.connect
database=('./database/radio.1.db')
logs=(r'./radiologs')
db=cnct(database)
xcte=db.execute
save=db.commit
clse=db.close

#main reading database
xcte('''CREATE TABLE IF NOT EXISTS RADIO (
        LID     INT     NOT NULL    PRIMARY KEY,
        RLID    INT     NOT NULL,
        TIME    TEXT    NOT NULL,
        DELAY   INT     NOT NULL,
        CODE    TEXT    NOT NULL,
        TEMP    REAL    NOT NULL,
        HUMI    REAL    NOT NULL,
        BTEMP   REAL    NOT NULL,
        RSSI    REAL    NOT NULL,
        SNR     REAL    NOT NULL,
        PWR     INT     NOT NULL,
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

#RSSI & SNR including errors
xcte('''CREATE TABLE IF NOT EXISTS RSALL (
        LID     INT     NOT NULL    PRIMARY KEY,
        SID     INT     NOT NULL,
        LEID    INT     NULL,
        TIME    TEXT    NOT NULL,
        RSSI    REAL    NOT NULL,
        SNR     REAL    NOT NULL,
        DATE    TEXT    NOT NULL,
        INFO    TEXT    NULL);''')

#error1 only
xcte('''CREATE TABLE IF NOT EXISTS ERROR1 (
        LID     INT     NOT NULL    PRIMARY KEY,
        EID     INT     NOT NULL,
        LEID    INT     NOT NULL,
        TIME    TEXT    NOT NULL,
        RSSI    REAL    NOT NULL,
        SNR     REAL    NOT NULL,
        DATE    TEXT    NOT NULL);''')

#error2 only
xcte('''CREATE TABLE IF NOT EXISTS ERROR2 (
        LID     INT     NOT NULL    PRIMARY KEY,
        EID     INT     NOT NULL,
        LEID    INT     NOT NULL,
        TIME    TEXT    NOT NULL,
        RSSI    REAL    NOT NULL,
        SNR     REAL    NOT NULL,
        DATE    TEXT    NOT NULL);''')

#error3 only
xcte('''CREATE TABLE IF NOT EXISTS ERROR3 (
        LID     INT     NOT NULL    PRIMARY KEY,
        EID     INT     NOT NULL,
        LEID    INT     NOT NULL,
        TIME    TEXT    NOT NULL,
        RSSI    REAL    NOT NULL,
        SNR     REAL    NOT NULL,
        DATE    TEXT    NOT NULL);''')

#database continuation
#gets last IDs from database (LID, EID, LEIDx3)
if(path(database)):
    LIDlast=xcte('''SELECT LID FROM RADIO''')
    for row in LIDlast:
        LID=int(row[0])
    EIDlast=xcte('''SELECT EID FROM ERROR''')
    for row in EIDlast:
        EID=int(row[0])
    EID1last=xcte('''SELECT LEID FROM ERROR1''')
    for row in EID1last:
        EID1=int(row[0])
    EID2last=xcte('''SELECT LEID FROM ERROR2''')
    for row in EID2last:
        EID2=int(row[0])
    EID3last=xcte('''SELECT LEID FROM ERROR3''')
    for row in EID3last:
        EID3=int(row[0])

if not(path(logs)):
    mkdir(logs)

#OBSOLETE (under review)
#should be replaced with log continuation
while(path(r'radiologs/radio.%s.csv' %LogID)):
    LogID+=1
    
with(open(r'radiologs/radio.%s.csv' %LogID, 'w') as log):
    log.write('lid, rlid, delay(s), code, temperatrue('+tc+'), humidity(%), board-temp('+tc+'), rssi(dBm), snr(dB), tx-pwr(dB), time, date\n')
with(open(r'radiologs/radio.err.pkt.csv', 'w') as pkt):
    pkt.write('id, error type, packet\n')

print("id, delay(s), code, temperatrue(C), humidity(%), board-temp(C), rssi(dBm), snr(dB), tx-power(dB), time, date")

try:
    while(True):
        LID+=1
        packet=radio.receive(timeout=90) #wait for packets (max 90 seconds)
        rssi=radio.rssi #rssi reading
        snr=radio.snr #snr reading
        rxData=(str(rssi)+c+str(snr))
        dayte=datetime.now().strftime('%d/%m/%Y') #import from dt.py
        tyme=datetime.now().strftime('%H:%M:%S') #import from dt.py
        datetyme=(tyme+c+dayte)
        if(rssi<=rssiLo)or(snr<=snrNeg): #Error 3
            EID+=1
            EID3+=1
            ERR3='Err3'
            info='LowRSSI'
            if(snr<=snrNeg):
                info='LowSNR'
            data=(str(LID)+d+str(EID)+d+str(EID3)+c+ERR3+c+info+c+c+c+rxData+c+datetyme)
            datacsv=(str(LID)+c+str(EID)+d+str(EID3)+c+ERR3+c+info+c+c+c+rxData+c+datetyme)
            if(rssi<=rssiLo)and(snr<=snrNeg):
                info2='LowSNR'
                data=(str(LID)+d+str(EID)+d+str(EID3)+c+ERR3+c+info+c+info2+c+c+rxData+c+datetyme)
                datacsv=(str(LID)+c+str(EID)+d+str(EID3)+c+ERR3+c+info+c+info2+c+c+rxData+c+datetyme)
                info='LowRSSI/LowSNR'
            with(open(r'radiologs/radio.err.pkt.csv', 'a')as pkt):
                pkt.write(str(LID)+c+str(EID)+d+str(EID3)+c+info+c+str(packet)+'\n')
            xcte('''INSERT INTO ERROR (LID,EID,LEID,TIME,CODE,RSSI,SNR,DATE,INFO)
                    VALUES (?,?,?,?,?,?,?,?,?)''',
                           (LID,EID,EID3,tyme,ERR3,rssi,snr,dayte,info))
            xcte('''INSERT INTO ERROR3 (LID,EID,LEID,TIME,RSSI,SNR,DATE)
                    VALUES (?,?,?,?,?,?,?)''',
                           (LID,EID,EID3,tyme,rssi,snr,dayte))
            radio_rst()
        else:
            try:
                data=str(packet, 'ascii') #change to utf-8
                part=data.split(',')
                loop=int(part[0])
                delay=int(part[1])
                code=str(part[2])
                temp=float(part[3])
                humi=float(part[4])
                btemp=float(part[5])
                txpwr=int(part[6])
                data=(str(LID)+d+str(loop)+c+str(delay)+c+code+c+str(temp)+tc+c+str(humi)+hd+c+str(btemp)+c+rxData+c+str(txpwr)+c+datetyme)
                datacsv=(str(LID)+c+str(loop)+c+str(delay)+c+code+c+str(temp)+c+str(humi)+c+str(btemp)+c+rxData+c+str(txpwr)+c+datetyme)
                xcte('''INSERT INTO RADIO (LID,RLID,TIME,DELAY,CODE,TEMP,HUMI,BTEMP,RSSI,SNR,PWR,DATE)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''',
                               (LID,loop,tyme,delay,code,temp,humi,btemp,rssi,snr,txpwr,dayte))
            except(UnicodeDecodeError): #Error 1
                EID+=1
                EID1+=1
                ERR1='Err1'
                info='UnicodeDecodeError'
                data=(str(LID)+d+str(EID)+d+str(EID1)+c+ERR1+c+info+c+c+c+rxData+c+datetyme)
                datacsv=(str(LID)+c+str(EID)+d+str(EID1)+c+ERR1+c+info+c+c+c+rxData+c+datetyme)
                with(open(r'radiologs/radio.err.pkt.csv', 'a')as pkt):
                    pkt.write(str(LID)+c+str(EID)+d+str(EID1)+c+info+c+str(packet)+'\n')
                xcte('''INSERT INTO ERROR (LID,EID,LEID,TIME,CODE,RSSI,SNR,DATE,INFO)
                        VALUES (?,?,?,?,?,?,?,?,?)''',
                               (LID,EID,EID1,tyme,ERR1,rssi,snr,dayte,info))
                xcte('''INSERT INTO ERROR1 (LID,EID,LEID,TIME,RSSI,SNR,DATE)
                        VALUES (?,?,?,?,?,?,?)''',
                               (LID,EID,EID1,tyme,rssi,snr,dayte))  
                radio_rst()
            except(TypeError): #Error 2
                EID+=1
                EID2+=1
                ERR2='Err2'
                info='TypeError'
                data=(str(LID)+d+str(EID)+d+str(EID2)+c+ERR2+c+info+c+c+c+rxData+c+datetyme)            
                datacsv=(str(LID)+c+str(EID)+d+str(EID2)+c+ERR2+c+info+c+c+c+rxData+c+datetyme)
                with(open(r'radiologs/radio.err.pkt.csv', 'a')as pkt):
                    pkt.write(str(LID)+c+str(EID)+d+str(EID2)+c+info+c+str(packet)+'\n')                
                xcte('''INSERT INTO ERROR (LID,EID,LEID,TIME,CODE,RSSI,SNR,DATE,INFO)
                        VALUES (?,?,?,?,?,?,?,?,?)''',
                               (LID,EID,EID2,tyme,ERR2,rssi,snr,dayte,info))
                xcte('''INSERT INTO ERROR2 (LID,EID,LEID,TIME,RSSI,SNR,DATE)
                        VALUES (?,?,?,?,?,?,?)''',
                               (LID,EID,EID2,tyme,rssi,snr,dayte))  
                radio_rst()
        save()
        with(open(r'radiologs/radio.%s.csv' %LogID, 'a') as log):
            log.write(datacsv+'\n')
        print(data)
except(KeyboardInterrupt):
    clse()
    exit(0)