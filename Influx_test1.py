#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  3 13:54:15 2023

@author: user272
"""

from influxdb_client import InfluxDBClient, Point
import time
import json
import logging
#from .ITK_INFLUX import ITK_INFLUX

#from modules.GUIlogging import init_logger

logger = logging.getLogger(__name__)

Influx = None # 
#influx_ini_file= "" # Path to ini file

def parse_errorstr(errorstr):
    """
    check error string returned by ITSDAQ
    - `None` : No Error --> return `None`
    - "" (empty string) : No Error  --> return `None`
    - "NONE" (case insensitive) : No Error  --> return `None`
    - anything else is considered an error --> return errorstr
    """

     # If errorstr is None, return None
    if errorstr is None :
        return None

    # Check for empty string
    if  errorstr  == "":
        return None

    # Check for case insensitve NONE
    if errorstr.lower() == "none" :
        return None

    # Got here...errorstr is a real error
    return errorstr

def parse_datastr(datastr):
    """
    check data string returned by ITSDAQ
    - Apply same parsing as for `parse_errorstr`.
    - `None` : No Data --> return `None`
    - Try `json.loads` --> return JSON structure
    - return original
    """

    # Apply same parsing as for an error string
    datastr=parse_errorstr(datastr)

    # If datastr is None, return None
    if datastr is None :
        return None

    # Try to parse json
    try:
        return json.loads(datastr)
    except json.decoder.JSONDecodeError as e:
        pass

    # Got here...datastr is some random data
    return datastr

class Coldjig_Influx_COMM:

    logger = logging.getLogger(__name__)
    
    def __init__(self, Influx):
        self.Influx = Influx
        self.setup=Influx.influxAttributeDictionary['setup']
        self.bucket=Influx.influxAttributeDictionary['bucket']
        self.sender=Influx.influxAttributeDictionary['setup_type']
        self.comm_measurement=Influx.influxAttributeDictionary['comm_measurement']
        logger.info(f'setup {self.setup}, bucket is {self.bucket}, sender is {self.sender}, comm_measurement is {self.comm_measurement}')

    def convertor(self,modules_list):
        json_d={'modules':modules_list}
        modules_string=json.dumps(json_d)
        return modules_string

    def SendCommand(self,modules,command_str,receiver):
        modules=self.convertor(modules)
        start_time = time.time_ns()
        point = Point("COMM").tag("SETUP", self.setup).tag("SENDER",self.sender).tag("RECEIVER", receiver).field("COMMAND",command_str).field("DATA", modules).field("ERROR", "NONE")
        self.Influx.write_comm_point(point)
        logger.info(f' Running {command_str} {modules}')
        return start_time

    def get_ITSDAQ_STATUS(self, start_time):
        logger.debug('Get ITSDAQ status')
        query= f'''
        from(bucket: \"{self.bucket}\") 
        |> range(start: time(v: {start_time}), stop: now())
        |> filter(fn: (r) => r["_measurement"] == \"{self.comm_measurement}\")
        |> filter(fn: (r) => r["SENDER"] == \"ITSDAQ\") 
        |> filter(fn: (r) => r["SETUP"] == \"{self.setup}\")  
        |> filter(fn: (r) => r["_field"] == \"COMMAND\" or r["_field"] == \"DATA\" or r["_field"] == \"ERROR\")  
        |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: \"_value\") 
        |> yield(name: \"last\")
        '''
        logger.debug(f'{query}')
        # logger.debug(f'query object is  {self.Influx.query_api.query(query)}')
        tables = self.Influx.query_api.query(query)
        logger.debug(f'tables are {tables}')
        try:
            for record in tables[0].records:
                if record["COMMAND"] == "STATUS":
                    record["ERROR"] = parse_errorstr(record["ERROR"])
                    logger.info(f' Data from ITSDAQ {record["DATA"]}')
                    logger.info(f' ERROR {record["ERROR"]}')
                    return {"DATA": record["DATA"], "ERROR": record["ERROR"]}
                else:
                    return None
        except Exception as e:
            logger.info("WAITING FOR ITSDAQ")
            return None


    def is_command_complete(self, start_time, command, receiver):
        '''
        Check ITSDAQ command has completed.  When complete
        ITSDAQ will echo the command with value "Complete"        
        '''

        logger.debug(f'Check {command} has completed')
        query= f'''
        from(bucket: \"{self.bucket}\")
        |> range(start: time(v: {start_time}), stop: now())
        |> filter(fn: (r) => r["_measurement"] == \"{self.comm_measurement}\")
        |> filter(fn: (r) => r["SENDER"] == \"{receiver}\")
        |> filter(fn: (r) => r["RECEIVER"] == \"COLDJIG\")
        |> filter(fn: (r) => r["SETUP"] == \"{self.setup}\")
        |> filter(fn: (r) => r["_field"] == \"COMMAND\" or r["_field"] == \"DATA\" or r["_field"] == \"ERROR\")
        |> drop(columns: [\"_start\",\"_stop\"])
        |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: \"_value\")
        |> filter(fn: (r) => r["COMMAND"] == \"{command}\")
        |> yield(name: \"last\")
        '''
        logger.debug(f'{query}')
        tables = self.Influx.query_api.query(query)
        logger.debug(f'tables are {tables}')
        if len(tables) == 0:
            logger.debug(f'{command} not completed')
            return None # no response detected yet
        else :
            logger.info("Message(s) sent to ColdJig")

            for record in tables[0].records:
                record["ERROR"] = parse_errorstr(record["ERROR"])
                record["DATA"] = parse_datastr(record["DATA"])

                logger.info(f' Data from ITSDAQ {record["DATA"]}')
                logger.info(f' ERROR {record["ERROR"]}')
                logger.info(f' TIME {record["_time"]}')

                return {"DATA": record["DATA"], "ERROR": record["ERROR"]}


if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Test ITSDAQ commands.')
    parser.add_argument('-c','--config',required=True,help='Part to influx config INI.')
    args=parser.parse_args()

    from ITSDAQ_COMM.ITK_INFLUX import ITK_INFLUX
    Influx = ITK_INFLUX(args.config)
    influx_class=Coldjig_Influx_COMM(Influx)
    modules=[0,1,3]
    #steps_to_test = ["INIT_MODULES", "INIT_BURNIN", "RUN_COLD_CHARACTERISATION", "HV_STABILISATION", "STATUS", "ABORT", "RUN_HYBRID_BURNIN_TESTS", "RUN_WARM_CHARACTERISATION"]
    A = ["INIT_RUN", "ITSDAQ"]
    B = ["HYBRID_ON", "ITSDCS"]
    C = ["INIT", "ITSDAQ"]
    D = ["INIT", "ITSDCS"]
    E = ["IVSCAN", "ITSDAQ"]
    F = ["HV_ON", "ITSDAQ"]
    G = ["RUN_CHARACTERISATION", "ITSDAQ"]
    H = ["HV_OFF", "ITSDAQ"]
    I = ["HYBRID_OFF", "ITSDCS"]
    #steps_to_test = [A, B, C, D, E, F, G, H, I]
    steps_to_test = [A, B, C, D, E, F, G, H, I]
    
    for step in steps_to_test:
        if step[0] == 'RUN_CHARACTERISATION':
            k = 0
            while k < 1:
                print(step[0], 'started')
                start_time = influx_class.SendCommand(modules, step[0], step[1])
                print(start_time)
                status = None
                while status is None:
                    status = influx_class.is_command_complete(start_time, step[0], step[1])
                print(status["DATA"])
                k+=1
                time.sleep(60)
                
            
        else:
            print(step[0], 'started')
            start_time = influx_class.SendCommand(modules, step[0], step[1])
            print(start_time)
            status = None
            while status is None:
                status = influx_class.is_command_complete(start_time, step[0], step[1])
            print(status["DATA"])
            time.sleep(2)
