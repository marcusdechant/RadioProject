#!/bin/python3/Radio/dev

#RadioProject
#Remote Sensor
#Marcus Dechant (c)
#RadioRX.py
#v3.1.6

#Change LEID to ESID
#Need UnicodeDecodeError handling
#Change Coding to UTF-8 over ASCII

#verbose
script='RadioRX.dev.py'
v='v3.1.6'
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

#constructors
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
def radio_rst():
    global radio
    radio.reset()
    radio=rfm9x(SPI,CS,RST,RF)

#local variables
EID=0
EID1=0
EID2=0
EID3=0
LID=0
LogID=0

#signal error triggers
rssiLo=(-120)
snrLo=5.5
snrNeg=(0)
snrLoLo=(-10)

#delimiters and units
c=', '
d='-'
tc='\u00b0'+'C'
hd='%'
dbm=' dBm'
dec=' dB'

#database
cnct=sql.connect
database=('./database/radio.1.db')
logs=(r'./radiologs')
db=cnct(database)
xcte=db.execute
save=db.commit
clse=db.close

#reading database
#LID = Loop ID
#EID = General Error ID
#ESID = Error Specific ID - LEID
#SID = Secondary ID, used with RSALL Table
#RLID = Remote Loop ID
#TYME = time of reading
#DELAY = time between readings
#CODE = status descriptor
#TEMP = SHT30 Temperature Reading
#HUMI = SHT30 Relative Humidity Reading
#BTEMP = Raspberry Pi Pico Board Temperature
#RSSI = RFM95W Return Signal Strenght Indication
#SNR = RFM95W Signal to Noise Ratio
#PWR = TX power level in dB
#DATE = date of reading
#INFO = explains cause of error

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

#if logs directory does not exist, make it
if not(path(logs)):
    mkdir(logs)

#OBSOLETE (under review)
#should be replaced with log continuation
#if a log file exists make a new one
while(path(r'radiologs/radio.%s.csv' %LogID)):
    LogID+=1

#log file header
with(open(r'radiologs/radio.%s.csv' %LogID, 'w') as log):
    log.write('lid, rlid, delay(s), code, temperatrue('+tc+'), humidity(%), board-temp('+tc+'), rssi(dBm), snr(dB), tx-pwr(dB), time, date\n')

#error packet tracking log file header
with(open(r'radiologs/radio.err.pkt.csv', 'w') as pkt):
    pkt.write('id, error type, packet\n')

#printout header
print("id, delay(s), code, temperatrue(C), humidity(%), board-temp(C), rssi(dBm), snr(dB), tx-power(dB), time, date")

#primary main loop
try:
    while(True):
        #add one to lid per loop
        LID+=1
        #radio receive, wait 90s before error
        packet=radio.receive(timeout=90)
        #get rssi from last message
        rssi=radio.rssi
        #get snr from last message
        snr=radio.snr
        #format rx data to be included in data
        rxData=(str(rssi)+c+str(snr))
        
        #should be moved to function
        #date
        dayte=datetime.now().strftime('%d/%m/%Y')
        #time
        tyme=datetime.now().strftime('%H:%M:%S')
        #format datetime to be included in data
        datetyme=(tyme+c+dayte)
        
        #-3 is less than -1
        # 3 is greater than 1
        #-3 is less than 1
        # 3 is greater than -1
        
        #if RSSI is lower than -120 (LoRa min) will result in error 3
        #if SNR is lower than 0 (noise floor) will result in error 3
        if(rssi<=rssiLo)or(snr<=snrNeg):
            #add 1 to EID
            EID+=1
            #add 1 to EID3 (LEID)
            EID3+=1
            #error 3 code
            ERR3='Err3'
            #error 3 information
            info='LowRSSI'
            #if only snr is triggered, info = low snr information
            if(snr<=snrNeg):
                info='LowSNR'
            #single info data
            data=(str(LID)+d+str(EID)+d+str(EID3)+c+ERR3+c+info+c+c+c+rxData+c+datetyme)
            #data for csv
            datacsv=(str(LID)+c+str(EID)+d+str(EID3)+c+ERR3+c+info+c+c+c+rxData+c+datetyme)
            #if both rssi and snr are low
            if(rssi<=rssiLo)and(snr<=snrNeg):
                #inlude info 2
                info2='LowSNR'
                data=(str(LID)+d+str(EID)+d+str(EID3)+c+ERR3+c+info+c+info2+c+c+rxData+c+datetyme)
                datacsv=(str(LID)+c+str(EID)+d+str(EID3)+c+ERR3+c+info+c+info2+c+c+rxData+c+datetyme)
                #info is both
                info='LowRSSI/LowSNR'
            #error packet tracking
            with(open(r'radiologs/radio.err.pkt.csv', 'a')as pkt):
                pkt.write(str(LID)+c+str(EID)+d+str(EID3)+c+info+c+str(packet)+'\n')
            #error database input
            xcte('''INSERT INTO ERROR (LID,EID,LEID,TIME,CODE,RSSI,SNR,DATE,INFO)
                    VALUES (?,?,?,?,?,?,?,?,?)''',
                           (LID,EID,EID3,tyme,ERR3,rssi,snr,dayte,info))
            xcte('''INSERT INTO ERROR3 (LID,EID,LEID,TIME,RSSI,SNR,DATE)
                    VALUES (?,?,?,?,?,?,?)''',
                           (LID,EID,EID3,tyme,rssi,snr,dayte))
            #reinitalize the radio as a precaution
            radio_rst()
            
        #normal packet is received
        else:
            try:
                #unload packet and process into data and database
                #data is received by the radio
                data=str(packet, 'ascii')
                #split into parts by ,
                part=data.split(',')
                #extract data
                loop=int(part[0])
                delay=int(part[1])
                code=str(part[2])
                temp=float(part[3])
                humi=float(part[4])
                btemp=float(part[5])
                txpwr=int(part[6])
                #concatinate data
                data=(str(LID)+d+str(loop)+c+str(delay)+c+code+c+str(temp)+tc+c+str(humi)+hd+c+str(btemp)+c+rxData+c+str(txpwr)+c+datetyme)
                datacsv=(str(LID)+c+str(loop)+c+str(delay)+c+code+c+str(temp)+c+str(humi)+c+str(btemp)+c+rxData+c+str(txpwr)+c+datetyme)
                xcte('''INSERT INTO RADIO (LID,RLID,TIME,DELAY,CODE,TEMP,HUMI,BTEMP,RSSI,SNR,PWR,DATE)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''',
                               (LID,loop,tyme,delay,code,temp,humi,btemp,rssi,snr,txpwr,dayte))
                                          
            #OBSOLETE
            #error3 is catching all ValueErrors
            #incase of ValueError, process error 1
            #except(ValueError):
            
            #incase of UnicodeDecodeError, process error 1
            except(UnicodeDecodeError):
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
            
            #Incase of TypeError, process Error2
            except(TypeError):
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
        
        #save database inputs
        save()
        #write to csv log
        with(open(r'radiologs/radio.%s.csv' %LogID, 'a') as log):
            log.write(datacsv+'\n')
        #print data to console
        print(data)

#escape    
except(KeyboardInterrupt):
    clse()
    exit(0)