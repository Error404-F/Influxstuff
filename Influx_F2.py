import Influx_test1 as IT
import time

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
    #steps_to_test = [A, B, C, D, E, F, G, H, I]
    #steps_to_test = [A, B, C, D, E, F, G, H, I]
    steps_to_test = [INITRUN, HON, INITDAQ, INITDCS, IV, HVON, CHAR, HVOFF, HOFF]
    IV_steps = [HVOFF, IV, HVON]
    
    Type = None
    while Type != "n" and Type != "y":
        
        Type = str(input("Long running test? y/n \n"))
        
        if Type == "n":
            iterations = 1
        elif Type == "y":
            runtime = 3600*int(input("How long would you like this to run (in hours)? \n"))
        else:
            print("Not a valid input, please try again")
        
    for step in steps_to_test:
        if step[0] == 'RUN_CHARACTERISATION':
            starttime = time.time()
            IVtime = starttime
            while time.time() <= starttime + runtime:
                print(step[0], 'started')
                start_time = influx_class.SendCommand(modules, step[0], step[1])
                print(start_time)
                status = None
                while status is None:
                    status = influx_class.is_command_complete(start_time, step[0], step[1])
                print(status["DATA"])
                if time.time() - IVtime > 3600:
                    for IVstep in IV_steps:
                        print(IVstep[0], 'started')
                        start_time = influx_class.SendCommand(modules, IVstep[0], IVstep[1])
                        print(start_time)
                        status = None
                        while status is None:
                            status = influx_class.is_command_complete(start_time, IVstep[0], IVstep[1])
                        print(status["DATA"])
                        
                    IVtime = time.time()
                time.sleep(1200)
            
        else:
            print(step[0], 'started')
            start_time = influx_class.SendCommand(modules, step[0], step[1])
            print(start_time)
            status = None
            while status is None:
                status = influx_class.is_command_complete(start_time, step[0], step[1])
            print(status["DATA"])
            time.sleep(2)
