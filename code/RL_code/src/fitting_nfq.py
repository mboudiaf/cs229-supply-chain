author = 'Malik Boudiaf, mboudiaf@stanford.edu'

from environment.SupplyChainEnv import SupplyChainEnv
from experiment.experiment import  Experiment
from learner.interface import ActionValueNetwork
from explorer.egreedy import EpsilonGreedyExplorer
from agent.learning import LearningAgent
from agent.logging import LoggingAgent
from learner.nfq import NFQ
from learner.nfq_test import NFQ_test
from environment.SupplyTask import SupplyTaskMDP
import pickle
from utilities import *
import pandas as pd

# Parameters of simulation
country = 'France'
timestep = 1 # [h]

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

# (Optional) We shuffle
#np.random.seed(0)
#random_order = np.random.permutation(range(30))
random_order = list(range(30))

#Splitting data
prod_train = [day_split_prod[i] for i in random_order[4:]]
prod_val = [day_split_prod[i] for i in random_order[2:4]]
prod_test = [day_split_prod[i] for i in random_order[0:2]]

price_train = [day_split_price[i] for i in random_order[4:]]
price_val = [day_split_price[i] for i in random_order[2:4]]
price_test = [day_split_price[i] for i in random_order[0:2]]

#Chosing discretizations
# STATES
discrete_battery=np.linspace(0,100,10)
discrete_vessel=np.linspace(0,100,10)
discrete_grid_price=np.linspace(min(normalized_price_dataset),max(normalized_price_dataset),100) # euro/kW
discrete_prod=np.linspace(min(normalized_prod_dataset),max(normalized_prod_dataset),100) # kW


#ACTIONS
discrete_elec_regime=np.linspace(20,40,10)# % of max rate production of electrolyzer
discrete_buy_sell=np.linspace(-15,15,10)# % of battery capacity

n_states=24*len(discrete_battery)*len(discrete_vessel)*len(discrete_grid_price)*len(discrete_prod)*len(discrete_elec_regime)
n_actions=len(discrete_elec_regime)*len(discrete_buy_sell)
print("Number of actions :",n_actions)
print("Number of states :",n_states)

#Initializing agent
#try:
#    agent=pickle.load(open('agent_nfq.txt','rb'))
#    print('Agent loaded')
#except Exception as e:
#    print(e)

#Initializing environment
environment =  SupplyChainEnv(normalized_prod_dataset[0:48],normalized_price_dataset[0:48],discrete_battery,discrete_vessel,discrete_elec_regime,discrete_grid_price,discrete_prod,discrete_buy_sell)

#Initializing agent
controller = ActionValueNetwork(dimState=6, numActions=n_actions, id2action = environment.id2action)
learner = NFQ(epsilon=0.4, gamma = 0.9, alpha=0.1) 
agent = LearningAgent(controller, learner, id2action = environment.id2action)
print('New agent created')


#Initializing task
task = SupplyTaskMDP(environment)

#Initializing experiment
experiment = Experiment(task, agent)

#Training
num_epochs = 10000
horizon = 48

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
    learn = True
    print("-------------------EPOCH  ",epoch,"/",num_epochs,' ---------------------')
    #for day in range(len(prod_train)):
    for day in range(1):
        #Reset environment and agent

        day_prod = prod_train[day]
        day_price=price_train[day]
        environment.reset(day_prod,day_price)
        LoggingAgent.reset(agent) 

        
        
        # Roll out the simulation
        battery_state,h2_vessel_state,regime_e,flow_g=experiment.doInteractions(horizon,day=day) 
        
        # Keep track of several state/action variables
        battery_states_day.append(battery_state)
        h2_vessel_states_day.append(h2_vessel_state)
        actions_electrolyzer_day.append(regime_e)
        actions_grid_day.append(flow_g)
        
        #Update Q(s,a) for all visited pairs (s,a)
        #print(len(agent.history['state']))
        #if len(agent.history['state'])>15:
         #   learn = True
        agent.learn()
        #else:
        #s    learn = False
        
        
    # Keep track of several state/action variables
    battery_states.append(battery_states_day)
    h2_vessel_states.append(h2_vessel_states_day)
    actions_electrolyzer.append(actions_electrolyzer_day)
    actions_grid.append(actions_grid_day)
    
    # Monitor the performance of the policy on the evaluation day
    print("Monitoring values")
    utilities,_,_,_,_  = eval_agent(agent,environment,experiment,prod_train,price_train,horizon=24)
    print("Utility on trains days :",utilities)
    
    utilities,_,_,_,_ = eval_agent(agent,environment,experiment,prod_test,price_test,horizon=24)
    eval_rewards.append(eval_utility)
    print("Utility on eval days :",utilities)
    if epoch % 20 == 0:
        pickle.dump(agent, open('models/agent_nfq.txt','wb'))
        

















