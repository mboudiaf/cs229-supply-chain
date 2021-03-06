author = 'Malik Boudiaf, mboudiaf@stanford.edu'

from scipy import r_

from learner.valuebased import ValueBasedLearner
from pybrain.datasets import SupervisedDataSet
from pybrain.supervised.trainers.rprop import RPropMinusTrainer
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.utilities import one_to_n


class NFQ(ValueBasedLearner):
    """ Neuro-fitted Q-learning"""

    def __init__(self, maxEpochs=15,epsilon = 0.3, gamma = 0.9, alpha=0.1):
        ValueBasedLearner.__init__(self,epsilon)
        self.gamma = gamma
        self.maxEpochs = maxEpochs
        self.alpha = alpha
        
    def learn(self):
        # convert reinforcement dataset to NFQ supervised dataset
        supervised = SupervisedDataSet(self.module.network.indim, 1)
        
        for seq in self.dataset:
            lastexperience = None
            for state, action, reward in seq:
                if not lastexperience:
                    # delay each experience in sequence by one
                    lastexperience = (state, action, reward)
                    continue

                # use experience from last timestep to do Q update
                (state_, action_, reward_) = lastexperience
                Q = self.module.getValue(state_, int(action_[0]))
                

                inp = r_[state_, one_to_n(int(action_[0]), self.module.numActions)]
                #input = r_[state_, action_]
                tgt = Q + self.alpha*(reward_ + self.gamma * max(self.module.getActionValues(state)) - Q)
                supervised.addSample(inp, tgt)

                # update last experience with current one
                lastexperience = (state, action, reward)

        # train module with backprop/rprop on dataset
        trainer = RPropMinusTrainer(self.module.network, dataset=supervised, batchlearning=True, verbose=True)
        trainer.trainUntilConvergence(maxEpochs=self.maxEpochs)




