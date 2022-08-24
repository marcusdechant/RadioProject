#!/bin/python3/Radio/dev

#RadioProject
#Remote Sensor Webpage
#Marcus Dechant (c)
#app.rx.py
#v0.1.7

import sqlite3 as sql
import os

from flask import Flask
from flask import render_template as template
from flask import request
from flask import flash
from flask import redirect
from flask import url_for as url4

from werkzeug.utils import secure_filename

conn=sql.connect
database=r'./database/radio.db'
    
app=Flask(__name__)

def single_data():
    db=conn(database)
    xcte=db.execute
    clse=db.close
    curs=xcte('''SELECT LID,RLID,TIME,DELAY,CODE,TEMP,HUMI,BTEMP,RSSI,SNR,PWR,DATE FROM RADIO''')
    data=curs.fetchall()
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
        pwr=str(row[10])
        date=str(row[11])
    clse()
    return(lid, rlid, tyme, dely, code, temp, humi, btmp, rssi, snr, pwr, date)

def all_data():
    db=conn(database)
    xcte=db.execute
    clse=db.close
    #xaxis determines how far back the graph goes.
    xaxis=request.args.get('x')
    try:
        curs=xcte('''SELECT LID,RLID,TIME,DELAY,CODE,TEMP,HUMI,BTEMP,RSSI,SNR,PWR,DATE FROM RADIO ORDER BY LID DESC LIMIT %s''' %xaxis)
    except: #exception raised when no readings exist in database to handle this the exception is passed as all readings
        xaxis=(-1)
        curs=xcte('''SELECT LID,RLID,TIME,DELAY,CODE,TEMP,HUMI,BTEMP,RSSI,SNR,PWR,DATE FROM RADIO ORDER BY LID DESC LIMIT %s''' %xaxis)
    data=reversed(curs.fetchall()) #get all readings and reverse the order (SQL query returns backwards)
    lidGr=[]
    rlidGr=[]
    tymeGr=[]
    delyGr=[]
    tempGr=[]
    humiGr=[]
    btmpGr=[]
    rssiGr=[]
    snrGr=[]
    pwrGr=[]
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
        pwrGr.append(row[10])
    clse()
    return(lidGr, rlidGr, tymeGr, delyGr, tempGr, humiGr, btmpGr, rssiGr, snrGr, pwrGr, xaxis)

#/
@app.route('/', methods=['GET'])
def gauge():
    (lid, rlid, tyme, dely, code, temp, humi, btmp, rssi, snr, pwr, date) = single_data()
    delay=int(dely)
    rV=int(delay*1000) #refresh value delay(1000)
    if(delay==10):
        base=delay*360 #base is 10(360)=3600 (1 hour)
        rV=60000 #if delay is 10, rV is 1 minute
    if(delay==30): 
        base=delay*120 #30(120)=3600 (1 hour)
    if(delay==60):
        base=delay*60 #60(60)=3600 (1 hour)
    x1=int(base/delay) #x1 = 1 hour of readings (x axis=base/delay=1 hour)
    x24=int(x1*24) #x24= 24 hours of readings (x axis=x1*24=24 hours)
    if(code=='Good'):
        color='#00C800' #green
    if(code=='HighTemp'):
        color='#C80000' #red
    if(code=='LowTemp'):
        color='#0000C8' #blue
    if(code=='LowHumi'):
        color='#00BBBB' #teal
    gaugeData={'LID':lid, 'RLID':rlid, 'TIME':tyme, 'DELAY':dely, 'CODE':code, 'TEMP':temp, 'HUMI':humi, 'BTEMP':btmp,
               'RSSI':rssi, 'SNR':snr, 'PWR':pwr, 'DATE':date, 'refreshValue':rV, 'xR':x1, 'xG':x24, 'COLOR':color, 'ex':None}
    return(template('gauge.html', **gaugeData)), 200 #200 = OK, data passed to gauge webpage
    
#/graph
@app.route('/graph', methods=['GET'])
def graph():
    (lid, rlid, tyme, dely, code, temp, humi, btmp, rssi, snr, pwr, date) = single_data()
    (lidGr, rlidGr, tymeGr, delyGr, tempGr, humiGr, btmpGr, rssiGr, snrGr, pwrGr, xaxis) = all_data()
    delay=int(dely)
    rV=delay*1000
    if(delay==10):
        base=delay*360
        rV=60000
    if(delay==30):
        base=delay*120
    if(delay==60):
        base=delay*60

    xH=int((int(xaxis)/base)*delay) #xH is the number of hours being displayed 
    if(xH==0):
        xH='ALL'
    x1=int(base/delay) #x1 = 1 hour of readings (x axis=base/delay=1 hour)
    x3=int(x1*3) #x1*3 = 3 hours
    x6=int(x1*6) #x1*6 = 6 hours
    x12=int(x1*12) #x1*12 = 12 hours
    x24=int(x1*24) #x1*24 = 24 hours
    xW=int(x24*7) #x24*7 = 7 days
    x4W=int(xW*4) #x7*4 = 4 weeks
    color='#FFFFFF'
    if(code=='Good'):
        color='#00C800'
    if(code=='HighTemp'):
        color='#C80000'
    if(code=='LowTemp'):
        color='#0000C8'
    if(code=='LowHumi'):
        color='#00BBBB'
    graphData={'ITN':lid, 'RLID':rlid, 'DELAY':dely, 'CODE':code, 'TEMP':temp, 'HUMI':humi, 
               'RSSI':rssi, 'SNR':snr, 'LID':lidGr, 'TEMPGR':tempGr, 'HUMIGR':humiGr, 'RSSIGR':rssiGr,
               'SNRGR':snrGr, 'refreshValue':rV, 'xH':xH, 'x1':x1, 'x3':x3, 'x6':x6, 
               'x12':x12, 'x24':x24, 'xW':xW,  'x4W':x4W, 'COLOR':color, 'ex':None}
    return(template('graph.html', **graphData)), 200
    
#/radiostat
@app.route('/radiostat', methods=['GET'])
def radio_stats():
    (lid, rlid, tyme, dely, code, temp, humi, btmp, rssi, snr, pwr, date) = single_data()
    (lidGr, rlidGr, tymeGr, delyGr, tempGr, humiGr, btmpGr, rssiGr, snrGr, pwrGr, xaxis) = all_data()
    delay=int(dely)
    rV=delay*1000
    if(delay==10):
        base=delay*360
        rV=60000
    if(delay==30):
        base=delay*120
    if(delay==60):
        base=delay*60
    xH=int((int(xaxis)/base)*delay)
    if(xH==0):
        xH='ALL'
    x1=int(base/delay)
    x3=int(x1*3)
    x6=int(x1*6)
    x12=int(x1*12)
    x24=int(x1*24)
    xW=int(x24*7)
    x4W=int(xW*4)
    radioData={'ITN':lid, 'LID':lidGr, 'DELAY':dely, 'RLID':rlid, 'RSSI':rssi, 'SNR':snr, 'PWR':pwr,
               'BTEMP':btmp, 'RSSIGR':rssiGr, 'SNRGR':snrGr, 'PWRGR':pwrGr, 'BTEMPGR':btmpGr, 'refreshValue':rV, 
               'xH':xH, 'x1':x1, 'x3':x3, 'x6':x6, 'x12':x12, 'x24':x24, 'xW':xW, 'x4W':x4W, 'ex':None}
    return(template('radiostat.html', **radioData)), 200
    
#/graphs
@app.route('/graphs', methods=['GET'])
def indv_graph():
    (lid, rlid, tyme, dely, code, temp, humi, btmp, rssi, snr, pwr, date) = single_data()
    (lidGr, rlidGr, tymeGr, delyGr, tempGr, humiGr, btmpGr, rssiGr, snrGr, pwrGr, xaxis) = all_data()
    delay=int(dely)
    rV=delay*1000
    if(delay==10):
        base=delay*360
        rV=60000
    if(delay==30):
        base=delay*120
    if(delay==60):
        base=delay*60
    xH=int((int(xaxis)/base)*delay)
    if(xH==0):
        xH='ALL'
    x1=int(base/delay)
    x3=int(x1*3)
    x6=int(x1*6)
    x12=int(x1*12)
    x24=int(x1*24)
    xW=int(x24*7)
    x4W=int(xW*4)
    color='#FFFFFF'
    if(code=='Good'):
        color='#00FF00'
    if(code=='HighTemp'):
        color='#FF0000'
    if(code=='LowTemp'):
        color='#0000FF'
    if(code=='LowHumi'):
        color='#00BBBB'
    graphData={'ITN':lid, 'RLID':rlid, 'DELAY':dely, 'CODE':code, 'TEMP':temp, 'HUMI':humi, 
               'RSSI':rssi, 'SNR':snr, 'LID':lidGr, 'TEMPGR':tempGr, 'HUMIGR':humiGr, 'RSSIGR':rssiGr,
               'SNRGR':snrGr, 'refreshValue':rV, 'xH':xH, 'x1':x1, 'x3':x3, 'x6':x6, 
               'x12':x12, 'x24':x24, 'xW':xW,  'x4W':x4W, 'COLOR':color, 'ex':None}
    return(template('indvGraphs.html', **graphData)), 200
    
#changes graph x axis with buttons
@app.route('/graph', methods=['POST','GET'])
def graph_input():
    if(request.method=='POST'):
        xID=request.form['x']
        inputData={'x':xID}
        return(redirect(url4('graph_input', **inputData))), 302
    return(template('graph.html')), 201
    
@app.route('/radiostat', methods=['POST','GET'])
def radio_input():
    if(request.method=='POST'):
        xID=request.form['x']
        inputData={'x':xID}
        return(redirect(url4('radio_input', **inputData))), 302
    return(template('radiostat.html')), 201

@app.route('/graphs', methods=['POST','GET'])
def indv_graph_input():
    if(request.method=='POST'):
        xID=request.form['x']
        inputData={'x':xID}
        return(redirect(url4('indv_graph_input', **inputData))), 302
    return(template('indvGraphs.html')), 201

if(__name__=='__main__'):
    app.run(host='192.168.1.12', port=5001, debug=True)