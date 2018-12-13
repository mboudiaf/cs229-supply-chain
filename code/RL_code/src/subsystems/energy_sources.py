author = 'Malik Boudiaf, mboudiaf@stanford.edu'

import numpy as np
from subsystems.subsystem import Subsystem

class energy_sources (Subsystem):
    
    
    def __init__(self,prod_dataset,discrete_prod):
        
        self.discrete_prod = discrete_prod
        self.dataset=prod_dataset #kW
        self.current_ind = 0
        self.current_prod = self.find_closest_discrete_load(self.discrete_prod,self.dataset[self.current_ind]) #kW



    def get_current_prod(self):
    	return self.current_prod

    def update_with_data(self):
        self.current_prod = self.find_closest_discrete_load(self.discrete_prod,self.dataset[self.current_ind]) #kW
        self.current_ind += 1

    def reset(self,prod_dataset):
        self.dataset = prod_dataset
        self.current_ind=0
        self.current_prod= self.find_closest_discrete_load(self.discrete_prod,self.dataset[self.current_ind]) #kW


        
        
        
        
    
    