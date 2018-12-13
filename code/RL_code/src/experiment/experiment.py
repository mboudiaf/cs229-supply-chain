author = 'Malik Boudiaf, mboudiaf@stanford.edu'

import matplotlib.pyplot as plt

class Experiment(object):
    """ An experiment matches up a task with an agent and handles their interactions.
    """

    def __init__(self, task, agent):
        self.task = task
        self.agent = agent
        self.stepid = 0

    def doInteractions(self, number = 1,day=0, test=False,given_policy=[]):
        """ The default implementation directly maps the methods of the agent and the task.
            Returns the number of interactions done.
        """
        self.stepid = 0 
        battery_states=[]
        h2_vessel_states=[]
        regime_e=[]
        flow_g=[]
        rewards=[]
        print("Sequence of chosen actions:")
        for _ in range(number):
            battery_state,h2_vessel_state,action_e,action_g,reward=self._oneInteraction(test,given_policy)
            
            # Keep track of what happened during the last day
            h2_vessel_states.append(h2_vessel_state)
            battery_states.append(battery_state)
            regime_e.append(action_e)
            flow_g.append(action_g)
            rewards.append(reward)
            
            # If terminal state reached, report day and hour
            if self.task.env.terminal_battery:
                print("Day",day,"Hour",self.stepid,"Terminal battery state reached")
                break
            if self.task.env.terminal_vessel:
                print("Day",day,"Hour",self.stepid,"Terminal vessel reached")
                break
        return battery_states,h2_vessel_states,regime_e,flow_g,rewards

    def _oneInteraction(self,test,given_policy):
        """ Give the observation to the agent, takes its resulting action and returns
            it to the task. Then gives the reward to the agent again and returns it.
        """
        state_id,real_state = self.task.getObservation()
       
        # First case : execute a given predefined list of actions
        if given_policy != []: 
            action=(given_policy[self.stepid,0],given_policy[self.stepid,1])
            self.task.performAction(action)
            reward = self.task.getReward(action)
            
        # Second case : use the policy of the agent given
        else:
            self.agent.integrateObservation(state_id)
            
            # If at training time, action is chosen by the explorer
            if test==False:
                action = int(self.agent.getAction())
                action = self.task.env.id2action[action]
            # If at test time, we take the max Q-value action
            else:
                self.agent.lastaction = self.agent.module.activate(self.agent.lastobs)
                action = self.task.env.id2action[int(self.agent.lastaction)]
                print(self.agent.lastaction)
                
            self.task.performAction(action)
            reward = self.task.getReward(action)
            self.agent.giveReward(reward)


      
        self.stepid += 1
        return self.task.env.battery.current_load,self.task.env.h2_vessel.current_load,action[0],action[1],reward

 