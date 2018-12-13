author = 'Malik Boudiaf, mboudiaf@stanford.edu'

from subsystems.subsystem import Subsystem
import numpy as np

class electrolyzer (Subsystem):
    
    
    def __init__(self,discrete_elec_regime,n_conv = 1):
        self.min_prod=0.15 # Zoe: I changed it, it used to be max = 0.15 and min = 1
        self.max_prod=1
        self.max_regime = 150*1.25*n_conv # kg/h produced
        self.discrete_regime=discrete_elec_regime
        self.efficiency= 53.9 # [kW.h / kg]
        self.regime=self.find_closest_discrete_load(self.discrete_regime,30)  # % of max_regime
        print("Initial electrolyzer regime :", self.regime)
        
    def get_required_input(self):
        #from the regime set, returns the required input power to the electrolyzer in [kW]
        return self.efficiency*self.regime/100*self.max_regime

    def set_regime(self,regime):
        self.regime=regime

    def get_h2_produced(self,time_step):
        #returns the quantity of h2 produced over the given duration
        # time_step in h
        return self.regime/100*self.max_regime*time_step #[kg]

    def reset(self):
        self.regime=self.find_closest_discrete_load(self.discrete_regime,30)  # % of max_regime# % of max_regime
        
        

        
        
        
    
    