#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 28 22:38:39 2018

CS229 - ML project 

@author: mcsweeny
"""

import numpy as np
import matplotlib.pyplot as plt
from main_V3 import import_data_csv, optim_main

#%% Path to input files
path_price_power_spot = "../cs229_MILP/input_data/electricity_market/day_ahead_France.csv"
path_h2flow_sales_industry = "../cs229_MILP/input_data/hydrogen_demand/demand_industry.csv"
path_h2flow_sales_mobility = "../cs229_MILP/input_data/hydrogen_demand/demand_mobility.csv"

#%% Duration simulation (max 30)
# Number of days
N_d = 2

#%% Characteristics generating units (solar and wind farms)
# Number of design features
n_gen = 3
# Energy Resource I - Solar farm
capa_solar = np.array([1.0, 2.0, 5.0, 10.0]); #[MW]
# Energy Resource II - Wind farm
capa_wind = np.array([1.0, 2.0, 5.0, 10.0]); #[MW]
# Country
country_project = ['France', 'Germany', 'Denmark_1', 'Denmark_2','SoCal']

#%% Characterisitics energy conversion technology (electrolyzer)
# Number of design features
n_conv = 5
design_conv = np.zeros((n_conv,))
# Minimum rate of production - Buffer rate
design_conv[0] = 20/100 # [%(min power)]
# Maximum rate of conversion
design_conv[1] = 100/100 # [%(max power)]
# Nominal power
design_conv[2] = 1e3 # [kW/unit]
# Optimal conversion efficiency
design_conv[3] = 53.9 # [kWh/kg(H2)]
# Max fluctuation of production
design_conv[4] = 0.5 #[%nom_power]
# Number of units
N_conv = np.array([5, 10, 15, 20])

#%% Characterisitics storage technology I - Battery packs
# Number of types of batteries (Tesla battery pack vs Ultrabattery)
type_batt = {"Li-ion":0,"Pb":1}
n_type_batt = len(type_batt)
# Number of design features 
n_batt = 5
battery = np.zeros((n_batt,n_type_batt))
# Efficiency
battery[0,:] = [0.90, 0.85] # []
# Constraint on the load (nominal, min discharge, max charge)
battery[1,:] = [210, 110] # [kWh] Capacity battery pack 
battery[2,:] = [0.05, 0.20] # [] Minimum load coeff
battery[3,:] = [0.95, 0.95] # [] Maximum load coeff
# Constraints on the charge/discharge 
battery[4,:] = [50, 100] # [kW]
# Number of units (packs)
N_batt = np.array([10, 50, 100, 200]);

#%% Characteristics storage technology II - H2 vessels
n_vess = 2
design_vess = np.zeros((n_vess,))
# cost H2 compression
design_vess[0] = 0.95 # [] efficiency
# 2500 gallon vessel at T=25°C and P=17 bar
design_vess[1] = 10 # [kg(H2)]
# Number of vessels
N_vess = [5, 10, 20, 40]

#%% Hydrogen cost
c_H2_industry = 1.0 # [$/kg(H2)]
c_H2_mobility = 2.0 # [$/kg(H2)]

#%% Inputs
# Simulation solar production 
curve_solar = import_data_csv("../cs229_MILP/input_data/production_sites/solar_prod.csv") # Normalized solar production for farm in selected country
solar_prod = 1e3*capa_solar[0]*curve_solar[::4,1]/max(curve_solar[::4,1]) # [kW]

# Simulation wind production
curve_wind = import_data_csv("../cs229_MILP/input_data/production_sites/wind_prod.csv") # Normalized wind production for a farm in selected country
wind_prod = 1e3*capa_wind[0]*curve_wind[::4,1]/max(curve_wind[::4,1]) # [kW]

#%% Optimization 

# Selection of battery type
design_batt = np.array(battery[:, type_batt["Li-ion"]]).reshape(-1,)
# Paths to input lists
path_data = [path_price_power_spot, path_h2flow_sales_industry, path_h2flow_sales_mobility]

# Optimization process
[y_conv,Eps_batt,M_vess,Psi_conv,Phi_conv,Psi_grid,R] = optim_main(design_conv, N_conv[2], design_batt, N_batt[3], design_vess, N_vess[3], solar_prod, wind_prod, c_H2_industry, c_H2_mobility, N_d, path_data)





