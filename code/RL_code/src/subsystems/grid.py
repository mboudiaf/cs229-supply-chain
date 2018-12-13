author = 'Malik Boudiaf, mboudiaf@stanford.edu'

import numpy as np
from subsystems.subsystem import Subsystem

class grid (Subsystem):
    
    
    def __init__(self,fluct_price_dataset,discrete_grid):
        self.fluct_price_discretization=discrete_grid
        self.fluct_price_dataset=fluct_price_dataset
        self.current_ind=0
        self.fluct_price=self.find_closest_discrete_load(self.fluct_price_discretization,self.fluct_price_dataset[self.current_ind])

    def get_fluct_price(self):
    	return self.fluct_price

    def update_with_data(self):
        self.fluct_price = self.find_closest_discrete_load(self.fluct_price_discretization,self.fluct_price_dataset[self.current_ind]) #kW
        self.current_ind += 1
        

    def reset(self, fluct_price_dataset):
        self.fluct_price_dataset = fluct_price_dataset
        self.current_ind=0
        self.fluct_price= self.find_closest_discrete_load(self.fluct_price_discretization,self.fluct_price_dataset[self.current_ind])

    
    