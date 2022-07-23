#!/bin/python3

import sqlite3 as sql

s = ','

db_num = input('\nRadio (1) or Error (2)?\n')

db = ('radio.db')
database = sql.connect(db)
if (db_num == '1') or (db_num == 'Radio'): 
    cur = database.execute('''SELECT * FROM RADIO''')
    print('\nLID,RLID,DELAY,CODE,TEMP,HUMI,bTEMP,RSSI,SNR')
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

        print(r0 + s + r1 + s + r2 + s + r3 + s + r4 + s + r5 + s + r6 + s + r7 + s + r8)

elif (db_num == '2') or (db_num == 'Error'):
    cur = database.execute('''SELECT * FROM ERROR''')
    print('\nLID,EID,CODE,RSSI,SNR')
    for row in cur:
        r0 = str(row[0])
        r1 = str(row[1])
        r2 = str(row[2])
        r3 = str(row[3])
        r4 = str(row[4])
    
        print(r0+s+r1+s+r2+s+r3+s+r4)

else:
    print('\nError')

print('\nEnd of Database')
database.close()
exit(0)
