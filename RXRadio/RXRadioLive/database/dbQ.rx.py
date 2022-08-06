#!/bin/python3/Radio
#Marcus Dechant (c)
#v0.1.3
script = 'dbQ.rx.dev.py'
v = 'v0.1.3'
author = 'Marcus Dechant (c)'
verbose =('\n'+script+' - ('+v+') - '+author+'\n')
print(verbose)
import sqlite3 as sql
c=(', ')
dbNum=input('Radio (1) or Error (2)?\n')
conn=sql.connect
database=('radio.db')
db=conn(database)
xcte=db.execute
save=db.commit
clse=db.close
if(dbNum=='1')or(dbNum=='Radio'):
    cur=xcte('''SELECT * FROM RADIO''')
    print('\nLID, RLID, TYME, DELAY, CODE, TEMP, HUMI, bTEMP, RSSI, SNR, DATE')
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
        print(r0+c+r1+c+r2+c+r3+c+r4+c+r5+c+r6+c+r7+c+r8+c+r9+c+r10)
elif(dbNum=='2')or(dbNum=='Error'):
    cur=xcte('''SELECT * FROM ERROR''')
    print('\nLID, EID, TYME, CODE, RSSI, SNR, DATE')
    for row in cur:
        r0=str(row[0])
        r1=str(row[1])
        r2=str(row[2])
        r3=str(row[3])
        r4=str(row[4])
        r5=str(row[5])
        r6=str(row[6])
        print(r0+c+r1+c+r2+c+r3+c+r4+c+r5+c+r6)
else:
    print('\nError. Not an option.')
print('\nEnd of Database')
clse()
exit(0)