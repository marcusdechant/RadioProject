#!/bin/python3/Radio/dev

#RadioProject
#Remote Sensor Webpage
#Marcus Dechant (c)
#app.rx.dev.py
#v0.1.3

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
database=r'./database/radio.3.db'
    
#flask app
app=Flask(__name__)

#most recent reading
def single_data():
    #database connection
    db=conn(database)
    xcte=db.execute
    clse=db.close
    #pull all from table radio
    curs=xcte('''SELECT LID,RLID,TIME,DELAY,CODE,TEMP,HUMI,BTEMP,RSSI,SNR,DATE FROM RADIO''')
    data=curs.fetchall()
    #iterate for last reading
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
    #return most recent reading
    return(lid, rlid, tyme, dely, code, temp, humi, btmp, rssi, snr, date)

#historical readings
def all_data():
    #database
    db=conn(database)
    xcte=db.execute
    clse=db.close
    #xaxis determines how far back the graph goes.
    xaxis=request.args.get('x')
    try:
        curs=xcte('''SELECT LID,RLID,TIME,DELAY,CODE,TEMP,HUMI,BTEMP,RSSI,SNR,DATE FROM RADIO ORDER BY LID DESC LIMIT %s''' %xaxis)
    except:
        #exception raised when no readings exist in database to handle this the exception is passed as all readings
        xaxis=(-1)
        curs=xcte('''SELECT LID,RLID,TIME,DELAY,CODE,TEMP,HUMI,BTEMP,RSSI,SNR,DATE FROM RADIO ORDER BY LID DESC LIMIT %s''' %xaxis)
    #get all readings and reverse the order (SQL query returns backwards)
    data=reversed(curs.fetchall())
    #reading arrays
    lidGr=[]
    rlidGr=[]
    tymeGr=[]
    delyGr=[]
    tempGr=[]
    humiGr=[]
    btmpGr=[]
    rssiGr=[]
    snrGr=[]
    #fill arrays
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
    #return historical readings
    return(lidGr, rlidGr, tymeGr, delyGr, tempGr, humiGr, btmpGr, rssiGr, snrGr, xaxis)

#/
#address and request method
@app.route('/', methods=['GET'])
#dash
def gauge():
    # variables from gauge_data() (most recent reading)
    (lid, rlid, tyme, dely, code, temp, humi, btmp, rssi, snr, date) = single_data()
    #redefine dely as an integer
    delay=int(dely)
    #refresh value delay * 1000
    rV=int(delay*1000)
    if(delay==10):
        #base is 10*360=3600 (1 hour)
        base=delay*360
        #if delay = 10, rV is negated for 1 minute
        rV=60000
    if(delay==30):
        #30*120=3600 (1 hour)
        base=delay*120
    if(delay==60):
        #60*60=3600 (1 hour)
        base=delay*60
    #x1 = 1 hour of readings (x axis=base/delay=1 hour)
    #used when navigating to Radio Status Graphs
    x1=int(base/delay)
    #x24= 24 hours of readings (x axis=x1*24=24 hours)
    #used when navigating to Readings Graph
    x24=int(x1*24)
    #dynamic text coloring, based on reading code.
    if(code=='Good'):
        #green
        color='00FF00'
    if(code=='HighTemp'):
        #red
        color='FF0000'
    if(code=='LowTemp'):
        #blue
        color='0000FF'
    if(code=='LowHumi'):
        #teal
        color='00BBBB'
    #data passed to gauge webpage
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
        'xR':x1,
        'xG':x24,
        'COLOR':color,
        'ex':None}
    return(template('gauge.html', **gaugeData)), 200 #200 = OK
    
#/graph
@app.route('/graph', methods=['GET'])
#reading graphs
def graph():
    #variables from single_data() (most recent reading)
    (lid, rlid, tyme, dely, code, temp, humi, btmp, rssi, snr, date) = single_data()
    #variables from graph_data() (all reading)
    (lidGr, rlidGr, tymeGr, delyGr, tempGr, humiGr, btmpGr, rssiGr, snrGr, xaxis) = all_data()
    delay=int(dely)
    rV=delay*1000
    if(delay==10):
        base=delay*360
        rV=60000
    if(delay==30):
        base=delay*120
    if(delay==60):
        base=delay*60
    #xH is the number of hours being displayed
    xH=int((int(xaxis)/base)*delay)
    #if xH is zero, it is showing all of the possible readings
    if(xH==0):
        xH='ALL'
    #used to change number of graph readings
    #x1 = 1 hour of readings (x axis=base/delay=1 hour)
    x1=int(base/delay)
    x3=int(x1*3) #x1*3 = 3 hours
    x6=int(x1*6) #x1*6 = 6 hours
    x12=int(x1*12) #x1*12 = 12 hours
    x24=int(x1*24) #x1*24 = 24 hours
    xW=int(x24*7) #x24*7 = 7 days
    x4W=int(xW*4) #x7*4 = 4 weeks
    #base color
    color='FFFFFF'
    if(code=='Good'):
        color='00FF00'
    if(code=='HighTemp'):
        color='FF0000'
    if(code=='LowTemp'):
        color='0000FF'
    if(code=='LowHumi'):
        color='00BBBB'
    #data passed to reading graphs
    graphData={
        'ITN':lid,
        'LID':lidGr,
        'RLID':rlid,
        'DELAY':dely,
        'CODE':code,
        'TEMP':temp,
        'HUMI':humi,
        'RSSI':rssi,
        'SNR':snr,
        'TEMPGR':tempGr,
        'HUMIGR':humiGr,
        'RSSIGR':rssiGr,
        'SNRGR':snrGr,
        'refreshValue':rV,
        'xH':xH,
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
    
#/radiostat
@app.route('/radiostat', methods=['GET'])
#radio status graphs
def radio_stats():
    (lid, rlid, tyme, dely, code, temp, humi, btmp, rssi, snr, date) = single_data()
    (lidGr, rlidGr, tymeGr, delyGr, tempGr, humiGr, btmpGr, rssiGr, snrGr, xaxis) = all_data()
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
    #data passed to radio status graphs
    radioData={
        'ITN':lid,
        'LID':lidGr,
        'DELAY':dely,
        'RLID':rlid,
        'RSSI':rssi,
        'SNR':snr,
        'BTEMP':btmp,
        'RSSIGR':rssiGr,
        'SNRGR':snrGr,
        'BTEMPGR':btmpGr,
        'refreshValue':rV,
        'xH':xH,
        'x1':x1,
        'x3':x3,
        'x6':x6,
        'x12':x12,
        'x24':x24,
        'xW':xW,
        'x4W':x4W,
        'ex':None}
    return(template('radiostat.html', **radioData)), 200
    
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

if(__name__=='__main__'):
    app.run(host='192.168.1.12', port=5001, debug=True)