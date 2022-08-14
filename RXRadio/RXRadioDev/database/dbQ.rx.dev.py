#!/bin/python3/Radio/dev

#Radio Project
#Remote Sensor
#Marcus Dechant (c)
#dbQ.rx.py
#v0.1.7

#verbose
script = 'dbQ.rx.dev.py'
v = 'v0.1.7'
author = 'Marcus Dechant (c)'
verbose =('\n'+script+' - ('+v+') - '+author+'\n')
print(verbose)

#Import List
import sqlite3 as sql

#comma separator
c=(', ')
d='-'

#user chooses database
table=input('Radio (1), Error (2), Error1 (3), Error2 (4), or Error3 (5)?\n')
dbnum=input('\nDatabase Number?\n')

#database
conn=sql.connect
database=('radio.%s.db' %dbnum)
db=conn(database)

#database constructors
xcte=db.execute
save=db.commit
clse=db.close

#RX database
if(table=='1')or(table=='Radio'): 
    #query all from database
    cur=xcte('''SELECT LID,RLID,TIME,DELAY,CODE,TEMP,HUMI,BTEMP,RSSI,SNR,PWR,DATE FROM RADIO''')
    #database header
    print('\nlid-rlid, time, delay, code, temp, humi, btemp, rssi, snr, txpwr, date')
    #select contents from database
    for row in cur:
        r0=str(row[0])
        r1=str(row[1])
        r2=str(row[2])
        r3=str(row[3])
        r4=str(row[4])
        r5=str(row[5])
        r6=str(row[6])
        r7=str(row[7])
        r8=str(row[8])
        r9=str(row[9])
        r10=str(row[10])
        r11=str(row[11])
        #displays contents of database
        print(r0+d+r1+c+r2+c+r3+c+r4+c+r5+c+r6+c+r7+c+r8+c+r9+c+r10+c+r11)

#error database
elif(table=='2')or(table=='Error'):
    cur=xcte('''SELECT LID,EID,LEID,TIME,CODE,RSSI,SNR,DATE,INFO FROM ERROR''')
    print('\nlid-eid-leid, time, code, rssi, snr, date, info')
    for row in cur:
        r0=str(row[0])
        r1=str(row[1])
        r2=str(row[2])
        r3=str(row[3])
        r4=str(row[4])
        r5=str(row[5])
        r6=str(row[6])
        r7=str(row[7])
        r8=str(row[8])
        print(r0+d+r1+d+r2+c+r3+c+r4+c+r5+c+r6+c+r7+c+r8)

elif(table=='3')or(table=='Error1'):
    cur=xcte('''SELECT LID,EID,LEID,TIME,RSSI,SNR,DATE FROM ERROR1''')
    print('\nlid-eid-leid, time, rssi, snr, date')
    for row in cur:
        r0=str(row[0])
        r1=str(row[1])
        r2=str(row[2])
        r3=str(row[3])
        r4=str(row[4])
        r5=str(row[5])
        r6=str(row[6])
        print(r0+d+r1+d+r2+c+r3+c+r4+c+r5+c+r6)
        
elif(table=='4')or(table=='Error2'):
    cur=xcte('''SELECT LID,EID,LEID,TIME,RSSI,SNR,DATE FROM ERROR2''')
    print('\nlid-eid-leid, time, rssi, snr, date')
    for row in cur:
        r0=str(row[0])
        r1=str(row[1])
        r2=str(row[2])
        r3=str(row[3])
        r4=str(row[4])
        r5=str(row[5])
        r6=str(row[6])
        print(r0+d+r1+d+r2+c+r3+c+r4+c+r5+c+r6)

elif(table=='5')or(table=='Error3'):
    cur=xcte('''SELECT LID,EID,LEID,TIME,RSSI,SNR,DATE FROM ERROR3''')
    print('\nlid-eid-leid, time, rssi, snr, date')
    for row in cur:
        r0=str(row[0])
        r1=str(row[1])
        r2=str(row[2])
        r3=str(row[3])
        r4=str(row[4])
        r5=str(row[5])
        r6=str(row[6])
        print(r0+d+r1+d+r2+c+r3+c+r4+c+r5+c+r6)
#user selection error
else:
    print('\nError. Not an option.')

print('\nEnd of Database')
clse()
exit(0)