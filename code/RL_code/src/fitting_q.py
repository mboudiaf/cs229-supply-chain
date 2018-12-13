author = 'Malik Boudiaf, mboudiaf@stanford.edu'

from environment.SupplyChainEnv import SupplyChainEnv
from experiment.experiment import  Experiment
from learner.interface import ActionValueTable
from explorer.egreedy import EpsilonGreedyExplorer
from agent.learning import LearningAgent
from agent.logging import LoggingAgent
from learner.q import Q
from environment.SupplyTask import SupplyTaskMDP
import pickle
from utilities import *
import pandas as pd

# Parameters of simulation
country = 'France'
timestep = 1 # [h]
horizon = 24 # [h] We want the model for be efficient for 24 
hours_of_data = 30*24 # [h]

#Loading data

file_solar = "../data/solar.xls" # w
file_wind = "../data/wind.xls" # MW
file_price = "../data/price.xlsx" # euro / MW

tableau = pd.DataFrame(generate_table(file_solar, file_wind, file_price, country))
price_dataset=tableau[3][:]
solar_dataset=tableau[1][:]
wind_dataset =tableau[2][:]

#Converting units
solar_dataset = solar_dataset.values * 1000 # mW -> kW
wind_dataset = wind_dataset.values * 1000
price_dataset = price_dataset.values / 1000 # euro/mW -> euro/kW

desired_prod_max= 10000 #kW
#desired_prod_std= 50
#normalized_prod_dataset = (prod_dataset - prod_dataset.mean())/prod_dataset.std()*desired_prod_std + desired_prod_mean
normalized_prod_dataset = desired_prod_max * (wind_dataset/wind_dataset.max() + solar_dataset/solar_dataset.max())
normalized_price_dataset= price_dataset


# We have data for 1 month
# So we can split the data as such : 26 days for training set , 2 days for dev set, 2 days for test set

#First we form day sequences of data
day_split_prod = [normalized_prod_dataset[24*i:24*(i+1)] for i in range(30)]
day_split_price = [normalized_price_dataset[24*i:24*(i+1)] for i in range(30)]

#We shuffle
#np.random.seed(0)
random_order = list(range(30))

#Splitting data
prod_train = [day_split_prod[i] for i in random_order[:26]]
prod_val = [day_split_prod[i] for i in random_order[26:28]]
prod_test = [day_split_prod[i] for i in random_order[28:30]]

price_train = [day_split_price[i] for i in random_order[:26]]
price_val = [day_split_price[i] for i in random_order[26:28]]
price_test = [day_split_price[i] for i in random_order[28:30]]

#Chosing discretizations
# STATES
discrete_battery=np.linspace(0,100,20)
discrete_vessel=np.linspace(0,100,20)
discrete_grid_price=np.linspace(min(normalized_price_dataset),max(normalized_price_dataset),10) # euro/kW
discrete_prod=np.linspace(min(normalized_prod_dataset),max(normalized_prod_dataset),10) # kW


#ACTIONS
discrete_elec_regime=np.linspace(15,40,8)# % of max rate production of electrolyzer
discrete_buy_sell=np.linspace(-15,-15,8)# % of battery capacity

n_states=24*len(discrete_battery)*len(discrete_vessel)*len(discrete_grid_price)*len(discrete_prod)*len(discrete_elec_regime)
n_actions=len(discrete_elec_regime)*len(discrete_buy_sell)
print("Number of actions :",n_actions)
print("Number of states :",n_states)

#building environment
controller = ActionValueTable(n_states, n_actions)
controller.initialize(0.)
learner = Q(epsilon=0.5) # comes by default with explorer = EpsilonGreedyExplorer(epsilon = 0.3, decay = 0.9999)
agent = LearningAgent(controller, learner)
print('New Q agent created')

environment =  SupplyChainEnv(normalized_prod_dataset[0:48],normalized_price_dataset[0:48],discrete_battery,discrete_vessel,discrete_elec_regime,discrete_grid_price,discrete_prod,discrete_buy_sell)

task = SupplyTaskMDP(environment)

experiment = Experiment(task, agent)

#Training
num_epochs = 1000
horizon = 48 # 24 interactions = horizon of 1 day

battery_states=[]
h2_vessel_states=[]
actions_electrolyzer=[]
actions_grid=[]
eval_rewards=[]
for epoch in range(num_epochs):
    actions_electrolyzer_day = []
    actions_grid_day = []
    battery_states_day = []
    h2_vessel_states_day = []
    print("-------------------EPOCH  ",epoch,"/",num_epochs,' ---------------------')
    for day in range(len(prod_train)):
        #print("----------DAY ",day," ----------")
        #Reset environment and agent
        day_prod = prod_train[day]
        day_price=prod_train[day]
        environment.reset(day_prod,day_price)
        LoggingAgent.reset(agent) 
        
        
        # Roll out the simulation
        battery_state,h2_vessel_state,regime_e,flow_g,_=experiment.doInteractions(horizon,day=day) 
        
        # Keep track of several state/action variables
        battery_states_day.append(battery_state)
        h2_vessel_states_day.append(h2_vessel_state)
        actions_electrolyzer_day.append(regime_e)
        actions_grid_day.append(flow_g)
        
        #Update Q(s,a) for all visited pairs (s,a)
        agent.learn()
        
    # Keep track of several state/action variables
    battery_states.append(battery_states_day)
    h2_vessel_states.append(h2_vessel_states_day)
    actions_electrolyzer.append(actions_electrolyzer_day)
    actions_grid.append(actions_grid_day)
    
    # Monitor the performance of the policy on the evaluation day
    #print("Monitoring values")
    #train_utility = eval_agent(agent,environment,experiment,prod_train,price_train,horizon=24)
    #print("Utility on trains days :",train_utility)
    
    utilities,battery_states,h2_vessel_states,flow_g,regime_e = eval_agent(agent,environment,experiment,prod_val,price_val,horizon=48)
    print("Utility on validation days :",utilities[0])
    
    utilities,battery_states,h2_vessel_states,flow_g,regime_e = eval_agent(agent,environment,experiment,prod_test,price_test,horizon=48)
    print("Utility on test days :",utilities[0])
    if epoch % 10000 == 0:
        fname="models/policy_e_"+str(epoch)+".txt"
        pickle.dump(regime_e[0], open(fname,'wb'))
        fname="models/policy_g_"+str(epoch)+".txt"
        pickle.dump(flow_g[0], open(fname,'wb'))

















