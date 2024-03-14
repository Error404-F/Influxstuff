#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 16:16:41 2024

@author: user272
"""

from pyftdi.i2c import I2cController
import time
#import numpy as np
import matplotlib.pyplot as plt
import datetime
import matplotlib.gridspec as gridspec
from influxdb_client import InfluxDBClient

token ='fCtqVLxNkcQCau7JO7vmcF99WjvbIO0Z2c_eNaUr3X2xtG-r02hJweylrBx223uNNLI7nNk63fKMK9WfkvfHTw=='
org = 'ITk'
client = InfluxDBClient(url="http://eprex5.ph.bham.ac.uk:8086", token=token, org=org)
write_api = client.write_api()
with open('HumidityData/RunNumber','r') as file:
    run =int(file.read())
    run += 1
with open('HumidityData/RunNumber', 'w') as file:
    file.write(str(run))

filename = 'HumidityData/HumAndTempData_Run'+str(run)+'.txt'
f = open(filename, 'w+')



#sensors = int(input('Number of sensors (USBs) '))

ctrl = I2cController()
ctrl.configure('ftdi:///1')
i2c = ctrl.get_port(0x27)

a = input('Humidity and Temperature? y/n \n')
runtime =int(input('Runtime (minutes)'))*60
print(runtime)
if a == 'y':
    byte = 4
else:
    byte = 2
bits = byte*8
z = 0
Humidity = []
Temperature = []
Time = []
start = time.time()
while time.time()<=start+runtime:
    while z == 0:
        i2c.write([0x27, 0])
        out = i2c.exchange([0x27, 1], byte)
        Hex = ''.join(format(x, '02x') for x in out)
        i = bin(int(Hex, 16))
        measure = time.time()
        t = measure-start
        #t2 = datetime.timedelta(seconds = t)
        #print(i)
        #print(len(i))
        #print(i[2:])
        
        x = f"{i[2:]:>0{bits}}"
        #print(x)
        hum = (int(x[2:16], 2)*100)/(2**14 - 1)
        per = str(hum)[:5]+'%'
        temp = None
        
        if per == '100.0%':
            continue
        else:
            print('Humidity:',per)
            Humidity.append(hum)
            Time.append(t)
            if a == 'y':
                temp = ((int(x[17:30], 2)*165)/(2**14-1))-40
                deg = str(temp)[:5] + u'\u2103'
                print('Temperature: ',deg)
                Temperature.append(temp)
                z = 1
        f.write(f'{measure}\t{hum}\t{temp}\n')
        write_api.write("longtermsetup", "ITk", [{"measurement": "Humidity and Temperature", "tags": {"location": "PB8 Box"}, "fields": {"Humidity": hum, "Temperature": temp }}])
    print()
    
    
    #Time = pd.to_datetime(Time)
    fig = plt.figure()
    gs = gridspec.GridSpec(2, 1, height_ratios=[1,1])
    ax = fig.add_subplot(gs[0])
    #myFmt = mdates.DateFormatter('%H,%M,%S')
    #ax.xaxis.set_major_formatter(myFmt)
    ax.plot(Time, Humidity)
    plt.xlabel('TIme/s')
    plt.ylabel('Humidity/%')
    if a == 'y':
        ax = fig.add_subplot(gs[1])
        ax.plot(Time, Temperature, 'HotPink')
        plt.xlabel('TIme/s')
        plt.ylabel('Temperature/Celsius')
    #x.gcf().autofmt_xdate()
    #plt.show()
    print(time.time()-(start+runtime))

    time.sleep(0.1)
    z = 0
    plt.close()

save = 'HumidityData/Run'+str(run)+'.png'
fig = plt.figure()
gs = gridspec.GridSpec(2, 1, height_ratios=[1,1])
ax = fig.add_subplot(gs[0])
#myFmt = mdates.DateFormatter('%H,%M,%S')
#ax.xaxis.set_major_formatter(myFmt)
ax.plot(Time, Humidity)
plt.xlabel('TIme/s')
plt.ylabel('Humidity/%')
if a == 'y':
    ax = fig.add_subplot(gs[1])
    ax.plot(Time, Temperature, 'HotPink')
    plt.xlabel('TIme/s')
    plt.ylabel('Temperature/Celsius')

plt.savefig(save)
