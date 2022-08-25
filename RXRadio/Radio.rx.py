#!/bin/python3/Radio/dev

#RadioProject
#Remote Sensor
#Marcus Dechant (c)
#RadioRX.py
#v3.1.9

#Change LEID to ESID
#Change Coding to UTF-8 over ASCII
#Integrate dt.py
#Integrate PostgreSQL

name='Radio.rx.py'
v='v3.1.9'
cpyr=u'\u00A9'
year=' 2022'
author=' Marcus Dechant'
verbose=(name+' - '+v+' - '+cpyr+year+author)
print('\n'+verbose+'\n')

import board as BO
import busio as BU

from psycopg2 import connect as ct #PostgresSQL db
db='radio'
u='radiopi'
psswd='rf915MHz'
host='127.0.0.1'
port=5432

from datetime import datetime #import from dt.py

from digitalio import DigitalInOut as digiIO

from os import mkdir
from os.path import exists as path

from lib.dt import tyme
from lib.dt import dayte

from adafruit_rfm9x import RFM9x as rfm9x

spi=BU.SPI(BO.SCK,MOSI=BO.MOSI,MISO=BO.MISO)
cs=digiIO(BO.CE1)
rst=digiIO(BO.D25)
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

logs=(r'./radiologs')
if not(path(logs)):
    mkdir(logs)

conn=ct(database=db,user=u,password=psswd,host=host,port=port)
conn.autocommit=True
cls=conn.close
save=conn.commit
helm=conn.cursor()
exe=helm.execute
rc=helm.rowcount
fa=helm.fetchall

ist='information_schema.tables'
ttn='tables.table_name'
#get last lid
rd_tb=('''SELECT * FROM %s WHERE %s='reading';''' %(ist,ttn))
exe(rd_tb)
rd_ch=bool(rc)
if(rd_ch is True):
    exe('''SELECT LID FROM reading;''')
    lid_last=fa()
    for row in lid_last:
        LID=int(row[0])
else: #main reading table
    tb_read='''CREATE TABLE IF NOT EXISTS reading(
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
               DATE    TEXT    NOT NULL);'''
    exe(tb_read) #error table
    tb_error='''CREATE TABLE IF NOT EXISTS error (
                LID     INT     NOT NULL    PRIMARY KEY,
                EID     INT     NOT NULL,
                LEID    INT     NOT NULL,
                TIME    TEXT    NOT NULL,
                CODE    TEXT    NOT NULL,
                RSSI    REAL    NOT NULL,
                SNR     REAL    NOT NULL,
                DATE    TEXT    NOT NULL,
                INFO    TEXT    NOT NULL);'''
    exe(tb_error) #rssi and snr including errors #WIP
    tb_rsall='''CREATE TABLE IF NOT EXISTS rsall (
                LID     INT     NOT NULL    PRIMARY KEY,
                SID     INT     NOT NULL,
                LEID    INT     NULL,
                TIME    TEXT    NOT NULL,
                RSSI    REAL    NOT NULL,
                SNR     REAL    NOT NULL,
                DATE    TEXT    NOT NULL,
                INFO    TEXT    NULL);'''
    exe(tb_rsall) #error1 table. UnicodeDecodeError.
    tb_error1='''CREATE TABLE IF NOT EXISTS error1 (
                 LID     INT     NOT NULL    PRIMARY KEY,
                 EID     INT     NOT NULL,
                 LEID    INT     NOT NULL,
                 TIME    TEXT    NOT NULL,
                 RSSI    REAL    NOT NULL,
                 SNR     REAL    NOT NULL,
                 DATE    TEXT    NOT NULL);'''
    exe(tb_error1) #error2 table. TypeError.
    tb_error2='''CREATE TABLE IF NOT EXISTS error2 (
                 LID     INT     NOT NULL    PRIMARY KEY,
                 EID     INT     NOT NULL,
                 LEID    INT     NOT NULL,
                 TIME    TEXT    NOT NULL,
                 RSSI    REAL    NOT NULL,
                 SNR     REAL    NOT NULL,
                 DATE    TEXT    NOT NULL);'''
    exe(tb_error2) #error3 table. Out-Of-Range.
    tb_error3='''CREATE TABLE IF NOT EXISTS ERROR3 (
                 LID     INT     NOT NULL    PRIMARY KEY,
                 EID     INT     NOT NULL,
                 LEID    INT     NOT NULL,
                 TIME    TEXT    NOT NULL,
                 RSSI    REAL    NOT NULL,
                 SNR     REAL    NOT NULL,
                 DATE    TEXT    NOT NULL);'''
    exe(tb_error3)
    save()
    
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
        dayte_=dayte()
        tyme_=tyme()
        datetyme=(tyme_+c+dayte_)
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
            para1=str(LID),str(EID),str(EID3),tyme_,str(ERR3),rssi,snr,dayte_,info
            para2=str(LID),str(EID),str(EID3),tyme_,rssi,snr,dayte_
            exe('''INSERT INTO error (LID,EID,LEID,TIME,CODE,RSSI,SNR,DATE,INFO)
                    VALUES %s''', (para1,))
            exe('''INSERT INTO ERROR3 (LID,EID,LEID,TIME,RSSI,SNR,DATE)
                    VALUES %s''', (para2,))
            with(open(r'radiologs/radio.err.pkt.csv', 'a')as pkt):
                pkt.write(str(LID)+c+str(EID)+d+str(EID3)+c+info+c+str(packet)+'\n')
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
                para=(str(LID),str(loop),tyme_,str(delay),str(code),str(temp),str(humi),str(btemp),str(rssi),str(snr),str(txpwr),dayte_)
                exe('''INSERT INTO reading (LID,RLID,TIME,DELAY,CODE,TEMP,HUMI,BTEMP,RSSI,SNR,PWR,DATE) 
                       VALUES %s''', (para,))
            except(UnicodeDecodeError): #Error 1
                EID+=1
                EID1+=1
                ERR1='Err1'
                info='UnicodeDecodeError'
                data=(str(LID)+d+str(EID)+d+str(EID1)+c+ERR1+c+info+c+c+c+rxData+c+datetyme)
                datacsv=(str(LID)+c+str(EID)+d+str(EID1)+c+ERR1+c+info+c+c+c+rxData+c+datetyme)
                para1=str(LID),str(EID),str(EID3),tyme_,ERR1,rssi,snr,dayte_,info
                para2=str(LID),str(EID),str(EID3),tyme_,rssi,snr,dayte_
                exe('''INSERT INTO error (LID,EID,LEID,TIME,CODE,RSSI,SNR,DATE,INFO)
                        VALUES %s''', (para1,))
                exe('''INSERT INTO error1 (LID,EID,LEID,TIME,RSSI,SNR,DATE)
                        VALUES %s''', (para2,))
                radio_rst()
                with(open(r'radiologs/radio.err.pkt.csv', 'a')as pkt):
                    pkt.write(str(LID)+c+str(EID)+d+str(EID1)+c+info+c+str(packet)+'\n')
            except(TypeError): #Error 2
                EID+=1
                EID2+=1
                ERR2='Err2'
                info='TypeError'
                data=(str(LID)+d+str(EID)+d+str(EID2)+c+ERR2+c+info+c+c+c+rxData+c+datetyme)            
                datacsv=(str(LID)+c+str(EID)+d+str(EID2)+c+ERR2+c+info+c+c+c+rxData+c+datetyme)
                para1=str(LID),str(EID),str(EID3),tyme_,ERR2,rssi,snr,dayte_,info
                para2=str(LID),str(EID),str(EID3),tyme_,rssi,snr,dayte_
                exe('''INSERT INTO error (LID,EID,LEID,TIME,CODE,RSSI,SNR,DATE,INFO)
                        VALUES %s''', (para1,))
                exe('''INSERT INTO error2 (LID,EID,LEID,TIME,RSSI,SNR,DATE)
                        VALUES %s''', (para2,))  
                radio_rst()
                with(open(r'radiologs/radio.err.pkt.csv', 'a')as pkt):
                    pkt.write(str(LID)+c+str(EID)+d+str(EID2)+c+info+c+str(packet)+'\n')
        save()
        with(open(r'radiologs/radio.%s.csv' %LogID, 'a') as log):
            log.write(datacsv+'\n')
        print(data)
except(KeyboardInterrupt):
    cls()
    exit(0)