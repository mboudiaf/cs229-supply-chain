author = 'Malik Boudiaf, mboudiaf@stanford.edu'

import numpy as np
from subsystems.subsystem import Subsystem



class H2_station (Subsystem):
    
    
    def __init__(self):
        self.required_flow=40 + 550/24 # industry = mobility : kg

    def get_required_h2(self):
        return self.required_flow
   
        
        
        
        
    
    