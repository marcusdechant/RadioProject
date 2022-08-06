#!/bin/python3/Radio/dev

#SHT Project
#Homebrew SCADA
#Marcus Dechant (c)
#dbQ.rx.py
#v0.1.2

#verbose
script = 'dbQ.rx.dev.py'
v = 'v0.1.2'
author = 'Marcus Dechant (c)'
verbose =('\n'+script+' - ('+v+') - '+author+'\n')
print(verbose)

#Import List
import sqlite3 as sql

#comma separator
c = (', ')

#user chooses database
dbNum = input('Radio (1) or Error (2)?\n')

#database
conn = sql.connect
database = ('radio.db')
db = conn(database)

#database constructors
xcte = db.execute
save = db.commit
clse = db.close

#RX database
if (dbNum == '1') or (dbNum == 'Radio'): 
    #query all from database
    cur = xcte('''SELECT * FROM RADIO''')
    #database header
    print('\nLID, RLID, TYME, DELAY, CODE, TEMP, HUMI, bTEMP, RSSI, SNR, DATE')
    #select contents from database
    for row in cur:
        r0 = str(row[0])
        r1 = str(row[1])
        r2 = str(row[2])
        r3 = str(row[3])
        r4 = str(row[4])
        r5 = str(row[5])
        r6 = str(row[6])
        r7 = str(row[7])
        r8 = str(row[8])
        r9 = str(row[9])
        r10 = str(row[10])
        #displays contents of database
        print(r0+c+r1+c+r2+c+r3+c+r4+c+r5+c+r6+c+r7+c+r8+c+r9+c+r10)

#error database
elif (dbNum == '2') or (dbNum == 'Error'):
    cur = xcte('''SELECT * FROM ERROR''')
    print('\nLID, EID, TYME, CODE, RSSI, SNR, DATE')
    for row in cur:
        r0 = str(row[0])
        r1 = str(row[1])
        r2 = str(row[2])
        r3 = str(row[3])
        r4 = str(row[4])
        r5 = str(row[5])
        r6 = str(row[6])
        print(r0+c+r1+c+r2+c+r3+c+r4+c+r5+c+r6)

#user selection error
else:
    print('\nError. Not an option.')

print('\nEnd of Database')
clse()
exit(0)