author = 'Malik Boudiaf, mboudiaf@stanford.edu'

from environment.task import Task
from scipy import array
import numpy as np
class SupplyTaskMDP(Task):
    """ This is a MDP task for the MazeEnvironment. The state is fully observable,
        giving the agent the current position of perseus. Reward is given on reaching
        the goal, otherwise no reward. """

    def getReward(self,action):
        """ """
        ##################### LILIE ##########################################
        if self.env.terminal_battery or self.env.terminal_vessel: #if an action was not allowed
            return -100000
        #elif self.env.time==47:
        #    return 100000
        else:
            return -self.env.grid.fluct_price*action[1]*self.env.battery.capacity/100  
        #Compute the reward based on the observations of the current environment self.env

        #return rewardx

        ####################### ZOZ #########################################
        
        #flow_from_grid=action[1]/100*self.env.battery.capacity # kW 
        #flow_from_sources=self.env.energy_sources.get_current_prod() #kw
        #flow_to_electrolyzer=self.env.electrolyzer.get_required_input()
        #flow_battery=flow_from_sources-flow_to_electrolyzer+flow_from_grid
        #gas_flow = self.env.electrolyzer.get_h2_produced(self.time_step)
        #clients = 0;
        #gas_flow_vessel = gas_flow - clients ## be careful : the H2 given to clients must be removed from this number
        
        #### Battery 
        
        # Storage capacity
        #if self.env.battery.current_load > self.env.battery.c_max || self.env.battery.current_load < self.env.battery.c_min:
        #    R = R - 10^5
        # charge/discharge
        #if flow_battery > max_inflow || flow_battery < max_outflow :
        #    R = R - 10^5
        # Load rate management  (see Constraints doc): ?? pb we dont know what was the flow_battery before. We should add it to "battery"
        # if abs(current_flow_battery - flow_battery) > delta_phi_max 
            # R = R - 10^5
        # Energy Balance  (see Constraints doc) ==> efficiency of battery should be taken into account in the computation of flow_battery ?
        

        #### Pressure Vessel
        
        # Storage capacity
        #if self.env.H2_vessel.current_load > self.env.H2_vessel.c_max || self.env.H2_vessel.current_load < self.env.H2_vessel.c_min:
        #    R = R - 10^5
       
        # Charge/Discharge
       #if gas_flow_vessel > self.env.H2_vessel.max_inflow || gas_flow_vessel < self.env.H2_vessel.max_outflow
        #   R = R - 10^5
        
        # hydrogen balance : computed when current_load is computed    
           
        #### Electrolyser 
        
        #if gas_flow > self.env.electrolyzer.max_prod || gas_flow < self.env.electrolyzer.min_prod:
        #    R = R - 10^5;
            
        # Energy balance and Production rate management are computed when gas_flow is computed
        
        #### Positive rewards
        
        #R = R - self.env.grid.fluct_price*action[1]/100    ### attention : sign to be verified
        # If we want to give a value to what is inside of the battery :
            # R = R + self.env.battery.current_load*self.env.battery.capacity/100*self.env.grid.nominal_price
            # where formula for total energy in the battery must be verified
            # nominal price should be added to the subsystem grid and could be the average price
        
            
        
    def performAction(self, action):
        """ The action vector is stripped and the only element is cast to integer and given
            to the super class.
        """
        Task.performAction(self, action)


    def getObservation(self):
        """ The agent receives its position in the maze, to make this a fully observable
            MDP problem.
        """
        real_state =[self.env.battery.current_load,self.env.h2_vessel.current_load,self.env.grid.fluct_price,self.env.energy_sources.current_prod,self.env.time,self.env.electrolyzer.regime]
        #state_id = None
        state_id = array([self.env.state2id(self.env.battery.current_load,self.env.h2_vessel.current_load,self.env.grid.fluct_price,self.env.energy_sources.current_prod,self.env.time,self.env.electrolyzer.regime)])
        return state_id,real_state



