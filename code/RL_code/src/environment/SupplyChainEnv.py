author = 'Malik Boudiaf, mboudiaf@stanford.edu'

from random import random, choice
from scipy import zeros
import numpy as np
from utilities import Named
from environment.environment import Environment
from subsystems.battery import battery
from subsystems.electrolyzer import electrolyzer
from subsystems.grid import grid
from subsystems.H2_vessel import H2_vessel
from subsystems.energy_sources import energy_sources
from subsystems.H2_station import H2_station



class SupplyChainEnv(Environment, Named):
    """ A draft of the Supply Chain Environment we need our agent to interact with
    """

    def __init__(self,prod_dataset,price_dataset,discrete_battery,discrete_vessel,discrete_elec_regime,discrete_grid_price,discrete_prod,discrete_buy_sell,**args):
        self.setArgs(**args)
        self.battery = battery(discrete_battery)
        self.h2_vessel = H2_vessel(discrete_vessel)
        self.h2_station = H2_station()
        self.electrolyzer = electrolyzer(discrete_elec_regime)
        self.energy_sources = energy_sources(prod_dataset,discrete_prod)
        self.grid = grid(price_dataset,discrete_grid_price)
        self.time=0
        self.terminal= False
        self.time_step= 1 #h

        # Create the table of all possible actions, and a mapping from their id to their value
        discretization_elec = discrete_elec_regime #electrolyzer functionning
        discretization_grid = discrete_buy_sell # how much electricity do we buy/sell ? (as % of battery SOC, >0 represents selling)
        allActions=[]
        id2action={}
        count=0
        for i in discretization_elec:
            for j in discretization_grid:
                allActions.append([i,j]) 
                id2action[count]=[i,j]
                count += 1


        # stochasticity
        self.stochAction = 0.
        self.stochObs = 0.
        self.allActions=allActions
        self.id2action=id2action

    def reset(self,prod_dataset,price_dataset):
        """ return to initial position (stochastically): """
        # Reinitialize charge of battery
        # Reinitialize H2 in H2_vessel
        self.battery.reset()
        self.h2_vessel.reset()
        self.time= 0
        self.grid.reset(price_dataset)
        self.energy_sources.reset(prod_dataset)
        self.electrolyzer.reset()
        self.terminal=False

    def performAction(self, action):
        """ updates the environment by performing the given action
        action : 
        """

        #If we want to introduce some stochasticity
        self.grid.update_with_data()
        self.energy_sources.update_with_data()

        self.electrolyzer.set_regime(action[0])
        flow_from_grid=action[1]/100*self.battery.capacity # kW 
        flow_from_sources=self.energy_sources.get_current_prod() #kw
        flow_to_electrolyzer=self.electrolyzer.get_required_input()
        flow_battery=flow_from_sources-flow_to_electrolyzer+flow_from_grid
        #print("From sources:",flow_from_sources)
        #print("Required by electrolyzer",flow_to_electrolyzer)
        #print("From/to the grid",flow_from_grid)
        #print("Flow through battery",flow_battery)
        gas_flow=self.electrolyzer.get_h2_produced(self.time_step)-self.h2_station.get_required_h2()
        # Update battery SOC based on current state and action
        self.terminal_battery = self.battery.update_battery_load(flow_battery,self.time_step)
        # Update quantiy of H2 in pressure vessel
        self.terminal_vessel = self.h2_vessel.update_H2_vessel_load(gas_flow,self.time_step)
        self.time = (self.time + 1) % 24

        
    def state2id(self,battery_current_load,h2_vessel_current_load,grid_fluct_price,energy_sources_current_prod,time,electrolyzer_regime):
        N_battery_values=len(self.battery.load_discretization)
        N_h2_values=len(self.h2_vessel.load_discretization)
        N_prod_values=len(self.energy_sources.discrete_prod)
        N_price_values=len(self.grid.fluct_price_discretization)
        N_regimes=len(self.electrolyzer.discrete_regime)

        idx_battery=np.where(battery_current_load==self.battery.load_discretization)[0][0]
        idx_h2=np.where(h2_vessel_current_load==self.h2_vessel.load_discretization)[0][0]
        idx_prod=np.where(energy_sources_current_prod==self.energy_sources.discrete_prod)[0][0]
        idx_price=np.where(grid_fluct_price==self.grid.fluct_price_discretization)[0][0]
        idx_electrolyzer=np.where(electrolyzer_regime==self.electrolyzer.discrete_regime)[0][0]

        return int(idx_electrolyzer+N_regimes*(time+ 24*(idx_battery + N_battery_values*(idx_h2 + N_h2_values*(idx_prod + N_prod_values*idx_price)))))




