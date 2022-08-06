#!/bin/python3/Radio/dev

#RadioProject
#Remote Sensor Webpage
#Marcus Dechant (c)
#app.rx.dev.py
#v0.0.3

#import list
import sqlite3 as sql
import os

#flask import list
from flask import Flask
from flask import render_template as template
from flask import request
from flask import flash
from flask import redirect
from flask import url_for as url4

#werkzeug.utils import list
from werkzeug.utils import secure_filename

#global variables
conn=sql.connect


#flask app
app=Flask(__name__)

#/
@app.route('/', methods=['GET'])
def gauge():
    (lid, rlid, tyme, dely, code, temp, humi, btmp, rssi, snr, date) = gauge_data()
    delay=int(dely)
    rV=int(delay*1000)
    if(delay==10):
        rV=60000
    gaugeData={
        'LID':lid,
        'RLID':rlid,
        'TIME':tyme,
        'DELAY':dely,
        'CODE':code,
        'TEMP':temp,
        'HUMI':humi,
        'BTEMP':btmp,
        'RSSI':rssi,
        'SNR':snr,
        'DATE':date,
        'refreshValue':rV,
        'ex':None}
    return(template('gauge.html', **gaugeData)), 200
    
#/graph
@app.route('/graph', methods=['GET'])
def graph():
    (lid, rlid, tyme, dely, code, temp, humi, btmp, rssi, snr, date) = gauge_data()
    (lidGr, rlidGr, tymeGr, delyGr, tempGr, humiGr, btmpGr, rssiGr, snrGr) = graph_data()
    delay=int(dely)
    rv=delay*1000
    if(delay==10):
        base=delay*360
        rV=60000
    if(delay==30):
        base=delay*120
    if(delay==60):
        base=delay*60
    x1=int(base/delay)
    x3=int(x1*3)
    x6=int(x1*6)
    x12=int(x1*12)
    x24=int(x1*24)
    xW=int(x24*7)
    x4W=int(xW*4)
    color='FFFFFF'
    #Code=""
    if(code=='Good'):
        color='00FF00'
    if(code=='HighTemp'):
        color='FF0000'
    if(code=='LowTemp'):
        color='0000FF'
    if(code=='LowHumi'):
        color='00BBBB'
    graphData={
        'ITN':lid,
        'LID':lidGr,
        'RLID':rlid,
        'DELAY':dely,
        'CODE':code,
        'TEMP':temp,
        'HUMI':humi,
        'TEMPGR':tempGr,
        'HUMIGR':humiGr,
        'BTEMP':btmpGr,
        'RSSI':rssiGr,
        'SNR':snrGr,
        'refreshValue':rV,
        'x1':x1,
        'x3':x3,
        'x6':x6,
        'x12':x12,
        'x24':x24,
        'xW':xW,
        'x4W':x4W,
        'COLOR':color,
        'ex':None}
    return(template('graph.html', **graphData)), 200
    
#/graph button input
@app.route('/graph', methods=['POST','GET'])
def graph_input():
    if(request.method=='POST'):
        xID=request.form['x']
        inputData={'x':xID}
        return(redirect(url4('graph_input', **inputData))), 302
    return(template('graph.html')), 201

def gauge_data():
    database=r'./database/radio.db'
    db=conn(database)
    xcte=db.execute
    clse=db.close
    curs=xcte('''SELECT * FROM RADIO''')
    fall=curs.fetchall
    data=fall()
    for row in data:
        lid=str(row[0])
        rlid=str(row[1])
        tyme=str(row[2])
        dely=str(row[3])
        code=str(row[4])
        temp=str(row[5])
        humi=str(row[6])
        btmp=str(row[7])
        rssi=str(row[8])
        snr=str(row[9])
        date=str(row[10])
    clse()
    return(lid, rlid, tyme, dely, code, temp, humi, btmp, rssi, snr, date)

def graph_data():
    database=r'./database/radio.db'
    db=conn(database)
    xcte=db.execute
    clse=db.close
    DATANUM=request.args.get('x')
    try:
        curs=xcte('''SELECT * FROM RADIO ORDER BY LID DESC LIMIT %s''' %DATANUM)
    except:
        DATANUM = -1
        curs=xcte('''SELECT * FROM RADIO ORDER BY LID DESC LIMIT %s''' %DATANUM)
    fall=curs.fetchall
    data=reversed(fall())
    
    lidGr=[]
    rlidGr=[]
    tymeGr=[]
    delyGr=[]
    tempGr=[]
    humiGr=[]
    btmpGr=[]
    rssiGr=[]
    snrGr=[]
    for row in data:
        lidGr.append(row[0])
        rlidGr.append(row[1])
        tymeGr.append(row[2])
        delyGr.append(row[3])
        tempGr.append(row[5])
        humiGr.append(row[6])
        btmpGr.append(row[7])
        rssiGr.append(row[8])
        snrGr.append(row[9])
    clse()
    return(lidGr, rlidGr, tymeGr, delyGr, tempGr, humiGr, btmpGr, rssiGr, snrGr)
    
if(__name__=='__main__'):
    app.run(host='192.168.1.12', port=5001, debug=True)