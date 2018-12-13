author = 'Malik Boudiaf, mboudiaf@stanford.edu'

import numpy as np
from subsystems.subsystem import Subsystem

class H2_vessel (Subsystem):
    
    
    def __init__(self,load_discretization, n_vessel = 40):
        
        self.c_min = 0.1
        self.c_max= 1
        self.efficiency = 0.95
        self.max_inflow = 92 #kg/h , max charging flow
        self.max_outflow = -300 #kg/h, max discharging flow
        self.capacity = 10*n_vessel #kg
        self.load_discretization=load_discretization
        self.current_load=load_discretization[int(len(load_discretization)/2)]
        print("Initial vessel load :", self.current_load*self.capacity/100, " kg")
   
    
    #%% Storage type II: H2 storage
        
    def update_H2_vessel_load(self, gas_flow,time_step):
        # flow > 0: storage
        # flow < 0: discharge 
        # flow is in kg/h and time_step is in h
        terminal=False
        #if gas_flow > self.max_inflow:
        #    gas_flow = self.max_inflow
        #elif gas_flow < self.max_outflow:
        #    gas_flow = self.max_outflow
        if self.current_load >= 100:
            self.current_load = 100
        self.current_load += gas_flow * time_step *100 / self.capacity ## be careful : accordint to the constraints paper (page 2), we must remove from this number the self_hydrogen consumption to run the H2 compressors
        if self.current_load <= 0:
            terminal=True
        self.current_load = self.find_closest_discrete_load(self.load_discretization,self.current_load) #Here we find the closest value in discretized table
        return terminal
        
    def reset(self):
        self.current_load=self.load_discretization[int(len(self.load_discretization)/2)]
        
        
        
        
    
    
