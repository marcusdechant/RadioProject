#!/bin/python

#Formatted DateTime
#(c) 2022 Marcus Dechant 
#dt.py
#v0.0.1

from datetime import datetime as dt

def tyme():
    tyme=dt.now().strftime('%H:%M:%S')
    return(tyme)

def dayte():
    dayte=dt.now().strftime('%d/%m/%Y')
    return(dayte)