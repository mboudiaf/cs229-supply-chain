author = 'Malik Boudiaf, mboudiaf@stanford.edu'

import numpy as np
from subsystems.subsystem import Subsystem


class battery(Subsystem):
    
    
    def __init__(self,load_discretization,n_batteries = 200):
        
        self.c_min = 0.05
        self.c_max= 0.95
        self.efficiency = 0.89
        self.max_inflow = 50 #kW , max charging flow
        self.max_outflow = -50 #kW, max discharging flow
        self.capacity = n_batteries*210 #kWh
        self.current_load=load_discretization[int(len(load_discretization)/2)]
        self.IV_curve=None
        self.load_discretization=load_discretization 
        print("Initial battery load :", self.current_load/100*self.capacity, " kW.h")
        
    #%% Storage type I: Batteries    
        
    def load_csv_battery_IV_curve(self,storage_type,C_rate):
        # I-V data for each type of battery and 
        
        csv_path = 'IV_curve'+C_rate+'.csv'
        with open(csv_path, 'r', newline='') as csv_fh:
            headers = csv_fh.readline().strip().split(',')
    
        I_cols = [i for i in range(len(headers)) if headers[i] == 'I']
        V_cols = [i for i in range(len(headers)) if headers[i] == 'V']
        I_data = np.loadtxt(csv_path, delimiter=',', skiprows=1, usecols=I_cols)
        V_data = np.loadtxt(csv_path, delimiter=',', skiprows=1, usecols=V_cols)
        
        IV_curve = [I_data,V_data]
        IV_curve.shape(-1,2)
        
        self.IV_curve=IV_curve
    
    
    
    def update_battery_load(self,power_flow,time_step):
        # power_flow > 0: storage
        # power_flow < 0: discharge
        #return a bool (called 'terminal') if the update is impossible (we ask the battery to provide more energy than it currently has)
        terminal=False

        #power_flow = self.max_inflow
           # print("!!!!!!!!!!!!!!!! Max charging flow reached")
        #elif power_flow < self.max_outflow:
        #power_flow = self.max_outflow
            #print("!!!!!!!!!!!!!!!! Max discharging flow reached")

            #power_flow = self.max_inflow ## Zoe : not sure about this ?
            #print("!!!!!!!!!!!!!!!! Max charging flow reached")
        #elif power_flow < self.max_outflow:
        #    power_flow = self.max_outflow ## Zoe : same
            #print("!!!!!!!!!!!!!!!! Max discharging flow reached")

        self.current_load += power_flow * time_step *100 / self.capacity
        
        if self.current_load >= 100:
            self.current_load = 100
        if self.current_load <= 0:
            terminal=True
        self.current_load=self.find_closest_discrete_load(self.load_discretization,self.current_load) #Here we find the closest value in discretized table
        return terminal
        
        

    def reset(self):
        # resets the battery load to an initial value
        self.current_load=self.load_discretization[int(len(self.load_discretization)/2)]

        
        
        
    
    
