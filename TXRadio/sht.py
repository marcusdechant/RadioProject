#sht.py
#(c) Marcus Dechant 2022
#Temperature and Humidity Sensor
import lib.SHT31D.adafruit_sht31d as SHT
import busio as BU
import board as BO
ICC=BU.I2C(scl=BO.GP19,sda=BO.GP18,frequency=200000)
sht30=SHT.SHT31D(ICC)
def t():
    TEMP=sht30.temperature
    temp=('{0:0.2f}'.format(TEMP))
    return(temp)
def h():
    HUMI=sht30.relative_humidity
    humi=('{0:0.2f}'.format(HUMI))
    return(humi)

