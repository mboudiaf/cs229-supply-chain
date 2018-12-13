#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  1 14:24:30 2018

@author: mcsweeny
"""

import numpy as np
from ortools.linear_solver import pywraplp
import pandas as pd
import sys
import matplotlib.pyplot as plt


def import_data_csv(data_file_path):
    data = pd.read_csv(data_file_path, sep=";")#,header=None)
    return data.values
    


def optim_main(design_conv, N_conv, design_batt, N_batt, design_vess, N_vess, Psi_solar, Psi_wind, c_H2_industry, c_H2_mobility, N_d, path_data):
    
    ## Characteristics units
    # Conversion - Electrolyzer
    prod_rate_min = design_conv[0]
    prod_rate_max = design_conv[1]
    power_nom = N_conv*design_conv[2]
    eff_conv = design_conv[3]
    var_Psi_conv = design_conv[4]
    # Storage capacity I - Electrochemical battery packs
    eff_batt = design_batt[0]
    C_batt = N_batt*design_batt[1]
    load_min = design_batt[2]
    load_max = design_batt[3]
    power_max = N_batt*design_batt[4]
    # Storage capacity II - H2(gas) storage vessels
    eff_vess = design_vess[0]
    C_vess = N_vess*design_vess[1]
   
    ## Inputs
    # Electricity market (spot market)
    Eps_spot = import_data_csv(path_data[0]) # [$/MWh]
    # contract I - Industry demand & price
    Phi_industry = import_data_csv(path_data[1])
    # contract II - H2 stations for mobility & price
    Phi_mobility_d = import_data_csv(path_data[2])
    
    # Simulation duration
    N_t = 24*N_d # [] number of iterations
    dt = 1  # [hr] duration of time step  
    Eps_spot = Eps_spot[0:N_t,1]*1e-3 # [$/kWh]
    Phi_industry = Phi_industry[0:N_t,1]
    Phi_mobility_d = Phi_mobility_d[0:N_d,1]
    Psi_solar = Psi_solar[0:N_t]
    Psi_wind = Psi_wind[0:N_t]
 
    # Plotting inputs
    # Production
    plt.figure(1)
    plt.plot(np.arange(N_t),Psi_solar,label='solar')
    plt.plot(np.arange(N_t),Psi_wind,label='wind')
    plt.xlabel('time [hrs]')
    plt.ylabel('production [kW]')
    plt.xlim([0,N_t])
    plt.ylim([0,1.1*max(max(Psi_solar),max(Psi_wind))])
    plt.grid()
    plt.title('Production of the solar and wind farms')
    plt.show()
    plt.legend()
    plt.figure
    # hydrogen demand
    plt.figure(2)
    plt.subplot(2,1,1)
    plt.bar(np.arange(N_t),Phi_industry,0.8,align="edge") 
    plt.xlabel("hour")
    plt.xlim([0, N_t])
    plt.ylabel("industry [kg/hr]")
    plt.ylim([0, 1.2*max(Phi_industry)])
    plt.gca().yaxis.grid(True)
    plt.legend()
    plt.show()
    plt.title("Mobility and Industry hydrogen contracts" )
    plt.subplot(2,1,2)
    plt.bar(np.arange(N_d),Phi_mobility_d,0.95,align="edge")
    plt.xlabel("day")
    plt.xlim([0, N_d])
    plt.ylabel("mobility [kg/day]")
    plt.ylim([0, 1.3*max(Phi_mobility_d)])
    plt.gca().yaxis.grid(True)
    plt.legend()
    plt.show()
    
    
    ## Initialization
    load_batt_0 = C_batt*(load_max+load_min)/2  # Initial state of load of the battery park
    load_vess_0 = C_vess/2                      # Initial state of load of the hydrogen pressure vessel

    ## Feasibility analysis
    H2_max_prod = N_t*dt*power_nom/eff_conv;   # [kg] maximum overall production of H2
    H2_demand = dt*sum(Phi_industry[:])+sum(Phi_mobility_d[:]) # [kg] required H2 overall 
    print('max production:',np.round(H2_max_prod,1),'kg(H2)')
    print('demand:',H2_demand,'kg(H2)')
    if H2_demand > H2_max_prod:
        print('UNFEASABLE')
    
    
    
    ## Optimization 
    # Instantiate a Glop solver, naming it LinearExample.
    s = pywraplp.Solver('Solver_H2_management',pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING); # for MILP

    # Decision variables 
    Psi_batt_in = N_t*[[]]; # [kWh/hr] Net energy stored in battery at iteration i
    Phi_vess_in = N_t*[[]]; # [kg(H2)/hr] Net hydrogen stored in vessel at iteration i 
    Psi_conv = N_t*[[]]; # [kW] production level of electrolyzer 
    Psi_grid = N_t*[[]]; # [kW] net inflow from the grid (>0 if electricity bought from the grid)
    for i in range(N_t):
        Psi_batt_in[i] = s.NumVar(-power_max, power_max, 'Psi_batt_in_'+str(i))
        Phi_vess_in[i] = s.NumVar(-s.infinity(), power_nom/eff_conv, 'Phi_vess_in_'+str(i))
        Psi_conv[i] = s.NumVar(0, power_nom, 'Psi_conv_'+str(i))
        Psi_grid[i] = s.NumVar(-s.infinity(), s.infinity(), 'Psi_grid_'+str(i))
        
    # Other variables
    Psi_node = N_t*9*[[]]; # [kW] Power transfer between the nodes 1, 2, 3, 4 and 8
    Phi_node = N_t*5*[[]]; # [kg(H2)/hr] Hydrogen transfer between the nodes 5, 6, 7 and 8
    Eps_batt = N_t*[[]]; # [kWh] energy stored in the battery
    M_vess = N_t*[[]]; # [kg(H2)] mass of hydrogen stored in the vessel
    y_conv = N_t*[[]]; # [] Binary variable (=1 if electrolizer is on, 0 otherwise)
    y1 = N_t*[[]]; # binary used to model eff_conv=eff_conv(Psi_conv)
    y2 = N_t*[[]]; # binary used to model eff_conv=eff_conv(Psi_conv)
    y3 = N_t*[[]]; # binary used to model eff_conv=eff_conv(Psi_conv)
    Phi_conv = N_t*[[]]; # [kg(H2)/hr] Hydrogen produced by electrolizer
    Phi_mobility = N_t*[[]]; # [kg(H2)/hr] distribution of prod for mobility
    R = N_t*[[]]; # [$] Net revenue at each time step
    for i in range(N_t):
        Eps_batt[i] = s.NumVar(load_min*C_batt,load_max*C_batt,'Eps_batt_'+str(i))
        M_vess[i] = s.NumVar(0, C_vess,'M_vess_'+str(i))
        y_conv[i] = s.IntVar(0, 1,'y_conv'+str(i))
        y1[i] = s.IntVar(0,1,'y1_'+str(i))
        y2[i] = s.IntVar(0,1,'y2_'+str(i))
        y3[i] = s.IntVar(0,1,'y3_'+str(i))
        Phi_conv[i] = s.NumVar(0, prod_rate_max*power_nom/eff_conv,'Phi_conv_'+str(i))
        Phi_mobility[i] = s.NumVar(0,s.infinity(),'Phi_mobility_'+str(i))
        R[i] = s.NumVar(-s.infinity(), s.infinity(),'R'+str(i))
        for j in range(9):
            Psi_node[N_t*j+i] = s.NumVar(-s.infinity(), s.infinity(),'Psi_node_'+str(i)+str(j)) 
        for j in range(5):
            Phi_node[N_t*j+i] = s.NumVar(-10*power_nom/eff_conv, 10*power_nom/eff_conv,'Phi_node_'+str(i)+str(j))
                    
    
    Eps_batt[0] = s.NumVar(load_batt_0, load_batt_0,'Eps_batt_00') # initialize battery load
    M_vess[0] = s.NumVar(load_vess_0, load_vess_0,'M_vess_00') # initialize vessel load
    Eps_batt[-1] = s.NumVar(load_batt_0, load_batt_0,'Eps_batt_end') # initialize battery load
    M_vess[-1] = s.NumVar(load_vess_0, load_vess_0,'M_vess_end') # initialize vessel load

    
    # Constraints
    
    # (1) Power balance in between nodes 1, 2, 3, 4 and 8
    constraint_power = N_t*[5*[[]]]
    for i in range(N_t):
        # solar farm
        constraint_power[i][0] = s.Constraint(Psi_solar[i],Psi_solar[i])
        constraint_power[i][0].SetCoefficient(Psi_node[N_t*0+i],1)
        constraint_power[i][0].SetCoefficient(Psi_node[N_t*1+i],1)
        constraint_power[i][0].SetCoefficient(Psi_node[N_t*2+i],1)
        # wind farm
        constraint_power[i][1] = s.Constraint(Psi_wind[i],Psi_wind[i])
        constraint_power[i][0].SetCoefficient(Psi_node[N_t*3+i],1)
        constraint_power[i][1].SetCoefficient(Psi_node[N_t*4+i],1)
        constraint_power[i][1].SetCoefficient(Psi_node[N_t*5+i],1)
        # grid node
        constraint_power[i][2] = s.Constraint(0,0)
        constraint_power[i][2].SetCoefficient(Psi_grid[i],-1)
        constraint_power[i][2].SetCoefficient(Psi_node[N_t*0+i],-1)
        constraint_power[i][2].SetCoefficient(Psi_node[N_t*3+i],-1)
        constraint_power[i][2].SetCoefficient(Psi_node[N_t*6+i],1)
        constraint_power[i][2].SetCoefficient(Psi_node[N_t*7+i],1)
        # battery pack node
        constraint_power[i][3] = s.Constraint(0,0)
        constraint_power[i][3].SetCoefficient(Psi_batt_in[i],-1)
        constraint_power[i][3].SetCoefficient(Psi_node[N_t*1+i],1)
        constraint_power[i][3].SetCoefficient(Psi_node[N_t*4+i],1)
        constraint_power[i][3].SetCoefficient(Psi_node[N_t*6+i],1)
        constraint_power[i][3].SetCoefficient(Psi_node[N_t*8+i],-1)
        # Electrolyzer node
        constraint_power[i][4] = s.Constraint(0,0)
        constraint_power[i][4].SetCoefficient(Psi_conv[i],-1)
        constraint_power[i][4].SetCoefficient(Psi_node[N_t*2+i],1)
        constraint_power[i][4].SetCoefficient(Psi_node[N_t*5+i],1)
        constraint_power[i][4].SetCoefficient(Psi_node[N_t*7+i],1)
        constraint_power[i][4].SetCoefficient(Psi_node[N_t*8+i],1)
        


    # (2) Hydrogen mass balance between nodes 5, 6, 7 and 8
    constraint_h2 = N_t*[4*[[]]]
    for i in range(N_t):
        # Industry node
        constraint_h2[i][0] = s.Constraint(1,1)#Phi_industry[i],Phi_industry[i])        
        constraint_h2[i][0].SetCoefficient(Phi_node[N_t*1+i],1/Phi_industry[i])
        constraint_h2[i][0].SetCoefficient(Phi_node[N_t*4+i],-1/Phi_industry[i])
        # Mobility node
        constraint_h2[i][1] = s.Constraint(0,0)
        constraint_h2[i][1].SetCoefficient(Phi_mobility[i],-1)
        constraint_h2[i][1].SetCoefficient(Phi_node[N_t*0+i],1)
        constraint_h2[i][1].SetCoefficient(Phi_node[N_t*3+i],-1)
        # Hydrogen vessel
        constraint_h2[i][2] = s.Constraint(0,0)
        constraint_h2[i][2].SetCoefficient(Phi_vess_in[i],1)
        constraint_h2[i][2].SetCoefficient(Phi_node[N_t*0+i],1)
        constraint_h2[i][2].SetCoefficient(Phi_node[N_t*1+i],1)
        constraint_h2[i][2].SetCoefficient(Phi_node[N_t*2+i],1)
        # Electrolyzer node
        constraint_h2[i][3] = s.Constraint(0,0)
        constraint_h2[i][3].SetCoefficient(Phi_conv[i],1)
        constraint_h2[i][3].SetCoefficient(Phi_node[N_t*2+i],1)
        constraint_h2[i][3].SetCoefficient(Phi_node[N_t*3+i],1)
        constraint_h2[i][3].SetCoefficient(Phi_node[N_t*4+i],1)
         

    # (3) Power storage in the battery park
    constraint_batt = N_t*[[]]
    for i in range(1,N_t):
        constraint_batt[i] = s.Constraint(0,0)
        constraint_batt[i].SetCoefficient(Psi_batt_in[i],-eff_batt*dt)
        constraint_batt[i].SetCoefficient(Eps_batt[i-1],-1)
        constraint_batt[i].SetCoefficient(Eps_batt[i],1)       
    
    
    # (4) Hydrogen storage in the vessel park
    constraint_vess = N_t*[[]]
    for i in range(1,N_t):
        constraint_vess[i] = s.Constraint(0,0)
        constraint_vess[i].SetCoefficient(Phi_vess_in[i-1],-eff_vess*dt)
        constraint_vess[i].SetCoefficient(M_vess[i-1],-1)
        constraint_vess[i].SetCoefficient(M_vess[i],1)
        
        
    # (5) Power->Hydrogen conversion in the electrolyzer park
    constraint_conv1 = N_t*[2*[[]]]
    constraint_conv2 = N_t*[2*[[]]]
    constraint_conv3 = N_t*[2*[[]]]
    constraint_conv4 = N_t*[[]]
    
    M = 2*power_nom
    
    for i in range(N_t):
        # If Psi_conv>3/4*Psi_nom then eff_conv=0.5*eff_conv_nom      
        constraint_conv1[i][0] = s.Constraint(0,s.infinity())
        constraint_conv1[i][0].SetCoefficient(Psi_conv[i],1)
        constraint_conv1[i][0].SetCoefficient(y1[i],-3/4*power_nom)
        constraint_conv1[i][1] = s.Constraint(-M,s.infinity())
        constraint_conv1[i][1].SetCoefficient(Phi_conv[i],-eff_conv/0.65)
        constraint_conv1[i][1].SetCoefficient(Psi_conv[i],1)
        constraint_conv1[i][1].SetCoefficient(y1[i],-M)
        # If 1/2*Psi_nom<Psi_conv<3/4*Psi_nom then eff_conv=0.65*eff_conv_nom  
        constraint_conv2[i][0] = s.Constraint(0,s.infinity())
        constraint_conv2[i][0].SetCoefficient(Psi_conv[i],1)
        constraint_conv2[i][0].SetCoefficient(y2[i],-1/2*power_nom)
        constraint_conv2[i][1] = s.Constraint(-M,s.infinity())
        constraint_conv2[i][1].SetCoefficient(Phi_conv[i],-eff_conv/0.85)
        constraint_conv2[i][1].SetCoefficient(Psi_conv[i],1)
        constraint_conv2[i][1].SetCoefficient(y2[i],-M)
        # If 1/4*Psi_nom<Psi_conv<1/2*Psi_nom then eff_conv=0.85*eff_conv_nom  
        constraint_conv3[i][0] = s.Constraint(0,s.infinity())
        constraint_conv3[i][0].SetCoefficient(Psi_conv[i],1)
        constraint_conv3[i][0].SetCoefficient(y3[i],-1/4*power_nom)
        constraint_conv3[i][1] = s.Constraint(-M,s.infinity())
        constraint_conv3[i][1].SetCoefficient(Phi_conv[i],-eff_conv/0.9)
        constraint_conv3[i][1].SetCoefficient(Psi_conv[i],1)
        constraint_conv3[i][1].SetCoefficient(y3[i],-M)
        # If Psi_conv<1/4*Psi_nom then eff_conv=eff_conv_nom 
        constraint_conv4[i] = s.Constraint(0,s.infinity())
        constraint_conv4[i].SetCoefficient(Phi_conv[i],-eff_conv)
        constraint_conv4[i].SetCoefficient(Psi_conv[i],1)
        
        
    # (6) On/Off policy for the electrolyzer fleet
    constraint_on = N_t*[3*[[]]]
    for i in range(N_t):
        # Electrolizer turned off if Psi_conv<20%.power_nom
        constraint_on[i][0] = s.Constraint(0,s.infinity())
        constraint_on[i][0].SetCoefficient(Psi_conv[i],1)
        constraint_on[i][0].SetCoefficient(y_conv[i],-prod_rate_min*power_nom)
        constraint_on[i][1] = s.Constraint(0,s.infinity())
        constraint_on[i][1].SetCoefficient(y_conv[i],M)
        constraint_on[i][1].SetCoefficient(Psi_conv[i],-1)
        constraint_on[i][2] = s.Constraint(0,s.infinity())
        constraint_on[i][2].SetCoefficient(y_conv[i],M*eff_conv)
        constraint_on[i][2].SetCoefficient(Phi_conv[i],-1)
        
        
    # (7) Mobility hydrogen contract
    constraint_mob = N_d*[[]]
    for d in range(N_d):
        constraint_mob[d] = s.Constraint(1,1)
        for i in range(24):
            constraint_mob[d].SetCoefficient(Phi_mobility[24*d+i],1/Phi_mobility_d[d])


    # (8) Constraint electrolyzer production fluctuation
    constraint_mgt = N_t*[[]] 
    for i in range(1,N_t):
        constraint_mgt[i] = s.Constraint(-var_Psi_conv*power_nom,var_Psi_conv*power_nom)
        constraint_mgt[i].SetCoefficient(Psi_conv[i],1)
        constraint_mgt[i].SetCoefficient(Psi_conv[i-1],1)
    
    
    
    # Objective function: Electricity cost = purchase(power_grid) - sales(power_grid) - sales(power_industry)
    # H2 revenue stream not accounted for in optimization process since this revenue is independent of the actions taken
    # Minimize the cost of purchasing electricity to the grid
    objective=s.Objective()
    for i in range(N_t):
        objective.SetCoefficient(Psi_node[N_t*7+i],Eps_spot[i]) # net purchase from the grid for the elctrolizer
        objective.SetCoefficient(Psi_node[N_t*6+i],Eps_spot[i]) # net purchase from the grid for the battery park
        objective.SetCoefficient(Psi_node[N_t*0+i],-Eps_spot[i]) # net sales to the grid from the solar farm
        objective.SetCoefficient(Psi_node[N_t*3+i],-Eps_spot[i]) # net purchase to the grid from the wind farm
    objective.SetMinimization()   

    ## Solve the system      
    s.Solve()
    print('Number of variables =', s.NumVariables())
    print('Number of constraints =', s.NumConstraints())

    result_status = s.Solve()# solve(s)

    if result_status == s.INFEASIBLE:
        print('No solution found')
        sys.exit ()
#    elif result_status == s.POSSIBLE_OVERFLOW:
#        print('Some inputs are too large and may cause an integer overflow.')
    elif result_status == s.OPTIMAL:
        print('Successful solve.')
        # The problem has an optimal solution.
        print(('Problem solved in %f milliseconds' % s.wall_time()))
        # The objective value of the solution.
        print(('Optimal cost of power purchase from the grid: $ %f' % s.Objective().Value()))



    ## Store useful results
    y_conv_opt = np.zeros((N_t,))
    Eps_batt_opt = np.zeros((N_t,))
    M_vess_opt = np.zeros((N_t,))
    Psi_conv_opt = np.zeros((N_t,))
    Phi_conv_opt = np.zeros((N_t,))
    Psi_grid_opt = np.zeros((N_t,))
    R_opt = np.zeros((N_t,))
    
    for i in range(N_t):
        y_conv_opt[i] = y_conv[i].solution_value()
        Eps_batt_opt[i] = Eps_batt[i].solution_value()
        M_vess_opt[i] = M_vess[i].solution_value()
        Psi_conv_opt[i] = Psi_conv[i].solution_value()
        Phi_conv_opt[i] = Phi_conv[i].solution_value()
        Psi_grid_opt[i] = Psi_grid[i].solution_value()
        R_opt[i] = R[i].solution_value()
      
        
    # Efficiency
    Eff_conv = np.zeros((N_t,))
    for i in range(N_t):
        if Psi_conv_opt[i]>0:
            Eff_conv[i] = Psi_conv_opt[i]/Phi_conv_opt[i]
           
            
    # Plotting
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    plt.title('Hydrogen production')
    plt.xlim([0, N_t])
    ax1.bar(np.arange(N_t),Phi_conv_opt,0.8,align="center") 
    ax2.plot(np.arange(N_t),Eff_conv,'r*',label='efficiency')
    ax2.plot(np.arange(N_t),eff_conv*np.ones((N_t,)),'r--',linewidth=0.5)
    ax1.set_xlabel('time [hrs]')
    ax1.set_ylabel('H2 produced [kg(H2)/hr]')
    ax2.set_ylabel('efficiency [kWh/kg(H2)]')
    ax1.set_ylim(0,1.2*max(Phi_conv_opt))
    ax2.set_ylim(0,1.2*eff_conv/0.5)
    plt.grid()
    plt.legend()
    plt.show()

    
    plt.figure(4)
    plt.subplot(2,1,1)
    plt.bar(np.arange(N_t),Psi_grid_opt,0.8,align="edge") 
    plt.xlabel("time [hrs]")
#    plt.xticks([24*7*5*i for i in range(52)], [5*i for i in range(26)])
    plt.xlim([0, 24*N_d])
    plt.ylabel("Power in [kWh/hr]")
    plt.ylim([1.2*min(Psi_grid_opt), 1.2*max(Psi_grid_opt)])
    plt.gca().yaxis.grid(True)
    plt.legend()
    plt.show()
    plt.title("Net Power purchase from the grid" )
    plt.subplot(2,1,2)
    plt.bar(np.arange(N_t),Eps_spot,0.95,align="edge")
    plt.xlabel("time [hr]")
#    plt.xticks(H2_dc[0::7*5,0], [5*i for i in range(11)])
    plt.xlim([0, 24*N_d])
    plt.ylabel("Power cost [$/kWh]")
    plt.ylim([0, 1.3*max(Eps_spot)])
    plt.gca().yaxis.grid(True)
    plt.show()
    
    
    plt.figure(5)
    plt.subplot(2,1,1)
    plt.bar(np.arange(N_t),M_vess_opt,0.8,align="edge") 
    plt.xlabel("time [hrs]")
#    plt.xticks([24*7*5*i for i in range(52)], [5*i for i in range(26)])
    plt.xlim([0, 24*N_d])
    plt.ylabel("H2 vessel [kg(H2)]")
    plt.ylim([0, 1.2*max(M_vess_opt)])
    plt.gca().yaxis.grid(True)
    plt.legend()
    plt.show()
    plt.title("Storage behavior" )
    plt.subplot(2,1,2)
    plt.bar(np.arange(N_t),Eps_batt_opt,0.95,align="edge")
    plt.xlabel("time [hr]")
#    plt.xticks(H2_dc[0::7*5,0], [5*i for i in range(11)])
    plt.xlim([0, 24*N_d])
    plt.ylabel("battery [kWh]")
    plt.ylim([0, 1.3*max(Eps_batt_opt)])
    plt.gca().yaxis.grid(True)
    plt.show()
    
 

    return [y_conv_opt,Eps_batt_opt,M_vess_opt,Psi_conv_opt,Phi_conv_opt,Psi_grid_opt,R_opt]




        