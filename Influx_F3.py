#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 29 10:21:34 2024

@author: user272
"""

import Influx_test1 as IT
import time
from func_timeout import func_timeout, FunctionTimedOut

def SendCommand(modules, command, location, timeout):
    print(command, 'started')
    start_time = influx_class.SendCommand(modules, command, location)
    print(start_time)
    status = None
    while status is None:
        status = func_timeout(timeout, influx_class.is_command_complete, args = (start_time, command, location))
    print(status["DATA"])

if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Test ITSDAQ commands.')
    parser.add_argument('-c','--config',required=True,help='Part to influx config INI.')
    args=parser.parse_args()

    from ITSDAQ_COMM.ITK_INFLUX import ITK_INFLUX
    Influx = ITK_INFLUX(args.config)
    influx_class=IT.Coldjig_Influx_COMM(Influx)
    modules=[0,1,3]
    #steps_to_test = ["INIT_MODULES", "INIT_BURNIN", "RUN_COLD_CHARACTERISATION", "HV_STABILISATION", "STATUS", "ABORT", "RUN_HYBRID_BURNIN_TESTS", "RUN_WARM_CHARACTERISATION"]
    INITRUN = ["INIT_RUN", "ITSDAQ"]
    HON = ["HYBRID_ON", "ITSDCS"]
    INITDAQ = ["INIT", "ITSDAQ"]
    INITDCS = ["INIT", "ITSDCS"]
    IV = ["IVSCAN", "ITSDAQ"]
    HVON = ["HV_ON", "ITSDAQ"]
    CHAR = ["RUN_CHARACTERISATION", "ITSDAQ"]
    HVOFF = ["HV_OFF", "ITSDAQ"]
    HOFF = ["HYBRID_OFF", "ITSDCS"]
    
    startup = [INITRUN, HON, INITDAQ, INITDCS, IV, HVON]
    IVscan = [HVOFF, IV, HVON]
    shutdown = [HVOFF, HOFF]
    breaks = [HVOFF, HVON]
    
    Type = None
    while Type != "n" and Type != "y":
        
        Type = str(input("Long running test? y/n \n"))
        
        if Type == "n":
            runtime = 60 #Arbitrary, just long enough to get it to start once
        elif Type == "y":
            runtime = 3600*int(input("How long would you like this to run (in hours)? \n"))
        else:
            print("Not a valid input, please try again")
            
    #Startup:
    for step in startup:
        SendCommand(modules, )
    time.sleep(2)
    
    #Main:
    
    StartTime = time.time()
    IVtime = StartTime
    Fails = 0
    while time.time() <= StartTime + runtime:
        try:
            SendCommand(modules, CHAR[0], CHAR[1], 600)
        except FunctionTimedOut:
            Fails += 1
            if Fails == 3:
                break
            else:
                Fails = 0
                continue
        if time.time() - IVtime > 3600:
            try:
                for IVstep in IVscan:
                    SendCommand(modules, IVstep[0], IVstep[1], 1200)
                    
            except FunctionTimedOut:
                Fails += 1
                if Fails == 3:
                    for step in breaks:
                        SendCommand(modules, breaks[0], breaks[1], 1200)
                        IVtime = time.time()
                    break
                else:
                    Fails = 0
                    IVtime = time.time()
                    continue
        time.sleep(1200)
    
    #Shutdown:
        for step in shutdown:
            SendCommand(modules, step[0], step[1], 600)
        